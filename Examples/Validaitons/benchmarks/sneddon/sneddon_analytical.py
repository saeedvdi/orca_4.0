"""
Sneddon (1946) pressurized crack — analytical solution and MOOSE comparison.

Problem
-------
A straight crack of half-length b, lying on y = 0 and running from x = -b to
x = +b, is embedded in an infinite linear-elastic medium of Young's modulus E
and Poisson's ratio nu, and is internally pressurized by a uniform fluid
pressure p_f acting on both faces.  The crack opens as

    w(s) = 4 (1 - nu^2) p_f / E * sqrt(b^2 - s^2)

where s is the distance from the crack centre.  The maximum (mid-crack)
opening is therefore

    w_max = 4 (1 - nu^2) p_f b / E

Because the crack is open everywhere, the interface must carry essentially no
constitutive traction: the whole response is the elastic medium reacting to the
fluid load on the faces.  A law that leaks a spurious tensile or contact
traction fails this benchmark even if it gets w_max right, so |sigma_n| / p_f is
reported alongside the opening.

Reference: Sneddon, I. N. (1946). The distribution of stress in the
neighbourhood of a crack in an elastic solid. Proc. R. Soc. Lond. A 187, 229-260.
Configuration follows the GEOS validation case:
  geosx-geosx.readthedocs-hosted.com/en/latest/docs/sphinx/advancedExamples/
  validationStudies/faultMechanics/sneddon/Example.html

What this script does
---------------------
Reads the MOOSE output of each interface constitutive law, compares it against
the closed form both as a scalar (w_max) and along the whole crack (the opening
profile), and writes the comparison out as CSV plus a figure.

Two independent measures of agreement are produced:

  * pointwise error of w(s) against the closed form, and
  * a shape fit.  Squaring the closed form gives

        w^2 = A^2 b^2 - A^2 s^2,       A = 4 (1 - nu^2) p_f / E

    which is linear in s^2.  Regressing w^2 on s^2 therefore recovers the
    amplitude A and the half-length b that the numerical solution actually
    carries, with no non-linear solver and no scipy dependency.  A correct
    solution must return both the analytic amplitude and the meshed b; the two
    failure modes are distinguishable, which a single scalar error cannot do.

Usage
-----
Run the decks first (from this directory):

    mpiexec -n 8 ../../../../orca-opt -i sneddon_barton_bandis.i
    mpiexec -n 8 ../../../../orca-opt -i sneddon_compression_tensile.i

then

    python sneddon_analytical.py                  # BBFast and MC
    python sneddon_analytical.py --all            # all four interface laws
    python sneddon_analytical.py --no-plot        # CSV only

Requires numpy and matplotlib only (no scipy), so it runs under either the
`moose` environment or the base miniforge python.

Outputs, written next to this script:
    sneddon_comparison_summary.csv   one row per law: scalars, errors, shape fit
    sneddon_comparison_profile.csv   s, analytic w, and each law's w
    sneddon_comparison.png           profile overlay and pointwise error
"""

import argparse
import csv
import glob
import os
import re
import sys

import numpy as np

# --------------------------------------------------------------------------
# Benchmark parameters.  These mirror the decks; verify_deck_parameters()
# re-reads the deck and fails loudly if the two ever drift apart.
# --------------------------------------------------------------------------
YOUNGS_MODULUS = 1.0e10  # Pa
POISSONS_RATIO = 0.25
CRACK_PRESSURE = 2.0e6  # Pa
HALF_LENGTH = 1.0  # m, crack runs x = -1 .. +1 on y = 0

# label -> deck suffix.  The first two are the pair asked for most often; the
# other two are the remaining laws in the suite.
MODELS = {
    "BBFast": "barton_bandis",
    "MC": "compression_tensile",
}
EXTRA_MODELS = {
    "BB flow/RSF": "bb_flow_rsf",
    "Peak-shelf-tail": "peak_shelf_tail",
}

MODEL_MATERIAL = {
    "BBFast": "ADOrcaBartonBandisContactTractionFastADHardening",
    "MC": "ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile",
    "BB flow/RSF": "ADOrcaBartonBandisFlowRSFContactTraction",
    "Peak-shelf-tail": "ADOrcaPeakShelfTailFlowRSFContactTraction",
}


def opening_amplitude(E=YOUNGS_MODULUS, nu=POISSONS_RATIO, p_f=CRACK_PRESSURE):
    """A in w(s) = A * sqrt(b^2 - s^2)."""
    return 4.0 * (1.0 - nu**2) * p_f / E


