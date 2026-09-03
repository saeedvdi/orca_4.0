#!/bin/bash

#SBATCH --job-name=Ye2018_SWT2_BBFast_sweep_21_F0p90_Pp0p60_T40p20_U0p84_A0p0165_BBhyd_IOsafe_kernel_SV_biot0p6_mesh3
#SBATCH --account=def-biaoli66
#SBATCH --time=48:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=180G
#SBATCH --output=logs/Ye2018_SWT2_BBFast_sweep_21_F0p90_Pp0p60_T40p20_U0p84_A0p0165_BBhyd_IOsafe_kernel_SV_biot0p6_mesh3_%j.out
#SBATCH --error=logs/Ye2018_SWT2_BBFast_sweep_21_F0p90_Pp0p60_T40p20_U0p84_A0p0165_BBhyd_IOsafe_kernel_SV_biot0p6_mesh3_%j.err

cd /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWT2

# Alliance injects SLURM_MEM_PER_CPU; --mem sets SLURM_MEM_PER_NODE. Clear both.
unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p logs results_csv results_exodus results_checkpoint

srun --mpi=pmi2 -n 32 /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/orca-opt -i Ye2018_SWT2_BBFast_sweep_21_F0p90_Pp0p60_T40p20_U0p84_A0p0165_BBhyd_IOsafe_kernel_SV_biot0p6_mesh3.i
