#!/usr/bin/env python3
"""Arm C (closure creep) of the Ye & Ghassemi 108-series: the wave-2 analysis.

Four questions, in the order they have to be answered:

  1. Do the long-hold CONTROLS stay flat over 1e6 s?  Everything downstream is
     conditional on this.
  2. Does the material integrate the creep ODE it advertises?  The model's own
     ``closure_creep_aperture_um_pp`` is checked against the same ODE
     reintegrated offline from the run's own ``effective_normal_compression``
     trace.
  3. Is ``closure_creep_time`` an interpretable parameter -- i.e. does the
     observed 63.2 % time match ``tau_c * sigma_ref / N_eff``?  Arm B's
     ``normal_unload_retention_time`` failed exactly this test (observed decay
     12-21x the input), so it must be asked of every new time constant.
  4. Does the aperture actually return to a_h0, as the choice of
     ``closure_creep_max_aperture`` was designed to guarantee?

``score_creep_against_table2`` additionally scores each arm-C run over its
PROTOCOL window against Ye & Ghassemi Table 2, using the PARENT deck's stage
clock.  The arm-C decks extend ``injection_pressure`` with a final point at
t ~ 1e6 s, so scoring them against their own schedule would sample stage 11 a
million seconds late; borrowing the parent's clock is what makes the creep run
and its parent comparable stage for stage.

Usage:
    python3 scripts/ye_series108_wave2.py
"""

import csv
import math
import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
STUDY = ROOT / "Examples" / "YeGhasemmi2018"

# stem -> (specimen, a_h0 um, a_c_max um, tau_c s, sigma_ref MPa, protocol end s,
#          a_min um, parent deck, parent CSV)
RUNS = {
    "108_15_swt1_creeptc1e4": ("SWT1", 1.630, 1.9132, 1.0e4, 65.47, 3500.0, 1.5105,
                               "100_01_swt1_vm55um_ppfix"),
    "108_11_swt1_creeptc1e5": ("SWT1", 1.630, 1.9132, 1.0e5, 65.47, 3500.0, 1.5105,
                               "100_01_swt1_vm55um_ppfix"),
    "108_16_swt1_creeptc1e6": ("SWT1", 1.630, 1.9132, 1.0e6, 65.47, 3500.0, 1.5105,
                               "100_01_swt1_vm55um_ppfix"),
    "108_12_swt2_creeptc1e5": ("SWT2", 2.110, 2.3038, 1.0e5, 66.74, 2850.0, 2.0045,
                               "100_04_swt2_apscale0p0177_ppfix"),
    "108_13_sw3_creeptc1e5":  ("SWS3", 1.220, 0.3590, 1.0e5, 32.10, 4800.0, 1.2200,
                               "100_06_sw3_resc1p30_unld0p00_ppfix"),
    "108_14_sw4_creeptc1e5":  ("SWS4", 0.740, 0.0207, 1.0e5, 31.00, 3500.0, 0.7400,
                               "93_07_sw4_final_theta30_jrc5_ppfix"),
}

CONTROLS = {"108_01_swt1_ctrl_hold1e6": ("SWT1", 3500.0, "100_01_swt1_vm55um_ppfix"),
            "108_02_sw4_ctrl_hold1e6":  ("SWS4", 3500.0, "93_07_sw4_final_theta30_jrc5_ppfix")}

# The 108 CSVs were delivered to the specimen-level directory, not to Sweeps/.
def run_csv(stem, spec):
    return STUDY / spec / "results_csv_hpc_rorqual" / f"{stem}_hpc.csv"


def load(path):
    with open(path) as fh:
        return list(csv.DictReader(fh))


def col(rows, name):
    return [float(r[name]) for r in rows]


def at(t, ts, ys):
    """Last value at or before t."""
    out = ys[0]
    for tt, yy in zip(ts, ys):
        if tt <= t + 1e-9:
            out = yy
        else:
            break
    return out


