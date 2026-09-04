#!/bin/bash
#SBATCH --job-name=109_05_sw4_g056_floor1nm_paperjrc
#SBATCH --account=def-biaoli66
#SBATCH --time=06:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --mem=16G
#SBATCH --output=109_05_sw4_g056_floor1nm_paperjrc_%j.out
#SBATCH --error=109_05_sw4_g056_floor1nm_paperjrc_%j.err

# Rebuilt at the measured SW-S4 JRC of 1.19, replacing a legacy ablation whose
# deck was never kept. Output stems end _paperjrc, so nothing is overwritten.
cd /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Paper_1_Validations/Ye_and_Ghassemi_2018/Paper_Cases/02_Mechanism_Tests/SWS4_109/inputs/

srun --mpi=pmi2 -n 32 /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/orca-opt -i 109_05_sw4_g056_floor1nm_paperjrc.i
