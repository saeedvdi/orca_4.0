#!/usr/bin/env python3
"""Build the three preregistered Kalantar 2025 round-7 diagnostic decks.

The parents are completed, already-scored runs.  Each child changes one mechanism:

* 110_16: OG-T, physical 28-degree mesh, traction rather than uniform-displacement preload.
* 110_17: OG-SH, stress-dependent tangential stiffness, stopped after stage 5.
* 110_18: OG-SC, stress-dependent tangential stiffness, stopped after stage 7.

Run this script from any directory.  Existing parent decks are never modified.
"""

from __future__ import annotations

import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "Examples/Kalantar2025"


def write_deck(path: Path, text: str) -> None:
    """Write deterministic decks without inheriting trailing whitespace."""
    normalized = "\n".join(line.rstrip() for line in text.splitlines()) + "\n"
    path.write_text(normalized)


def replace_once(text: str, pattern: str, replacement: str, label: str,
                 flags: int = 0) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=flags)
    if count != 1:
        raise SystemExit(f"{label}: expected one match, found {count}")
    return updated


def prepend_header(text: str, header: str) -> str:
    return header.rstrip() + "\n\n" + text


def build_ogt_traction_probe() -> Path:
    parent = STUDY / "OGT/110_11_og_t_preload_probe.i"
    out = STUDY / "OGT/110_16_og_t_traction_probe_r7.i"
    old_stem = "110_11_og_t_preload_probe"
    stem = out.stem
    text = parent.read_text()
    text = text.replace(old_stem, stem)

    # The physical 28-degree mesh and all constitutive constants are inherited from
    # the completed round-5 probe.  Only the top-face loading representation changes.
    traction_vars = (
        "axial_traction_initial = -3.3e7   # ROUND 7: balance the -33 MPa initial stress\n"
        "axial_traction_final = -1.9343e8   # ROUND 7: Table-2 stage-1 sigma_1 target\n"
    )
    text = replace_once(
        text,
        r"^axial_pres_initial\s*=\s*[^\n]+\naxial_pres_final\s*=\s*[^\n]+$",
        traction_vars.rstrip(),
        "OG-T traction variables",
        flags=re.M,
    )

    traction_function = """  [axial_traction_ramp]
    type = ParsedFunction
    expression = 'if(t<2.0,${axial_traction_initial},if(t<55.0,${axial_traction_initial}+(${axial_traction_final}-${axial_traction_initial})*(t-2.0)/53.0,${axial_traction_final}))'
  []
"""
    text = replace_once(
        text,
        # This parent block closes with four spaces (an inherited formatting
        # oddity); matching the ordinary two-space function terminator would
        # consume the following injection-pressure block as well.
        r"  \[axial_disp_ramp\]\n.*?^    \[\]\n",
        traction_function,
        "OG-T axial function",
        flags=re.M | re.S,
    )

    traction_bc = """  [axial_load]
    # Diagnostic boundary arm: apply the measured axial stress as a distributed
    # traction instead of forcing every top-face node to one displacement.
    type = FunctionNeumannBC
    variable = disp_z
    boundary = top_nodeset
    function = axial_traction_ramp
  []
"""
    text = replace_once(
        text,
        r"  \[axial_load\]\n.*?^  \[\]\n",
        traction_bc,
        "OG-T axial boundary",
        flags=re.M | re.S,
    )

    # Under traction control there is no imposed axial-displacement command. Keep
    # this legacy CSV column dimensionally valid by reporting the realised mean top
    # displacement; machine-spring diagnostics then correctly collapse to zero.
    realised_displacement_pp = """  [axial_command_m_pp]
    type = SideAverageValue
    variable = disp_z
    boundary = top_nodeset
  []
"""
    text = replace_once(
        text,
        r"  \[axial_command_m_pp\]\n.*?^  \[\]\n",
        realised_displacement_pp,
        "OG-T axial command diagnostic",
        flags=re.M | re.S,
    )
    text = text.replace("LOCAL DIAGNOSTIC, NOT AN HPC JOB", "ROUND-7 HPC DIAGNOSTIC")
    text = text.replace("Run it on <= 24 ranks:", "Submit with the generated 32-rank HPC script:")

    header = """# =============================================================================
# 110_16_og_t_traction_probe_r7
#
# KALANTAR 2025 ROUND 7 -- OG-T BOUNDARY-CONDITION FALSIFIER.
# Parent: 110_11_og_t_preload_probe.i (physical 28-degree mesh, corrected frame).
#
# ONE CHANGE: the top face uses a distributed axial traction ramp instead of a
# FunctionPenaltyDirichletBC that forces every top node to the same displacement.
# The mesh, fracture angle, initial stress, pore pressure, joint law, and 60 s
# horizon are unchanged. Exodus remains every step for the required tip-field audit.
#
# PASS GATE BEFORE ANY FULL OG-T RUN:
#   1. cumulative plastic slip remains zero through 60 s;
#   2. d(bb_effective_normal_stress)/d(paper-frame sigma_n) becomes positive and
#      approximately one, rather than the round-5 value -0.379;
#   3. the two normal-stress channels agree within approximately 5 percent.
# A failure means the fracture-tip/platen representation still needs redesign.
# ============================================================================="""
    write_deck(out, prepend_header(text, header))
    return out


