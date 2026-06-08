#!/usr/bin/env python3
"""Append language_ecology_primary_type directly to index_data.csv.

This preserves the existing space-padded CSV formatting by appending one field
to each raw line. A timestamped backup is written in this folder first.
"""

from __future__ import annotations

import csv
import datetime
import shutil
from pathlib import Path

from apply_language_ecology import classify


HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
INDEX_PATH = ROOT / "index_data.csv"
NEW_COLUMN = "language_ecology_primary_type"


def clean(value: str | None) -> str:
    return (value or "").strip()


def main() -> None:
    stamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    backup = HERE / f"index_data.backup_before_language_ecology_{stamp}.csv"
    shutil.copy2(INDEX_PATH, backup)

    raw_lines = INDEX_PATH.read_text(encoding="utf-8").splitlines(keepends=True)
    header_fields = next(csv.reader([raw_lines[0]], skipinitialspace=True))
    stripped_header = [clean(field) for field in header_fields]

    if NEW_COLUMN in stripped_header:
        print(f"{NEW_COLUMN} already exists in index_data.csv; no changes made.")
        print(f"Backup retained at {backup.relative_to(ROOT)}")
        return

    out = [raw_lines[0].rstrip("\n").rstrip("\r") + f",{NEW_COLUMN}\n"]

    for line in raw_lines[1:]:
        if not line.strip():
            out.append(line)
            continue
        fields = next(csv.reader([line], skipinitialspace=True))
        row = dict(zip(stripped_header, [clean(field) for field in fields]))
        ecology_type = classify(row)[NEW_COLUMN]
        out.append(line.rstrip("\n").rstrip("\r") + f",{ecology_type}\n")

    INDEX_PATH.write_text("".join(out), encoding="utf-8")

    print(f"Appended {NEW_COLUMN} to index_data.csv")
    print(f"Backup written to {backup.relative_to(ROOT)}")


if __name__ == "__main__":
    main()

