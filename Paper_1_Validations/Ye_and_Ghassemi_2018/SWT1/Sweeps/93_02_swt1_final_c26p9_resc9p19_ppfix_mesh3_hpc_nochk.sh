#!/bin/bash

#SBATCH --job-name=93_02_swt1_final_c26p9_resc9p19_ppfix_mesh3_hpc
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWT1
#SBATCH --account=def-biaoli66
#SBATCH --time=2-00:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=128
#SBATCH --cpus-per-task=1
#SBATCH --mem=128G
#SBATCH --output=logs/93_02_swt1_final_c26p9_resc9p19_ppfix_mesh3_hpc_%j.out
#SBATCH --error=logs/93_02_swt1_final_c26p9_resc9p19_ppfix_mesh3_hpc_%j.err

cd /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWT1

# Clear conflicting memory env vars (Alliance injects SLURM_MEM_PER_CPU; --mem sets SLURM_MEM_PER_NODE).
unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p results_csv_hpc_rorqual results_exodus_hpc_rorqual logs

srun --mpi=pmi2 -n 128 /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/orca-opt -i 93_02_swt1_final_c26p9_resc9p19_ppfix_mesh3.i \
    Outputs/chk/enable=false \
    csv_file_base=results_csv_hpc_rorqual/93_02_swt1_final_c26p9_resc9p19_ppfix_mesh3_hpc \
    exodus_file_base=results_exodus_hpc_rorqual/93_02_swt1_final_c26p9_resc9p19_ppfix_mesh3_hpc
