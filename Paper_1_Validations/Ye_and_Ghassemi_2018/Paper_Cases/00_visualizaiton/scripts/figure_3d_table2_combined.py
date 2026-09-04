#!/usr/bin/env python3
"""Combined Table 2 comparison: all seven scored/derived channels, all four specimens.

Merges what were separate mechanical (4 rows) and hydraulic (3 rows) figures into
one 7 x 4 page figure, saving one AGU publication unit. Both parent scripts already
build rows=quantity, columns=specimen through the same helper, so this only has to
concatenate their spec tuples and give the result a taller canvas.

Rows: effective normal stress, shear stress, normal dilation, shear displacement,
flow rate, hydraulic aperture, fracture permeability.
"""
import importlib.util, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent

def _load(name, filename):
    spec = importlib.util.spec_from_file_location(name, HERE / filename)
    mod = importlib.util.module_from_spec(spec); sys.modules[name] = mod
    spec.loader.exec_module(mod); return mod

mech = _load("_m3b", "figure_3b_table2_mechanical.py")
hyd  = _load("_m3c", "figure_3c_table2_hydraulic.py")

# --- path shim -------------------------------------------------------------
# The parent scripts resolve results under Examples/YeGhasemmi2018/<sample>,
# but the campaign folders were reorganised to
# Paper_1_Validations/Ye_and_Ghassemi_2018/<sample>. Rather than edit the
# tracked parents, redirect the lookup here. The "Sweeps" preference in the
# original sort is preserved: only that copy is scoreable.
from pathlib import Path as _P

_ALT_ROOTS = ("Examples/YeGhasemmi2018", "Paper_1_Validations/Ye_and_Ghassemi_2018")


def _result_path(sample, row, _root=mech.PROJECT_ROOT):
    recorded = _root / str(row["source_csv"])
    if recorded.is_file():
        return recorded
    cands = []
    for rel in _ALT_ROOTS:
        base = _root / rel / sample
        if base.is_dir():
            cands += [q for q in base.rglob(recorded.name)
                      if "partial_every_step" not in q.parts]
    if not cands:
        raise FileNotFoundError(f"{recorded.name} not found under {_ALT_ROOTS}")
    cands.sort(key=lambda q: (0 if "Sweeps" in q.parts else 1, len(q.parts), str(q)))
    return cands[0]


def _mc_paths(_root=mech.PROJECT_ROOT):
    out = {}
    for sample, case in mech.FINAL_MC_CASES.items():
        for rel in _ALT_ROOTS:
            q = _root / rel / sample / "results_csv_mc_sweep_hpc" / f"{case}.csv"
            if q.is_file():
                out[sample] = q
                break
        else:
            hits = []
            for rel in _ALT_ROOTS:
                base = _root / rel / sample
                if base.is_dir():
                    hits += list(base.rglob(f"{case}.csv"))
            if not hits:
                raise FileNotFoundError(f"{case}.csv not found for {sample}")
            out[sample] = sorted(hits, key=lambda q: len(q.parts))[0]
    return out


for _m in (mech, hyd):
    _m.result_path = _result_path
    _m.FINAL_MC_RESULT_PATHS = _mc_paths()
# ---------------------------------------------------------------------------

# --- one y scale per panel ------------------------------------------------
# The parent pairs SW-T1 with SW-T2 and SW-S3 with SW-S4 so that comparisons
# within a family are direct. Across seven rows that flattens the smaller member
# of each pair, because the specimens differ in range within a family as much as
# the families differ from each other. Each panel therefore gets its own y scale.
# The x axis stays common, since every column is the same ordered injection
# pressure loading and unloading sequence.
mech.TABLE2_SCALE_GROUPS = (("SWT1",), ("SWT2",), ("SWS3",), ("SWS4",))

COMBINED_SPECS = mech.TABLE2_MECHANICAL_SPECS + hyd.TABLE2_HYDRAULIC_SPECS
FIGURE_KEY = "table2_combined"
# 7 rows on one page: AGU text height leaves ~8.8 in once the caption is set.
mech.FIGURE_SIZES_IN[FIGURE_KEY] = (7.2, 8.8)

OUTPUT_FILENAME = "Figure_Table2_Combined_All_Specimens.pdf"


def figure_table2_combined():
    fig = mech._figure_table2_specimens(
        COMBINED_SPECS, FIGURE_KEY, mech.FINAL_BB_CASES, mech.FINAL_MC_CASES)
    # the parent tunes margins for 3-4 rows; 7 rows need tighter vertical packing
    fig.subplots_adjust(left=0.135, right=0.995, bottom=0.050, top=0.930,
                        wspace=0.28, hspace=0.32)
    return fig


def main():
    fig = figure_table2_combined()
    out = mech.OUTPUT_DIR / OUTPUT_FILENAME
    fig.savefig(out, format="pdf", dpi=mech.AGU_SAVE_DPI, bbox_inches="tight",
                facecolor="white",
                metadata={"Title": OUTPUT_FILENAME.removesuffix(".pdf").replace("_", " "),
                          "Author": "ORCA Ye--Ghassemi validation workflow",
                          "Subject": "AGU manuscript result figure"})
    fig.savefig(str(out).replace(".pdf", ".png"), dpi=200, bbox_inches="tight",
                facecolor="white")
    print(out)
    return out


if __name__ == "__main__":
    main()
