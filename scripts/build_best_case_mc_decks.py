#!/usr/bin/env python3
"""Build matched Mohr-Coulomb decks for the best physical BBFast cases.

The validated 94-series decks already contain the audited Barton-Bandis to
Mohr-Coulomb envelope transfer and all required AD-property/postprocessor
changes.  This script carries the later, specimen-specific 100-series
refinements onto those MC baselines without reopening the transfer itself.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "Examples" / "YeGhasemmi2018"


@dataclass(frozen=True)
class DeckSpec:
    sample: str
    mc_parent: str
    bb_sibling: str
    output: str
    selection_note: str
    changes: tuple[tuple[str, str], ...] = ()


SPECS = (
    DeckSpec(
        sample="SWT1",
        mc_parent="94_01_swt1_mc_final.i",
        bb_sibling="100_01_swt1_vm55um_ppfix.i",
        output="102_01_swt1_mc_vm55um_ppfix.i",
        selection_note=(
            "Updated-ranking best physical case: maximum closure 55.00 um; "
            "mean BBFast nRMSE 2.688632%."
        ),
        changes=(
            (
                "    maximum_closure = 4.591e-5",
                "    maximum_closure = 5.500e-5       # 102_01: copied from BBFast 100_01",
            ),
            (
                "    normal_closure_offset = 4.433e-5",
                "    normal_closure_offset = 5.167067369997e-5 # 102_01: preserves initial seating",
            ),
        ),
    ),
    DeckSpec(
        sample="SWT2",
        mc_parent="94_03_swt2_mc_final.i",
        bb_sibling="100_04_swt2_apscale0p0177_ppfix.i",
        output="102_02_swt2_mc_apscale0p0177_ppfix.i",
        selection_note=(
            "Updated-ranking nominal best physical case: aperture scale 0.0177; "
            "mean BBFast nRMSE 2.131869% (0.0175-0.0177 unresolved)."
        ),
        changes=(
            (
                "aperture_scale = 0.0165",
                "aperture_scale = 0.0177 # 102_02: copied from BBFast 100_04",
            ),
        ),
    ),
    DeckSpec(
        sample="SWS3",
        mc_parent="94_05_sw3_mc_final.i",
        bb_sibling="100_06_sw3_resc1p30_unld0p00_ppfix.i",
        output="102_03_sw3_mc_resc1p30_ppfix.i",
        selection_note=(
            "Updated-ranking nominal best physical case: residual cohesion 1.30 MPa; "
            "mean BBFast nRMSE 4.353781% (gain below the reproducibility floor)."
        ),
        changes=(
            (
                "    cohesion_smooth = 1.400e6",
                "    cohesion_smooth = 1.300e6 # 102_03: copied from BBFast 100_06 residual",
            ),
        ),
    ),
    DeckSpec(
        sample="SWS4",
        mc_parent="94_07_sw4_mc_final.i",
        bb_sibling="93_07_sw4_final_theta30_jrc5_ppfix.i",
        output="102_04_sw4_mc_theta30_jrc5_ppfix.i",
        selection_note=(
            "Updated-ranking tied best and authoritative physical case: no 99-series "
            "scalar refinement was accepted; mean BBFast nRMSE 6.139187%."
        ),
    ),
)


def replace_once(text: str, old: str, new: str, deck: Path) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{deck}: expected one occurrence of {old!r}, found {count}")
    return text.replace(old, new, 1)


def build(spec: DeckSpec) -> Path:
    sample_dir = EXAMPLES / spec.sample
    source = sample_dir / spec.mc_parent
    target = sample_dir / spec.output
    old_case = source.stem
    new_case = target.stem
    text = source.read_text()

    if old_case not in text:
        raise RuntimeError(f"{source}: case name {old_case!r} is absent")
    text = text.replace(old_case, new_case)

    for old, new in spec.changes:
        text = replace_once(text, old, new, source)

    extra = ""
    if spec.sample == "SWS3":
        extra = (
            "# NOTE: BBFast 100_06 also sets normal_unload_retention_fraction=0.00.\n"
            "# The MC material has no corresponding unload-retention parameter, so that\n"
            "# BBFast-only mechanism is intentionally not invented for this baseline.\n"
        )

    banner = (
        "# ============================================================================\n"
        f"# {new_case} -- BEST-PHYSICAL-CASE MOHR-COULOMB VALIDATION\n"
        f"# BBFast sibling: {spec.bb_sibling}\n"
        f"# Audited MC parent: {spec.mc_parent}\n"
        f"# {spec.selection_note}\n"
        "#\n"
        "# Construction rule: retain the validated 94-series MC transfer and copy\n"
        "# only the later best-case refinement(s) named above. Mesh, loading history,\n"
        "# hydraulics, boundary conditions, solver, and reporting remain paired.\n"
        f"{extra}"
        "# Validate with a two-step execution; --check-input alone does not resolve\n"
        "# every material property consumed during initialSetup.\n"
        "# ============================================================================\n"
    )

    target.write_text(banner + text)
    return target


def main() -> None:
    for spec in SPECS:
        path = build(spec)
        print(path.relative_to(ROOT))


if __name__ == "__main__":
    main()
