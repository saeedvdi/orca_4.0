#!/bin/bash

#SBATCH --job-name=84_01_sw3_bbfast_postevent_retreat4p5um_m0_kernel_SV_biot0p6_mesh3
#SBATCH --account=def-biaoli66
#SBATCH --time=48:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=180G
#SBATCH --output=logs/84_01_sw3_bbfast_postevent_retreat4p5um_m0_kernel_SV_biot0p6_mesh3_%j.out
#SBATCH --error=logs/84_01_sw3_bbfast_postevent_retreat4p5um_m0_kernel_SV_biot0p6_mesh3_%j.err

cd /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWS3

# Alliance injects SLURM_MEM_PER_CPU; --mem sets SLURM_MEM_PER_NODE. Clear both.
unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p logs results_csv results_exodus results_checkpoint

srun --mpi=pmi2 -n 32 /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/orca-opt -i 84_01_sw3_bbfast_postevent_retreat4p5um_m0_kernel_SV_biot0p6_mesh3.i
