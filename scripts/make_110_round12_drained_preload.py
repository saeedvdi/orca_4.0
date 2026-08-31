#!/usr/bin/env python3
"""
Build the Kalantar 2025 ROUND-12 OG-T drained-preload arm.

WHY THIS ROUND EXISTS
---------------------
Round 11 refuted the last mechanical hypothesis for OG-T and its own null found the
cause instead.  Over the 2 -> 55 s preload ramp the interface pore pressure rises
2.19 -> 51.08 MPa, and with fault_pressure_coefficient = 1.0 that removes 46.7 of the
joint's 64.5 MPa of effective normal stress.  Add alpha_f * p back and the total-stress
slope d(sigma_n)/d(sigma_d) is +0.277 on OG-T and +0.277 on OG-SH: load reaches the joint
correctly and always did.  Measured Skempton B = 0.914 against 0.930 predicted from the
deck's own constants -- the model is doing CORRECT UNDRAINED POROELASTICITY ON THE WRONG
PROTOCOL.

Why OG-T alone.  a_h at preload is 0.10 um (OG-T), 1.42 (OG-SC), 4.92 (OG-SH), so a_h^3
differs by 119 000x.  OG-SH's fracture connects both ports with thousands of times the
matrix conductance and bleeds the overpressure away as fast as the ramp makes it
(dp/dsigma_d = 0.017).  OG-T's carries Q = 0.000 mL/min and cannot (0.372-0.416 on every
OG-T deck across five rounds, under both loading modes).  The 0.10 um aperture is FAITHFUL
to Kalantar's Table 2 -- the defect is the protocol, not the aperture.

Ruled out by data and not to be re-proposed: poroelastic constants (byte-identical across
the three decks), ramp duration (identical), drainage ports (a single node in all three),
axial BC type (displacement 0.376 vs traction 0.379 on the same specimen).
Full argument: Examples/Kalantar2025/Doc/Memory/KALANTAR2025_ROUND11_BACKANALYSIS.md.

THE FIX
-------
Give the specimen time to drain before the test starts, which is what the experiment does.
Consolidation coefficient c = kM/mu = 1.4e-20 * 1.083e11 / 1e-3 = 1.5e-6 m^2/s, and the far
corners of the core sit ~40 mm from the nearest port, so tau_c ~ L^2/c ~ 1.0e3 s.  The
parent's 53 s ramp is 5 % of ONE time constant.

    ramp    2 -> 10 000 s   (10 tau_c, quasi-drained loading)
    hold   10 000 -> 14 000 s   (4 tau_c at constant sigma_d, pure equilibration)
    then the parent's own 6800 s injection schedule, shifted by +13 945 s

The hold is the part that does the work and it is why this is not merely "a slower ramp":
the experiment brings the specimen to its preload and lets the pore system settle before
stage 1.  The parent gives it 45 s.

Nothing else changes.  Same graded mesh, same joint law, same constitutive constants, same
injection schedule, same solver.  Inside the injection window the time-stepping segments are
the parent's, shifted -- so the calibrated window is stepped exactly as the parent stepped it
and the two runs differ only in what happened before it.

THE DECKS
---------
    110_36_og_t_drained_preload_r12   THE GATE.  Injection held flat at 3 MPa = the
                                      production pressure, so nothing drives flow and the
                                      run measures the preload alone.  ~560 steps.
    110_37_og_t_drained_full_r12      The full 17-stage cycle on the same preload.
                                      Interpretable ONLY if 110_36 passes.

PREREGISTERED GATE for 110_36, all five (current value in brackets):

    1. d(interface_pressure) over the ramp          <= 3 MPa        [48.9]
       -- OG-SH, which scores ratio 0.999, sits at 3.46 MPa on the same measure;
          OG-SC at 13.01 scores 0.930; every OG-T deck is at 23.7-36.6.
    2. bb_effective_normal_stress_pp divided by
       effective_normal_paper_frame_mpa_pp          >= 0.93         [0.277]
    3. pre-slip slope d(sigma'_n)/d(sigma_d)        +0.22 +- 0.04   [-0.100]
    4. tau/tau_limit at sigma_d = 160.43 MPa        < 1.0           [yields at 57.6]
    5. cumulative_plastic_slip at end of preload    < 10 um         [0.5-2.4 mm]

Score with:  python3 scripts/score_110_round11.py <csv>

FAIL MEANS.  If Delta p falls but the ratio does not follow, the diagnosis in the round-11
back-analysis is wrong and that document is the thing to correct -- not this deck.  If
Delta p does not fall at all, the drainage path is blocked by something other than the
fracture aperture and the ports are the next thing to look at.

WHAT IS DELIBERATELY NOT DONE HERE.  A steady-state preload solve would be cheaper and is
arguably the more faithful representation of the experiment.  It is not used, because it
would change the solver path at the same time as the protocol and a failure could not then
be attributed.  Reach for it only if the slow ramp proves too expensive.

Idempotent: rerun freely, it overwrites its own outputs and touches nothing else.
"""

