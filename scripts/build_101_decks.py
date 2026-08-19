#!/usr/bin/env python3
"""
build_101_decks.py -- generate the 101-series discussion decks (the corrected and
extended re-run of the 97/98 pair).

WHY THERE IS A 101 SERIES AT ALL
================================
The 97 (cyclic) and 98 (shut-in) batch answered its questions, but three things
in it are not publication-grade, and one further question the results themselves
raised was never asked.  The 101 series fixes all four.

  (1) THREE OF THE FOUR CYCLIC RUNS WERE KILLED BY THEIR WALL-CLOCK ALLOCATION.
      Not a physics problem -- a resourcing bug.  submit_discussion_97_98.sh and
      DISCUSSION_DECKS_97_98.md both advertise "8 jobs, 32 ranks / 32 G / 24 h",
      and the four 98 scripts do request that.  The four 97 scripts request
      16 ranks / 12 h, because scripts/make_hpc_nochk_jobs.py rewrites
      "#SBATCH --time=" but inherits "--ntasks" and the "srun -n" from its
      template.  SW-S3 reached 1 cycle of 3 and contributed nothing.
      The wall-time estimate in that submit script was also wrong by ~2.5x: it
      assumed 1.85 s wall per simulated second, measured on SW-S3's 4802 s
      validation run, but three of the four decks carry dtmax = 0.75 s, so a
      15.8 ks cyclic run is ~21 000 steps, not ~8500.  Here the wall time is set
      from the STEP COUNT (end_time / dtmax), not from the simulated duration.

  (2) SW-S4'S CYCLES DID NOT SEE THE SAME LOADING FRAME AS EACH OTHER.
      SW-S4's parent carries two fitted, absolute-time loading-frame terms: an
      axial piston relaxation (relax_t0 = 1000 s, relax_dur = 800 s) and a
      confinement bleed (side_unload_t0 = 1900 s, side_unload_dur = 1400 s).
      Both are min(...,1)-bounded, so they saturate and hold.  In 97_04 the
      confinement bleed saturated at t = 3300 s, i.e. AFTER cycle 1's peak hold
      (1821 s) and BEFORE cycle 2's (5209 s).  Cycle 1 therefore ran at a
      different effective normal stress from cycles 2 and 3, which is exactly
      the variable the experiment is trying to hold fixed.  The measured cost
      was large: +7.4 of the +13.1 % apparent cycle-2 permeability gain was the
      bleed, not the cycling.
      FIX: retime both frame terms (and the poroelastic piston compensation) so
      they complete during a quiescent settling window BEFORE injection starts,
      and start the injection ramp at t = 800 s.  Magnitudes are untouched, only
      the anchors; the saturated end state is identical.  All three cycles then
      see one frozen frame.  This is applied to every SW-S4 deck in the series,
      including the shut-in ones, where the bleed used to run straight through
      the post-shut-in observation window.
      FALSIFIER: if slip onset occurs during the settling window (before t =
      800 s, at ambient pore pressure), the confinement bleed alone reactivates
      the fault.  That would be a result in its own right, but it would also
      mean the settling window has to shrink -- check reported_czm_shear_slip
      at t = 800 s before reading anything else.

  (3) THE ARREST TEST WAS RUN ON AN ALREADY-DECELERATING FAULT.
      98 ramps to peak, holds 200 s, then shuts in.  The completed runs show the
      peak slip RATE occurring 262-491 s BEFORE the shut-in instant -- during
      the ramp.  So "slip arrests after shut-in" was demonstrated starting from
      a state that was already slowing down.  The 101 series adds the control
      that isolates the hold: shut in at the instant peak pressure is reached
      (hold = 0), same peak, same ramp rate, everything else identical.  It also
      adds a slow bleed-off arm (tau = 1500 s instead of 150 s) on the two most
      slip-prone specimens, because a fast shut-in makes arrest easy and the
      field-relevant case is a slow one.

  (4) THE QUESTIONS THE 97 RESULT RAISED WERE NEVER ASKED.
      97 landed on outcome 1 (repeating an excursion to the same peak reproduces
      the first excursion), but NOT for the pre-registered reason.  The joint
      does not end each cycle below residual strength and re-pressurise
      elastically; it sits exactly ON the yield surface (tau - tau_lim = 0.0000
      to five figures at every peak hold on SW-T1 and SW-T2) in neutral plastic
      equilibrium, and what stops slip from accumulating is the series
      compliance of the loading column, which sheds stress the instant slip
      resumes.  That makes the null result a statement about the LOADING SYSTEM,
      not about the aperture law -- and therefore not obviously transferable to
      the field.  Two new groups test it:
        B  escalating-peak cycles.  Equal-peak cycling breaks no new ground by
           construction, so it cannot see outcome 2 or 3.  Three cycles at
           P_peak-4, P_peak-2, P_peak MPa do, in equal 2 MPa increments, so the
           question "does the increment shrink?" is read straight off the table.
        E  a loading-frame stiffness bracket on SW-T1 (2x stiffer, 2x softer).
           If saturation is set by the frame, the retained enhancement per cycle
           must move with the frame stiffness.  If it is set by the aperture
           law, it must not.  This is the direct test of the claim, and the
           answer is what decides whether the null result generalises.

WHAT IS AND IS NOT CHANGED FROM THE 93-SERIES PARENT
====================================================
Changed: the [injection_pressure] function, end_time, the three output file
bases, the Exodus write interval (10 -> 50 steps; nothing reads Exodus for these
runs and a 21 000-step job would otherwise write 2100 full-mesh frames), and two
added OUTPUT-ONLY postprocessors.  SW-S4 additionally has its five frame-term
time anchors retimed as described above; group E additionally scales the axial
BC penalty and rescales the commanded piston displacements by the inverse of the
same factor so the commanded STRESS is unchanged.

Not changed anywhere: the mesh, the source nodesets, every constitutive
parameter, the paper-frame constants, the flow constants, the solver and its
tolerances, and dtmax.  In particular dtmax is left alone deliberately.  It is
the obvious wall-time lever (a pressure-gated dt cap would cut these runs by
more than half, since ~60 % of a cyclic run sits below any pressure at which
anything happens) but it changes how the slip-weakening integral is integrated,
and an unverified speedup is not worth it when 48 h of wall clock is free.  If a
101 run still times out, that is the lever to reach for -- not before.

THE TWO ADDED POSTPROCESSORS
============================
  strength_margin_mpa_pp   (limit_tau - |tau|) in MPa, BOTH taken in the
        interface frame.  This is the quantity the 97/98 analysis had to
        reconstruct by hand, and it was got wrong the first time by differencing
        the paper-frame shear stress against the interface-frame limit -- two
        different frames, so the "overstress" it showed was an artefact.  It is
        also the sharpest single number in the cyclic result, so it should not
        be a derived quantity computed in a notebook.
  slip_rate_mm_per_s_pp    d(slip)/dt from ChangeOverTimePostprocessor with
        divide_by_dt.  The shut-in test's primary observable.  Finite-differ-
        encing the CSV works but is noisy across the adaptive time steps, and
        "where is the slip-rate maximum" is precisely the question.

Neither can affect the solve: both are postprocessors of already-computed
quantities and nothing consumes them.

DECK INVENTORY (16 decks, all mesh 5, all on the 93-series finals)
==================================================================
  A  101_01..04  equal-peak 3-cycle          the 97 experiment, resourced to finish
  B  101_05..08  escalating-peak 3-cycle     outcome 2/3, which A cannot see
  C  101_09..12  shut-in, no pre-shut-in hold  isolates the hold
  D  101_13,14   shut-in, tau = 1500 s       isolates the bleed-off rate
  E  101_15,16   SW-T1 2-cycle, frame 2x / 0.5x   tests the saturating mechanism

Run tier A first; it is the one that must exist.  B and E are what turn a null
result into an argument.  C and D are cheap.
"""

