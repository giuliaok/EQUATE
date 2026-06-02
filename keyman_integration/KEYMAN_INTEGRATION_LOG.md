# Keyman Keyboard Data

Date: 2026-06-02.

## The column

`index_data.csv` has one Keyman column: `keyman_keyboards_n`.

It is the number of distinct Keyman keyboards available for the language. A value greater than 0 means at least one Keyman keyboard exists; 0 means none.

Source: the Keyman keyboard catalogue at https://keyman.com (SIL-affiliated). Each language is matched to Keyman by its ISO 639-3 code (`iso_code`). Every one of the 6,003 rows has a value.

## Coverage

880 of 6,003 languages (14.7%) have at least one Keyman keyboard. Counts for well-resourced languages:

| Language | iso_code | keyman_keyboards_n |
|---|---|---|
| English | eng | 12 |
| Hindi | hin | 6 |
| Western Farsi (Persian) | pes | 5 |
| Standard Latvian | lvs | 4 |
| Standard Arabic | arb | 4 |
| Estonian | ekk | 3 |
| Mandarin Chinese | cmn | 1 |

## How to read the macrolanguage cases

Keyman tags some keyboards with a broad macrolanguage code (for example `ara` for Arabic), while the dataset uses specific individual-language codes (for example `arb` for Standard Arabic). Two rules apply.

When a macrolanguage has one standard written variety, its keyboards count toward that variety. So a keyboard Keyman labels `ara` counts for Standard Arabic (`arb`). The 12 such cases:

| Keyman code | Counts toward | Variety |
|---|---|---|
| ara | arb | Standard Arabic |
| fas | pes | Western Farsi (Iranian Persian) |
| est | ekk | Estonian |
| lav | lvs | Standard Latvian |
| swa | swh | Swahili (coastal standard) |
| grn | gug | Paraguayan Guarani |
| kau | knc | Central Kanuri |
| sqi | als | Tosk Albanian (basis of Standard Albanian) |
| zha | zyb | Yongbei Zhuang (basis of Standard Zhuang) |
| doi | dgo | Dogri |
| ori | ory | Odia |
| ipk | esi | North Alaskan Inupiatun |

When a macrolanguage is a cover term spanning many varieties with no single standard, its generic keyboards are not counted toward any one variety. These varieties may therefore show 0 even though a generic keyboard exists for the group:

Quechua, Zapotec, Romani, Fula, Tuareg, Pashto, Oromo, Aymara, Balochi, Sardinian, Gondi, Manding, Lahnda, Kpelle, and Syriac/Neo-Aramaic.

## Regenerate

```bash
python3 keyman_integration/apply_keyman.py
```

This rebuilds `keyman_keyboards_n` from `keyman_keyboards.json` (the saved catalogue) and `macro_map.json` (the 12 mappings above), backing up `index_data.csv` first. The other files in this folder are the inputs and the record of how the macrolanguage decisions were made.