import os
import re
import subprocess
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STUDY = os.path.join(ROOT, "Examples", "Kalantar2025")
PARENT = os.path.join(STUDY, "OGT", "110_29_og_t_graded_full_r10.i")

RAMP_START = 2.0
RAMP_END = 10000.0          # 10 consolidation times
PRELOAD_END = 14000.0       # + 4 more at constant sigma_d
PARENT_RAMP_END = 55.0
PARENT_END = 6800.0         # the parent's own injection schedule ends here
SHIFT = PRELOAD_END - PARENT_RAMP_END      # 13945.0
PRELOAD_DT = 25.0           # 40 steps per consolidation time
PROBE_INJECTION_PA = 3.0e6  # = production_pressure: no drive, preload only


def read(path):
    with open(path) as fh:
        return fh.read().split("\n")


def sub_one(lines, pattern, new, what):
    """Replace exactly one matching line, and prove it was exactly one."""
    hits = [n for n, l in enumerate(lines) if re.match(pattern, l)]
    assert len(hits) == 1, f"{what}: expected 1 match, found {len(hits)}"
    lines[hits[0]] = new
    return lines


def strip_banner(lines):
    i = next(n for n, l in enumerate(lines) if l.startswith("mesh_file"))
    j = max(n for n in range(i) if re.fullmatch(r"#{10,}", lines[n].strip()))
    return lines[j:]


def retarget_outputs(lines, stem):
    hits = 0
    for n, l in enumerate(lines):
        for key, kind in (("exodus_file_base", "exodus"),
                          ("csv_file_base", "csv"),
                          ("checkpoint_file_base", "checkpoint")):
            if l.startswith(key):
                lines[n] = (f"{key} = results_{kind}_hpc/{stem}_hpc"
                            f"   # ROUND 12: self-named output")
                hits += 1
    assert hits == 3, f"expected 3 *_file_base lines, retargeted {hits}"
    return lines


def slow_the_ramp(lines):
    """2 -> 55 s becomes 2 -> RAMP_END, then flat through the hold."""
    span = RAMP_END - RAMP_START
    new = (f"      expression = 'if(t<{RAMP_START},${{axial_pres_initial}},"
           f"if(t<{RAMP_END},${{axial_pres_initial}}+(${{axial_pres_final}}"
           f"-${{axial_pres_initial}})*(t-{RAMP_START})/{span},"
           f"${{axial_pres_final}}))'   # ROUND 12: 53 s -> {span:.0f} s, "
           f"then held to {PRELOAD_END:.0f} s")
    return sub_one(lines, r"^      expression = 'if\(t<2\.0,", new, "axial ramp")


def shift_injection(lines):
    """Move the whole injection schedule behind the drained preload."""
    hits = [n for n, l in enumerate(lines) if l.startswith("    x = '0.0 100.0 400.0")]
    assert len(hits) == 1, f"injection x: expected 1 match, found {len(hits)}"
    n = hits[0]
    xs = [float(v) for v in lines[n].split("'")[1].split()]
    shifted = [0.0] + [x + SHIFT for x in xs]
    ys = lines[n + 1].split("'")[1].split()
    assert len(ys) == len(xs), "injection x and y differ in length"
    lines[n] = ("    x = '" + " ".join(f"{v:.1f}" for v in shifted) + "'"
                f"   # ROUND 12: schedule shifted +{SHIFT:.0f} s behind the drained preload")
    lines[n + 1] = ("    y = '" + ys[0] + " " + " ".join(ys) + "'"
                    "   # ROUND 12: leading point holds the initial 3 MPa through the preload")
    return lines


def flatten_injection(lines):
    """Probe only: hold injection at the production pressure so nothing drives flow."""
    hits = [n for n, l in enumerate(lines) if l.startswith("    x = '0.0 100.0 400.0")]
    assert len(hits) == 1
    n = hits[0]
    lines[n] = (f"    x = '0.0 {PRELOAD_END:.1f}'"
                "   # ROUND 12 PROBE: no injection schedule, the preload is the experiment")
    lines[n + 1] = (f"    y = '{PROBE_INJECTION_PA:.1f} {PROBE_INJECTION_PA:.1f}'"
                    "   # ROUND 12 PROBE: held at production_pressure, zero drive")
    return lines


