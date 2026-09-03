#!/bin/bash

#SBATCH --job-name=sws4_117_01_wave1
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWS4
#SBATCH --account=def-biaoli66
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --output=logs/117_01_sws4_jrc1p19_m1p60_dc74p5_protocol_ppfix_%j.out
#SBATCH --error=logs/117_01_sws4_jrc1p19_m1p60_dc74p5_protocol_ppfix_%j.err

set -euo pipefail

PROJECT_ROOT=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0
CASE_STEM=117_01_sws4_jrc1p19_m1p60_dc74p5_protocol_ppfix
CASE_DIR=${PROJECT_ROOT}/Examples/YeGhasemmi2018/SWS4
SOURCE_INPUT=${PROJECT_ROOT}/Examples/YeGhasemmi2018/protocol_consistency_20260902/SWS4/recalibration_wave1_20260902/${CASE_STEM}.i

cd "${CASE_DIR}"
unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p proposed_inputs results_csv_hpc results_exodus_hpc logs
cp "${SOURCE_INPUT}" "proposed_inputs/${CASE_STEM}.i"

srun --mpi=pmi2 -n 32 "${PROJECT_ROOT}/orca-opt" -i "proposed_inputs/${CASE_STEM}.i" \
  Outputs/chk/enable=false \
  "csv_file_base=results_csv_hpc/${CASE_STEM}" \
  "exodus_file_base=results_exodus_hpc/${CASE_STEM}"
