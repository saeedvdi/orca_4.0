"""
Fracture effective-stress coefficient — verification and analytical bounds.

Question
--------
Ye & Ghassemi (2018) decks set `fault_pressure_coefficient` to 0.86 (SW-S4), 0.87 (SW-S3)
and 1.0 (SW-T1/T2); the reference model used 0.935. Is there an analytical way to
determine it, rather than fitting it?

Yes. The coefficient is not free:

    sigma'_n = sigma_n + chi p        with       chi = 1 - A_c/A          [EXACT]

from a force balance across the fracture, `A_c` being the real solid-solid contact area.
The whole question reduces to the contact-area fraction, which two standard closures
bracket. This script does three things:

  1. VERIFIES the identity numerically. `chi_resolved.i` builds the contact patches
     explicitly and never applies a chi; the coefficient is recovered from the force
     balance the solver performs. Sweeping the contact fraction checks chi = 1 - A_c/A
     across the range.
  2. VERIFIES the operator. `chi_homogenized.i` applies a uniform chi and must return it.
  3. BOUNDS chi from material properties, and reports where the values in use fall.

The bound
---------
The asperities carry the whole solid load: sigma'_n = (A_c/A) sigma_c. They cannot carry
more than the indentation hardness H, so sigma_c <= H, and therefore

    A_c/A >= sigma'_n / H          =>      chi <= 1 - sigma'_n / H        [UPPER BOUND]

Note the DIRECTION. Plastic contact is the state of MINIMUM contact area -- it is the one
in which each asperity carries the most it can -- so it bounds chi from ABOVE, not below.
Pushing chi toward 1 means shrinking the contact area, which drives the asperity stress up:

    chi -> 1   =>   A_c/A -> 0   =>   sigma_c -> infinity

so chi = 1 is the value that is strictly unattainable, and small chi is the easy end. That
is the opposite of the intuition that "chi should be about 1 for a fracture", and the
resolved deck's asperity-stress column is what makes it concrete.

H is the main uncertainty, spanning about a factor of seven:

    H ~ 3 x UCS  = 450 MPa   (Tabor's relation applied to the bulk strength)
    H ~ 2-5 GPa              (indentation hardness of the constituent minerals)

giving chi <= 0.933 at the low end and chi <= 0.99 at the high end.

Elastic (Persson) small-load contact is reported for reference, with the RMS surface slope
Z2 from JRC via Tse & Cruden (1979), JRC = 32.2 + 32.47 log10(Z2):

    A_c/A = 4 sigma'_n / (sqrt(pi) E* Z2),      E* = E / (2 (1-nu^2))

but for these stresses it returns contact areas so small that the implied asperity stress
is several GPa, i.e. far past yield. The script reports that implied stress so the
inconsistency is visible rather than hidden.

Usage
-----
    python chi_analytical.py                 # bounds + read whatever decks have run
    python chi_analytical.py --sweep         # also run chi_resolved.i at several A_c/A
    python chi_analytical.py --no-plot

Writes chi_verification_summary.csv and chi_bounds.png next to itself.
"""

import argparse
import csv
import math
import os
import re
import shutil
import subprocess
import sys
import tempfile

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.abspath(os.path.join(HERE, "..", "..", "..", ".."))
ORCA = os.path.join(REPO, "orca-opt")
MPIEXEC = "/home/geomechanics/miniforge/envs/moose/bin/mpiexec"

# Sierra White granite, Ye & Ghassemi (2018). All EXP except H.
E = 67.0e9
NU = 0.32
UCS = 150.0e6
H_INDENT = 3.0 * UCS          # Tabor: indentation hardness ~ 3 x uniaxial strength
E_STAR = E / (2.0 * (1.0 - NU**2))

# Values in use, for reference.
IN_USE = [
    ("SW-T1 / SW-T2", 1.000),
    ("reference model", 0.935),
    ("SW-S3", 0.870),
    ("SW-S4", 0.860),
]


def z2_from_jrc(jrc):
    """RMS surface slope from JRC (Tse & Cruden 1979)."""
    return 10.0 ** ((jrc - 32.2) / 32.47)


def chi_plastic(sigma_eff, hardness=H_INDENT):
    return 1.0 - sigma_eff / hardness


def chi_elastic(sigma_eff, jrc):
    z2 = z2_from_jrc(jrc)
    return 1.0 - 4.0 * sigma_eff / (math.sqrt(math.pi) * E_STAR * z2)


