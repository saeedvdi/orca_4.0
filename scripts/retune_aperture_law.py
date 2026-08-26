"""Retune the aperture law of a completed run against Ye & Ghassemi Table 2 FLOW.

The hydraulic aperture assembled by ADOrcaRoughnessDamageFracturePermeability is

    a_h = a_h0 + stress_aperture + aperture_scale*mechanical_aperture
          + dilation + self_prop - slip_damage_fill            (clamped)

and Table 2's flow follows the cubic law Q ~ a_h^3 dP.  Every completed run
exports `hydraulic_aperture_um_pp` and `normal_stress_aperture_um_pp`, so the
stress term can be swapped for a candidate law *exactly* while every other
contribution is carried over unchanged:

    a_h_new = a_h_model - stress_aperture_old + stress_aperture_new
    Q_new   = Q_model * (a_h_new / a_h_model)^3

Two candidate laws are fitted, both already implemented in the material:

  LINEAR   stress_aperture = C_n * (N_ref - N)                 [compliance branch]
  BB       stress_aperture = V_h * [g(N_ref) - g(N)],
           g(N) = N^p/(sigma0^p + N^p),  sigma0 = V_h*K_h      [nonlinear branch]

For the mode-I specimens `aperture_scale` is fitted jointly, because there the
mechanical term is recoverable in closed form (nothing else contributes).

CAVEAT: aperture feeds back into pressure diffusion and hence into sigma'_n, so
this is a calibration proposal, not a prediction.  It ranks candidates; the deck
still has to be run.
"""
import sys
import numpy as np
import pandas as pd
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
import table2_gate as G
from table2_gate import score_run

RUNS = {
    #                csv (relative to ROOT)                                              tag        a_h0   scale   N_ref[Pa]  p   fit_scale
    "SWT1": ("Examples/YeGhasemmi2018/SWT1/results_csv_hpc_rorqual/100_01_swt1_vm55um_ppfix_hpc.csv",
             "100_01", 1.63e-6, 0.016, 65.47e6, 4.0, True),
    "SWT2": ("Examples/YeGhasemmi2018/SWT2/results_csv_hpc_rorqual/100_04_swt2_apscale0p0177_ppfix_hpc.csv",
             "100_04", 2.11e-6, 0.0177, 66.74e6, 4.0, True),
    "SWS3": ("Examples/YeGhasemmi2018/SWS3/results_csv_hpc_rorqual/100_06_sw3_resc1p30_unld0p00_ppfix_hpc.csv",
             "100_06", 1.22e-6, 0.001, 32.1e6, 4.0, False),
    "SWS4": ("Examples/YeGhasemmi2018/SWS4/results_csv_hpc_rorqual/93_07_sw4_final_theta30_jrc5_ppfix_hpc.csv",
             "93_07", 0.74e-6, 0.001, 31.0e6, 2.0, False),
}


def bb_gap(N, s0, p):
    return N ** p / (s0 ** p + N ** p)


def stage_frame(sample):
    csv, tag, a0, scale, nref, p, fit_scale = RUNS[sample]
    path = ROOT / csv
    res = score_run(path, sample, tag, 0.15, "stage1", 55.0)
    tab = res["table"]
    raw = pd.read_csv(path)
    pick = lambda col: np.array([raw.iloc[(raw["time"] - t).abs().idxmin()][col]
                                 for t in tab["stage_time_s"]])
    return dict(
        tag=tag, a0=a0, scale=scale, nref=nref, p=p, fit_scale=fit_scale,
        sn=tab["sigma_n_MPa_model"].to_numpy() * 1e6,
        ah=pick("hydraulic_aperture_um_pp") * 1e-6,
        sa=pick("normal_stress_aperture_um_pp") * 1e-6,
        q_model=tab["Q_ml_min_model"].to_numpy(),
        q_paper=tab["Q_ml_min_paper"].to_numpy(),
        ah_paper=np.asarray(G.TABLE2[sample]["ah_um"], float) * 1e-6,
    )


def q_rmse(f, q_new):
    """Range-normalised Q RMSE in %, the table2_gate convention."""
    rng = f["q_paper"].max() - f["q_paper"].min()
    return 100.0 * float(np.sqrt(np.mean((q_new - f["q_paper"]) ** 2))) / rng