import os
import re
import stat

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
EX = os.path.join(ROOT, "Examples", "YeGhasemmi2018")
HPC_ROOT = "/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0"

MPA = 1.0e6

P_FLOOR = 8.0            # MPa; the level all four digitized schedules bleed back to
T_HOLD = 200.0           # s at each probe point
SHUTIN_TAU_FAST = 150.0  # s, the 98-series value
SHUTIN_TAU_SLOW = 1500.0  # s, the field-relevant slow bleed-off
SHUTIN_OBSERVE = 3000.0
SHUTIN_OBSERVE_SLOW = 6000.0   # tau = 1500 s needs >= 4 tau to get back to ambient

# Wall-clock model.  Measured on 97_03 (SW-S3, 16 ranks): 8200 steps in 43 200 s
# = 5.3 s/step.  Assume 1.6x from 16 -> 32 ranks (the solve is LU/MUMPS-bound and
# does not scale linearly), i.e. 3.3 s/step, and take 24 h unless that exceeds
# 14 h, in which case 48 h.
SEC_PER_STEP_32 = 3.3

SPECS = {
    # sample: parent stem, ambient, peak, time-to-peak (all MEASURED from the
    # parent's own digitized [injection_pressure] schedule, not chosen)
    "SWT1": ("93_01_swt1_final_c26p9_resc9p19_ppfix", 5.00, 28.00, 1640.0),
    "SWT2": ("93_03_swt2_final_theta30_resc9p71_ppfix", 5.00, 28.00, 2280.0),
    "SWS3": ("93_05_sw3_final_resc1p40_ppfix", 5.75, 28.57, 2569.2),
    "SWS4": ("93_07_sw4_final_theta30_jrc5_ppfix", 5.00, 27.96, 1720.7),
}

