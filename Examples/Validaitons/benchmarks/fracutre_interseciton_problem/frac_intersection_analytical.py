"""
Two intersecting fractures ("T-fracture") — comparison against the Phan et al. (2003)
boundary-element reference solution.

Problem
-------
A pressurized vertical crack whose upper tip lands on the middle of a compressed,
frictional horizontal fracture:

    vertical    x = 0,    y in [-50, +50]    100 MPa fluid pressure inside
    horizontal  y = +50,  x in [-25, +25]    frictional, mu = tan(30 deg), no cohesion

with a far-field sigma_yy = -100 MPa and sigma_xx = 0, rollers on every outer boundary.

Reference: GEOS validation case
  geosx-geosx.readthedocs-hosted.com/en/latest/docs/sphinx/advancedExamples/
  validationStudies/faultMechanics/intersectFrac/Example.html
built from inputFiles/lagrangianContactMechanics/TFrac_base.xml.  The reference curves
are the symmetric-Galerkin boundary element solution of

  Phan, Napier, Gray & Kaplan (2003), "Symmetric-Galerkin BEM simulation of fracture
  with frictional contact", Int. J. Numer. Meth. Engng 57, 835-851,

shipped with GEOS as Aperture.txt / Slip.txt / NormalTraction.txt and reproduced here
verbatim.  There is no closed form for this configuration; Sneddon's isolated-crack
solution is carried alongside only as a scale, and the reference is expected to BEAT it
(see below).

What is compared
----------------
Three curves, all at the end of loading:

  1. aperture      of the vertical fracture   vs y,  in mm
  2. normal traction of the horizontal fracture vs x,  in MPa (compression reported
     positive, following the reference file's own sign)
  3. slip          of the horizontal fracture vs x,  in mm

Coordinate mapping.  The reference files use an arc length measured from one tip:

    Aperture.txt        s in [0, 100]  ->  y = +50 - s      (s = 0 at the T-junction)
    NormalTraction.txt  s in [0,  50]  ->  x = s - 25
    Slip.txt            s in [0,  50]  ->  x = s - 25

Why this case is not covered by sneddon/ or shear_compression/
--------------------------------------------------------------
Those exercise an open interface and a closed sliding one separately.  Here the two
MEET, and three things follow that neither can reach:

  * At the T-junction the mesh node must separate into three pieces, because the crack
    faces slide apart ALONG the horizontal fracture.  The reference aperture there is
    135 mm, not the zero an ordinary crack tip would give.  A junction that is welded
    shut scores this as ~0 and nothing else in the deck complains.
  * The peak aperture sits ABOVE the isolated-crack closed form -- Phan et al. give
    282.2 mm against Sneddon's 274.3 mm, i.e. +2.9 %.  The horizontal fracture is what
    relieves the upper end of the crack.
  * The horizontal fracture is loaded normal to itself; nothing shears it directly.  Its
    ~67 mm of slip is induced entirely by the crack opening beneath it, at a Coulomb
    limit that the same opening is simultaneously moving.

Two checks independent of the reference file are reported as well:

  * the slip must be ANTISYMMETRIC about the junction, because its driver is;
  * where the horizontal fracture slides, |tau| / |sigma_n| must sit exactly on
    tan(30 deg) = 0.57735.  Near the tips it must fall BELOW that -- those parts are
    still stuck -- so a profile pinned at 0.57735 everywhere would be the bug, not the
    result.

The slip sign is reported for both orientations, because which side of the interface is
"primary" is a mesh-generation detail that flips the tangential jump and nothing else.

Usage
-----
Run the decks first (from this directory):

    mpiexec -n 8 ../../../../orca-opt -i frac_intersection_barton_bandis.i

then

    python frac_intersection_analytical.py
    python frac_intersection_analytical.py --no-plot
    python frac_intersection_analytical.py --models barton_bandis compression_tensile

Writes frac_intersection_comparison_summary.csv, frac_intersection_comparison_profile.csv
and one figure per panel (frac_intersection_comparison_aperture.png,
_traction.png, _slip.png) next to itself.  Requires numpy; matplotlib only for the figures.
"""

import argparse
import csv
import glob
import math
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

MODELS = [
    ("barton_bandis", "BBFast", "ADOrcaBartonBandisContactTractionFastADHardening"),
    (
        "compression_tensile",
        "MC",
        "ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile",
    ),
    ("bb_flow_rsf", "BB flow/RSF", "ADOrcaBartonBandisFlowRSFContactTraction"),
    ("peak_shelf_tail", "Peak-shelf-tail", "ADOrcaPeakShelfTailFlowRSFContactTraction"),
]


