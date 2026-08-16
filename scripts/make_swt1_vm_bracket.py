#!/usr/bin/env python3
"""
make_swt1_vm_bracket.py -- generate the SW-T1 normal-closure (V_m) bracket decks.

WHY THIS BRACKET EXISTS
=======================
Scoring the finished SW-T1 alpha=0.6 run against the 2026-08-16 re-extracted
validation set showed two complaints that SURVIVE an optimal uniform time shift,
i.e. they are not injection-schedule phase error:

    normal dilation rebound   model  17.4 um   measured  49.3 um   (0.35x)
    eff. normal stress rebound model  17.33 MPa measured   9.55 MPa (1.82x)

Those are not two defects. On a matched window (each record's own peak-open to
t = 3000 s) they are one number -- the normal UNLOADING STIFFNESS of the
joint+frame system:

    model     +16.23 um  /  +13.94 MPa  ->  0.859 MPa/um
    measured  +44.21 um  /   +5.98 MPa  ->  0.135 MPa/um      6.3x too stiff

A joint that is too stiff on unload cannot open, so it under-delivers dilation,
and it over-transmits the stress change, so sigma'_n over-rebounds. Because
SW-T1 runs use_kinematic_aperture = true, the hydraulic aperture is the
mechanical gap, so the same defect appears a third time in the hydraulics:
fracture permeability decays only 1.15x from peak to end of unload against 1.46x
measured, while the PEAK permeability is fine (1.04x). The residual permeability
misfit is entirely on the unload branch.

WHERE THE STIFFNESS COMES FROM
==============================
The deck's closure constants put the joint on the vertical part of the
Barton-Bandis power law before any load is applied. With

    sigma_n = (K_ni V_m) [c / (V_m - c)]^(1/p)     (OrcaNormalClosure.h)
    K_ni = 2.443e11 Pa/m,  V_m = 4.591e-5 m,  p = 3.28,  offset = 4.433e-5 m

the pre-seating offset alone is 96.6% of V_m, and at the operating stresses the
closure ratio and tangent are

    sigma'_n = 67 MPa (preload)     c/V_m = 0.9972    k_n = 158 MPa/um  (646x K_ni)
    sigma'_n = 35 MPa (event min)   c/V_m = 0.9766    k_n =  10 MPa/um  ( 42x K_ni)

so the joint is effectively rigid across the whole experiment. The scale stress
of the law is sigma_0 = K_ni V_m = 11.2 MPa, and the specimen is run at 30-67
MPa -- 3 to 6 times past it. This is why normal_unload_retention_fraction never
cured the over-rebound: at f = 0.94 it is already suppressing 94% of the
reclosure, but it modulates a spring roughly 12x stiffer than the bulk/frame
path it sits in series with (inferred k_frame ~ 0.94 MPa/um), so it has almost
no authority over the system stiffness. It is the wrong knob, not a knob set
wrong.

WHAT THE BRACKET DOES
=====================
Raise V_m so the joint sits lower on the asymptote and keeps some compliance in
the 30-67 MPa window, and re-solve normal_closure_offset so the PRE-SEATED
STRESS AT ZERO MECHANICAL OVERLAP IS UNCHANGED. Holding that invariant is the
whole point: it keeps the preload state and the Table-2 aperture fit intact so
the only thing the bracket varies is the tangent stiffness.

Two points, not one, for the same reason the SW-S3 phi_r bracket used two: the
frame stiffness is INFERRED from a single scored run under a series-spring
assumption, so the required softening is a magnitude, not a prediction. The
bracket is sized to straddle the measured 0.135 MPa/um rather than to hit it.

NOT DONE HERE, DELIBERATELY
===========================
reversible_normal_compliance would make the dilation panel match on its own, but
it is declared OUTPUT ONLY -- it adds C_n <sigma_ref - sigma'_n>_+ to the
reported opening and cannot touch traction, aperture, permeability or flow. It
would repair one panel of a three-panel symptom and leave sigma'_n and the
permeability unload branch exactly as wrong as they are now. Fix the stiffness
first; only then decide whether any cosmetic term is still warranted.
"""

