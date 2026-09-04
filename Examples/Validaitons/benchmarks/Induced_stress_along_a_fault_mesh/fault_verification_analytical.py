"""
Induced stresses along a fault bounding a pressurized, displaced reservoir —
comparison against the Wu et al. (2020) reference solution.

Problem
-------
A 300 m thick reservoir is cut by a normal fault dipping at 60 deg with a 100 m
vertical offset, so the two compartments overlap only partly:

    sampled compartment  (x > x_fault):   z = -100 .. +200 m   [up-thrown]
    opposite compartment (x < x_fault):   z = -200 .. +100 m   [down-thrown]

These are the two halves of the mesh's `fracture_block`, which is the reservoir;
`offset_top` and `offset_bottom` are the non-reservoir blocks juxtaposed against
it by the 100 m throw, not part of it.
    fault:  x_fault(z) = tan(30 deg) * z

Raising the pore pressure by 20 MPa makes a compartment expand, and that
deformation perturbs the stress on the fault plane.  Two cases are run: an
impermeable fault, where only the opposite compartment is pressurized, and a
permeable fault, where both are.

The fault is NOT a mechanical interface here — it carries no contact or friction
in the reference case either.  This benchmark exercises the poroelastic coupling,
not the contact law, which is what makes it complementary to `sneddon/` and
`shear_compression/`.

Reference: GEOS validation case
  geosx-geosx.readthedocs-hosted.com/en/latest/docs/sphinx/advancedExamples/
  validationStudies/faultMechanics/faultVerification/Example.html
whose reference curve `AnalyticalSolution.txt` is reproduced verbatim here.

What is compared
----------------
The change in TOTAL stress, tension positive, in MPa:

    d sigma_xx = d sigma'_xx - alpha * dp
    d sigma_zz = d sigma'_zz - alpha * dp
    d sigma_xz = d sigma'_xz                (shear carries no pressure term)

The decks solve the perturbation problem directly — zero initial stress, only the
pressure change applied — so the computed stress *is* d sigma', and the decks
already subtract alpha*dp.  This script only reorders and averages.

Axis convention.  The reference file uses y for the vertical axis and x-y for the
dip plane; this mesh uses z for vertical and y for the out-of-plane direction:

    reference  x  y  xy      <->      this mesh  x  z  xz

Two independent checks are reported besides the pointwise error:

  * `d sigma_xx + d sigma_zz` must equal `-alpha dp (1-2nu)/(1-nu)` = -14.824 MPa
    wherever the sampled column sits inside a pressurized layer, and zero
    elsewhere.  That is the one-dimensional limit of the closed form, it is exact,
    and it fixes both the sign convention and the Biot coefficient.
  * the shear component is checked with both signs, because a left-right mirror
    between this mesh and the reference one would flip it and nothing else.  The
    script reports which orientation matches rather than assuming.

Usage
-----
Run the decks first (from this directory):

    mpiexec -n 8 ../../../../orca-opt -i fault_verification_impermeable.i
    mpiexec -n 8 ../../../../orca-opt -i fault_verification_permeable.i

then

    python fault_verification_analytical.py
    python fault_verification_analytical.py --no-plot

Requires numpy and matplotlib only.

Outputs, written next to this script:
    fault_verification_comparison_summary.csv   per case and component: errors
    fault_verification_comparison_profile.csv   depth, reference and computed
    fault_verification_comparison_xx.png        d sigma_xx profile figure
    fault_verification_comparison_zz.png        d sigma_zz profile figure
    fault_verification_comparison_xz.png        d sigma_xz profile figure
"""

import argparse
import csv
import glob
import os
import re
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))

# --- benchmark parameters, mirroring the decks ---
YOUNGS_MODULUS = 14.95e9
POISSONS_RATIO = 0.15
GRAIN_BULK_MODULUS = 7.12e10
BULK_MODULUS = YOUNGS_MODULUS / (3.0 * (1.0 - 2.0 * POISSONS_RATIO))
BIOT = 1.0 - BULK_MODULUS / GRAIN_BULK_MODULUS
PRESSURE_BUILDUP = 20.0e6

# The exact 1-D limit inside a laterally extensive pressurized layer.
UNIAXIAL_SUM_MPA = (
    -BIOT * PRESSURE_BUILDUP * (1.0 - 2.0 * POISSONS_RATIO) / (1.0 - POISSONS_RATIO) / 1e6
)

REFERENCE_FILE = os.path.join(HERE, "AnalyticalSolution.txt")
CASES = {"impermeable": "imp", "permeable": "per"}

# Reference-file column order:
#   distance, SigXXper, SigYYper, SigXYper, SigXXimp, SigYYimp, SigXYimp
REF_COLUMNS = {
    "permeable": {"xx": 1, "zz": 2, "xz": 3},
    "impermeable": {"xx": 4, "zz": 5, "xz": 6},
}