# --------------------------------------------------------------------------------------
# deck + reference input
# --------------------------------------------------------------------------------------
def deck_constants(deck):
    """Read the top-level benchmark constants straight out of the deck.

    Keeping the script and the deck on one source of truth is the point: a silent
    disagreement between the two is exactly the kind of error a validation script is
    supposed to make impossible.
    """
    text = open(deck).read()
    # Anchor on the block header at column 0 -- the prose above it mentions "[Mesh]"
    # too, and matching that one truncates the header before the constants.
    head = text[: re.search(r"^\[Mesh\]", text, re.M).start()]
    out = {}
    for key in (
        "bulk_modulus",
        "shear_modulus",
        "remote_compression",
        "crack_pressure",
        "friction_angle_deg",
        "half_length_v",
    ):
        m = re.search(rf"^{key}\s*=\s*([0-9.eE+-]+)", head, re.M)
        if not m:
            raise RuntimeError(f"{key} not found in {os.path.basename(deck)}")
        out[key] = float(m.group(1))
    K, G = out["bulk_modulus"], out["shear_modulus"]
    out["youngs_modulus"] = 9.0 * K * G / (3.0 * K + G)
    out["poissons_ratio"] = (3.0 * K - 2.0 * G) / (2.0 * (3.0 * K + G))
    return out


def load_reference():
    """Reference curves, mapped from the files' tip-based arc length onto mesh axes."""
    ap = np.loadtxt(os.path.join(HERE, "Aperture.txt"))
    tn = np.loadtxt(os.path.join(HERE, "NormalTraction.txt"))
    sl = np.loadtxt(os.path.join(HERE, "Slip.txt"))
    ref = {
        # s = 0 sits at the T-junction, so y decreases with s.
        "aperture": (50.0 - ap[:, 0], ap[:, 1]),
        "traction": (tn[:, 0] - 25.0, tn[:, 1]),
        "slip": (sl[:, 0] - 25.0, sl[:, 1]),
    }
    for k, (x, v) in ref.items():
        order = np.argsort(x)
        ref[k] = (x[order], v[order])
    return ref


def last_profile(stem):
    """Newest indexed CSV for a VectorPostprocessor.

    The exact-index match matters: a bare `stem_*` glob also swallows
    `stem_other_*`-style siblings and silently compares the wrong sideset.
    """
    pat = re.compile(re.escape(stem) + r"_\d+\.csv$")
    files = sorted(f for f in glob.glob(stem + "_*.csv") if pat.search(f))
    if not files:
        return None
    for path in reversed(files):
        with open(path, newline="") as fh:
            rows = list(csv.DictReader(fh))
        if len(rows) > 1:
            return path, rows
    return None


# --------------------------------------------------------------------------------------
# comparison
# --------------------------------------------------------------------------------------
def interp_reference(ref_x, ref_v, x, split_at_zero=False):
    """Reference sampled onto `x`.

    `split_at_zero` interpolates the two halves separately.  The slip is discontinuous
    across the junction -- it reverses sign there -- so interpolating straight through
    would invent a ramp between +67 and -67 mm that is in neither solution.
    """
    if not split_at_zero:
        return np.interp(x, ref_x, ref_v)
    out = np.empty_like(x, dtype=float)
    for side in (-1.0, 1.0):
        m_ref = (ref_x * side) > 0.0
        m_x = (x * side) > 0.0
        if m_ref.sum() >= 2 and m_x.any():
            out[m_x] = np.interp(x[m_x], ref_x[m_ref], ref_v[m_ref])
    return out


def score(x, num, ref_x, ref_v, split_at_zero=False):
    """RMS / max-abs error against the reference, plus the same as a % of its span."""
    ref = interp_reference(ref_x, ref_v, x, split_at_zero=split_at_zero)
    err = num - ref
    span = float(ref_v.max() - ref_v.min())
    return {
        "points": len(x),
        "rms": float(np.sqrt(np.mean(err**2))),
        "max_abs": float(np.max(np.abs(err))),
        "span": span,
        "rms_pct": 100.0 * float(np.sqrt(np.mean(err**2))) / span if span else float("nan"),
    }, ref


