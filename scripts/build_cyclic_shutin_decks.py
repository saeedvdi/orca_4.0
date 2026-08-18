#!/usr/bin/env python3
"""
build_cyclic_shutin_decks.py -- generate the 97 (cyclic) and 98 (shut-in) discussion decks.

WHAT THESE DECKS ARE FOR
========================
They are the paper's discussion-section runs, and they are NOT scoreable against
Table 2.  Table 2 is stage-wise data recorded under Ye & Ghassemi's own monotonic
injection history; these decks deliberately replace that history.  The 93-series
remains the validation set.

  97 (cyclic)   Three equal-peak load/unload cycles.  Question: how much
                permeability enhancement is retained after the FIRST cycle, and
                does it keep accumulating on cycles 2 and 3 or saturate?
  98 (shut-in)  Ramp to peak, hold, then an abrupt shut-in with the injection
                node relaxing exponentially toward ambient.  Question: does slip
                keep growing after the injection pressure has returned to near
                ambient (delayed reactivation) or arrest promptly?

WHAT CHANGES FROM THE 93-SERIES PARENT
======================================
Exactly three things: the [injection_pressure] function, end_time, and the three
output file bases.  Every constitutive parameter, the mesh, the source nodesets,
the boundary conditions, the paper-frame constants, the flow constants and the
solver are byte-identical to the validated parent.  This is the same minimal-diff
recipe the 68-series prototypes used (68_02_..._cyclic / _shutin), which is why
those two decks are the design reference here -- but they sit on the 68 deck
generation, which predates the theta30 mesh, the ppfix reporting frame and JRC=5,
so they could not be reused directly.

WHY EQUAL-PEAK CYCLES AND NOT AN INCREASING STAIRCASE
=====================================================
The 68-series prototype ramped to 15/20/24/28 MPa on successive cycles.  That
confounds two effects: enhancement from cycling, and enhancement from simply
reaching a higher pressure than before.  Holding the peak fixed isolates the
first, which is the question being asked.

WHY THE HOLDS MATTER
====================
The permeability probe must be taken at the SAME pressure in every cycle or the
comparison is confounded by the elastic part of the closure law.  Each cycle
therefore holds at the peak and again at the floor, and the enhancement is read
at those holds.  The holds are also where the slip velocity relaxes to zero, so
the reading is insensitive to the Perzyna tangential_viscosity overstress
(eta*V), which is a first-order term on the ramps -- see the memory note
"tangential-viscosity-is-the-hidden-rate-law".

WHY THE CALIBRATED RAMP RATE IS PRESERVED
=========================================
Each specimen ramps at its own R = (P_peak - P_ambient)/t_peak, taken from its
digitized schedule, rather than at a common convenient rate.  The model has a
genuine rate dependence, so a cyclic run at a different loading rate than the
validation run would not be comparable to it.  The cost is wall time and it is
affordable: 93_05 (SW-S3, mesh 5) finished 4802 s of simulated time in 8877 s of
wall time on 32 ranks, i.e. ~1.85 s wall per simulated second.

CAVEAT TO CARRY INTO THE WRITE-UP
=================================
SW-S4's parent carries fitted, time-anchored loading-frame terms -- axial piston
relaxation from relax_t0 = 1000 s and a confinement bleed from side_unload_t0 =
1900 s over 1400 s.  Both are min(...,1)-bounded, so they saturate and then hold
for the remainder of an extended run; nothing runs away.  But they were fitted to
the paper's schedule, and on a ~10 ks cyclic history they hold at their saturated
values for most of the run.  That is a property of the deck, not of the cyclic
schedule, and it should be stated rather than silently inherited.
"""

import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EX = os.path.join(ROOT, "Examples", "YeGhasemmi2018")

MPA = 1.0e6

# Ambient, peak and time-to-peak are MEASURED from each parent's own digitized
# [injection_pressure] schedule, not chosen.  P_floor = 8 MPa is likewise the
# level all four schedules bleed back to after the peak (measured end values:
# 8.00 / 8.00 / 7.88 / 7.97 MPa), so it is the paper's own intermediate floor.
P_FLOOR = 8.0
T_HOLD = 200.0          # s at each probe point
N_CYCLES = 3
SHUTIN_HOLD = 200.0     # s at peak before shut-in
SHUTIN_TAU = 150.0      # s exponential fall-off time constant
SHUTIN_OBSERVE = 3000.0  # s of post-shut-in observation

