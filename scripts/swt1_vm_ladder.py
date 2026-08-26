import sys
from pathlib import Path
ROOT = Path("/media/geomechanics/Data4TB/projects/orca_4.0")
sys.path.insert(0, str(ROOT / "scripts"))
import table2_gate as G
EX = ROOT / "Examples/YeGhasemmi2018"
R = "SWT1/results_csv_hpc_rorqual"
CH = ["Q_ml_min","sigma_n_MPa","tau_MPa","dn_mm","ds_mm"]
LAD = [
 (45.91, "93_01_swt1_final_c26p9_resc9p19_ppfix_hpc.csv"),
 (50.00, "99_01_swt1_vm50um_ppfix_hpc.csv"),
 (55.00, "100_01_swt1_vm55um_ppfix_hpc.csv"),
 (70.00, "105_01_swt1_vm70um_ppfix_hpc.csv"),
 (90.00, "105_02_swt1_vm90um_ppfix_hpc.csv"),
 (110.0, "105_03_swt1_vm110um_ppfix_hpc.csv"),
]
print(f"{'V_m um':>8}" + "".join(f"{c:>12}" for c in CH) + f"{'MEAN':>10}")
for vm, f in LAD:
    p = EX / R / f
    if not p.is_file():
        print(f"{vm:>8.2f}  MISSING {f}"); continue
    res = G.score_run(p, "SWT1", "biot_ab_20260815", 0.15, "stage1", 55.0)
    s = G.normalised_scores(res)
    if not s:
        print(f"{vm:>8.2f}  incomplete reached={res['reached']}/11"); continue
    print(f"{vm:>8.2f}" + "".join(f"{s[c]:>12.2f}" for c in CH) + f"{s['mean']:>10.2f}")
