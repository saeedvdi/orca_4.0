#!/usr/bin/env python3
"""
Decompose the hydraulic-aperture budget of the four Ye & Ghassemi decks of record,
term by term, at the eleven Table-2 hold stages.

This is the arithmetic behind the manuscript's self-propping claim. The material
ADOrcaRoughnessDamageFracturePermeability assembles

    a_h = clamp[ a_h0 + a_sigma + chi*a_m + lambda*Delta_cum*r(R) + a_prop
                 - a_gouge - a_creep ; a_min, a_max ],
    r(R) = r_res + (1 - r_res) R,

and every one of those terms is an exported postprocessor except the two products
chi*a_m and lambda*Delta_cum*r(R), which are formed here from the deck constants.
The residual column is a_h minus the reconstructed sum: it is the clamp, and it is
the only way to see when a_min is carrying the answer instead of the physics.

Stage sampling is delegated to scripts/table2_gate.py so the rows line up exactly
with the scored table.

Usage:
    python3 scripts/aperture_budget_decomposition.py [--csv]
"""

import sys
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import table2_gate as gate  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
YE = ROOT / "Examples/YeGhasemmi2018"

# deck constants, read from the four decks of record (grep-checked, not inferred)
RUNS = {
    "SW-T1": dict(
        csv="SWT1/Sweeps/results_csv_local/107_01_swt1_coh27p2_apscale0p01512_ppfix.csv",
        a_h0=1.63e-6, chi=0.01512, lam=0.0, r_res=0.714876033058,
        a_prop=0.0, a_min=1.5105e-6, a_max=8e-6, kinematic=True,
    ),
    "SW-T2": dict(
        csv="SWT2/Sweeps/results_csv_hpc_rorqual/100_04_swt2_apscale0p0177_ppfix_hpc.csv",
        a_h0=2.11e-6, chi=0.0177, lam=0.0, r_res=0.747330960854,
        a_prop=0.0, a_min=2.0045e-6, a_max=8e-6, kinematic=True,
    ),
    "SW-S3": dict(
        csv="SWS3/Sweeps/results_csv_hpc_rorqual/100_06_sw3_resc1p30_unld0p00_ppfix_hpc.csv",
        a_h0=1.22e-6, chi=0.001, lam=0.038, r_res=0.28,
        a_prop=0.0, a_min=1.22e-6, a_max=8e-6, kinematic=False,
    ),
    "SW-S4": dict(
        csv="SWS4/Sweeps/results_csv_hpc_rorqual/93_07_sw4_final_theta30_jrc5_ppfix_hpc.csv",
        a_h0=0.74e-6, chi=0.001, lam=0.0117, r_res=0.28,
        a_prop=0.0, a_min=0.74e-6, a_max=8e-6, kinematic=False,
    ),
}

SAMPLE = {"SW-T1": "SWT1", "SW-T2": "SWT2", "SW-S3": "SWS3", "SW-S4": "SWS4"}


def stage_rows(csv_path: Path, sample: str) -> tuple[pd.DataFrame, list[int | None]]:
    """Return the raw CSV and the row index sampled at each of the eleven stages."""
    deck = gate.find_deck(csv_path, None)
    x, y = gate.parse_schedule(deck)
    times = gate.stage_times(x, y, 0.15)

    raw = pd.read_csv(csv_path)
    raw = raw.sort_values("time").drop_duplicates("time", keep="last").reset_index(drop=True)
    t = pd.to_numeric(raw["time"], errors="coerce")
    t_end = float(t.iloc[-1])
    grace = 2.0 * float(np.median(np.diff(t))) if len(t) > 2 else 0.0

    rows: list[int | None] = []
    for st in times:
        if st > t_end + grace:
            rows.append(None)
        else:
            rows.append(int(t.index[t <= min(st, t_end)][-1]))
    return raw, rows