def chi_self_consistent(far_field, pressure, hardness=H_INDENT):
    """Fully plastic contact in equilibrium with its own effective stress.

    sigma'_n = c H  and  sigma'_n = S - (1-c) p  give  c = (S - p)/(H - p), the MINIMUM
    sustainable contact fraction and hence the MAXIMUM chi. Compression-positive magnitudes.
    """
    c = (far_field - pressure) / (hardness - pressure)
    return 1.0 - c, c


def read_csv(path):
    with open(path, newline="") as fh:
        rows = list(csv.DictReader(fh))
    return rows[-1] if rows else None


def run_resolved(fraction, workdir, ranks):
    """Run chi_resolved.i at a given nominal contact fraction."""
    text = open(os.path.join(HERE, "chi_resolved.i")).read()
    text, n = re.subn(r"^contact_fraction = [0-9.eE+-]+", f"contact_fraction = {fraction}",
                      text, count=1, flags=re.M)
    if n != 1:
        raise RuntimeError("could not set contact_fraction")
    deck = os.path.join(workdir, f"chi_c{fraction:.4f}.i")
    open(deck, "w").write(text)
    env = dict(os.environ)
    env["LIBRARY_PATH"] = "/home/geomechanics/miniforge/envs/moose/lib"
    proc = subprocess.run(
        [MPIEXEC, "-n", str(ranks), ORCA, "-i", os.path.basename(deck)],
        cwd=workdir, env=env, capture_output=True, text=True,
    )
    if proc.returncode != 0:
        raise RuntimeError("\n".join(proc.stdout.strip().splitlines()[-12:]))
    return read_csv(os.path.join(workdir, f"chi_c{fraction:.4f}_out.csv"))


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__.strip().split("\n")[0])
    parser.add_argument("--sweep", action="store_true",
                        help="run chi_resolved.i at several contact fractions")
    parser.add_argument("--fractions", type=float, nargs="+",
                        default=[0.05, 0.10, 0.14, 0.20, 0.30])
    parser.add_argument("--ranks", type=int, default=4)
    parser.add_argument("--no-plot", action="store_true")
    args = parser.parse_args(argv)

    print("Fracture effective-stress coefficient  chi = 1 - A_c/A\n")
    print(f"  Sierra White granite:  E = {E/1e9:.0f} GPa, nu = {NU}, UCS = {UCS/1e6:.0f} MPa")
    print(f"  E* = E/(2(1-nu^2)) = {E_STAR/1e9:.2f} GPa      H = 3 UCS = {H_INDENT/1e6:.0f} MPa\n")

    rows = []

    # ---------------------------------------------------------------- verification
    print("  VERIFICATION 1 - the operator (chi_homogenized.i)")
    hom = read_csv(os.path.join(HERE, "chi_homogenized_out.csv"))
    if hom is None:
        print("     not run\n")
    else:
        print(f"     chi set {float(hom['chi_set']):.6f}   chi measured {float(hom['chi_measured']):.6f}"
              f"   sigma'_n error {float(hom['sigma_eff_rel_error']):.2e}")
        print(f"     fracture stayed closed: max normal jump {float(hom['closure_max']):.3e} m\n")
        rows.append({"check": "homogenized operator", "contact_fraction": "",
                     "chi_expected": float(hom["chi_set"]),
                     "chi_measured": float(hom["chi_measured"]),
                     "rel_error": float(hom["sigma_eff_rel_error"])})

    print("  VERIFICATION 2 - the identity chi = 1 - A_c/A (chi_resolved.i)")
    print("     the deck applies NO chi; it is recovered from the force balance\n")
    results = []
    if args.sweep:
        if not os.path.exists(ORCA):
            print(f"     orca-opt not found at {ORCA}", file=sys.stderr)
            return 1
        workdir = tempfile.mkdtemp(prefix="chi_sweep_")
        try:
            for frac in args.fractions:
                print(f"     A_c/A = {frac:.4f} ... ", end="", flush=True)
                last = run_resolved(frac, workdir, args.ranks)
                results.append(last)
                print(f"chi = {float(last['chi_measured']):.7f}")
        finally:
            shutil.rmtree(workdir, ignore_errors=True)
        print()
    else:
        last = read_csv(os.path.join(HERE, "chi_resolved_out.csv"))
        if last:
            results.append(last)

    if results:
        print(f"     {'A_c/A realized':>15s} {'chi = 1-A_c/A':>14s} {'chi measured':>14s} "
              f"{'rel error':>11s} {'asperity stress':>16s}")
        for last in results:
            c = float(last["contact_fraction_realized"])
            print(f"     {c:15.6f} {float(last['chi_analytic']):14.7f} "
                  f"{float(last['chi_measured']):14.7f} {float(last['chi_rel_error']):11.2e} "
                  f"{abs(float(last['sigma_c_mean']))/1e6:13.2f} MPa")
            rows.append({"check": "resolved contact patches",
                         "contact_fraction": c,
                         "chi_expected": float(last["chi_analytic"]),
                         "chi_measured": float(last["chi_measured"]),
                         "rel_error": float(last["chi_rel_error"])})
        print()

    # ---------------------------------------------------------------- bounds
    far, p = 30.0e6, 0.0
    print(f"  UPPER BOUND on chi at sigma'_n = {far/1e6:.0f} MPa")
    print(f"     {'H':>12s} {'source':>34s} {'min A_c/A':>11s} {'max chi':>9s}")
    bounds = {}
    for hardness, src in ((3.0 * UCS, "Tabor, H = 3 x UCS"),
                          (2.0e9, "mineral indentation, low"),
                          (5.0e9, "mineral indentation, high")):
        cb = chi_plastic(far, hardness)
        bounds[src] = cb
        print(f"     {hardness/1e6:9.0f} MPa {src:>34s} {far/hardness:11.5f} {cb:9.5f}")
        rows.append({"check": f"upper bound ({src})", "contact_fraction": far / hardness,
                     "chi_expected": cb, "chi_measured": "", "rel_error": ""})
    chi_max = chi_plastic(far, 5.0e9)   # the most permissive credible bound
    chi_max_tabor = chi_plastic(far, 3.0 * UCS)
    print()

    print("  ELASTIC (Persson) estimate, and why it is not usable here")
    print(f"     {'JRC':>5s} {'A_c/A':>9s} {'chi':>8s} {'implied asperity stress':>25s}")
    for jrc in (25.0, 5.0, 0.0):
        ce = chi_elastic(far, jrc)
        ac = 1.0 - ce
        print(f"     {jrc:5.1f} {ac:9.5f} {ce:8.5f} {far/ac/1e9:22.2f} GPa")
    print("     Every one of those exceeds any credible indentation hardness, so the")
    print("     asperities would yield and the contact area would grow until sigma_c = H.")
    print("     The small-load elastic limit does not apply at 30 MPa on granite.\n")

    print("  SELF-CONSISTENT fully plastic chi during injection (H = 3 x UCS)")
    print(f"     {'p (MPa)':>9s} {'min A_c/A':>11s} {'max chi':>9s}")
    for pp in (0.0, 5.0e6, 10.0e6, 15.0e6, 20.0e6):
        chi_sc, c_sc = chi_self_consistent(far, pp)
        print(f"     {pp/1e6:9.1f} {c_sc:11.5f} {chi_sc:9.5f}")
        rows.append({"check": f"max chi, fully plastic, p={pp/1e6:.0f} MPa",
                     "contact_fraction": c_sc, "chi_expected": chi_sc,
                     "chi_measured": "", "rel_error": ""})
    print("     chi rises toward 1 as injection unclamps the fracture, so a CONSTANT chi")
    print("     has the wrong trend whatever value is chosen.\n")

    print("  VALUES IN USE, and what each implies")
    print(f"     {'':18s} {'chi':>7s} {'A_c/A':>8s} {'asperity stress':>17s}  verdict")
    for name, chi in IN_USE:
        ac = 1.0 - chi
        sc = far / ac if ac > 0 else float("inf")
        if ac <= 0.0:
            verdict = "IMPOSSIBLE - needs zero contact area"
        elif chi > chi_max:
            verdict = "above every credible bound"
        elif chi > chi_max_tabor:
            verdict = "feasible only if H > 3 x UCS"
        else:
            verdict = "feasible"
        sstr = f"{sc/1e6:14.0f} MPa" if math.isfinite(sc) else "           inf"
        print(f"     {name:18s} {chi:7.3f} {ac:8.4f} {sstr}   {verdict}")
        rows.append({"check": f"in use: {name}", "contact_fraction": ac,
                     "chi_expected": "", "chi_measured": chi, "rel_error": verdict})
    print()
    print("     So the saw-cut values are the PHYSICALLY COMFORTABLE ones: 0.86 needs the")
    print("     asperities to carry 214 MPa, well inside any hardness. It is chi = 1.0 on")
    print("     the tensile fractures that is unattainable in the strict sense - it needs")
    print("     no contact at all - though as an idealization it is only ~1-7 % past the")
    print("     bound. The physically expected ORDERING, a lower chi on the better-mated")
    print("     saw cut and chi near 1 on the rough tensile fracture, is what the decks")
    print("     already encode.\n")

    out = os.path.join(HERE, "chi_verification_summary.csv")
    with open(out, "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=["check", "contact_fraction", "chi_expected",
                                           "chi_measured", "rel_error"])
        w.writeheader()
        w.writerows(rows)
    print(f"  wrote {out}")

    if args.no_plot:
        return 0
    try:
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
    except ImportError:
        print("  matplotlib not available — skipping the figure")
        return 0

    plt.rcParams.update(
        {
            "font.family": "serif",
            "font.serif": ["Times New Roman", "DejaVu Serif", "serif"],
            "mathtext.fontset": "dejavuserif",
            "font.size": 20,
            "axes.titlesize": 22,
            "axes.labelsize": 22,
            "xtick.labelsize": 18,
            "ytick.labelsize": 18,
            "legend.fontsize": 18,
        }
    )

    fig1, ax1 = plt.subplots(figsize=(10.0, 7.5))
    c = np.linspace(0.0, 0.35, 200)
    ax1.plot(c, 1.0 - c, "-", color="0.25", lw=2, label=r"$\chi = 1 - A_c/A$  (exact)")
    if results:
        ax1.plot([float(r["contact_fraction_realized"]) for r in results],
                 [float(r["chi_measured"]) for r in results],
                 "o", ms=9, mfc="tab:orange", mec="k", label="Orca, resolved patches")
    ax1.set_xlabel(r"real contact area fraction  $A_c/A$")
    ax1.set_ylabel(r"effective stress coefficient  $\chi$")
    ax1.set_title("Verification: the identity holds")
    ax1.grid(alpha=0.3)
    ax1.legend(frameon=False)
    fig1.tight_layout()
    out1 = os.path.join(HERE, "chi_bounds_verification.png")
    fig1.savefig(out1, dpi=600)
    plt.close(fig1)
    print(f"  wrote {out1}")

    fig2, ax2 = plt.subplots(figsize=(10.0, 7.5))
    sig = np.linspace(1e6, 45e6, 200)
    ax2.plot(sig / 1e6, chi_plastic(sig, 3.0 * UCS), "-", color="tab:red", lw=2,
             label=r"upper bound, $H=3\,$UCS $=450$ MPa")
    ax2.plot(sig / 1e6, chi_plastic(sig, 5.0e9), "--", color="tab:red", lw=1.4,
             label=r"upper bound, $H=5$ GPa")
    ax2.fill_between(sig / 1e6, 0.0, chi_plastic(sig, 3.0 * UCS),
                     color="tab:green", alpha=0.10)
    ax2.text(15, 0.875, "attainable\n($H=3\\,$UCS)", fontsize=16, color="tab:green", ha="center")
    for name, chi in IN_USE:
        ax2.axhline(chi, color="0.5", lw=0.8, ls="-." if chi < 0.9 else "-", alpha=0.8)
        ax2.text(44.5, chi + 0.002, f"{name}  {chi:.3f}", fontsize=14, ha="right", va="bottom")
    ax2.axvline(30.0, color="0.3", lw=0.8)
    ax2.text(30.4, 0.845, "Ye 2018\nconfining", fontsize=14, color="0.3")
    ax2.set_xlabel(r"effective normal stress  $\sigma'_n$  (MPa)")
    ax2.set_ylabel(r"$\chi$")
    ax2.set_ylim(0.84, 1.03)
    ax2.set_xlim(0, 45)
    ax2.set_title("Bounds, and the values in use")
    ax2.grid(alpha=0.3)
    ax2.legend(frameon=False, loc="lower left")
    fig2.tight_layout()
    out2 = os.path.join(HERE, "chi_bounds_values.png")
    fig2.savefig(out2, dpi=600)
    plt.close(fig2)
    print(f"  wrote {out2}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
