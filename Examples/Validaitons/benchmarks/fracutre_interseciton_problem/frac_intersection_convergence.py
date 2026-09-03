"""
T-fracture benchmark — mesh convergence at the fracture tips and the junction.

Why
---
The headline result splits cleanly in two. The aperture and the slip match Phan et al.
to ~2.6 % and ~1.3 % of span, but the normal traction on the horizontal fracture comes
in at 12.3 %, and that number is not spread over the profile: over the stretch
3 m < |x| < 22 m it is 1.7 %, and essentially the whole error lives in three elements
per side — the two crack tips and the element abutting the T-junction.

Those are exactly the three places where the reference has a singularity that a
constant-per-element contact traction cannot represent: r^(-1/2) at each tip, and a drop
from 118 MPa to zero across ~1 m at the junction. So the 12.3 % is either a
discretization error that shrinks under refinement, or a defect in the contact
formulation that does not. Refining is what tells them apart, and this script does that.

What is varied
--------------
Only `refinement` on the `core` and `cap` blocks — the two that carry the fractures. The
outer mesh, the material, the loading and every solver setting are untouched, so the
sweep isolates fracture resolution. RefineBlockGenerator refines the neighbours enough to
avoid hanging nodes, so the surrounding matrix coarsens away from the fractures as before.

Element count on the refined blocks grows as 4^r, so level 2 is already ~110k elements
with a direct solve; that is the practical ceiling on a workstation.

Usage
-----
    python frac_intersection_convergence.py                    # levels 0..2, BBFast
    python frac_intersection_convergence.py --levels 0 1
    python frac_intersection_convergence.py --model compression_tensile
    python frac_intersection_convergence.py --ranks 8

Writes `frac_intersection_convergence.csv` and `.png` next to itself. Requires numpy and
matplotlib; needs `orca-opt` and mpiexec to run the cases.
"""

import argparse
import csv
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

HALF_LENGTH_V = 50.0
HALF_LENGTH_H = 25.0
BASE_SIDES_H = 32  # horizontal-fracture element count at refinement level 0


def build_case(model, level, workdir):
    """Copy the deck into `workdir` with a RefineBlockGenerator at `level`."""
    src = os.path.join(HERE, f"frac_intersection_{model}.i")
    text = open(src).read()
    if level > 0:
        refine = (
            "  [refine_fracture_blocks]\n"
            "    type = RefineBlockGenerator\n"
            "    input = make_cap\n"
            "    block = 'core cap'\n"
            f"    refinement = '{level} {level}'\n"
            "  []\n"
        )
        anchor = "  [break_horizontal]\n    type = BreakMeshByBlockGenerator\n    input = make_cap"
        if anchor not in text:
            raise RuntimeError(f"could not find the break_horizontal anchor in {src}")
        text = text.replace(
            anchor,
            refine
            + "  [break_horizontal]\n    type = BreakMeshByBlockGenerator\n"
            "    input = refine_fracture_blocks",
            1,
        )
    # The mesh path in the deck is relative to the deck; the scratch copy is elsewhere.
    text = text.replace(
        "file = mesh/frac_intersection_mesh.e",
        f"file = {os.path.join(HERE, 'mesh', 'frac_intersection_mesh.e')}",
    )
    dst = os.path.join(workdir, f"tfrac_r{level}.i")
    open(dst, "w").write(text)
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
        tail = "\n".join(proc.stdout.strip().splitlines()[-15:])
        raise RuntimeError(f"{os.path.basename(deck)} failed:\n{tail}")


def last_profile(stem):
    pat = re.compile(re.escape(stem) + r"_\d+\.csv$")
    files = sorted(f for f in __import__("glob").glob(stem + "_*.csv") if pat.search(f))
    for path in reversed(files):
        with open(path, newline="") as fh:
            rows = list(csv.DictReader(fh))
        if len(rows) > 1:
            return rows
    raise RuntimeError(f"no populated profile for {stem}")


def load_reference():
    ap = np.loadtxt(os.path.join(HERE, "Aperture.txt"))
    tn = np.loadtxt(os.path.join(HERE, "NormalTraction.txt"))
    sl = np.loadtxt(os.path.join(HERE, "Slip.txt"))
    out = {
        "aperture": (HALF_LENGTH_V - ap[:, 0], ap[:, 1]),
        "traction": (tn[:, 0] - HALF_LENGTH_H, tn[:, 1]),
        "slip": (sl[:, 0] - HALF_LENGTH_H, sl[:, 1]),
    }
    for k, (x, v) in out.items():
        o = np.argsort(x)
        out[k] = (x[o], v[o])
    return out


def rms_pct(num, ref_x, ref_v, x, split=False):
    if split:
        ref = np.empty_like(x, dtype=float)
        for side in (-1.0, 1.0):
            m, mr = (x * side) > 0, (ref_x * side) > 0
            ref[m] = np.interp(x[m], ref_x[mr], ref_v[mr])
    else:
        ref = np.interp(x, ref_x, ref_v)
    span = float(ref_v.max() - ref_v.min())
    return 100.0 * float(np.sqrt(np.mean((num - ref) ** 2))) / span


