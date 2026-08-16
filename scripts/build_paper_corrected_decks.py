#!/usr/bin/env python3
"""
build_paper_corrected_decks.py -- generate the 89-series decks that apply the
2026-08-16 paper audit to the four Ye & Ghassemi (2018) specimens.

Every constant written here is derived in scripts/refit_joint_constants_from_paper.py
from the paper's own Table 1 / Table 2 / Sec. 2.1, and every parent deck is left
untouched so the pre-audit configuration stays reproducible.

Controlled axes (one row = one deck):

  89_01  SW-S4  30 deg mesh  AND  paper JRC/JCS/phi_r      correction, both fixes
  89_06  SW-S4  30 deg mesh only                           attribution control for 89_01
  89_02  SW-S3  paper JRC/JCS/phi_r                        correction
  89_03  SW-T2  30 deg mesh only                           correction
  89_04  SW-T1  cohesion refit                             CANDIDATE, must be scored
  89_05  SW-T2  30 deg mesh AND cohesion refit             CANDIDATE, must be scored

Run:  python3 scripts/build_paper_corrected_decks.py
      python3 scripts/build_paper_corrected_decks.py --check     # dry run, report only
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EX = os.path.join(ROOT, "Examples", "YeGhasemmi2018")

# HPC output convention introduced by commit 9a5f081 ("updates the input file to run
# on hpc"): every base moves to results_*_hpc_rorqual/ and the stem gains _hpc.
HPC_DIRS = {"exodus": "results_exodus_hpc_rorqual",
            "csv": "results_csv_hpc_rorqual",
            "checkpoint": "results_checkpoint_hpc_rorqual"}

# Water at 20 C (the paper's stated test temperature, Sec. 2.5). The decks carried
# 4.7836e9, 2.17x too stiff. It enters only OrcaTHMaterial's 1/M for the matrix
# blocks -- the fracture flow does not read it -- so at porosity 1e-3 this moves
# matrix storage by ~6 % and nothing else.
K_WATER = "2.2e9"

# --- SW-S4 paper-frame reporting, eq (3)-(4) at theta = 30 deg -----------------
SW_S4_PAPER_FRAME = """
  # ---------------------------------------------------------------------------
  # Paper-frame reduction, Ye & Ghassemi (2018) eq (3)-(4), theta = 30 deg:
  #   sigma'_n = (sigma_3 - P_p) + sigma_d sin^2(theta),  P_p = (P_i + P_o)/2
  #   tau      = sigma_d sin(theta) cos(theta)
  # SW-S4 was the only specimen without these, so its scorecard compared a fault-
  # averaged czm_sigma_n against Table 2's frame-reduced value while its three
  # siblings compared like with like (audit finding, 2026-08-16).
  # sin^2(30) = 0.25 exactly; sin(30)cos(30) = 0.433012701892219.
  # ---------------------------------------------------------------------------
  [effective_normal_paper_frame_mpa_pp]
    type = ParsedPostprocessor
    pp_names = 'differential_stress_reaction_mpa_pp injection_pressure_pp pp_outlet_pp'
    expression = '30.0 - 0.5*(injection_pressure_pp + pp_outlet_pp)*1e-6 + 0.25*differential_stress_reaction_mpa_pp'
  []
  [shear_stress_paper_frame_mpa_pp]
    type = ParsedPostprocessor
    pp_names = differential_stress_reaction_mpa_pp
    expression = '0.433012701892219*differential_stress_reaction_mpa_pp'
  []
"""

ANCHOR_S4_PP = """  [differential_stress_reaction_mpa_pp]
    type = ParsedPostprocessor
    pp_names = sigma1_reaction_mpa_pp
    expression = 'sigma1_reaction_mpa_pp - ${confining_pressure} * 1e-6'
  []
