#!/usr/bin/env python3
"""Read-only audit of the curated Ye and Ghassemi (2018) paper cases."""

from __future__ import annotations

import csv
from pathlib import Path


ROOT = Path(__file__).resolve().parent
CASES = ROOT / "Paper_Cases"


REQUIRED = {
    "main validation": [
        "01_Main_Validation/SWT1/BB/107_01_swt1_coh27p2_apscale0p01512_ppfix.i",
        "01_Main_Validation/SWT1/BB/107_01_swt1_coh27p2_apscale0p01512_ppfix.csv",
        "01_Main_Validation/SWT1/MC/SWT1_OrcaMohrCoulombContactTraction.i",
        "01_Main_Validation/SWT1/MC/SWT1_OrcaMohrCoulombContactTraction.sh",
        "01_Main_Validation/SWT1/MC/SWT1_OrcaMohrCoulombContactTraction_pb04.csv",
        "01_Main_Validation/SWT2/BB/100_04_swt2_apscale0p0177_ppfix.i",
        "01_Main_Validation/SWT2/BB/100_04_swt2_apscale0p0177_ppfix_hpc.csv",
        "01_Main_Validation/SWT2/MC/SWT2_OrcaMohrCoulombContactTraction.i",
        "01_Main_Validation/SWT2/MC/SWT2_OrcaMohrCoulombContactTraction.sh",
        "01_Main_Validation/SWT2/MC/SWT2_OrcaMohrCoulombContactTraction_pb04.csv",
        "01_Main_Validation/SWS3/BB/100_06_sw3_resc1p30_unld0p00_ppfix.i",
        "01_Main_Validation/SWS3/BB/100_06_sw3_resc1p30_unld0p00_ppfix_hpc.csv",
        "01_Main_Validation/SWS3/MC/SWS3_OrcaMohrCoulombContactTraction.i",
        "01_Main_Validation/SWS3/MC/SWS3_OrcaMohrCoulombContactTraction.sh",
        "01_Main_Validation/SWS3/MC/SWS3_OrcaMohrCoulombContactTraction_pb06.csv",
        "01_Main_Validation/SWS4/BB/93_07_sw4_final_theta30_jrc5_ppfix.i",
        "01_Main_Validation/SWS4/BB/93_07_sw4_final_theta30_jrc5_ppfix_hpc.csv",
        "01_Main_Validation/SWS4/MC/SWS4_OrcaMohrCoulombContactTraction.i",
        "01_Main_Validation/SWS4/MC/SWS4_OrcaMohrCoulombContactTraction.sh",
        "01_Main_Validation/SWS4/MC/SWS4_OrcaMohrCoulombContactTraction_center.csv",
    ],
    "mechanism tests": [
        *[f"02_Mechanism_Tests/SWS4_109/{kind}/109_0{i}_sw4_{name}" for i, name in [(1, "floor1nm_g028_ppfix"), (2, "floor1nm_g042_ppfix"), (3, "floor1nm_nodilation_ppfix")] for kind in ("inputs", "results")],
        *[f"02_Mechanism_Tests/SWS3_110/{kind}/110_0{i}_sw3_{name}" for i, name in [(1, "floor1nm_g040_ppfix"), (2, "floor1nm_nodilation_ppfix"), (3, "floor1nm_nogouge_ppfix")] for kind in ("inputs", "results")],
        *[f"02_Mechanism_Tests/SWT1_111/{kind}/111_0{i}_swt1_{name}" for i, name in [(1, "floor1nm_control_ppfix"), (2, "floor1nm_nokinematic_ppfix")] for kind in ("inputs", "results")],
        *[f"02_Mechanism_Tests/SWT2_111/{kind}/111_0{i}_swt2_{name}" for i, name in [(3, "floor1nm_control_ppfix"), (4, "floor1nm_nokinematic_ppfix")] for kind in ("inputs", "results")],
    ],
}


def normalize_required(path: str) -> str:
    if "/inputs/" in path:
        return path + ".i"
    if "/results/" in path:
        return path + ".csv"
    return path


def last_time(path: Path) -> float | None:
    try:
        with path.open(newline="") as stream:
            rows = csv.DictReader(stream)
            last = None
            for row in rows:
                last = float(row["time"])
            return last
    except (OSError, KeyError, TypeError, ValueError):
        return None


def main() -> int:
    failures = 0
    for group, paths in REQUIRED.items():
        print(f"[{group}]")
        for raw in paths:
            rel = normalize_required(raw)
            path = CASES / rel
            state = "OK" if path.is_file() else "MISSING"
            failures += state == "MISSING"
            print(f"{state:7} {rel}")

    print("[extended depressurization]")
    expected = {"115_01": 4500.0, "115_02": 3852.5, "115_03": 5802.4, "115_04": 4500.0}
    incomplete = CASES / "03_Extended_Depressurization_115/incomplete_results_do_not_use"
    for case, end in expected.items():
        files = sorted(incomplete.glob(f"{case}*.csv"))
        observed = last_time(files[0]) if files else None
        state = "MISSING" if observed is None else ("COMPLETE" if observed >= end else "INCOMPLETE")
        print(f"{state:10} {case}: last_time={observed}, required_end={end}")

    print("[protocol consistency 116]")
    protocol = CASES / "04_Protocol_Consistency_116_Under_Review"
    for number in range(1, 12):
        tag = f"116_{number:02d}"
        inputs = list(protocol.rglob(f"{tag}*.i"))
        results = list(protocol.rglob(f"{tag}*.csv"))
        print(f"{tag}: inputs={len(inputs)}, results={len(results)}")

    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