def crack_opening(s, b=HALF_LENGTH, **kw):
    """Sneddon opening profile w(s).  Zero outside the crack."""
    s = np.asarray(s, dtype=float)
    inside = np.abs(s) <= b
    w = np.zeros_like(s)
    w[inside] = opening_amplitude(**kw) * np.sqrt(b**2 - s[inside] ** 2)
    return w


def max_opening(b=HALF_LENGTH, **kw):
    """w_max = 4 (1 - nu^2) p_f b / E."""
    return opening_amplitude(**kw) * b


# --------------------------------------------------------------------------
# Reading MOOSE output
# --------------------------------------------------------------------------
def _read_csv(path):
    """Read a MOOSE CSV into a dict of float arrays."""
    with open(path, newline="") as fh:
        rows = list(csv.DictReader(fh))
    if not rows:
        return {}
    out = {}
    for key in rows[0]:
        vals = []
        for r in rows:
            try:
                vals.append(float(r[key]))
            except (TypeError, ValueError):
                vals.append(np.nan)
        out[key] = np.asarray(vals)
    return out


def read_scalars(directory, suffix):
    """Final-time scalar postprocessor values from sneddon_<suffix>_out.csv."""
    path = os.path.join(directory, f"sneddon_{suffix}_out.csv")
    if not os.path.exists(path):
        return None
    data = _read_csv(path)
    if not data:
        return None
    return {k: v[-1] for k, v in data.items()}


def read_profile(directory, suffix):
    """
    Opening profile from the last non-empty crack_opening_profile CSV.

    MOOSE writes one numbered file per execution of the VectorPostprocessor.
    The highest-numbered file with data is the converged profile.  Files that
    contain only a header are skipped rather than treated as a failure: that is
    exactly what the whole suite produced while the sampler was set to
    `execute_on = FINAL`, and skipping them keeps this script usable against
    older output.
    """
    pattern = os.path.join(directory, f"sneddon_{suffix}_out_crack_opening_profile_*.csv")
    for path in sorted(glob.glob(pattern), reverse=True):
        data = _read_csv(path)
        if data and len(next(iter(data.values()))) > 1:
            order = np.argsort(data["x"])
            return {
                "path": os.path.basename(path),
                "s": data["x"][order],  # crack lies on y = 0, so s == x
                "w": data["crack_opening"][order],
            }
    return None


# --------------------------------------------------------------------------
# Shape fit:  w^2 = A^2 b^2 - A^2 s^2  is linear in s^2
# --------------------------------------------------------------------------
def fit_ellipse(s, w, tip_exclusion=0.10):
    """
    Recover (amplitude, half_length) from a numerical opening profile.

    Points within `tip_exclusion` of the tip are dropped: the closed form has a
    square-root singularity in the stress there, so the tip elements carry the
    bulk of the discretization error and would otherwise dominate a
    least-squares fit that is meant to characterize the bulk of the crack.
    """
    s = np.asarray(s, float)
    w = np.asarray(w, float)
    keep = (np.abs(s) <= (1.0 - tip_exclusion) * np.max(np.abs(s))) & (w > 0.0)
    if keep.sum() < 3:
        return float("nan"), float("nan")
    slope, intercept = np.polyfit(s[keep] ** 2, w[keep] ** 2, 1)
    if slope >= 0.0 or intercept <= 0.0:
        return float("nan"), float("nan")
    amplitude = np.sqrt(-slope)
    half_length = np.sqrt(intercept / (amplitude**2))
    return float(amplitude), float(half_length)


# --------------------------------------------------------------------------
# Deck cross-check
# --------------------------------------------------------------------------
def verify_deck_parameters(directory, suffix="barton_bandis"):
    """
    Re-read the benchmark constants from the deck and compare with this file.

    A validation script that silently disagrees with the deck it is validating
    is worse than no script, so any drift is reported rather than absorbed.
    """
    path = os.path.join(directory, f"sneddon_{suffix}.i")
    if not os.path.exists(path):
        return []
    text = open(path).read()
    expected = {
        "youngs_modulus": YOUNGS_MODULUS,
        "poissons_ratio": POISSONS_RATIO,
        "crack_pressure": CRACK_PRESSURE,
        "half_length": HALF_LENGTH,
    }
    problems = []
    for name, want in expected.items():
        m = re.search(rf"^{name}\s*=\s*([0-9eE.+-]+)\s*(?:#.*)?$", text, re.M)
        if not m:
            problems.append(f"{name}: not found in {os.path.basename(path)}")
            continue
        got = float(m.group(1))
        if not np.isclose(got, want, rtol=1e-12):
            problems.append(f"{name}: deck has {got:g}, this script uses {want:g}")
    return problems