COMPONENTS = [
    ("xx", "dtotal_xx", r"$\Delta\sigma_{xx}$"),
    ("zz", "dtotal_zz", r"$\Delta\sigma_{zz}$"),
    ("xz", "dstress_xz", r"$\Delta\sigma_{xz}$"),
]


def read_reference():
    """Depth and the six reference stress columns, in MPa."""
    if not os.path.exists(REFERENCE_FILE):
        return None
    data = np.loadtxt(REFERENCE_FILE, skiprows=1)
    return data


def read_profile(case):
    """
    Collapse the sampled column to one value per depth.

    The band is one element wide but 60 elements deep in the out-of-plane
    direction; under plane strain those 60 values are identical, so averaging
    them is exact and the spread is reported as a plane-strain check.
    """
    # Exact match: `fault_profile_*` would also catch `fault_profile_other_*`,
    # which is the diagnostic band on the far side of the fault.
    stem = os.path.join(HERE, f"fault_verification_{case}_out_fault_profile_")
    paths = [p for p in glob.glob(stem + "*.csv")
             if re.fullmatch(re.escape(stem) + r"\d+\.csv", p)]
    for path in sorted(paths, reverse=True):
        with open(path, newline="") as fh:
            rows = list(csv.DictReader(fh))
        if len(rows) <= 1:
            continue
        cols = {k: np.array([float(r[k]) for r in rows]) for k in rows[0]}
        # Group by depth level.  Centroid z values repeat exactly per level but
        # carry the usual float noise, so group on the rounded value rather than
        # testing equality against it.  Levels outside the reference range are
        # dropped rather than extrapolated.
        z_rounded = np.round(cols["z"], 3)
        depths = np.array([d for d in np.unique(z_rounded) if abs(d) <= 300.0])
        out = {"path": os.path.basename(path), "z": depths, "spread": {}}
        for key in ("dtotal_xx", "dtotal_zz", "dstress_xz", "delta_p"):
            if key not in cols:
                continue
            means, spreads = [], []
            for d in depths:
                sel = z_rounded == d
                v = cols[key][sel]
                means.append(v.mean())
                spreads.append(v.max() - v.min())
            out[key] = np.array(means) / 1e6  # Pa -> MPa
            out["spread"][key] = float(np.max(spreads)) / 1e6
        return out
    return None


def compare(case, prof, ref):
    """Pointwise comparison of one case against the reference, per component."""
    z = prof["z"]
    y_ref = ref[:, 0]
    records = []
    for key, varname, _ in COMPONENTS:
        if varname not in prof:
            continue
        num = prof[varname]
        ana = np.interp(z, y_ref, ref[:, REF_COLUMNS[case][key]])
        resid = num - ana
        span = float(np.max(ref[:, REF_COLUMNS[case][key]]) - np.min(ref[:, REF_COLUMNS[case][key]]))
        rec = {
            "case": case,
            "component": key,
            "points": len(z),
            "rms_error_MPa": float(np.sqrt(np.mean(resid**2))),
            "max_abs_error_MPa": float(np.max(np.abs(resid))),
            "reference_span_MPa": span,
            "rms_error_pct_of_span": float(np.sqrt(np.mean(resid**2)) / span * 100.0),
            "out_of_plane_spread_MPa": prof["spread"].get(varname, float("nan")),
        }
        if key == "xz":
            flipped = -num - ana
            rec["rms_error_flipped_MPa"] = float(np.sqrt(np.mean(flipped**2)))
        records.append(rec)
    return records


def check_uniaxial_limit(prof):
    """
    d sigma_xx + d sigma_zz must be -14.824 MPa where the sampled column is inside
    a pressurized layer and 0 where it is not.  Exact, and independent of the
    reference file.
    """
    if "dtotal_xx" not in prof or "delta_p" not in prof:
        return None
    total = prof["dtotal_xx"] + prof["dtotal_zz"]
    pressurized = prof["delta_p"] > 0.5 * PRESSURE_BUILDUP / 1e6
    out = {"n_pressurized": int(pressurized.sum()), "n_dry": int((~pressurized).sum())}
    if pressurized.any():
        out["sum_in_layer_MPa"] = float(np.mean(total[pressurized]))
        out["sum_in_layer_expected_MPa"] = UNIAXIAL_SUM_MPA
    if (~pressurized).any():
        out["sum_outside_MPa"] = float(np.mean(total[~pressurized]))
    return out


def write_summary(records):
    path = os.path.join(HERE, "fault_verification_comparison_summary.csv")
    fields = []
    for r in records:
        for k in r:
            if k not in fields:
                fields.append(k)
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=fields)
        w.writeheader()
        w.writerows(records)
    return path


