"""
Single inclined fracture under far-field compression — analytical solution and
MOOSE comparison.

Problem
-------
A fracture of half-length b, inclined at psi to the direction of a remote
uniaxial compression sigma, is embedded in an infinite linear-elastic medium of
Young's modulus E and Poisson's ratio nu.  The fracture stays closed and slides
frictionally with friction angle theta, giving

    g_t(s) = 4 (1 - nu^2) / E * sigma sin(psi) [cos(psi) - sin(psi) tan(theta)]
             * sqrt(b^2 - s^2)

    sigma_n = -sigma sin^2(psi)                        (tension positive)

so the maximum (mid-fracture) slip is

    g_t,max = 4 (1 - nu^2) b sigma sin(psi) [cos(psi) - sin(psi) tan(theta)] / E

Unlike Sneddon, the interface here is closed and sliding, so the Coulomb return
map is the mechanism under test: the amplitude depends on the friction
coefficient through the [cos psi - sin psi tan theta] driving term.  Getting it
right requires the yield surface, the contact normal stress and the slip
direction all to be correct.

Configuration follows the GEOS validation case:
  geosx-geosx.readthedocs-hosted.com/en/latest/docs/sphinx/advancedExamples/
  validationStudies/faultMechanics/singleFracCompression/Example.html

The inclination is measured from the mesh, not assumed
------------------------------------------------------
sigma_n = -sigma sin^2(psi) is pure statics.  It does not depend on the friction
law, on the constitutive model, or (in the mean) on mesh resolution, so a large
error in the computed normal stress can only mean the fracture is not inclined
at the angle the closed form was evaluated at.

This script therefore does not take psi on faith.  It measures the inclination
and the half-length from the sampled fracture geometry, and reports the closed
form evaluated at BOTH the deck-declared geometry and the as-meshed geometry.
When the two disagree the difference is stated explicitly rather than being
absorbed into a "model error".

Usage
-----
Run the decks first (from this directory):

    mpiexec -n 8 ../../../../orca-opt -i shear_compression_barton_bandis.i
    mpiexec -n 8 ../../../../orca-opt -i shear_compression_compression_tensile.i

then

    python shear_compression_analytical.py               # BBFast and MC
    python shear_compression_analytical.py --all         # all four interface laws
    python shear_compression_analytical.py --no-plot     # CSV only

Requires numpy and matplotlib only (no scipy), so it runs under either the
`moose` environment or the base miniforge python.  netCDF4 is used if available
to read the fracture half-length straight from the mesh, and the script falls
back to the sampled extent when it is not.

Outputs, written next to this script:
    shear_compression_comparison_summary.csv     per law: scalars, errors, shape fit
    shear_compression_comparison_profile.csv     s, analytic and numerical slip
    shear_compression_comparison_slip.png        profile overlay
    shear_compression_comparison_residual.png    numerical - analytic error
    shear_compression_comparison_sigma_n.png     normal stress
"""

import argparse
import csv
import glob
import math
import os
import re
import sys

import numpy as np

# --------------------------------------------------------------------------
# Benchmark parameters, mirroring the decks.
# --------------------------------------------------------------------------
BULK_MODULUS = 16.66666666666666e9  # Pa
SHEAR_MODULUS = 1.0e10  # Pa
YOUNGS_MODULUS = 9.0 * BULK_MODULUS * SHEAR_MODULUS / (3.0 * BULK_MODULUS + SHEAR_MODULUS)
POISSONS_RATIO = (3.0 * BULK_MODULUS - 2.0 * SHEAR_MODULUS) / (
    2.0 * (3.0 * BULK_MODULUS + SHEAR_MODULUS)
)
REMOTE_COMPRESSION = 1.0e8  # Pa, applied along x
FRICTION_ANGLE_DEG = 30.0

# Geometry as declared in the deck.  measure_geometry() reads what the mesh
# actually contains; the two are reported side by side.
DECK_INCLINATION_DEG = 20.0
DECK_HALF_LENGTH = 1.0

# The mesh is discovered from the deck rather than hard-coded: the decks were
# repointed at a corrected mesh on 2026-09-02, and a hard-coded path here would
# have gone on reporting the half-length of the superseded file.
MESH_FALLBACK = os.path.join("mesh", "single_fracture_under_shear_compression_mesh.e")
FRACTURE_NODESET = "fracture_interface"