"""

# --- edit primitives ----------------------------------------------------------


def sub(pattern, repl, count=0, flags=re.M):
    return ("re", pattern, repl, count, flags)


def literal(old, new, count=0):
    return ("lit", old, new, count, 0)


def insert_after(anchor, text):
    return ("ins", anchor, text, 1, 0)


def apply_edits(text, edits, label):
    for kind, a, b, count, flags in edits:
        if kind == "re":
            text, n = re.subn(a, b, text, count=count, flags=flags)
        elif kind == "lit":
            n = text.count(a) if count == 0 else min(count, text.count(a))
            text = text.replace(a, b, -1 if count == 0 else count)
        else:
            if anchor_missing := (a not in text):
                n = 0
            else:
                text = text.replace(a, a + b, 1)
                n = 1
            del anchor_missing
        if n == 0:
            raise SystemExit(f"{label}: edit matched nothing: {a[:90]!r}")
    return text


def hpc_outputs(stem):
    """Repoint the three output bases at the HPC directories, with the _hpc suffix."""
    return [
        sub(r"^exodus_file_base\s*=\s*\S+.*$",
            f"exodus_file_base = {HPC_DIRS['exodus']}/{stem}_hpc"),
        sub(r"^csv_file_base\s*=\s*\S+.*$",
            f"csv_file_base    = {HPC_DIRS['csv']}/{stem}_hpc"),
        sub(r"^checkpoint_file_base\s*=\s*\S+.*$",
            f"checkpoint_file_base = {HPC_DIRS['checkpoint']}/{stem}_hpc"),
    ]


def water():
    return [sub(r"^fluid_bulk_modulus\s*=\s*\S+.*$",
                f"fluid_bulk_modulus = {K_WATER}  # water at 20 C (Sec. 2.5); was "
                f"4.7835616438e9, 2.17x too stiff")]


# --- the fracture-angle and joint-constant edits ------------------------------

SW_S4_MESH30 = [
    literal("mesh_file = mesh/ye2018_sw_s4_size5_mesh.e",
            "mesh_file = mesh/ye2018_sw_s4_theta30_size5_mesh.e"),
    # The corrected mesh names its boundaries like SW-S3/T1/T2 do.
    literal("nodesets_to_convert = 'top bottom sides'",
            "nodesets_to_convert = 'top_nodeset bottom_nodeset sides_nodeset'"),
    sub(r"^(\s*)boundary = top$", r"\1boundary = top_nodeset"),
    sub(r"^(\s*)boundary = bottom$", r"\1boundary = bottom_nodeset"),
    sub(r"^(\s*)boundary = sides$", r"\1boundary = sides_nodeset"),
    # Source nodes: EXACT interface-node coordinates on the new plane, not the ideal
    # borehole position. On the size-5 mesh the ideal position has a BULK node 1.73 mm
    # away and the nearest interface node 1.78 mm away, so use_closest_node would have
    # pinned injection into the matrix. Verified with scripts/check_source_nodes.py.
    literal("coord = '-0.019255 0 0.021745'",
            "coord = '-0.018367273 0.0 0.027536950'   # exact interface node, 6.89 mm "
            "in from the sidewall"),
    literal("coord = '0.019255 0 0.091255'",
            "coord = '0.018367273 0.0 0.091163050'   # exact interface node, 6.89 mm "
            "in from the sidewall"),
]

SW_S4_PAPER_JOINT = [
    sub(r"^bb_jrc = 17\.5\b.*$",
        "bb_jrc = 1.19                        # PAPER Table 1 (measured). Was 17.5, "
        "14.7x the measured value."),
    sub(r"^bb_jcs = 3\.0e8\b.*$",
        "bb_jcs = 1.5e8                       # PAPER Sec. 2.1 UCS. Was 3.0e8, 2x the "
        "measured value."),
    sub(r"^bb_residual_friction_angle = 7\.5\b.*$",
        "bb_residual_friction_angle = 23.709  # pins the envelope through Table 2's last "
        "stick stage (26.51 MPa, 12.14 MPa) at the measured JRC/JCS. Was 7.5, which no "
        "granite joint has."),
]

SW_S3_PAPER_JOINT = [
    sub(r"^(\s*)jrc = 23\.35\s*$",
        r"\1jrc = 1.96                        # PAPER Table 1 (measured). Was 23.35 -- "
        "11.9x measured AND outside Barton's 0-20 scale."),
    sub(r"^(\s*)jcs = 3\.0e8\s*$",
        r"\1jcs = 1.5e8                       # PAPER Sec. 2.1 UCS. Was 3.0e8."),
    # Anchored on the exact line so slip_weakening_residual_friction_angle_degrees,
    # which is also 8.45 and is DELIBERATELY unchanged, cannot be caught.
    sub(r"^(\s*)residual_friction_angle_degrees = 8\.45\s*$",
        r"\1residual_friction_angle_degrees = 29.756  # pins the envelope through Table "
        "2's last stick stage (23.42 MPa, 14.26 MPa) at the measured JRC/JCS. Was 8.45."),
]

SW_T2_MESH30 = [
    literal("mesh_file = mesh/ye2018_sw_T2_mesh_size_5.e",
            "mesh_file = mesh/ye2018_sw_T2_theta30_mesh_size_5.e"),
    literal("coord = '-0.019260000 0.0 0.034295977'",
            "coord = '-0.018370909 0.0 0.034530652'   # exact interface node on the "
            "30 deg plane"),
    literal("coord = '0.019260000 0.0 0.098404023'",
            "coord = '0.018370909 0.0 0.098169348'   # exact interface node on the "
            "30 deg plane"),
    # Paper-frame reduction must follow the mesh: sin^2 and sin*cos at 30, not 31.
    literal("0.265264218607055*differential_stress_reaction_mpa_pp",
            "0.25*differential_stress_reaction_mpa_pp"),
    literal("0.441473796429463*differential_stress_reaction_mpa_pp",
            "0.433012701892219*differential_stress_reaction_mpa_pp"),
]


def cohesion_refit(sample, phi_r, c_peak, c_res, old_phi_r, old_tail):
    """Replace an impossible phi_r with the granite basic angle plus asperity cohesion."""
    return [
        sub(rf"^(\s*)residual_friction_angle_degrees = {re.escape(old_phi_r)}\s*$",
            rf"\1residual_friction_angle_degrees = {phi_r}   # granite basic friction, "
            f"measured on this campaign's own saw cut (SW-S3). Was {old_phi_r}, above "
            "every measured granite value."),
        sub(rf"^(\s*)slip_weakening_residual_friction_angle_degrees = {re.escape(old_tail)}\s*$",
            rf"\1slip_weakening_residual_friction_angle_degrees = {phi_r}   # slip "
            "destroys ROUGHNESS, not the rock's basic friction angle -- Barton's own "
            f"picture. Was {old_tail}.\n"
            rf"\1cohesion = {c_peak}          # asperity interlock of a MATED Mode-I "
            "fracture; pins the peak envelope through Table 2's last stick stage.\n"
            rf"\1residual_cohesion = {c_res}   # interlock surviving the burst; pins the "
            "post-burst stage. Table 2 shows this joint retaining most of its dilation, "
            "so it does not lose all interlock in one event."),
    ]


HEADER = """# ==============================================================================
# {stem}
# GENERATED {date} by scripts/build_paper_corrected_decks.py from
#   {parent}
# -- do not hand-edit; regenerate instead. The parent is left untouched.
#
# WHY: scripts/paper_parameter_audit.py compared all four decks against Ye &
# Ghassemi (2018) itself rather than against each other, and found that several
# constants presented as measured joint properties were invented. Every value
# changed below is derived in scripts/refit_joint_constants_from_paper.py from
# the paper's own Table 1, Table 2 and Sec. 2.1. Nothing is tuned to a run.
#
# CONTROLLED AXIS: {axis}
#
{body}#
# UNCHANGED AND DELIBERATELY SO: slip-weakening D_c, exponent and tail floor;
# dilation angles; normal-closure constants; hydraulic constants; every BC and
# the load path. The tail floor is an ABSOLUTE friction coefficient with no JRC
# or JCS in it, so refitting the peak envelope leaves its calibration valid.
#
# STATUS: {status}
# ==============================================================================
"""

DATE = "2026-08-16"

DECKS = [
    dict(out="SWS4/89_01_sw4_bbfast_theta30_paperjrc_kernel_SV_biot0p6.i",
         parent="SWS4/68_01_sw4_bbfast_tail6p50_eta3p50_m0_kernel_SV.i",
         axis="fracture angle AND joint constants (both audit corrections)",
         status="CORRECTION. Both changes replace an invented value with the paper's "
                "own. Re-gate axial_pres_final if the post-ramp tau moves more than "
                "0.5 MPa: the 30 deg mesh raises tau by 2.1 % and the sigma_d part of "
                "sigma'_n by 6.0 % at the same axial load, both toward the data.",
         body="""# 1. MESH  28.990 deg, 2.85 mm off centre  ->  30.000 deg, centred.