# --------------------------------------------------------------------------
# Comparison
# --------------------------------------------------------------------------
def compare(directory, models):
    """Build one summary record per model, plus the profile table."""
    summary = []
    profiles = {}
    w_max_ref = max_opening()

    for label, suffix in models.items():
        scalars = read_scalars(directory, suffix)
        profile = read_profile(directory, suffix)
        if scalars is None and profile is None:
            print(f"  {label:16s} no output found (deck not run?)", file=sys.stderr)
            continue

        rec = {
            "model": label,
            "material": MODEL_MATERIAL.get(label, ""),
            "w_max_analytic_m": w_max_ref,
        }

        if scalars is not None:
            w_max = scalars.get("w_max", float("nan"))
            rec["w_max_numerical_m"] = w_max
            rec["w_max_rel_error"] = abs(w_max - w_max_ref) / w_max_ref
            rec["sigma_n_mean_Pa"] = scalars.get("sigma_n_mean", float("nan"))
            rec["open_traction_ratio"] = scalars.get("open_traction_ratio", float("nan"))

        if profile is not None:
            s = profile["s"]
            w_num = profile["w"]
            w_ana = crack_opening(s)
            resid = w_num - w_ana
            rec["profile_points"] = len(s)
            rec["profile_source"] = profile["path"]
            rec["profile_rms_error_m"] = float(np.sqrt(np.mean(resid**2)))
            rec["profile_rms_rel_error"] = float(
                np.sqrt(np.mean(resid**2)) / w_max_ref
            )
            rec["profile_max_abs_error_m"] = float(np.max(np.abs(resid)))
            amp, b_fit = fit_ellipse(s, w_num)
            rec["fitted_amplitude"] = amp
            rec["fitted_amplitude_analytic"] = opening_amplitude()
            rec["fitted_amplitude_rel_error"] = (
                abs(amp - opening_amplitude()) / opening_amplitude()
            )
            rec["fitted_half_length_m"] = b_fit
            rec["fitted_half_length_rel_error"] = abs(b_fit - HALF_LENGTH) / HALF_LENGTH
            profiles[label] = (s, w_num)

        summary.append(rec)

    return summary, profiles