def deck_mesh_path(directory, suffix="barton_bandis"):
    """The mesh file the deck actually loads, resolved against `directory`."""
    deck = os.path.join(directory, f"shear_compression_{suffix}.i")
    if os.path.exists(deck):
        m = re.search(r"^\s*file\s*=\s*(\S+\.e)\s*$", open(deck).read(), re.M)
        if m:
            return os.path.join(directory, m.group(1))
    return os.path.join(directory, MESH_FALLBACK)

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


# --------------------------------------------------------------------------
# Closed form
# --------------------------------------------------------------------------
def driving_stress(psi_deg, sigma=REMOTE_COMPRESSION, theta_deg=FRICTION_ANGLE_DEG):
    """sigma sin(psi) [cos(psi) - sin(psi) tan(theta)]."""
    psi = math.radians(psi_deg)
    theta = math.radians(theta_deg)
    return sigma * math.sin(psi) * (math.cos(psi) - math.sin(psi) * math.tan(theta))


def slip_amplitude(psi_deg, E=YOUNGS_MODULUS, nu=POISSONS_RATIO, **kw):
    """A in g_t(s) = A * sqrt(b^2 - s^2)."""
    return 4.0 * (1.0 - nu**2) * driving_stress(psi_deg, **kw) / E


def slip_profile(s, psi_deg, b, **kw):
    """Frictional slip profile g_t(s).  Zero outside the fracture."""
    s = np.asarray(s, dtype=float)
    inside = np.abs(s) <= b
    g = np.zeros_like(s)
    g[inside] = slip_amplitude(psi_deg, **kw) * np.sqrt(b**2 - s[inside] ** 2)
    return g


def max_slip(psi_deg, b, **kw):
    """g_t,max = A * b."""
    return slip_amplitude(psi_deg, **kw) * b


def normal_stress(psi_deg, sigma=REMOTE_COMPRESSION):
    """sigma_n = -sigma sin^2(psi), tension positive."""
    return -sigma * math.sin(math.radians(psi_deg)) ** 2


# --------------------------------------------------------------------------
# Reading MOOSE output
# --------------------------------------------------------------------------
def _read_csv(path):
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
    path = os.path.join(directory, f"shear_compression_{suffix}_out.csv")
    if not os.path.exists(path):
        return None
    data = _read_csv(path)
    if not data:
        return None
    return {k: v[-1] for k, v in data.items()}


def read_profile(directory, suffix):
    """
    Slip profile from the last non-empty slip_profile CSV.

    The fracture is inclined and passes through the origin, so the along-fracture
    coordinate is s = sign(x) * hypot(x, y).  Header-only files are skipped:
    that is what the whole suite produced while the sampler was set to
    `execute_on = FINAL`.
    """
    pattern = os.path.join(
        directory, f"shear_compression_{suffix}_out_slip_profile_*.csv"
    )
    for path in sorted(glob.glob(pattern), reverse=True):
        data = _read_csv(path)
        if not data or len(next(iter(data.values()))) <= 1:
            continue
        x, y = data["x"], data["y"]
        s = np.sign(x) * np.hypot(x, y)
        order = np.argsort(s)
        return {
            "path": os.path.basename(path),
            "s": s[order],
            "x": x[order],
            "y": y[order],
            "slip": data["czm_slip_out"][order],
            "sigma_n": data["czm_sigma_n_out"][order],
            "opening": data["crack_opening"][order],
        }
    return None


