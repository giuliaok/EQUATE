#!/usr/bin/env python3
"""Add an EGIDS-grounded language-ecology classification to index_data.csv.

This is a data-backed replacement basis for the heuristic
`language_ecology_primary_type` (see apply_language_ecology.py). Instead of an
ad-hoc point score, the ecology type is derived from Ethnologue's **Language
Status = EGIDS** (Expanded Graded Intergenerational Disruption Scale; Lewis &
Simons 2010), combined with structured cross-country usage already in the index.

Adds TWO columns (the existing `language_ecology_primary_type` is left intact):

  egids_level         the bare EGIDS scale code only: 0,1,2,3,4,5,6a,6b,7,8a,
                      8b,9,10  (blank if Ethnologue has no/Unestablished status)
  ecology_egids_type  derived ecology label, same vocabulary as the old column:
                      standardized_bridge | bridge | local_standardized | local

COPYRIGHT NOTE: only the bare EGIDS *level code* is stored (one short factual
field, transformed) -- never Ethnologue's verbatim status prose. The EGIDS scale
itself is published methodology (Lewis & Simons 2010). Cite Ethnologue
(Eberhard, Simons & Fennig) + EGIDS as the source of `egids_level`.

EGIDS level meanings (for reference): 0 International, 1 National, 2 Provincial,
3 Wider Communication, 4 Educational, 5 Developing, 6a Vigorous, 6b Threatened,
7 Shifting, 8a Moribund, 8b Nearly extinct, 9 Dormant, 10 Extinct.

Classification rules (all traceable, no opaque scoring):
  standardized = EGIDS in {0,1,2,3,4,5}                       (institutional..developing)
                 OR, when EGIDS is missing, institutional_status == 1   (fallback)
  bridge       = EGIDS in {0,1,2,3}                           (wider-communication tiers)
                 OR spoken across >= 5 countries
                 OR (institutional_status == 1 AND spoken across >= 3 countries)
  ->  standardized & bridge  -> standardized_bridge
      bridge only            -> bridge
      standardized & !bridge -> local_standardized
      else                   -> local
Country spread is counted from country_iso_code + other_country_iso_codes.
(n_speakers is deliberately NOT used: it carries placeholder sentinels.)

Mirrors keyman_integration/apply_keyman.py for the append; backs up first.
"""
import csv, os, re, shutil, datetime
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CSV = os.path.join(ROOT, "index_data.csv")
ETH = os.path.join(ROOT, "ethnologue_languages.csv")
NEW_COLS = ["egids_level", "ecology_egids_type"]

STD = {"0", "1", "2", "3", "4", "5"}
WIDE = {"0", "1", "2", "3"}


def egids_code(status):
    """Bare EGIDS level from Ethnologue Language Status prose; '' otherwise."""
    m = re.match(r"\s*(\d{1,2})([ab])?\*?", status or "")
    return (m.group(1) + (m.group(2) or "")) if m else ""


# 1. iso -> EGIDS code (Ethnologue ISO is in the page URL; iso_639_3 col is empty)
eth = {}
with open(ETH, newline="") as f:
    r = csv.reader(f, skipinitialspace=True)
    eh = [h.strip() for h in next(r)]
    ueg = {h: i for i, h in enumerate(eh)}
    for row in r:
        url = row[ueg["url"]].strip() if ueg["url"] < len(row) else ""
        m = re.search(r"/language/([a-z]{3})\b", url)
        if not m:
            continue
        code = egids_code(row[ueg["Language Status"]].strip() if ueg["Language Status"] < len(row) else "")
        eth.setdefault(m.group(1), code)
        if code and not eth[m.group(1)]:
            eth[m.group(1)] = code

# 2. backup
stamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
backup = os.path.join(HERE, f"index_data.backup_before_egids_{stamp}.csv")
shutil.copy2(CSV, backup)

with open(CSV, newline="") as f:
    raw = f.readlines()
header = [h.strip() for h in next(csv.reader([raw[0]], skipinitialspace=True))]
col = {h: i for i, h in enumerate(header)}


def country_count(fields):
    s = {fields[col["country_iso_code"]].strip()}
    for c in re.split(r"[-,;]", fields[col["other_country_iso_codes"]].strip()):
        c = c.strip()
        if c:
            s.add(c)
    return len({c for c in s if c})


def classify(fields):
    iso = fields[col["iso_code"]].strip()
    eg_ = eth.get(iso, "")
    inst = fields[col["institutional_status"]].strip() == "1"
    cc = country_count(fields)
    if eg_ in STD:
        standardized = True
    elif eg_ == "":
        standardized = inst
    else:
        standardized = False
    bridge = (eg_ in WIDE) or (cc >= 5) or (inst and cc >= 3)
    if bridge and standardized:
        label = "standardized_bridge"
    elif bridge:
        label = "bridge"
    elif standardized:
        label = "local_standardized"
    else:
        label = "local"
    return eg_, label


out = [raw[0].rstrip("\n").rstrip("\r") + "," + ",".join(NEW_COLS) + "\n"]
type_dist, level_dist = Counter(), Counter()
for line in raw[1:]:
    if not line.strip():
        out.append(line)
        continue
    fields = next(csv.reader([line], skipinitialspace=True))
    eg_, label = classify(fields)
    type_dist[label] += 1
    level_dist[eg_ or "(blank)"] += 1
    out.append(line.rstrip("\n").rstrip("\r") + f",{eg_},{label}\n")

with open(CSV, "w", newline="") as f:
    f.writelines(out)

# verify
with open(CSV, newline="") as f:
    r = csv.reader(f, skipinitialspace=True)
    hdr = next(r)
    ncol = len(hdr)
    bad = sum(1 for row in r if len(row) != ncol)

print(f"backup: {backup}")
print(f"columns now: {ncol} (added {len(NEW_COLS)})")
print(f"inconsistent rows: {bad}")
print("\necology_egids_type distribution:")
for k, v in type_dist.most_common():
    print(f"  {v:5d}  {k}")
print(f"\negids_level coverage: {sum(v for k,v in level_dist.items() if k!='(blank)')} populated, "
      f"{level_dist['(blank)']} blank")
