#!/bin/bash
# ============================================================================
# Discussion-section batch: the 97 (cyclic) and 98 (shut-in) decks.
#
# See DISCUSSION_DECKS_97_98.md for the schedule design and, importantly, for
# what to MEASURE -- neither series is scoreable against Table 2, because both
# replace the paper's monotonic injection history by design. Do not run
# scripts/table2_gate.py on these.
#
# Each deck is its 93-series validated parent with three changes and no others:
# the [injection_pressure] function, end_time, and the output file bases.
#
# 8 jobs, 32 ranks / 32 G / 24 h. Longest estimated wall time is 8.1 h
# (97_03_sw3_cyclic3, 15793 s of simulated time at the measured 1.85 s/s rate).
# They are independent of each other and of the 94-series MC baseline, so
# submission order does not matter.
# ============================================================================
set -u
cd "$(dirname "$0")"

JOBS=(
  # --- 97: three equal-peak load/unload cycles; permeability enhancement ---
  SWT1/97_01_swt1_cyclic3_hpc_nochk.sh
  SWT2/97_02_swt2_cyclic3_hpc_nochk.sh
  SWS3/97_03_sw3_cyclic3_hpc_nochk.sh
  SWS4/97_04_sw4_cyclic3_hpc_nochk.sh
  # --- 98: ramp, hold, exponential shut-in; delayed reactivation ----------
  SWT1/98_01_swt1_shutin_hpc_nochk.sh
  SWT2/98_02_swt2_shutin_hpc_nochk.sh
  SWS3/98_03_sw3_shutin_hpc_nochk.sh
  SWS4/98_04_sw4_shutin_hpc_nochk.sh
)

echo "discussion batch: ${#JOBS[@]} decks (4 cyclic + 4 shut-in)"
for s in "${JOBS[@]}"; do
  if [ ! -f "$s" ]; then
    echo "MISSING: $s" >&2
    continue
  fi
  echo "sbatch $s"
  sbatch "$s"
done
