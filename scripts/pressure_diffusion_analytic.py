#!/usr/bin/env python
"""Compare test/tests/verification/pressure_diffusion against the erfc solution.

The MOOSE test itself is a CSVDiff against a gold file -- a regression lock, which
by construction only proves the answer has not CHANGED. This script is what makes
that gold file mean something: it checks the numbers against the mathematics, and
in particular pins the hydraulic diffusivity c = M k / mu, which is the one thing a
wrong k/mu convention would move.

Run it whenever the gold file is regenerated.

    /home/geomechanics/miniforge/bin/python scripts/pressure_diffusion_analytic.py

Half-space with a step inlet: p(x,0) = 0, p(0,t) = p0,

    p(x,t) = p0 erfc( x / (2 sqrt(c t)) )

Carslaw & Jaeger, "Conduction of Heat in Solids", 2nd ed., section 2.4.
"""

import os
import sys
from math import erfc, sqrt

# --- problem constants, mirroring pressure_diffusion.i ----------------------
PHI = 0.001
ALPHA = 0.6
KF = 4.7835616438e9
SOLID_BULK_COMPLIANCE = 1.611901e-11        # = 1/Kd
PERM = 5e-19                                # m^2
MU = 1.002e-3                               # Pa s
P0 = 1e6                                    # Pa
BAR_LENGTH = 4.0                            # m

# Biot modulus, identical to OrcaTHMaterial::computeBiotModulus.
M = 1.0 / ((1.0 - ALPHA) * (ALPHA - PHI) * SOLID_BULK_COMPLIANCE + PHI / KF)

# Hydraulic diffusivity of the rigid-skeleton problem.
C = M * PERM / MU

PROBES = [("p_x0p10", 0.10), ("p_x0p25", 0.25),
          ("p_x0p50", 0.50), ("p_x1p00", 1.00)]

# Times to report. The final time is the one the gold file is compared at; the
# earlier ones check that the diffusivity is right throughout, not just at the
# end -- a wrong c that happened to match at one instant would still drift.
REPORT_TIMES = [100.0, 250.0, 500.0, 1000.0]


def pressure(x, t):
    if t <= 0.0:
        return 0.0
    return P0 * erfc(x / (2.0 * sqrt(C * t)))


def read_csv(path):
    with open(path) as fh:
        header = fh.readline().strip().split(",")
        rows = [[float(v) for v in line.strip().split(",")]
                for line in fh if line.strip()]
    return header, rows


def main():
    here = os.path.dirname(os.path.abspath(__file__))
    csv = os.path.join(here, os.pardir, "test", "tests", "verification",
                       "pressure_diffusion", "gold", "pressure_diffusion_out.csv")
    csv = os.path.normpath(csv)
    if not os.path.exists(csv):
        sys.exit("gold CSV not found: %s\nRun the test first." % csv)

    header, rows = read_csv(csv)
    icol = {name: i for i, name in enumerate(header)}

    print("Biot modulus  M = %.6e Pa" % M)
    print("diffusivity   c = M k / mu = %.10e m^2/s" % C)
    print("diffusion length sqrt(4 c t) at t = 1000 s: %.4f m (bar is %.1f m)"
          % (sqrt(4.0 * C * 1000.0), BAR_LENGTH))
    print("half-space validity: erfc at the far end = %.3e"
          % erfc(BAR_LENGTH / (2.0 * sqrt(C * 1000.0))))
    print()

    # Errors are normalised by the inlet step p0, not by the local value. In the
    # erfc tail the analytic pressure falls below a Pascal while the FE solution
    # keeps a small non-zero foot, so the LOCAL relative error blows up to
    # thousands of percent on an absolute discrepancy of ~0.01 Pa against a
    # 1e6 Pa step. Normalising by p0 is the meaningful measure for a step
    # problem; the local ratio is printed alongside but only where the analytic
    # value is above 0.1% of p0, and is marked "tail" elsewhere.
    TAIL = 1e-3 * P0

    worst = 0.0
    for t_report in REPORT_TIMES:
        row = min(rows, key=lambda r: abs(r[icol["time"]] - t_report))
        t = row[icol["time"]]
        print("t = %.0f s   sqrt(c t) = %.5f m" % (t, sqrt(C * t)))
        print("  %-10s %6s   %14s %14s %10s %10s"
              % ("probe", "x [m]", "numeric [Pa]", "erfc [Pa]", "err/p0", "err/local"))
        for name, x in PROBES:
            num = row[icol[name]]
            ana = pressure(x, t)
            err_p0 = (num - ana) / P0
            worst = max(worst, abs(err_p0))
            if ana > TAIL:
                local = "%9.3f%%" % (100.0 * (num - ana) / ana)
            else:
                local = "      tail"
            print("  %-10s %6.2f   %14.4f %14.4f %9.4f%% %s"
                  % (name, x, num, ana, 100.0 * err_p0, local))
        print()

    far = rows[-1][icol["p_far_end"]]
    print("far end at t = 1000 s: %.3e Pa (must stay at round-off, else the "
          "half-space solution does not apply)" % far)
    print("worst error over all probes and reported times: %.4f%% of p0"
          % (100.0 * worst))


if __name__ == "__main__":
    main()