SPECS = [
    # sample, parent stem,                                    P_amb, P_peak, t_peak
    ("SWT1", "93_01_swt1_final_c26p9_resc9p19_ppfix",          5.00, 28.00, 1640.0),
    ("SWT2", "93_03_swt2_final_theta30_resc9p71_ppfix",        5.00, 28.00, 2280.0),
    ("SWS3", "93_05_sw3_final_resc1p40_ppfix",                 5.75, 28.57, 2569.2),
    ("SWS4", "93_07_sw4_final_theta30_jrc5_ppfix",             5.00, 27.96, 1720.7),
]

CYCLIC_STEMS = {
    "SWT1": "97_01_swt1_cyclic3",
    "SWT2": "97_02_swt2_cyclic3",
    "SWS3": "97_03_sw3_cyclic3",
    "SWS4": "97_04_sw4_cyclic3",
}
SHUTIN_STEMS = {
    "SWT1": "98_01_swt1_shutin",
    "SWT2": "98_02_swt2_shutin",
    "SWS3": "98_03_sw3_shutin",
    "SWS4": "98_04_sw4_shutin",
}


def cyclic_schedule(p_amb, p_peak, t_peak):
    """Three equal-peak cycles at the parent's own ramp rate R.

    Returns (xs, ys, end_time, probe_times).  probe_times are the mid-hold
    instants at which the permeability comparison should be read.
    """
    rate = (p_peak - p_amb) / (t_peak - 2.0)   # MPa/s, the parent's own rate
    t_up_first = (p_peak - p_amb) / rate       # == t_peak - 2
    t_up = (p_peak - P_FLOOR) / rate           # cycles 2..N start from the floor
    t_final = (P_FLOOR - p_amb) / rate

    xs, ys, probes = [0.0, 2.0], [p_amb, p_amb], []
    t = 2.0
    for k in range(N_CYCLES):
        t += t_up_first if k == 0 else t_up
        xs.append(t); ys.append(p_peak)
        probes.append(("peak", k + 1, t + T_HOLD / 2.0))
        t += T_HOLD
        xs.append(t); ys.append(p_peak)
        t += t_up                              # down-leg, same rate
        xs.append(t); ys.append(P_FLOOR)
        probes.append(("floor", k + 1, t + T_HOLD / 2.0))
        t += T_HOLD
        xs.append(t); ys.append(P_FLOOR)
    t += t_final
    xs.append(t); ys.append(p_amb)
    t += T_HOLD
    xs.append(t); ys.append(p_amb)
    return xs, ys, t, probes, rate


def shutin_expression(p_amb, p_peak, t_peak):
    t_hold_end = t_peak + SHUTIN_HOLD
    a, pk = p_amb * MPA, p_peak * MPA
    return (
        f"if(t<2.0, {a:.6g}, "
        f"if(t<{t_peak:.6g}, {a:.6g}+({pk:.6g}-{a:.6g})*(t-2.0)/{t_peak - 2.0:.6g}, "
        f"if(t<{t_hold_end:.6g}, {pk:.6g}, "
        f"{a:.6g}+({pk:.6g}-{a:.6g})*exp(-(t-{t_hold_end:.6g})/{SHUTIN_TAU:.6g}))))"
    ), t_hold_end + SHUTIN_OBSERVE


def replace_injection_block(text, new_body):
    """Swap the [injection_pressure] block body, keeping indentation."""
    lines = text.split("\n")
    start = next(i for i, l in enumerate(lines) if "[injection_pressure]" in l
                 and not l.lstrip().startswith("#"))
    end = next(i for i in range(start + 1, len(lines)) if lines[i].rstrip() == "  []")
    return "\n".join(lines[:start] + new_body + lines[end + 1:])


def set_end_time(text, end_time):
    out, done = [], False
    for line in text.split("\n"):
        if not done and re.match(r"^\s*end_time\s*=", line):
            line = f"  end_time = {end_time:.1f}"
            done = True
        out.append(line)
    if not done:
        raise RuntimeError("end_time not found")
    return "\n".join(out)


