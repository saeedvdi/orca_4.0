#!/bin/bash
#
# Submit every SWS3 kernel_SV deck as its own SLURM job.
# Generated 2026-08-15. Run from this directory: ./run_all.sh
#
# Each deck gets one 32-rank node for 12 h. Pass --dry to list without submitting.

set -u
cd "$(dirname "$0")"
mkdir -p logs results_csv results_exodus results_checkpoint

DRY=0; [ "${1:-}" = "--dry" ] && DRY=1

DECKS=(
  "83_11_sw3_mc_opening_gate5d30_m0_kernel_SV"
  "84_01_sw3_bbfast_postevent_retreat4p5um_m0_kernel_SV"
  "84_02_sw3_bbfast_postevent_retreat6p0um_m0_kernel_SV"
  "84_01_sw3_bbfast_postevent_retreat4p5um_m0_kernel_SV_biot0p6"
)

for deck in "${DECKS[@]}"; do
  if [ ! -f "$deck.i" ]; then echo "MISSING $deck.i -- skipped"; continue; fi
  if [ "$DRY" = 1 ]; then echo "would submit $deck.sh"; continue; fi
  jid=$(sbatch --parsable "$deck.sh") || { echo "FAILED to submit $deck"; continue; }
  echo "submitted $deck  jobid=$jid"
done