#    The old journal reuses SW-S3's fracture-plane offsets (bit-identical z-span),
#    so SW-S4 was never cut at its own angle. Table 2 recovers 30.02 deg from the
#    paper's own eq (3)/(4) at all eleven hold stages, and Table 1 prints 30.
#    Boundary names follow the corrected mesh (top_nodeset/bottom_nodeset/
#    sides_nodeset) and the source nodes move onto the new plane.
# 2. JOINT  JRC 17.50 -> 1.19, JCS 300 -> 150 MPa, phi_r 7.50 -> 23.709 deg.
#    The three errors cancel at the calibration point but d(tau)/d(sigma'_n) does
#    not: 0.322 against 0.447, 28 % too flat, and that derivative is what an
#    injection test sweeps. The old envelope's mu RISES 0.462 -> 0.580 as
#    injection unloads the joint (the "LOCK" several deck generations fought);
#    the new one is flat at 0.456 -> 0.464, matching the near-linear Coulomb
#    envelope the paper's own SW-S4 data show.
#    Slip-weakening slope at onset falls 1.326e11 -> 1.224e11 Pa/m, i.e. from
#    just ABOVE the measured k_sys = 1.25e11 to just below it.
# 3. sigma'_n and tau paper-frame postprocessors added (SW-S4 was the only
#    specimen scored without them).
# 4. W/L 0.81 -> 0.814819511514, inverted from Table 2's own Q, a_h and dP.
# 5. fluid_bulk_modulus -> 2.2e9 (water at 20 C).
""",
         edits=lambda stem: (
             SW_S4_MESH30 + SW_S4_PAPER_JOINT + water() + hpc_outputs(stem) + [
                 sub(r"^paper_flow_width_over_length_sw_s4 = \S+.*$",
                     "paper_flow_width_over_length_sw_s4 = 0.814819511514  # inverted "
                     "from Table 2 via eq (10); was 0.81, 0.5 % low"),
                 insert_after(ANCHOR_S4_PP, SW_S4_PAPER_FRAME),
             ])),

    dict(out="SWS4/89_06_sw4_bbfast_theta30_kernel_SV_biot0p6.i",
         parent="SWS4/68_01_sw4_bbfast_tail6p50_eta3p50_m0_kernel_SV.i",
         axis="fracture angle ONLY (attribution control for 89_01)",
         status="CORRECTION, and the control that separates the mesh effect from the "
                "joint-constant effect in 89_01.",
         body="""# MESH ONLY: 28.990 deg / 2.85 mm off centre -> 30.000 deg / centred, with the
