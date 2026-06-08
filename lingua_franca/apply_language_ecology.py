#!/usr/bin/env python3
"""Append Bird-style language ecology labels to the EQUATE index.

This script intentionally writes a derived CSV instead of modifying
`index_data.csv`. The classification is heuristic and should be framed as a
sensitivity/context layer, not as ground truth about a community's wishes.
"""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INDEX_PATH = ROOT / "index_data.csv"
OUTPUT_PATH = ROOT / "index_data_with_language_ecology.csv"


APPENDED_COLUMNS = [
    "is_standardized_language",
    "is_local_language",
    "is_bridge_language",
    "language_ecology_primary_type",
    "language_ecology_confidence",
    "language_ecology_evidence",
]


ENDANGERED_STATUSES = {
    "endangered/unsafe",
    "definitely endangered",
    "potentially vulnerable",
    "severely endangered",
    "critically endangered",
    "not in use",
}


# Curated high-level bridge/contact languages. This is deliberately conservative:
# languages not listed here can still be classified as bridge-like if their
# country spread and speaker count are large enough.
CURATED_BRIDGE_ISOS = {
    "eng",  # English
    "fra",  # French
    "spa",  # Spanish
    "por",  # Portuguese
    "rus",  # Russian
    "ara",  # Arabic macrolanguage
    "arb",  # Standard Arabic
    "cmn",  # Mandarin Chinese
    "zho",  # Chinese macrolanguage
    "hin",  # Hindi
    "urd",  # Urdu
    "ben",  # Bengali
    "ind",  # Indonesian
    "msa",  # Malay macrolanguage
    "swh",  # Swahili
    "swa",  # Swahili macrolanguage
    "hau",  # Hausa
    "amh",  # Amharic
    "fas",  # Persian macrolanguage
    "pes",  # Iranian Persian
    "tur",  # Turkish
    "deu",  # German
    "ita",  # Italian
    "nld",  # Dutch
    "jpn",  # Japanese
    "kor",  # Korean
    "vie",  # Vietnamese
    "tha",  # Thai
    "tgl",  # Tagalog
    "fil",  # Filipino
}


def clean(value: str | None) -> str:
    return (value or "").strip()


def numeric(value: str | None, default: float = 0.0) -> float:
    try:
        return float(clean(value))
    except ValueError:
        return default


def read_index() -> list[dict[str, str]]:
    with INDEX_PATH.open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f, skipinitialspace=True)
        reader.fieldnames = [clean(name) for name in reader.fieldnames or []]
        return [{clean(k): clean(v) for k, v in row.items()} for row in reader]


def country_spread(row: dict[str, str]) -> int:
    countries = set()
    if clean(row.get("country_iso_code")):
        countries.add(clean(row.get("country_iso_code")))
    for code in clean(row.get("other_country_iso_codes")).split("-"):
        if code:
            countries.add(code)
    return len(countries)


