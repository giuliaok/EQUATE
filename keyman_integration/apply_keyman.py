#!/usr/bin/env python3
"""Add Keyman keyboard-availability columns to index_data.csv.

Joins the Keyman cloud keyboard catalogue (keyed by ISO 639-3) onto the
language index by iso_code. Macrolanguage codes used by Keyman are credited
to their standard individual variety via macro_map.json (see KEYMAN_INTEGRATION_LOG.md).

Adds one column:
  keyman_keyboards_n     count of distinct Keyman keyboards available
                         (a keyboard exists for the language iff this is > 0)

Reads:  keyman_keyboards.json, macro_map.json (alongside this script),
        index_data.csv (in the repo root, the parent directory)
Writes: index_data.csv in the repo root (a timestamped backup is made
        next to this script first)

Run from anywhere: paths are resolved relative to this file's location.
"""
import csv, json, os, shutil, datetime
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CSV = os.path.join(ROOT, "index_data.csv")
NEW_COLS = ["keyman_keyboards_n"]

# 1. distinct keyboard ids per base ISO 639-3 code
kb_by_iso = defaultdict(set)
kb = json.load(open(os.path.join(HERE, "keyman_keyboards.json")))["keyboards"]
for k in kb:
    kid = k["id"]
    for l in k.get("languages", []):
        base = l["id"].strip().lower().split("-")[0]
        kb_by_iso[base].add(kid)

# 2. credit macrolanguage keyboards to the standard individual variety
macro_map = json.load(open(os.path.join(HERE, "macro_map.json")))  # {macro_iso: standard_iso}
for macro, std in macro_map.items():
    if macro in kb_by_iso:
        kb_by_iso[std] |= kb_by_iso[macro]

def count_for(iso):
    return len(kb_by_iso.get(iso, set()))

# 3. backup (kept next to this script, not in the repo root)
stamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
backup = os.path.join(HERE, f"index_data.backup_{stamp}.csv")
shutil.copy2(CSV, backup)

# 4. read raw lines; parse each robustly (skipinitialspace) to get iso_code
with open(CSV, newline="") as f:
    raw = f.readlines()

# locate iso_code index from header (stripped)
header_fields = next(csv.reader([raw[0]], skipinitialspace=True))
iso_idx = [h.strip() for h in header_fields].index("iso_code")

out = []
# header: append new column names (match the file's existing un-padded style for new cols)
out.append(raw[0].rstrip("\n").rstrip("\r") + "," + ",".join(NEW_COLS) + "\n")

matched_rows = 0
for line in raw[1:]:
    if not line.strip():
        out.append(line)
        continue
    fields = next(csv.reader([line], skipinitialspace=True))
    iso = fields[iso_idx].strip().lower()
    n = count_for(iso)
    if n:
        matched_rows += 1
    body = line.rstrip("\n").rstrip("\r")
    out.append(f"{body},{n}\n")

with open(CSV, "w", newline="") as f:
    f.writelines(out)

# 5. verify + report
with open(CSV, newline="") as f:
    r = csv.reader(f, skipinitialspace=True)
    hdr = next(r)
    ncol = len(hdr)
    bad = sum(1 for row in r if len(row) != ncol)

total = len(raw) - 1
print(f"backup written: {backup}")
print(f"columns now: {ncol} (added {len(NEW_COLS)})")
print(f"rows: {total}, rows with keyman_keyboards_n>0: {matched_rows} ({100*matched_rows/total:.1f}%)")
print(f"rows with inconsistent column count after write: {bad}")
print(f"macrolanguage mappings applied: {len(macro_map)} -> {macro_map}")
