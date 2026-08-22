#!/bin/bash
# ============================================================================
# 103-series control batch -- 3 decks, 32 ranks / 32 G / 6 h each.
#
# ONE parameter differs from each deck's 100-series BBFast parent:
# slip_weakening_exponent 1.4 -> 1.0, which is the exponent the transferred
# Mohr-Coulomb law is structurally forced into.  The 102 pairs already agree to
# ~1e-4 MPa through stage 4 and land on the same residual envelope, so the
# weakening PATH is the only remaining explanation for MC yielding a stage early.
# This isolates it.
#
# SW-S4 is deliberately absent: its exponent is already 1.10, so the change is a
# 9%% perturbation rather than a test -- and SW-S4 is correspondingly the one
# specimen where MC nearly matches BBFast.  That is the control, for free.
#
# These KEEP the paper schedule and ARE scoreable against Table 2.
# ============================================================================
set -u
cd ""/bin"

JOBS=(
  SWT1/103_01_swt1_weakexp1p0_ppfix_hpc_nochk.sh
  SWT2/103_02_swt2_weakexp1p0_ppfix_hpc_nochk.sh
  SWS3/103_03_sw3_weakexp1p0_ppfix_hpc_nochk.sh
)
echo "103 control batch: ${#JOBS[@]} decks"
for s in "${JOBS[@]}"; do
  [ -f "$s" ] || { echo "MISSING: $s" >&2; continue; }
  echo "sbatch $s"; sbatch "$s"
done