def retime(lines, end_time, full_cycle):
    """Prefix a coarse preload segment; shift the parent's own segments behind it."""
    n = next(k for k, l in enumerate(lines) if l.startswith("      time_t = '"))
    assert lines[n + 1].startswith("      time_dt = '")
    if full_cycle:
        t = [float(v) for v in lines[n].split("'")[1].split()]
        d = [float(v) for v in lines[n + 1].split("'")[1].split()]
        assert len(t) == len(d), "time_t and time_dt differ in length"
        # Drop the parent's own preload segment (t < 99.5); the new one replaces it.
        keep = [(tt, dd) for tt, dd in zip(t, d) if tt >= 99.5]
        new_t = [0.0, 0.5, RAMP_START, RAMP_END, PRELOAD_END - 0.5] + \
                [tt + SHIFT for tt, _ in keep]
        new_d = [0.5, 0.5, PRELOAD_DT, PRELOAD_DT, 1.50] + [dd for _, dd in keep]
        # The parent's last segment point IS its end_time, so the shift carries it to
        # ours; nothing needs appending. Asserted below.
    else:
        new_t = [0.0, 0.5, RAMP_START, RAMP_END, PRELOAD_END]
        new_d = [0.5, 0.5, PRELOAD_DT, PRELOAD_DT, PRELOAD_DT]
    assert len(new_t) == len(new_d), \
        f"time_t has {len(new_t)} entries, time_dt has {len(new_d)}"
    assert all(b >= a for a, b in zip(new_t, new_t[1:])), "time_t is not monotonic"
    assert abs(new_t[-1] - end_time) < 1e-6, \
        f"last time_t {new_t[-1]} does not land on end_time {end_time}"
    lines[n] = ("      time_t = '" + " ".join(f"{v:.1f}" for v in new_t) + "'"
                "   # ROUND 12: coarse drained preload, then the parent's own segments")
    lines[n + 1] = ("      time_dt = '" + " ".join(f"{v:.2f}" for v in new_d) + "'"
                    "   # ROUND 12: see time_t above")
    # event_dt_cap: keep the parent's 0.5 s inside the injection window, coarse before it.
    c = next(k for k, l in enumerate(lines) if l == "    x = '0 60'")
    assert lines[c + 1] == "    y = '0.5 0.5'"
    if full_cycle:
        lines[c] = (f"    x = '0 {RAMP_START} {PRELOAD_END}'"
                    "   # ROUND 12: coarse through the preload, parent's cap after it")
        lines[c + 1] = f"    y = '{PRELOAD_DT} {PRELOAD_DT} 0.5'   # ROUND 12: see x above"
    else:
        lines[c] = (f"    x = '0 {RAMP_START}'"
                    "   # ROUND 12 PROBE: coarse throughout, no event to resolve")
        lines[c + 1] = f"    y = '{PRELOAD_DT} {PRELOAD_DT}'   # ROUND 12 PROBE: see x above"
    lines = sub_one(lines, r"^  end_time = ",
                    f"  end_time = {end_time:.0f}   # ROUND 12: "
                    + ("preload + the parent's 6800 s cycle" if full_cycle
                       else "the drained preload alone"), "end_time")
    lines = sub_one(lines, r"^  dtmax = ",
                    f"  dtmax = {PRELOAD_DT if not full_cycle else 5.0}"
                    "   # ROUND 12: segment limits govern", "dtmax")
    return lines


def banner(stem, title, body):
    rule = "# " + "=" * 77
    out = [rule, f"# {stem}", "#", f"# {title}",
           f"# Parent: {os.path.basename(PARENT)} (verbatim except the changes below).", "#"]
    out += ["# " + l if l else "#" for l in body.strip("\n").split("\n")]
    out += ["#",
            "# Generated by scripts/make_110_round12_drained_preload.py -- edit the script,",
            "# not this file.", rule, ""]
    return out


def build(stem, title, body, full_cycle, end_time):
    lines = strip_banner(read(PARENT))
    lines = slow_the_ramp(lines)
    lines = shift_injection(lines) if full_cycle else flatten_injection(lines)
    lines = retime(lines, end_time, full_cycle)
    lines = retarget_outputs(lines, stem)
    path = os.path.join(STUDY, "OGT", stem + ".i")
    with open(path, "w") as fh:
        fh.write("\n".join(banner(stem, title, body) + lines))
    print(f"  wrote {os.path.relpath(path, ROOT)}  ({len(lines)} lines)")
    return path


