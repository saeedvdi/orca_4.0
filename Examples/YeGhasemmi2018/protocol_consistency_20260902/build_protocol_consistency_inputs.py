#!/usr/bin/env python3
"""Build the Ye-Ghassemi protocol-consistency BB/MC input package.

The source decks remain untouched.  The default common machine stiffness is the
796 kN/mm MTS-815 value reported by Kalantar et al. (2025).  It is deliberately
labelled a provisional sensitivity, not a measurement of Ye and Ghassemi's
MTS-816.  Regenerate with --ksys-kn-per-mm when a better common value is chosen.
"""

from __future__ import annotations

import argparse
import math
import re
from dataclasses import dataclass
from pathlib import Path


PROJECT = Path("/media/geomechanics/Data4TB/projects/orca_4.0")
YE = PROJECT / "Examples/YeGhasemmi2018"
HERE = Path(__file__).resolve().parent


@dataclass(frozen=True)
class Specimen:
    directory: str
    area: float
    # The two values below are read from the adopted BB result immediately
    # after t=55 s.  They preserve the existing near-critical preload when the
    # spring stiffness is changed; every new case still requires the short gate.
    top_displacement_at_gate: float
    spring_stress_at_gate_mpa: float


SPECIMENS = {
    "SWT1": Specimen("SWT1", 0.00200454848465, -0.00029077433401189, 181.59322839662),
    "SWT2": Specimen("SWT2", 0.00200454848465, -0.00033973882463990, 202.28994133740),
    "SWS3": Specimen("SWS3", 0.00200534212950, -0.000057849060164724, 62.867836288757),
    "SWS4": Specimen("SWS4", 0.00200375499689, -0.000048991888305809, 59.287892763188),
}


SOURCE_NAMES = {
    ("SWT1", "bb"): "SWT1_OrcaBartonBandisContactTractionFastADHardening.i",
    ("SWT1", "mc"): "SWT1_OrcaMohrCoulombContactTraction.i",
    ("SWT2", "bb"): "SWT2_OrcaBartonBandisContactTractionFastADHardening.i",
    ("SWT2", "mc"): "SWT2_OrcaMohrCoulombContactTraction.i",
    ("SWS3", "bb"): "SWS3_OrcaBartonBandisContactTractionFastADHardening.i",
    ("SWS3", "mc"): "SWS3_OrcaMohrCoulombContactTraction.i",
    ("SWS4", "bb"): "SWS4_OrcaBartonBandisContactTractionFastADHardening.i",
    ("SWS4", "mc"): "SWS4_OrcaMohrCoulombContactTraction.i",
}


CASES = [
    ("SWT1", "bb", "116_01_swt1_bb_commonK796_protocol_ppfix", "main"),
    ("SWT1", "mc", "116_02_swt1_mc_commonK796_protocol_ppfix", "main"),
    ("SWT2", "bb", "116_03_swt2_bb_theta31_commonK796_protocol_ppfix", "main"),
    ("SWT2", "mc", "116_04_swt2_mc_theta31_commonK796_protocol_ppfix", "main"),
    ("SWS3", "bb", "116_05_sws3_bb_fixedpiston_commonK796_protocol_ppfix", "main"),
    ("SWS3", "mc", "116_06_sws3_mc_fixedpiston_commonK796_protocol_ppfix", "main"),
    ("SWS4", "bb", "116_07_sws4_bb_jrc1p19_fixedpiston_commonK796_ppfix", "jrc1p19"),
    ("SWS4", "mc", "116_08_sws4_mc_fixedpiston_commonK796_protocol_ppfix", "main"),
    ("SWS4", "bb", "116_09_sws4_bb_jrc5_fixedpiston_commonK796_control", "jrc5"),
    ("SWT2", "bb", "116_10_swt2_bb_theta31_commonK796_eqhold_ppfix", "eqhold"),
    ("SWT2", "mc", "116_11_swt2_mc_theta31_commonK796_eqhold_ppfix", "eqhold"),
]