import os
import re

EX = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                  "Examples", "YeGhasemmi2018")
PARENT = os.path.join(EX, "SWT1", "87_01_swt1_bbfast_injfix_kernel_SV_biot0p6.i")

K_NI = 2.443e11      # Pa/m
V_M = 4.591e-5       # m
P = 3.28
OFFSET = 4.433e-5    # m


def sigma(c, v_m, k_ni=K_NI):
    """Barton-Bandis power-law closure stress [Pa]."""
    return k_ni * v_m * (c / (v_m - c)) ** (1.0 / P)


def closure_for_sigma(s, v_m, k_ni=K_NI):
    """Invert the law: closure [m] that produces stress s [Pa]."""
    x = (s / (k_ni * v_m)) ** P
    return x * v_m / (1.0 + x)


def tangent(c, v_m, k_ni=K_NI):
    """d(sigma_n)/d(closure) [Pa/m]."""
    x = c / (v_m - c)
    return (k_ni * v_m / P) * x ** (1.0 / P - 1.0) * v_m / (v_m - c) ** 2


def offset_preserving_preseat(v_m, k_ni=K_NI):
    """New offset that reproduces the original pre-seated stress at zero overlap."""
    return closure_for_sigma(sigma(OFFSET, V_M), v_m, k_ni)


def softest_possible_joint(k_ni=K_NI):
    """
    Lowest tangent stiffness the power law can produce at ANY stress, for a given
    K_ni, minimised over V_m.

    Substituting x = c/(V_m - c) into the tangent collapses V_m out entirely:

        k_n = (K_ni / p) x^(1/p - 1) (1 + x)^2

    so V_m only moves the joint along a fixed curve -- it cannot lower the floor.
    d/dx of the bracket vanishes at x* = -a/(a + 2) with a = 1/p - 1, giving

        k_n,min = (K_ni / p) (x*)^a (1 + x*)^2

    This is why the bracket below is not V_m alone: the answer to "how soft can
    V_m make this joint" is a number, and it is not soft enough.
    """
    a = 1.0 / P - 1.0
    x_star = -a / (a + 2.0)
    return (k_ni / P) * x_star ** a * (1.0 + x_star) ** 2, x_star


# Measured joint+frame unloading stiffness, and what 87_01 actually delivers,
# both on the matched window (own peak-open -> t = 3000 s).
K_SYS_MEASURED = 0.135e12   # Pa/m
K_SYS_PARENT = 0.859e12     # Pa/m

# Series-spring inference: 1/k_sys = 1/k_joint + 1/k_frame, evaluated at the
# event-minimum stress. This is ONE equation with ONE unknown fitted to ONE
# scored run -- it is not an independent measurement of the frame, which is
# exactly why the arms below span a factor of 4 in V_m instead of aiming at a
# single computed answer.
K_FRAME = 1.0 / (1.0 / K_SYS_PARENT - 1.0 / tangent(closure_for_sigma(35e6, V_M), V_M))

# Joint stiffness needed so the series pair lands on the measured system value.
K_JOINT_TARGET = 1.0 / (1.0 / K_SYS_MEASURED - 1.0 / K_FRAME)

# V_m alone bottoms out at softest_possible_joint(K_NI); if that floor is above
# K_JOINT_TARGET then K_ni has to move as well, and by at least this factor.
_K_FLOOR, _ = softest_possible_joint(K_NI)
K_NI_SCALE = min(1.0, K_JOINT_TARGET / _K_FLOOR)

SIGMA_EVENT = 35e6  # Pa, the effective normal stress at the slip-event minimum


def v_m_at_softest(k_ni):
    """V_m that puts the joint at its stiffness minimum when sigma'_n = SIGMA_EVENT."""
    _, x_star = softest_possible_joint(k_ni)
    return SIGMA_EVENT / (k_ni * x_star ** (1.0 / P))


