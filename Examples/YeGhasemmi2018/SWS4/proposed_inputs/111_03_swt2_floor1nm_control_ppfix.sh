#!/bin/bash
#SBATCH --job-name=111_03_swt2_floor1nm_control_ppfix       
#SBATCH --account=def-biaoli66   
#SBATCH --time=06:00:00             # Time limit (hh:mm:ss)
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --mem=16G                   
#SBATCH --output=111_03_swt2_floor1nm_control_ppfix_%j.out    
#SBATCH --error=111_03_swt2_floor1nm_control_ppfix_%j.err     

# Navigate to the simulation directory
cd /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/SWS4/proposed_inputs

# Run your MOOSE application (replace `your_moose_exec` with the actual executable)
srun --mpi=pmi2 -n 32 /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/orca-opt -i 111_03_swt2_floor1nm_control_ppfix.i