# --------------------------------------------------------------------------
# Geometry, measured rather than assumed
# --------------------------------------------------------------------------
def measure_geometry(directory, profile):
    """
    Return (psi_deg, half_length, source) for the fracture as actually meshed.

    The inclination comes from the sampled points, which are exactly collinear
    and pass through the origin, so it is exact and needs no extra dependency.
    The half-length comes from the mesh nodeset when netCDF4 is importable —
    quadrature points sit inside the elements and so under-report the tips by
    half an element — and otherwise falls back to the sampled extent.
    """
    psi = None
    if profile is not None:
        x, y = profile["x"], profile["y"]
        span = np.argmax(x) if len(x) else 0
        # slope through the collinear sample points
        slope = np.polyfit(x, y, 1)[0]
        psi = abs(math.degrees(math.atan(slope)))
        sampled_half = float(np.max(np.abs(profile["s"])))
    else:
        sampled_half = float("nan")

    mesh_path = deck_mesh_path(directory)
    if os.path.exists(mesh_path):
        try:
            import netCDF4

            with netCDF4.Dataset(mesh_path) as ds:
                # Exodus pads name records with NULs.  Masking is disabled first
                # so the padding arrives as bytes rather than as masked entries,
                # which stringify to "-" and would corrupt every name.
                ds.set_auto_mask(False)
                names = [
                    b"".join(row).split(b"\x00")[0].decode().strip()
                    for row in ds.variables["ns_names"][:]
                ]
                idx = names.index(FRACTURE_NODESET) + 1
                nodes = ds.variables[f"node_ns{idx}"][:] - 1
                nx = np.asarray(ds.variables["coordx"][:])[nodes]
                ny = np.asarray(ds.variables["coordy"][:])[nodes]
                half = 0.5 * math.hypot(nx.max() - nx.min(), ny.max() - ny.min())
                if psi is None:
                    psi = abs(math.degrees(math.atan2(ny.max() - ny.min(),
                                                      nx.max() - nx.min())))
                return psi, half, f"mesh nodeset of {os.path.basename(mesh_path)}"
        except Exception:
            pass

    return psi, sampled_half, "sampled quadrature points (tips under-reported)"


def fit_ellipse(s, g, tip_exclusion=0.10):
    """
    Recover (amplitude, half_length) from a numerical profile.

    g^2 = A^2 b^2 - A^2 s^2 is linear in s^2, so a straight-line regression of
    g^2 on s^2 gives both without a non-linear solver.  Tip points are dropped
    because the closed form is singular there and the tip elements would
    otherwise dominate the fit.
    """
    s = np.asarray(s, float)
    g = np.asarray(g, float)
    keep = (np.abs(s) <= (1.0 - tip_exclusion) * np.max(np.abs(s))) & (g > 0.0)
    if keep.sum() < 3:
        return float("nan"), float("nan")
    slope, intercept = np.polyfit(s[keep] ** 2, g[keep] ** 2, 1)
    if slope >= 0.0 or intercept <= 0.0:
        return float("nan"), float("nan")
    amplitude = math.sqrt(-slope)
    return amplitude, math.sqrt(intercept / amplitude**2)


def verify_deck_parameters(directory, suffix="barton_bandis"):
    """Report any drift between this script's constants and the deck's."""
    path = os.path.join(directory, f"shear_compression_{suffix}.i")
    if not os.path.exists(path):
        return []
    text = open(path).read()
    expected = {
        "bulk_modulus": BULK_MODULUS,
        "shear_modulus": SHEAR_MODULUS,
        "remote_compression": REMOTE_COMPRESSION,
        "inclination_deg": DECK_INCLINATION_DEG,
        "friction_angle_deg": FRICTION_ANGLE_DEG,
        "half_length": DECK_HALF_LENGTH,
    }
    problems = []
    for name, want in expected.items():
        m = re.search(rf"^{name}\s*=\s*([0-9eE.+-]+)\s*(?:#.*)?$", text, re.M)
        if not m:
            problems.append(f"{name}: not found in {os.path.basename(path)}")
            continue
        got = float(m.group(1))
        if not np.isclose(got, want, rtol=1e-9):
            problems.append(f"{name}: deck has {got:g}, this script uses {want:g}")
    return problems


