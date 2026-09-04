#!/usr/bin/env python3
"""Regenerate the tau--sigma_n' strength-path figure for the main paper.

The upstream plotter defaults to the corrected-protocol (116) case set and stamps
a red "LEGACY-PROTOCOL PROTOTYPE" banner on the other one. For THIS paper the
so-called legacy set is not a prototype: it is the primary calibrated
reconstruction reported in Table 1 (SW-T1 107_01, SW-T2 100_04, SW-S3 100_06,
SW-S4 93_07, with MC members pb04/pb04/pb06/center). Section 4.2 compares those
cases, so this wrapper selects them and suppresses the banner, which would be
inaccurate in the manuscript's framing. The 116 set belongs to Section 4.3 and
is plotted by running the upstream script with its own defaults.

    python3 scripts/make_strength_path_figure.py
"""
import importlib.util, os, sys
from pathlib import Path

UP = Path("/media/geomechanics/Data4TB/projects/orca_4.0/Paper_1_Validations/"
          "Ye_and_Ghassemi_2018/Docs/Table2_Strength_Path_Figure/"
          "plot_ye2018_table2_strength_paths.py")
OUT = Path(__file__).resolve().parent.parent / "Figures"


def load():
    spec = importlib.util.spec_from_file_location("_sp", UP)
    m = importlib.util.module_from_spec(spec)
    sys.modules["_sp"] = m
    spec.loader.exec_module(m)
    return m


def main():
    m = load()
    m.add_status = lambda figure, case_set: None      # suppress the banner
    m.set_style()
    frame = m.collect("legacy")
    OUT.mkdir(parents=True, exist_ok=True)
    fig = m.plot_main(frame, "legacy")
    for suf in ("pdf", "png"):
        p = OUT / f"Figure_Strength_Paths.{suf}"
        fig.savefig(p, dpi=600 if suf == "png" else None)
        print(p)
    # keep the exported stage table beside the figure for traceability
    frame.to_csv(OUT / "Figure_Strength_Paths_data.csv", index=False)
    print(OUT / "Figure_Strength_Paths_data.csv")


if __name__ == "__main__":
    main()