def classify(row: dict[str, str]) -> dict[str, str]:
    iso = clean(row.get("iso_code")).lower()
    speakers = numeric(row.get("n_speakers"))
    countries = country_spread(row)
    institutional = clean(row.get("institutional_status")) == "1"
    endangered = clean(row.get("endangerment_status")).lower() in ENDANGERED_STATUSES

    dictionary = numeric(row.get("dictionary_exists")) > 0
    bible = numeric(row.get("bible_exists")) > 0
    keyboards = numeric(row.get("keyman_keyboards_n")) > 0
    wiki_articles = numeric(row.get("wiki_articles_n"))
    models = numeric(row.get("models_n"))
    datasets = numeric(row.get("datasets_n"))

    standardized_score = 0
    standardized_evidence = []
    if institutional:
        standardized_score += 3
        standardized_evidence.append("institutional_status=1")
    if dictionary:
        standardized_score += 1
        standardized_evidence.append("dictionary_exists")
    if bible:
        standardized_score += 1
        standardized_evidence.append("bible_exists")
    if wiki_articles >= 1000:
        standardized_score += 1
        standardized_evidence.append("wiki_articles_n>=1000")
    if wiki_articles >= 10000:
        standardized_score += 1
        standardized_evidence.append("wiki_articles_n>=10000")
    if keyboards:
        standardized_score += 1
        standardized_evidence.append("keyman_keyboards_n>0")
    if speakers >= 1_000_000 and not endangered:
        standardized_score += 1
        standardized_evidence.append("speakers>=1M_and_not_endangered")

    strong_noninstitutional_standard_proxy = (
        not institutional
        and dictionary
        and keyboards
        and wiki_articles >= 10000
        and speakers >= 1_000_000
    )
    is_standardized = institutional or strong_noninstitutional_standard_proxy

    bridge_score = 0
    bridge_evidence = []
    if iso in CURATED_BRIDGE_ISOS:
        bridge_score += 4
        bridge_evidence.append("curated_global_or_regional_bridge_iso")
    if countries >= 5 and speakers >= 10_000_000:
        bridge_score += 2
        bridge_evidence.append("country_spread>=5_and_speakers>=10M")
    if countries >= 10:
        bridge_score += 1
        bridge_evidence.append("country_spread>=10")
    if institutional and countries >= 3:
        bridge_score += 1
        bridge_evidence.append("institutional_and_multicountry")

    is_bridge = bridge_score >= 3

    local_score = 0
    local_evidence = []
    if not institutional:
        local_score += 1
        local_evidence.append("institutional_status=0")
    if endangered:
        local_score += 2
        local_evidence.append("endangered_or_not_in_use")
    if speakers < 1_000_000:
        local_score += 1
        local_evidence.append("speakers<1M")
    if countries <= 2:
        local_score += 1
        local_evidence.append("country_spread<=2")
    if models == 0 and datasets == 0:
        local_score += 1
        local_evidence.append("models_n=0_and_datasets_n=0")

    is_local = local_score >= 3 and not is_bridge

    if is_bridge and is_standardized:
        primary = "standardized_bridge"
    elif is_bridge:
        primary = "bridge"
    elif is_local and is_standardized:
        primary = "local_standardized"
    elif is_standardized:
        primary = "standardized"
    elif is_local:
        primary = "local"
    else:
        primary = "uncertain"

    confidence_score = max(standardized_score if is_standardized else 0, bridge_score if is_bridge else 0, local_score if is_local else 0)
    if confidence_score >= 5:
        confidence = "high"
    elif confidence_score >= 3:
        confidence = "medium"
    else:
        confidence = "low"

    evidence = []
    if standardized_evidence:
        evidence.append("standardized:" + "|".join(standardized_evidence))
    if bridge_evidence:
        evidence.append("bridge:" + "|".join(bridge_evidence))
    if local_evidence:
        evidence.append("local:" + "|".join(local_evidence))

    return {
        "is_standardized_language": "1" if is_standardized else "0",
        "is_local_language": "1" if is_local else "0",
        "is_bridge_language": "1" if is_bridge else "0",
        "language_ecology_primary_type": primary,
        "language_ecology_confidence": confidence,
        "language_ecology_evidence": "; ".join(evidence),
    }


def main() -> None:
    rows = read_index()
    header = list(rows[0].keys()) + APPENDED_COLUMNS

    counts: dict[str, int] = {}
    with OUTPUT_PATH.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=header)
        writer.writeheader()
        for row in rows:
            ecology = classify(row)
            counts[ecology["language_ecology_primary_type"]] = counts.get(ecology["language_ecology_primary_type"], 0) + 1
            writer.writerow({**row, **ecology})

    print(f"Wrote {OUTPUT_PATH.relative_to(ROOT)}")
    for key in sorted(counts):
        print(f"{key}: {counts[key]}")


if __name__ == "__main__":
    main()
