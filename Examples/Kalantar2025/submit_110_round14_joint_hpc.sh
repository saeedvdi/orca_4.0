#!/bin/bash

# Kalantar ROUND 14 -- OG-SH and OG-SC.
#
#   cd /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/Kalantar2025
#   sbatch submit_110_round14_joint_hpc.sh
#
# WHAT ROUND 13 SETTLED.  110_38 reproduced 110_13 to every printed digit, so its
# ladder is readable:
#
#   D_c (um)  d_s@st9  tau@st9  tau nRMSE  Q nRMSE  mean
#     100      27.40    21.57      29 %     9.3 %    19
#      50      60.72    16.59      24 %      13 %    19
#      30      75.90    14.51      55 %      15 %    35
#      15      77.79    14.26      68 %      16 %    42
#   experiment 42.0     18.97
#
# The response is linear in 1/D_c and the experiment is BRACKETED by 100 and 50 um.
# Interpolating the two channels independently gives 69.5 um from d_s and 65.7 um
# from tau -- they agree, which is why 70 and 60 are the arms here.
#
# THE NEW FINDING, AND IT IS THE MORE IMPORTANT ONE.  Reconstructing the aperture
# budget stage by stage (a_h = a_h0 + normal_stress_aperture - slip_damage, residual
# 0.005-0.076 um) shows OG-SH's closure term spans 0.0013 -> 0.0238 um across the
# ENTIRE experiment. Table 2 needs 0.61 um on the unloading branch alone.
#
# The cause is in ADOrcaRoughnessDamageFracturePermeability::computeStressAperture:
#     opening(N) = V_m*(g(ref) - g(N)),  g(s) = s^p/(sigma_0^p + s^p),  sigma_0 = V_m*K_ni
# With V_m = 1.2 um and K_ni = 1.25e13, sigma_0 = 15 MPa and p = 4, so over OG-SH's
# 33-43 MPa range g sits at 0.96-0.99 -- the joint is on the flat top of its own
# closure curve. The term is not disabled by a flag; it is saturated by its constants.
#
# THIS IS NOT A NEW REPAIR.  OG-SC received exactly this fix in an earlier round --
# bb_max_aperture_closure = 2.6545e-06, sigma_0 = 36.36 MPa, and its closure is
# demonstrably live, spanning 0.0432 -> 1.0512 um in 110_45.  OG-SH never got it.
# That is the whole finding: a known correction that was applied to one specimen and
# not carried across.
#
# WHY IT WAS INVISIBLE.  Table 2's two branches separate the two mechanisms:
#     loading   st1->st5: d_s +37 um, sigma'_n -9.64 MPa (FALLING), a_h -0.54 um
#     unloading st5->st9: d_s + 3 um, sigma'_n +5.66 MPa (RISING),  a_h -0.61 um
# On unloading the joint barely slips, so 0.61 um is pure closure: -0.1078 um/MPa.
# On loading sigma'_n FALLS, so closure would OPEN the joint ~0.98 um; since a_h
# instead falls 0.54, gouge must supply ~1.52 um.  The deck's slip_damage_scale is
# 1.15 um -- exactly Table 2's END-TO-END loss, 4.87 -> 3.72.  The old calibration
# gave the whole loss to gouge because closure contributed nothing, so it got the
# ENDPOINT right and the PATH wrong.  A compensating error -- and it is why the
# control scores Q 9.3 % while every round-13 arm with MORE slip scored worse.
#
# THE FIT AND ITS LIMITS.
#   V_m = 8.0 um, sigma_0 = 24.0 MPa -> K_ni = 3.00e12   RMS 0.084 um (unloading)
#   gouge scale 2.85 um, characteristic slip 52.5 um     RMS 0.053 um (loading)
#   V_m IS A CHOICE, NOT A MEASUREMENT.  RMS is 0.113 at V_m = 4 um, 0.084 at 8,
#   0.078 at 30 -- flat above 6 because g is near-linear over the working range and
#   only the local slope is constrained.  8.0 um is the smallest sane value within
#   8 % of the asymptote for a joint whose aperture is 3.7-4.9 um.  Do not report
#   V_m as fitted.
#
# REFUTED IN ROUND 13, do not re-propose: cohesion as a level knob.  110_43/110_44
# raised OG-SC cohesion 0 -> 0.6 -> 1.0 MPa and it still burst at stage 6
# (tau 9.11/9.16/9.20); 110_42 cut OG-SH cohesion and the joint failed during its own
# preload, stage-1 slip 31.4 um against 2.74.  Under displacement control a stronger
# joint carries more shear stress, so cohesion moves tau and tau_limit together.
#
# Array map:
#   0  OG-SH  110_48_og_sh_dc70_r14              D_c = 70 um ONLY
#   1  OG-SH  110_49_og_sh_aperture_r14          aperture pair ONLY, D_c = 100
#   2  OG-SH  110_50_og_sh_dc70_aperture_r14     both        the candidate
#   3  OG-SH  110_51_og_sh_dc60_aperture_r14     D_c = 60 + aperture
#   4  OG-SC  110_52_og_sc_swres22p66_r14        slip-weakening residual -> 22.660
#   5  OG-SC  110_53_og_sc_dc40_r14              D_c 15.22 -> 40 um
#   6  OG-SC  110_54_og_sc_dc40_swres22p66_r14   both
#
# READING ORDER, AND IT MATTERS.
#
#   python3 scripts/kalantar_gate.py \
#     Examples/Kalantar2025/OGSH/results_csv_hpc/110_48_og_sh_dc70_r14_hpc.csv \
#     --deck Examples/Kalantar2025/OGSH/110_48_og_sh_dc70_r14.i
#
#   Baselines: OG-SH control 110_38 (tau 29 %, Q 9.3 %, mean 19).
#              OG-SC parent  110_45 (tau 36 %, a_h 11 %, mean 23).
#
#   1. TASKS 0 AND 1 BEFORE TASK 2.  They act on different channels -- D_c on tau and
#      d_s, the aperture pair on a_h and Q -- and round 13 already showed a
#      two-parameter arm cannot be attributed when the one-parameter arms have not
#      been run (110_42 changed D_c and cohesion together and was unreadable).
#        110_48 expect d_s@st9 ~ 42 um, tau@st9 ~ 19.0.
#        110_49 expect tau and d_s BARELY TO MOVE -- the aperture law does not feed
#               joint strength -- while a_h falls 0.61 um on the unloading branch
#               instead of the control's 0.029.  IF TAU MOVES MATERIALLY IN 110_49,
#               the two laws are coupled more than assumed and tasks 2 and 3 cannot
#               be read as a sum.  Say so rather than reporting the combined mean.
#   2. Then 110_50, and read it on BOTH channels.  Round 13's trap was that D_c = 50
#      improved tau 29 -> 24 while Q decayed 9.3 -> 13 and the mean never moved.  A
#      mean that does not improve is the result, not a rounding artefact.
#   3. 110_51 brackets D_c under the restored aperture law.  Gouge now saturates over
#      52.5 um instead of 15, so the aperture absorbs slip differently and the best
#      D_c need not be the one interpolated from round-13 runs.
#   4. OG-SC: 110_52 is EXPECTED TO FALL SHORT.  22.660 is this deck's own
#      residual_friction_angle_degrees, and a slip-weakening floor above the basic
#      friction angle would mean slip strengthens the joint -- so it is the physical
#      ceiling, while extrapolating the unloading-branch tau asks for 24.79 deg.  Its
#      job is to show the lever is exhausted.  110_53 is the one that could actually
#      move the burst: a burst is the weakening slope exceeding the machine stiffness,
#      and D_c sets that slope.  Score OG-SC on WHERE IT BURSTS -- it must hold
#      tau ~ 13 MPa through stage 6 (P_i = 21) and break at stage 7 (P_i = 24) -- not
#      on the mean alone.
#
# OG-SC gets NO aperture arm; see the note above about 110_45's closure already being
# live and better fitted (RMS 25 nm, on genuinely slip-free stages) than any
# re-derivation from its post-burst unloading branch.
#
# Checkpoints ON for every task -- rounds 8-10 lost six runs to wall-clock truncation
# with no restart, which is why nothing scoreable was newer than round 6.
#
# Decks generated by scripts/build_110_kalantar_round14_decks.py; all nine Syntax OK.

