# MED (Most Extensive Description) integration

Adds one column to `index_data.csv`:

```text
med_type
```

`med_type` is Glottolog's **Most Extensive Description** category — the
descriptive-status of each language, i.e. the most substantial piece of
documentation that exists for it. It is a clean, citable measure of *how well
documented* a language is, independent of how endangered it is (`endangerment_status`)
or how AI-ready it is. Added 2026-06-15.

Why it matters for the paper: reviewers (R2/R3, citing Nigatu et al. 2024 and
Bird 2022) asked us to account for **linguistic documentation** as a readiness
factor. `med_type` pairs with `endangerment_status` to reproduce Glottolog's
GlottoScope MED×AES view, and lets us show that a language can be well
documented (`long grammar`) yet have no usable AI — and vice versa.

## Categories

Glottolog's five ordered MED levels (most → least extensive), verbatim from
<https://glottolog.org/langdoc/status>:

| med_type | definition |
|---|---|
| `long grammar`    | grammar with more than 300 pages |
| `grammar`         | grammar with less than 300 pages |
| `grammar sketch`  | grammar sketch |
| `phonology/text`  | New Testament, text, phonology, study of a specific feature, **or** dictionary |
| `Wordlist or less`| wordlist or less |

(Strings are kept exactly as Glottolog publishes them, including the capital `W`
in `Wordlist or less` and the slash in `phonology/text`.)

## Source data (traceable)

- Authoritative source: **glottolog-cldf**, file `cldf/values.csv`, rows where
  `Parameter_ID == "med"`; code→label map from `cldf/codes.csv`.
  Pulled 2026-06-15 from
  `https://raw.githubusercontent.com/glottolog/glottolog-cldf/master/cldf/values.csv`
  and `.../cldf/codes.csv`.
- Cached in this folder so the join is reproducible **without re-downloading**:
  - `med_by_glottocode.csv` — `glottocode, med_type, med_code` for **9,317**
    glottocodes (every languoid Glottolog assigns a MED).
  - `glottolog_med_codes.csv` — the raw `codes.csv` (med code → label).

Join key: **`glottocode`** (Glottolog's identifier, present on every index row —
including the contact-language rows that lack an ISO code).

## Files

- `apply_med.py` — appends `med_type` to `index_data.csv`.
- `med_by_glottocode.csv`, `glottolog_med_codes.csv` — cached source data.
- `index_data.backup_<timestamp>.csv` — backup made before the edit.

## Exact method

```sh
python3 med_integration/apply_med.py
```

The script:

1. Writes a timestamped backup into `med_integration/` first.
2. Builds `glottocode -> med_type` from `med_by_glottocode.csv`.
3. Reads `index_data.csv` raw lines, parsing each with
   `csv.reader(..., skipinitialspace=True)` (the file is space-padded), to read
   `glottocode`.
4. Appends `med_type` to the end of each line, preserving the existing
   space-padded formatting (same convention as `keyman_integration/apply_keyman.py`).
5. Verifies column-count consistency and prints coverage.

## Results (2026-06-15 run)

Coverage: **5,984 / 6,003 (99.7%)** matched by glottocode.

```text
1779  long grammar
1586  grammar sketch
 920  phonology/text
 906  grammar
 793  Wordlist or less
  19  (blank)
```

The **19 blank** rows are glottocodes Glottolog does not assign a MED to —
constructed / historical / very recent languoids (e.g. Interlingua,
Old Turkish, Haitian Vodoun Culture Language). They are left empty (not guessed).
Re-run the script to print the full list.

## Caveats

- A MED reflects documentation *about* a language by anyone; it is **not**
  evidence that the language is written or used in writing by its community
  (see `writing_script_integration/` for that).
- Tied to a Glottolog release; re-pull `med_by_glottocode.csv` to update.
