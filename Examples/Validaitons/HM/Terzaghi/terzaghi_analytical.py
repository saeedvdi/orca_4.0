"""
Terzaghi 1D consolidation — analytical solution and MOOSE comparison.

Problem
-------
A laterally confined column of height H is loaded at its top (z = H) by a
constant compressive stress q at t = 0.  The top face drains freely (p = 0)
while the base (z = 0) is impermeable.

The numerical input starts from p = 0 and applies q during the first transient
increment, matching the MOOSE PorousFlow validation.  The analytical solution
is the state just after loading, t = 0+, where the undrained excess pressure is:

    p0 = alpha*m*q / (S + alpha^2*m)

Governing PDE:
    dp/dt = cv * d^2p/dz^2

    cv = (k / mu) / (S + alpha^2*m)
    S = 1/M,  m = 1/Mc
    Mc = lambda + 2*G  (1-D constrained modulus, oedometric)
    M is the Biot modulus.

BCs:  p(H, t) = 0  (drainage),  dp/dz(0, t) = 0  (impermeable)
IC for analytical curve: p(z, 0+) = p0

Analytical solution  [Terzaghi, 1943]:
    p(z, t) = (4*q/pi) * sum_{n=0}^{inf}
                (-1)^n / (2n+1) * cos(Mn * z/H) * exp(-Mn^2 * Tv)
    where  Mn = (2n+1)*pi/2  and  Tv = cv*t/H^2

Reference: Terzaghi, K. (1943). Theoretical Soil Mechanics. Wiley.

Usage
-----
Run standalone to generate analytical plots:
    python terzaghi_analytical.py

After running MOOSE with Terzaghi_1D.i, CSV output
(Terzaghi_1D.csv) must be in the same directory for comparison plots.
"""

import numpy as np
import matplotlib.pyplot as plt
import sys
from pathlib import Path


def _strip_jupyter_args(argv):
    """Remove IPython kernel flags that are injected into notebook sys.argv."""
    cleaned = []
    skip_next = False
    for arg in argv:
        if skip_next:
            skip_next = False
            continue

        if arg in ('-f', '--f', '--file'):
            skip_next = True
            continue
        if arg.startswith(('-f=', '--f=', '--file=', '--IPKernelApp.connection_file=')):
            continue
        if arg.endswith('.json') and Path(arg).name.startswith('kernel-'):
            continue

        cleaned.append(arg)
    return cleaned


def _csv_from_argv(argv, default='Terzaghi_1D.csv'):
    for arg in _strip_jupyter_args(argv):
        if arg.startswith('-'):
            continue
        return arg
    return default


def _resolve_csv_file(csv_file):
    path = Path(csv_file).expanduser()
    if path.exists() or path.is_absolute():
        return path

    candidates = []
    if '__file__' in globals():
        candidates.append(Path(__file__).resolve().parent / path)
    candidates.append(Path.cwd() / 'Examples' / 'HM' / 'Terzaghi' / path)

    for candidate in candidates:
        if candidate.exists():
            return candidate
    return path

# ============================================================
# Material parameters  — must match Terzaghi_1D.i
# ============================================================
E   = 1e5    # Young's modulus (Pa)
nu  = 0.2    # Poisson's ratio
phi = 0.3    # Initial porosity
k   = 1e-10  # Intrinsic permeability (m^2)
mu  = 1e-3   # Fluid viscosity (Pa·s)
alpha_biot = 1.0  # Biot coefficient
Kf = 1e12   # Fluid bulk modulus (Pa), matching Terzaghi_1D.i

# Derived elastic constants
K  = E / (3.0 * (1.0 - 2.0*nu))   # Drained bulk modulus
G  = E / (2.0 * (1.0 + nu))       # Shear modulus
lam = K - 2.0*G/3.0               # Lamé first parameter
Mc  = lam + 2.0*G                 # 1-D constrained modulus = K + 4G/3

# Biot modulus, storage, and consolidation coefficient consistent with
# OrcaTHMaterial and the MOOSE PorousFlow notation.
# For alpha=1 this gives M=Kf/phi; as Kf -> infinity, cv -> (k/mu)*Mc.
inv_M = (1.0 - alpha_biot) * (alpha_biot - phi) / K + phi / Kf
M = 1.0 / inv_M
S = 1.0 / M
m = 1.0 / Mc
cv = (k / mu) / (S + alpha_biot**2 * m)

