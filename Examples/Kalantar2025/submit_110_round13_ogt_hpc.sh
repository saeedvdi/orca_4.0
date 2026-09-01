#!/bin/bash

# Kalantar ROUND 13 -- OG-T FLOW-PATH PROBES.
#
#   cd /home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/Kalantar2025
#   sbatch submit_110_round13_ogt_hpc.sh
#
# Submitted SEPARATELY from the joint-law arms on purpose: these are 600 s probes that
# finish in minutes, and a 6 h reservation will start far sooner in the queue than the
# 48 h one. The OG-T gate result should come back before the OG-SH ladder does.
#
# WHY.  Round 12 lengthened the preload ramp 53 s -> 9998 s and cut the interface
# overpressure 48.9 -> 21.0 MPa, but failed all five of its gates.  The end of 110_36
# says why.  With the load HELD constant from t = 10000 to 14000 s, p - 3 MPa decays
# with a time constant that converges to 3449 s:
#
#     t = 10325   p = 5.836   tau_fit = 3572 s
#     t = 12275   p = 4.591   tau_fit = 3401 s
#     t = 14000   p = 3.974   tau_fit = 3449 s
#
# The round-12 rationale assumed 1.0e3 s.  c = kM/mu = 1.4e-20 * 108.3e9 / 1e-3 =
# 1.516e-6 m^2/s is correct, so tau = 3449 s implies a drainage length of
# sqrt(c*tau) = 72 mm.  The CONCEPT was right and the LENGTH was wrong -- 9998 s is
# 2.9 time constants, not the 10 it was sold as.
#
# 72 mm is not the port spacing.  It is radial convergence into a SINGLE NODE.  [BCs]
# has exactly two pore-pressure boundaries, source_in and source_out, each an
# ExtraNodesetGenerator with use_closest_node = true; every other surface is no-flow.
# The whole specimen drains through two points on a 0.10 um fracture.
#
# Chasing this with ramp length does not work.  Quasi-steady overpressure is
# (dp/dsigma_d) * (sigma_d_final / T) * tau; with the measured 0.254, 160.43 MPa and
# 3449 s, dp <= 3 MPa needs T >= 4.7e4 s, and the observed relief is WEAKER than that
# single-mode estimate (it predicts 9.5 MPa at the end of round 12's ramp; the run
# showed 20.5).  The empirical scaling is worse still: a 189x longer ramp bought 18 %
# relief in dp/dsigma_d, 0.305 -> 0.249.
#
# THE FIX.  The reading notes' own plane-channel model has the inlet and outlet as
# LINE SOURCES SPANNING THE FULL WIDTH W, not points.  These decks build that with a
# BoundingBoxNodeSetGenerator around each port.  Verified against
# mesh/kalantar2025_og_t_theta28_graded.e: 11 nodes each, spanning y = -14.910 to
# +14.910 mm, against a predicted chord half-width sqrt(r^2 - x^2) = 15.221 mm.
# The BCs AND all four port postprocessors per side are repointed onto the line --
# inj_reaction_sum_pp is a NodalSum and flow_rate_pp is built straight off it, so a
# BC on 11 nodes with a postprocessor on 1 would report a ninth of the mass.
#
# This is the paper's stated geometry, not a new fit.  It touches neither the aperture
# (0.10 um, faithful to Table 2) nor the matrix permeability (1.4e-20, Kalantar
# section 2.1).  IT IS NOT A MECHANICAL BOUNDARY CONDITION -- five of those have been
# falsified on OG-T and that finding stands; a flow path is a different object.
#
# The ramp goes BACK to the original 53 s.  Round 12 already priced the long ramp; if
# the ports are the bottleneck the short ramp must work, and if it does OG-T becomes
# cheap again for every future round.
#
# Array map:
#   0  110_46_og_t_lineport_r13             line ports, 53 s ramp          THE GATE
#   1  110_47_og_t_lineport_drainends_r13   + pore pressure 3 MPa on the platens
#
# READ TASK 0 FIRST:
#
#   python3 scripts/score_110_round11.py \
#     Examples/Kalantar2025/OGT/results_csv_hpc/110_46_og_t_lineport_r13_hpc.csv
#
#   Baseline to beat is 110_08 (same 53 s ramp, point ports): dp = 48.9 MPa.
#   Round 12 with a 189x longer ramp and point ports reached 21.0.
#
#   1. dp_MPa                                  <= 3.0
#   2. bb_effective_normal_stress_pp / effective_normal_paper_frame_mpa_pp  >= 0.93
#   3. pre-slip slope d(sigma'_n)/d(sigma_d)   +0.22 +- 0.04
#   4. tau/tau_limit at sigma_d = 160.43 MPa   < 1.0
#   5. cumulative_plastic_slip at 600 s        < 10 um
#
# GATES 2 AND 3 ARE KNOWN TO BE MIS-SPECIFIED -- READ THIS BEFORE SCORING.
# effective_normal_paper_frame_mpa_pp is a TOTAL stress: it regresses on sigma_d at
# +0.2544 with no pore-pressure subtraction.  bb_effective_normal_stress_pp is an
# EFFECTIVE one.  Over the 243 pre-slip steps of 110_36,
#
#     bb_eff - (paper_frame - interface_pressure) = +3.151 +- 0.077 MPa
#
# constant to 0.08 MPa while sigma_d went 0 -> 82 and p went 0 -> 23.  That constant is
# p_out = 3.0 MPa.  110_08 gives the same, +3.287 +- 0.188.  So the ratio is
# effective / total and cannot reach 0.93 while p is large, BY CONSTRUCTION -- it was
# never a statement about whether load reaches the joint, and the load path was never
# broken.  This is also the "+0.277 slope offset" that has been chased since round 7.
# Score gate 1 (dp), 4 (yield) and 5 (slip), which are sound.  For 2 and 3 use
# bb_eff against (paper_frame - interface_pressure + p_out).
#
# TASK 1 IS A BOUND, NOT A MODEL.  Holding pore pressure at 3 MPa on the platens is a
# claim about Kalantar's apparatus -- that the end platens are fluid-connected -- and
# the reading notes do NOT confirm it.  If task 0 passes, task 1 is surplus; report it
# and move on.  If task 0 fails and task 1 passes, what you have learned is how much
# extra drainage OG-T needs, not that the apparatus provides it.  Do not put task 1 in
# the paper as a validated configuration without evidence from the experiment.
#
# IF BOTH FAIL, the ports are not the bottleneck either and the 3449 s is intrinsic to
# the matrix at 1.4e-20 m^2.  The remaining honest option is to stop simulating the
# preload transient at all -- initialise pore pressure at 3 MPa uniform, apply the
# axial load in a steady solve, and start the transient at the top of the injection
# cycle.  The lab preload was slow enough to be drained; reproducing its transient is
# not part of the validation.  That is a deck change, not a round.
#
# Decks generated by scripts/build_110_kalantar_round13_decks.py; both Syntax OK.

#SBATCH --job-name=kalantar_110_r13_ogt
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/Kalantar2025
#SBATCH --account=def-biaoli66
#SBATCH --time=6:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=32G
#SBATCH --array=0-1
#SBATCH --output=kalantar_110_r13_ogt_%A_%a.out
#SBATCH --error=kalantar_110_r13_ogt_%A_%a.err

set -euo pipefail

project_root=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0
study_root=${project_root}/Examples/Kalantar2025

case "${SLURM_ARRAY_TASK_ID}" in
  0) case_dir=OGT; stem=110_46_og_t_lineport_r13 ;;
  1) case_dir=OGT; stem=110_47_og_t_lineport_drainends_r13 ;;
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

# 600 s probes, ~400 steps. No checkpoints needed.
srun --mpi=pmi2 -n "${ranks}" "${executable}" -i "${stem}.i" \
  Outputs/chk/enable=false \
  csv_file_base="results_csv_hpc/${stem}_hpc" \
  exodus_file_base="results_exodus_hpc/${stem}_hpc" \
  checkpoint_file_base="results_checkpoint_hpc/${stem}_hpc"
