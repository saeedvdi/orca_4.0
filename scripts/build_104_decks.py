#!/usr/bin/env python3
"""
build_104_decks.py -- the two follow-ups the 101 analysis left open.

Both are shut-in decks, so they reuse build_101_decks' schedule builder verbatim
and differ from their 101 counterparts in ONE parameter each (arm 1) or in the
shut-in time constant only (arm 2).

=============================================================================
ARM 1 (104_01..03) -- WHY DOES SW-S4 CLOSE WHEN THE OTHER THREE PROP OPEN?
=============================================================================
101 measured, at MATCHED effective normal stress (end state vs the loading path
at the same sigma'_n, so reversible closure is differenced out):

    SW-T1  k x1.609      SW-T2  k x1.459      SW-S3  k x1.497      SW-S4  k x0.859

SW-S4 is the only specimen that ends LESS permeable than it was on the way up.

TWO EXPLANATIONS WERE PROPOSED AND BOTH WERE WRONG.

(1) "Roughness destruction."  Falsified by the 101 data itself: all four degrade
    and SW-S3 degrades MOST while still gaining.

        SW-T1  roughness_state 0.2246 -> 0.1264 (-43.7%)   k x1.609
        SW-T2                  0.1882 -> 0.1206 (-35.9%)   k x1.459
        SW-S3                  0.6400 -> 0.1862 (-70.9%)   k x1.497
        SW-S4                  0.4478 -> 0.2128 (-52.5%)   k x0.859

(2) "SW-S4's dilation contribution was cut 17x in calibration, so it is the one
    specimen where the loss term wins."  This is what DISCUSSION_101_RESULTS.md
    said on first writing and it is also wrong, because SW-T1 and SW-T2 carry
    dilation_scale = 0.0 -- strictly less than SW-S4's 0.0117 -- and they prop
    open the most.  dilation_scale cannot be read across specimens at all,
    because it is only live when use_kinematic_aperture = false.

WHAT THE SOURCE ACTUALLY SAYS.  In
ADOrcaRoughnessDamageFracturePermeability.C::computeQpProperties,

    a_h = a_h0 + stress_aperture + aperture_scale*mechanical_aperture
                                 + dilation_term + self_prop - slip_damage_fill

    dilation_term   = 0                                   if use_kinematic_aperture
                    = dilation_scale * cumulative_dilation * retention(R)  otherwise
    retention(R)    = retention_residual + (1-retention_residual)*R
    R               = 1                                   if use_kinematic_aperture
                    = roughness_state                     otherwise
    slip_damage_fill= slip_damage_scale * (1 - exp(-<s-s*>_+ / s_c))   if use_slip_damage

and the decks pair up like this:

    specimen  a_h0     kinematic  dilation_scale  use_slip_damage  damage_scale  s*
    SW-T1     1.63 um  true       0.0             FALSE            --            --
    SW-T2     2.11 um  true       0.0             FALSE            --            --
    SW-S3     1.22 um  false      0.038           true             0.40 um       30 um
    SW-S4     0.74 um  false      0.0117          true             0.28 um       20 um

So SW-T1/T2 are in kinematic mode: R is PINNED AT 1, the dilation term is off by
construction (it already lives in mechanical_aperture), and use_slip_damage is
false.  Their aperture has NO subtraction channel of any kind -- roughness
degradation is incapable of closing them, which is why (1) failed.

The gouge-fill term is enabled on SW-S3 and SW-S4 ONLY, and at the end of the
101 shut-in runs it is worth

    SW-S3   0.40*(1-exp(-(73.8-30)/30)) = 0.307 um  =  25% of its 1.22 um a_h0
    SW-S4   0.28*(1-exp(-(90.7-20)/30)) = 0.253 um  =  34% of its 0.74 um a_h0

(the SW-S4 figure reproduces the run's own slip_damage_aperture_um_pp = 0.2533
to four figures, so this is the term, not an estimate of it).

WORKING HYPOTHESIS: the closure sign is set by the balance between the dilation
term and the gouge-fill term, and SW-S4 loses because it has the SMALLEST
dilation gain (dilation_scale 0.0117, a third of SW-S3's) against the LARGEST
fractional subtraction (34% of a_h0, and its onset s* is 20 um rather than 30 um
so it starts filling earlier).

These three decks separate the two arms.  Each changes exactly one thing.

    104_01  SW-S4, use_slip_damage false      -- kill the subtraction
    104_02  SW-S4, dilation_scale -> 0.038    -- raise the gain to SW-S3's
    104_03  SW-S3, use_slip_damage false      -- same knob, on the specimen
                                                 that already gains

PREDICTIONS, written before the runs:
  * 104_01 flips the sign: k ratio 0.859 -> above 1.0.  If it does not, the
    gouge-fill term is not what closes SW-S4 and the remaining suspect is the
    retention discount on the dilation term.
  * 104_02 raises the ratio.  Whether it alone clears 1.0 says whether the
    dilation arm is sufficient on its own or only contributory.
  * 104_03 raises SW-S3 above 1.497.  This is the sign control: the same knob
    must push the same way on a specimen that is already on the other side of
    the line.  If SW-S3 barely moves while SW-S4 flips, the two specimens are
    not differing by this channel and the hypothesis is wrong even if 104_01
    "works".

NOT SCOREABLE AGAINST TABLE 2.  104_01..03 change calibrated parameters, so
their monotonic accuracy is meaningless; they answer a mechanism question about
the 101 result and nothing else.  The validated run for each specimen remains
its 93-series parent.

=============================================================================
ARM 2 (104_04..05) -- FINISH THE RATE-INDEPENDENCE TEST
=============================================================================
101 group D ran the slow bleed-off (tau = 1500 s vs 150 s) on SW-T1 and SW-S4
only, and found the retained permeability essentially unmoved:

    SW-T1   k x1.609 (tau=150)  ->  x1.584 (tau=1500)     -1.6%
    SW-S4   k x0.859            ->  x0.855                -0.5%

That is two specimens, not four, and the manuscript should not generalise a
rate-independence claim from half the set.  These two decks complete it with no
new parameters at all -- same hold, same tau, same observation window as 101_13
and 101_14, applied to the two specimens that were missing.

PREDICTION: both land within ~2% of their tau = 150 s values (SW-T2 x1.459,
SW-S3 x1.497).  A larger move on either would mean the shut-in decay time is a
real variable and the 101 group-D result was specimen-specific luck.

These two ARE ordinary 101-group-D decks; they carry no parameter change and
exist only because group D was under-populated.
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from build_101_decks import (  # noqa: E402
    EX,
    SHUTIN_OBSERVE_SLOW,
    SHUTIN_TAU_SLOW,
    SHUTIN_TAU_FAST,
    SHUTIN_OBSERVE,
    SPECS,
    T_SETTLE,
    build,
    shutin_expression,
    write_slurm,
)


def set_scalar_104(path, name, value, note):
    """Rewrite one top-level scalar in a written deck.

    build_101_decks.set_scalar formats with '%.10g', so it cannot carry a MOOSE
    boolean, and it tags every edit '# 101:' -- wrong in a 104 deck.  Doing the
    edits here keeps the provenance comment honest and accepts both types.
    """
    with open(path) as fh:
        text = fh.read()
    pat = re.compile(rf"^(\s*){re.escape(name)}\s*=\s*\S+.*$", flags=re.M)
    if not pat.search(text):
        raise RuntimeError(f"{os.path.basename(path)}: '{name}' not found")
    text = pat.sub(lambda m: f"{m.group(1)}{name} = {value}    # 104: {note}",
                   text, count=1)
    with open(path, "w") as fh:
        fh.write(text)

# stem, sample, hold, tau, observe, [(scalar, value, note)], why-lines
PLAN = [
    dict(
        stem="104_01_sw4_shutin_nogouge", sample="SWS4",
        hold=0.0, tau=SHUTIN_TAU_FAST, observe=SHUTIN_OBSERVE,
        mirrors="101_12_sw4_shutin_nohold",
        extra=(("use_slip_damage", "false",
                "104_01: was true; the ONLY change from 101_12"),),
        why=[
            "  # ARM 1 -- kill the gouge-fill subtraction on SW-S4.",
            "  # 101 found SW-S4 the only specimen to end LESS permeable than the loading",
            "  # path at matched sigma'_n (k x0.859 against x1.459-1.609 for the others).",
            "  # slip_damage_fill reaches 0.253 um here, which is 34% of this deck's",
            "  # a_h0 = 0.74 um -- the largest fractional subtraction of any of the four,",
            "  # and SW-T1/SW-T2 have this channel switched off entirely.",
            "  # PREDICTION: the k ratio crosses 1.0.",
            "  # FALSIFIER: if it stays below 1.0, gouge-fill is not the cause and the",
            "  # remaining suspect is the retention(R) discount on the dilation term,",
            "  # which is live here (use_kinematic_aperture = false) and dead on T1/T2.",
        ],
    ),
    dict(
        stem="104_02_sw4_shutin_dscale0p038", sample="SWS4",
        hold=0.0, tau=SHUTIN_TAU_FAST, observe=SHUTIN_OBSERVE,
        mirrors="101_12_sw4_shutin_nohold",
        extra=(("dilation_scale", 0.038,
                "104_02: was 0.0117 (SW-S3's value); the ONLY change from 101_12"),),
        why=[
            "  # ARM 1 -- raise SW-S4's dilation gain to SW-S3's.",
            "  # SW-S3 and SW-S4 are the two decks running the non-kinematic aperture",
            "  # path, so dilation_scale is directly comparable BETWEEN THEM (it is not",
            "  # comparable to SW-T1/T2, whose 0.0 means 'off because kinematic', not",
            "  # 'small').  SW-S3 gains k x1.497 at 0.038; SW-S4 loses at 0.0117.",
            "  # PREDICTION: the k ratio rises.  Whether it alone clears 1.0 separates",
            "  # 'the dilation arm is sufficient' from 'both arms are needed'.",
            "  # NOTE this deck deliberately breaks SW-S4's hydraulic calibration: a_h",
            "  # and therefore Q will not match Table 2.  That is the point of a probe.",
        ],
    ),
    dict(
        stem="104_03_sw3_shutin_nogouge", sample="SWS3",
        hold=0.0, tau=SHUTIN_TAU_FAST, observe=SHUTIN_OBSERVE,
        mirrors="101_11_sw3_shutin_nohold",
        extra=(("use_slip_damage", "false",
                "104_03: was true; the ONLY change from 101_11"),),
        why=[
            "  # ARM 1 -- the SIGN CONTROL for 104_01.",
            "  # Same knob, on the specimen that is already on the other side of the",
            "  # line (k x1.497).  Its gouge-fill reaches 0.307 um = 25% of a_h0.",
            "  # PREDICTION: the k ratio rises above 1.497.",
            "  # WHY THIS DECK EXISTS: without it, a successful 104_01 is uninterpretable.",
            "  # A knob that flips SW-S4 but does nothing to SW-S3 is not the channel the",
            "  # two specimens differ by, and the hypothesis would be wrong even though",
            "  # its headline prediction came true.",
        ],
    ),
    dict(
        stem="104_04_swt2_shutin_slowtau", sample="SWT2",
        hold=200.0, tau=SHUTIN_TAU_SLOW, observe=SHUTIN_OBSERVE_SLOW,
        mirrors="101_10_swt2_shutin_nohold",
        extra=(),
        why=[
            "  # ARM 2 -- complete the rate-independence test.",
            "  # 101 group D ran tau = 1500 s on SW-T1 and SW-S4 only and found the",
            "  # retained permeability essentially unmoved (x1.609 -> x1.584, and",
            "  # x0.859 -> x0.855).  Two specimens is not four, and the manuscript",
            "  # should not generalise from half the set.  No parameter changes: this is",
            "  # an ordinary group-D deck for a specimen group D skipped.",
            "  # PREDICTION: within ~2% of this specimen's tau = 150 s value, k x1.459.",
        ],
    ),
    dict(
        stem="104_05_sw3_shutin_slowtau", sample="SWS3",
        hold=200.0, tau=SHUTIN_TAU_SLOW, observe=SHUTIN_OBSERVE_SLOW,
        mirrors="101_11_sw3_shutin_nohold",
        extra=(),
        why=[
            "  # ARM 2 -- complete the rate-independence test.",
            "  # See 104_04.  No parameter changes.",
            "  # PREDICTION: within ~2% of this specimen's tau = 150 s value, k x1.497.",
        ],
    ),
]


def banner_104(entry, t_shut, end_time):
    s = entry["sample"]
    changed = (", ".join(f"{n} = {v}" for n, v, _ in entry["extra"])
               if entry["extra"] else "NONE (schedule only)")
    return ([
        "  # ========================================================================",
        "  # 104-SERIES FOLLOW-UP DECK -- opened by the 101 analysis",
        f"  # {entry['stem']}   parent: {SPECS[s][0]}",
        f"  # mirrors: {entry['mirrors']}   (same schedule shape; see below)",
        f"  # parameter change from that mirror: {changed}",
        "  #",
        "  # This REPLACES the digitized Ye & Ghassemi schedule by design, so it is",
        "  # NOT scoreable against Table 2 and scripts/table2_gate.py must not be run",
        "  # on it.  The validated run for this specimen is its 93-series parent.",
        "  # ------------------------------------------------------------------------",
    ] + entry["why"] + [
        "  #",
        f"  # Shut-in instant t = {t_shut:.1f} s;  observation to t = {end_time:.1f} s.",
        "  # PRIMARY OBSERVABLE: end_to_matched_permeability_ratio from",
        "  # scripts/analyze_104.py -- the end state against the LOADING path at the",
        "  # same effective normal stress, so reversible closure is differenced out.",
        "  # ========================================================================",
    ])


def main():
    print(f"{'deck':34s}{'sample':8s}{'tau':>7s}{'t_shut':>10s}{'end':>10s}"
          f"{'walltime':>10s}{'steps':>8s}{'est_h':>7s}  change")
    for entry in PLAN:
        s = entry["sample"]
        _, p_amb, p_peak, t_peak = SPECS[s]
        expr, t_shut, end_time = shutin_expression(
            p_amb, p_peak, t_peak - 2.0, T_SETTLE[s],
            entry["hold"], entry["tau"], entry["observe"])

        body = [
            "  [injection_pressure]",
            "    type = ParsedFunction",
            f"    expression = '{expr}'",
            "  []",
        ]
        path, dtmax = build(s, entry["stem"], banner_104(entry, t_shut, end_time),
                            body, end_time)
        for name, value, note in entry["extra"]:
            set_scalar_104(path, name, value, note)
        walltime, steps, est_h = write_slurm(
            s, entry["stem"], end_time, dtmax, "104-series follow-up")
        changed = (";".join(f"{n}={v}" for n, v, _ in entry["extra"])
                   if entry["extra"] else "-")
        print(f"{entry['stem']:34s}{s:8s}{entry['tau']:7.0f}{t_shut:10.1f}"
              f"{end_time:10.1f}{walltime:>10s}{steps:8d}{est_h:7.1f}  {changed}")


if __name__ == "__main__":
    raise SystemExit(main())