# SW-S4 alone carries absolute-time loading-frame terms.  Retime them to complete
# inside a quiescent settling window; magnitudes untouched, saturated end state
# identical.  Injection then starts at T_SETTLE.
FRAME_RETIME = {
    "poro_dur": 300.0,        # was 945.0 -> piston poroelastic compensation done by t = 355
    "relax_t0": 100.0,        # was 1000.0
    "relax_dur": 400.0,       # was  800.0 -> axial relaxation done by t = 500
    "side_unload_t0": 100.0,  # was 1900.0
    "side_unload_dur": 600.0,  # was 1400.0 -> confinement bleed done by t = 700
}
T_SETTLE = {"SWT1": 2.0, "SWT2": 2.0, "SWS3": 2.0, "SWS4": 800.0}

NEW_PPS = """
  # --- 101-SERIES ADDITIONS (output only; nothing consumes these) -------------
  # Both were reconstructed by hand from the CSV for the 97/98 analysis, and the
  # strength margin was got WRONG that way the first time: it differenced the
  # paper-frame shear stress against the interface-frame limit, two different
  # frames, and reported a spurious overstress.  Computed here it is unambiguous
  # -- limit_tau_pp and shear_traction_magnitude_pa are the same pair the
  # constitutive law itself compares, in the interface frame.
  [strength_margin_mpa_pp]
    type = ParsedPostprocessor
    pp_names = 'limit_tau_pp shear_traction_magnitude_pa'
    expression = '(limit_tau_pp - shear_traction_magnitude_pa) * 1e-6'
  []
  # Primary observable of the shut-in test.  Finite-differencing the CSV works
  # but is noisy across adaptive steps, and "where is the slip-rate maximum" is
  # exactly the question being asked.
  [slip_rate_mm_per_s_pp]
    type = ChangeOverTimePostprocessor
    postprocessor = reported_czm_shear_slip_mm_pp
    divide_by_dt = true
  []
"""

SLURM = """#!/bin/bash

#SBATCH --job-name={stem}_hpc
#SBATCH --chdir={hpc_root}/Examples/YeGhasemmi2018/{sample}
#SBATCH --account=def-biaoli66
#SBATCH --time={walltime}
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --output=logs/{stem}_hpc_%j.out
#SBATCH --error=logs/{stem}_hpc_%j.err

cd {hpc_root}/Examples/YeGhasemmi2018/{sample}

# Clear conflicting memory env vars (Alliance injects SLURM_MEM_PER_CPU; --mem sets SLURM_MEM_PER_NODE).
unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p results_csv_hpc_rorqual results_exodus_hpc_rorqual logs

# ---------------------------------------------------------------------------
# {note}
#
# RESOURCES ARE SIZED FROM THE STEP COUNT, NOT THE SIMULATED DURATION.  This
# deck runs {end_time:.0f} s at dtmax = {dtmax} s, i.e. >= {steps} steps.  At the
# measured 5.3 s/step on 16 ranks and an assumed 1.6x from 16 -> 32 ranks, that
# is ~{est_h:.1f} h, so --time={walltime}.  The 97-series jobs died because they
# inherited 16 ranks / 12 h from a template while their own documentation
# advertised 32 ranks / 24 h, and because the wall estimate was made from
# simulated seconds against a deck with a 2x coarser dtmax.
#
# Outputs/chk/enable=false -- the cluster caps file count and a 32-rank MOOSE
# Checkpoint writes a _cp/ tree of one .rd per rank.  No checkpoint means no
# restart, but CSV is written incrementally, so even a killed job leaves a
# readable partial record.
# ---------------------------------------------------------------------------

srun --mpi=pmi2 -n 32 {hpc_root}/orca-opt -i {stem}.i \\
    Outputs/chk/enable=false \\
    csv_file_base=results_csv_hpc_rorqual/{stem}_hpc \\
    exodus_file_base=results_exodus_hpc_rorqual/{stem}_hpc
"""


# ---------------------------------------------------------------------------
# text surgery on the parent deck
# ---------------------------------------------------------------------------

def replace_injection_block(text, new_body):
    lines = text.split("\n")
    start = next(i for i, l in enumerate(lines)
                 if "[injection_pressure]" in l and not l.lstrip().startswith("#"))
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


def get_dtmax(text):
    m = re.search(r"^\s*dtmax\s*=\s*([0-9.eE+-]+)", text, flags=re.M)
    if not m:
        raise RuntimeError("dtmax not found")
    return float(m.group(1))


