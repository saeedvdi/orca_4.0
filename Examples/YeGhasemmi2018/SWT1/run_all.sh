#!/bin/bash
#
# Submit every SWT1 kernel_SV deck as its own SLURM job.
# Generated 2026-08-15. Run from this directory: ./run_all.sh
#
# Each deck gets one 32-rank node for 12 h. Pass --dry to list without submitting.

set -u
cd "$(dirname "$0")"
mkdir -p logs results_csv results_exodus results_checkpoint

DRY=0; [ "${1:-}" = "--dry" ] && DRY=1

DECKS=(
  "Ye2018_SWT1_BBFast_sweep_19_F0p95_Pp0p60_T40p00_U0p94_A0p0160_Kinematic_IOsafe_kernel_SV"
  "Ye2018_SWT1_BBFast_sweep_20_F0p95_Pp0p60_T40p00_U0p94_A0p0115_Cn1p80em14_LinearHyd_Kinematic_IOsafe_kernel_SV"
  "Ye2018_SWT1_BBFast_sweep_19_F0p95_Pp0p60_T40p00_U0p94_A0p0160_Kinematic_IOsafe_kernel_SV_biot0p6"
)

for deck in "${DECKS[@]}"; do
  if [ ! -f "$deck.i" ]; then echo "MISSING $deck.i -- skipped"; continue; fi
  if [ "$DRY" = 1 ]; then echo "would submit $deck.sh"; continue; fi
  jid=$(sbatch --parsable "$deck.sh") || { echo "FAILED to submit $deck"; continue; }
  echo "submitted $deck  jobid=$jid"
done