# boundary renames and the source nodes moved onto the new plane. The joint
# constants are left at their pre-audit values so that 89_01 minus this deck
# isolates what the JRC/JCS/phi_r refit does.
# The paper-frame postprocessors, W/L and fluid bulk modulus are corrected here
# too, because they are reporting/physical fixes that are not the axis.
""",
         edits=lambda stem: (
             SW_S4_MESH30 + water() + hpc_outputs(stem) + [
                 sub(r"^paper_flow_width_over_length_sw_s4 = \S+.*$",
                     "paper_flow_width_over_length_sw_s4 = 0.814819511514  # inverted "
                     "from Table 2 via eq (10); was 0.81, 0.5 % low"),
                 insert_after(ANCHOR_S4_PP, SW_S4_PAPER_FRAME),
             ])),

    dict(out="SWS3/89_02_sw3_bbfast_paperjrc_kernel_SV_biot0p6.i",
         parent="SWS3/86_01_sw3_bbfast_biot0p6_phir8p45_m0_kernel_SV.i",
         axis="joint constants only (the SW-S3 mesh is already at its Table-1 angle)",
         status="CORRECTION. The parent deck's own header already concedes that "
                "JRC = 23.35 is 'an explicitly labeled effective transfer parameter, "
                "not a measured joint property'. This deck makes it the measured one.",
         body="""# JOINT  JRC 23.35 -> 1.96, JCS 300 -> 150 MPa, phi_r 8.45 -> 29.756 deg.