MC_SELECTED = {
    # Selected equal-budget cases used in the paper comparison: pb04, pb04,
    # pb06, and center, respectively.
    "SWT1": (0.509312, 0.640304, 4.07374e7, 7.8115e6, 1.125e-4),
    "SWT2": (0.508576, 0.640304, 4.72549e7, 8.2535e6, 1.125e-4),
    "SWS3": (0.952344, 0.166432, 2.3805e6, 1.19e6, 5.0e-5),
    "SWS4": (0.9804, 0.1139, 3.225e6, 0.0, 8.0e-5),
}


# Coordinates are the continuous 6.0 mm sidewall-offset targets on the reported
# mean fracture plane.  ExtraNodesetGenerator uses the closest existing node;
# therefore a coarse size-5 mesh may retain a small realized offset error.
PORT_TARGETS = {
    "SWT1": (
        ("-0.018370909 0.0 0.035000400", "-0.019260000 0.0 0.033577557"),
        ("0.018370909 0.0 0.093799600", "0.019260000 0.0 0.095222443"),
    ),
    "SWT2": (
        ("-0.018370909 0.0 0.034530652", "-0.019260000 0.0 0.034295977"),
        ("0.018370909 0.0 0.098169348", "0.019260000 0.0 0.098404023"),
    ),
    "SWS3": (
        ("-0.023159583 0.0 0.019919005", "-0.019265000 0.0 0.026945020"),
        ("0.023159583 0.0 0.103480995", "0.019265000 0.0 0.096454980"),
    ),
    "SWS4": (
        ("-0.018367273 0.0 0.027536950", "-0.019255000 0.0 0.025999536"),
        ("0.018367273 0.0 0.091163050", "0.019255000 0.0 0.092700464"),
    ),
}


T2_BASE_X = (
    "0.0 60.0 130.0 480.0 565.0 995.0 1070.0 1360.0 1460.0 "
    "1755.0 1850.0 2145.0 2280.0 2500.0 2510.0 2560.0 2570.0 "
    "2605.0 2615.0 2650.0 2660.0 2705.0 2725.0 2830.0 2852.5"
)
T2_BASE_Y = (
    "5e+06 5e+06 8e+06 8e+06 1.2e+07 1.2e+07 1.6e+07 1.6e+07 "
    "2e+07 2e+07 2.4e+07 2.4e+07 2.8e+07 2.8e+07 2.4e+07 "
    "2.4e+07 2e+07 2e+07 1.6e+07 1.6e+07 1.2e+07 1.2e+07 "
    "8e+06 8e+06 8e+06"
)
T2_EQ_X = (
    "0.0 60.0 130.0 480.0 565.0 995.0 1070.0 1360.0 1460.0 "
    "1755.0 1850.0 2145.0 2280.0 2500.0 2510.0 2910.0 2920.0 "
    "3320.0 3330.0 3730.0 3740.0 4140.0 4160.0 4560.0"
)
T2_EQ_Y = (
    "5e+06 5e+06 8e+06 8e+06 1.2e+07 1.2e+07 1.6e+07 1.6e+07 "
    "2e+07 2e+07 2.4e+07 2.4e+07 2.8e+07 2.8e+07 2.4e+07 "
    "2.4e+07 2e+07 2e+07 1.6e+07 1.6e+07 1.2e+07 1.2e+07 "
    "8e+06 8e+06"
)


def replace_once(text: str, pattern: str, replacement: str, label: str) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1, flags=re.MULTILINE)
    if count != 1:
        raise RuntimeError(f"{label}: expected one replacement, found {count}: {pattern}")
    return updated


def set_scalar(text: str, name: str, value: str, label: str) -> str:
    return replace_once(text, rf"^{re.escape(name)}\s*=.*$", f"{name} = {value}", label)