# --------------------------------------------------------------------------
# Comparison
# --------------------------------------------------------------------------
def compare(directory, models, geom):
    psi_mesh, b_mesh, _ = geom
    summary = []
    profiles = {}

    for label, suffix in models.items():
        scalars = read_scalars(directory, suffix)
        profile = read_profile(directory, suffix)
        if scalars is None and profile is None:
            print(f"  {label:16s} no output found (deck not run?)", file=sys.stderr)
            continue

        rec = {
            "model": label,
            "material": MODEL_MATERIAL.get(label, ""),
            "slip_max_analytic_deck_m": max_slip(DECK_INCLINATION_DEG, DECK_HALF_LENGTH),
            "slip_max_analytic_mesh_m": max_slip(psi_mesh, b_mesh),
            "sigma_n_analytic_deck_Pa": normal_stress(DECK_INCLINATION_DEG),
            "sigma_n_analytic_mesh_Pa": normal_stress(psi_mesh),
        }

        if scalars is not None:
            slip = scalars.get("slip_max", float("nan"))
            sig = scalars.get("sigma_n_mean", float("nan"))
            rec["slip_max_numerical_m"] = slip
            rec["slip_max_rel_error_deck"] = abs(
                slip - rec["slip_max_analytic_deck_m"]
            ) / rec["slip_max_analytic_deck_m"]
            rec["slip_max_rel_error_mesh"] = abs(
                slip - rec["slip_max_analytic_mesh_m"]
            ) / rec["slip_max_analytic_mesh_m"]
            rec["sigma_n_numerical_Pa"] = sig
            rec["sigma_n_rel_error_deck"] = abs(
                sig - rec["sigma_n_analytic_deck_Pa"]
            ) / abs(rec["sigma_n_analytic_deck_Pa"])
            rec["sigma_n_rel_error_mesh"] = abs(
                sig - rec["sigma_n_analytic_mesh_Pa"]
            ) / abs(rec["sigma_n_analytic_mesh_Pa"])
            rec["opening_max_m"] = scalars.get("opening_max", float("nan"))

        if profile is not None:
            s, g = profile["s"], profile["slip"]
            g_mesh = slip_profile(s, psi_mesh, b_mesh)
            resid = g - g_mesh
            rec["profile_points"] = len(s)
            rec["profile_source"] = profile["path"]
            rec["profile_rms_error_m"] = float(np.sqrt(np.mean(resid**2)))
            rec["profile_rms_rel_error_mesh"] = float(
                np.sqrt(np.mean(resid**2)) / max_slip(psi_mesh, b_mesh)
            )
            amp, b_fit = fit_ellipse(s, g)
            rec["fitted_amplitude"] = amp
            rec["fitted_amplitude_analytic_deck"] = slip_amplitude(DECK_INCLINATION_DEG)
            rec["fitted_amplitude_analytic_mesh"] = slip_amplitude(psi_mesh)
            rec["fitted_amplitude_rel_error_deck"] = abs(
                amp / slip_amplitude(DECK_INCLINATION_DEG) - 1.0
            )
            rec["fitted_amplitude_rel_error_mesh"] = abs(
                amp / slip_amplitude(psi_mesh) - 1.0
            )
            rec["fitted_half_length_m"] = b_fit
            profiles[label] = profile

        summary.append(rec)

    return summary, profiles


def write_summary(directory, summary):
    path = os.path.join(directory, "shear_compression_comparison_summary.csv")
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


def write_profiles(directory, profiles, geom):
    if not profiles:
        return None
    psi_mesh, b_mesh, _ = geom
    path = os.path.join(directory, "shear_compression_comparison_profile.csv")
    grid = next(iter(profiles.values()))["s"]
    g_deck = slip_profile(grid, DECK_INCLINATION_DEG, DECK_HALF_LENGTH)
    g_mesh = slip_profile(grid, psi_mesh, b_mesh)
    header = ["s_m", "slip_analytic_deck_geometry_m", "slip_analytic_mesh_geometry_m"]
    cols = [grid, g_deck, g_mesh]
    for lbl, p in profiles.items():
        header.append(f"slip_{lbl}_m")
        cols.append(np.interp(grid, p["s"], p["slip"]))
    for lbl, p in profiles.items():
        header.append(f"err_vs_mesh_geometry_{lbl}_m")
        cols.append(np.interp(grid, p["s"], p["slip"]) - g_mesh)
    for lbl, p in profiles.items():
        header.append(f"sigma_n_{lbl}_Pa")
        cols.append(np.interp(grid, p["s"], p["sigma_n"]))
    with open(path, "w", newline="") as fh:
        writer = csv.writer(fh)
        writer.writerow(header)
        writer.writerows(np.column_stack(cols))
    return path


