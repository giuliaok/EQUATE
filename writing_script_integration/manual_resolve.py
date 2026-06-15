#!/usr/bin/env python3
"""Apply hand-verified writing_script resolutions for sizable languages that
Ethnologue's Writing field left blank.

Each entry records the SOURCE so the call is auditable for the paper:
  wikidata = Wikidata writing-system property (P282) for the language's ISO 639-3
  ethnologue = a script/orthography signal in Ethnologue's non-Writing fields
  web = a per-language source (noted inline)

Updates the existing writing_script column IN PLACE (last column). Only fills
rows whose writing_script is currently blank (never overrides Yes/No).
A timestamped backup is written next to this script first.
"""
import csv, os, shutil, datetime

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CSV = os.path.join(ROOT, "index_data.csv")

# iso 639-3 -> (writing_script, source note)
RESOLUTIONS = {
    # Wikidata P282 writing system present
    "sou": ("Yes", "wikidata: Thai script"),
    "byo": ("Yes", "wikidata: Miao script"),
    "tzo": ("Yes", "wikidata: Latin script"),
    "smw": ("Yes", "wikidata: Latin script"),
    "swi": ("Yes", "wikidata: Sui script"),
    "uum": ("Yes", "wikidata: Cyrillic/Greek"),
    "sly": ("Yes", "wikidata: Latin script"),
    "yky": ("Yes", "wikidata: Latin script"),
    "wne": ("Yes", "wikidata: Arabic alphabet"),
    # Ethnologue non-Writing fields
    "onb": ("Yes", "ethnologue: Chinese characters w/ Lingao reading"),
    "mfp": ("Yes", "ethnologue: dictionary"),
    "gew": ("Yes", "ethnologue: Arabic script mentioned"),
    "akg": ("Yes", "ethnologue: texts"),
    "btz": ("Yes", "ethnologue: dictionary"),
}


def main():
    with open(CSV, newline="") as f:
        raw = f.readlines()
    header = [h.strip() for h in next(csv.reader([raw[0]], skipinitialspace=True))]
    assert header[-1] == "writing_script", header[-1]
    col = {h: i for i, h in enumerate(header)}

    stamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    backup = os.path.join(HERE, f"index_data.backup_{stamp}.csv")
    shutil.copy2(CSV, backup)

    applied, skipped = [], []
    out = [raw[0]]
    for line in raw[1:]:
        if not line.strip():
            out.append(line)
            continue
        fields = next(csv.reader([line], skipinitialspace=True))
        iso = fields[col["iso_code"]].strip()
        cur = fields[col["writing_script"]].strip()
        newval = cur
        if iso in RESOLUTIONS:
            val, _ = RESOLUTIONS[iso]
            if cur == "":
                newval = val
                applied.append(iso)
            else:
                skipped.append((iso, cur))
        body = line.rstrip("\n").rstrip("\r")
        before, _, _old = body.rpartition(",")
        out.append(f"{before},{newval}\n")

    with open(CSV, "w", newline="") as f:
        f.writelines(out)

    print(f"backup: {backup}")
    print(f"applied {len(applied)} resolutions: {applied}")
    if skipped:
        print(f"skipped (already had a value): {skipped}")


if __name__ == "__main__":
    main()
