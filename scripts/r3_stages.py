#!/usr/bin/env python3
"""Per-stage table for a Kalantar run, plus the diagnostic channels the gate
does not score (tau/tau_limit, mobilised JRC, the constitutive sigma'_n)."""
import sys, math
from pathlib import Path
import numpy as np, pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parent))
import kalantar_gate as kg
from table2_gate import parse_schedule, first_column

EXTRA = ["bb_jrc_mobilized_pp", "bb_effective_normal_stress_pp",
         "bb_limit_tau_pp", "czm_tau_2_pp",
         "bb_dilation_angle_pp", "cohesion_effective_pp",
         "injection_pressure_pp"]


def table(csv_path, sample, deck):
    x, y = parse_schedule(Path(deck))
    ref = kg.reference(sample)
    times = kg.kal_stage_times(x, y, ref, 0.15)
    raw = (pd.read_csv(csv_path).sort_values("time")
           .drop_duplicates("time", keep="last").reset_index(drop=True))
    model = pd.DataFrame({"time": pd.to_numeric(raw["time"], errors="coerce")})
    for key, cands in kg.KAL_COLUMNS.items():
        s, _ = first_column(raw, cands)
        model[key] = np.nan if s is None else s
    for c in EXTRA:
        model[c] = raw[c] if c in raw.columns else np.nan

    rows = [model[model["time"] <= t + 1e-9].iloc[-1] for t in times]
    got = pd.DataFrame(rows).reset_index(drop=True)
    cos_t = math.cos(math.radians(kg.THETA_DECK[sample]))

    print(f"\n=== {sample}  {Path(csv_path).name}   ({len(times)} stages, "
          f"t_end={model['time'].iloc[-1]:.0f}) ===")
    hdr = ("st  Pi   br   | tau_m  tau_M   err%  | sn_m   sn_M   err% | "
           "ah_m  ah_M  err% | ds_m   ds_M   | t/tlim  JRC")
    print(hdr)
    for i in range(len(got)):
        r, g = ref.iloc[i], got.iloc[i]
        tl = g.get("bb_limit_tau_pp", np.nan)
        tau_c = abs(g.get("czm_tau_2_pp", np.nan)) / 1e6
        ratio = tau_c / (tl / 1e6) if np.isfinite(tl) and tl else np.nan
        if np.isfinite(tl) and tl < 1e3:      # already MPa
            ratio = tau_c * 1e6 / tl if tl else np.nan
        def e(m, o):
            return 100.0 * (m - o) / o if o else np.nan
        print(f"{i+1:2d} {r.Pi_MPa:4.0f} {r.branch[:4]:4s} | "
              f"{r.tau_MPa:6.2f} {g.tau_MPa:6.2f} {e(g.tau_MPa, r.tau_MPa):6.1f} | "
              f"{r.sigma_n_MPa:6.2f} {g.sigma_n_MPa:6.2f} "
              f"{e(g.sigma_n_MPa, r.sigma_n_MPa):5.1f} | "
              f"{r.ah_um:5.2f} {g.ah_um:5.2f} {e(g.ah_um, r.ah_um):5.1f} | "
              f"{r.ds_mm/cos_t:6.4f} {g.ds_mm:6.4f} | "
              f"{ratio:6.4f} {g.get('bb_jrc_mobilized_pp', np.nan):6.3f}")


if __name__ == "__main__":
    table(sys.argv[1], sys.argv[2], sys.argv[3])