def set_exodus_interval(text, interval):
    """Raise the Exodus write interval inside the [exodus] block only."""
    lines = text.split("\n")
    start = next(i for i, l in enumerate(lines) if l.rstrip() == "  [exodus]")
    end = next(i for i in range(start + 1, len(lines)) if lines[i].rstrip() == "  []")
    hit = False
    for i in range(start, end):
        if re.match(r"^\s*time_step_interval\s*=", lines[i]):
            lines[i] = (f"    time_step_interval = {interval}"
                        "   # 101: these runs are 10-21 ks of simulated time;"
                        " nothing reads Exodus for them")
            hit = True
    if not hit:
        raise RuntimeError("exodus time_step_interval not found")
    return "\n".join(lines)


def set_scalar(text, name, value, note):
    """Replace a top-level `name = value` assignment, preserving nothing else."""
    pat = re.compile(rf"^{re.escape(name)}\s*=\s*\S+.*$", flags=re.M)
    if not pat.search(text):
        raise RuntimeError(f"scalar '{name}' not found")
    return pat.sub(f"{name} = {value:.10g}    # 101: {note}", text, count=1)


def add_postprocessors(text):
    """Insert the two new postprocessors after [reported_czm_shear_slip_mm_pp]."""
    lines = text.split("\n")
    start = next(i for i, l in enumerate(lines)
                 if l.rstrip() == "  [reported_czm_shear_slip_mm_pp]")
    end = next(i for i in range(start + 1, len(lines)) if lines[i].rstrip() == "  []")
    for required in ("[limit_tau_pp]", "[shear_traction_magnitude_pa]"):
        if required not in text:
            raise RuntimeError(f"parent lacks {required}; strength margin cannot be formed")
    return "\n".join(lines[:end + 1] + NEW_PPS.split("\n") + lines[end + 1:])


# ---------------------------------------------------------------------------
# schedules
# ---------------------------------------------------------------------------

def cyclic_schedule(p_amb, peaks, rate, t_start):
    """Load/unload cycles at a fixed rate with holds at every peak and floor.

    Returns (xs, ys, end_time, probes).  Probes are mid-hold instants: the
    pressure is identical from cycle to cycle there and the slip velocity has
    relaxed, so the reading carries no eta*V Perzyna overstress.
    """
    xs, ys, probes = [0.0, t_start], [p_amb, p_amb], []
    t, prev = t_start, p_amb
    for k, pk in enumerate(peaks):
        t += (pk - prev) / rate
        xs.append(t); ys.append(pk)
        probes.append(("peak", k + 1, t + T_HOLD / 2.0))
        t += T_HOLD
        xs.append(t); ys.append(pk)
        t += (pk - P_FLOOR) / rate
        xs.append(t); ys.append(P_FLOOR)
        probes.append(("floor", k + 1, t + T_HOLD / 2.0))
        t += T_HOLD
        xs.append(t); ys.append(P_FLOOR)
        prev = P_FLOOR
    t += (P_FLOOR - p_amb) / rate
    xs.append(t); ys.append(p_amb)
    probes.append(("final ambient", 0, t + T_HOLD / 2.0))
    t += T_HOLD
    xs.append(t); ys.append(p_amb)
    return xs, ys, t, probes


def shutin_expression(p_amb, p_peak, t_ramp, t_start, hold, tau, observe):
    t_shut = t_start + t_ramp + hold
    a, pk = p_amb * MPA, p_peak * MPA
    expr = (
        f"if(t<{t_start:.6g}, {a:.6g}, "
        f"if(t<{t_start + t_ramp:.6g}, {a:.6g}+({pk:.6g}-{a:.6g})*(t-{t_start:.6g})/{t_ramp:.6g}, "
        f"if(t<{t_shut:.6g}, {pk:.6g}, "
        f"{a:.6g}+({pk:.6g}-{a:.6g})*exp(-(t-{t_shut:.6g})/{tau:.6g}))))"
    )
    return expr, t_shut, t_shut + observe


# ---------------------------------------------------------------------------
# deck construction
# ---------------------------------------------------------------------------

def build(sample, stem, header, body, end_time, extra_scalars=()):
    parent = SPECS[sample][0]
    with open(os.path.join(EX, sample, parent + ".i")) as fh:
        text = fh.read()
    dtmax = get_dtmax(text)

    # Rename FIRST: the banner names the parent explicitly, and a later blanket
    # replace would rewrite that reference to point at the deck itself.
    text = text.replace(parent, stem)
    text = replace_injection_block(text, header + body)
    text = set_end_time(text, end_time)
    text = set_exodus_interval(text, 50)
    text = add_postprocessors(text)
    if sample == "SWS4":
        for name, value in FRAME_RETIME.items():
            text = set_scalar(text, name, value,
                              "frame term retimed to complete before injection starts")
    for name, value, note in extra_scalars:
        text = set_scalar(text, name, value, note)

    out = os.path.join(EX, sample, stem + ".i")
    with open(out, "w") as fh:
        fh.write(text)
    return out, dtmax


