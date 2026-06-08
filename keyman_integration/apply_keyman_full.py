#!/usr/bin/env python3
"""Regenerate keyman_keyboards_n from the FULL Keyman search/2.0 catalogue.

Supersedes the legacy build (apply_keyman.py + keyman_keyboards.json), which used
the cloud/4.0 API (only 323 keyboards, 639-3 tags) and undercounted ~2x. The
search/2.0 catalogue (~910 keyboards) tags languages in 2-letter BCP-47 (e.g.
Korean = "ko"), so we normalize each tag to ISO 639-3 before joining on iso_code.

Inputs (defaults; override via argv):
  --catalogue  /tmp/keyman_full_catalogue.json   {keyboard_id: [bcp47 tags]}
  --iso639     /tmp/iso639-3.tab                  SIL table (Part1<->Id map)
Reads macro_map.json next to this script; backs up index_data.csv before writing.

Counting matches apply_keyman.py: keyman_keyboards_n = # distinct keyboard ids
tagging the language (after stripping script/region subtags), plus macro_map
credit of macrolanguage keyboards to their standard individual variety.
"""
import csv, json, os, shutil, datetime, sys
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CSV = os.path.join(ROOT, "index_data.csv")
COL = "keyman_keyboards_n"

def arg(flag, default):
    return sys.argv[sys.argv.index(flag) + 1] if flag in sys.argv else default
CATALOGUE = arg("--catalogue", "/tmp/keyman_full_catalogue.json")
ISO639 = arg("--iso639", "/tmp/iso639-3.tab")

# 1. 639-1 -> 639-3 map + valid 639-3 set
iso_rows = list(csv.DictReader(open(ISO639), delimiter="\t"))
p1to3 = {r["Part1"]: r["Id"] for r in iso_rows if r["Part1"]}
valid3 = {r["Id"] for r in iso_rows}
def to_iso3(tag):
    b = tag.split("-")[0].strip().lower()
    if len(b) == 2: return p1to3.get(b)
    if len(b) == 3 and b in valid3: return b
    return None

# 2. distinct keyboard ids per 639-3 code
cat = json.load(open(CATALOGUE))
if not cat:
    sys.exit("catalogue is empty -- fetch it first (search/2.0 enumeration)")
kb_by_iso = defaultdict(set)
for kid, tags in cat.items():
    for t in tags:
        i3 = to_iso3(t)
        if i3: kb_by_iso[i3].add(kid)
print(f"catalogue keyboards: {len(cat)} | distinct 639-3 langs covered: {len(kb_by_iso)}")

# 3. credit macrolanguage keyboards to the standard individual variety
macro_map = json.load(open(os.path.join(HERE, "macro_map.json")))
for macro, std in macro_map.items():
    if macro in kb_by_iso:
        kb_by_iso[std] |= kb_by_iso[macro]
def count_for(iso): return len(kb_by_iso.get(iso, set()))

# 4. backup
stamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
backup = os.path.join(HERE, f"index_data.backup_{stamp}.csv")
shutil.copy2(CSV, backup)

# 5. rewrite the COL column in place (it is the last column), preserving width
with open(CSV, newline="") as f: raw = f.readlines()
hdr = [h.strip() for h in next(csv.reader([raw[0]], skipinitialspace=True))]
iso_i, col_i, ncol = hdr.index("iso_code"), hdr.index(COL), len(hdr)
assert col_i == ncol - 1, f"{COL} must be the last column"
width = len(raw[1].rstrip("\n").rsplit(",", 1)[1])  # current field width (e.g. 19)

changed = []
for n in range(1, len(raw)):
    if not raw[n].strip(): continue
    fields = next(csv.reader([raw[n]], skipinitialspace=True))
    iso = fields[iso_i].strip().lower()
    old = int(fields[col_i]) if fields[col_i].strip().lstrip("-").isdigit() else 0
    new = count_for(iso)
    if new != old: changed.append((fields[2].strip(), iso, old, new))
    head = raw[n].rstrip("\n").rsplit(",", 1)[0]
    raw[n] = f"{head},{str(new).rjust(width)}\n"
with open(CSV, "w", newline="") as f: f.writelines(raw)

# 6. verify + report
with open(CSV, newline="") as f:
    r = csv.reader(f, skipinitialspace=True); next(r)
    bad = sum(1 for row in r if len(row) != ncol)
total = sum(1 for l in raw[1:] if l.strip())
nonzero = sum(1 for l in raw[1:] if l.strip() and int(l.rstrip().rsplit(",", 1)[1]) > 0)
newly = [c for c in changed if c[2] == 0 and c[3] > 0]
lost = [c for c in changed if c[2] > 0 and c[3] == 0]
print(f"backup: {backup}")
print(f"rows: {total} | with keyman>0: {nonzero} ({100*nonzero/total:.1f}%) | bad col count: {bad}")
print(f"changed rows: {len(changed)} | newly nonzero (0->n): {len(newly)} | dropped to 0: {len(lost)}")
changed.sort(key=lambda c: -(c[3] - c[2]))
print("\nTop 25 increases:")
for nm, iso, o, nw in changed[:25]:
    print(f"  {iso:5} {nm[:32]:32} {o:>4} -> {nw}")
if lost:
    print(f"\nWARNING {len(lost)} rows dropped to 0 (mapping gaps?): {[(c[1]) for c in lost[:20]]}")
