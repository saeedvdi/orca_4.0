#!/usr/bin/env python3
"""
check_mesh_geometry.py -- measure L, D and the fracture angle straight out of a
built Exodus mesh and compare them with Ye & Ghassemi (2018) Table 1.

WHY THIS EXISTS
===============
Journal headers lie. Several meshes in this campaign carry a comment block stating
one geometry and a `create vertex` line producing another, and the SW-S4 journal is
a copy of SW-S3's with only the height edited -- which left its fracture plane at
28.99 deg while the comment said 30. The only trustworthy source is the .e file, so
this measures it:

    L      z bounding box
    D      max of the x and y bounding boxes
    theta  least-squares plane fit through the `fracture_interface` nodeset,
           reported as the angle from the core long axis (z), which is the
           convention the paper uses.

Run it after any mesh rebuild, BEFORE check_source_nodes.py -- a mis-transcribed
vertex shows up here as a wrong angle, whereas check_source_nodes.py would only
report that the source moved.

NOTE on SW-T2. Table 1 prints 31 deg, but the theta-recovery identity applied to
Table 2,
        tan(theta) = (sigma'_n - sigma_3 + P_p) / tau
returns 30.00 deg at all eleven hold stages (spread 29.991-30.008), while the same
test reproduces Table 1 for SW-T1, SW-S3 and SW-S4 to three decimals. The campaign
therefore models SW-T2 at 30 deg and this script flags 31 deg as the error. See
Examples/YeGhasemmi2018/MESHES.md.

Usage:
    python3 scripts/check_mesh_geometry.py <mesh.e> [<mesh.e> ...]
    python3 scripts/check_mesh_geometry.py 'Examples/YeGhasemmi2018/*/mesh/*.e'

Needs netCDF4 (available in the `moose` conda environment).
"""

import glob
import math
import os
import sys

import numpy as np
from netCDF4 import Dataset

# Table 1, plus the SW-T2 correction argued in the docstring.
TABLE1 = {                      # L_mm,   D_mm,  theta_deg
    "SWT1": (128.80, 50.52, 32.0),
    "SWT2": (132.70, 50.52, 30.0),
    "SWS3": (123.40, 50.53, 29.0),
    "SWS4": (118.70, 50.51, 30.0),
}
TOL_L, TOL_D, TOL_TH = 0.05, 0.02, 0.02     # mm, mm, deg


def sample_of(name):
    n = name.upper()
    for key, pats in (("SWS3", ("SWS3", "SW_S3", "SW3")),
                      ("SWS4", ("SWS4", "SW_S4", "SW4")),
                      ("SWT1", ("SWT1", "SW_T1")),
                      ("SWT2", ("SWT2", "SW_T2"))):
        if any(p in n for p in pats):
            return key
    return None


def _names(ds, var):
    if var not in ds.variables:
        return []
    return ["".join(c.decode() if isinstance(c, bytes) else str(c)
                    for c in row if c is not np.ma.masked).strip("\x00").strip()
            for row in ds.variables[var][:]]


def measure(path):
    ds = Dataset(path)
    try:
        x, y, z = (np.array(ds.variables[c][:], dtype=float)
                   for c in ("coordx", "coordy", "coordz"))
        L = (z.max() - z.min()) * 1e3
        D = max(x.max() - x.min(), y.max() - y.min()) * 1e3

        idx = None
        for i, nm in enumerate(_names(ds, "ns_names")):
            if "fracture" in nm.lower() or "interface" in nm.lower():
                idx = np.array(ds.variables[f"node_ns{i + 1}"][:], dtype=int) - 1
                break
        if idx is None:     # fall back to nodes shared by both element blocks
            blocks = [np.unique(np.array(ds.variables[v][:]).ravel()) - 1
                      for v in ds.variables if v.startswith("connect")]
            idx = np.intersect1d(*blocks) if len(blocks) == 2 else None

        theta = rms = float("nan")
        if idx is not None and len(idx) > 3:
            # z = a + b x + c y ; the plane's angle from the z axis is atan(1/|grad|)
            A = np.column_stack([np.ones(len(idx)), x[idx], y[idx]])
            coef, *_ = np.linalg.lstsq(A, z[idx], rcond=None)
            theta = math.degrees(math.atan2(1.0, math.hypot(coef[1], coef[2])))
            rms = float(np.sqrt(np.mean((A @ coef - z[idx]) ** 2))) * 1e6
        return L, D, theta, rms, len(x), 0 if idx is None else len(idx)
    finally:
        ds.close()


def main(patterns):
    paths = []
    for p in patterns:
        paths.extend(sorted(glob.glob(p)) or [p])
    if not paths:
        raise SystemExit("no meshes matched")

    print(f"{'file':46} {'L mm':>8} {'want':>8} {'dL':>7} {'D mm':>7} "
          f"{'theta':>8} {'want':>6} {'dth':>7} {'planar':>8} {'nodes':>8} {'ifc':>5}")
    bad = 0
    for p in paths:
        try:
            L, D, th, rms, nn, nifc = measure(p)
        except Exception as exc:                          # noqa: BLE001
            print(f"{os.path.basename(p):46} ERROR {exc}")
            bad += 1
            continue
        s = sample_of(os.path.basename(p))
        if s is None:
            print(f"{os.path.basename(p):46} {L:8.2f} {'?':>8} {'':>7} {D:7.2f} "
                  f"{th:8.3f} {'?':>6} {'':>7} {rms:8.2f} {nn:8d} {nifc:5d}"
                  "   (unrecognised sample)")
            continue
        Lp, Dp, thp = TABLE1[s]
        flags = []
        if abs(L - Lp) > TOL_L:
            flags.append("L")
        if abs(D - Dp) > TOL_D:
            flags.append("D")
        if not math.isnan(th) and abs(th - thp) > TOL_TH:
            flags.append("THETA")
        bad += bool(flags)
        print(f"{os.path.basename(p):46} {L:8.2f} {Lp:8.2f} {L - Lp:+7.2f} {D:7.2f} "
              f"{th:8.3f} {thp:6.1f} {th - thp:+7.3f} {rms:8.2f} {nn:8d} {nifc:5d}"
              f"   {'*** ' + ' '.join(flags) if flags else 'ok'}")

    print(f"\n'planar' is the RMS residual of the plane fit, in um: a mated saw cut or\n"
          f"tensile fracture is modelled as planar, so anything above ~1 um means the\n"
          f"nodeset picked up more than the fracture surface.")
    return 1 if bad else 0


if __name__ == "__main__":
    if len(sys.argv) < 2:
        raise SystemExit(__doc__)
    sys.exit(main(sys.argv[1:]))
