"""Refit the HYDRAULIC Barton-Bandis closure law from Table 2's pre-event aperture.

Model (ADOrcaRoughnessDamageFracturePermeability::computeStressAperture, type 0):
    a_h(N) = a_h0 + V_h * [ g(N_ref) - g(N) ],   g(N) = N^p / (sigma0^p + N^p),
    sigma0 = V_h * K_h.
Pre-event there is no dilation, no slip damage and (kinematic mode, joint in
contact) no mechanical-gap term, so this IS the whole aperture model.
Fit (V_h, sigma0) on stages 1-5 with p fixed at the deck value, then report the
K_h that reproduces sigma0.
"""
import sys, numpy as np
from pathlib import Path

ROOT=Path("/media/geomechanics/Data4TB/projects/orca_4.0"); sys.path.insert(0,str(ROOT/"scripts"))
import table2_gate as G

DECK = {  # V_h [m], K_h [Pa/m], p, N_ref [Pa], nonlinear on?
 "SWT1": (1.2e-6, 1.25e13, 4.0, 65.47e6, False),
 "SWT2": (1.2e-6, 1.25e13, 4.0, 66.74e6, True),
 "SWS3": (1.2e-6,  1.25e13, 4.0, 32.1e6, True),
 "SWS4": (1.05e-6, 1.43e13, 2.0, 31.0e6, True),
}

def a_of_N(N, Vh, s0, p, Nref, a0):
    g = lambda x: x**p/(s0**p + x**p)
    return a0 + Vh*(g(Nref) - g(N))

for s in ["SWT1","SWT2","SWS3","SWS4"]:
    Vh0, Kh0, p, Nref, nl = DECK[s]
    ah = np.asarray(G.TABLE2[s]["ah_um"],float)[:5]*1e-6
    sn = np.asarray(G.TABLE2[s]["sigma_n_MPa"],float)[:5]*1e6
    a0 = ah[0]                      # deck's initial_hydraulic_aperture, held fixed
    s0_deck = Vh0*Kh0
    pred_deck = a_of_N(sn, Vh0, s0_deck, p, Nref, a0)
    def resid(q):
        Vh, s0 = np.exp(q)
        return (a_of_N(sn, Vh, s0, p, Nref, a0) - ah)*1e9   # nm
    # brute-force grid + local refine; only two parameters, no scipy needed
    best=None
    for lv in np.linspace(np.log(1e-7), np.log(5e-5), 400):
        for ls in np.linspace(np.log(5e6), np.log(5e8), 400):
            c=float(np.sum(resid(np.array([lv,ls]))**2))
            if best is None or c<best[0]: best=(c,lv,ls)
    c,lv,ls=best
    for step in [0.05,0.01,0.002,0.0004]:
        improved=True
        while improved:
            improved=False
            for dv,ds in [(step,0),(-step,0),(0,step),(0,-step),(step,step),(-step,-step),(step,-step),(-step,step)]:
                cc=float(np.sum(resid(np.array([lv+dv,ls+ds]))**2))
                if cc<c: c,lv,ls=cc,lv+dv,ls+ds; improved=True
    Vh, s0 = np.exp([lv,ls])
    pred = a_of_N(sn, Vh, s0, p, Nref, a0)
    print("="*92)
    print(f"{s}   p = {p}   N_ref = {Nref/1e6:.2f} MPa   a_h0 = {a0*1e6:.3f} um   nonlinear_flag={nl}")
    print(f"   deck   V_h = {Vh0*1e6:8.4f} um   K_h = {Kh0:9.3e} Pa/m   sigma0 = {s0_deck/1e6:8.3f} MPa"
          f"   max|err| = {np.abs(pred_deck-ah).max()*1e6:7.4f} um")
    print(f"   FIT    V_h = {Vh*1e6:8.4f} um   K_h = {s0/Vh:9.3e} Pa/m   sigma0 = {s0/1e6:8.3f} MPa"
          f"   max|err| = {np.abs(pred-ah).max()*1e6:7.4f} um")
    print(f"   {'sn MPa':>9}{'a_h paper':>11}{'a_h deck':>11}{'a_h fit':>11}   (um)")
    for i in range(5):
        print(f"   {sn[i]/1e6:>9.2f}{ah[i]*1e6:>11.3f}{pred_deck[i]*1e6:>11.3f}{pred[i]*1e6:>11.3f}")
