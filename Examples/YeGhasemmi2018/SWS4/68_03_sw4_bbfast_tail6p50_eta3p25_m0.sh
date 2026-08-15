#!/bin/bash
#SBATCH --job-name=68_03_sw4_bbfast_tail6p50_eta3p25_m0
#SBATCH --account=def-biaoli66
#SBATCH --time=06:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=64
#SBATCH --cpus-per-task=1
#SBATCH --mem=64G
#SBATCH --output=68_03_sw4_bbfast_tail6p50_eta3p25_m0_%j.out
#SBATCH --error=68_03_sw4_bbfast_tail6p50_eta3p25_m0_%j.err

set -euo pipefail

project_root=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_3.0_claude
case_dir=$project_root/Examples/YeGhasemmi2018/SW4_July10/SW4_68_TARGETED_RESIDUAL_SWEEPS
case_stem=68_03_sw4_bbfast_tail6p50_eta3p25_m0
orca_bin=$project_root/orca-opt
input_file=$case_dir/$case_stem.i
mesh_file=$project_root/Examples/YeGhasemmi2018/SW4_July10/mesh/ye2018_sw_s4_low_mesh.e

cd "$case_dir"
mkdir -p results_csv results_exodus results_checkpoint

{
  echo "utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "host=$(hostname)"
  echo "slurm_job_id=${SLURM_JOB_ID:-unavailable}"
  echo "case=$case_stem"
  echo "mpi_tasks=64"
  echo "memory=64G"
  echo "git_revision=$(git -C "$project_root" rev-parse HEAD 2>/dev/null || echo unavailable)"
  echo "binary_sha256=$(sha256sum "$orca_bin" | awk '{print $1}')"
  echo "input_sha256=$(sha256sum "$input_file" | awk '{print $1}')"
  echo "mesh_sha256=$(sha256sum "$mesh_file" | awk '{print $1}')"
  echo "git_status_begin"
  git -C "$project_root" status --short 2>/dev/null || true
  echo "git_status_end"
} > "results_csv/$case_stem.provenance.txt"

unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
exec srun --mpi=pmi2 -n 64 "$orca_bin" -i "$case_stem.i" "$@"