def read_case(workdir, level, ref):
    base = os.path.join(workdir, f"tfrac_r{level}_out")
    ap = last_profile(base + "_aperture_profile")
    hz = last_profile(base + "_horizontal_profile")

    y = np.array([float(r["y"]) for r in ap])
    dn = np.array([float(r["dn_v"]) for r in ap]) * 1.0e3
    o = np.argsort(y)
    y, dn = y[o], dn[o]

    x = np.array([float(r["x"]) for r in hz])
    tn = -np.array([float(r["sigma_n_h"]) for r in hz]) / 1.0e6
    sl = np.array([float(r["ds_h"]) for r in hz]) * 1.0e3
    o = np.argsort(x)
    x, tn, sl = x[o], tn[o], sl[o]
    # The tangential-jump sign is a mesh-generation convention; take the matching one.
    slip = sl if rms_pct(sl, *ref["slip"], x, split=True) < rms_pct(
        -sl, *ref["slip"], x, split=True
    ) else -sl

    # Away from the three singular points, where the reference is smooth.
    smooth = (np.abs(x) > 3.0) & (np.abs(x) < 22.0)
    return {
        "refinement_level": level,
        "fracture_elements": len(x) // 2,
        "element_size_m": 2.0 * HALF_LENGTH_H / (BASE_SIDES_H * 2**level),
        "aperture_rms_pct": rms_pct(dn, *ref["aperture"], y),
        "traction_rms_pct": rms_pct(tn, *ref["traction"], x),
        "traction_smooth_rms_pct": rms_pct(tn[smooth], *ref["traction"], x[smooth]),
        "slip_rms_pct": rms_pct(slip, *ref["slip"], x, split=True),
        "peak_aperture_mm": float(dn.max()),
        "junction_aperture_mm": float(dn[np.argmax(y)]),
        "peak_slip_mm": float(np.abs(slip).max()),
    }


def observed_order(h, err):
    h, err = np.asarray(h, float), np.asarray(err, float)
    good = (err > 0) & np.isfinite(err)
    if good.sum() < 2:
        return float("nan")
    return float(np.polyfit(np.log(h[good]), np.log(err[good]), 1)[0])


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.strip().split("\n")[0])
    parser.add_argument("--levels", type=int, nargs="+", default=[0, 1, 2])
    parser.add_argument("--model", default="barton_bandis")
    parser.add_argument("--ranks", type=int, default=8)
    parser.add_argument("--keep", action="store_true")
    args = parser.parse_args(argv)

    if not os.path.exists(ORCA):
        print(f"orca-opt not found at {ORCA}", file=sys.stderr)
        return 1

    ref = load_reference()
    ref_peak = float(ref["aperture"][1].max())
    ref_junction = float(np.interp(49.68, *ref["aperture"]))
    ref_peak_slip = float(np.abs(ref["slip"][1]).max())

    workdir = tempfile.mkdtemp(prefix="tfrac_conv_")
    print(f"T-fracture convergence sweep — model {args.model}, scratch {workdir}\n")

    rows = []
    try:
        for level in args.levels:
            deck = build_case(args.model, level, workdir)
            print(f"  refinement {level} ... ", end="", flush=True)
            run_case(deck, args.ranks)
            row = read_case(workdir, level, ref)
            rows.append(row)
            print(
                f"h={row['element_size_m']:.4f} m, {row['fracture_elements']} elements, "
                f"traction {row['traction_rms_pct']:.2f} %"
            )
    finally:
        if not args.keep:
            shutil.rmtree(workdir, ignore_errors=True)

    if not rows:
        return 1

    print()
    head = (
        f"  {'level':>5s} {'h (m)':>8s} {'elems':>6s} {'aperture':>9s} {'traction':>9s} "
        f"{'(smooth)':>9s} {'slip':>8s} {'peak ap':>9s} {'junction':>9s} {'peak slip':>10s}"
    )
    print(head)
    print("  " + "-" * (len(head) - 2))
    for r in rows:
        print(
            f"  {r['refinement_level']:5d} {r['element_size_m']:8.4f} "
            f"{r['fracture_elements']:6d} {r['aperture_rms_pct']:8.2f}% "
            f"{r['traction_rms_pct']:8.2f}% {r['traction_smooth_rms_pct']:8.2f}% "
            f"{r['slip_rms_pct']:7.2f}% {r['peak_aperture_mm']:9.2f} "
            f"{r['junction_aperture_mm']:9.2f} {r['peak_slip_mm']:10.2f}"
        )
    print(
        f"\n  Phan et al.                                                          "
        f"  {ref_peak:9.2f} {ref_junction:9.2f} {ref_peak_slip:10.2f}"
    )
    print()
    h = [r["element_size_m"] for r in rows]
    for key, label in (
        ("aperture_rms_pct", "aperture"),
        ("traction_rms_pct", "normal traction"),
        ("slip_rms_pct", "slip"),
    ):
        print(f"  observed order in h for {label:<18s}: {observed_order(h, [r[key] for r in rows]):5.2f}")
    print()

    out_csv = os.path.join(HERE, "frac_intersection_convergence.csv")
    with open(out_csv, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    print(f"  wrote {out_csv}")

    try:
        import matplotlib

        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        return 0

    fig, ax = plt.subplots(figsize=(6.8, 4.8))
    for key, marker, label in (
        ("aperture_rms_pct", "o", "aperture"),
        ("traction_rms_pct", "s", "normal traction"),
        ("traction_smooth_rms_pct", "d", "normal traction, smooth stretch only"),
        ("slip_rms_pct", "^", "slip"),
    ):
        ax.loglog(h, [r[key] for r in rows], marker + "-", label=label)
    ax.set_xlabel("fracture element size $h$  (m)")
    ax.set_ylabel("RMS error vs Phan et al.  (% of span)")
    ax.set_title("T-fracture — fracture mesh convergence", fontsize=11)
    ax.grid(alpha=0.3, which="both")
    ax.legend(frameon=False, fontsize=9)
    fig.tight_layout()
    out_png = os.path.join(HERE, "frac_intersection_convergence.png")
    fig.savefig(out_png, dpi=150)
    plt.close(fig)
    print(f"  wrote {out_png}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
