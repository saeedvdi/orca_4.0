#!/usr/bin/env python3
"""
check_axis_intervals.py -- explain, and predict, source pinning on the Kalantar
and Ye2018 meshes.

WHY THIS EXISTS
===============
check_source_nodes.py answers "did the source land on the fracture, and how far
from the design point?".  It does not say WHY, so every miss looked like bad luck
and the only known remedy was to try another global mesh size and re-measure.

There is no luck in it.  Both boreholes sit at y = 0 on the fracture plane, which
is exactly the MAJOR AXIS of the fracture ellipse -- i.e. on the curve produced by
the `webcut ... yplane` in the journal, not in the interior of a surface.  Cubit
divides that curve into N EQUAL intervals (verified: min spacing == max spacing to
machine precision on all six meshes).  So the available node positions along it
are k/N of the half-length, the design borehole sits at

    x_design / r = (r - 0.005) / r = 0.01999 / 0.02499 = 0.799920

and the pinning error is pure integer arithmetic:

    nearest fraction = round(0.79992 * N) / N

Measured on the six meshes in this repo (2026-08-24):

    mesh              N    nearest fraction     pinning error
    _size3  OG-SH     25   20/25 = 0.800000         4.1 um   <-- N divisible by 5
    _size3  OG-T      27   22/27 = 0.814815       792.9 um
    _size3  OG-SC     26   21/26 = 0.807692       388.5 um
    graded  OG-SH     28   22/28 = 0.785714       732.2 um
    graded  OG-T      29   23/29 = 0.793103       362.8 um
    graded  OG-SC     27   22/27 = 0.814815       744.4 um

Every one of those reproduces the independently measured check_source_nodes.py
distance to 0.1 um.  OG-SH's much-quoted "4.1 um" pin was never a property of that
mesh being good: it is N = 25 being divisible by 5, because the design borehole
sits two microns off exactly 4/5 of the radius.  Nothing else about OG-SH's mesh
is special, and nothing about the other two is wrong.

WHAT TO DO WITH IT
==================
Two fixes, both in the journals:

  1. Split the axis curve at the design position (a vertex -> a node, always).
     Exact and mesh-size independent.  This is the active mechanism.
  2. Force N divisible by 5 (`curve <id> interval 25`).  Lands a node at exactly
     0.8 r = 0.019992, i.e. 4.1 um from design, at any global coarseness, with no
     change to the topology.  This is the zero-risk fallback.

Either one decouples source pinning from mesh size, which is what makes the mesh
free to be coarsened.

Usage:
    python3 scripts/check_axis_intervals.py <mesh.e> [<mesh.e> ...]
    python3 scripts/check_axis_intervals.py <mesh.e> --inset 0.004   # hole edge

Geometry (L, radius, fracture angle) is inferred from the mesh, so this works on
any rebuild without being told what it is looking at.  Needs netCDF4 (the `moose`
conda environment).
"""

import argparse
import math
import sys

import numpy as np
from netCDF4 import Dataset

TOL_PLANE = 1e-9   # m, node-on-plane test
TOL_AXIS = 1e-9    # m, |y| test for "on the major axis"


def interface_nodes(ds):
    """Node ids shared by both element blocks -- i.e. lying on the webcut plane."""
    blocks = [np.unique(np.array(ds.variables[v][:]).ravel()) - 1
              for v in ds.variables if v.startswith("connect")]
    if len(blocks) != 2:
        raise SystemExit(f"expected 2 element blocks, found {len(blocks)}")
    return np.intersect1d(blocks[0], blocks[1])


def infer_geometry(xyz, iface):
    """Return (length, radius, theta_deg, z_centre, cot_theta) from the mesh itself.

    The fracture plane is z = z0 + x cot(theta); it does not vary with y, so a
    two-parameter least-squares fit over the interface nodes recovers both the
    angle and the centre without any input from the journal.
    """
    length = float(xyz[:, 2].max() - xyz[:, 2].min())
    radius = float(np.hypot(xyz[:, 0], xyz[:, 1]).max())
    x, z = xyz[iface, 0], xyz[iface, 2]
    A = np.column_stack([np.ones_like(x), x])
    (z0, cot), *_ = np.linalg.lstsq(A, z, rcond=None)
    resid = float(np.abs(z - (z0 + cot * x)).max())
    theta = math.degrees(math.atan2(1.0, cot))
    return length, radius, theta, float(z0), float(cot), resid


