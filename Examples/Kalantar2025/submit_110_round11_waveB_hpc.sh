#!/bin/bash

# Kalantar ROUND 11, WAVE B -- gated on Wave A.
#
#   cd /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/Kalantar2025
#   sbatch submit_110_round11_waveB_hpc.sh
#
# DO NOT SUBMIT THIS UNTIL 110_30 HAS PASSED ITS GATE IN WAVE A:
#   d(bb_effective_normal_stress)/d(sigma_d) at +0.20 +- 0.04 pre-slip, and
#   bb_effective_normal_stress_pp / effective_normal_paper_frame_mpa_pp >= 0.93,
#   with tau/tau_limit below 1.0 for the whole preload ramp.
#
# Array map:
#   0  OG-T   110_35  full 17-stage cycle, bonded platens -- the first OG-T
#                     validation run whose specimen did not yield in its preload
#   1  OG-SH  110_33  r6 with bonded platens -- over-constraint control, 9/9 must hold
#   2  OG-SC  110_34  r6 with bonded platens -- over-constraint control, 13/13 must hold
#
# The two controls are not optional.  A pass on 110_35 cannot be claimed without
# showing the same restraint leaves the two specimens that already score
# 0.93-1.00 on the normal-stress ratio undamaged on Table 2.

#SBATCH --job-name=kalantar_110_r11b
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/Kalantar2025
#SBATCH --account=def-biaoli66
#SBATCH --time=3-00:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=64
#SBATCH --cpus-per-task=1
#SBATCH --mem=64G
#SBATCH --array=0-2
#SBATCH --output=kalantar_110_r11b_%A_%a.out
#SBATCH --error=kalantar_110_r11b_%A_%a.err

set -euo pipefail

project_root=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0
study_root=${project_root}/Examples/Kalantar2025

case "${SLURM_ARRAY_TASK_ID}" in
  0) case_dir=OGT;  stem=110_35_og_t_platen_bonded_full_r11 ;;
  1) case_dir=OGSH; stem=110_33_og_sh_platen_bonded_r11 ;;
  2) case_dir=OGSC; stem=110_34_og_sc_platen_bonded_r11 ;;
  *) echo "Unexpected SLURM_ARRAY_TASK_ID=${SLURM_ARRAY_TASK_ID}" >&2; exit 2 ;;
esac

ranks=64
case_path=${study_root}/${case_dir}
input_path=${case_path}/${stem}.i
executable=${project_root}/orca-opt

if [[ ! -f "${input_path}" ]]; then
  echo "Missing input deck: ${input_path}" >&2
  exit 3
fi

if [[ ! -x "${executable}" ]]; then
  echo "Missing or non-executable application: ${executable}" >&2
  exit 4
fi

cd "${case_path}"

unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p results_csv_hpc results_exodus_hpc results_checkpoint_hpc logs

echo "Starting array task ${SLURM_ARRAY_TASK_ID}: ${case_dir}/${stem}.i"
echo "SLURM job ${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}; ${ranks} ranks, 64G, 72 h"

srun --mpi=pmi2 -n "${ranks}" "${executable}" -i "${stem}.i" \
  Outputs/chk/enable=false \
  csv_file_base="results_csv_hpc/${stem}_hpc" \
  exodus_file_base="results_exodus_hpc/${stem}_hpc"