def write_summary(directory, summary):
    path = os.path.join(directory, "sneddon_comparison_summary.csv")
    fields = []
    for rec in summary:
        for k in rec:
            if k not in fields:
                fields.append(k)
    with open(path, "w", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        for rec in summary:
            writer.writerow(rec)
    return path


def write_profiles(directory, profiles):
    """
    Interpolate every model onto one s grid so the file is a single table.

    The models are run on the same mesh, so their sample points coincide in
    practice; interpolating anyway keeps the writer correct if a refined deck is
    ever added to the comparison.
    """
    if not profiles:
        return None
    path = os.path.join(directory, "sneddon_comparison_profile.csv")
    grid = next(iter(profiles.values()))[0]
    header = ["s_m", "w_analytic_m"] + [f"w_{lbl}_m" for lbl in profiles]
    header += [f"err_{lbl}_m" for lbl in profiles]
    w_ana = crack_opening(grid)
    cols = [grid, w_ana]
    for _, (s, w) in profiles.items():
        cols.append(np.interp(grid, s, w))
    for col in list(cols[2:]):
        cols.append(col - w_ana)
    with open(path, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(header)
        writer.writerows(np.column_stack(cols))
    return path


def plot(directory, profiles):
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # Figure is only ever meant to show the two laws asked for most often; any
    # extra laws computed via --all are kept in the CSVs but dropped here.
    profiles = {lbl: profiles[lbl] for lbl in MODELS if lbl in profiles}

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

    # The laws agree to ~12 significant figures, so plotting every point of both
    # series would stack identical markers on top of each other and the shape
    # difference would be invisible.  Staggering which points each series draws
    # (markevery with opposite phase) interleaves circles and squares along the
    # curve instead of hiding one under the other, on top of making the squares
    # themselves bigger, filled, and open-circle vs. filled-square in style.
    style = {
        "BBFast": dict(marker="o", ms=11.0, mfc="none", mew=1.8, markevery=(0, 2)),
        "MC": dict(marker="s", ms=8.0, mfc="tab:orange", mew=0.0, alpha=0.9, markevery=(1, 2)),
    }

    s_fine = np.linspace(-HALF_LENGTH, HALF_LENGTH, 400)

    fig, ax = plt.subplots(figsize=(10.0, 7.5))
    ax.plot(
        s_fine,
        crack_opening(s_fine) * 1e3,
        "k-",
        lw=2.0,
        label=r"Sneddon  $w=\frac{4(1-\nu^2)p_f}{E}\sqrt{b^2-s^2}$",
    )
    for label, (s, w) in profiles.items():
        ax.plot(s, w * 1e3, ls="none", label=label, **style.get(label, {}))

    ax.set_xlabel("distance along crack $s$  (m)")
    ax.set_ylabel("crack opening $w$  (mm)")
    ax.set_title(
        "Sneddon pressurized-crack benchmark\n"
        f"$E$={YOUNGS_MODULUS/1e9:g} GPa,  $\\nu$={POISSONS_RATIO:g},  "
        f"$p_f$={CRACK_PRESSURE/1e6:g} MPa,  $b$={HALF_LENGTH:g} m"
    )
    ax.legend(frameon=False)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    path = os.path.join(directory, "sneddon_comparison.png")
    fig.savefig(path, dpi=600)
    plt.close(fig)

    fig_e, axe = plt.subplots(figsize=(10.0, 7.5))
    for label, (s, w) in profiles.items():
        axe.plot(
            s, (w - crack_opening(s)) * 1e6, ls="none", label=label, **style.get(label, {})
        )
    axe.axhline(0.0, color="k", lw=0.8)
    axe.set_xlabel("distance along crack $s$  (m)")
    axe.set_ylabel(r"numerical $-$ analytic  ($\mu$m)")
    axe.legend(frameon=False)
    axe.grid(alpha=0.3)
    fig_e.tight_layout()
    path_e = os.path.join(directory, "sneddon_comparison_residual.png")
    fig_e.savefig(path_e, dpi=600)
    plt.close(fig_e)

    return path, path_e


def report(summary):
    print()
    print(f"  analytic w_max = {max_opening():.6e} m")
    print()
    head = (
        f"  {'model':16s} {'w_max (m)':>14s} {'err':>9s} "
        f"{'|sig_n|/p_f':>12s} {'prof RMS':>10s} {'fit A err':>10s} {'fit b (m)':>10s}"
    )
    print(head)
    print("  " + "-" * (len(head) - 2))
    for rec in summary:
        print(
            f"  {rec['model']:16s} "
            f"{rec.get('w_max_numerical_m', float('nan')):14.6e} "
            f"{rec.get('w_max_rel_error', float('nan')) * 100:8.3f}% "
            f"{rec.get('open_traction_ratio', float('nan')):12.2e} "
            f"{rec.get('profile_rms_rel_error', float('nan')) * 100:9.3f}% "
            f"{rec.get('fitted_amplitude_rel_error', float('nan')) * 100:9.3f}% "
            f"{rec.get('fitted_half_length_m', float('nan')):10.5f}"
        )
    print()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument(
        "--dir",
        default=os.path.dirname(os.path.abspath(__file__)),
        help="directory holding the MOOSE output (default: this script's directory)",
    )
    parser.add_argument(
        "--all", action="store_true", help="include all four interface laws"
    )
    parser.add_argument("--no-plot", action="store_true", help="skip the figure")
    args = parser.parse_args(argv)

    models = dict(MODELS)
    if args.all:
        models.update(EXTRA_MODELS)

    print(f"Sneddon benchmark comparison — reading {args.dir}")

    problems = verify_deck_parameters(args.dir)
    if problems:
        print("\n  WARNING: this script and the deck disagree:", file=sys.stderr)
        for p in problems:
            print(f"    {p}", file=sys.stderr)
        print(
            "  The comparison below uses THIS SCRIPT's values.\n",
            file=sys.stderr,
        )

    summary, profiles = compare(args.dir, models)
    if not summary:
        print("No MOOSE output found. Run the decks first.", file=sys.stderr)
        return 1

    report(summary)
    print(f"  wrote {write_summary(args.dir, summary)}")
    p = write_profiles(args.dir, profiles)
    if p:
        print(f"  wrote {p}")
    if not args.no_plot and profiles:
        path, path_e = plot(args.dir, profiles)
        print(f"  wrote {path}")
        print(f"  wrote {path_e}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