def predict(f, sa_new, scale_new):
    base = f["ah"] - f["sa"]
    if f["fit_scale"]:
        mech = (f["ah"] - f["a0"] - f["sa"]) / f["scale"]
        base = f["a0"] + scale_new * mech
    ah_new = np.maximum(base + sa_new, f["a0"])
    return ah_new, f["q_model"] * (ah_new / f["ah"]) ** 3


def report(sample):
    f = stage_frame(sample)
    print("=" * 108)
    print(f"{sample}  ({f['tag']})   N_ref = {f['nref']/1e6:.2f} MPa   p = {f['p']}   "
          f"a_h0 = {f['a0']*1e6:.3f} um   sigma'_n range {f['sn'].min()/1e6:.1f}-{f['sn'].max()/1e6:.1f} MPa")
    print(f"   as-run                                              Q RMSE = {q_rmse(f, f['q_model']):6.3f} %"
          f"    max|a_h err| = {np.abs(f['ah']-f['ah_paper']).max()*1e6:.3f} um")

    scales = np.linspace(0.5 * f["scale"], 1.2 * f["scale"], 141) if f["fit_scale"] else np.array([f["scale"]])
    best = {}

    # ---- LINEAR compliance branch -------------------------------------------------
    grid = np.linspace(0.0, 6.0e-14, 601)
    cand = [(q_rmse(f, predict(f, c * (f["nref"] - f["sn"]), s)[1]), c, s) for c in grid for s in scales]
    e, c, s = min(cand)
    best["linear"] = (e, dict(normal_stress_aperture_compliance=c, aperture_scale=s))
    ah_lin = predict(f, c * (f["nref"] - f["sn"]), s)[0]
    print(f"   LINEAR   C_n = {c:.4e} m/Pa   aperture_scale = {s:.5f}      Q RMSE = {e:6.3f} %"
          f"    max|a_h err| = {np.abs(ah_lin-f['ah_paper']).max()*1e6:.3f} um")

    # ---- BB power-law branch ------------------------------------------------------
    gref = bb_gap(f["nref"], None, None) if False else None
    cand = []
    for vh in np.geomspace(0.05e-6, 60e-6, 200):
        for s0 in np.geomspace(1.5e6, 3e8, 260):
            sa = vh * (bb_gap(f["nref"], s0, f["p"]) - bb_gap(f["sn"], s0, f["p"]))
            for s in scales[:: max(1, len(scales) // 15)]:
                cand.append((q_rmse(f, predict(f, sa, s)[1]), vh, s0, s))
    e, vh, s0, s = min(cand)
    best["bb"] = (e, dict(bb_max_aperture_closure=vh, bb_initial_normal_stiffness=s0 / vh,
                          aperture_scale=s))
    sa = vh * (bb_gap(f["nref"], s0, f["p"]) - bb_gap(f["sn"], s0, f["p"]))
    ah_bb = predict(f, sa, s)[0]
    print(f"   BB       V_h = {vh*1e6:7.4f} um   K_h = {s0/vh:9.3e} Pa/m  (sigma0 = {s0/1e6:6.2f} MPa)"
          f"   aperture_scale = {s:.5f}   Q RMSE = {e:6.3f} %    max|a_h err| = {np.abs(ah_bb-f['ah_paper']).max()*1e6:.3f} um")

    out = pd.DataFrame(dict(
        stage=range(1, 12),
        sn_MPa=(f["sn"] / 1e6).round(2),
        ah_paper=(f["ah_paper"] * 1e6).round(3),
        ah_run=(f["ah"] * 1e6).round(3),
        ah_linear=(ah_lin * 1e6).round(3),
        ah_bb=(ah_bb * 1e6).round(3),
        Q_paper=f["q_paper"].round(4),
        Q_run=f["q_model"].round(4),
        Q_linear=predict(f, c * (f["nref"] - f["sn"]), best["linear"][1]["aperture_scale"])[1].round(4),
        Q_bb=predict(f, sa, s)[1].round(4),
    ))
    print(out.to_string(index=False))
    return best


if __name__ == "__main__":
    targets = sys.argv[1:] or list(RUNS)
    for t in targets:
        report(t)