# 23.35 is 11.9x the paper's measured 1.96 AND outside Barton's 0-20 scale;
# phi_r = 8.45 deg existed only to compensate for it. The refitted 29.756 deg
# sits squarely in the measured granite basic-friction range.
# The old envelope's mu rises 0.607 -> 0.800 across the injection sweep and sits
# 12-31 % ABOVE the measured tau at every loading hold; the new one is flat at
# 0.603 -> 0.618 and passes exactly through the last stick stage.
# Slip-weakening slope at onset falls 2.084e11 -> 1.797e11 Pa/m (13.8 % more
# stable), so this cannot introduce a strength cliff the parent does not have.
# W/L -> 0.812485740964 and fluid_bulk_modulus -> 2.2e9 as elsewhere.
#
# NOTE the SW-S3 mesh is 124.40 mm long against the paper's 123.40 mm. That
# needs Cubit, which is not available here; mesh/sw3_mesh_L123p4.jou carries the
# corrected journal and mesh/README_mesh_length.md records what it changes
# (0.8 % on axial stiffness only -- the flow path length is set from Table 2).
""",
         edits=lambda stem: (
             SW_S3_PAPER_JOINT + water() + hpc_outputs(stem) + [
                 sub(r"^paper_flow_width_over_length_sw_s3 = \S+.*$",
                     "paper_flow_width_over_length_sw_s3 = 0.812485740964  # inverted "
                     "from Table 2 via eq (10)"),
             ])),

    dict(out="SWT2/89_03_swt2_bbfast_theta30_kernel_SV_biot0p6.i",
         parent="SWT2/87_02_swt2_bbfast_injfix_kernel_SV_biot0p6.i",
         axis="fracture angle only",
         status="CORRECTION, and the control for 89_05.",
         body="""# MESH  31.000 deg -> 30.000 deg.
# Table 1 prints 31 deg but the paper's own reduction disagrees with itself at
# that angle: dividing eq (3) by eq (4) gives tan(theta) = (sigma'_n - sigma_3
# + P_p)/tau, which returns 30.00 deg at all eleven SW-T2 hold stages (and
# reproduces the printed angle for SW-T1, SW-S3 and SW-S4). The data were
# therefore reduced at 30 deg, so the model must be cut at 30 deg.
# The paper-frame postprocessors move with it: sin^2 0.2653 -> 0.25,
# sin*cos 0.4415 -> 0.4330.
""",
         edits=lambda stem: SW_T2_MESH30 + water() + hpc_outputs(stem)),

    dict(out="SWT1/89_04_swt1_bbfast_cohesion_kernel_SV_biot0p6.i",
         parent="SWT1/87_01_swt1_bbfast_injfix_kernel_SV_biot0p6.i",
         axis="strength parameterisation: phi_r = 44.1 deg, c = 0  ->  phi_r = 29.756 "
              "deg, c = 24.65 MPa",
         status="CANDIDATE, not a correction. It must be scored against Table 2 before "
                "it replaces 87_01. Peak strength at the calibration point is identical "
                "by construction, but d(tau)/d(sigma'_n) changes 0.928 -> 0.554, so the "
                "post-onset trajectory will differ materially.",
         body="""# SW-T1 and SW-T2 already use the paper's measured JRC and JCS, yet they need
