# Writing-script integration

Adds one column to `index_data.csv`:

```text
writing_script    Yes | No | (blank)
```

`writing_script` records whether a language has a **writing system / established
script**. Added 2026-06-15.

- `Yes` — the language has an attested script / written form.
- `No`  — the language is explicitly **unwritten**.
- blank — genuinely unknown (no source records writing status). Blank means
  *no data*, **not** "unwritten".

Why it matters for the paper: R3 (and R1/R2, citing Bird 2022) argued that the
**absence of standardized writing practices** is a major, ignored hindrance to
AI-readiness. `writing_script` makes that explicit and pairs with `med_type`
(a language can be well documented yet have no community script).

## Sources & method (in the order applied)

The column is built in three passes. To reproduce from scratch, start from an
`index_data.csv` that does **not** yet have `writing_script` and run them in
order:

```sh
python3 writing_script_integration/apply_writing_script.py      # 1. Ethnologue base (appends column)
python3 writing_script_integration/backfill_writing_script.py   # 2. resource + macrolanguage backfill (in place)
python3 writing_script_integration/manual_resolve.py            # 3. hand-verified resolutions (in place)
```

Each script writes a timestamped backup into this folder first.

### 1. `apply_writing_script.py` — Ethnologue (primary source)

- Source: `ethnologue_languages.csv` (repo root), the **`Writing`** field
  (e.g. `"Latin script [Latn]."`, `"Unwritten [Qaax]."`).
- Join key: **ISO 639-3**, taken from each Ethnologue row's page URL
  (`/language/<iso>`) — the CSV's `iso_639_3` column is empty.
- Classification: contains a script → `Yes`; `Unwritten` → `No`; blank → `""`.
- Result: **Yes 2,682 / No 591 / blank 2,730**.

Ethnologue's `Writing` field is blank for ~45% of our languages — *including
major ones* (Russian's Ethnologue `Writing` field is genuinely empty). Blank
there is missing data, which is why passes 2–3 exist.

### 2. `backfill_writing_script.py` — internal evidence + macrolanguage

Fills **blank** rows only (never overrides Ethnologue Yes/No).

- **Reliable text signals → `Yes`** (each *requires* an orthography to exist):
  `bible_exists==1`, `wiki_articles_n>0`, `cc_gb>0`, `opus_gb>0`,
  `keyman_keyboards_n>0`. → **+919**.
- **Macrolanguage inheritance → `Yes`**: a blank variety inherits `Yes` if its
  ISO 639-3 macrolanguage (or any sibling variety) is written. Uses
  `keyman_integration/iso639_macro.tab`. → **+26** (e.g. Southern Uzbek, Min
  Zhong Chinese, Zhuang varieties).

Deliberately **not** used as signals, and why:
- `dictionary_exists` — a **dead column**: it is `1` for all 6,003 rows.
- `wikitongues_gb` — oral video, does not imply a script.
- `models_n` / `datasets_n` — ambiguous (may be speech-only ASR/TTS).

Kept, not overridden: **106** rows are Ethnologue `No` (Unwritten) yet have a
Keyman keyboard (nascent / revitalization orthographies). We keep Ethnologue's
`No` and only report these.

### 3. `manual_resolve.py` — hand-verified resolutions

Resolves sizable languages still blank, with a **source recorded per language**
in the script's `RESOLUTIONS` dict (auditable). 14 resolutions:

- **Wikidata** writing-system property (P282), queried 2026-06-15 by ISO 639-3:
  `sou` (Thai), `byo` (Miao), `tzo`/`smw`/`sly`/`yky` (Latin), `swi` (Sui),
  `uum` (Cyrillic/Greek), `wne` (Arabic).
- **Ethnologue** non-`Writing` fields: `onb` (Chinese characters), `mfp`/`btz`
  (dictionary), `gew` (Arabic), `akg` (texts).

## Final distribution (2026-06-15)

```text
Yes      3,641      (2,682 Ethnologue + 919 text-signal + 26 macro + 14 verified)
No         591      (Ethnologue "Unwritten")
(blank)  1,771
```

Blanks went 2,730 → 1,771 (−35%); every major language resolves.

## Remaining blanks (1,771) — deliberately left unknown

- **~1,745 tiny / dormant languages** (median ~500 speakers, mostly
  *Definitely endangered* / *Not in use*). Plausibly unwritten, but unconfirmable;
  `blank` is the honest label.
- **26 medium regional languages** (>100k real speakers, Phu Thai 870k → Tolaki
  120k) for which **no** structured source (Wikidata P282, Ethnologue, resource
  columns) records writing status. Not force-labelled. List is reproducible from
  the data (blank `writing_script` AND `n_speakers > 100000`).

Policy decision (chosen with the team): resolve the authoritatively-verifiable
big ones; leave the genuinely-undocumented remainder blank rather than guess
`No` (which would mislabel written-but-resource-poor varieties).

## Data-quality flags found during this work

- **`dictionary_exists` is constant `1`** for all 6,003 rows — currently
  meaningless; not used here.
- **`n_speakers` contains placeholder/sentinel values** (`999999` ×140,
  `9999999` ×42, `99999` ×360, …; ~550+ rows). Filter these when using speaker
  counts.

## Files

- `apply_writing_script.py` — pass 1 (Ethnologue base, appends column).
- `backfill_writing_script.py` — pass 2 (text-signal + macrolanguage backfill).
- `manual_resolve.py` — pass 3 (hand-verified resolutions, with sources).
- `index_data.backup_<timestamp>.csv` — backups (one per run).
