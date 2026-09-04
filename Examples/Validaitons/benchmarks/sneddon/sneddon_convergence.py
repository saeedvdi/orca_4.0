"""
Sneddon benchmark — crack-tip mesh convergence study.

Why
---
The headline Sneddon result is "2.03 % agreement with the closed form". On its
own that is a weak statement: it could equally be a converged 2 % model error or
an unconverged discretization error that happens to land at 2 %. The two are
distinguished only by refining and watching what the error does.

The shape fit in `sneddon_analytical.py` already suggests the answer. It splits
the 2.03 % into an amplitude error of 0.69 % and an effective half-length of
0.9865 m against a meshed 1.0 m. Both point at the crack tip, where the closed
form has a square-root singularity that QUAD4 elements cannot represent. If that
diagnosis is right, refining the tip must drive both down.

This script runs the deck at successive `RefineBlockGenerator` levels and reports
the trend, converting "2 % agreement" into "converging to the analytic solution",
which is the statement a reviewer will actually want.

What is varied
--------------
Only `refinement` on `matrix_bottom_mid` / `matrix_top_mid` — the two blocks that
straddle the crack. The outer box, the base grid and every material and solver
setting are untouched, so the sweep isolates crack-tip resolution. The domain
error (a 40 m box standing in for an infinite medium) is held fixed by
construction and will show up as the floor the sequence converges to.

Element count grows as 4^r on the refined blocks, so level 5 is roughly 330k
elements with a direct solve; that is the practical ceiling on a workstation.

Usage
-----
    python sneddon_convergence.py                        # levels 2..5, BBFast
    python sneddon_convergence.py --levels 2 3 4
    python sneddon_convergence.py --model compression_tensile
    python sneddon_convergence.py --ranks 8

Writes `sneddon_convergence.csv` and `sneddon_convergence.png` next to itself.
Requires numpy and matplotlib; needs `orca-opt` and mpiexec to run the cases.
"""

import argparse
import csv
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
ORCA = os.path.join(REPO, "orca-opt")
MPIEXEC = "/home/geomechanics/miniforge/envs/moose/bin/mpiexec"

# Mirrors the deck; sneddon_analytical.py cross-checks these against it.
YOUNGS_MODULUS = 1.0e10
POISSONS_RATIO = 0.25
CRACK_PRESSURE = 2.0e6
HALF_LENGTH = 1.0
W_MAX_ANALYTIC = 4.0 * (1.0 - POISSONS_RATIO**2) * CRACK_PRESSURE * HALF_LENGTH / YOUNGS_MODULUS


def build_case(model, level, workdir):
    """Copy the deck into `workdir` with `refinement` set to `level`."""
    src = os.path.join(HERE, f"sneddon_{model}.i")
    text = open(src).read()
    new, n = re.subn(
        r"(\[refine_crack_blocks\](?:.|\n)*?refinement = ')\d+ \d+(')",
        rf"\g<1>{level} {level}\g<2>",
        text,
        count=1,
    )
    if n != 1:
        raise RuntimeError(f"could not set refinement in {src}")
    dst = os.path.join(workdir, f"sneddon_r{level}.i")
    open(dst, "w").write(new)
    return dst


def run_case(deck, ranks):
    env = dict(os.environ)
    env["LIBRARY_PATH"] = "/home/geomechanics/miniforge/envs/moose/lib"
    proc = subprocess.run(
        [MPIEXEC, "-n", str(ranks), ORCA, "-i", os.path.basename(deck)],
        cwd=os.path.dirname(deck),
        env=env,
        capture_output=True,
        text=True,
    )
    if proc.returncode != 0:
        tail = "\n".join(proc.stdout.strip().splitlines()[-12:])
        raise RuntimeError(f"{os.path.basename(deck)} failed:\n{tail}")
    return proc.stdout


def read_case(workdir, level):
    """Return (w_max, fitted amplitude, fitted half-length, n_elem)."""
    base = os.path.join(workdir, f"sneddon_r{level}_out")
    with open(base + ".csv", newline="") as fh:
        rows = list(csv.DictReader(fh))
    w_max = float(rows[-1]["w_max"])

    profile = None
    for idx in range(9, -1, -1):
        path = f"{base}_crack_opening_profile_000{idx}.csv"
        if not os.path.exists(path):
            continue
        with open(path, newline="") as fh:
            prof = list(csv.DictReader(fh))
        if len(prof) > 1:
            profile = prof
            break
    if profile is None:
        return w_max, float("nan"), float("nan"), 0

    s = np.array([float(r["x"]) for r in profile])
    w = np.array([float(r["crack_opening"]) for r in profile])
    keep = (np.abs(s) <= 0.9 * np.max(np.abs(s))) & (w > 0)
    slope, intercept = np.polyfit(s[keep] ** 2, w[keep] ** 2, 1)
    amp = math.sqrt(-slope)
    b_fit = math.sqrt(intercept / amp**2)
    return w_max, amp, b_fit, len(s)


