#!/usr/bin/env python3
"""OG-SC: is the normal-closure law saturated at Kalantar's stress level?

The material computes (ADOrcaRoughnessDamageFracturePermeability.C:486-493)

    opening(sigma'_n) = V_m * [ g(sigma_ref) - g(sigma'_n) ],
    g(s) = s^p / (sigma_0^p + s^p),   sigma_0 = V_m * K_ni

so the aperture response to a stress change is set entirely by where sigma_0
sits relative to the operating range. Score the deck's constants against
Table 2's own pre-burst pressurization branch, where OG-SC's slip is < 1.2 um
and the closure term is therefore the only thing moving a_h.
"""
import numpy as np
from scipy.optimize import least_squares

V_M, K_NI, P = 1.2e-6, 1.25e13, 4.0          # deck 110_06 as it ran
SIGMA0 = V_M * K_NI

# Table 2, OG-SC, pressurization stages 1-6 (sigma'_n MPa, a_h um). Stage 1 is
# the anchor: initial_hydraulic_aperture and reference_effective_normal_stress
# are both pinned there, so the closure term vanishes at it by construction.
SN = np.array([36.098, 34.59, 33.07, 31.55, 30.02, 28.48])
AH = np.array([1.03,   1.18,  1.23,  1.36,  1.53,  1.60])
SLIP_UM = np.array([0.0, 0.0, 0.0, 1.2, 1.2, 1.2])   # Table 2 dLs, negligible


def g(s_mpa, sigma0_mpa, p):
    return s_mpa ** p / (sigma0_mpa ** p + s_mpa ** p)


def opening_um(sn, vm_um, sigma0_mpa, p):
    return vm_um * (g(SN[0], sigma0_mpa, p) - g(sn, sigma0_mpa, p))


print(f"deck as run:  V_m = {V_M*1e6:.3f} um   K_ni = {K_NI:.3e} Pa/m   "
      f"sigma_0 = {SIGMA0/1e6:.2f} MPa   p = {P:.0f}")
print(f"operating range sigma'_n = {SN.min():.2f} - {SN.max():.2f} MPa  "
      f"-> sigma'_n / sigma_0 = {SN.min()/(SIGMA0/1e6):.2f} - "
      f"{SN.max()/(SIGMA0/1e6):.2f}\n")

print(f"{'stage':>5}{'sn':>8}{'a_h meas':>10}{'need':>8}{'deck gives':>12}{'factor':>8}")
for i, (s, a) in enumerate(zip(SN, AH), 1):
    need = a - AH[0]
    got = opening_um(s, V_M * 1e6, SIGMA0 / 1e6, P)
    f = need / got if got > 1e-9 else np.inf
    print(f"{i:5d}{s:8.2f}{a:10.2f}{need:8.3f}{got:12.4f}{f:8.1f}")

print(f"\n  g(sigma_ref) = {g(SN[0], SIGMA0/1e6, P):.5f}   "
      f"g(sigma_min) = {g(SN[-1], SIGMA0/1e6, P):.5f}   "
      f"span = {g(SN[0], SIGMA0/1e6, P) - g(SN[-1], SIGMA0/1e6, P):.5f}")
print("  The whole 7.6 MPa unloading moves g by that span only: the law is")
print("  saturated, so V_m sets a ceiling the data never gets near.\n")

# Refit V_m and sigma_0 on the same six points, p held at the deck's 4.
def resid(x):
    vm, s0 = x
    return opening_um(SN, vm, s0, P) - (AH - AH[0])

sol = least_squares(resid, [2.0, 30.0], bounds=([0.1, 5.0], [20.0, 60.0]))
vm, s0 = sol.x
print(f"refit on those six points (p held at {P:.0f}):")
print(f"  V_m      = {vm:.3f} um      (deck {V_M*1e6:.3f})")
print(f"  sigma_0  = {s0:.2f} MPa     (deck {SIGMA0/1e6:.2f})")
print(f"  K_ni     = {s0*1e6/(vm*1e-6):.3e} Pa/m   (deck {K_NI:.3e})")
print(f"  RMS residual = {np.sqrt(np.mean(resid(sol.x)**2))*1e3:.1f} nm "
      f"on a 0.57 um swing\n")
print(f"{'stage':>5}{'sn':>8}{'a_h meas':>10}{'a_h refit':>11}{'err %':>8}")
for i, (s, a) in enumerate(zip(SN, AH), 1):
    m = AH[0] + opening_um(s, vm, s0, P)
    print(f"{i:5d}{s:8.2f}{a:10.2f}{m:11.2f}{100*(m-a)/a:8.1f}")
