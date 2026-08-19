#!/bin/bash
# ==========================================================================
# 101-series discussion batch -- 16 decks, 32 ranks / 32 G each.
#
# See doc/DISCUSSION_DECKS_101.md for the design and, importantly, for what
# to MEASURE.  None of these is scoreable against Table 2: every one of them
# replaces the paper's monotonic injection history by design.  Do not run
# scripts/table2_gate.py on them.
#
# Tier order is the order to run them in if the allocation is tight.  Tier 1
# is the batch that must exist -- it is the 97 experiment, which died on a
# 12 h / 16-rank allocation that its own documentation said was 24 h / 32.
# ==========================================================================
set -u
cd "$(dirname "$0")"

JOBS=(
  # --- TIER 1 -- equal-peak cyclic.  The 97 experiment, resourced to finish.
  SWT1/101_01_swt1_cyclic3_eq_hpc_nochk.sh
  SWT2/101_02_swt2_cyclic3_eq_hpc_nochk.sh
  SWS3/101_03_sw3_cyclic3_eq_hpc_nochk.sh
  SWS4/101_04_sw4_cyclic3_eq_hpc_nochk.sh
  # --- TIER 2 -- shut-in with no hold.  Cheap; isolates the pre-shut-in hold.
  SWT1/101_09_swt1_shutin_nohold_hpc_nochk.sh
  SWT2/101_10_swt2_shutin_nohold_hpc_nochk.sh
  SWS3/101_11_sw3_shutin_nohold_hpc_nochk.sh
  SWS4/101_12_sw4_shutin_nohold_hpc_nochk.sh
  # --- TIER 3 -- escalating-peak cyclic.  Outcome 2/3, which tier 1 cannot see.
  SWT1/101_05_swt1_cyclic3_esc_hpc_nochk.sh
  SWT2/101_06_swt2_cyclic3_esc_hpc_nochk.sh
  SWS3/101_07_sw3_cyclic3_esc_hpc_nochk.sh
  SWS4/101_08_sw4_cyclic3_esc_hpc_nochk.sh
  # --- TIER 4 -- slow shut-in.  Does arrest survive a realistic bleed-off?
  SWT1/101_13_swt1_shutin_slowtau_hpc_nochk.sh
  SWS4/101_14_sw4_shutin_slowtau_hpc_nochk.sh
  # --- TIER 4 -- SW-T1 frame bracket.  Tests the saturating mechanism itself.
  SWT1/101_15_swt1_cyclic2_frame2x_hpc_nochk.sh
  SWT1/101_16_swt1_cyclic2_frame0p5x_hpc_nochk.sh
)

echo "101 batch: ${#JOBS[@]} decks"
for s in "${JOBS[@]}"; do
  if [ ! -f "$s" ]; then echo "MISSING: $s" >&2; continue; fi
  echo "sbatch $s"
  sbatch "$s"
done
