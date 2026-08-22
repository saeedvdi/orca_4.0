#!/usr/bin/env python3
"""
build_103_weakening_exponent_decks.py -- the slip-weakening exponent control.

THE QUESTION
============
The 102-series showed linear Mohr-Coulomb failing one injection stage before the
measured slip event on SW-T1, SW-T2 and SW-S3, while its BBFast pair stays on the
measured high-strength branch.  The write-up attributed that to "a single
roughness-dependent path".  Tracing the yield event says something much more
specific, and this deck set tests it.

WHAT THE 102 DATA ACTUALLY SHOW
===============================
The two envelopes are matched at BOTH ends, not just at onset:

    specimen   peak tau_lim (BB / MC)     residual tau_lim (BB / MC)
    SW-T1      73.675 / 73.765 MPa        35.695 / 36.726 MPa
    SW-T2      80.108 / 80.223            36.371 / 35.896
    SW-S3      21.316 / 21.292             8.506 /  6.871
    SW-S4      15.735 / 15.758             6.096 /  6.722

Peak agrees to <= 0.12 MPa everywhere.  And stages 1-4 of every paired run agree
to ~1e-4 MPa in tau.  So the transfer is sound: the arms are the same model until
yield, and they end at the same residual.  The ONLY thing that differs is the
PATH between those two endpoints -- the shape of the weakening in slip:

    BBFast   W    = exp(-(gamma/D_c)^m)   with m = 1.4 (SW-S4: 1.10)
    MC       Rbar = exp(-gamma/L)          i.e. m = 1 identically

At gamma << D_c the two are far apart, and gamma << D_c is exactly where the
yield decision is made.  Measured on SW-T1, strength lost per unit plastic slip:

    gamma =  1 um   BB 0.016 MPa   MC 0.185 MPa   ratio 11.7x
    gamma =  5 um   BB 0.151       MC 0.913       ratio  6.1x
    gamma = 20 um   BB 1.023       MC 3.476       ratio  3.4x

The pre-yield strength margin is only 1-2 MPa, so that is decisive.  At t = 1350 s
on SW-T1 the BBFast margin is +1.043 MPa and the MC margin is -0.068 MPa, and the
difference is entirely in how much cohesion each has already shed at the same
plastic slip (0.036 vs 0.885 MPa).

THE INTERNAL CONSISTENCY CHECK THAT MOTIVATED THIS
==================================================
Solve for the decay length that would make MC lose strength at BBFast's rate at
the plastic slip each specimen has reached at its last pre-event stage:

    specimen   gamma at stage 5   D_c      m      L needed   L used    factor
    SW-T1          1.50 um       150 um   1.40   9.46e-4    1.5e-4      6.3x
    SW-T2          2.95 um       150 um   1.40   7.22e-4    1.5e-4      4.8x
    SW-S3          0.70 um        60 um   1.40   3.56e-4    4.0e-5      8.9x
    SW-S4         47.64 um       74.5 um  1.10   7.79e-5    8.0e-5      1.0x

SW-S4 needs no correction -- its exponent is already 1.10, so its MC transfer is
rate-matched by construction.  And SW-S4 is precisely the one specimen where MC
nearly matches BBFast (1.46x overall, and 1.09x once the d_n channel is set
aside).  The three specimens carrying m = 1.4 are the three where MC collapses.
That correlation is already in the existing data and costs nothing, but it is
correlational.  This deck set makes it causal.

WHY THE TEST RUNS ON THE BBFast SIDE
====================================
The obvious experiment -- lengthen the MC roughness decay until it matches -- is
not clean, and 102_01's own header says why:

    "roughness_state is consumed by [czm_aperture]
     (ADOrcaRoughnessDamageFracturePermeability), so these three MUST match or
     the hydraulic aperture -- and therefore Q -- would differ for a reason that
     has nothing to do with the shear law."

In the MC material ONE state variable drives both the strength and the aperture,
so any change to its decay moves Q as a side effect.  The exponent parameters
cannot be used to compensate either: friction_roughness_exponent and
cohesion_roughness_exponent are range-checked >= 1.0, and they only ever make the
strength decay FASTER.

BBFast has no such coupling.  Strength weakening uses characteristic_slip_distance
and slip_weakening_exponent; the aperture uses a separate roughness_characteristic_slip
with its own exponential.  So setting

    slip_weakening_exponent : 1.4 -> 1.0

changes the strength path into exactly MC's form and touches nothing else -- not
the envelope endpoints, not the aperture, not the dilation, not the unload
retention, not the solver.  ONE parameter.

PREDICTION, WRITTEN DOWN BEFORE THE RUNS
========================================
If the exponent is the mechanism, 103 should reproduce the MC failure mode on all
three specimens: yield at stage 5 instead of stage 6, ~0.5 mm of slip one stage
early, tau collapsing to near residual while the measurement is still on the
high-strength branch.  Its mean nRMSE should move a large fraction of the way
from its BBFast parent toward its MC pair.

FALSIFIER: if 103 still holds through stage 5, the exponent is NOT the mechanism
and the 102 gap has another cause -- look next at the normal-unloading path,
which is the other known asymmetry (every MC arm's normal jump is frozen after
slip: SW-T1 closes 2.0 nm against a 9.6 MPa rise in sigma'_n, where BBFast closes
36.4 um).

WHAT THIS DOES AND DOES NOT LICENCE
===================================
It does not make MC "unfairly treated" -- a linear Coulomb law with a single
roughness state genuinely cannot carry a weakening exponent, and that is a real
limitation of the formulation.  What it does is convert the manuscript's claim
from "MC weakens too early" into "the weakening EXPONENT is what places the
transition, and a one-state Coulomb law has no way to represent it" -- a
statement about constitutive form, which is what the paper says it is arguing.

SW-S4 IS DELIBERATELY NOT INCLUDED.  Its exponent is 1.10, so this change is a
9% perturbation rather than a test, and its cohesion-weakening channel is inert
in any case (cohesion_effective == 0; see task #91).
"""

