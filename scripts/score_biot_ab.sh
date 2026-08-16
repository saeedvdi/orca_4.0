#!/bin/bash
# Score the three Biot alpha A/B pairs against Ye & Ghassemi Table 2.
#
# Each pair is one deck run twice, identical except biot_coefficient
# (1e-12 baseline vs 0.6). Pairs that have not finished are still scored --
# table2_gate.py reports the stages reached and leaves the rest blank -- so this
# is safe to run mid-campaign to watch the comparison develop.
#
#   ./score_biot_ab.sh [tag]        # default tag biot_ab_20260815
set -uo pipefail

TAG="${1:-biot_ab_20260815}"
ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
EX="$ROOT/Examples/YeGhasemmi2018"
GATE="$ROOT/scripts/table2_gate.py"
# The moose env has no pandas; the base env does.
PY=/home/geomechanics/miniforge/bin/python

declare -A PAIR=(
  [SWS3]=84_01_sw3_bbfast_postevent_retreat4p5um_m0_kernel_SV
  [SWT1]=Ye2018_SWT1_BBFast_sweep_19_F0p95_Pp0p60_T40p00_U0p94_A0p0160_Kinematic_IOsafe_kernel_SV
  [SWT2]=Ye2018_SWT2_BBFast_sweep_21_F0p90_Pp0p60_T40p20_U0p84_A0p0165_BBhyd_IOsafe_kernel_SV
)

for s in SWS3 SWT1 SWT2; do
  base="${PAIR[$s]}"
  a="$EX/$s/results_csv/${base}_${TAG}.csv"
  b="$EX/$s/results_csv/${base}_biot0p6_${TAG}.csv"
  if [ ! -f "$a" ] || [ ! -f "$b" ]; then
    echo "### $s: skipped (missing $( [ -f "$a" ] || echo baseline ) $( [ -f "$b" ] || echo alpha0.6 ) CSV)"
    continue
  fi
  "$PY" "$GATE" --tag "$TAG" --sample "$s" \
      --label 'alpha=1e-12' --label 'alpha=0.6' \
      --csv-out "$EX/$s/results_csv/${base}_${TAG}_table2.csv" \
      "$a" "$b"
done
