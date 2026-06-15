#!/usr/bin/env python3
"""Add the Glottolog MED (Most Extensive Description) column to index_data.csv.

Joins Glottolog's MED classification (the descriptive-status of each languoid,
https://glottolog.org/langdoc/status) onto the language index by `glottocode`.

Adds one column:
  med_type   Glottolog Most Extensive Description category, one of:
               long grammar | grammar | grammar sketch | phonology/text |
               Wordlist or less
             Blank if the glottocode is not in Glottolog's MED set
             (e.g. constructed or historical languoids).

Source data: med_by_glottocode.csv (cached from glottolog-cldf cldf/values.csv,
parameter `med`; see glottolog_med_codes.csv for the code->label mapping).

Mirrors keyman_integration/apply_keyman.py: reads raw lines and appends the new
field to the end of each line, preserving the file's space-padded formatting.
A timestamped backup is written next to this script first.
"""
import csv, os, shutil, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CSV = os.path.join(ROOT, "index_data.csv")
NEW_COLS = ["med_type"]

# 1. glottocode -> MED label
g2med = {}
with open(os.path.join(HERE, "med_by_glottocode.csv"), newline="") as f:
    for row in csv.DictReader(f):
        g2med[row["glottocode"]] = row["med_type"]

# 2. backup (kept next to this script, not in the repo root)
stamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
backup = os.path.join(HERE, f"index_data.backup_{stamp}.csv")
shutil.copy2(CSV, backup)

# 3. read raw lines; parse each robustly (skipinitialspace) to get glottocode
with open(CSV, newline="") as f:
    raw = f.readlines()

header_fields = next(csv.reader([raw[0]], skipinitialspace=True))
g_idx = [h.strip() for h in header_fields].index("glottocode")

out = [raw[0].rstrip("\n").rstrip("\r") + "," + ",".join(NEW_COLS) + "\n"]

matched = 0
unmatched = []
for line in raw[1:]:
    if not line.strip():
        out.append(line)
        continue
    fields = next(csv.reader([line], skipinitialspace=True))
    gc = fields[g_idx].strip()
    med = g2med.get(gc, "")
    if med:
        matched += 1
    else:
        unmatched.append((gc, fields[3].strip() if len(fields) > 3 else ""))
    body = line.rstrip("\n").rstrip("\r")
    out.append(f"{body},{med}\n")

with open(CSV, "w", newline="") as f:
    f.writelines(out)

# 4. verify + report
with open(CSV, newline="") as f:
    r = csv.reader(f, skipinitialspace=True)
    hdr = next(r)
    ncol = len(hdr)
    rows = list(r)
    bad = sum(1 for row in rows if len(row) != ncol)

from collections import Counter
total = len(rows)
print(f"backup written: {backup}")
print(f"columns now: {ncol} (added {len(NEW_COLS)})")
print(f"rows: {total}, matched MED: {matched} ({100*matched/total:.1f}%), unmatched: {len(unmatched)}")
print(f"rows with inconsistent column count after write: {bad}")
print("med_type distribution:")
for k, v in Counter(g2med.get(row[g_idx].strip(), "(blank)") for row in rows).most_common():
    print(f"  {v:5d}  {k}")
if unmatched:
    print(f"\nunmatched glottocodes ({len(unmatched)}) left blank:")
    for gc, nm in unmatched:
        print(f"  {gc:14} {nm}")