# Geometry
H      = 1.0    # Column height (m)
q_load = 1000.0 # Applied compressive stress (Pa)
p0     = alpha_biot * m * q_load / (S + alpha_biot**2 * m)

# Characteristic time
tc = H**2 / cv

print("=" * 50)
print("Terzaghi 1D consolidation — parameters")
print(f"  K  = {K:.1f} Pa,  G = {G:.1f} Pa")
print(f"  Mc = {Mc:.1f} Pa  (constrained modulus)")
print(f"  M  = {M:.3e} Pa   (Biot modulus)")
print(f"  S  = 1/M = {S:.3e} 1/Pa")
print(f"  cv = {cv:.6f} m^2/s")
print(f"  tc = H^2/cv = {tc:.2f} s")
print(f"  p0 = alpha*m*q/(S+alpha^2*m) = {p0:.1f} Pa")
print("=" * 50)


# ============================================================
# Analytical solution
# ============================================================
def terzaghi_pressure(z, t, n_terms=100):
    """
    Normalised pore pressure p(z,t)/p0.

    Parameters
    ----------
    z : float or array  — position from impermeable base (0 ≤ z ≤ H)
    t : float           — time > 0
    """
    Tv = cv * t / H**2
    total = np.zeros_like(np.asarray(z, dtype=float))
    for n in range(n_terms):
        Mn = (2*n + 1) * np.pi / 2.0
        total += ((-1)**n / (2*n + 1)) * np.cos(Mn * np.asarray(z) / H) * np.exp(-Mn**2 * Tv)
    return 4.0 / np.pi * total


def terzaghi_settlement_U(t, n_terms=100):
    """
    Average degree of consolidation U(t) = 1 - sum 8/((2n+1)^2 pi^2) exp(-Mn^2 Tv).
    """
    Tv = cv * t / H**2
    s = 0.0
    for n in range(n_terms):
        Mn = (2*n + 1) * np.pi / 2.0
        s += (1.0 / (2*n + 1)**2) * np.exp(-Mn**2 * Tv)
    return 1.0 - (8.0 / np.pi**2) * s


# ============================================================
# Analytical-only plots
# ============================================================
def plot_analytical():
    Tv_list   = [0.01, 0.05, 0.1, 0.2, 0.5, 1.0, 2.0]
    z_arr     = np.linspace(0, H, 300)
    colors    = plt.cm.viridis(np.linspace(0.05, 0.95, len(Tv_list)))
    Tv_cont   = np.linspace(1e-4, 3.0, 400)

    fig, axes = plt.subplots(1, 2, figsize=(12, 5))
    fig.suptitle('Terzaghi 1D Consolidation — Analytical Solution', fontsize=13)

    # ── Left: pressure profiles p/p0 vs z/H ──
    ax = axes[0]
    for Tv, c in zip(Tv_list, colors):
        t = Tv * tc
        p_norm = terzaghi_pressure(z_arr, t)
        ax.plot(p_norm, z_arr / H, color=c, lw=1.8, label=f'Tv={Tv}')
    ax.set_xlabel('p / p₀', fontsize=11)
    ax.set_ylabel('z / H  (0 = base, 1 = drainage)', fontsize=11)
    ax.set_title('Pore pressure profiles')
    ax.set_xlim([0, 1.05])
    ax.set_ylim([0, 1])
    ax.legend(fontsize=8, loc='lower left')
    ax.grid(True, alpha=0.3)

    # ── Right: degree of consolidation U vs Tv ──
    ax = axes[1]
    U_arr = np.array([terzaghi_settlement_U(Tv * tc) for Tv in Tv_cont])
    ax.plot(Tv_cont, U_arr, 'b-', lw=2, label='Analytical')
    ax.set_xlabel('Tv = cv · t / H²', fontsize=11)
    ax.set_ylabel('U  (degree of consolidation)', fontsize=11)
    ax.set_title('Consolidation curve')
    ax.set_xlim([0, 3])
    ax.set_ylim([0, 1.02])
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('terzaghi_analytical.png', dpi=150, bbox_inches='tight')
    print("Saved terzaghi_analytical.png")


