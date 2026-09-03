#!/bin/bash
# ---------------------------------------------------------------------------
# Run every Paper_Cases/01_Main_Validation case: BB and MC for all four
# specimens, as one 8-task Slurm array.
#
#   sbatch run_all_main_validation_hpc.sh          # all 8
#   sbatch --array=0-3 run_all_main_validation_hpc.sh   # the four BB cases
#   sbatch --array=4-7 run_all_main_validation_hpc.sh   # the four MC cases
#   sbatch --array=6   run_all_main_validation_hpc.sh   # SWS4 BB only
#
# Task map:  0 SWT1-BB  1 SWT2-BB  2 SWS3-BB  3 SWS4-BB
#            4 SWT1-MC  5 SWT2-MC  6 SWS3-MC  7 SWS4-MC
#
# Each task cd's into its own specimen directory, where the staged deck sits
# beside mesh/ so the deck's input-relative `mesh_file` resolves. Outputs land
# in <SPEC>/results_exodus_stages and <SPEC>/results_csv_stages.
#
# The BB decks already carry sync_times, so each writes 23 pressure-
# synchronised states across the full injection cycle.
#
# MC is a 9-member equal-budget sweep; this script runs each specimen's
# PAPER-SELECTED member only (SWT1/SWT2 pb04, SWS3 pb06, SWS4 center), with
# that member's parameters baked in below. To run other members, use the
# per-specimen run_<SPEC>_mc.sh, which keeps the full sweep.
#
# Repo root: set ORCA_ROOT to override without editing this file. NOTE that
# --chdir below cannot take a variable and must be edited if your checkout
# is not at the path shown.
# ---------------------------------------------------------------------------
#SBATCH --job-name=ye2018_main_validation
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Paper_1_Validations/Ye_and_Ghassemi_2018/Paper_Cases/01_Main_Validation
#SBATCH --account=def-biaoli66
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --array=0-7
#SBATCH --output=logs/main_validation_%A_%a.out
#SBATCH --error=logs/main_validation_%A_%a.err

set -euo pipefail

PROJECT_ROOT=${ORCA_ROOT:-/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0}
BASE_DIR=${PROJECT_ROOT}/Paper_1_Validations/Ye_and_Ghassemi_2018/Paper_Cases/01_Main_Validation
IDX=${SLURM_ARRAY_TASK_ID:-0}

SPEC=(SWT1 SWT2 SWS3 SWS4 SWT1 SWT2 SWS3 SWS4)
LAW=(BB BB BB BB MC MC MC MC)
DECK=(SWT1_OrcaBartonBandisContactTractionFastADHardening SWT2_OrcaBartonBandisContactTractionFastADHardening SWS3_OrcaBartonBandisContactTractionFastADHardening SWS4_OrcaBartonBandisContactTractionFastADHardening SWT1_OrcaMohrCoulombContactTraction SWT2_OrcaMohrCoulombContactTraction SWS3_OrcaMohrCoulombContactTraction SWS4_OrcaMohrCoulombContactTraction)
STEM=(SWT1_OrcaBartonBandisContactTractionFastADHardening SWT2_OrcaBartonBandisContactTractionFastADHardening SWS3_OrcaBartonBandisContactTractionFastADHardening SWS4_OrcaBartonBandisContactTractionFastADHardening SWT1_OrcaMohrCoulombContactTraction_pb04 SWT2_OrcaMohrCoulombContactTraction_pb04 SWS3_OrcaMohrCoulombContactTraction_pb06 SWS4_OrcaMohrCoulombContactTraction_center)
# MC-only parameters, indexed 4..7 (empty placeholders for the BB tasks 0..3)
MU_ROUGH=(- - - - 0.509312 0.508576 0.952344 0.9804)
C_ROUGH=(- - - - 4.07374e7 4.72549e7 2.3805e6 3.225e6)
MU_SMOOTH=(- - - - 0.640304 0.640304 0.166432 0.1139)
C_SMOOTH=(- - - - 7.8115e6 8.2535e6 1.19e6 0)
D_ROUGH=(- - - - 1.125e-4 1.125e-4 5e-5 8e-5)

if (( IDX < 0 || IDX >= ${#SPEC[@]} )); then
  echo "SLURM_ARRAY_TASK_ID must be 0..7" >&2; exit 2
fi

S=${SPEC[$IDX]}; L=${LAW[$IDX]}; D=${DECK[$IDX]}; O=${STEM[$IDX]}
CASE_DIR=${BASE_DIR}/${S}

if [[ ! -d ${CASE_DIR} ]]; then echo "missing case dir: ${CASE_DIR}" >&2; exit 2; fi
cd "${CASE_DIR}"
if [[ ! -f ${D}.i ]]; then echo "missing deck: ${CASE_DIR}/${D}.i" >&2; exit 2; fi

# strip the trailing comment FIRST, then take everything after the first '='.
# SWS3's line ends in a comment containing 'L=123.40mm', so a greedy '.*='
# would match inside the comment and yield garbage.
MESH=$(grep -m1 '^mesh_file' "${D}.i" | sed 's/#.*//; s/^[^=]*=[[:space:]]*//; s/[[:space:]]*$//')
if [[ ! -f ${MESH} ]]; then echo "mesh not found from ${CASE_DIR}: ${MESH}" >&2; exit 2; fi

unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
# One self-contained folder per case. The decks default to THREE separate
# directories (results_exodus/, results_csv/, results_checkpoint/), which
# scatters a single run's artifacts; all three bases are redirected here so
# everything for a case lands together. file_base is CWD-relative in MOOSE,
# which is why the cd above must happen first.
OUTDIR=results/${O}
mkdir -p "${OUTDIR}" logs

echo "task ${IDX}: ${S} ${L}"
echo "  deck : ${CASE_DIR}/${D}.i"
echo "  mesh : ${MESH}"
echo "  out  : ${CASE_DIR}/${OUTDIR}/"

COMMON=(Outputs/chk/enable=false
        "csv_file_base=${OUTDIR}/${O}"
        "exodus_file_base=${OUTDIR}/${O}"
        "checkpoint_file_base=${OUTDIR}/${O}_chk")

if [[ ${L} == BB ]]; then
  srun --mpi=pmi2 -n 32 "${PROJECT_ROOT}/orca-opt" -i "${D}.i" "${COMMON[@]}"
else
  srun --mpi=pmi2 -n 32 "${PROJECT_ROOT}/orca-opt" -i "${D}.i" "${COMMON[@]}" \
    "Materials/czm_contact/friction_coefficient_rough=${MU_ROUGH[$IDX]}" \
    "Materials/czm_contact/cohesion_rough=${C_ROUGH[$IDX]}" \
    "Materials/czm_contact/friction_coefficient_smooth=${MU_SMOOTH[$IDX]}" \
    "Materials/czm_contact/cohesion_smooth=${C_SMOOTH[$IDX]}" \
    "Materials/czm_contact/roughness_decay_distance=${D_ROUGH[$IDX]}"
fi
