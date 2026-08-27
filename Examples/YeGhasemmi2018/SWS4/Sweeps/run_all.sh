#!/bin/bash
#
# Submit every SWS4 kernel_SV deck as its own SLURM job.
# Generated 2026-08-15. Run from this directory: ./run_all.sh
#
# Each deck gets one 32-rank node for 12 h. Pass --dry to list without submitting.

set -u
cd "$(dirname "$0")"
mkdir -p logs results_csv results_exodus results_checkpoint

DRY=0; [ "${1:-}" = "--dry" ] && DRY=1

DECKS=(
  "67_11_sw4_mc_dS0p15_s28_w12_m0_kernel_SV"
  "68_01_sw4_bbfast_tail6p50_eta3p50_m0_kernel_SV"
  "68_02_sw4_bbfast_tail6p75_eta3p25_m0_kernel_SV"
  "68_02_sw4_bbfast_tail6p75_eta3p25_m0_bakhtar_kernel_SV"
  "68_02_sw4_bbfast_tail6p75_eta3p25_m0_bakhtar_cyclic_kernel_SV"
  "68_02_sw4_bbfast_tail6p75_eta3p25_m0_cyclic_kernel_SV"
  "68_02_sw4_bbfast_tail6p75_eta3p25_m0_shutin_kernel_SV"
  "68_03_sw4_bbfast_tail6p50_eta3p25_m0_kernel_SV"
)

for deck in "${DECKS[@]}"; do
  if [ ! -f "$deck.i" ]; then echo "MISSING $deck.i -- skipped"; continue; fi
  if [ "$DRY" = 1 ]; then echo "would submit $deck.sh"; continue; fi
  jid=$(sbatch --parsable "$deck.sh") || { echo "FAILED to submit $deck"; continue; }
  echo "submitted $deck  jobid=$jid"
done
