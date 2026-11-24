# EQUATE

**A composite index of language equity in data and technology.**

EQUATE measures how equitably the world's languages are represented across the
data, models, and infrastructure that modern language technology is built on.
It brings together dozens of heterogeneous sources into a
single, interpretable, per-language index, together with the code to collect
the underlying data, compute the index, and analyse it geographically and over
time.

> **Note on provenance.** This repository contains the 
> analysis pipeline. The large raw and intermediate data files are **not**
> tracked here (they are sizeable and governed by the terms of their original
> sources); scripts and notebooks read them from a local `data/` directory. See
> [`data/README.md`](data/README.md) for the expected layout.

---

## Table of contents

- [What EQUATE measures](#what-equate-measures)
- [Repository structure](#repository-structure)
- [The pipeline](#the-pipeline)
- [Data sources](#data-sources)
- [Installation](#installation)
- [Reproducing the index](#reproducing-the-index)
- [Longitudinal analyses](#longitudinal-analyses)
- [Conventions & notes](#conventions--notes)
- [Citation](#citation)
- [License](#license)

---

## What EQUATE measures

Each language is described by a set of features that are organised into three
thematic **feature groups**:

| Group        | What it captures                                   | Example features |
|--------------|----------------------------------------------------|------------------|
| **Technical** | Availability of data and models for the language  | Common Crawl volume, # HuggingFace models, OPUS volume, documentation-archive volume, speech-corpus hours, Bible availability |
| **Internet**  | Connectivity and digital infrastructure           | % households with phones / home internet, average download speed, % individuals using the internet, cybersecurity legislation |
| **Language**  | Socio-linguistic and socio-economic standing      | institutional status, # speakers, Wikipedia active users, literacy rate, subnational GDP / HDI / education, R&D spend |

The index is computed in `index/index_computation/`:

1. **Normalisation.** Skewed count features (corpus volumes, model counts,
   speaker counts, …) are log-transformed; binary features (Bible exists,
   cybersecurity law exists, institutional status) are kept as indicators.
2. **Correlation merging.** Within each group, features correlated above a
   threshold (0.85) are merged so that redundant signals are not double-counted.
3. **Rank-based weighting.** Features are ranked within their group and given
   normalised linear weights (highest rank → highest weight).
4. **Aggregation.** A per-group index and a combined **full index** are produced
   for every language.

The result is a per-language score (and per-group sub-scores) that can be mapped
geographically and tracked through time.

---

## Repository structure

```
EQUATE/
├── index/                          # Build the index: fetch → clean → combine → compute
│   ├── index_data_fetching/        #   1. Collect raw data from each source
│   │   ├── UNESCO/                 #      UNESCO language profiles (scraper + driver)
│   │   ├── Wikitongues/            #      Wikitongues video durations
│   │   ├── bibles/                 #      Bible translation availability
│   │   ├── universities/           #      University locations near speaker regions
│   │   ├── language_speakers_counts/   #  Speaker counts & endangerment (Wikidata/UNESCO)
│   │   ├── typological_similarities/   #  URIEL+ featural typological distances
│   │   └── documentation_archives/ #      Language archives: ELAR, PARADISEC, AILLA,
│   │                               #      Pangloss, Kaipuleohone, California Lang. Archive, DOBES
│   ├── index_data_cleanup+interpolation/   # 2. Clean, standardise & interpolate features
│   │   └── log.md                  #      Human-readable record of cleanup decisions
│   ├── all_data_combination.ipynb  # 3. Merge every source into one per-language table
│   └── index_computation/          # 4. Weighting & index calculation
│       ├── full_index_calculations.ipynb
│       └── group-wise_index.ipynb
│
├── huggingface_longitudinal_work/  # HuggingFace models/datasets, over time (Wayback + commits)
│   ├── huggingface_*.ipynb         #   counts, models, datasets, commit exploration
│   ├── *.py / *.sh                 #   scrapers + batch drivers (rate-limit aware)
│   └── wayback_work/               #   language time series reconstructed from the Wayback Machine
│
├── analysis/                       # Paper analyses & figures
│   ├── geographical_mapping.ipynb  #   map the index onto world geography
│   ├── longitudinal_analyses.ipynb #   trends over time
│   └── gompertz.ipynb              #   Gompertz technology-adoption curves
│
├── data/                           # (git-ignored) expected inputs — see data/README.md
├── requirements.txt
├── CITATION.cff
└── LICENSE
```

---

## The pipeline

The index is produced in four stages. Within `index/`, run them in this order:

```
index_data_fetching/           →  index_data_cleanup+interpolation/
        ↓                                      ↓
  raw per-source data                 cleaned, interpolated features
                      ↘                       ↙
                   all_data_combination.ipynb
                              ↓
                    index_computation/   →   per-language EQUATE index
                              ↓
                        analysis/        →   maps, trends, figures
```

1. **Fetch** (`index_data_fetching/`) — each sub-folder is self-contained and
   collects one source. Scrapers are deliberately **rate-limit aware**: the
   HuggingFace and archive crawlers sleep between batches, and large jobs are
   split into CSV chunks processed by the accompanying `*.sh` drivers.
2. **Clean & interpolate** (`index_data_cleanup+interpolation/`) — standardise
   column names, reconcile ISO/Glottocodes, fill gaps (e.g. literacy, internet
   speed, STEM-graduate shares) and handle edge cases such as small island
   nations. `log.md` documents the manual decisions.
3. **Combine** (`all_data_combination.ipynb`) — join all sources into a single
   per-language matrix keyed by language.
4. **Compute** (`index_computation/`) — apply the weighting scheme above to
   produce the full and group-wise indices.

---

## Data sources

EQUATE integrates (among others):

- **Models & datasets** — HuggingFace Hub (model/dataset counts, downloads,
  likes, commit history), reconstructed over time via the Wayback Machine.
- **Text corpora** — Common Crawl, OPUS, Wikipedia (article counts, active
  users), MADLAD, PanLex.
- **Speech & documentation archives** — ELAR, PARADISEC, AILLA, Pangloss,
  Kaipuleohone, the California Language Archive, DOBES, Wikitongues, XEUS.
- **Linguistic metadata** — Glottolog, URIEL+ (typological distances),
  institutional status, endangerment status, ACL Anthology coverage, Bible
  translations.
- **Demographics & socio-economics** — speaker counts (Wikidata, Ethnologue,
  UNESCO), universities, subnational GDP / HDI / education, R&D expenditure,
  age structure, literacy.
- **Connectivity** — ITU indicators, World Bank series (broadband, phones,
  computers), national/subnational internet speeds, ICT and cybersecurity
  policy.

Please consult and comply with each source's terms of use and licensing when
re-collecting or redistributing data (!!)

---

## Installation

Requires **Python 3.10+**.

```bash
# (recommended) create an isolated environment
python -m venv .venv && source .venv/bin/activate

pip install -r requirements.txt
```

A few notebooks additionally use `dask-geopandas` (installed via
`requirements.txt`) and the `parallel` GNU utility for the chunked shell
drivers. `urielplus` downloads typological databases on first use.

---

## Reproducing the index

1. Populate `data/` with the required inputs (see
   [`data/README.md`](data/README.md)). The chunked scrapers can point at a
   custom data directory via an environment variable:

   ```bash
   DATA_DIR=/path/to/data ./huggingface_longitudinal_work/HF.sh
   DATA_DIR=/path/to/data ./index/index_data_fetching/UNESCO/unesco.sh
   ```

2. Run the cleanup/interpolation notebooks in
   `index/index_data_cleanup+interpolation/`.
3. Run `index/all_data_combination.ipynb` to build the merged table.
4. Run the notebooks in `index/index_computation/` to compute the index.
5. Explore and visualise with the notebooks in `analysis/`.

---

## Longitudinal analyses

`huggingface_longitudinal_work/` reconstructs how language coverage on the
HuggingFace Hub evolved over time, combining:

- **Wayback snapshots** (`wayback_work/`) for historical per-language counts, and
- **commit-level exploration** (`commits_explorer_timely.py`,
  `huggingface_commits_explorer.ipynb`) for the timing of contributions.

`analysis/gompertz.ipynb` fits **Gompertz adoption curves** to technology and
connectivity indicators (mobile phones, fixed broadband, personal computers,
EVs) to characterise diffusion dynamics.

---


## Citation

If you use EQUATE, please cite the accompanying paper. A machine-readable
citation is provided in [`CITATION.cff`](CITATION.cff); please complete the
author and venue fields before release.

```bibtex
@article{occhini2026artificial,
  title={Artificial intelligence is creating a new global linguistic hierarchy},
  author={Occhini, Giulia and Tanaka-Ishii, Kumiko and Barford, Anna and Tikochinski, Refael and Hu, Songbo and Reichart, Roi and Zhou, Yijie and Claus, Hannah and Petti, Ulla and Vuli{\'c}, Ivan and others},
  journal={arXiv preprint arXiv:2602.12018},
  year={2026}
}

```

---

## License

Released under the [MIT License](LICENSE). 
