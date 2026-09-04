#!/bin/bash
#SBATCH --job-name=109_06_sw4_nodilation_floor074_paperjrc
#SBATCH --account=def-biaoli66
#SBATCH --time=06:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --mem=16G
#SBATCH --output=109_06_sw4_nodilation_floor074_paperjrc_%j.out
#SBATCH --error=109_06_sw4_nodilation_floor074_paperjrc_%j.err

# Rebuilt at the measured SW-S4 JRC of 1.19, replacing a legacy ablation whose
# deck was never kept. Output stems end _paperjrc, so nothing is overwritten.
cd /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWS4/proposed_inputs

srun --mpi=pmi2 -n 32 /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/orca-opt -i 109_06_sw4_nodilation_floor074_paperjrc.i
