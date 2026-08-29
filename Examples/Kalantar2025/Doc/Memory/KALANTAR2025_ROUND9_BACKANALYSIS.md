# Kalantar 2025 — Round-9 outcome and Round-10 run design

Date: 2026-08-28. Branch: `orca_v10`.

## Round-9 outcome

- OG-SC `110_24` reached its stage-7 horizon and passed four of five gates. It missed
  only `tau_6 = 12.95 +/- 0.25 MPa`: the result was 13.277 MPa. The preregistered
  rule says not to promote it to a full cycle. The physically defined paper-mean
  pressure is retained as evidence; no fitted pressure coefficient is restored.
- OG-SH `110_25`, the `b=0` direct-rate control, reached stage 5 but failed both
  physical outcome gates: 25.244 um slip against 30–60 um and 22.081 MPa shear
  stress against `<=21.14 MPa`.
- OG-SH `110_26`, `b=0.006`, stopped at 408.189/2000 s. Its output timestep fell
  repeatedly to 0.013–0.05 s immediately after the first hold while slip velocity
  toggled around zero. It is a convergence failure, not a physical result. The HPC
  stdout/stderr was not present in the downloaded artifacts, so the exact nonlinear
  failure message remains required evidence.
- OG-T `110_23` has an input deck but no CSV. It must be resubmitted unchanged; no
  parameter inference is allowed until its 60 s preload gates are available.

## Round-10 decision

The next attributable step is to close the aging bracket between the completed
`b=0` control and the incomplete `b=0.006` arm. At the user's request, the two
OG-SH diagnostics cover the complete pressure cycle rather than stopping at stage 5:

| deck | only physical change | horizon |
|---|---:|---:|
| `110_27_og_sh_rsf_a010_b002_r10.i` | `rsf_b=0.002` | full 9 stages, 3600 s |
| `110_28_og_sh_rsf_a010_b004_r10.i` | `rsf_b=0.004` | full 9 stages, 3600 s |

Both retain `a=0.010`, `D_rs=50 um`, `V0=5e-8 m/s`, the BB law, mesh, loading,
solver, and outputs. A separately named OG-T deck, `110_29_og_t_graded_full_r10.i`,
extends the `110_23` graded-mesh probe through all 17 stages to 6800 s. Its full-cycle
timestep schedule and production Exodus cadence come from `110_11`; its graded mesh,
exact source nodes, corrected frame, material model, boundary conditions, and loading
functions remain those of `110_23`.

Pass criteria for either OG-SH arm are: reach 3600 s without a cutback cascade,
stage-5 in-plane slip 30–60 um, `tau_5<=21.14 MPa`, finite outputs through stage 9,
and no runaway. A monotone
move from `b=0` through 0.002 and 0.004 toward both gates supports aging. If both
complete and miss, aging alone is insufficient. If convergence fails at a
reproducible `b` threshold, obtain the full HPC nonlinear logs and investigate the
RSF active-set/tangent before changing another physical parameter.

For OG-T, the first 60 s remains a gate: zero cumulative plastic slip, positive
constitutive-versus-paper-frame normal-stress slope, and at most 5% normal-stress
disagreement. The full output is retained if that gate fails, but the injection stages
are then diagnostic and must not be scored as a valid constitutive response.

OG-SC is deliberately absent from Round 10. Promoting `110_24` after it failed a
written gate, or adjusting a parameter to erase a 0.077 MPa gate miss, would rewrite
the decision rule after seeing the result.