def write_profiles(profiles, ref):
    path = os.path.join(HERE, "fault_verification_comparison_profile.csv")
    rows = []
    for case, prof in profiles.items():
        for i, z in enumerate(prof["z"]):
            row = {"case": case, "z_m": z, "delta_p_MPa": prof["delta_p"][i]}
            for key, varname, _ in COMPONENTS:
                if varname not in prof:
                    continue
                row[f"num_{key}_MPa"] = prof[varname][i]
                row[f"ref_{key}_MPa"] = float(
                    np.interp(z, ref[:, 0], ref[:, REF_COLUMNS[case][key]])
                )
            rows.append(row)
    with open(path, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    return path


def plot(profiles, ref):
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

    colors = {"impermeable": "tab:orange", "permeable": "tab:green"}
    markers = {"impermeable": "o", "permeable": "s"}
    stems = {"xx": "xx", "zz": "zz", "xz": "xz"}

    paths = []
    for key, varname, label in COMPONENTS:
        fig, ax = plt.subplots(figsize=(9.0, 7.5))
        for case, prof in profiles.items():
            ax.plot(
                ref[:, REF_COLUMNS[case][key]],
                ref[:, 0],
                "-",
                lw=3.0,
                alpha=0.45,
                color=colors[case],
                label=f"Wu et al. — {case}",
            )
            if varname in prof:
                ax.plot(
                    prof[varname],
                    prof["z"],
                    markers[case],
                    ms=6,
                    mfc="none",
                    color=colors[case],
                    label=f"Orca — {case}",
                )
        ax.set_xlabel(label + "  (MPa)")
        ax.set_ylabel("depth along the fault, $z$  (m)")
        ax.grid(alpha=0.3)
        ax.set_ylim(-300, 380)
        ax.legend(frameon=False, loc="upper left", fontsize=15)
        ax.set_title(
            "Induced stresses on a fault bounding a pressurized displaced reservoir\n"
            f"$E$={YOUNGS_MODULUS/1e9:g} GPa, $\\nu$={POISSONS_RATIO:g}, "
            f"$\\alpha$={BIOT:.2f}, $\\Delta p$={PRESSURE_BUILDUP/1e6:g} MPa",
            fontsize=14,
        )
        fig.tight_layout()
        path = os.path.join(HERE, f"fault_verification_comparison_{stems[key]}.png")
        fig.savefig(path, dpi=600)
        plt.close(fig)
        paths.append(path)
    return paths


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--no-plot", action="store_true")
    args = parser.parse_args(argv)

    ref = read_reference()
    if ref is None:
        print(f"Reference data not found: {REFERENCE_FILE}", file=sys.stderr)
        return 1

    print("Fault-verification comparison against Wu et al. (2020)\n")
    print(f"  Biot coefficient alpha  = {BIOT:.6f}")
    print(f"  1-D limit of d sxx+d szz inside the pressurized layer = {UNIAXIAL_SUM_MPA:.4f} MPa\n")

    profiles, records = {}, []
    for case in CASES:
        prof = read_profile(case)
        if prof is None:
            print(f"  {case:12s} no output found (deck not run?)", file=sys.stderr)
            continue
        profiles[case] = prof
        records.extend(compare(case, prof, ref))

        lim = check_uniaxial_limit(prof)
        print(f"  {case}: {len(prof['z'])} sample depths from {prof['path']}")
        if lim:
            if "sum_in_layer_MPa" in lim:
                print(
                    f"     inside pressurized layer ({lim['n_pressurized']} pts): "
                    f"d sxx + d szz = {lim['sum_in_layer_MPa']:8.4f} MPa "
                    f"(exact {lim['sum_in_layer_expected_MPa']:.4f})"
                )
            if "sum_outside_MPa" in lim:
                print(
                    f"     outside                  ({lim['n_dry']} pts): "
                    f"d sxx + d szz = {lim['sum_outside_MPa']:8.4f} MPa (exact 0)"
                )
        print(
            f"     out-of-plane spread (plane-strain check): "
            f"{max(prof['spread'].values()):.3e} MPa"
        )
    print()

    if not records:
        print("No MOOSE output found. Run the decks first.", file=sys.stderr)
        return 1

    head = (
        f"  {'case':13s} {'comp':>5s} {'RMS (MPa)':>10s} {'max (MPa)':>10s} "
        f"{'span (MPa)':>11s} {'RMS % span':>11s}"
    )
    print(head)
    print("  " + "-" * (len(head) - 2))
    for r in records:
        line = (
            f"  {r['case']:13s} {r['component']:>5s} {r['rms_error_MPa']:10.4f} "
            f"{r['max_abs_error_MPa']:10.4f} {r['reference_span_MPa']:11.4f} "
            f"{r['rms_error_pct_of_span']:10.2f}%"
        )
        if "rms_error_flipped_MPa" in r:
            better = "as-is" if r["rms_error_MPa"] <= r["rms_error_flipped_MPa"] else "FLIPPED"
            line += f"   [sign check: {better}, flipped RMS {r['rms_error_flipped_MPa']:.4f}]"
        print(line)
    print()

    print(f"  wrote {write_summary(records)}")
    print(f"  wrote {write_profiles(profiles, ref)}")
    if not args.no_plot:
        for path in plot(profiles, ref):
            print(f"  wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