# phi_r = 44.1 and 46.3 deg -- above every measured granite basic friction angle
# and, for SW-T2, essentially the paper's INTACT-rock friction angle of 46 deg.
# The reason is structural: Barton's roughness term is mobilization-limited and
# decays to zero as sigma'_n approaches JCS. These mated tensile fractures are
# held at sigma'_n/JCS ~ 0.38, where the measured JRC = 15.32 buys only 6.4 deg,
# so a mu of 1.17 has nowhere to live except phi_r. computeCohesionEffective()
# returned a hard-coded 0.0, so cohesion was not available.
#
# This deck uses the new `cohesion` / `residual_cohesion` parameters (branch
# orca_v5) to put that strength where it physically belongs:
#   phi_r             = 29.756 deg  -- granite basic friction, measured on this
#                                      campaign's OWN saw cut (SW-S3 refit)
#   cohesion          = 24.65 MPa   -- asperity interlock at peak; 81 % of the
#                                      30.30 MPa intact cohesion implied by the
#                                      paper's own UCS = 150 MPa and phi = 46 deg
#   residual_cohesion = 11.176 MPa  -- interlock surviving the burst, pinned on
#                                      the post-burst stage (31.79, 29.35 MPa)
#   tail phi          = 29.756 deg  -- slip destroys roughness, not the rock's
#                                      basic friction angle (Barton's own picture)
# Nothing in the derivation knows about the intact cohesion, so landing next to
# it is a result rather than a fit.
""",
         edits=lambda stem: (
             cohesion_refit("SW-T1", "29.756", "2.465e7", "1.1176e7", "44.1", "40")
             + water() + hpc_outputs(stem))),

    dict(out="SWT2/89_05_swt2_bbfast_theta30_cohesion_kernel_SV_biot0p6.i",
         parent="SWT2/87_02_swt2_bbfast_injfix_kernel_SV_biot0p6.i",
         axis="fracture angle AND strength parameterisation",
         status="CANDIDATE, not a correction. Score against 89_03 (mesh only) to "
                "separate the two effects.",
         body="""# 1. MESH  31.000 -> 30.000 deg, as 89_03; see that deck's header.
# 2. STRENGTH  phi_r = 46.29 deg, c = 0  ->  phi_r = 29.756 deg,
#    cohesion = 31.65 MPa, residual_cohesion = 10.695 MPa, tail phi = 29.756 deg.
#    46.29 deg is essentially the paper's INTACT-rock friction angle of 46 deg,
#    which is not a joint property. The refitted cohesion is 104 % of the
#    30.30 MPa intact cohesion implied by the paper's own UCS and phi -- exactly
#    what a fully mated Mode-I fracture should show, since its asperities ARE
#    intact rock. d(tau)/d(sigma'_n) changes 0.999 -> 0.553.
""",
         edits=lambda stem: (
             SW_T2_MESH30
             + cohesion_refit("SW-T2", "29.756", "3.165e7", "1.0695e7",
                              "46.29182452", "40.2")
             + water() + hpc_outputs(stem))),
]


SLURM = """#!/bin/bash

#SBATCH --job-name={stem}_hpc
#SBATCH --account=def-biaoli66
#SBATCH --time={time}
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --output=logs/{stem}_hpc_%j.out
#SBATCH --error=logs/{stem}_hpc_%j.err

cd /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/{sample}

# Clear conflicting memory env vars (Alliance injects SLURM_MEM_PER_CPU; --mem sets SLURM_MEM_PER_NODE).
unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p results_csv_hpc_rorqual results_exodus_hpc_rorqual logs

srun --mpi=pmi2 -n 32 /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/orca-opt -i {stem}.i \\
    Outputs/chk/enable=false \\
    csv_file_base=results_csv_hpc_rorqual/{stem}_hpc \\
    exodus_file_base=results_exodus_hpc_rorqual/{stem}_hpc
"""

WALLTIME = {"SWS3": "24:00:00", "SWS4": "24:00:00", "SWT1": "12:00:00", "SWT2": "12:00:00"}


def main():
    dry = "--check" in sys.argv
    for d in DECKS:
        out = os.path.join(EX, d["out"])
        parent = os.path.join(EX, d["parent"])
        stem = os.path.splitext(os.path.basename(out))[0]
        sample = d["out"].split("/")[0]

        text = open(parent).read()
        text = apply_edits(text, d["edits"](stem), stem)
        header = HEADER.format(stem=stem, date=DATE, parent=d["parent"],
                               axis=d["axis"], body=d["body"], status=d["status"])
        text = header + text

        sh = os.path.join(EX, sample, stem + "_hpc_nochk.sh")
        if dry:
            print(f"[dry] would write {d['out']}  ({len(text.splitlines())} lines)")
            print(f"[dry] would write {sample}/{stem}_hpc_nochk.sh")
            continue
        with open(out, "w") as f:
            f.write(text)
        with open(sh, "w") as f:
            f.write(SLURM.format(stem=stem, sample=sample, time=WALLTIME[sample]))
        os.chmod(sh, 0o755)
        print(f"wrote {d['out']}")
        print(f"wrote {sample}/{stem}_hpc_nochk.sh")


if __name__ == "__main__":
    main()
