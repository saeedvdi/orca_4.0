#!/bin/bash
# ---------------------------------------------------------------------------
# Rerun of the three main-validation cases that failed with a missing mesh:
# original array tasks 2, 6 and 7 of run_all_main_validation_hpc.sh.
#
#   new idx 0  <- task 2   SWS3 BB
#   new idx 1  <- task 6   SWS3 MC (pb06)
#   new idx 2  <- task 7   SWS4 MC (center)
#
#   sbatch run_rerun_failed_meshcases.sh          # all three
#   sbatch --array=0 run_rerun_failed_meshcases.sh   # SWS3 BB only
#
# Dispatch, output layout and MC parameters are identical to the main
# launcher, so these results are interchangeable with tasks 0-7. Each case
# writes one self-contained folder, results/<case>/.
#
# Decks and meshes now live under 00_visualizaiton/inputs.
# The mesh preflight below prints the working directory and the contents of
# mesh/ when it fails, so a second miss is diagnosable from the log alone.
# Equivalent one-liner if you prefer the original launcher:
#   sbatch --array=2,6,7 run_all_main_validation_hpc.sh
# ---------------------------------------------------------------------------
#SBATCH --job-name=ye2018_rerun_mesh
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Paper_1_Validations/Ye_and_Ghassemi_2018/Paper_Cases/01_Main_Validation
#SBATCH --account=def-biaoli66
#SBATCH --time=24:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --array=0-2
#SBATCH --output=logs/rerun_%A_%a.out
#SBATCH --error=logs/rerun_%A_%a.err

set -euo pipefail

PROJECT_ROOT=${ORCA_ROOT:-/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0}
BASE_DIR=${PROJECT_ROOT}/Paper_1_Validations/Ye_and_Ghassemi_2018/Paper_Cases/00_visualizaiton/inputs/used_in_paper/01_main_validation
IDX=${SLURM_ARRAY_TASK_ID:-0}

SPEC=(SWS3 SWS3 SWS4)
LAW=(BB MC MC)
DECK=(SWS3_OrcaBartonBandisContactTractionFastADHardening SWS3_OrcaMohrCoulombContactTraction SWS4_OrcaMohrCoulombContactTraction)
STEM=(SWS3_OrcaBartonBandisContactTractionFastADHardening SWS3_OrcaMohrCoulombContactTraction_pb06 SWS4_OrcaMohrCoulombContactTraction_center)
ORIG=(2 6 7)
MU_ROUGH=(- 0.952344 0.9804)
C_ROUGH=(- 2.3805e6 3.225e6)
MU_SMOOTH=(- 0.166432 0.1139)
C_SMOOTH=(- 1.19e6 0)
D_ROUGH=(- 5e-5 8e-5)

if (( IDX < 0 || IDX >= ${#SPEC[@]} )); then
  echo "index must be 0..2" >&2; exit 2
fi

S=${SPEC[$IDX]}; L=${LAW[$IDX]}; D=${DECK[$IDX]}; O=${STEM[$IDX]}
CASE_DIR=${BASE_DIR}
echo "rerun idx ${IDX} (was task ${ORIG[$IDX]}): ${S} ${L}"

if [[ ! -d ${CASE_DIR} ]]; then echo "missing case dir: ${CASE_DIR}" >&2; exit 2; fi
cd "${CASE_DIR}"
if [[ ! -f ${D}.i ]]; then echo "missing deck: ${CASE_DIR}/${D}.i" >&2; exit 2; fi

# --- mesh preflight: this is what failed last time, so report it loudly -----
MESH=$(grep -m1 '^mesh_file' "${D}.i" | sed 's/#.*//; s/^[^=]*=[[:space:]]*//; s/[[:space:]]*$//')
if [[ ! -f ${MESH} ]]; then
  echo "MESH NOT FOUND" >&2
  echo "  deck          : ${CASE_DIR}/${D}.i" >&2
  echo "  mesh_file says: ${MESH}" >&2
  echo "  resolved to   : ${CASE_DIR}/${MESH}" >&2
  echo "  cwd           : $(pwd)" >&2
  echo "  contents of mesh/ :" >&2
  ls -la mesh/ >&2 2>/dev/null || echo "    (no mesh/ directory here)" >&2
  exit 2
fi
echo "  deck : ${CASE_DIR}/${D}.i"
echo "  mesh : ${MESH}  ($(stat -c%s "${MESH}") bytes)"

OUTDIR=results/${O}
mkdir -p "${OUTDIR}" logs
echo "  out  : ${CASE_DIR}/${OUTDIR}/"

unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
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