def banner(stem, sample, kind, lines):
    return ([
        "  # ========================================================================",
        f"  # 101-SERIES DISCUSSION DECK -- {kind}",
        f"  # {stem}   parent: {SPECS[sample][0]}",
        "  #",
        "  # This REPLACES the digitized Ye & Ghassemi schedule by design, so it is",
        "  # NOT scoreable against Table 2 and scripts/table2_gate.py must not be run",
        "  # on it.  The validated run for this specimen is its 93-series parent.",
        "  # ------------------------------------------------------------------------",
    ] + lines + [
        "  # ========================================================================",
    ])


def cyclic_deck(sample, stem, peaks, kind, why, extra_scalars=()):
    parent, p_amb, p_peak, t_peak = SPECS[sample]
    rate = (p_peak - p_amb) / (t_peak - 2.0)
    t_start = T_SETTLE[sample]
    xs, ys, end_time, probes = cyclic_schedule(p_amb, peaks, rate, t_start)

    lines = why + [
        "  #",
        f"  # Ramp rate R = {rate * 1000:.4f} kPa/s, this specimen's own rate, measured from",
        f"  # its digitized schedule ({p_amb:.2f} -> {p_peak:.2f} MPa in {t_peak:.1f} s).  The model",
        "  # has a genuine rate dependence (tangential_viscosity), so a cyclic run at a",
        "  # convenient rate would not be comparable to the run it is compared against.",
        "  #",
        "  # Peaks (MPa): " + ", ".join(f"{p:.2f}" for p in peaks)
        + f";  floor {P_FLOOR:.2f} MPa;  every peak and floor held {T_HOLD:.0f} s.",
    ]
    if t_start > 2.0:
        lines += [
            "  #",
            f"  # Injection starts at t = {t_start:.0f} s, not t = 2 s.  SW-S4's fitted",
            "  # loading-frame terms are retimed (see the scalars near the top of this",
            "  # deck) to complete by t = 700 s, so every cycle sees ONE frozen frame.",
            "  # In 97_04 they did not: the confinement bleed saturated at t = 3300 s,",
            "  # between cycle 1's peak hold and cycle 2's, and accounted for +7.4 of",
            "  # the +13.1 % apparent cycle-2 permeability gain.",
            "  # CHECK FIRST: slip at t = 800 s must still be ~0.  If it is not, the",
            "  # confinement bleed alone reactivated the fault at ambient pore pressure",
            "  # and the settling window is too long.",
        ]
    lines += [
        "  #",
        "  # READ THE COMPARISON AT THE HOLDS.  The pressure is identical from cycle to",
        "  # cycle there and the slip velocity has relaxed, so the reading is free of",
        "  # the Perzyna eta*V overstress that dominates on the ramps.  Probe instants:",
    ] + [f"  #     {('cycle %d %s' % (c, w)) if c else w:<21s} hold  t = {tt:9.1f} s"
         for w, c, tt in probes]

    body = [
        "  [injection_pressure]",
        "    type = PiecewiseLinear",
        "    x = '" + " ".join(f"{v:.4f}" for v in xs) + "'",
        "    y = '" + " ".join(f"{v * MPA:.6g}" for v in ys) + "'",
        "  []",
    ]
    return build(sample, stem, banner(stem, sample, kind, lines), body, end_time,
                 extra_scalars)


def shutin_deck(sample, stem, hold, tau, observe, kind, why):
    parent, p_amb, p_peak, t_peak = SPECS[sample]
    t_start = T_SETTLE[sample]
    t_ramp = t_peak - 2.0
    expr, t_shut, end_time = shutin_expression(
        p_amb, p_peak, t_ramp, t_start, hold, tau, observe)

    lines = why + [
        "  #",
        f"  # Ramp {p_amb:.2f} -> {p_peak:.2f} MPa over t = {t_start:.0f} .. {t_start + t_ramp:.1f} s at this",
        f"  # specimen's own rate, hold {hold:.0f} s, then shut in: the injection node relaxes",
        f"  # exponentially toward ambient with tau = {tau:.0f} s.",
        f"  # Shut-in instant t = {t_shut:.1f} s;  {observe:.0f} s of observation after it.",
    ]
    if t_start > 2.0:
        lines += [
            "  #",
            f"  # Injection starts at t = {t_start:.0f} s because SW-S4's fitted frame terms are",
            "  # retimed to complete by t = 700 s.  In 98_04 the confinement bleed ran",
            "  # from 1900 to 3300 s, i.e. straight THROUGH the post-shut-in observation",
            "  # window, steadily lowering the effective normal stress while the test was",
            "  # asking whether slip arrests.  The old result (it does) was therefore",
            "  # conservative; this one is clean.",
        ]
    lines += [
        "  #",
        "  # Primary observable: slip_rate_mm_per_s_pp.  The question is whether it has",
        "  # a SECOND maximum after the shut-in instant.  In the 98 runs it did not --",
        "  # the only maximum was 262-491 s BEFORE shut-in, on the ramp.",
    ]

    body = [
        "  [injection_pressure]",
        "    type = ParsedFunction",
        f"    expression = '{expr}'",
        "  []",
    ]
    return build(sample, stem, banner(stem, sample, kind, lines), body, end_time)