def plot(directory, profiles, geom):
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

    # BBFast is an open blue circle, MC a filled orange square, and the two
    # series' points are staggered (opposite markevery phase) so the shape
    # difference stays visible instead of one marker hiding under the other.
    style = {
        "BBFast": dict(marker="o", ms=11.0, mfc="none", mew=1.8, markevery=(0, 2)),
        "MC": dict(marker="s", ms=8.0, mfc="tab:orange", mec="tab:orange", mew=0.0, alpha=0.9,
                   markevery=(1, 2)),
        "BB flow/RSF": dict(marker="^", ms=6.0, mfc="none", alpha=0.7),
        "Peak-shelf-tail": dict(marker="v", ms=5.0, mfc="none", alpha=0.7),
    }

    psi_mesh, b_mesh, _ = geom
    default_style = dict(marker="o", ms=4.5, mfc="none", alpha=0.65)

    s_fine = np.linspace(-b_mesh, b_mesh, 400)
    s_deck = np.linspace(-DECK_HALF_LENGTH, DECK_HALF_LENGTH, 400)

    paths = []

    fig, ax = plt.subplots(figsize=(10.0, 7.5))
    ax.plot(
        s_fine,
        slip_profile(s_fine, psi_mesh, b_mesh) * 1e3,
        "k-",
        lw=2.0,
        label=f"analytic, as-meshed  ($\\psi$={psi_mesh:.3f}°, $b$={b_mesh:.4f} m)",
    )
    ax.plot(
        s_deck,
        slip_profile(s_deck, DECK_INCLINATION_DEG, DECK_HALF_LENGTH) * 1e3,
        "--",
        color="0.55",
        lw=1.6,
        label=f"analytic, deck constants  ($\\psi$={DECK_INCLINATION_DEG:g}°, $b$={DECK_HALF_LENGTH:g} m)",
    )
    for label, p in profiles.items():
        ax.plot(p["s"], p["slip"] * 1e3, ls="none", label=label, **style.get(label, default_style))
    ax.set_xlabel("distance along fracture $s$  (m)")
    ax.set_ylabel("tangential slip $g_t$  (mm)")
    ax.set_title(
        "Inclined fracture under compression\n"
        f"$E$={YOUNGS_MODULUS/1e9:g} GPa,  $\\nu$={POISSONS_RATIO:g},  "
        f"$\\sigma$={REMOTE_COMPRESSION/1e6:g} MPa,  $\\theta$={FRICTION_ANGLE_DEG:g}°",
        fontsize=16,
    )
    ax.legend(frameon=False)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    path = os.path.join(directory, "shear_compression_comparison_slip.png")
    fig.savefig(path, dpi=600)
    plt.close(fig)
    paths.append(path)

    fig_e, axe = plt.subplots(figsize=(10.0, 7.5))
    for label, p in profiles.items():
        axe.plot(
            p["s"],
            (p["slip"] - slip_profile(p["s"], psi_mesh, b_mesh)) * 1e6,
            ls="none",
            label=label,
            **style.get(label, default_style),
        )
    axe.axhline(0.0, color="k", lw=0.8)
    axe.set_xlabel("distance along fracture $s$  (m)")
    axe.set_ylabel(r"numerical $-$ analytic (as-meshed, $\mu$m)")
    axe.legend(frameon=False)
    axe.grid(alpha=0.3)
    fig_e.tight_layout()
    path_e = os.path.join(directory, "shear_compression_comparison_residual.png")
    fig_e.savefig(path_e, dpi=600)
    plt.close(fig_e)
    paths.append(path_e)

    fig_n, axn = plt.subplots(figsize=(10.0, 7.5))
    for label, p in profiles.items():
        axn.plot(p["s"], p["sigma_n"] / 1e6, ls="none", label=label, **style.get(label, default_style))
    axn.axhline(
        normal_stress(psi_mesh) / 1e6,
        color="k",
        lw=1.6,
        label=f"analytic as-meshed  {normal_stress(psi_mesh)/1e6:.2f} MPa",
    )
    axn.axhline(
        normal_stress(DECK_INCLINATION_DEG) / 1e6,
        color="0.55",
        ls="--",
        lw=1.4,
        label=f"analytic deck  {normal_stress(DECK_INCLINATION_DEG)/1e6:.2f} MPa",
    )
    axn.set_xlabel("distance along fracture $s$  (m)")
    axn.set_ylabel(r"$\sigma_n$  (MPa)")
    axn.legend(frameon=False)
    axn.grid(alpha=0.3)
    fig_n.tight_layout()
    path_n = os.path.join(directory, "shear_compression_comparison_sigma_n.png")
    fig_n.savefig(path_n, dpi=600)
    plt.close(fig_n)
    paths.append(path_n)

    return paths


