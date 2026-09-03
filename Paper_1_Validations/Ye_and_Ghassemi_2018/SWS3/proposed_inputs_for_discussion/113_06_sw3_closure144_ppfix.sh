#!/bin/bash

#SBATCH --job-name=113_06_sw3_closure144_ppfix
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWS3
#SBATCH --account=def-biaoli66
#SBATCH --time=12:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --mem=24G
#SBATCH --output=proposed_inputs/paper_compelling_20260902/logs/113_06_sw3_closure144_ppfix_%j.out
#SBATCH --error=proposed_inputs/paper_compelling_20260902/logs/113_06_sw3_closure144_ppfix_%j.err

set -euo pipefail

PROJECT_ROOT=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0
CASE_STEM=113_06_sw3_closure144_ppfix
CASE_DIR=${PROJECT_ROOT}/Examples/YeGhasemmi2018/SWS3

cd "${CASE_DIR}"
unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p proposed_inputs/paper_compelling_20260902/{csv,exodus,checkpoint,logs}

srun --mpi=pmi2 -n 8 "${PROJECT_ROOT}/orca-opt" -i "proposed_inputs/${CASE_STEM}.i"   Outputs/chk/enable=false
