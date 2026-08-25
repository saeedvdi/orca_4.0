# Kalantar 2025 — round-5 back-analysis and round-6 run design

**2026-08-25.** OG-SH and OG-SC are complete. The available OG-T CSV is a live or
truncated snapshot at 3305.5/6800 s (48.6%); it is diagnostic only and is not scored.
The old direct gate repeated its last row through unreached holds, so
`scripts/kalantar_gate.py` now stops at the last reached hold and refuses an aggregate
score until the deck end time is present.

## 1. Scorecard

| specimen | round 4 mean nRMSE | round 5 mean nRMSE | force | scored flow | state |
|---|---:|---:|---:|---:|---|
| OG-SH | 31 | **21.87** | tau 34.85 | Q 8.89 | complete |
| OG-SC | 29 | **28.95** | tau 47.41 | a_h 10.48 | complete; statistically unchanged |
| OG-T | 58 (control) | — | — | — | **48.6%, not scoreable** |

The round-5 frame change helped OG-SH's aggregate score but did not close its coupled
response. OG-SC's successful closure fit survived the frame change: its aperture score
remains 10. OG-T still has hundreds of micrometres of slip before the first scored hold,
so no constitutive parameter is identifiable from it.

## 2. The three preregistered nulls

### 2.1 OG-SH stage-5/9 slip: failed on outcome

The prediction was stage-9 slip `48 +/- 5 um`, at unchanged `D_c = 150 um`. Round 5
stopped accumulating plastic slip after stage 5 and ended at **23.14 um**. At stage 5:

| | Table 2 | round 3, soft frame | round 5, corrected frame |
|---|---:|---:|---:|
| tau [MPa] | 19.57 | 21.22 | **22.48** |
| reported slip [um] | 44.6 | 55.25 | **23.18** |

The frame correction overshot the desired response: too little slip and too much force.
That is a failed outcome null, not evidence that the frame derivation was wrong.

### 2.2 Frame unloading slope: passed on mechanism

Use the within-run pressurization path, where the axial command is fixed and the joint
actually moves. Between stages 1 and 5:

```
round 3:  -(21.2225 - 25.6335) / (55.2516 - 2.8093) = 84.11 MPa/mm
round 5:  -(22.4765 - 25.8607) / (23.1786 - 2.7438) = 165.61 MPa/mm
expected from measured K_sys in the model slip frame                  = 172.0 MPa/mm
```

Round 5 is within 3.7% of the target. The earlier cross-run secant was not a valid
frame-stiffness measurement because changing the boundary stiffness moves the nonlinear
equilibrium branch. The within-run slope is the direct test. **The frame fix is closed.**

### 2.3 OG-SC aperture: passed

The no-change null was `a_h(stage 6) = 1.60 +/- 0.10 um`. Round 5 gives **1.53 um**,
the same as round 4. Keep `V_m`, `K_ni`, and the residual angle fixed.

## 3. What remains

### OG-SH: re-bracket D_c on the corrected frame

The frame is now a verified boundary condition. At `D_c = 150 um`, the model is too
stable (`tau_5 +14.9%`, slip `23.18` vs `44.6 um`). Round 6 therefore uses a single
corrected-frame bracket arm at **`D_c = 100 um`**. This is deliberately not another fit
to `tau(s_measured)`; the run must solve its own coupled slip.

Preregistered null: **stage-5 slip = `45 +/- 15 um`, and tau error < +8%.** If it
overshoots past 60 um, the bracket lies between 100 and 150 um. If it stays below 30 um,
`D_c` is not sufficiently leveraged on the corrected branch and should not be swept again.

### OG-SC: inherited tangential viscosity is now isolated

Round 5 reduced burst slip from 64.9 to 45.3 um but the model still burst at stage 6;
the paper stays locked through stage 6 and bursts at stage 7. Before the burst the model
has accumulated **3.75 um plastic slip at stage 5**, while Table 2 resolves only 1.2 um
axial shortening at that point (about 1.4 um in-plane). That premature slip degrades the
otherwise correctly bracketed envelope.

Round 6 changes only `tangential_viscosity`, **`4e11 -> 2e12 Pa.s/m`**. Preregistered
null: **stage-5 plastic slip <= 2 um and the first macroscopic burst moves to stage 7.**
The aperture/closure constants, residual, `D_c`, frame, mesh, and schedule are held.

### OG-T: test geometry before physics

The round-5 snapshot remains invalid before injection. A second full 28-degree run cannot
identify a material constant. The remaining falsifier is the verified 26-degree sensitivity
mesh: it requires a 104.48 mm core and reduces fracture-tip clearance from 3.00 to 1.00 mm.

Round 6 therefore submits only a **60 s preload probe** on the 26-degree arm. If tip
interaction causes the inversion, the slope of constitutive normal stress versus the
paper-frame value must become still more negative. If it improves, the clearance ordering
is falsified and the axial/traction boundary must be revisited. No Table-2 score or flow
claim is permitted from this arm.

## 4. Round-6 files and resources

| file | purpose | submitted horizon |
|---|---|---:|
| `OGSH/110_13_og_sh_bbfast_r6.i` | corrected-frame D_c bracket | 3600 s |
| `OGT/110_14_og_t_preload_probe.i` | 26-degree tip-clearance falsifier | 60 s |
| `OGSC/110_15_og_sc_bbfast_r6.i` | 5x tangential-viscosity arm | 9100 s |

All three SLURM scripts request one node, **64 MPI ranks, 64 GB, and 24 hours**. Their
`#SBATCH --ntasks` and `srun -n` values are verified equal. All three inputs return
`Syntax OK` under the `moose` environment.