def read_model(model):
    """Numerical profiles for one material law, in reference units (mm and MPa)."""
    base = os.path.join(HERE, f"frac_intersection_{model}_out")
    got = last_profile(base + "_aperture_profile")
    if got is None:
        return None
    ap_file, ap_rows = got
    got = last_profile(base + "_horizontal_profile")
    if got is None:
        return None
    hz_file, hz_rows = got

    y = np.array([float(r["y"]) for r in ap_rows])
    dn = np.array([float(r["dn_v"]) for r in ap_rows]) * 1.0e3  # m -> mm
    order = np.argsort(y)
    vert = {"y": y[order], "aperture_mm": dn[order], "file": os.path.basename(ap_file)}

    x = np.array([float(r["x"]) for r in hz_rows])
    # The reference reports the normal traction as a positive compression magnitude.
    tn = -np.array([float(r["sigma_n_h"]) for r in hz_rows]) / 1.0e6
    sl = np.array([float(r["ds_h"]) for r in hz_rows]) * 1.0e3
    tau = np.array([float(r["tau_h"]) for r in hz_rows]) / 1.0e6
    # Mobilized friction, recomputed here rather than read from the deck. As a ParsedAux
    # reading two other AuxVariables it was not guaranteed to run after them and silently
    # reported the previous step's ratio; the exported tractions have no such hazard.
    # The 1e3 Pa floor keeps it finite at the junction, where sigma_n is driven to zero.
    mu = np.abs(tau) / (np.abs(tn) + 1.0e-3)
    order = np.argsort(x)
    horiz = {
        "x": x[order],
        "traction_MPa": tn[order],
        "slip_mm": sl[order],
        "shear_MPa": tau[order],
        "mu": mu[order],
        "file": os.path.basename(hz_file),
    }
    return vert, horiz


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.strip().split("\n")[0])
    parser.add_argument("--models", nargs="+", default=[m[0] for m in MODELS])
    parser.add_argument("--no-plot", action="store_true")
    args = parser.parse_args(argv)

    ref = load_reference()

    deck = os.path.join(HERE, f"frac_intersection_{args.models[0]}.i")
    if not os.path.exists(deck):
        print(f"deck not found: {deck}", file=sys.stderr)
        return 1
    const = deck_constants(deck)
    E, nu = const["youngs_modulus"], const["poissons_ratio"]
    b = const["half_length_v"]
    p = const["crack_pressure"]
    mu_expected = math.tan(math.radians(const["friction_angle_deg"]))
    # Isolated pressurized crack, for scale only -- NOT the solution to this problem.
    sneddon_amp_mm = 4.0 * (1.0 - nu**2) * p * b / E * 1.0e3

    print("Two intersecting fractures — Phan et al. (2003) reference comparison\n")
    print(f"  E  = {E/1e9:.4f} GPa      nu = {nu:.5f}      mu = tan(30 deg) = {mu_expected:.5f}")
    print(f"  fluid pressure   {p/1e6:.1f} MPa in the vertical fracture")
    print(f"  far field        sigma_yy = {-const['remote_compression']/1e6:.1f} MPa\n")
    print(f"  isolated-crack (Sneddon) peak aperture   {sneddon_amp_mm:8.3f} mm")
    ref_peak = float(ref["aperture"][1].max())
    print(
        f"  Phan et al. peak aperture                {ref_peak:8.3f} mm"
        f"   ({100*(ref_peak/sneddon_amp_mm-1):+.2f} % vs isolated)\n"
    )

    summary, profile_rows = [], []
    for model, label, material in MODELS:
        if model not in args.models:
            continue
        got = read_model(model)
        if got is None:
            print(f"  {label:16s} no profile output — run the deck first")
            continue
        vert, horiz = got

        s_ap, ref_ap = score(vert["y"], vert["aperture_mm"], *ref["aperture"])
        s_tn, ref_tn = score(horiz["x"], horiz["traction_MPa"], *ref["traction"])
        s_sl, ref_sl = score(horiz["x"], horiz["slip_mm"], *ref["slip"], split_at_zero=True)
        s_sl_flip, _ = score(
            horiz["x"], -horiz["slip_mm"], *ref["slip"], split_at_zero=True
        )
        # Which orientation of the tangential jump matches the reference frame.
        if s_sl_flip["rms"] < s_sl["rms"]:
            slip_sign, s_sl_used, slip_num = "flipped", s_sl_flip, -horiz["slip_mm"]
        else:
            slip_sign, s_sl_used, slip_num = "as-is", s_sl, horiz["slip_mm"]

        # The outermost element at each horizontal-fracture tip carries the usual
        # penalty-contact oscillation; report the interior separately rather than
        # trimming it silently.
        tip = np.abs(horiz["x"]) < 0.9 * float(np.max(np.abs(horiz["x"])))
        s_tn_int, _ = score(
            horiz["x"][tip], horiz["traction_MPa"][tip], *ref["traction"]
        )

        peak_ap = float(vert["aperture_mm"].max())
        # Aperture at the T-junction: the topological check.  A junction node that was
        # not split reports ~0 here instead of ~135 mm.
        junction_ap = float(vert["aperture_mm"][np.argmax(vert["y"])])
        ref_junction = float(np.interp(vert["y"].max(), *ref["aperture"]))

        # Slip antisymmetry, independent of the reference.
        asym = float(
            np.max(np.abs(slip_num + np.interp(-horiz["x"], horiz["x"], slip_num)))
        )
        # Mobilized friction where the fracture actually slides.
        sliding = np.abs(slip_num) > 0.05 * np.max(np.abs(slip_num))
        mu_sliding = float(np.mean(horiz["mu"][sliding])) if sliding.any() else float("nan")

        print(f"  {label:16s} ({material})")
        print(
            f"      aperture (vertical)     rms {s_ap['rms']:7.3f} mm   "
            f"max {s_ap['max_abs']:7.3f} mm   {s_ap['rms_pct']:5.2f} % of span"
        )
        print(
            f"      normal traction (horiz) rms {s_tn['rms']:7.3f} MPa  "
            f"max {s_tn['max_abs']:7.3f} MPa  {s_tn['rms_pct']:5.2f} % of span"
            f"   [interior only {s_tn_int['rms_pct']:5.2f} %]"
        )
        print(
            f"      slip (horizontal)       rms {s_sl_used['rms']:7.3f} mm   "
            f"max {s_sl_used['max_abs']:7.3f} mm   {s_sl_used['rms_pct']:5.2f} % of span"
            f"   [sign {slip_sign}]"
        )
        print(
            f"      peak aperture {peak_ap:8.3f} mm  vs Phan {ref_peak:8.3f}"
            f"  ({100*(peak_ap/ref_peak-1):+6.2f} %)   vs Sneddon ratio {peak_ap/sneddon_amp_mm:.4f}"
        )
        print(
            f"      junction aperture {junction_ap:8.3f} mm  vs Phan {ref_junction:8.3f}"
            f"  ({100*(junction_ap/ref_junction-1):+6.2f} %)"
        )
        print(
            f"      slip antisymmetry residual {asym:.3e} mm      "
            f"mobilized mu where sliding {mu_sliding:.5f} (expected {mu_expected:.5f})"
        )
        print()

        summary.append(
            {
                "model": label,
                "material": material,
                "aperture_rms_mm": s_ap["rms"],
                "aperture_max_abs_mm": s_ap["max_abs"],
                "aperture_rms_pct_of_span": s_ap["rms_pct"],
                "traction_rms_MPa": s_tn["rms"],
                "traction_max_abs_MPa": s_tn["max_abs"],
                "traction_rms_pct_of_span": s_tn["rms_pct"],
                "traction_interior_rms_pct_of_span": s_tn_int["rms_pct"],
                "slip_rms_mm": s_sl_used["rms"],
                "slip_max_abs_mm": s_sl_used["max_abs"],
                "slip_rms_pct_of_span": s_sl_used["rms_pct"],
                "slip_sign_convention": slip_sign,
                "peak_aperture_mm": peak_ap,
                "peak_aperture_reference_mm": ref_peak,
                "peak_aperture_rel_error": peak_ap / ref_peak - 1.0,
                "peak_aperture_over_sneddon": peak_ap / sneddon_amp_mm,
                "sneddon_peak_aperture_mm": sneddon_amp_mm,
                "junction_aperture_mm": junction_ap,
                "junction_aperture_reference_mm": ref_junction,
                "junction_aperture_rel_error": junction_ap / ref_junction - 1.0,
                "slip_antisymmetry_residual_mm": asym,
                "mobilized_mu_sliding": mu_sliding,
                "mobilized_mu_expected": mu_expected,
                "aperture_profile_file": vert["file"],
                "horizontal_profile_file": horiz["file"],
            }
        )

        for yy, num, rr in zip(vert["y"], vert["aperture_mm"], ref_ap):
            profile_rows.append(
                {
                    "model": label,
                    "curve": "aperture_vertical",
                    "coordinate_m": yy,
                    "numerical": num,
                    "reference": rr,
                    "units": "mm",
                }
            )
        for xx, num, rr in zip(horiz["x"], horiz["traction_MPa"], ref_tn):
            profile_rows.append(
                {
                    "model": label,
                    "curve": "normal_traction_horizontal",
                    "coordinate_m": xx,
                    "numerical": num,
                    "reference": rr,
                    "units": "MPa",
                }
            )
        for xx, num, rr in zip(horiz["x"], slip_num, ref_sl):
            profile_rows.append(
                {
                    "model": label,
                    "curve": "slip_horizontal",
                    "coordinate_m": xx,
                    "numerical": num,
                    "reference": rr,
                    "units": "mm",
                }
            )

    if not summary:
        return 1

    out = os.path.join(HERE, "frac_intersection_comparison_summary.csv")
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(summary[0]))
        w.writeheader()
        w.writerows(summary)
    print(f"  wrote {out}")

    out = os.path.join(HERE, "frac_intersection_comparison_profile.csv")
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(profile_rows[0]))
        w.writeheader()
        w.writerows(profile_rows)
    print(f"  wrote {out}")

    if args.no_plot:
        return 0
    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("  matplotlib not available — skipping the figure")
        return 0

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

    # BBFast and MC are the pair this suite compares most often, so they get a
    # pronounced, staggered marker style (open circle vs. filled square, offset
    # sampling) rather than being buried under the flat-marker cycle used for
    # the two extra laws.
    style = {
        "BBFast": dict(marker="o", ms=11.0, mfc="none", mew=1.8, alpha=1.0, markevery=(0, 2)),
        "MC": dict(marker="s", ms=8.0, mfc="tab:orange", mec="tab:orange", mew=0.0, alpha=0.9,
                   markevery=(1, 2)),
        "BB flow/RSF": dict(marker="^", ms=6.0, mfc="none", alpha=0.7),
        "Peak-shelf-tail": dict(marker="v", ms=5.0, mfc="none", alpha=0.7),
    }

    panels = [
        ("aperture_vertical", "vertical fracture position $y$  (m)", "aperture  (mm)",
         "Vertical fracture — aperture", "aperture"),
        ("normal_traction_horizontal", "horizontal fracture position $x$  (m)",
         "normal traction  (MPa)", "Horizontal fracture — normal traction", "traction"),
        ("slip_horizontal", "horizontal fracture position $x$  (m)", "slip  (mm)",
         "Horizontal fracture — slip", "slip"),
    ]
    paths = []
    for curve, xlabel, ylabel, title, stem in panels:
        fig, ax = plt.subplots(figsize=(9.0, 7.5))
        key = {"aperture_vertical": "aperture", "normal_traction_horizontal": "traction",
               "slip_horizontal": "slip"}[curve]
        rx, rv = ref[key]
        if key == "slip":
            for side in (-1.0, 1.0):
                m = (rx * side) > 0
                ax.plot(rx[m], rv[m], "-", color="0.25", lw=2.5,
                        label="Phan et al. (2003)" if side < 0 else None)
        else:
            ax.plot(rx, rv, "-", color="0.25", lw=2.5, label="Phan et al. (2003)")
        for model, label, _ in MODELS:
            rows = [r for r in profile_rows if r["model"] == label and r["curve"] == curve]
            if not rows:
                continue
            ax.plot(
                [r["coordinate_m"] for r in rows],
                [r["numerical"] for r in rows],
                ls="none",
                label=f"Orca — {label}",
                **style.get(label, dict(marker="o", ms=4, mfc="none", alpha=0.65)),
            )
        if key == "aperture":
            yy = np.linspace(-b, b, 201)
            ax.plot(yy, sneddon_amp_mm * np.sqrt(np.maximum(b**2 - yy**2, 0.0)) / b,
                    "--", color="tab:red", lw=1.2, label="Sneddon (isolated crack)")
        ax.set_xlabel(xlabel)
        ax.set_ylabel(ylabel)
        ax.set_title(title)
        ax.grid(alpha=0.3)
        ax.legend(frameon=False)
        fig.tight_layout()
        out = os.path.join(HERE, f"frac_intersection_comparison_{stem}.png")
        fig.savefig(out, dpi=600)
        plt.close(fig)
        print(f"  wrote {out}")
        paths.append(out)
    return 0


if __name__ == "__main__":
    sys.exit(main())