def controls_are_flat():
    print("=" * 96)
    print("1. CONTROLS -- a_h over the 1e6 s hold (the gate for arms B and C)")
    print("=" * 96)
    for stem, (spec, tp, _parent) in CONTROLS.items():
        rows = load(run_csv(stem, spec))
        ts, ah = col(rows, "time"), col(rows, "hydraulic_aperture_um_pp")
        held = [y for t, y in zip(ts, ah) if t >= tp]
        a0 = at(tp, ts, ah)
        print(f"  {stem:28s} a_h(T_p) = {a0:.6f} um   drift over 1e6 s = "
              f"{1e6 * (ah[-1] - a0) / a0:+.2f} ppm   spread = "
              f"{1e6 * (max(held) - min(held)) / a0:.2f} ppm")


def creep_ode_audit():
    print()
    print("=" * 96)
    print("2. RATE LAW -- model a_c against the same ODE reintegrated offline")
    print("   da_c/dt = (1/tau_c) (<N_eff>_+ / sigma_ref)^q (a_cmax - a_c),  implicit, q = 1")
    print("=" * 96)
    print(f"  {'run':24s} {'max rel dev':>12s} {'at t (s)':>11s} {'a_c/a_cmax there':>17s} "
          f"{'end rel dev':>12s}")
    for stem, (spec, _ah0, acmax, tc, sref, tp, _amin, _p) in RUNS.items():
        rows = load(run_csv(stem, spec))
        ts = col(rows, "time")
        ac = col(rows, "closure_creep_aperture_um_pp")
        ne = col(rows, "effective_normal_compression_mpa_pp")
        a, off = 0.0, []
        for i, t in enumerate(ts):
            dt = t - ts[i - 1] if i else t
            rate = max(ne[i], 0.0) / sref / tc
            a = (a + rate * dt * acmax) / (1.0 + rate * dt)
            off.append(a)
        # Compare only where the transient is resolvable; below 1 % of a_cmax both
        # curves are rounding noise and the ratio is meaningless.
        live = [(m, o, t) for m, o, t in zip(ac, off, ts) if o > 0.01 * acmax]
        worst, t_worst, o_worst = max((abs(m - o) / o, t, o) for m, o, t in live)
        print(f"  {stem:24s} {100 * worst:11.2f}% {t_worst:11.4g} {o_worst / acmax:17.3f} "
              f"{100 * abs(ac[-1] - off[-1]) / off[-1]:11.2f}%")


def time_constant():
    print()
    print("=" * 96)
    print("3. IS tau_c INTERPRETABLE?  observed 63.2 % time vs tau_c * sigma_ref / N_eff")
    print("=" * 96)
    print(f"  {'run':24s} {'N_eff(end)':>11s} {'tau_pred':>11s} {'t_63.2%':>12s} {'ratio':>7s}")
    for stem, (spec, _ah0, acmax, tc, sref, tp, _amin, _p) in RUNS.items():
        rows = load(run_csv(stem, spec))
        ts, ac = col(rows, "time"), col(rows, "closure_creep_aperture_um_pp")
        ne = col(rows, "effective_normal_compression_mpa_pp")
        level = 0.632 * acmax
        t632 = next((t for t, a in zip(ts, ac) if a >= level), None)
        pred = tc * sref / ne[-1]
        got = f"{t632:12.4g}" if t632 else "not reached".rjust(12)
        ratio = f"{t632 / pred:7.3f}" if t632 else "      -"
        print(f"  {stem:24s} {ne[-1]:10.3f} {pred:11.4g} {got} {ratio}")


def does_it_close():
    print()
    print("=" * 96)
    print("4. DOES a_h RETURN TO a_h0?  a_c_max was chosen so that it must")
    print("=" * 96)
    print(f"  {'run':24s} {'a_h(T_p)':>9s} {'a_h(end)':>9s} {'a_h0':>7s} {'a_min':>7s} "
          f"{'a_c/a_cmax':>11s} {'gap to a_h0':>12s} {'k(end)/k(T_p)':>14s}")
    for stem, (spec, ah0, acmax, tc, sref, tp, amin, _p) in RUNS.items():
        rows = load(run_csv(stem, spec))
        ts, ah = col(rows, "time"), col(rows, "hydraulic_aperture_um_pp")
        ac = col(rows, "closure_creep_aperture_um_pp")
        a_tp = at(tp, ts, ah)
        print(f"  {stem:24s} {a_tp:9.4f} {ah[-1]:9.4f} {ah0:7.4f} {amin:7.4f} "
              f"{ac[-1] / acmax:11.3f} {ah[-1] - ah0:+12.4f} {(ah[-1] / a_tp) ** 2:14.4f}")


