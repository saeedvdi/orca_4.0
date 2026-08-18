#!/bin/bash

#SBATCH --job-name=96_05_sw3_biot0p2_fpc1p0_hpc
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWS3
#SBATCH --account=def-biaoli66
#SBATCH --time=12:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=16
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --output=logs/96_05_sw3_biot0p2_fpc1p0_hpc_%j.out
#SBATCH --error=logs/96_05_sw3_biot0p2_fpc1p0_hpc_%j.err

cd /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWS3

# Clear conflicting memory env vars (Alliance injects SLURM_MEM_PER_CPU; --mem sets SLURM_MEM_PER_NODE).
unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p results_csv_hpc_rorqual results_exodus_hpc_rorqual logs

srun --mpi=pmi2 -n 16 /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/orca-opt -i 96_05_sw3_biot0p2_fpc1p0.i \
    Outputs/chk/enable=false \
    csv_file_base=results_csv_hpc_rorqual/96_05_sw3_biot0p2_fpc1p0_hpc \
    exodus_file_base=results_exodus_hpc_rorqual/96_05_sw3_biot0p2_fpc1p0_hpc