#SBATCH --job-name=kalantar_110_r14
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/Kalantar2025
#SBATCH --account=def-biaoli66
#SBATCH --time=2-00:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=64
#SBATCH --cpus-per-task=1
#SBATCH --mem=64G
#SBATCH --array=0-6
#SBATCH --output=kalantar_110_r14_%A_%a.out
#SBATCH --error=kalantar_110_r14_%A_%a.err

set -euo pipefail

project_root=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0
study_root=${project_root}/Examples/Kalantar2025

case "${SLURM_ARRAY_TASK_ID}" in
  0) case_dir=OGSH; stem=110_48_og_sh_dc70_r14 ;;
  1) case_dir=OGSH; stem=110_49_og_sh_aperture_r14 ;;
  2) case_dir=OGSH; stem=110_50_og_sh_dc70_aperture_r14 ;;
  3) case_dir=OGSH; stem=110_51_og_sh_dc60_aperture_r14 ;;
  4) case_dir=OGSC; stem=110_52_og_sc_swres22p66_r14 ;;
  5) case_dir=OGSC; stem=110_53_og_sc_dc40_r14 ;;
  6) case_dir=OGSC; stem=110_54_og_sc_dc40_swres22p66_r14 ;;
  *) echo "Unexpected SLURM_ARRAY_TASK_ID=${SLURM_ARRAY_TASK_ID}" >&2; exit 2 ;;
esac

ranks=64
case_path=${study_root}/${case_dir}
input_path=${case_path}/${stem}.i
executable=${project_root}/orca-opt

[[ -f "${input_path}" ]] || { echo "Missing input deck: ${input_path}" >&2; exit 3; }
[[ -x "${executable}" ]] || { echo "Missing application: ${executable}" >&2; exit 4; }

cd "${case_path}"
unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p results_csv_hpc results_exodus_hpc results_checkpoint_hpc logs

echo "Starting array task ${SLURM_ARRAY_TASK_ID}: ${case_dir}/${stem}.i"
echo "SLURM job ${SLURM_ARRAY_JOB_ID}_${SLURM_ARRAY_TASK_ID}; ${ranks} ranks, 64G"

srun --mpi=pmi2 -n "${ranks}" "${executable}" -i "${stem}.i" \
  Outputs/chk/enable=true \
  csv_file_base="results_csv_hpc/${stem}_hpc" \
  exodus_file_base="results_exodus_hpc/${stem}_hpc" \
  checkpoint_file_base="results_checkpoint_hpc/${stem}_hpc"
