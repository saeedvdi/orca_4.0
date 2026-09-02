#!/bin/bash

#SBATCH --job-name=112_02_swt1_eta200gpa_s_ppfix
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWT1
#SBATCH --account=def-biaoli66
#SBATCH --time=12:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --mem=24G
#SBATCH --output=proposed_inputs/paper_compelling_20260902/logs/112_02_swt1_eta200gpa_s_ppfix_%j.out
#SBATCH --error=proposed_inputs/paper_compelling_20260902/logs/112_02_swt1_eta200gpa_s_ppfix_%j.err

set -euo pipefail

PROJECT_ROOT=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0
CASE_STEM=112_02_swt1_eta200gpa_s_ppfix
CASE_DIR=${PROJECT_ROOT}/Examples/YeGhasemmi2018/SWT1

cd "${CASE_DIR}"
unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p proposed_inputs/paper_compelling_20260902/{csv,exodus,checkpoint,logs}

srun --mpi=pmi2 -n 8 "${PROJECT_ROOT}/orca-opt" -i "proposed_inputs/${CASE_STEM}.i"   Outputs/chk/enable=false
