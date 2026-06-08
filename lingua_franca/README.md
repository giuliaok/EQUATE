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
