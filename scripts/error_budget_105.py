import sys, numpy as np
from pathlib import Path
ROOT=Path("/media/geomechanics/Data4TB/projects/orca_4.0"); sys.path.insert(0,str(ROOT/"scripts"))
import table2_gate as G
EX=ROOT/"Examples/YeGhasemmi2018"; R="results_csv_hpc_rorqual"
BEST=[("SW-T1","SWT1",f"SWT1/{R}/100_01_swt1_vm55um_ppfix_hpc.csv","100_01 Vm=55um"),
      ("SW-T2","SWT2",f"SWT2/{R}/100_04_swt2_apscale0p0177_ppfix_hpc.csv","100_04 apscale"),
      ("SW-S3","SWS3",f"SWS3/{R}/100_06_sw3_resc1p30_unld0p00_ppfix_hpc.csv","100_06 resc1.30"),
      ("SW-S4","SWS4",f"SWS4/{R}/93_07_sw4_final_theta30_jrc5_ppfix_hpc.csv","93_07 final")]
CH=["Q_ml_min","sigma_n_MPa","tau_MPa","dn_mm","ds_mm"]
rows=[]
print(f"{'specimen':<8}{'best run':<18}" + "".join(f"{c:>12}" for c in CH) + f"{'MEAN':>9}{'sig_d share':>13}")
tot={}
for lab,s,rel,name in BEST:
    p=EX/rel
    if not p.is_file(): print(f"{lab}: MISSING {rel}"); continue
    r=G.score_run(p,s,"biot_ab_20260815",0.15,"stage1",55.0); sc=G.normalised_scores(r)
    share=(sc["sigma_n_MPa"]+sc["tau_MPa"])/(5*sc["mean"])
    print(f"{lab:<8}{name:<18}"+"".join(f"{sc[c]:>12.2f}" for c in CH)+f"{sc['mean']:>9.2f}{share*100:>12.0f}%")
    tot[lab]=sc
print()
print("campaign mean over the four best available runs: %.3f" % np.mean([v["mean"] for v in tot.values()]))
print()
# Q split: pre-event (stages 1-5) vs event+unloading (6-11)
print("Q error budget, share of the Q channel's squared error")
print(f"{'specimen':<8}{'pre-event st1-5':>18}{'event st6':>12}{'unload st7-11':>16}")
for lab,s,rel,name in BEST:
    p=EX/rel
    if not p.is_file(): continue
    r=G.score_run(p,s,"biot_ab_20260815",0.15,"stage1",55.0); t=r["table"]
    e=t["Q_ml_min_err"].values**2; tt=e.sum()
    print(f"{lab:<8}{100*e[:5].sum()/tt:>17.0f}%{100*e[5]/tt:>11.0f}%{100*e[6:].sum()/tt:>15.0f}%")
