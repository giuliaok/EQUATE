# EQUATE — added columns in `index_data.csv`

`index_data.csv` has one row per language (6,003 languages). This note explains
the six columns added on top of the core index, what they contain, how they were
worked out (in plain terms), and their basic counts.

Full method, scripts, and sources for each are in the matching folders:
`keyman_integration/`, `lingua_franca/`, `med_integration/`,
`writing_script_integration/`.

| column | what it is | how it was derived (simple) |
|---|---|---|
| `keyman_keyboards_n` | how many Keyman keyboards exist for the language | counted from the Keyman keyboard catalogue, matched by language code (ISO 639-3) |
| `language_ecology_primary_type` | older "kind of language" label | a rule-of-thumb score from columns we already had — *superseded by `ecology_egids_type`* |
| `med_type` | how well the language is documented | copied from Glottolog's documentation rating, matched by glottocode |
| `writing_script` | does the language have a writing system? | from Ethnologue, plus sensible fill-ins where Ethnologue is blank |
| `egids_level` | the language's place on the standard EGIDS scale | taken from Ethnologue's "Language Status" |
| `ecology_egids_type` | data-backed "kind of language" label | worked out from `egids_level` + official status + number of countries |

---

## `keyman_keyboards_n`
Number of digital keyboards available for the language.

**How:** counted from the published Keyman keyboard catalogue, matched to each
language by its ISO 639-3 code.

**Stats:** 1,831 languages (31%) have at least one keyboard; the rest have 0. The
most for any language is 34. (A low number for a big language usually means it
already has good built-in keyboards elsewhere, so few were built in Keyman.)

## `language_ecology_primary_type`  *(older — kept for comparison)*
A label for the kind of language: `local`, `local_standardized`, `standardized`,
`standardized_bridge`, `bridge`, `uncertain`.

**How:** an early rule-of-thumb score built from columns we already had (official
status, keyboards, Wikipedia size, speaker numbers, number of countries). It is
**not strongly backed by outside data**, so it has been replaced by
`ecology_egids_type` (below). Kept only so the two can be compared.

**Stats:** local 5,697 · local_standardized 244 · standardized 34 ·
standardized_bridge 23 · uncertain 3 · bridge 2.

## `med_type`
Glottolog's "Most Extensive Description" — how much documentation exists for the
language, from a full grammar down to just a wordlist.

**How:** taken straight from Glottolog, matched by glottocode. Values are
Glottolog's own categories.

**Stats:** long grammar 1,779 · grammar sketch 1,586 · phonology/text 920 ·
grammar 906 · wordlist or less 793 · blank 19 (Glottolog has no rating).

## `writing_script`
Does the language have a writing system? `Yes`, `No`, or blank (unknown).

**How:** from Ethnologue's "Writing" field (`Yes` = a script is listed, `No` =
"Unwritten"). Where Ethnologue is blank, we mark `Yes` if the language clearly
has written material — a Bible, a Wikipedia, web text, or a keyboard — or shares
a script with its larger (macro)language. Left blank when nothing tells us
either way (blank means *no data*, not "unwritten").

**Stats:** Yes 3,641 · No 591 · blank 1,771.

## `egids_level`
The language's level on the EGIDS scale, a standard measure of how a language is
used (0 = international, 1 = national, … 6a = vigorous everyday use, … 10 =
extinct).

**How:** taken from Ethnologue's "Language Status". Only the short scale code is
stored (e.g. `5`, `6a`), not Ethnologue's text.

**Stats:** 3,977 languages have a level; 2,026 are blank (Ethnologue gives no
established status).

## `ecology_egids_type`  *(newer — data-backed)*
The data-backed version of `language_ecology_primary_type`. Same labels, but
grounded in the EGIDS scale: `standardized_bridge`, `local_standardized`,
`local`.

**How:** worked out from `egids_level` plus two facts already in the index —
whether the language is official, and how many countries it is used in:
- used across many countries / a language of wider communication → a **bridge**;
- institutional or developing (EGIDS 0–5) → **standardized**;
- everything else → **local**.

**Stats:** local 4,772 · local_standardized 1,165 · standardized_bridge 66.

**Compared with the old `language_ecology_primary_type`:** the two labels agree
for **82%** of languages and differ for **18%** (under 20%). Almost all of that
difference — **945 languages** — is `local` → `local_standardized`: languages the
old rule-of-thumb missed but that EGIDS records as standardized/developing.

---

## Sources & credit
- Keyboards: **Keyman** keyboard catalogue.
- Documentation rating: **Glottolog** (Most Extensive Description).
- Writing system, language status: **Ethnologue** (Eberhard, Simons & Fennig) —
  only short codes / derived labels are stored, not Ethnologue's text.
- EGIDS scale: **Lewis & Simons (2010)**.
