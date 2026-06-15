#!/usr/bin/env python3
"""Add a writing-script column to index_data.csv from Ethnologue.

Joins Ethnologue's `Writing` field (e.g. "Latin script [Latn].",
"Unwritten [Qaax].") onto the language index by ISO 639-3. Ethnologue's ISO
is taken from its page URL (/language/<iso>); the iso_639_3 column is empty.

Adds one column:
  writing_script   "Yes"  if Ethnologue lists any script / writing system
                   "No"   if Ethnologue states the language is Unwritten
                   ""     if the Writing field is blank or the language is not
                          in Ethnologue (blank = no data, NOT 'unwritten')

Mirrors keyman_integration/apply_keyman.py: appends the new field to the end of
each raw line, preserving the file's space-padded formatting. A timestamped
backup is written next to this script first.
"""
import csv, os, re, shutil, datetime
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CSV = os.path.join(ROOT, "index_data.csv")
ETH = os.path.join(ROOT, "ethnologue_languages.csv")
NEW_COLS = ["writing_script"]


def classify(writing):
    wl = writing.lower()
    if not writing:
        return ""              # no data
    if "script" in wl:
        return "Yes"           # any attested script -> written (takes precedence)
    if "unwritten" in wl:
        return "No"
    return "Yes"               # other non-blank writing systems (e.g. picture writing)


# 1. iso -> writing status from Ethnologue (precedence: Yes > No > blank)
rank = {"Yes": 2, "No": 1, "": 0}
iso2w = {}
with open(ETH, newline="") as f:
    r = csv.reader(f, skipinitialspace=True)
    eh = [h.strip() for h in next(r)]
    ei = {h: i for i, h in enumerate(eh)}
    for row in r:
        url = row[ei["url"]].strip() if ei["url"] < len(row) else ""
        m = re.search(r"/language/([a-z]{3})\b", url)
        if not m:
            continue
        iso = m.group(1)
        cls = classify(row[ei["Writing"]].strip() if ei["Writing"] < len(row) else "")
        if rank[cls] > rank.get(iso2w.get(iso, ""), -1):
            iso2w[iso] = cls

# 2. backup
stamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
backup = os.path.join(HERE, f"index_data.backup_{stamp}.csv")
shutil.copy2(CSV, backup)

# 3. read raw lines; parse each robustly to get iso_code; append writing_script
with open(CSV, newline="") as f:
    raw = f.readlines()
header_fields = next(csv.reader([raw[0]], skipinitialspace=True))
iso_idx = [h.strip() for h in header_fields].index("iso_code")

out = [raw[0].rstrip("\n").rstrip("\r") + "," + ",".join(NEW_COLS) + "\n"]
for line in raw[1:]:
    if not line.strip():
        out.append(line)
        continue
    fields = next(csv.reader([line], skipinitialspace=True))
    iso = fields[iso_idx].strip().lower()
    out.append(line.rstrip("\n").rstrip("\r") + f",{iso2w.get(iso, '')}\n")

with open(CSV, "w", newline="") as f:
    f.writelines(out)

# 4. verify + report
with open(CSV, newline="") as f:
    r = csv.reader(f, skipinitialspace=True)
    hdr = next(r)
    ncol = len(hdr)
    wi = [h.strip() for h in hdr].index("writing_script")
    ii = [h.strip() for h in hdr].index("iso_code")
    rows = list(r)
bad = sum(1 for row in rows if len(row) != ncol)
dist = Counter((row[wi].strip() or "(blank)") for row in rows)
nomatch = sum(1 for row in rows if row[ii].strip().lower() not in iso2w)

print(f"backup written: {backup}")
print(f"columns now: {ncol} (added {len(NEW_COLS)})")
print(f"rows: {len(rows)}, inconsistent column count after write: {bad}")
print(f"writing_script distribution:")
for k, v in dist.most_common():
    print(f"  {v:5d}  {k}")
print(f"(of the blanks, {nomatch} have no Ethnologue match at all)")