def report(summary, geom):
    psi_mesh, b_mesh, source = geom
    print()
    print(f"  geometry as meshed : psi = {psi_mesh:.5f} deg, b = {b_mesh:.6f} m  [{source}]")
    print(f"  geometry in deck   : psi = {DECK_INCLINATION_DEG:.5f} deg, b = {DECK_HALF_LENGTH:.6f} m")
    if abs(psi_mesh - DECK_INCLINATION_DEG) > 1e-3:
        print()
        print("  *** The deck's declared inclination is not the meshed inclination. ***")
        print(f"      analytic g_t,max   deck {max_slip(DECK_INCLINATION_DEG, DECK_HALF_LENGTH):.6e} m"
              f"   as-meshed {max_slip(psi_mesh, b_mesh):.6e} m")
        print(f"      analytic sigma_n   deck {normal_stress(DECK_INCLINATION_DEG):.6e} Pa"
              f"   as-meshed {normal_stress(psi_mesh):.6e} Pa")
    print()

    head = (
        f"  {'model':16s} {'slip_max (m)':>14s} {'err/deck':>9s} {'err/mesh':>9s} "
        f"{'sig_n (MPa)':>12s} {'err/deck':>9s} {'err/mesh':>9s} {'fitA/mesh':>10s}"
    )
    print(head)
    print("  " + "-" * (len(head) - 2))
    for rec in summary:
        print(
            f"  {rec['model']:16s} "
            f"{rec.get('slip_max_numerical_m', float('nan')):14.6e} "
            f"{rec.get('slip_max_rel_error_deck', float('nan')) * 100:8.3f}% "
            f"{rec.get('slip_max_rel_error_mesh', float('nan')) * 100:8.3f}% "
            f"{rec.get('sigma_n_numerical_Pa', float('nan')) / 1e6:12.4f} "
            f"{rec.get('sigma_n_rel_error_deck', float('nan')) * 100:8.3f}% "
            f"{rec.get('sigma_n_rel_error_mesh', float('nan')) * 100:8.3f}% "
            f"{rec.get('fitted_amplitude_rel_error_mesh', float('nan')) * 100:9.3f}%"
        )
    print()
    print("  'err/deck' compares against the closed form at the deck's declared psi and b;")
    print("  'err/mesh' compares against the closed form at the geometry actually meshed.")
    print("  'fitA/mesh' is the shape-fit amplitude against the as-meshed closed form and")
    print("  is the cleanest single number: it is independent of the tip discretization.")
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

    print(f"Shear-compression benchmark comparison — reading {args.dir}")

    problems = verify_deck_parameters(args.dir)
    if problems:
        print("\n  WARNING: this script and the deck disagree:", file=sys.stderr)
        for p in problems:
            print(f"    {p}", file=sys.stderr)
        print(file=sys.stderr)

    reference = read_profile(args.dir, MODELS["BBFast"]) or read_profile(
        args.dir, MODELS["MC"]
    )
    geom = measure_geometry(args.dir, reference)
    if geom[0] is None:
        print(
            "Cannot determine the fracture geometry: no profile output and no mesh.",
            file=sys.stderr,
        )
        return 1

    summary, profiles = compare(args.dir, models, geom)
    if not summary:
        print("No MOOSE output found. Run the decks first.", file=sys.stderr)
        return 1

    report(summary, geom)
    print(f"  wrote {write_summary(args.dir, summary)}")
    p = write_profiles(args.dir, profiles, geom)
    if p:
        print(f"  wrote {p}")
    if not args.no_plot and profiles:
        for path in plot(args.dir, profiles, geom):
            print(f"  wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