def write_slurm(sample, stem, end_time, dtmax, note):
    steps = int(end_time / dtmax) + 1
    est_h = steps * SEC_PER_STEP_32 / 3600.0
    walltime = "24:00:00" if est_h < 14.0 else "48:00:00"
    out = os.path.join(EX, sample, stem + "_hpc_nochk.sh")
    with open(out, "w") as fh:
        fh.write(SLURM.format(stem=stem, sample=sample, hpc_root=HPC_ROOT,
                              walltime=walltime, note=note, end_time=end_time,
                              dtmax=dtmax, steps=steps, est_h=est_h))
    os.chmod(out, os.stat(out).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return walltime, steps, est_h


# ---------------------------------------------------------------------------

WHY_EQ = [
    "  # GROUP A -- three EQUAL-peak load/unload cycles.",
    "  # Question: is the permeability enhancement from an injection cycle retained,",
    "  # and does it keep accumulating on cycles 2 and 3 or saturate?  Holding the",
    "  # peak fixed is what isolates 'enhancement from cycling' from 'enhancement",
    "  # from reaching a pressure never reached before'.",
    "  # This is the 97-series experiment.  It is repeated because three of the four",
    "  # 97 runs were killed by a 12 h / 16-rank allocation their own documentation",
    "  # said was 24 h / 32 ranks, and SW-S3 reached one cycle of three.",
]

WHY_ESC = [
    "  # GROUP B -- three ESCALATING-peak cycles, in equal 2 MPa increments.",
    "  # Group A cannot see the pre-registered outcomes 2 and 3 (continued growth,",
    "  # or gouge outrunning dilation), because an equal-peak cycle breaks no new",
    "  # ground by construction: the joint re-treads a path it has already taken.",
    "  # This deck escalates, which is also what a field stimulation actually does.",
    "  # Because the increments are equal, 'does the enhancement per increment",
    "  # shrink?' is read straight off the peak-hold rows -- no normalisation, no",
    "  # model.  A shrinking increment is saturation; a constant one is not.",
]

WHY_NOHOLD = [
    "  # GROUP C -- shut-in with NO pre-shut-in hold.",
    "  # The 98 runs held 200 s at peak before shutting in, and the completed runs",
    "  # show the peak slip RATE occurring 262-491 s BEFORE the shut-in instant,",
    "  # i.e. during the ramp.  So 'slip arrests after shut-in' was established",
    "  # starting from a fault that was already decelerating.  This deck shuts in",
    "  # at the instant peak pressure is reached.  Same peak, same ramp rate, same",
    "  # everything else: the hold is the only variable, so the pair 98 vs 101",
    "  # answers 'how long must you hold before shut-in arrests the fault?'.",
]

WHY_SLOW = [
    "  # GROUP D -- shut-in with a SLOW bleed-off, tau = 1500 s instead of 150 s.",
    "  # A fast shut-in makes arrest easy: the pressure is gone before the fault can",
    "  # respond.  The field-relevant case is a well that bleeds off over hours.",
    "  # If slip still arrests at tau = 1500 s, arrest is not a race between the",
    "  # wellbore fall-off and diffusion into the fault, and the negative result",
    "  # generalises.  If it does not, the 98 result is an artefact of tau = 150 s",
    "  # and that is the more important finding.",
]

WHY_FRAME = [
    "  # GROUP E -- loading-frame stiffness bracket, two equal-peak cycles.",
    "  # The 97 result showed the joint sitting EXACTLY on the yield surface at",
    "  # every peak hold (tau - tau_lim = 0.0000 MPa to five figures), not below it.",
    "  # It is in neutral plastic equilibrium: the slip-weakening variable W is",
    "  # spent, so tau_lim no longer moves, and what stops slip from accumulating",
    "  # is the SERIES COMPLIANCE OF THE LOADING COLUMN, which sheds shear stress",
    "  # the instant slip resumes.  That makes the null result a statement about",
    "  # the loading system rather than about the aperture law -- and a lab loading",
    "  # frame is not a reservoir.",
    "  # This deck tests it directly.  axial_bc_penalty is scaled and the commanded",
    "  # piston displacements are scaled by its inverse, so the commanded STRESS is",
    "  # unchanged and only the series stiffness moves.  Two cycles suffice: the",
    "  # question is whether cycle 2 reproduces cycle 1.",
    "  # PREDICTION: if the frame sets the saturation, the cycle-2/cycle-1 aperture",
    "  # ratio moves with the stiffness.  If the aperture law sets it, it does not.",
]


def main():
    made = []

    def note(stem, kind):
        return f"101-series discussion deck: {kind}"

    # --- A: equal-peak 3-cycle, all four specimens --------------------------
    for sample, stem in (("SWT1", "101_01_swt1_cyclic3_eq"),
                         ("SWT2", "101_02_swt2_cyclic3_eq"),
                         ("SWS3", "101_03_sw3_cyclic3_eq"),
                         ("SWS4", "101_04_sw4_cyclic3_eq")):
        p_peak = SPECS[sample][2]
        peaks = [p_peak] * 3
        rate = (p_peak - SPECS[sample][1]) / (SPECS[sample][3] - 2.0)
        _, _, et, _ = cyclic_schedule(SPECS[sample][1], peaks, rate, T_SETTLE[sample])
        _, dtmax = cyclic_deck(sample, stem, peaks, "equal-peak 3-cycle", WHY_EQ)
        made.append((sample, stem, et, dtmax, "A", "equal-peak 3-cycle"))

    # --- B: escalating-peak 3-cycle, all four specimens ---------------------
    for sample, stem in (("SWT1", "101_05_swt1_cyclic3_esc"),
                         ("SWT2", "101_06_swt2_cyclic3_esc"),
                         ("SWS3", "101_07_sw3_cyclic3_esc"),
                         ("SWS4", "101_08_sw4_cyclic3_esc")):
        p_peak = SPECS[sample][2]
        peaks = [p_peak - 4.0, p_peak - 2.0, p_peak]
        rate = (p_peak - SPECS[sample][1]) / (SPECS[sample][3] - 2.0)
        _, _, et, _ = cyclic_schedule(SPECS[sample][1], peaks, rate, T_SETTLE[sample])
        _, dtmax = cyclic_deck(sample, stem, peaks, "escalating-peak 3-cycle", WHY_ESC)
        made.append((sample, stem, et, dtmax, "B", "escalating-peak 3-cycle"))

    # --- C: shut-in with no pre-shut-in hold --------------------------------
    for sample, stem in (("SWT1", "101_09_swt1_shutin_nohold"),
                         ("SWT2", "101_10_swt2_shutin_nohold"),
                         ("SWS3", "101_11_sw3_shutin_nohold"),
                         ("SWS4", "101_12_sw4_shutin_nohold")):
        _, _, _, t_peak = SPECS[sample]
        _, _, et = shutin_expression(SPECS[sample][1], SPECS[sample][2], t_peak - 2.0,
                                     T_SETTLE[sample], 0.0, SHUTIN_TAU_FAST,
                                     SHUTIN_OBSERVE)
        _, dtmax = shutin_deck(sample, stem, 0.0, SHUTIN_TAU_FAST, SHUTIN_OBSERVE,
                               "shut-in, no pre-shut-in hold", WHY_NOHOLD)
        made.append((sample, stem, et, dtmax, "C", "shut-in, hold = 0"))

    # --- D: slow shut-in on the two most slip-prone specimens ---------------
    for sample, stem in (("SWT1", "101_13_swt1_shutin_slowtau"),
                         ("SWS4", "101_14_sw4_shutin_slowtau")):
        _, _, _, t_peak = SPECS[sample]
        _, _, et = shutin_expression(SPECS[sample][1], SPECS[sample][2], t_peak - 2.0,
                                     T_SETTLE[sample], 200.0, SHUTIN_TAU_SLOW,
                                     SHUTIN_OBSERVE_SLOW)
        _, dtmax = shutin_deck(sample, stem, 200.0, SHUTIN_TAU_SLOW,
                               SHUTIN_OBSERVE_SLOW, "shut-in, slow bleed-off", WHY_SLOW)
        made.append((sample, stem, et, dtmax, "D", "shut-in, tau = 1500 s"))

    # --- E: loading-frame stiffness bracket on SW-T1 ------------------------
    # axial_pres_* are COMMANDED DISPLACEMENTS equal to -sigma/penalty, so scaling
    # the penalty by g and the displacements by 1/g holds the commanded stress
    # fixed and moves only the series stiffness.  (Check: SW-T1's
    # axial_pres_initial 7.5188e-5 x penalty 4.123e11 = 31.0 MPa = sigma_zz0.)
    base_pen = 412300000000.0
    base_ini = -7.5187969924812e-05
    base_fin = -0.000731213888696882
    for stem, g, label in (("101_15_swt1_cyclic2_frame2x", 2.0, "2x STIFFER"),
                           ("101_16_swt1_cyclic2_frame0p5x", 0.5, "2x SOFTER")):
        p_peak = SPECS["SWT1"][2]
        peaks = [p_peak] * 2
        rate = (p_peak - SPECS["SWT1"][1]) / (SPECS["SWT1"][3] - 2.0)
        _, _, et, _ = cyclic_schedule(SPECS["SWT1"][1], peaks, rate, 2.0)
        why = WHY_FRAME + [
            "  #",
            f"  # THIS ARM: axial_bc_penalty x {g} ({label}).  Commanded stress unchanged.",
        ]
        _, dtmax = cyclic_deck(
            "SWT1", stem, peaks, f"frame bracket, {label}", why,
            extra_scalars=(
                ("axial_bc_penalty", base_pen * g,
                 f"frame bracket arm: k_machine x {g}"),
                ("axial_pres_initial", base_ini / g,
                 f"rescaled by 1/{g} so the commanded stress is unchanged"),
                ("axial_pres_final", base_fin / g,
                 f"rescaled by 1/{g} so the commanded stress is unchanged"),
            ))
        made.append(("SWT1", stem, et, dtmax, "E", f"frame {label.lower()}, 2-cycle"))

    # --- SLURM ---------------------------------------------------------------
    print(f"{'deck':34s} {'grp':4s} {'end_time':>9s} {'dtmax':>6s} {'steps':>7s} "
          f"{'est h':>6s} {'wall':>9s}")
    for sample, stem, et, dtmax, grp, kind in made:
        wall, steps, est_h = write_slurm(sample, stem, et, dtmax, note(stem, kind))
        print(f"{stem:34s} {grp:4s} {et:9.1f} {dtmax:6.2f} {steps:7d} "
              f"{est_h:6.1f} {wall:>9s}")

    # --- submit script -------------------------------------------------------
    tiers = {}
    for sample, stem, et, dtmax, grp, kind in made:
        tiers.setdefault(grp, []).append(f"  {sample}/{stem}_hpc_nochk.sh")
    headers = {
        "A": "TIER 1 -- equal-peak cyclic.  The 97 experiment, resourced to finish.",
        "B": "TIER 3 -- escalating-peak cyclic.  Outcome 2/3, which tier 1 cannot see.",
        "C": "TIER 2 -- shut-in with no hold.  Cheap; isolates the pre-shut-in hold.",
        "D": "TIER 4 -- slow shut-in.  Does arrest survive a realistic bleed-off?",
        "E": "TIER 4 -- SW-T1 frame bracket.  Tests the saturating mechanism itself.",
    }
    lines = ["#!/bin/bash",
             "# " + "=" * 74,
             "# 101-series discussion batch -- 16 decks, 32 ranks / 32 G each.",
             "#",
             "# See doc/DISCUSSION_DECKS_101.md for the design and, importantly, for what",
             "# to MEASURE.  None of these is scoreable against Table 2: every one of them",
             "# replaces the paper's monotonic injection history by design.  Do not run",
             "# scripts/table2_gate.py on them.",
             "#",
             "# Tier order is the order to run them in if the allocation is tight.  Tier 1",
             "# is the batch that must exist -- it is the 97 experiment, which died on a",
             "# 12 h / 16-rank allocation that its own documentation said was 24 h / 32.",
             "# " + "=" * 74,
             "set -u",
             'cd "$(dirname "$0")"',
             "", "JOBS=("]
    for grp in ("A", "C", "B", "D", "E"):
        lines.append(f"  # --- {headers[grp]}")
        lines += tiers[grp]
    lines += [")", "",
              'echo "101 batch: ${#JOBS[@]} decks"',
              'for s in "${JOBS[@]}"; do',
              '  if [ ! -f "$s" ]; then echo "MISSING: $s" >&2; continue; fi',
              '  echo "sbatch $s"',
              '  sbatch "$s"',
              'done', ""]
    sub = os.path.join(EX, "submit_discussion_101.sh")
    with open(sub, "w") as fh:
        fh.write("\n".join(lines))
    os.chmod(sub, os.stat(sub).st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print(f"\nwrote {os.path.relpath(sub, ROOT)}")
    return made


if __name__ == "__main__":
    main()
