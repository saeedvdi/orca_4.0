#!/usr/bin/env python
"""Compare test/tests/verification/terzaghi against Verruijt's closed-form solution.

The MOOSE test itself is a CSVDiff against a gold file -- a regression lock, which
by construction only proves the answer has not CHANGED. This script is what makes
that gold file mean something: it checks the numbers against the mathematics.

Run it whenever the gold file is regenerated.

    /home/geomechanics/miniforge/bin/python scripts/terzaghi_analytic.py

Reference: A. Verruijt, "Theory and Problems of Poroelasticity", TU Delft 2013,
section 2.2. Same parameter set as MOOSE's porous_flow terzaghi.i.
"""

import sys
import os
import numpy as np

# --- problem constants, mirroring terzaghi.i --------------------------------
H = 10.0            # column height
LA, MU = 2.0, 3.0   # Lame parameters
K = LA + 2.0 * MU / 3.0             # 4.0   drained bulk modulus
M_CONF = 1.0 / (K + 4.0 * MU / 3.0)  # 0.125 confined compressibility
KF = 8.0
PHI = 0.1
ALPHA = 0.6
MOBILITY = 1.5      # permeability / viscosity
Q = 1.0             # applied normal stress

# Storativity. Identical to Orca's 1/M in OrcaTHMaterial::computeBiotModulus.
S = PHI / KF + (ALPHA - PHI) * (1.0 - ALPHA) / K          # 0.0625
C = MOBILITY / (S + ALPHA**2 * M_CONF)                    # 13.95348837
P0 = ALPHA * M_CONF * Q / (S + ALPHA**2 * M_CONF)         # 0.69767442

UZ0 = Q * M_CONF * H * S / (S + ALPHA**2 * M_CONF)        # undrained settlement
UZINF = Q * M_CONF * H                                    # drained settlement

NTERMS = 4000


def pressure(z, t):
    """p(z,t): z measured up from the sealed base, drained face at z=H."""
    if t <= 0.0:
        return 0.0
    k = np.arange(1, NTERMS + 1)
    n = 2 * k - 1
    return float(
        (4.0 * P0 / np.pi)
        * np.sum(
            ((-1.0) ** (k - 1) / n)
            * np.cos(n * np.pi * z / (2.0 * H))
            * np.exp(-(n**2) * np.pi**2 * C * t / (4.0 * H**2))
        )
    )


def consolidation(t):
    """Degree of consolidation U(t) in [0,1]."""
    if t <= 0.0:
        return 0.0
    k = np.arange(1, NTERMS + 1)
    n = 2 * k - 1
    return float(
        1.0
        - (8.0 / np.pi**2)
        * np.sum(np.exp(-(n**2) * np.pi**2 * C * t / (4.0 * H**2)) / n**2)
    )


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    csv = os.path.join(here, "..", "test", "tests", "verification", "terzaghi",
                       "gold", "terzaghi_out.csv")
    if len(sys.argv) > 1:
        csv = sys.argv[1]
    if not os.path.exists(csv):
        sys.exit(f"not found: {csv}\nRun the test first, or pass a CSV path.")

    data = np.genfromtxt(csv, delimiter=",", names=True)
    t = np.atleast_1d(data["time"])

    print(f"Terzaghi verification against Verruijt section 2.2")
    print(f"  file      {os.path.relpath(csv, os.path.join(here, '..'))}")
    print(f"  S={S:.6g}  M=1/S={1/S:.6g}  c={C:.8f}  p0={P0:.8f}")
    print(f"  uz0={UZ0:.6f}  uzinf={UZINF:.6f}\n")

    # Pressure columns, and the height each was sampled at.
    probes = [("p0", 0.0), ("p2", 2.0), ("p5", 5.0), ("p8", 8.0)]

    print(f"{'probe':>6} {'z':>5} {'max |err|':>12} {'max rel':>10} "
          f"{'RMS err':>12}   (t > 0.05 only)")
    worst = 0.0
    for name, z in probes:
        if name not in data.dtype.names:
            continue
        num = np.atleast_1d(data[name])
        exact = np.array([pressure(z, ti) for ti in t])
        # Skip the first few steps: the drained face forces a discontinuity at
        # t=0+, and equal-order elements ring there. That is a known and
        # documented property of the discretisation, not of the physics.
        m = t > 0.05
        err = np.abs(num[m] - exact[m])
        rel = err / max(P0, 1e-30)
        print(f"{name:>6} {z:5.1f} {err.max():12.3e} {rel.max():10.3e} "
              f"{np.sqrt((err**2).mean()):12.3e}")
        worst = max(worst, rel.max())

    # Settlement, as degree of consolidation.
    if "uz_top" in data.dtype.names:
        uz = -np.atleast_1d(data["uz_top"])   # report downward-positive
        U_num = (uz - UZ0) / (UZINF - UZ0)
        U_exact = np.array([consolidation(ti) for ti in t])
        m = t > 0.05
        err = np.abs(U_num[m] - U_exact[m])
        print(f"\n  degree of consolidation U:  max |err| = {err.max():.3e}"
              f"   RMS = {np.sqrt((err**2).mean()):.3e}")
        print(f"  undrained settlement uz(t->0+): "
              f"numeric {uz[1]:.6f} vs exact {UZ0:.6f} "
              f"({100*(uz[1]-UZ0)/UZ0:+.2f} %)")
        print(f"  final settlement    uz(t=end) : "
              f"numeric {uz[-1]:.6f} vs exact {UZINF*U_exact[-1] + UZ0*(1-U_exact[-1]):.6f}")

    print(f"\n  worst relative pressure error: {100*worst:.2f} % of p0")


if __name__ == "__main__":
    main()
