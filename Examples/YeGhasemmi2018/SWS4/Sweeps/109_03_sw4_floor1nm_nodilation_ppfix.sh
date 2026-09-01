#!/bin/bash

#SBATCH --job-name=109_03_sw4_floor1nm_nodilation_ppfix
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWS4
#SBATCH --account=def-biaoli66
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --output=paper_revision_20260901_followup/logs/109_03_sw4_floor1nm_nodilation_ppfix_%j.out
#SBATCH --error=paper_revision_20260901_followup/logs/109_03_sw4_floor1nm_nodilation_ppfix_%j.err

set -euo pipefail

PROJECT_ROOT=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0
CASE_STEM=109_03_sw4_floor1nm_nodilation_ppfix
CASE_DIR=${PROJECT_ROOT}/Examples/YeGhasemmi2018/SWS4

# Run from the specimen directory, not from Sweeps/.  The deck's mesh path
# (../mesh/...) is resolved relative to the INPUT FILE, so it reaches SWS4/mesh
# from Sweeps/; the Outputs file_base paths are resolved relative to the
# WORKING DIRECTORY, so they must be read from SWS4/.
cd "${CASE_DIR}"

# Alliance injects SLURM_MEM_PER_CPU; --mem sets SLURM_MEM_PER_NODE. Clear both.
unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU

# MOOSE creates these itself, but SLURM does not create the log directory.
mkdir -p paper_revision_20260901_followup/{csv,exodus,checkpoint,logs}

# Do NOT override csv_file_base/exodus_file_base here.  These are diagnostic
# counterfactuals, not Table 2 validation cases; the deck deliberately writes
# them to paper_revision_20260901_followup/ so they stay out of
# results_csv_hpc_rorqual/ and out of the Table 2 ranking glob.
srun --mpi=pmi2 -n 32 "${PROJECT_ROOT}/orca-opt" -i "Sweeps/${CASE_STEM}.i" \
    Outputs/chk/enable=false