def set_active_material_value(text: str, name: str, value: str, label: str) -> str:
    pattern = rf"^(\s+){re.escape(name)}\s*=\s*[^#\n]+(?:\s*#.*)?$"
    return replace_once(text, pattern, rf"\g<1>{name} = {value}", label)


def common_header(specimen: str, model: str, stem: str, ksys: float, kp: float) -> str:
    return f"""################################################################################
# ACTIVE PROTOCOL-CONSISTENCY CASE: {stem}
# Generated by build_protocol_consistency_inputs.py; parent deck is unchanged.
# Model/specimen: {model.upper()} / {specimen}
# COMMON MACHINE SPRING: K_sys = {ksys / 1e6:.6g} kN/mm and
# k_p = K_sys/A = {kp:.12g} Pa/m.
# IMPORTANT: K_sys is a provisional common sensitivity.  The default 796 kN/mm
# is reported by Kalantar et al. (2025) for an MTS 815, not measured for the
# Ye-Ghassemi MTS 816.  Regenerate the package when an MTS 816 value is chosen.
# The near-critical command was transformed to preserve the adopted parent's
# t=55 s specimen displacement and spring stress.  Run the supplied preload gate
# before the full HPC job, particularly for SW-T2 after its 31-degree mesh swap.
# No constitutive refit was performed.
################################################################################

"""


