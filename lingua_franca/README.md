# Language Ecology Primary Type

This folder adds one sociolinguistic context column to `index_data.csv`:

```text
language_ecology_primary_type
```

The column is a heuristic Bird-style ecology label. It is intended to help the
paper avoid treating all languages as the same kind of unit. A model count or
resource count means something different for a standardized national language, a
local/minority language, or a bridge/contact language used for wider access.

## Files

- `apply_language_ecology.py`: computes ecology labels from the existing
  `index_data.csv` fields.
- `apply_primary_ecology_to_index.py`: appends only
  `language_ecology_primary_type` directly to `index_data.csv`.
- `index_data.backup_before_language_ecology_*.csv`: timestamped backup made
  before the direct edit.

## Exact Method Used

I appended `language_ecology_primary_type` to `index_data.csv` with:

```sh
python3 lingua_franca/apply_primary_ecology_to_index.py
```

That script:

1. Creates a timestamped backup in `lingua_franca/`.
2. Reads `index_data.csv` using `csv.reader(..., skipinitialspace=True)`,
   because the CSV is space-padded.
3. Preserves the existing raw CSV formatting by appending one field to each raw
   line rather than rewriting the full file.
4. Calls `classify(row)` from `apply_language_ecology.py`.
5. Writes only one new column: `language_ecology_primary_type`.

## Label Values

The possible values are:

```text
standardized_bridge
bridge
local_standardized
standardized
local
uncertain
```

Current distribution after integration:

```text
local: 5697
local_standardized: 244
standardized: 34
standardized_bridge: 23
uncertain: 3
bridge: 2
```

## Classification Rules

The classifier computes three internal signals: standardized, bridge, and local.
Only the final primary type is written into `index_data.csv`.

### Standardized Signal

A language is treated as standardized if either:

- `institutional_status == 1`, or
- it has a strong non-institutional standard proxy:
  `dictionary_exists`, `keyman_keyboards_n > 0`, `wiki_articles_n >= 10000`,
  and `n_speakers >= 1000000`.

Other fields are recorded as evidence inside the script, but these are the
decisive conditions.

### Bridge Signal

A language is treated as a bridge language if its bridge score is at least 3.
The score comes from:

- `+4` if its ISO code is in the curated global/regional bridge list.
- `+2` if it is used across at least 5 countries and has at least 10 million
  speakers.
- `+1` if it is used across at least 10 countries.
- `+1` if it has institutional status and is used across at least 3 countries.

The curated bridge ISO list is defined in `apply_language_ecology.py`.

### Local Signal

A language is treated as local if its local score is at least 3 and it is not a
bridge language. The score comes from:

- `+1` if `institutional_status == 0`.
- `+2` if the language is endangered, unsafe, vulnerable, severely endangered,
  critically endangered, or not in use.
- `+1` if `n_speakers < 1000000`.
- `+1` if country spread is at most 2.
- `+1` if `models_n == 0` and `datasets_n == 0`.

Country spread is computed from `country_iso_code` plus
`other_country_iso_codes`.

## Primary Type Selection

The final label is assigned in this order:

1. standardized + bridge -> `standardized_bridge`
2. bridge only -> `bridge`
3. local + standardized -> `local_standardized`
4. standardized only -> `standardized`
5. local only -> `local`
6. otherwise -> `uncertain`

## Framing for the Paper

Describe this as a reproducible heuristic ecology layer, not as ground truth
about community preferences. It should be used to contextualize the index and
reviewer response, not as proof that a community wants direct LLM support or
that bridge-language access replaces direct language support.

---

# EGIDS-grounded ecology: `egids_level` + `ecology_egids_type`

The heuristic `language_ecology_primary_type` above is a homemade point score,
which is hard to defend to a reviewer ("how did you get these numbers?"). This
is a **data-backed replacement**, grounded in Ethnologue's **Language Status =
EGIDS** (Expanded Graded Intergenerational Disruption Scale; Lewis & Simons
2010). Both columns are added by `apply_ecology_egids.py`; the old column is left
intact for comparison.

- `egids_level` — the bare EGIDS scale code only: `0,1,2,3,4,5,6a,6b,7,8a,8b,9,10`
  (blank if Ethnologue has no / "Unestablished" status).
- `ecology_egids_type` — the derived label, same vocabulary as the heuristic
  column: `standardized_bridge | bridge | local_standardized | local`.

EGIDS level meanings: 0 International, 1 National, 2 Provincial, 3 Wider
Communication, 4 Educational, 5 Developing, 6a Vigorous, 6b Threatened,
7 Shifting, 8a Moribund, 8b Nearly extinct, 9 Dormant, 10 Extinct.

## Source & join

Ethnologue `Language Status`, joined by **ISO 639-3** (taken from each
Ethnologue page URL `/language/<iso>`; the `iso_639_3` column is empty).
Coverage: **3,977 / 6,003** have an EGIDS level; 2,026 blank.

**Copyright:** only the bare EGIDS level *code* is stored — never Ethnologue's
verbatim status prose. The EGIDS scale itself is published methodology
(Lewis & Simons 2010). Cite Ethnologue (Eberhard, Simons & Fennig) + EGIDS.

## How `ecology_egids_type` is derived

Every input is named — no opaque scoring:

- **standardized** = `egids_level` in {0,1,2,3,4,5} (institutional … developing);
  OR, when `egids_level` is blank, `institutional_status == 1`. (This fallback
  rescues major languages whose EGIDS is missing/"Unestablished" in this CSV,
  e.g. French, Spanish, Swahili.)
- **bridge** = `egids_level` in {0,1,2,3} (wider-communication tiers);
  OR used across **≥ 5 countries**;
  OR (`institutional_status == 1` AND used across ≥ 3 countries).
- **label**:
  - standardized & bridge → `standardized_bridge`
  - bridge only → `bridge`
  - standardized & not bridge → `local_standardized`
  - otherwise → `local`

Country spread = distinct countries in `country_iso_code` +
`other_country_iso_codes`. `n_speakers` is deliberately **not** used (it carries
placeholder sentinels).

**Current setting (option A):** EGIDS 3 (Wider Communication) counts as
standardized, so contact/trade languages land in `standardized_bridge` and the
plain `bridge` label is empty. Option B (move EGIDS 3 out of standardized) would
relabel those as `bridge`.

## Results

Distribution: `local` 4,772 · `local_standardized` 1,165 ·
`standardized_bridge` 66.

Agreement with the heuristic `language_ecology_primary_type`: **same label for
82%** of languages, **differ for 18%** (under 20%). ~945 of the differences are
`local → local_standardized` — languages the heuristic missed but that EGIDS
records as standardized/developing.

## Reproduce

```sh
python3 lingua_franca/apply_ecology_egids.py
```

Backs up `index_data.csv` into `lingua_franca/` first, then appends the two
columns (preserving the space-padded formatting).
