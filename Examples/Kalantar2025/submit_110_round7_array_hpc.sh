#!/bin/bash

# Submit all three Kalantar round-7 diagnostics with:
#
#   sbatch submit_110_round7_array_hpc.sh
#
# All three tasks are eligible to start together; SLURM controls actual start times.
# Array map:
#   0  OG-T   110_16  28-degree traction-boundary preload probe
#   1  OG-SH  110_17  stress-dependent tangential-stiffness probe through stage 5
#   2  OG-SC  110_18  stress-dependent tangential-stiffness probe through stage 7

#SBATCH --job-name=kalantar_110_r7
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/Kalantar2025
#SBATCH --account=def-biaoli66
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --array=0-2
#SBATCH --output=kalantar_110_r7_%A_%a.out
#SBATCH --error=kalantar_110_r7_%A_%a.err

set -euo pipefail

project_root=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0
study_root=${project_root}/Examples/Kalantar2025

case "${SLURM_ARRAY_TASK_ID}" in
  0)
    case_dir=OGT
    stem=110_16_og_t_traction_probe_r7
    ;;
  1)
    case_dir=OGSH
    stem=110_17_og_sh_ktshape_r7
    ;;
  2)
    case_dir=OGSC
    stem=110_18_og_sc_ktshape_r7
    ;;
  *)
    echo "Unexpected SLURM_ARRAY_TASK_ID=${SLURM_ARRAY_TASK_ID}" >&2
    exit 2
    ;;
esac

cd "${study_root}/${case_dir}"

if [[ ! -f "${stem}.i" ]]; then
  echo "Missing input deck: ${study_root}/${case_dir}/${stem}.i" >&2
  exit 3
fi

unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p results_csv_hpc results_exodus_hpc logs

echo "Starting task ${SLURM_ARRAY_TASK_ID}: ${case_dir}/${stem}.i"
echo "32 MPI ranks, 32G RAM, 24 h; executable must be built from orca_v9"

srun --mpi=pmi2 -n 32 "${project_root}/orca-opt" -i "${stem}.i" \
  Outputs/chk/enable=false \
  csv_file_base="results_csv_hpc/${stem}_hpc" \
  exodus_file_base="results_exodus_hpc/${stem}_hpc"
