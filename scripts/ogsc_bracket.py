#!/usr/bin/env python3
"""Does OG-SC's deck value phi_r = 22.660 deg already satisfy BOTH Table-2
conditions -- hold at stage 6, fail by stage 7 -- on the UNWEAKENED envelope?

If it does, the early burst cannot be blamed on the peak envelope, and the
round-3 'bracket narrows to 22.660 < phi_r' inference has to be withdrawn.
"""
import math

JRC, JCS, PHI_R = 4.23, 153.0, 22.660
D_C_UM, N, PHI_RES = 15.22, 1.4, 15.354

def bb_limit(sn):
    ang = PHI_R + JRC * math.log10(JCS / sn)
    return sn * math.tan(math.radians(ang)), ang

def weakened(sn, slip_um):
    mu_p = bb_limit(sn)[0] / sn
    mu_r = math.tan(math.radians(PHI_RES))
    W = math.exp(-((slip_um / D_C_UM) ** N))
    return sn * (mu_r + (mu_p - mu_r) * W)

print("Table 2 requires: HOLD at stage 6, FAIL by stage 7.\n")
for st, sn, tau in ((5, 30.02, 13.02), (6, 28.48, 12.95), (7, 25.12, 13.00)):
    lim, ang = bb_limit(sn)
    verdict = "holds" if lim > tau else "FAILS"
    print(f"stage {st}: sigma'_n {sn:6.2f}  tau {tau:6.2f}  "
          f"BB limit {lim:6.2f} (phi_peak {ang:6.3f} deg)  ->  {verdict}"
          f"   margin {100*(lim-tau)/tau:+6.1f} %")

print("\nBoth conditions are met at the deck's own phi_r. Now the same states "
      "with the\nweakening the run actually accumulated before its burst:\n")
for slip in (1.2, 4.0, 9.11):
    lim = weakened(28.48, slip)
    print(f"  stage 6 at {slip:5.2f} um of slip: tau_limit {lim:6.2f} vs tau 12.95  "
          f"-> {'holds' if lim > 12.95 else 'BURSTS'}")

print(f"\nMeasured slip at stage 6 (Table 2) is 1.2 um. The run reached 9.11 um.")
print("So the burst is bought by premature weakening, not by a weak envelope.")