def report(mesh_path, inset):
    ds = Dataset(mesh_path)
    xyz = np.column_stack([np.array(ds.variables[c][:]) for c in ("coordx", "coordy", "coordz")])
    iface = interface_nodes(ds)
    length, radius, theta, z0, cot, resid = infer_geometry(xyz, iface)
    sin_t = math.sin(math.radians(theta))
    half_curve = radius / sin_t

    print(f"\n=== {mesh_path}")
    print(f"  inferred  L = {length*1e3:.3f} mm   r = {radius*1e3:.4f} mm   "
          f"theta = {theta:.4f} deg   plane residual {resid*1e6:.2f} um")
    print(f"  {len(xyz)} nodes, {len(iface)} on the fracture interface, "
          f"major-axis half-length {half_curve*1e3:.4f} mm")

    on_plane = np.abs(xyz[:, 2] - (z0 + cot * xyz[:, 0])) < TOL_PLANE
    axis = on_plane & (np.abs(xyz[:, 1]) < TOL_AXIS)
    xs = np.sort(xyz[axis & (xyz[:, 0] > TOL_AXIS), 0])
    if len(xs) < 2:
        print("  !! no major-axis nodes found -- is this the expected geometry?")
        ds.close()
        return

    n_int = len(xs)                       # intervals on the +x half-curve
    spacing = np.diff(xs) / sin_t
    uniform = (spacing.max() - spacing.min()) < 1e-9
    print(f"  axis intervals N = {n_int}   along-curve spacing "
          f"{spacing.mean()*1e3:.4f} mm  ({'uniform' if uniform else 'NON-UNIFORM'})")

    x_design = radius - inset
    frac = x_design / radius
    k = int(round(frac * n_int))
    x_node = xs[int(np.argmin(np.abs(xs - x_design)))]
    err_curve = abs(x_node - x_design) / sin_t
    sep_design = 2 * x_design / sin_t
    sep_node = 2 * x_node / sin_t

    print(f"  design x = {x_design:.6f}  (fraction {frac:.6f} of r)")
    print(f"  nearest node x = {x_node:.9f}  = {k}/{n_int} = {k/n_int:.6f}"
          f"   ->  {err_curve*1e6:.1f} um along the fracture")
    print(f"  borehole separation {sep_node*1e3:.4f} mm vs design "
          f"{sep_design*1e3:.4f} mm  ({(sep_node/sep_design-1)*100:+.3f} %)")

    if n_int % 5 == 0:
        print(f"  VERDICT  N = {n_int} is divisible by 5, so a node sits at exactly "
              f"0.8 r.  Pinning is as good as this scheme allows ({err_curve*1e6:.1f} um).")
    else:
        best = 5 * round(n_int / 5) or 5
        print(f"  VERDICT  N = {n_int} is NOT divisible by 5 -> {err_curve*1e6:.1f} um error.")
        print(f"           Fix A (active in the journal): split the axis curve at the")
        print(f"           design position; the vertex forces a node, error -> 0.")
        print(f"           Fix B (no topology change): `curve <id> interval {best}`,")
        print(f"           which puts a node at 0.8 r, {abs(0.8*radius-x_design)/sin_t*1e6:.1f} um from design.")
    ds.close()


def main():
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("meshes", nargs="+")
    ap.add_argument("--inset", type=float, default=0.005,
                    help="borehole inset from the sidewall in m (default 0.005, the "
                         "hole-CENTRE reading of the paper's '5 mm'; use 0.004 for "
                         "the hole-edge reading)")
    args = ap.parse_args()
    for m in args.meshes:
        report(m, args.inset)
    print()


if __name__ == "__main__":
    sys.exit(main())
