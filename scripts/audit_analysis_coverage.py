#!/usr/bin/env python3
"""Build exhaustive input-deck and simulation-result analysis coverage indexes."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

import table2_gate


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "Examples/YeGhasemmi2018"
DEFAULT_OUTPUT = ROOT / "doc/independent_analysis"
SAMPLES = ("SWT1", "SWT2", "SWS3", "SWS4")


def is_true(value: object) -> bool:
    return value is True or str(value).strip().lower() == "true"


def result_files() -> list[Path]:
    files: list[Path] = []
    for sample in SAMPLES:
        files.extend((EXAMPLES / sample).glob("results_csv*/*.csv"))
    return sorted(files)


def mapped_deck(path: Path) -> Path | None:
    try:
        return table2_gate.find_deck(path, "biot_ab_20260815")
    except SystemExit:
        return None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=True)

    ranking = pd.read_csv(DEFAULT_OUTPUT / "TABLE2_ERROR_ACCURACY_RANKING.csv")
    ranked_sources = {
        str((ROOT / source).resolve()): row
        for source, (_, row) in zip(ranking["source_csv"], ranking.iterrows())
    }
    ranked_cases = {row["case"]: row for _, row in ranking.iterrows()}
    discussion = pd.read_csv(DEFAULT_OUTPUT / "DISCUSSION_101_RUN_INDEX.csv")
    discussion_cases = {row["case"]: row for _, row in discussion.iterrows()}

    result_rows: list[dict] = []
    results_for_deck: dict[str, list[dict]] = {}
    for path in result_files():
        relative = str(path.relative_to(ROOT))
        deck = mapped_deck(path)
        deck_relative = str(deck.relative_to(ROOT)) if deck else ""
        stem = path.stem[:-4] if path.stem.endswith("_hpc") else path.stem
        source_key = str(path.resolve())

        if source_key in ranked_sources:
            row = ranked_sources[source_key]
            status = "table2_ranked" if is_true(row["comparable_for_ranking"]) else "table2_partial"
            artifact = "TABLE2_ERROR_ACCURACY_RANKING.csv"
        elif stem in discussion_cases:
            row = discussion_cases[stem]
            status = "discussion_101_" + str(row["analysis_status"])
            artifact = "DISCUSSION_101_RUN_INDEX.csv"
        elif stem.startswith(("97_", "98_")):
            status = "superseded_discussion_run"
            artifact = "CONSOLIDATED_ANALYSIS_2026-08-18.md"
        elif stem.startswith(("87_01_", "88_02_", "88_03_")):
            status = "retired_invalid_do_not_score"
            artifact = "MEMORY.md"
        elif path.name.endswith("_table2.csv") or path.name in {
            "sws3_final_ab.csv", "sws3_stage6_ab.csv"
        }:
            status = "derived_summary_not_simulation"
            artifact = ""
        elif deck and deck.stem in ranked_cases:
            status = "duplicate_or_cross_machine_repeat"
            artifact = "CONSOLIDATED_ANALYSIS_2026-08-18.md"
        else:
            status = "unindexed_result"
            artifact = ""

        item = {
            "sample": table2_gate.detect_sample(path),
            "result_csv": relative,
            "mapped_input_deck": deck_relative,
            "analysis_status": status,
            "analysis_artifact": artifact,
        }
        result_rows.append(item)
        if deck:
            results_for_deck.setdefault(str(deck.resolve()), []).append(item)

    deck_rows: list[dict] = []
    for sample in SAMPLES:
        for deck in sorted((EXAMPLES / sample).glob("*.i")):
            stem = deck.stem
            linked = results_for_deck.get(str(deck.resolve()), [])
            if stem in ranked_cases:
                row = ranked_cases[stem]
                status = "table2_ranked" if is_true(row["comparable_for_ranking"]) else "table2_partial"
                artifact = "TABLE2_ERROR_ACCURACY_RANKING.csv"
            elif stem in discussion_cases:
                row = discussion_cases[stem]
                status = "discussion_101_" + str(row["analysis_status"])
                artifact = "DISCUSSION_101_RUN_INDEX.csv"
            elif stem.startswith(("97_", "98_")) and linked:
                status = "superseded_discussion_run"
                artifact = "CONSOLIDATED_ANALYSIS_2026-08-18.md"
            elif stem.startswith(("87_01_", "88_02_", "88_03_")) and linked:
                status = "retired_invalid_do_not_score"
                artifact = "MEMORY.md"
            elif linked:
                statuses = sorted({item["analysis_status"] for item in linked})
                status = ";".join(statuses)
                artifact = ";".join(sorted({item["analysis_artifact"] for item in linked if item["analysis_artifact"]}))
            else:
                status = "no_result_available"
                artifact = ""
            deck_rows.append({
                "sample": sample,
                "input_deck": str(deck.relative_to(ROOT)),
                "result_file_count": len(linked),
                "result_files": ";".join(item["result_csv"] for item in linked),
                "analysis_status": status,
                "analysis_artifact": artifact,
            })

    # The material-property comparison intentionally covers only the four scientific
    # campaign directories.  Still enumerate every other repository .i file so an
    # "all inputs" audit cannot silently omit verification tests or future decks.
    campaign_inputs = {str((ROOT / row["input_deck"]).resolve()) for row in deck_rows}
    for deck in sorted(ROOT.rglob("*.i")):
        if ".git" in deck.parts or str(deck.resolve()) in campaign_inputs:
            continue
        relative = deck.relative_to(ROOT)
        is_test = relative.parts[:2] == ("test", "tests")
        deck_rows.append({
            "sample": "TEST" if is_test else "NON_CAMPAIGN",
            "input_deck": str(relative),
            "result_file_count": 0,
            "result_files": "",
            "analysis_status": (
                "software_verification_test_not_campaign"
                if is_test
                else "unclassified_non_campaign_input"
            ),
            "analysis_artifact": "test/tests" if is_test else "",
        })

    result_frame = pd.DataFrame(result_rows)
    deck_frame = pd.DataFrame(deck_rows)
    result_frame.to_csv(output / "RESULT_FILE_ANALYSIS_COVERAGE.csv", index=False)
    deck_frame.to_csv(output / "INPUT_DECK_ANALYSIS_COVERAGE.csv", index=False)

    print(f"repository input files: {len(deck_frame)}")
    print(deck_frame["analysis_status"].value_counts().to_string())
    print(f"result CSVs: {len(result_frame)}")
    print(result_frame["analysis_status"].value_counts().to_string())
    unindexed = result_frame[result_frame["analysis_status"] == "unindexed_result"]
    if not unindexed.empty:
        print("ERROR: unindexed simulation results remain")
        print(unindexed["result_csv"].to_string(index=False))
        return 1
    unclassified_inputs = deck_frame[
        deck_frame["analysis_status"] == "unclassified_non_campaign_input"
    ]
    if not unclassified_inputs.empty:
        print("ERROR: unclassified non-campaign input files remain")
        print(unclassified_inputs["input_deck"].to_string(index=False))
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