def budget(label: str) -> pd.DataFrame:
    cfg = RUNS[label]
    raw, rows = stage_rows(YE / cfg["csv"], SAMPLE[label])

    def col(name):
        return pd.to_numeric(raw[name], errors="coerce") if name in raw.columns else pd.Series(
            np.nan, index=raw.index)

    um = 1e6
    a_h = col("hydraulic_aperture_um_pp")
    a_sig = col("normal_stress_aperture_um_pp")
    a_m = col("mechanical_aperture_pp") * um
    dcum = col("cumulative_dilation_pp") * um
    R = col("roughness_state_pp").clip(0.0, 1.0)
    a_g = col("slip_damage_aperture_um_pp")
    k13 = col("fracture_permeability_1e13_m2_pp")
    sn = col("bb_effective_normal_stress_pp")
    slip = col("cumulative_plastic_slip_pp") * um

    r_fac = cfg["r_res"] + (1.0 - cfg["r_res"]) * R
    chi_am = cfg["chi"] * a_m
    lam_term = 0.0 * a_m if cfg["kinematic"] else cfg["lam"] * dcum * r_fac

    recon = cfg["a_h0"] * um + a_sig + chi_am + lam_term + cfg["a_prop"] * um - a_g

    out = []
    for i, r in enumerate(rows, start=1):
        if r is None:
            continue
        out.append(dict(
            specimen=label, stage=i,
            sigma_n_MPa=float(sn.iloc[r]),
            slip_um=float(slip.iloc[r]),
            R=float(R.iloc[r]),
            a_h0=cfg["a_h0"] * um,
            a_sigma=float(a_sig.iloc[r]),
            chi_am=float(chi_am.iloc[r]),
            lam_dil=float(lam_term.iloc[r]) if not cfg["kinematic"] else 0.0,
            a_gouge=float(a_g.iloc[r]),
            recon=float(recon.iloc[r]),
            a_h=float(a_h.iloc[r]),
            clamp=float(a_h.iloc[r]) - float(recon.iloc[r]),
            a_h_paper=gate.TABLE2[SAMPLE[label]]["ah_um"][i - 1],
            k_1e13=float(k13.iloc[r]),
        ))
    return pd.DataFrame(out)


def main() -> int:
    frames = [budget(k) for k in RUNS]
    full = pd.concat(frames, ignore_index=True)

    if "--csv" in sys.argv:
        dest = YE / "Docs/Memory/APERTURE_BUDGET_DECOMPOSITION.csv"
        full.to_csv(dest, index=False, float_format="%.4f")
        print(f"wrote {dest}")

    pd.set_option("display.width", 200)
    for label, f in zip(RUNS, frames):
        print(f"\n=== {label}   (all apertures in um)")
        print(f[["stage", "sigma_n_MPa", "slip_um", "R", "a_sigma", "chi_am", "lam_dil",
                 "a_gouge", "recon", "a_h", "clamp", "a_h_paper", "k_1e13"]]
              .to_string(index=False, float_format=lambda v: f"{v:9.4f}"))

    # Headline: floor -> peak -> floor, model against Table 2.
    print("\n=== self-propping summary (stage 1 floor, stage 6 peak, stage 11 floor)")
    hdr = ("spec   a1_mod a1_pap  a6_mod a6_pap  a11_mod a11_pap | "
           "gain_mod gain_pap  ret_mod ret_pap | k1 k6 k11 (1e-13 m2)  T11/T1 mod pap")
    print(hdr)
    for label, f in zip(RUNS, frames):
        g = f.set_index("stage")
        if not {1, 6, 11}.issubset(set(g.index)):
            print(f"{label}  incomplete: stages {sorted(g.index)}")
            continue
        a1, a6, a11 = (g.loc[s, "a_h"] for s in (1, 6, 11))
        p1, p6, p11 = (g.loc[s, "a_h_paper"] for s in (1, 6, 11))
        k1, k6, k11 = (g.loc[s, "k_1e13"] for s in (1, 6, 11))
        print(f"{label} {a1:6.3f} {p1:6.3f}  {a6:6.3f} {p6:6.3f}  {a11:6.3f} {p11:6.3f} | "
              f"{a6/a1:7.3f} {p6/p1:7.3f}  {(a11-a1)/(a6-a1) if a6>a1 else float('nan'):7.3f} "
              f"{(p11-p1)/(p6-p1) if p6>p1 else float('nan'):7.3f} | "
              f"{k1:6.3f} {k6:6.3f} {k11:6.3f}  {(a11/a1)**3:6.3f} {(p11/p1)**3:6.3f}")
    # Which term supplies the retained aperture at the final floor stage.
    print("\n=== attribution of the retained aperture at stage 11 (um, and % of the retained excess)")
    print("spec    a_h11   a_h0   excess |   a_sigma     chi*a_m    lam*dil    -a_gouge   clamp")
    for label, f in zip(RUNS, frames):
        g = f.set_index("stage")
        if 11 not in g.index:
            print(f"{label}  no stage 11")
            continue
        r = g.loc[11]
        exc = r["a_h"] - r["a_h0"]
        parts = [("a_sigma", r["a_sigma"]), ("chi_am", r["chi_am"]),
                 ("lam_dil", r["lam_dil"]), ("-a_gouge", -r["a_gouge"]),
                 ("clamp", r["clamp"])]
        cells = "  ".join(f"{v:6.3f} ({100*v/exc:5.1f}%)" for _, v in parts)
        print(f"{label} {r['a_h']:6.3f} {r['a_h0']:6.3f} {exc:7.3f} | {cells}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
