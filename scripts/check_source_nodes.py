#!/usr/bin/env python3
"""
check_source_nodes.py -- verify that a deck's injection/production coordinates snap
to a node that is actually ON the fracture interface.

WHY THIS EXISTS
===============
`ExtraNodesetGenerator ... use_closest_node = true` never errors. If the requested
coordinate misses the fracture plane it silently pins the source to the nearest
BULK node, and the run proceeds with the injection driving the matrix instead of
the joint. This has bitten this project before -- a 41 um miss changed a whole
calibration -- so the rule is: run this after ANY mesh rebuild or source move.

Usage:
    python3 scripts/check_source_nodes.py <mesh.e> x y z [x y z ...]
    python3 scripts/check_source_nodes.py --deck <deck.i>      # parse both sources

Needs netCDF4 (available in the `moose` conda environment).
"""

import os
import re
import sys

import numpy as np
from netCDF4 import Dataset


def interface_nodes(ds):
    """Node ids shared by both element blocks -- i.e. lying on the webcut plane."""
    blocks = [np.unique(np.array(ds.variables[v][:]).ravel()) - 1
              for v in ds.variables if v.startswith("connect")]
    if len(blocks) != 2:
        raise SystemExit(f"expected 2 element blocks, found {len(blocks)}")
    return np.intersect1d(blocks[0], blocks[1])


def check(mesh_path, coords):
    ds = Dataset(mesh_path)
    xyz = np.column_stack([np.array(ds.variables[c][:]) for c in ("coordx", "coordy", "coordz")])
    iface = interface_nodes(ds)

    print(f"mesh: {mesh_path}")
    print(f"  {len(xyz)} nodes, {len(iface)} on the fracture interface\n")

    worst = 0.0
    for c in coords:
        c = np.asarray(c, dtype=float)
        d_all = np.linalg.norm(xyz - c, axis=1)
        j_all = int(np.argmin(d_all))
        d_if = np.linalg.norm(xyz[iface] - c, axis=1)
        j_if = int(iface[int(np.argmin(d_if))])
        on_interface = j_all in set(iface.tolist())
        worst = max(worst, d_all[j_all])

        print(f"  requested   {c[0]: .6f} {c[1]: .6f} {c[2]: .6f}")
        print(f"  snaps to    {xyz[j_all][0]: .6f} {xyz[j_all][1]: .6f} "
              f"{xyz[j_all][2]: .6f}   (node {j_all + 1}, {d_all[j_all]*1e6:.1f} um away)")
        if on_interface:
            print("  VERDICT     OK -- the closest node IS on the fracture interface")
        else:
            print(f"  VERDICT     *** BULK NODE *** nearest interface node is "
                  f"{d_if.min()*1e6:.1f} um away (node {j_if + 1}); injection would "
                  f"drive the matrix, not the joint")
        print()
    ds.close()
    return worst


def parse_deck(path):
    """Pull mesh_file and the two source coords out of a deck."""
    txt = open(path).read()
    m = re.search(r"^\s*mesh_file\s*=\s*(\S+)", txt, re.M)
    if not m:
        raise SystemExit(f"{path}: no mesh_file")
    mesh = os.path.join(os.path.dirname(os.path.abspath(path)), m.group(1))
    coords = [tuple(float(v) for v in c.split())
              for c in re.findall(r"^\s*coord\s*=\s*'([^']+)'", txt, re.M)]
    return mesh, coords


if __name__ == "__main__":
    args = sys.argv[1:]
    if not args:
        raise SystemExit(__doc__)
    if args[0] == "--deck":
        rc = 0
        for deck in args[1:]:
            mesh, coords = parse_deck(deck)
            print(f"=== {deck}")
            check(mesh, coords)
        sys.exit(rc)
    nums = [float(v) for v in args[1:]]
    check(args[0], [nums[i:i + 3] for i in range(0, len(nums), 3)])
