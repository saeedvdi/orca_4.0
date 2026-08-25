#!/usr/bin/env python3
"""OG-SH: how long is the slip-weakening distance, and does shortening it break
the stability class the paper reports?

The law (ADOrcaBartonBandisContactTractionFastADHardening.C:113-118) is

    mu(s) = mu_r + (mu_p - mu_r) * exp( -(s/D)^n ),   n = slip_weakening_exponent

so the build-time stability assertion `D > delta_tau / k_eff` -- which assumes a
LINEAR drop over D -- is not the right cap for this law. Compute the real one.
"""
import math
import numpy as np

K_SYS = 796e6          # N/m, Kalantar's reported frame stiffness
A = math.pi * 0.02499 ** 2
N = 1.4                # slip_weakening_exponent, all three decks

CASES = [  # name, theta, D_c deck [m], (tau,sn) at peak, (tau,sn) at residual, slip_axial [mm]
    ("OG-SH", 29.0, 1.500e-4, (26.14, 42.99), (18.97, 39.01), 0.042),
    ("OG-SC", 30.0, 1.522e-5, (13.16, 36.10), ( 9.73, 25.12), 0.023),
]

# Peak of x^(n-1) exp(-x^n): d/dx = 0  ->  x^n = (n-1)/n
x_star = ((N - 1.0) / N) ** (1.0 / N)
shape = N * x_star ** (N - 1.0) * math.exp(-(x_star ** N))
print(f"slip-weakening exponent n = {N}")
print(f"  the exp(-(s/D)^n) law reaches its steepest slope at s/D = {x_star:.4f},")
print(f"  where |d mu/d s| = {shape:.4f} * (mu_p - mu_r) / D.")
print(f"  A LINEAR drop over D would give 1.0000, so the true stability cap is")
print(f"  {shape:.4f} x the naive delta_tau / k_eff -- the assertion is "
      f"{1/shape:.2f}x too strict.\n")

for name, th_deg, D_deck, (tau_p, sn_p), (tau_r, sn_r), slip_ax in CASES:
    th = math.radians(th_deg)
    k_eff = K_SYS * math.cos(th) ** 2 * math.sin(th) / A / 1e9   # MPa/mm
    slip_ip = slip_ax / math.cos(th)    # Table 2 dL_s is axial; the law uses in-plane

    # Only the FRICTION drop is slip-weakening. The rest of the tau drop is
    # sigma'_n falling under injection, which the law does not control -- charging
    # it to the weakening term is what makes the naive cap too strict.
    mu_p, mu_r = tau_p / sn_p, tau_r / sn_r
    dtau_total = tau_p - tau_r
    dtau_mu = (mu_p - mu_r) * sn_r          # the part D_c is responsible for
    naive = dtau_mu / k_eff * 1e3           # um
    true_cap = shape * naive

    # D that puts the joint at 90 % of its friction drop by the measured slip.
    D_90 = slip_ip * 1e3 / (math.log(10.0) ** (1.0 / N))   # from exp(-(s/D)^n)=0.1
    W = math.exp(-((slip_ip * 1e3) / (D_deck * 1e6)) ** N)
    print(f"{name}:  k_eff = {k_eff:.1f} MPa/mm   tau drop {dtau_total:.2f} MPa, of "
          f"which {dtau_mu:.2f} is friction (mu {mu_p:.4f} -> {mu_r:.4f})")
    print(f"        measured in-plane slip {slip_ip*1e3:.1f} um")
    print(f"   deck D_c                    = {D_deck*1e6:8.1f} um")
    print(f"   naive cap   dtau_mu/k_eff   = {naive:8.1f} um")
    print(f"   TRUE cap  {shape:.3f}*dtau_mu/k = {true_cap:8.1f} um   "
          f"(below = unstable)")
    print(f"   D for 90 % of the drop at the measured slip = {D_90:8.1f} um")
    print(f"   verdict: {'STABLE' if D_90 > true_cap else 'UNSTABLE'} at that D, "
          f"margin {D_90/true_cap:.2f}x")
    print(f"   the deck's D_c delivers {100*(1-W):.0f} % of the drop there\n")