ARMS = [
    # tag, slug, V_m [m], K_ni [Pa/m], one-line intent
    ("88_01", "vm2x", V_M * 2.0, K_NI,
     "V_m x2 -- partial softening, closure still near the fitted regime"),
    ("88_02", "vmopt", v_m_at_softest(K_NI), K_NI,
     "V_m at the analytic softness optimum -- the softest this law gets at fixed K_ni"),
    ("88_03", "vmopt_kni", v_m_at_softest(K_NI * K_NI_SCALE), K_NI * K_NI_SCALE,
     f"same, plus K_ni x{K_NI_SCALE:.3f} -- the only way past the fixed-K_ni floor"),
]


def main():
    with open(PARENT) as fh:
        parent = fh.read()

    baseline_preseat = sigma(OFFSET, V_M)
    print(f"parent: V_m={V_M:.4e}  offset={OFFSET:.4e}  offset/V_m={OFFSET/V_M:.4f}")
    print(f"        pre-seated stress at zero overlap = {baseline_preseat/1e6:.2f} MPa")
    for s in (35e6, 67e6):
        c = closure_for_sigma(s, V_M)
        print(f"        at sigma'_n={s/1e6:5.1f} MPa: c/V_m={c/V_M:.4f}  "
              f"k_n={tangent(c, V_M)/1e12:7.3f} MPa/um")
    print(f"        inferred k_frame = {K_FRAME/1e12:.3f} MPa/um   "
          f"target k_sys = {K_SYS_MEASURED/1e12:.3f} MPa/um")

    floor, x_star = softest_possible_joint(K_NI)
    print(f"        V_m-only stiffness floor at K_ni = {K_NI:.4g}: "
          f"{floor/1e12:.3f} MPa/um (x* = {x_star:.4f})")
    print(f"        k_joint needed for k_sys = {K_SYS_MEASURED/1e12:.3f}: "
          f"{K_JOINT_TARGET/1e12:.3f} MPa/um  ->  K_ni must scale by {K_NI_SCALE:.3f}")

    for tag, slug, v_m, k_ni, intent in ARMS:
        off = offset_preserving_preseat(v_m, k_ni)
        deck = f"{tag}_swt1_bbfast_{slug}_injfix_kernel_SV_biot0p6"
        print(f"\n{deck}\n  {intent}")
        print(f"  V_m={v_m:.4e} ({v_m/V_M:.2f}x)  K_ni={k_ni:.4e} ({k_ni/K_NI:.3f}x)  "
              f"offset={off:.4e}  offset/V_m={off/v_m:.4f}")
        print(f"  pre-seat check = {sigma(off, v_m, k_ni)/1e6:.2f} MPa "
              f"(parent {baseline_preseat/1e6:.2f})")
        stiff = {}
        for s in (35e6, 67e6):
            c = closure_for_sigma(s, v_m, k_ni)
            stiff[s] = tangent(c, v_m, k_ni)
            print(f"  at sigma'_n={s/1e6:5.1f} MPa: c/V_m={c/v_m:.4f}  "
                  f"k_n={stiff[s]/1e12:7.3f} MPa/um")
        k_sys = 1.0 / (1.0 / stiff[35e6] + 1.0 / K_FRAME)
        print(f"  predicted k_sys = {k_sys/1e12:.3f} MPa/um "
              f"(parent {K_SYS_PARENT/1e12:.3f}, measured {K_SYS_MEASURED/1e12:.3f})")

        text = parent

        # The three closure constants. Anchored to line starts so the prose in the
        # header (which names these parameters) cannot be hit -- the same class of
        # mistake that made an unanchored [injection_pressure] regex match a comment
        # when the 87_0x decks were built. initial_normal_stiffness is matched with a
        # leading-whitespace anchor so it cannot collide with the deck-level
        # bb_initial_normal_stiffness, which is a different (aperture) parameter.
        text, n1 = re.subn(r"^(\s*maximum_closure\s*=\s*)\S+",
                           lambda m: f"{m.group(1)}{v_m:.6e}", text, flags=re.M)
        text, n2 = re.subn(r"^(\s*normal_closure_offset\s*=\s*)\S+",
                           lambda m: f"{m.group(1)}{off:.6e}", text, flags=re.M)
        text, n3 = re.subn(r"^(\s+initial_normal_stiffness\s*=\s*)\S+",
                           lambda m: f"{m.group(1)}{k_ni:.6e}", text, flags=re.M)
        assert n1 == 1 and n2 == 1 and n3 == 1, (
            f"{deck}: matched V_m {n1}x, offset {n2}x, K_ni {n3}x")

        # Output basenames.
        text = text.replace("87_01_swt1_bbfast_injfix_kernel_SV_biot0p6", deck)

        header = f"""# =============================================================================
# {deck}.i
#
# SW-T1 normal-closure stiffness bracket, arm {tag}.
# {intent}
#
# Derived from 87_01 (the injection-schedule-corrected deck). ONLY the
# Barton-Bandis closure constants differ:
#
#     maximum_closure          {V_M:.4e} -> {v_m:.4e}   ({v_m/V_M:.2f}x)
#     initial_normal_stiffness {K_NI:.4e} -> {k_ni:.4e}   ({k_ni/K_NI:.3f}x)
#     normal_closure_offset    {OFFSET:.4e} -> {off:.4e}
#
# The offset is re-solved so the PRE-SEATED STRESS AT ZERO MECHANICAL OVERLAP is
# unchanged at {baseline_preseat/1e6:.2f} MPa. That invariant keeps the preload state and the
# Table-2 aperture fit intact, so the arm varies tangent stiffness ALONE.
#
# Joint tangent stiffness k_n = d(sigma_n)/d(closure), from the deck constants
# through the actual law in OrcaNormalClosure.h:
#
#                        parent 87_01        this arm
#   sigma'_n = 67 MPa    {tangent(closure_for_sigma(67e6, V_M), V_M)/1e12:8.2f} MPa/um    {stiff[67e6]/1e12:8.3f} MPa/um
#   sigma'_n = 35 MPa    {tangent(closure_for_sigma(35e6, V_M), V_M)/1e12:8.2f} MPa/um    {stiff[35e6]/1e12:8.3f} MPa/um
#
# TARGET. The measured joint+frame unloading stiffness is {K_SYS_MEASURED/1e12:.3f} MPa/um; 87_01
# delivers {K_SYS_PARENT/1e12:.3f} MPa/um, {K_SYS_PARENT/K_SYS_MEASURED:.1f}x too stiff. That single number is BOTH reported
# symptoms -- normal dilation rebound 0.35x measured, and effective normal stress
# rebound 1.82x measured -- and, through use_kinematic_aperture = true, the
# under-decaying permeability on the unload branch as well.
#
# Predicted system stiffness for this arm, 1/k_sys = 1/k_joint + 1/k_frame with
# the inferred k_frame = {K_FRAME/1e12:.3f} MPa/um:
#
#     k_sys ~ {1.0/(1.0/stiff[35e6] + 1.0/K_FRAME)/1e12:.3f} MPa/um     (parent {K_SYS_PARENT/1e12:.3f}, measured {K_SYS_MEASURED/1e12:.3f})
#
# WHY THREE ARMS AND WHY K_ni MOVES. Substituting x = c/(V_m - c) collapses V_m
# out of the tangent entirely: k_n = (K_ni/p) x^(1/p-1) (1+x)^2. V_m therefore
# only slides the joint along a fixed curve whose minimum is {floor/1e12:.3f} MPa/um at
# K_ni = {K_NI:.4g} -- above the {K_JOINT_TARGET/1e12:.3f} MPa/um the series pair needs. So V_m alone
# PROVABLY cannot reach the measured compliance, and arm 88_03 scales K_ni by
# {K_NI_SCALE:.3f} to get past that floor. 88_01/88_02 bracket how much of the misfit V_m
# can absorb on its own.
#
# k_frame is fitted to a single scored run under a series-spring assumption --
# one equation, one unknown -- so it is a magnitude, not an independent
# measurement. Score all three and interpolate; do not assume any one lands.
#
# See scripts/make_swt1_vm_bracket.py for the full derivation.
# =============================================================================
"""
        out = os.path.join(EX, "SWT1", deck + ".i")
        with open(out, "w") as fh:
            fh.write(header + text)
        print(f"  wrote {out}")


if __name__ == "__main__":
    main()
