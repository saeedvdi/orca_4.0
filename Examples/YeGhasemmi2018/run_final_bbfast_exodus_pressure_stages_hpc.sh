#!/bin/bash

# Re-run the four final BBFast cases with compact, pressure-synchronized Exodus output.
# Submit all four:  sbatch run_final_bbfast_exodus_pressure_stages_hpc.sh
# Submit one only:  sbatch --array=0 run_final_bbfast_exodus_pressure_stages_hpc.sh
# Array order: 0=SWT1, 1=SWT2, 2=SWS3, 3=SWS4.

#SBATCH --job-name=bbfast_exostages
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018
#SBATCH --account=def-biaoli66
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --array=0-3
#SBATCH --output=bbfast_exostages_%A_%a.out
#SBATCH --error=bbfast_exostages_%A_%a.err

set -euo pipefail

PROJECT_ROOT=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0
ORCA_EXECUTABLE=${PROJECT_ROOT}/orca-opt

SAMPLES=(SWT1 SWT2 SWS3 SWS4)
INPUTS=(
  SWT1_OrcaBartonBandisContactTractionFastADHardening.i
  SWT2_OrcaBartonBandisContactTractionFastADHardening.i
  SWS3_OrcaBartonBandisContactTractionFastADHardening.i
  SWS4_OrcaBartonBandisContactTractionFastADHardening.i
)
OUTPUT_STEMS=(
  SWT1_OrcaBartonBandisContactTractionFastADHardening
  SWT2_OrcaBartonBandisContactTractionFastADHardening
  SWS3_OrcaBartonBandisContactTractionFastADHardening
  SWS4_OrcaBartonBandisContactTractionFastADHardening
)

# t=0, loading at 6,8,...,28 MPa, then unloading at 26,24,...,8 MPa.
# The 8/12/16/20/24/28 MPa stage times are the ends of their holds.  The
# intervening 2 MPa points are exact PiecewiseLinear crossing times.  SWS3's
# final schedule knot is 4802.4 s but its validated end_time is 4802.0 s, so
# its last synchronized output remains at 4802.0 s to preserve the final deck.
SYNC_TIMES=(
  "0 68.3333333 370 402.5 675 707.5 980 1012.5 1260 1300 1565 1602.5 1900 1930 2165 2192.5 2455 2485 2755 2787.5 3055 3090 3500"
  "0 83.3333333 480 522.5 995 1032.5 1360 1410 1755 1802.5 2145 2212.5 2500 2505 2560 2565 2605 2610 2650 2655 2705 2715 2852.5"
  "0 82.3694668 500.8 613.311156 972.7 1115.80626 1528.8 1625.18577 1914.6 2028.09387 2300.4 2421.23438 2699 2799.41838 3115.1 3255.49821 3544.1 3671.80176 3963.8 4053.19846 4360.1 4442.06901 4802"
  "0 88.0695771 319.78644 419.383237 639.222106 713.035275 947.447989 1018.41614 1255.68177 1330.62241 1535.88024 1632.36945 1788.0289 1900.88513 2113.63729 2212.32235 2439.25753 2516.5855 2742.42001 2829.46122 3028.75301 3131.76413 3404.83669"
)

TASK_INDEX=${SLURM_ARRAY_TASK_ID:-0}
if (( TASK_INDEX < 0 || TASK_INDEX >= ${#SAMPLES[@]} )); then
  echo "SLURM_ARRAY_TASK_ID must be 0, 1, 2, or 3" >&2
  exit 2
fi

SAMPLE=${SAMPLES[$TASK_INDEX]}
INPUT=${INPUTS[$TASK_INDEX]}
OUTPUT_STEM=${OUTPUT_STEMS[$TASK_INDEX]}
CASE_DIR=${PROJECT_ROOT}/Examples/YeGhasemmi2018/${SAMPLE}

cd "${CASE_DIR}"
unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p results_exodus_pressure_stages results_csv_pressure_stages

echo "Sample: ${SAMPLE}"
echo "Input: ${CASE_DIR}/${INPUT}"
echo "Exodus: results_exodus_pressure_stages/${OUTPUT_STEM}.e"
echo "Synchronized times: ${SYNC_TIMES[$TASK_INDEX]}"

srun --mpi=pmi2 -n 32 "${ORCA_EXECUTABLE}" -i "${INPUT}" \
  Outputs/chk/enable=false \
  "Outputs/exodus/execute_on=INITIAL TIMESTEP_END" \
  Outputs/exodus/sync_only=true \
  "Outputs/exodus/sync_times=${SYNC_TIMES[$TASK_INDEX]}" \
  "exodus_file_base=results_exodus_pressure_stages/${OUTPUT_STEM}" \
  "Outputs/csv/execute_on=INITIAL TIMESTEP_END" \
  Outputs/csv/sync_only=true \
  "Outputs/csv/sync_times=${SYNC_TIMES[$TASK_INDEX]}" \
  "csv_file_base=results_csv_pressure_stages/${OUTPUT_STEM}"
