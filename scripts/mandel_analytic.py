#!/usr/bin/env python
"""Compare test/tests/verification/mandel against the Cheng & Detournay solution.

    /home/geomechanics/miniforge/bin/python scripts/mandel_analytic.py

The MOOSE test is a CSVDiff against a gold file -- a regression lock, which only
proves the answer has not CHANGED. This script checks it against the mathematics.

Mandel's problem: a plane-strain sample -a<=x<=a, -b<=y<=b squashed by rigid,
impermeable, frictionless platens at y=+/-b under constant total force F, drained
at x=+/-a. Because the platens are rigid, load shed by the draining edges is
transferred inward and the centre pressure RISES above its undrained value before
decaying -- the Mandel-Cryer effect. Terzaghi cannot exhibit this.

    alpha_n are the positive roots of   tan(a) = [(1-nu)/(nuu-nu)] a

    p(x,t) = (2 F B (1+nuu) / 3a)
             SUM_n  sin(a_n)/(a_n - sin a_n cos a_n)
                    * [cos(a_n x/a) - cos(a_n)]
                    * exp(-a_n^2 c t / a^2)

    u_y(y,t)/y = -F(1-nu)/(2 G a)
                 + (F(1-nuu)/(G a))
                   SUM_n  sin(a_n) cos(a_n)/(a_n - sin a_n cos a_n)
                          * exp(-a_n^2 c t / a^2)

Reference: A.H.-D. Cheng and E. Detournay, "A direct boundary element method for
plane strain poroelasticity", Int. J. Numer. Anal. Methods Geomech. 12 (1988)
551-572. Same parameter set as MOOSE's porous_flow mandel_constM.i.

The script does TWO things:

  1. compares the simulated pressure profile against the series, and
  2. regenerates the platen displacement table that mandel.i imposes as a
     boundary condition, from the SAME series, and reports the agreement.

(2) matters because that table was reproduced from the MOOSE reference input. If
this script's independent evaluation of u_y reproduces it, the imposed boundary
condition is verified rather than taken on trust -- and the pressure comparison in
(1) then rests on a boundary condition known to be right.
"""

import csv
import os
import sys
from math import atan, cos, exp, pi, sin, tan

# --- problem constants, mirroring mandel.i ----------------------------------
A = 1.0             # half-width
B_HEIGHT = 0.1      # half-height
LA, G = 0.5, 0.75   # Lame lambda, shear modulus
K = LA + 2.0 * G / 3.0                    # 1.0    drained bulk modulus
KF = 8.0
PHI = 0.1
ALPHA = 0.6
MOBILITY = 1.5      # permeability / viscosity
F = 1.0             # applied normal force per unit area

NU = LA / (2.0 * (LA + G))                          # 0.2      drained Poisson
M = 1.0 / (PHI / KF + (ALPHA - PHI) * (1.0 - ALPHA) / K)   # 4.705882
KU = K + ALPHA ** 2 * M                             # 2.694118 undrained bulk
NUU = (3.0 * KU - 2.0 * G) / (6.0 * KU + 2.0 * G)   # 0.372627 undrained Poisson
SKEMPTON = ALPHA * M / KU                           # 1.048035
C = (2.0 * MOBILITY * SKEMPTON ** 2 * G * (1.0 - NU) * (1.0 + NUU) ** 2
     / (9.0 * (1.0 - NUU) * (NUU - NU)))            # consolidation coefficient

NROOTS = 200
KAPPA = (1.0 - NU) / (NUU - NU)

PROBES = [("p0", 0.0), ("p2", 0.2), ("p4", 0.4), ("p6", 0.6), ("p8", 0.8)]


def roots():
    """Positive roots of tan(a) = KAPPA a, one per interval ((n-1)pi, (n-1)pi + pi/2)."""
    out = []
    for n in range(NROOTS):
        lo = n * pi + 1e-12
        hi = n * pi + pi / 2.0 - 1e-12
        # f = tan(a) - KAPPA a is negative at lo and positive near hi.
        f = lambda a: tan(a) - KAPPA * a
        flo, fhi = f(lo), f(hi)
        if flo * fhi > 0.0:
            continue
        for _ in range(200):
            mid = 0.5 * (lo + hi)
            if f(lo) * f(mid) <= 0.0:
                hi = mid
            else:
                lo = mid
        out.append(0.5 * (lo + hi))
    return out


ROOTS = roots()


def pressure(x, t):
    if t <= 0.0:
        t = 0.0
    pre = 2.0 * F * SKEMPTON * (1.0 + NUU) / (3.0 * A)
    s = 0.0
    for an in ROOTS:
        den = an - sin(an) * cos(an)
        s += (sin(an) / den) * (cos(an * x / A) - cos(an)) * exp(-an ** 2 * C * t / A ** 2)
    return pre * s


def uy(y, t):
    base = -F * (1.0 - NU) / (2.0 * G * A)
    s = 0.0
    for an in ROOTS:
        den = an - sin(an) * cos(an)
        s += (sin(an) * cos(an) / den) * exp(-an ** 2 * C * t / A ** 2)
    return (base + F * (1.0 - NUU) / (G * A) * s) * y