def build(kind, sample, parent_stem, new_stem, p_amb, p_peak, t_peak):
    parent = os.path.join(EX, sample, parent_stem + ".i")
    with open(parent) as fh:
        text = fh.read()

    if kind == "cyclic":
        xs, ys, end_time, probes, rate = cyclic_schedule(p_amb, p_peak, t_peak)
        probe_lines = "\n".join(
            f"  #     cycle {c} {w:<5s} hold  t = {tt:9.1f} s"
            for w, c, tt in probes)
        body = [
            "  # ------------------------------------------------------------------------",
            f"  # DISCUSSION DECK ({kind}).  {N_CYCLES} EQUAL-PEAK load/unload cycles.",
            "  # This REPLACES the digitized Ye & Ghassemi schedule; do not score against",
            "  # Table 2.  The validated run is the 93-series parent.",
            "  #",
            f"  # Ramp rate R = {rate * 1000:.4f} kPa/s, taken from this specimen's own",
            f"  # schedule ({p_amb:.2f} -> {p_peak:.2f} MPa in {t_peak:.1f} s), so the cyclic run",
            "  # loads at the same rate as the run it is compared against.",
            f"  # Peak {p_peak:.2f} MPa held {T_HOLD:.0f} s; floor {P_FLOOR:.2f} MPa held {T_HOLD:.0f} s.",
            "  #",
            "  # PERMEABILITY IS READ AT THE HOLDS, where the pressure is identical from",
            "  # cycle to cycle and the slip velocity has relaxed (so the eta*V overstress",
            "  # is not in the reading).  Probe instants:",
            probe_lines,
            "  # ------------------------------------------------------------------------",
            "  [injection_pressure]",
            "    type = PiecewiseLinear",
            "    x = '" + " ".join(f"{v:.4f}" for v in xs) + "'",
            "    y = '" + " ".join(f"{v * MPA:.6g}" for v in ys) + "'",
            "  []",
        ]
    else:
        expr, end_time = shutin_expression(p_amb, p_peak, t_peak)
        body = [
            "  # ------------------------------------------------------------------------",
            f"  # DISCUSSION DECK ({kind}).  Post-shut-in fault reactivation.",
            "  # This REPLACES the digitized Ye & Ghassemi schedule; do not score against",
            "  # Table 2.  The validated run is the 93-series parent.",
            "  #",
            f"  # Ramp {p_amb:.2f} -> {p_peak:.2f} MPa over t = 2 .. {t_peak:.1f} s at this",
            f"  # specimen's own rate, hold {SHUTIN_HOLD:.0f} s (past onset), then an ABRUPT",
            f"  # shut-in: the injection node relaxes exponentially toward ambient with",
            f"  # tau = {SHUTIN_TAU:.0f} s, a standard proxy for wellbore pressure fall-off.",
            f"  # end_time gives {SHUTIN_OBSERVE:.0f} s of post-shut-in observation.",
            "  #",
            "  # The question: once the injection-point pressure is back near ambient, does",
            "  # slip keep growing on pressure already diffused into the fault, or arrest?",
            "  # ------------------------------------------------------------------------",
            "  [injection_pressure]",
            "    type = ParsedFunction",
            f"    expression = '{expr}'",
            "  []",
        ]

    text = replace_injection_block(text, body)
    text = set_end_time(text, end_time)
    text = text.replace(parent_stem, new_stem)

    out = os.path.join(EX, sample, new_stem + ".i")
    with open(out, "w") as fh:
        fh.write(text)
    return out, end_time


def main():
    print(f"{'deck':28s} {'sample':7s} {'end_time':>10s}  {'est wall (h)':>12s}")
    made = []
    for sample, parent, p_amb, p_peak, t_peak in SPECS:
        for kind, stems in (("cyclic", CYCLIC_STEMS), ("shutin", SHUTIN_STEMS)):
            out, et = build(kind, sample, parent, stems[sample], p_amb, p_peak, t_peak)
            made.append((sample, stems[sample], et))
            print(f"{stems[sample]:28s} {sample:7s} {et:10.1f}  {et * 1.85 / 3600:12.1f}")
    return made


if __name__ == "__main__":
    main()
