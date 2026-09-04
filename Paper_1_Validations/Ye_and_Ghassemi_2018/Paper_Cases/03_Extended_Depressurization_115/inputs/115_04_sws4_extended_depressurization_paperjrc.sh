#!/bin/bash
#SBATCH --job-name=115_04_sws4_extended_depressurization_paperjrc
#SBATCH --account=def-biaoli66
#SBATCH --time=06:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --mem=16G
#SBATCH --output=115_04_sws4_extended_depressurization_paperjrc_%j.out
#SBATCH --error=115_04_sws4_extended_depressurization_paperjrc_%j.err

# Rebased onto the measured SW-S4 JRC of 1.19. Output stems end _paperjrc, so
# nothing here overwrites the JRC 5.0 results.
cd /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Paper_1_Validations/Ye_and_Ghassemi_2018/Paper_Cases/03_Extended_Depressurization_115/inputs/

srun --mpi=pmi2 -n 32 /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/orca-opt -i 115_04_sws4_extended_depressurization_paperjrc.i