def score_creep_against_table2():
    """Score each arm-C run over its protocol window, on the PARENT's stage clock."""
    sys.path.insert(0, str(ROOT / "scripts"))
    import table2_gate as gate

    print()
    print("=" * 96)
    print("5. DOES CREEP COST THE CALIBRATED MATCH?  Table-2 nRMSE over the protocol window,")
    print("   scored on the parent deck's stage clock (the arm-C schedule runs to 1e6 s)")
    print("=" * 96)
    parents = {"SWT1": ("100_01_swt1_vm55um_ppfix", "SWT1"),
               "SWT2": ("100_04_swt2_apscale0p0177_ppfix", "SWT2"),
               "SWS3": ("100_06_sw3_resc1p30_unld0p00_ppfix", "SWS3"),
               "SWS4": ("93_07_sw4_final_theta30_jrc5_ppfix", "SWS4")}
    current = {}
    gate.find_deck = lambda csv_path, tag: STUDY / current["spec"] / "Sweeps" / (
        parents[current["spec"]][0] + ".i")

    order = [("SWT1", "100_01_swt1_vm55um_ppfix", "parent"),
             ("SWT1", "108_01_swt1_ctrl_hold1e6", "control"),
             ("SWT1", "108_15_swt1_creeptc1e4", "tau_c = 1e4"),
             ("SWT1", "108_11_swt1_creeptc1e5", "tau_c = 1e5"),
             ("SWT1", "108_16_swt1_creeptc1e6", "tau_c = 1e6"),
             ("SWT2", "100_04_swt2_apscale0p0177_ppfix", "parent"),
             ("SWT2", "108_12_swt2_creeptc1e5", "tau_c = 1e5"),
             ("SWS3", "100_06_sw3_resc1p30_unld0p00_ppfix", "parent"),
             ("SWS3", "108_13_sw3_creeptc1e5", "tau_c = 1e5"),
             ("SWS4", "93_07_sw4_final_theta30_jrc5_ppfix", "parent"),
             ("SWS4", "108_02_sw4_ctrl_hold1e6", "control"),
             ("SWS4", "108_14_sw4_creeptc1e5", "tau_c = 1e5")]

    print(f"  {'sample':7s} {'run':22s} {'Q':>7s} {'sig_n':>7s} {'tau':>7s} {'d_n':>7s} "
          f"{'d_s':>7s} {'MEAN%':>7s} {'vs parent':>10s}")
    base = {}
    for spec, stem, label in order:
        current["spec"] = spec
        if stem.startswith("108_"):
            path = run_csv(stem, spec)
        else:
            path = STUDY / spec / "Sweeps" / "results_csv_hpc_rorqual" / f"{stem}_hpc.csv"
        res = gate.score_run(path, spec, None, 0.15, "stage1", 55.0)
        s = gate.normalised_scores(res)
        if not s:
            print(f"  {spec:7s} {label:22s} incomplete ({res['reached']}/11 stages)")
            continue
        if label == "parent":
            base[spec] = s["mean"]
            delta = ""
        else:
            delta = f"{s['mean'] - base[spec]:+10.4f}"
        print(f"  {spec:7s} {label:22s} " +
              " ".join(f"{s[k]:7.4f}" for k in
                       ("Q_ml_min", "sigma_n_MPa", "tau_MPa", "dn_mm", "ds_mm")) +
              f" {s['mean']:7.4f} {delta}")


def main():
    controls_are_flat()
    creep_ode_audit()
    time_constant()
    does_it_close()
    score_creep_against_table2()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