def observed_order(h, err):
    """Least-squares slope of log(err) vs log(h): the observed convergence rate."""
    h = np.asarray(h, float)
    err = np.asarray(err, float)
    good = (err > 0) & np.isfinite(err)
    if good.sum() < 2:
        return float("nan")
    return float(np.polyfit(np.log(h[good]), np.log(err[good]), 1)[0])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--levels", type=int, nargs="+", default=[2, 3, 4, 5])
    parser.add_argument("--model", default="barton_bandis")
    parser.add_argument("--ranks", type=int, default=8)
    parser.add_argument("--keep", action="store_true", help="keep the scratch decks")
    args = parser.parse_args(argv)

    if not os.path.exists(ORCA):
        print(f"orca-opt not found at {ORCA}", file=sys.stderr)
        return 1

    workdir = tempfile.mkdtemp(prefix="sneddon_conv_")
    # The deck loads no external mesh, but it does resolve output paths relative
    # to its own directory, so the scratch copy is self-contained.
    print(f"Sneddon convergence sweep — model {args.model}, scratch {workdir}\n")

    rows = []
    try:
        for level in args.levels:
            deck = build_case(args.model, level, workdir)
            print(f"  refinement {level} ... ", end="", flush=True)
            run_case(deck, args.ranks)
            w_max, amp, b_fit, npts = read_case(workdir, level)
            # Element size across the crack: base grid is 40 m / 80 cells = 0.5 m.
            h = 0.5 / (2**level)
            rows.append(
                {
                    "refinement_level": level,
                    "element_size_m": h,
                    "elements_across_crack": int(round(2 * HALF_LENGTH / h)),
                    "profile_samples": npts,
                    "w_max_m": w_max,
                    "w_max_rel_error": abs(w_max - W_MAX_ANALYTIC) / W_MAX_ANALYTIC,
                    "fitted_amplitude": amp,
                    "fitted_amplitude_rel_error": abs(
                        amp - 4.0 * (1.0 - POISSONS_RATIO**2) * CRACK_PRESSURE / YOUNGS_MODULUS
                    )
                    / (4.0 * (1.0 - POISSONS_RATIO**2) * CRACK_PRESSURE / YOUNGS_MODULUS),
                    "fitted_half_length_m": b_fit,
                    "fitted_half_length_rel_error": abs(b_fit - HALF_LENGTH) / HALF_LENGTH,
                }
            )
            print(
                f"h={h:.5f} m, w_max={w_max:.7e}, "
                f"err={rows[-1]['w_max_rel_error']*100:.3f}%"
            )
    finally:
        if not args.keep:
            shutil.rmtree(workdir, ignore_errors=True)

    if not rows:
        return 1

    h = [r["element_size_m"] for r in rows]
    print()
    print(f"  analytic w_max = {W_MAX_ANALYTIC:.7e} m")
    print()
    head = (
        f"  {'level':>5s} {'h (m)':>9s} {'elems/crack':>12s} {'w_max err':>10s} "
        f"{'amp err':>9s} {'b_fit (m)':>10s} {'b err':>8s}"
    )
    print(head)
    print("  " + "-" * (len(head) - 2))
    for r in rows:
        print(
            f"  {r['refinement_level']:5d} {r['element_size_m']:9.5f} "
            f"{r['elements_across_crack']:12d} "
            f"{r['w_max_rel_error']*100:9.3f}% {r['fitted_amplitude_rel_error']*100:8.3f}% "
            f"{r['fitted_half_length_m']:10.5f} {r['fitted_half_length_rel_error']*100:7.3f}%"
        )
    print()
    for key, label in (
        ("w_max_rel_error", "w_max"),
        ("fitted_amplitude_rel_error", "fitted amplitude"),
        ("fitted_half_length_rel_error", "fitted half-length"),
    ):
        p = observed_order(h, [r[key] for r in rows])
        print(f"  observed order in h for {label:<20s}: {p:5.2f}")
    print()

    out_csv = os.path.join(HERE, "sneddon_convergence.csv")
    with open(out_csv, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    print(f"  wrote {out_csv}")

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt

        plt.rcParams.update(
            {
                "font.family": "serif",
                "font.serif": ["Times New Roman", "DejaVu Serif", "serif"],
                "mathtext.fontset": "dejavuserif",
                "font.size": 20,
                "axes.titlesize": 22,
                "axes.labelsize": 22,
                "xtick.labelsize": 18,
                "ytick.labelsize": 18,
                "legend.fontsize": 18,
            }
        )

        fig, ax = plt.subplots(figsize=(10.0, 7.5))
        for key, marker, label in (
            ("w_max_rel_error", "o", r"$w_{\max}$"),
            ("fitted_amplitude_rel_error", "s", "fitted amplitude $A$"),
            ("fitted_half_length_rel_error", "^", "fitted half-length $b$"),
        ):
            ax.loglog(h, [r[key] * 100 for r in rows], marker + "-", label=label)
        ref = np.array(h, float)
        ax.loglog(
            ref,
            100 * rows[0]["w_max_rel_error"] * (ref / ref[0]) ** 0.5,
            "k--",
            lw=1.0,
            label=r"$O(h^{1/2})$ reference",
        )
        ax.set_xlabel("element size at the crack tip $h$  (m)")
        ax.set_ylabel("relative error  (%)")
        ax.set_title("Sneddon — crack-tip mesh convergence")
        ax.grid(alpha=0.3, which="both")
        ax.legend(frameon=False)
        fig.tight_layout()
        out_png = os.path.join(HERE, "sneddon_convergence.png")
        fig.savefig(out_png, dpi=600)
        plt.close(fig)
        print(f"  wrote {out_png}")
    except ImportError:
        pass

    return 0


if __name__ == "__main__":
    sys.exit(main())