# ============================================================
# Comparison with MOOSE CSV output
# ============================================================
def plot_comparison(csv_file='Terzaghi_1D.csv'):
    try:
        import pandas as pd
    except ImportError:
        print("pandas not available — skipping comparison plot.")
        return

    csv_path = _resolve_csv_file(csv_file)
    if not csv_path.exists():
        print(f"MOOSE CSV not found: {csv_path}")
        print("Run MOOSE with Terzaghi_1D.i first, then re-run this script.")
        return

    df = pd.read_csv(csv_path)
    print(f"\nLoaded MOOSE output: {csv_path}")
    print(f"  Columns : {list(df.columns)}")
    print(f"  Rows    : {len(df)}")

    # MOOSE writes an initial all-zero row before the undrained IC is reflected
    # in the coupled transient solution. Skip it for validation plots.
    df = df[df['time'] > 0.0].copy()
    t_num = df['time'].values

    # Dense analytical time axis
    t_ana = np.linspace(0.01, t_num.max() * 1.05, 600)

    fig, axes = plt.subplots(1, 2, figsize=(13, 5))
    fig.suptitle('Terzaghi 1D Consolidation — Analytical vs MOOSE', fontsize=13)

    # ── Left: p/p0 vs t/tc at several heights ──
    ax = axes[0]

    # z/H values matching the postprocessors in the input file
    monitor_points = [
        ('p_z0',   0.0,   'Impermeable base (z=0)'),
        ('p_z025', 0.25,  'z/H = 0.25'),
        ('p_z050', 0.5,   'z/H = 0.50'),
        ('p_z075', 0.75,  'z/H = 0.75'),
    ]
    clrs = plt.cm.tab10(np.linspace(0, 0.5, len(monitor_points)))

    for (col, z_loc, label), c in zip(monitor_points, clrs):
        p_ana = np.array([terzaghi_pressure(z_loc * H, t) * p0 for t in t_ana])
        ax.plot(t_ana / tc, p_ana / p0, color=c, lw=2, label=f'Analytical ({label})')
        if col in df.columns:
            ax.plot(t_num / tc, df[col].values / p0, 'o', color=c, ms=4,
                    label=f'MOOSE ({label})')

    ax.set_xlabel('t / tc', fontsize=11)
    ax.set_ylabel('p / p₀', fontsize=11)
    ax.set_title('Pore pressure dissipation')
    ax.set_xlim([0, t_num.max() / tc * 1.05])
    ax.set_ylim([-0.02, 1.05])
    ax.legend(fontsize=7, ncol=2)
    ax.grid(True, alpha=0.3)

    # ── Right: degree of consolidation U vs t/tc ──
    ax = axes[1]
    U_initial = H * (q_load - alpha_biot * p0) / Mc
    U_final = q_load * H / Mc  # Drained settlement (m)

    U_ana = np.array([terzaghi_settlement_U(t) for t in t_ana])
    ax.plot(t_ana / tc, U_ana, 'b-', lw=2, label='Analytical')

    if 'uz_top' in df.columns:
        # Settlement is negative (compression). Convert to degree of consolidation
        # relative to the instantaneous undrained and final drained settlements.
        U_moose = (np.abs(df['uz_top'].values) - U_initial) / (U_final - U_initial)
        ax.plot(t_num / tc, U_moose, 'ro', ms=4, label='MOOSE')
        print(f"\n  Expected initial settlement = {U_initial*1e3:.6f} mm")
        print(f"  Expected final settlement = {U_final*1e3:.3f} mm")
        print(f"  MOOSE final settlement    = {np.abs(df['uz_top'].values[-1])*1e3:.3f} mm")

    ax.set_xlabel('t / tc', fontsize=11)
    ax.set_ylabel('U  (degree of consolidation)', fontsize=11)
    ax.set_title('Settlement — analytical vs MOOSE')
    ax.set_xlim([0, t_num.max() / tc * 1.05])
    ax.set_ylim([0, 1.05])
    ax.legend(fontsize=10)
    ax.grid(True, alpha=0.3)

    plt.tight_layout()
    plt.savefig('terzaghi_comparison.png', dpi=150, bbox_inches='tight')
    print("Saved terzaghi_comparison.png")


# ============================================================
if __name__ == '__main__':
    plot_analytical()

    csv = _csv_from_argv(sys.argv[1:])
    plot_comparison(csv)

    plt.show()
