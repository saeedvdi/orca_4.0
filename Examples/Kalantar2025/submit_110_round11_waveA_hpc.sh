#!/bin/bash

# Kalantar ROUND 11, WAVE A -- the three 60 s OG-T platen diagnostics.
#
#   cd /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/Kalantar2025
#   sbatch submit_110_round11_waveA_hpc.sh
#
# WHY.  Sampled at the same 5 um of joint slip, the ratio of the joint's own
# effective normal stress to the paper-frame value it should track is 0.515 on
# OG-T r7, 0.509 on OG-T r6 and 0.520 on OG-T r4, against 0.999 on OG-SH, 0.931
# on OG-SC and 0.969 on Ye SW-T1.  OG-T delivers HALF the normal stress to its
# joint, on both meshes and under both load trains, so it yields during its own
# preload at sigma_d ~ 65 MPa instead of holding to the experiment's 160.43 MPa.
# Round 3 blamed fracture-tip clearance and preregistered that the 1.00 mm mesh
# would be markedly worse than the 3.00 mm mesh; it came out 0.509 vs 0.515.
# That hypothesis is refuted.  What was never tested is the platen: both end
# faces are laterally free, and OG-T's fracture spans 94 mm of a 100 mm core.
#
# Array map:
#   0  OG-T  110_32  locked joint, free platens   -- THE NULL, read this first
#   1  OG-T  110_30  bonded platens, both ends    -- the hypothesis
#   2  OG-T  110_31  bonded bottom platen only    -- asymmetric control
#   3  OG-T  110_23  graded mesh, unchanged BCs   -- resolution null (round 8, never run)
#
# 110_23 was built in round 8 and never submitted.  It costs nothing here and it
# is the second null: if the 0.515 deficit is a discretisation artefact of the
# split-interface map rather than mechanics, refining the mesh moves it.  If it
# comes back 0.515 on the graded mesh too, resolution is excluded.
#
# READING ORDER.  If 110_32 still shows ~0.5 with ZERO slip, the shielding is
# elastic, no platen BC can fix it, and a pass in 110_30 is over-constraint
# masking a mesh or interface-map defect -- stop and go at the interface instead.
# Score every arm with scripts/score_110_round11.py.
#
# These are 60 s preload probes with no injection.  They are minutes, not hours.

#SBATCH --job-name=kalantar_110_r11a
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/Kalantar2025
#SBATCH --account=def-biaoli66
#SBATCH --time=03:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --array=0-3
#SBATCH --output=kalantar_110_r11a_%A_%a.out
#SBATCH --error=kalantar_110_r11a_%A_%a.err

set -euo pipefail

project_root=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0
study_root=${project_root}/Examples/Kalantar2025

case "${SLURM_ARRAY_TASK_ID}" in
  0) case_dir=OGT; stem=110_32_og_t_locked_joint_r11 ;;
  1) case_dir=OGT; stem=110_30_og_t_platen_bonded_r11 ;;
  2) case_dir=OGT; stem=110_31_og_t_platen_base_bonded_r11 ;;
  3) case_dir=OGT; stem=110_23_og_t_graded_preload_r8 ;;
  *) echo "Unexpected SLURM_ARRAY_TASK_ID=${SLURM_ARRAY_TASK_ID}" >&2; exit 2 ;;
esac

ranks=32
case_path=${study_root}/${case_dir}
input_path=${case_path}/${stem}.i
executable=${project_root}/orca-opt

if [[ ! -f "${input_path}" ]]; then
  echo "Missing input deck: ${input_path}" >&2
  exit 3
fi

if [[ ! -x "${executable}" ]]; then
  echo "Missing or non-executable application: ${executable}" >&2
  exit 4
fi

cd "${case_path}"

unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p results_csv_hpc results_exodus_hpc results_checkpoint_hpc logs

echo "Starting array task ${SLURM_ARRAY_TASK_ID}: ${case_dir}/${stem}.i"
echo "SLURM job ${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}; ${ranks} ranks, 32G"

srun --mpi=pmi2 -n "${ranks}" "${executable}" -i "${stem}.i" \
  Outputs/chk/enable=false \
  csv_file_base="results_csv_hpc/${stem}_hpc" \
  exodus_file_base="results_exodus_hpc/${stem}_hpc"
