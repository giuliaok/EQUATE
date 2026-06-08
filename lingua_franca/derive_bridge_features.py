#!/usr/bin/env python3
"""
Derive lingua-franca / bridge-language features for EQUATE.

Addresses the contact/bridge-language point raised by all three reviewers
(Bird 2022). Two constructs:

  (A) BRIDGE ACCESS  -- for each language, the AI-readiness of the de-facto
      lingua franca its community uses. Rebuts R3: "unavailability of AI for
      language X doesn't mean AI hasn't been adopted in the area; people use
      the local lingua franca."

  (B) BRIDGE STATUS  -- does a language itself serve as a bridge, and for how
      many languages / speakers. Rebuts R2: "a factor accounting for whether
      this was a bridge language, and the size of the population it supports."

Operationalization (no hand-curated table; fully derived from the data):
  The bridge language of a country is the highest-AI_resource_readiness
  language spoken there (primary OR other country). Each language's bridge is
  the bridge of its PRIMARY country.

Writes lingua_franca/bridge_languages.csv and prints rebuttal-oriented stats.
Does NOT modify index_data.csv.
"""
import csv, re, os
from collections import defaultdict

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "..", "index_data.csv")
OUT = os.path.join(HERE, "bridge_languages.csv")


def load():
    with open(SRC, newline="") as f:
        r = csv.reader(f, skipinitialspace=True)
        header = [h.strip() for h in next(r)]
        rows = [row for row in r]
    return header, rows


