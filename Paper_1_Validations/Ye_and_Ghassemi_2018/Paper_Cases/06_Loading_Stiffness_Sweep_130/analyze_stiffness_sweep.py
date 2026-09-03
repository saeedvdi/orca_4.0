#!/usr/bin/env python3
"""Extract slip-burst characteristics from the series-130 loading-stiffness sweep.

Reports, per member, the quantities Ye and Ghassemi (2018) tabulate in their
Table 3 -- peak slip rate and peak stress-relaxation rate through the dynamic
slip interval -- as a function of the axial boundary stiffness alone. Their
measured SW-T1 values are 4.89e-5 m/s and 7.69 MPa/s.

Usage:  python3 analyze_stiffness_sweep.py [results_csv]
"""
import csv, glob, os, re, sys
import numpy as np

YG_SLIP_RATE = 4.89e-5     # m/s, Ye & Ghassemi Table 3, SW-T1 dynamic interval
YG_DROP_RATE = 7.69        # MPa/s, same
K0 = 4.123e11

def load(path):
    rows = list(csv.DictReader(open(path)))
    g = lambda k: np.array([float(r[k]) for r in rows])
    return g("time"), g("differential_stress_mpa_pp"), g("reported_czm_shear_slip_mm_pp")

def burst(t, sd, ds):
    """Locate the dynamic interval as the window of steepest stress relaxation."""
    dt = np.diff(t)
    ok = dt > 0
    rate = np.zeros_like(dt); rate[ok] = np.diff(sd)[ok] / dt[ok]     # MPa/s, negative
    sr = np.zeros_like(dt); sr[ok] = np.diff(ds)[ok] * 1e-3 / dt[ok]  # m/s
    i = int(np.argmin(rate))
    # extend while relaxation stays within 10% of peak, to get the interval
    lo = hi = i
    thr = 0.10 * rate[i]
    while lo > 0 and rate[lo - 1] < thr: lo -= 1
    while hi < len(rate) - 1 and rate[hi + 1] < thr: hi += 1
    return dict(t_onset=t[lo], dur=t[hi + 1] - t[lo],
                drop=sd[lo] - sd[hi + 1], peak_drop_rate=-rate[i],
                peak_slip_rate=sr[i], total_slip=ds[-1])

def main():
    d = sys.argv[1] if len(sys.argv) > 1 else "results_csv"
    files = sorted(glob.glob(os.path.join(d, "130_*_swt1_kp*.csv")))
    if not files:
        sys.exit(f"no member CSVs in {d}/ -- runs not finished yet?")
    print(f"{'member':>7} {'k_p (Pa/m)':>12} {'k/k0':>7} {'t_slip':>8} {'dur':>7} "
          f"{'drop':>8} {'d(sd)/dt':>10} {'slip rate':>11} {'d_s tot':>8}")
    print(f"{'':>7} {'':>12} {'':>7} {'(s)':>8} {'(s)':>7} {'(MPa)':>8} "
          f"{'(MPa/s)':>10} {'(m/s)':>11} {'(mm)':>8}")
    out = []
    for f in files:
        m = re.search(r"130_(\d+)_swt1_kp([0-9p]+e[0-9]+)", os.path.basename(f))
        k = float(m.group(2).replace("p", "."))
        try:
            b = burst(*load(f))
        except Exception as e:
            print(f"{m.group(1):>7} {k:12.3e}  -- unreadable: {e}"); continue
        out.append((k, b))
        print(f"{m.group(1):>7} {k:12.3e} {k/K0:7.2f} {b['t_onset']:8.1f} {b['dur']:7.2f} "
              f"{b['drop']:8.2f} {b['peak_drop_rate']:10.2f} {b['peak_slip_rate']:11.2e} "
              f"{b['total_slip']:8.3f}")
    print(f"\nYe & Ghassemi (2018) Table 3, SW-T1 dynamic interval: "
          f"{YG_DROP_RATE} MPa/s, {YG_SLIP_RATE:.2e} m/s")
    if len(out) > 2:
        k = np.array([o[0] for o in out]); r = np.array([o[1]['peak_drop_rate'] for o in out])
        good = (k > 0) & (r > 0)
        if good.sum() > 2:
            p = np.polyfit(np.log10(k[good]), np.log10(r[good]), 1)
            print(f"power-law fit: peak stress-drop rate ~ k_p^{p[0]:.2f}")
            print("(slope near 0 would mean the frame does not control the drop; "
                  "a clear positive slope is the paper's point)")
        try:
            import matplotlib; matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            fig, ax = plt.subplots(1, 2, figsize=(7.2, 2.9))
            ax[0].loglog(k, r, "o-", color="#1f77b4")
            ax[0].axhline(YG_DROP_RATE, ls="--", c="k", lw=0.8)
            ax[0].text(k.min(), YG_DROP_RATE*1.1, "Ye & Ghassemi SW-T1", fontsize=6)
            ax[0].set_xlabel(r"axial boundary stiffness $k_p$ (Pa m$^{-1}$)", fontsize=7)
            ax[0].set_ylabel(r"peak $|\mathrm{d}\sigma_d/\mathrm{d}t|$ (MPa s$^{-1}$)", fontsize=7)
            s = np.array([o[1]['peak_slip_rate'] for o in out])
            ax[1].loglog(k, s, "s-", color="#d62728")
            ax[1].axhline(YG_SLIP_RATE, ls="--", c="k", lw=0.8)
            ax[1].set_xlabel(r"axial boundary stiffness $k_p$ (Pa m$^{-1}$)", fontsize=7)
            ax[1].set_ylabel(r"peak slip rate (m s$^{-1}$)", fontsize=7)
            for a in ax:
                a.axvline(K0, color="0.6", lw=0.8, ls=":")
                a.tick_params(labelsize=6); a.grid(alpha=0.3, lw=0.4)
            fig.tight_layout()
            fig.savefig("Figure_Stiffness_Sweep.pdf"); fig.savefig("Figure_Stiffness_Sweep.png", dpi=200)
            print("wrote Figure_Stiffness_Sweep.pdf")
        except ImportError:
            pass

if __name__ == "__main__":
    main()
