#!/bin/bash
#SBATCH --job-name=67_11_sw4_mc_dS0p15_s28_w12_m0
#SBATCH --account=def-biaoli66
#SBATCH --time=06:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --output=67_11_sw4_mc_dS0p15_s28_w12_m0_%j.out
#SBATCH --error=67_11_sw4_mc_dS0p15_s28_w12_m0_%j.err

cd /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_3.0_claude/Examples/YeGhasemmi2018/SW4_July10/SW4_67_FINAL_FOUR

# Clear conflicting memory env vars (Alliance injects SLURM_MEM_PER_CPU; --mem sets SLURM_MEM_PER_NODE).
unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p results_csv results_exodus results_checkpoint

srun --mpi=pmi2 -n 32 /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_3.0_claude/orca-opt -i 67_11_sw4_mc_dS0p15_s28_w12_m0.i