def main():
    header, rows = load()
    idx = {h: i for i, h in enumerate(header)}

    def g(row, col):
        return row[idx[col]].strip()

    def fnum(row, col):
        try:
            return float(g(row, col))
        except ValueError:
            return 0.0

    def ai_rr(row):
        try:
            return float(g(row, "AI_resource_readiness"))
        except ValueError:
            return -1.0

    def countries_of(row):
        s = {g(row, "country_iso_code")}
        for c in re.split(r"[-,;]", g(row, "other_country_iso_codes")):
            c = c.strip()
            if c:
                s.add(c)
        return {c for c in s if c}

    # ----- bridge per country = max AI_rr co-territorial language -----
    by_country = defaultdict(list)
    for row in rows:
        for cc in countries_of(row):
            by_country[cc].append(row)

    # Backstop: the major world lingua francas as official/working languages of
    # countries that the raw `other_country_iso_codes` lists miss (English's list
    # is already comprehensive; the others are patchy, which otherwise lets a tiny
    # local language win the max-AI_rr tiebreak -- e.g. Mossi for Burkina Faso).
    # Curated, auditable by a sociolinguist (Giulia). ISO 639-3 -> official countries.
    LF_OFFICIAL = {
        "fra": "FRA BEL CHE LUX MCO CAN HTI BEN BFA BDI CMR CAF TCD COM COG COD "
               "CIV DJI GNQ GAB GIN MDG MLI NER RWA SEN SYC TGO VUT".split(),
        "spa": "ESP MEX GTM HND SLV NIC CRI PAN CUB DOM COL VEN ECU PER BOL PRY "
               "CHL ARG URY GNQ".split(),
        "por": "PRT BRA AGO MOZ GNB CPV STP TLS GNQ".split(),
        "arb": "DZA BHR TCD COM DJI EGY IRQ JOR KWT LBN LBY MRT MAR OMN PSE QAT "
               "SAU SOM SDN SYR TUN ARE YEM".split(),
        "rus": "RUS BLR KAZ KGZ".split(),
        "cmn": "CHN TWN SGP".split(),
        "zsm": "MYS BRN SGP".split(),
        "pes": "IRN".split(),
        "prs": "AFG".split(),
        "hin": "IND".split(),
        "swh": "TZA KEN UGA COD".split(),
        "tur": "TUR CYP".split(),
    }
    row_by_iso = {g(row, "iso_code"): row for row in rows}
    for lf_iso, ccs in LF_OFFICIAL.items():
        lf_row = row_by_iso.get(lf_iso)
        if lf_row is None:
            continue
        for cc in ccs:
            if lf_row not in by_country[cc]:
                by_country[cc].append(lf_row)

    bridge = {}  # country -> (name, iso, AI_rr)
    for cc, langs in by_country.items():
        best = max(langs, key=ai_rr)
        bridge[cc] = (g(best, "language_name"), g(best, "iso_code"), ai_rr(best))

    # ----- per-language bridge (A) via PRIMARY country -----
    lang_bridge = {}  # iso -> (b_name, b_iso, b_ai_rr)
    for row in rows:
        iso = g(row, "iso_code")
        lang_bridge[iso] = bridge[g(row, "country_iso_code")]

    # ----- bridge status (B): who does each bridge serve -----
    n_bridged = defaultdict(int)        # bridge_iso -> # of OTHER langs served
    spk_bridged = defaultdict(float)    # bridge_iso -> speakers of those langs
    for row in rows:
        iso = g(row, "iso_code")
        b_name, b_iso, b_rr = lang_bridge[iso]
        if b_iso != iso:  # don't count a bridge serving itself
            n_bridged[b_iso] += 1
            spk_bridged[b_iso] += fnum(row, "n_speakers")

    # ----- write output -----
    out_header = ["iso_code", "language_name", "primary_country", "n_speakers",
                  "models_n", "own_AI_resource_readiness",
                  "bridge_lang_iso", "bridge_lang_name", "bridge_AI_resource_readiness",
                  "is_bridge_language", "n_languages_bridged", "speakers_bridged"]
    with open(OUT, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(out_header)
        for row in rows:
            iso = g(row, "iso_code")
            b_name, b_iso, b_rr = lang_bridge[iso]
            is_bridge = 1 if n_bridged.get(iso, 0) > 0 else 0
            w.writerow([
                iso, g(row, "language_name"), g(row, "country_iso_code"),
                g(row, "n_speakers"), g(row, "models_n"),
                f"{ai_rr(row):.6f}",
                b_iso, b_name, f"{b_rr:.6f}",
                is_bridge, n_bridged.get(iso, 0), int(spk_bridged.get(iso, 0.0)),
            ])

    # ================= REBUTTAL-ORIENTED SUMMARY =================
    MAJOR_LF = {"eng", "fra", "spa", "por", "arb", "rus", "cmn", "hin", "ind", "deu"}
    n = len(rows)

    print(f"== Coverage ==")
    print(f"languages: {n}   countries with derived bridge: {len(bridge)}")

    # (A) For languages with ~no own AI resources, how good is their bridge?
    own_zero = [row for row in rows if fnum(row, "models_n") == 0]
    print(f"\n== (A) Bridge access for the {len(own_zero)} languages with 0 own HF models ==")
    buckets = {"major global LF (eng/fra/spa/...)": 0,
               "other high bridge (AI_rr>=0.05)": 0,
               "low bridge (AI_rr 0.005-0.05)": 0,
               "double-excluded (bridge AI_rr<0.005)": 0}
    for row in own_zero:
        _, b_iso, b_rr = lang_bridge[g(row, "iso_code")]
        if b_iso in MAJOR_LF:
            buckets["major global LF (eng/fra/spa/...)"] += 1
        elif b_rr >= 0.05:
            buckets["other high bridge (AI_rr>=0.05)"] += 1
        elif b_rr >= 0.005:
            buckets["low bridge (AI_rr 0.005-0.05)"] += 1
        else:
            buckets["double-excluded (bridge AI_rr<0.005)"] += 1
    for k, v in buckets.items():
        print(f"  {v:5d}  ({100*v/len(own_zero):4.1f}%)  {k}")

    # speakers behind double exclusion
    dbl = [row for row in own_zero
           if lang_bridge[g(row, "iso_code")][2] < 0.005
           and lang_bridge[g(row, "iso_code")][1] not in MAJOR_LF]
    print(f"\n  'Double-excluded' languages (no own models AND weak bridge): {len(dbl)}")
    print(f"  total speakers behind them: {int(sum(fnum(row,'n_speakers') for row in dbl)):,}")

    # (B) Top bridges
    print(f"\n== (B) Top bridge languages by # languages bridged ==")
    name_of = {g(row, "iso_code"): g(row, "language_name") for row in rows}
    for b_iso, cnt in sorted(n_bridged.items(), key=lambda kv: kv[1], reverse=True)[:15]:
        print(f"  {b_iso}  {name_of.get(b_iso,'?')[:24]:24} "
              f"langs={cnt:4d}  speakers_bridged={int(spk_bridged[b_iso]):>14,}")

    print(f"\nWrote {OUT}")


if __name__ == "__main__":
    main()