GATE = """
PREREGISTERED GATE -- all five, current value of each in brackets:

  1. rise in interface_pressure_pp over the ramp        <= 3 MPa       [48.9]
     (3 MPa is not arbitrary: measured over the same pre-slip window OG-SH sits at
      3.46 MPa and delivers ratio 0.999, OG-SC at 13.01 and delivers 0.930, and every
      OG-T deck at 23.7-36.6 and delivers 0.38-0.52.)
  2. bb_effective_normal_stress_pp divided by
     effective_normal_paper_frame_mpa_pp                >= 0.93        [0.277]
  3. pre-slip slope d(sigma'_n)/d(sigma_d)              +0.22 +- 0.04  [-0.100]
  4. tau/tau_limit at sigma_d = 160.43 MPa              < 1.0          [yields at 57.6]
  5. cumulative_plastic_slip at the end of the preload  < 10 um        [0.5-2.4 mm]

Score with: python3 scripts/score_110_round11.py <csv>
"""

print("Round 12 -- OG-T drained preload")
paths = [
    build("110_36_og_t_drained_preload_r12",
          "ROUND 12 -- OG-T DRAINED PRELOAD.  THE GATE.",
          f"""
ONE MECHANISM CHANGES: the specimen is given time to drain before the test starts.

  ramp    {RAMP_START:.0f} -> {RAMP_END:.0f} s      (10 consolidation times; the parent ramps in 53 s)
  hold   {RAMP_END:.0f} -> {PRELOAD_END:.0f} s   (4 more at constant sigma_d, pure equilibration)

Injection is held flat at the production pressure ({PROBE_INJECTION_PA / 1e6:.0f} MPa), so nothing drives
flow and this run measures the preload and nothing else.  Mesh, joint law, constitutive
constants, confining pressure and solver are the parent's, untouched.

WHY.  Round 11's null found that OG-T's preload is UNDRAINED: interface pore pressure
rises 2.19 -> 51.08 MPa over 53 s, which removes 46.7 of the joint's 64.5 MPa of effective
normal stress and makes it yield at sigma_d = 57.6 MPa instead of holding to 160.43.
Measured Skempton B = 0.914 against 0.930 predicted from this deck's own constants.  The
model is right; the protocol is wrong.  OG-SH does not show it because its 4.87 um
fracture is 119 000x more transmissive in a_h^3 and drains the specimen as the ramp loads
it.  OG-T's 0.10 um fracture carries Q = 0.000 mL/min and cannot.
{GATE}
FAIL MEANS.  If Delta p falls but the ratio does not follow, the round-11 diagnosis is
wrong and KALANTAR2025_ROUND11_BACKANALYSIS.md is what needs correcting, not this deck.
If Delta p does not fall at all, the drainage path is blocked by something other than the
aperture and the single-node ports are the next suspect.
""", full_cycle=False, end_time=PRELOAD_END),
    build("110_37_og_t_drained_full_r12",
          "ROUND 12 -- OG-T FULL 17-STAGE CYCLE ON THE DRAINED PRELOAD.",
          f"""
The same preload as 110_36, followed by the parent's own 6800 s injection schedule shifted
by +{SHIFT:.0f} s so it begins 45 s after the preload ends -- exactly the gap the parent leaves.
Inside the injection window the time-stepping segments are the parent's, shifted, so the
calibrated window is stepped as the parent stepped it and the two runs differ only in what
happened before it.

DO NOT INTERPRET THIS RUN UNTIL 110_36 HAS PASSED ITS GATE.  Every OG-T validation datum
in this campaign was taken from a specimen that had already yielded during its own preload.
If 110_36 fails, this run is another one of those and should be discarded, not analysed.

It is submitted alongside 110_36 rather than after it only to save an HPC round trip; that
is a scheduling decision, not a statement that the gate is expected to pass.

WHAT IT DELIVERS IF THE GATE PASSES.  OG-T is the richest of Kalantar's three specimens:
17 hold stages with a_h printed to 0.01 um on every one, rising 0.10 -> 1.11 um and
returning to 0.00, and tau falling 66.5 -> 20.4 MPa.  The return to zero is the direct
experimental test of the manuscript's limitation that retained aperture is unbounded
because the only saturating term in the budget is the negative one.

Note what it CANNOT deliver, which is a property of the experiment and not of the model:
OG-T's pre-slip branch spans sigma'_n 51.47-59.33 MPa and its post-slip branch 27.50-37.96,
so the two are DISJOINT and no matched-stress propping comparison exists for this specimen.
Use OG-SC for that.  See Doc/Memory/KALANTAR2025_PAPER_VALIDATION_PLAN.md section 4.
""", full_cycle=True, end_time=PARENT_END + SHIFT),
]
print(f"\nShift applied to the injection schedule: +{SHIFT:.0f} s")