import os
import re
import stat

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EX = os.path.join(ROOT, "Examples", "YeGhasemmi2018")

NEW_EXPONENT = 1.0

# sample, BBFast best-case parent, new stem, the MC pair this is predicting
DECKS = [
    ("SWT1", "100_01_swt1_vm55um_ppfix",
     "103_01_swt1_weakexp1p0_ppfix", "102_01_swt1_mc_vm55um_ppfix"),
    ("SWT2", "100_04_swt2_apscale0p0177_ppfix",
     "103_02_swt2_weakexp1p0_ppfix", "102_02_swt2_mc_apscale0p0177_ppfix"),
    ("SWS3", "100_06_sw3_resc1p30_unld0p00_ppfix",
     "103_03_sw3_weakexp1p0_ppfix", "102_03_sw3_mc_resc1p30_ppfix"),
]

HEADER = """
######################################################################################
# 103-SERIES CONTROL DECK -- slip-weakening EXPONENT, and nothing else.
#
#   parent : {parent}
#   pair   : {mc} (the Mohr-Coulomb arm this is predicting)
#
# ONE parameter changes from the parent: slip_weakening_exponent {old} -> {new}.
# That turns BBFast's strength weakening
#       W = exp(-(gamma/D_c)^{old})
# into the form the transferred Mohr-Coulomb law is stuck with,
#       W = exp(-(gamma/D_c)^1) = exp(-gamma/D_c),
# while leaving the peak envelope, the residual envelope, the hydraulic aperture
# (which BBFast drives from a SEPARATE roughness_characteristic_slip), the
# dilation, the normal-unload retention and the solver exactly as calibrated.
#
# The 102 pairs agree to ~1e-4 MPa in tau through stage 4 and land on the same
# residual, so the weakening PATH is the only thing left that can explain why the
# MC arm yields a stage early.  This deck isolates it.
#
# PREDICTION: yield at stage 5 rather than stage 6; ~0.5 mm of slip one stage
# early; mean nRMSE moving a large fraction of the way from the parent toward the
# MC pair.
# FALSIFIER: if stage 5 still holds, the exponent is not the mechanism -- look at
# the normal-unloading path instead (every MC arm's normal jump is frozen after
# slip; SW-T1 closes 2.0 nm for a 9.6 MPa rise in sigma'_n where BBFast closes
# 36.4 um).
#
# Scoreable against Table 2: YES.  Unlike the 97/98/101 discussion decks this one
# keeps the paper's own monotonic injection history, so scripts/table2_gate.py
# applies directly and the result is directly comparable to its parent and pair.
######################################################################################
"""

SLURM = """#!/bin/bash
# Local run: {ranks} ranks.  The workstation ceiling is 24 ranks TOTAL across all
# concurrent jobs -- past that the wall time doubles rather than improving.
set -euo pipefail
cd "$(dirname "$0")"
mkdir -p results_csv_local results_exodus_local logs

mpiexec -n {ranks} ../../../orca-opt -i {stem}.i \\
    Outputs/chk/enable=false \\
    csv_file_base=results_csv_local/{stem}_local \\
    exodus_file_base=results_exodus_local/{stem}_local \\
    2>&1 | tee logs/{stem}_local.log
"""


def set_scalar(text, name, value, note):
    pat = re.compile(rf"^(\s*){re.escape(name)}\s*=\s*\S+.*$", flags=re.M)
    m = pat.search(text)
    if not m:
        raise RuntimeError(f"'{name}' not found")
    return pat.sub(lambda mm: f"{mm.group(1)}{name} = {value}    # 103: {note}",
                   text, count=1)


def main():
    ranks = 8
    print(f"{'deck':32s} {'parent':34s} {'exponent':>9s}")
    for sample, parent, stem, mc in DECKS:
        path = os.path.join(EX, sample, parent + ".i")
        with open(path) as fh:
            text = fh.read()

        m = re.search(r"^\s*slip_weakening_exponent\s*=\s*(\S+)", text, flags=re.M)
        if not m:
            raise RuntimeError(f"{parent}: slip_weakening_exponent not found")
        old = m.group(1)
        if old.startswith("${"):
            raise RuntimeError(f"{parent}: exponent is indirected through {old}; "
                               "set the top-level variable instead")

        text = text.replace(parent, stem)
        text = set_scalar(text, "slip_weakening_exponent", NEW_EXPONENT,
                          f"was {old}; the ONLY change from {parent}")
        text = HEADER.format(parent=parent, mc=mc, old=old, new=NEW_EXPONENT) + text

        out = os.path.join(EX, sample, stem + ".i")
        with open(out, "w") as fh:
            fh.write(text)

        sh = os.path.join(EX, sample, stem + "_local.sh")
        with open(sh, "w") as fh:
            fh.write(SLURM.format(stem=stem, ranks=ranks))
        os.chmod(sh, os.stat(sh).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)

        print(f"{stem:32s} {parent:34s} {old:>6s} -> {NEW_EXPONENT}")


if __name__ == "__main__":
    main()