# The platen table as it appears in mandel.i (and in the MOOSE reference).
TABLE_T = [0, 0.002, 0.006, 0.014, 0.03, 0.046, 0.062, 0.078, 0.094, 0.11,
           0.126, 0.142, 0.158, 0.174, 0.19, 0.206, 0.222, 0.238, 0.254, 0.27,
           0.286, 0.302, 0.318, 0.334, 0.35, 0.366, 0.382, 0.398, 0.414, 0.43,
           0.446, 0.462, 0.478, 0.494, 0.51, 0.526, 0.542, 0.558, 0.574, 0.59,
           0.606, 0.622, 0.638, 0.654, 0.67, 0.686, 0.702]
TABLE_U = [-0.041824842, -0.042730269, -0.043412712, -0.04428867, -0.045509181,
           -0.04645965, -0.047268246, -0.047974749, -0.048597109, -0.0491467,
           -0.049632388, -0.050061697, -0.050441198, -0.050776675, -0.051073238,
           -0.0513354, -0.051567152, -0.051772022, -0.051953128, -0.052113227,
           -0.052254754, -0.052379865, -0.052490464, -0.052588233, -0.052674662,
           -0.052751065, -0.052818606, -0.052878312, -0.052931093, -0.052977751,
           -0.053018997, -0.053055459, -0.053087691, -0.053116185, -0.053141373,
           -0.05316364, -0.053183324, -0.053200724, -0.053216106, -0.053229704,
           -0.053241725, -0.053252351, -0.053261745, -0.053270049, -0.053277389,
           -0.053283879, -0.053289615]


def check_platen_table():
    print("BOUNDARY-CONDITION CHECK: the platen table in mandel.i, regenerated")
    print("independently from the series above.")
    worst, worst_t = 0.0, 0.0
    for t, u_ref in zip(TABLE_T, TABLE_U):
        u_own = uy(B_HEIGHT, t)
        err = abs(u_own - u_ref)
        if err > worst:
            worst, worst_t = err, t
    print("   entries: %d,  worst absolute difference: %.3e at t = %.3f"
          % (len(TABLE_T), worst, worst_t))
    print("   u_y(b, 0)     series %.9f   table %.9f" % (uy(B_HEIGHT, 0.0), TABLE_U[0]))
    print("   u_y(b, 0.702) series %.9f   table %.9f" % (uy(B_HEIGHT, 0.702), TABLE_U[-1]))
    print("   drained limit -F(1-nu)b/(2 G a) = %.9f"
          % (-F * (1.0 - NU) * B_HEIGHT / (2.0 * G * A)))
    print()


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    csv_path = os.path.normpath(os.path.join(
        here, os.pardir, "test", "tests", "verification", "mandel", "gold",
        "mandel_csv.csv"))
    print("derived constants")
    print("   nu  = %.6f   M   = %.6f   Ku  = %.6f" % (NU, M, KU))
    print("   nuu = %.6f   B   = %.6f   c   = %.6f" % (NUU, SKEMPTON, C))
    print("   undrained uniform pressure F B (1+nuu)/3a = %.6f"
          % (F * SKEMPTON * (1.0 + NUU) / (3.0 * A)))
    print("   %d series roots, first three: %.6f %.6f %.6f"
          % (len(ROOTS), ROOTS[0], ROOTS[1], ROOTS[2]))
    print()

    check_platen_table()

    if not os.path.exists(csv_path):
        sys.exit("gold CSV not found: %s\nRun the test first." % csv_path)
    with open(csv_path) as fh:
        rows = list(csv.DictReader(fh))

    print("PRESSURE CHECK. Errors are normalised by the undrained pressure p_u,")
    print("since the profile decays through zero and local ratios lose meaning.")
    p_u = F * SKEMPTON * (1.0 + NUU) / (3.0 * A)

    report = [rows[0], rows[len(rows) // 8], rows[len(rows) // 4],
              rows[len(rows) // 2], rows[3 * len(rows) // 4], rows[-1]]
    worst = 0.0
    for r in report:
        t = float(r["time"])
        print("t = %.5f" % t)
        print("   %-6s %6s %12s %12s %10s" % ("probe", "x", "numeric", "series", "err/p_u"))
        for name, x in PROBES:
            num, ana = float(r[name]), pressure(x, t)
            e = (num - ana) / p_u
            worst = max(worst, abs(e))
            print("   %-6s %6.1f %12.6f %12.6f %9.3f%%" % (name, x, num, ana, 100.0 * e))
    print()

    p0 = [float(r["p0"]) for r in rows]
    t0 = [float(r["time"]) for r in rows]
    imax = p0.index(max(p0))
    print("MANDEL-CRYER OVERSHOOT -- the signature Terzaghi cannot produce")
    print("   undrained p_u                = %.6f" % p_u)
    print("   simulated peak p0            = %.6f at t = %.5f" % (p0[imax], t0[imax]))
    print("   series    peak p0            = %.6f" % max(pressure(0.0, t) for t in t0))
    print("   overshoot above p_u          = %.2f%%" % (100.0 * (p0[imax] / p_u - 1.0)))
    print("   p0 rises for the first %d of %d output rows, then decays"
          % (imax + 1, len(rows)))
    print()

    force = [float(r["total_downwards_force"]) for r in rows]
    print("APPLIED FORCE -- the boundary condition the platen displacement stands in for")
    print("   target F = %.1f, simulated range %.6f to %.6f (worst %.3f%% off)"
          % (F, min(force), max(force),
             100.0 * max(abs(f - F) for f in force) / F))
    print()
    print("worst pressure error over all reported times: %.3f%% of p_u" % (100.0 * worst))


if __name__ == "__main__":
    main()