def build_stiffness_probe(*, parent_rel: str, out_rel: str, old_stem: str,
                          end_time: float, specimen: str, gate: str) -> Path:
    parent = STUDY / parent_rel
    out = STUDY / out_rel
    stem = out.stem
    text = parent.read_text().replace(old_stem, stem)

    stiffness = """    penalty_tangent = ${penalty_tangent}
    # ROUND 7: shape-only test. At stage-1 sigma'_n, k_t remains the legacy
    # 1e13 Pa/m; it then scales linearly with effective normal stress.
    use_stress_dependent_tangential_stiffness = true
    tangential_stiffness_reference_stress = ${reference_effective_normal_stress}
    tangential_stiffness_exponent = 1.0
    min_tangential_stiffness_fraction = 0.05"""
    text = replace_once(
        text,
        r"    penalty_tangent\s*=\s*\$\{penalty_tangent\}",
        stiffness,
        f"{specimen} tangential stiffness parameters",
    )

    text = replace_once(
        text,
        r"^(\s*end_time\s*=\s*)[0-9.]+([^\n]*)$",
        rf"\g<1>{end_time:g}   # ROUND 7 diagnostic horizon\2",
        f"{specimen} end time",
        flags=re.M,
    )

    stiffness_pp = """  [bb_tangential_stiffness_pp]
    type = SideAverageMaterialProperty
    property = bb_tangential_stiffness
    boundary = fracture_interface
  []

"""
    text = replace_once(
        text,
        r"(?=  \[bb_normal_stiffness_tangent_pp\])",
        stiffness_pp,
        f"{specimen} stiffness postprocessor",
    )

    header = f"""# =============================================================================
# {stem}
#
# KALANTAR 2025 ROUND 7 -- {specimen} STRESS-DEPENDENT SHEAR-STIFFNESS PROBE.
#
# ONE CHANGE: enable k_t = penalty_tangent * max(0.05, sigma'_n/sigma_ref),
# with sigma_ref equal to Table-2 stage-1 sigma'_n. The stiffness at stage 1
# therefore remains 1e13 Pa/m and only its stress dependence is tested.
# Material strength, frame, aperture, D_c, viscosity, mesh, and schedule are held.
# This diagnostic stops at t={end_time:g} s.
#
# PASS GATE: {gate}
# ============================================================================="""
    write_deck(out, prepend_header(text, header))
    return out


def main() -> int:
    outputs = [
        build_ogt_traction_probe(),
        build_stiffness_probe(
            parent_rel="OGSH/110_13_og_sh_bbfast_r6.i",
            out_rel="OGSH/110_17_og_sh_ktshape_r7.i",
            old_stem="110_13_og_sh_bbfast_r6",
            end_time=2000,
            specimen="OG-SH",
            gate="stage-5 slip 30-60 um, tau error below +8%, and no burst.",
        ),
        build_stiffness_probe(
            # Use round 5 so the ineffective round-6 5x viscosity arm is not retained.
            parent_rel="OGSC/110_12_og_sc_bbfast_r5.i",
            out_rel="OGSC/110_18_og_sc_ktshape_r7.i",
            old_stem="110_12_og_sc_bbfast_r5",
            end_time=4900,
            specimen="OG-SC",
            gate="stage-5 plastic slip <=2 um, no stage-6 burst, burst at stage 7.",
        ),
    ]
    for path in outputs:
        print(path.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
