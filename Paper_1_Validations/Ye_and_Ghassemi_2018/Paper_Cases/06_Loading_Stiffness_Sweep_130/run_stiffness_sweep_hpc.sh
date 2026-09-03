#!/bin/bash
# Loading-stiffness sweep on SW-T1 (series 130): how much of the measured stress
# drop is a property of the loading frame rather than of the fracture?
#
#   sbatch run_stiffness_sweep_hpc.sh        # all 7
#   sbatch --array=2 run_stiffness_sweep_hpc.sh   # calibrated control only
#
# Every member is the selected SW-T1 Barton-Bandis deck with ONLY the axial
# boundary stiffness changed and the commanded displacement recompensated so the
# preload state is unchanged. Index 2 is the calibrated value and must reproduce
# the paper's SW-T1 case; treat it as the control.
#
# Exodus and checkpoints are off and CSV is written every timestep, because the
# quantity of interest is the time derivative of differential stress through the
# slip burst, not the field.
#SBATCH --job-name=swt1_ksweep
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Paper_1_Validations/Ye_and_Ghassemi_2018/Paper_Cases/06_Loading_Stiffness_Sweep_130
#SBATCH --account=def-biaoli66
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --array=0-6
#SBATCH --output=logs/ksweep_%A_%a.out
#SBATCH --error=logs/ksweep_%A_%a.err

set -euo pipefail
PROJECT_ROOT=${ORCA_ROOT:-/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0}
CASE_DIR=${PROJECT_ROOT}/Paper_1_Validations/Ye_and_Ghassemi_2018/Paper_Cases/06_Loading_Stiffness_Sweep_130
cd "${CASE_DIR}"

DECKS=(130_01_swt1_kp1p000e11 130_02_swt1_kp2p000e11 130_03_swt1_kp4p123e11 130_04_swt1_kp1p000e12 130_05_swt1_kp3p000e12 130_06_swt1_kp1p000e13 130_07_swt1_kp1p000e14)
IDX=${SLURM_ARRAY_TASK_ID:-2}
if (( IDX < 0 || IDX >= ${#DECKS[@]} )); then echo "index must be 0..6" >&2; exit 2; fi
D=${DECKS[$IDX]}
[[ -f ${D}.i ]] || { echo "missing deck ${CASE_DIR}/${D}.i" >&2; exit 2; }
MESH=$(grep -m1 '^mesh_file' "${D}.i" | sed 's/#.*//; s/^[^=]*=[[:space:]]*//; s/[[:space:]]*$//')
[[ -f ${MESH} ]] || { echo "mesh not found: ${MESH}" >&2; exit 2; }

unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p results_csv logs
echo "member ${IDX}: ${D}   k_p = $(grep -m1 '^axial_bc_penalty' ${D}.i)"
srun --mpi=pmi2 -n 32 "${PROJECT_ROOT}/orca-opt" -i "${D}.i" \
  Outputs/chk/enable=false \
  Outputs/exodus/enable=false \
  Outputs/csv/time_step_interval=1 \
  "csv_file_base=results_csv/${D}"
