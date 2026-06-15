#!/usr/bin/env python3
"""Backfill blank writing_script values from internal evidence of written use.

Ethnologue's `Writing` field is blank for ~45% of our languages -- including
major ones like Russian (its Ethnologue Writing field is genuinely empty). A
blank there means "no data", not "unwritten". But many of those languages
plainly DO have a writing system, evidenced by resources we already track that
cannot exist without an established orthography.

Rule (applied only to rows where writing_script is currently blank):
  set writing_script = "Yes" if ANY reliable TEXT signal is present:
      bible_exists == 1     (a published Bible translation needs an orthography)
      wiki_articles_n > 0   (a Wikipedia)
      cc_gb > 0             (Common Crawl web text)
      opus_gb > 0           (OPUS parallel text corpora)
      keyman_keyboards_n>0  (a keyboard layout needs a script)

Deliberately NOT used:
  dictionary_exists  -- constant 1 for every row (meaningless as populated)
  wikitongues_gb     -- oral video, does not imply a script
  models_n/datasets_n-- ambiguous (may be speech-only ASR/TTS)

Explicit Ethnologue "Yes"/"No" are left untouched (Ethnologue's "Unwritten"
judgement is kept even where a Keyman keyboard exists -- those conflicts are
reported, not overridden). Rows with no signal stay blank (truly unknown).

Updates the existing writing_script column IN PLACE (it is the last column).
A timestamped backup is written next to this script first.
"""
import csv, os, shutil, datetime
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
CSV = os.path.join(ROOT, "index_data.csv")


def main():
    with open(CSV, newline="") as f:
        raw = f.readlines()

    header = [h.strip() for h in next(csv.reader([raw[0]], skipinitialspace=True))]
    assert header[-1] == "writing_script", f"writing_script must be last col, got {header[-1]!r}"
    col = {h: i for i, h in enumerate(header)}

    def num(fields, c):
        try:
            return float(fields[col[c]].strip())
        except (ValueError, IndexError):
            return 0.0

    def reliable_text_signal(fields):
        return (fields[col["bible_exists"]].strip() == "1"
                or num(fields, "wiki_articles_n") > 0
                or num(fields, "cc_gb") > 0
                or num(fields, "opus_gb") > 0
                or num(fields, "keyman_keyboards_n") > 0)

    # macrolanguage -> Yes if the macro itself or any sibling individual variety
    # is written (a regional variety shares its macrolanguage's script).
    iso_ws = {}
    for line in raw[1:]:
        if not line.strip():
            continue
        f = next(csv.reader([line], skipinitialspace=True))
        iso_ws[f[col["iso_code"]].strip()] = f[col["writing_script"]].strip()
    member2macro, macro_members = {}, {}
    mtab = os.path.join(ROOT, "keyman_integration", "iso639_macro.tab")
    with open(mtab) as f:
        rd = csv.reader(f, delimiter="\t"); next(rd)
        for row in rd:
            if len(row) >= 2:
                member2macro[row[1].strip()] = row[0].strip()
                macro_members.setdefault(row[0].strip(), set()).add(row[1].strip())

    def macro_written(iso):
        macro = member2macro.get(iso)
        if not macro:
            return False
        return iso_ws.get(macro) == "Yes" or any(iso_ws.get(s) == "Yes" for s in macro_members.get(macro, ()))

    stamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    backup = os.path.join(HERE, f"index_data.backup_{stamp}.csv")
    shutil.copy2(CSV, backup)

    out = [raw[0]]
    filled = 0
    filled_macro = 0
    conflicts = []   # explicit "No" but has a text signal
    for line in raw[1:]:
        if not line.strip():
            out.append(line)
            continue
        fields = next(csv.reader([line], skipinitialspace=True))
        cur = fields[col["writing_script"]].strip()

        if cur == "No" and reliable_text_signal(fields):
            conflicts.append(fields[col["language_name"]].strip())

        newval = cur
        if cur == "" and reliable_text_signal(fields):
            newval = "Yes"
            filled += 1
        elif cur == "" and macro_written(fields[col["iso_code"]].strip()):
            newval = "Yes"
            filled_macro += 1

        body = line.rstrip("\n").rstrip("\r")
        before, _, _old = body.rpartition(",")
        out.append(f"{before},{newval}\n")

    with open(CSV, "w", newline="") as f:
        f.writelines(out)

    # report
    with open(CSV, newline="") as f:
        r = csv.reader(f, skipinitialspace=True)
        hdr = [h.strip() for h in next(r)]
        wi = hdr.index("writing_script")
        rows = list(r)
    dist = Counter(row[wi].strip() or "(blank)" for row in rows)
    print(f"backup: {backup}")
    print(f"blanks backfilled to Yes via reliable text signals: {filled}")
    print(f"blanks backfilled to Yes via macrolanguage inheritance: {filled_macro}")
    print("writing_script distribution now:")
    for k, v in dist.most_common():
        print(f"  {v:5d}  {k}")
    print(f"\nNOTE: {len(conflicts)} rows are Ethnologue 'No' (Unwritten) yet have a text "
          f"signal (kept as No). e.g. {conflicts[:6]}")


if __name__ == "__main__":
    main()