def transform(
    specimen: str,
    model: str,
    stem: str,
    variant: str,
    ksys: float,
    ye_root: Path,
) -> str:
    spec = SPECIMENS[specimen]
    source = ye_root / spec.directory / SOURCE_NAMES[(specimen, model)]
    text = source.read_text()

    kp = ksys / spec.area
    u_initial = -31.0e6 / kp
    u_final = spec.top_displacement_at_gate - spec.spring_stress_at_gate_mpa * 1e6 / kp

    text = set_scalar(text, "axial_bc_penalty", f"{kp:.12g}", stem)
    text = set_scalar(text, "axial_pres_initial", f"{u_initial:.15g}", stem)
    text = set_scalar(text, "axial_pres_final", f"{u_final:.15g}", stem)

    # One output tree shared by the portable package, separated by case stem.
    text = set_scalar(
        text,
        "exodus_file_base",
        f"proposed_inputs/protocol_consistency_20260902/exodus/{stem}",
        stem,
    )

    for old_coord, new_coord in PORT_TARGETS[specimen]:
        if old_coord not in text:
            raise RuntimeError(f"{stem}: source port coordinate not found: {old_coord}")
        text = text.replace(old_coord, new_coord)
        text = re.sub(
            rf"^(\s*coord\s*=\s*'{re.escape(new_coord)}').*$",
            rf"\1   # requested 6.0 mm sidewall target; closest mesh node is selected",
            text,
            flags=re.MULTILINE,
        )
    text = set_scalar(
        text,
        "csv_file_base",
        f"proposed_inputs/protocol_consistency_20260902/csv/{stem}",
        stem,
    )
    text = set_scalar(
        text,
        "checkpoint_file_base",
        f"proposed_inputs/protocol_consistency_20260902/checkpoint/{stem}",
        stem,
    )

    # Use the physical Table-1 angle for SW-T2.  The parent 30-degree case is
    # retained separately because the published Table-2 stresses imply 30 deg.
    if specimen == "SWT2":
        text = set_scalar(text, "mesh_file", "../mesh/ye2018_sw_T2_mesh_size_5.e", stem)
        text = set_scalar(text, "bulk_sin_theta", f"{math.sin(math.radians(31.0)):.16g}", stem)
        text = set_scalar(text, "bulk_cos_theta", f"{math.cos(math.radians(31.0)):.16g}", stem)
        text = text.replace(
            "0.25*differential_stress_reaction_mpa_pp",
            "0.265264218607055*differential_stress_reaction_mpa_pp",
        )
        text = text.replace(
            "0.433012701892219*differential_stress_reaction_mpa_pp",
            "0.441473796429463*differential_stress_reaction_mpa_pp",
        )

    # SW-S3: remove the live 4.5 um retreat.  Move the requested port targets to
    # the paper's 6 mm offset.  ExtraNodesetGenerator selects the closest mesh
    # node, so the realized offset must be checked in the generated-mesh audit.
    if specimen == "SWS3":
        text = replace_once(
            text,
            r"^(\s+)expression = 'if\(t<2\.0,\$\{axial_pres_initial\}.*4\.5e-06.*$",
            r"\g<1>expression = 'if(t<2.0,${axial_pres_initial},if(t<55.0,${axial_pres_initial}+(${axial_pres_final}-${axial_pres_initial})*(t-2.0)/53.0,${axial_pres_final}))'",
            stem,
        )
    # SW-S4: eliminate all fitted load-side histories.  Keeping the unused
    # variables at zero is deliberate and makes command-line auditing simple.
    if specimen == "SWS4":
        text = set_scalar(text, "poro_du", "0.0", stem)
        text = set_scalar(text, "axial_relax_du", "0.0", stem)
        text = set_scalar(text, "side_unload_relax_pressure", "0.0", stem)

    if model == "mc":
        mu_r, mu_s, c_r, c_s, decay = MC_SELECTED[specimen]
        text = set_active_material_value(text, "friction_coefficient_rough", f"{mu_r:.9g}", stem)
        text = set_active_material_value(text, "friction_coefficient_smooth", f"{mu_s:.9g}", stem)
        text = set_active_material_value(text, "cohesion_rough", f"{c_r:.9g}", stem)
        text = set_active_material_value(text, "cohesion_smooth", f"{c_s:.9g}", stem)
        if specimen == "SWS4":
            # The SWS4 deck exposes the decay distance through this top-level
            # alias.  Retain the material reference so HIT does not reject an
            # otherwise orphaned command-line parameter.
            text = set_scalar(text, "bb_roughness_characteristic_slip", f"{decay:.9g}", stem)
        else:
            text = set_active_material_value(text, "roughness_decay_distance", f"{decay:.9g}", stem)

    if specimen == "SWS4" and model == "bb":
        text = set_scalar(text, "bb_jrc", "1.19" if variant == "jrc1p19" else "5.0", stem)

    if variant == "eqhold":
        if T2_BASE_X not in text or T2_BASE_Y not in text:
            raise RuntimeError(f"{stem}: base SW-T2 schedule not found")
        text = text.replace(T2_BASE_X, T2_EQ_X, 1).replace(T2_BASE_Y, T2_EQ_Y, 1)
        text = replace_once(text, r"^(\s*)end_time\s*=.*$", r"\g<1>end_time = 4560.0", stem)

    # The submit scripts install each generated deck in the live specimen's
    # proposed_inputs directory.  Resolve all parent mesh paths from there.
    text = re.sub(r"^mesh_file\s*=\s*mesh/", "mesh_file = ../mesh/", text, flags=re.MULTILINE)

    return common_header(specimen, model, stem, ksys, kp) + text


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--ksys-kn-per-mm",
        type=float,
        default=796.0,
        help="one common physical machine stiffness in kN/mm (default: 796)",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        default=PROJECT,
        help="Orca project root containing Examples/YeGhasemmi2018",
    )
    args = parser.parse_args()
    if args.ksys_kn_per_mm <= 0:
        raise SystemExit("--ksys-kn-per-mm must be positive")
    ksys = args.ksys_kn_per_mm * 1.0e6  # kN/mm == MN/m == 1e6 N/m
    ye_root = args.project_root / "Examples/YeGhasemmi2018"

    for specimen, model, stem, variant in CASES:
        out_dir = HERE / specimen
        out_dir.mkdir(parents=True, exist_ok=True)
        (out_dir / f"{stem}.i").write_text(
            transform(specimen, model, stem, variant, ksys, ye_root)
        )

    print(f"Generated {len(CASES)} inputs with common K_sys={args.ksys_kn_per_mm:g} kN/mm")


if __name__ == "__main__":
    main()
