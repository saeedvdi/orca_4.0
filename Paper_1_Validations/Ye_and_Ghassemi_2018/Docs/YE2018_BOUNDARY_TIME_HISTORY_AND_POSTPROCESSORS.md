# Ye and Ghassemi (2018): axial-boundary time history and postprocessor audit

## Scope

This note explains how the finite-stiffness axial boundary acts over time in the four 116-series protocol-consistency models and identifies the validation quantities obtained from its postprocessors. The Barton--Bandis (BB) and Mohr--Coulomb (MC) models for a given specimen use the same boundary stiffness and actuator-command history. Their calculated top displacement and reaction can differ after slip because their fracture constitutive responses differ.

## Command history used in the four specimens

All four specimens use the same three-stage form:

$$
\bar u_z(t)=
\begin{cases}
u_0, & 0\le t<2\ \mathrm{s},\\
u_0+(u_f-u_0)(t-2)/53, & 2\le t<55\ \mathrm{s},\\
u_f, & t\ge55\ \mathrm{s}.
\end{cases}
$$

The specimen-specific values are:

| Specimen | Fracture angle | End time (s) | $k_p$ (Pa/m) | $u_0$ (mm) | $u_f$ (mm) | Ramp rate, 2--55 s (mm/s) |
|---|---:|---:|---:|---:|---:|---:|
| SW-T1 | $32^\circ$ | 3500.00 | $3.9709691\times10^{11}$ | -0.078067 | -0.748076 | -0.012642 |
| SW-T2 | $31^\circ$ | 2852.53 | $3.9709691\times10^{11}$ | -0.078067 | -0.849161 | -0.014549 |
| SW-S3 | $29^\circ$ | 4802.00 | $3.9693975\times10^{11}$ | -0.078097 | -0.216230 | -0.002606 |
| SW-S4 | $30^\circ$ | 3500.00 | $3.9725416\times10^{11}$ | -0.078036 | -0.198236 | -0.002268 |

The nearly identical values of $u_0$ precompress the boundary spring to approximately 31 MPa and balance the inherited isotropic initial stress. Between 2 and 55 s, the command becomes more compressive and establishes the specimen-specific axial preload. The tensile-fracture specimens require much larger final commands because their target axial stresses are higher. This is not caused by a different machine stiffness: all four use $K_{\mathrm{sys}}=Ak_p=796$ kN/mm.

After 55 s, the command is constant in the main BB and MC cases. The SW-S4 expression still contains the older `poro_du` and `axial_relax_du` terms, but both coefficients are set to zero in cases 116_07--116_09. Its command is therefore also exactly constant after 55 s. The SWT2 `eqhold` cases 116_10 and 116_11 use the same axial command as cases 116_03 and 116_04.

## What remains fixed and what is allowed to evolve

For $t\ge55$ s, only the remote command is fixed:

$$
\bar u_z(t)=u_f.
$$

The specimen-top displacement is an unknown of the coupled problem. At every converged time step,

$$
t_z(t)=k_p\left[u_f-u_z(t)\right].
$$

Therefore, neither $u_z(t)$ nor $t_z(t)$ is held constant. Fluid pressure changes effective normal stress and may cause fracture slip, dilation, closure, and bulk poroelastic deformation. These mechanisms change $u_z$, which changes the spring gap and axial reaction. For example, if the specimen accommodates additional compressive shortening, $u_z$ becomes more negative and moves closer to the negative command $u_f$. The spring gap becomes smaller and the axial compression decreases. This produces stress relaxation even though the command does not move.

The sequence during each accepted time step is:

1. evaluate the command $\bar u_z(t)$;
2. use the current trial top displacement to assemble the penalty residual and Jacobian;
3. solve the monolithic displacement--pressure--fracture equilibrium problem;
4. accept the converged top displacement and reaction; and
5. evaluate the postprocessors and write them to the CSV file.

The boundary is thus part of every Newton solve. It is not a load calculated once and then applied unchanged.

## Postprocessor calculation chain

The main boundary quantities are calculated in the following order:

$$
\bar u_z
\xrightarrow{\text{function}}
\left(\bar u_z,\langle u_z\rangle_{\Gamma_t}\right)
\xrightarrow{\text{subtraction}}
\Delta u_{\mathrm{spring}}
\xrightarrow{\times k_p}
\sigma_1^{\mathrm{spring}}.
$$

The independent reaction route is

$$
\boldsymbol{R}_{\mathrm{internal}}
\xrightarrow{\texttt{mech\_reaction tag}}
F_z^R
\xrightarrow{/A}
\sigma_1^R
\xrightarrow{-\sigma_3}
q.
$$

The corresponding input-file names are:

| Quantity | Postprocessor | Direct or derived? |
|---|---|---|
| Command $\bar u_z$ | `axial_command_m_pp` | Direct evaluation of the boundary function |
| Mean top displacement | `top_disp_z_mean_m_pp` | Direct side average of the solved displacement |
| Spring gap | `machine_spring_gap_m_pp` | Difference between the preceding two quantities |
| Spring traction magnitude | `machine_spring_sigma1_mpa_pp` | Gap multiplied by $k_p$ |
| Raw top reaction | `top_reaction_z_raw` | Direct sum of the tagged internal nodal residual |
| Reaction stress | `sigma1_reaction_mpa_pp` | Absolute reaction divided by nominal area |
| Differential stress | `differential_stress_reaction_mpa_pp` | Reaction stress minus 30 MPa confinement |
| Reaction--spring difference | `reaction_vs_machine_spring_mpa_pp` | Signed implementation diagnostic |

The word *direct* here means that a postprocessor reads a function, field, tagged residual, or material property without fitting it to Table 2. It does not mean that every value is an independent experimental measurement.

## Area normalization in the reaction check

The meshed top areas in the available outputs are about 0.2853% smaller than the nominal circular areas used by `sigma1_reaction_mpa_pp`. The calculated relation is

$$
\frac{\sigma_1^{R,A}-\sigma_1^{\mathrm{spring}}}
{\sigma_1^{\mathrm{spring}}}
\approx-0.2853\%.
$$

This exactly explains the small negative value of `reaction_vs_machine_spring_mpa_pp`. It is not evidence of failed force equilibrium. An area-consistent check should instead use

$$
\sigma_1^{R,\mathrm{FE}}
=\frac{|F_z^R|}{A_{\mathrm{FE}}},
$$

where $A_{\mathrm{FE}}$ is `top_boundary_area_pp`. The corrected comparison can be calculated from the existing CSV files without rerunning the simulations.

## Validation quantities that depend on the boundary

The reaction gives the differential stress

$$
q=\sigma_1^R-\sigma_3.
$$

For a fracture plane at angle $\theta$ to the specimen axis, the paper-frame stresses are

$$
\sigma_n'=\sigma_3+q\sin^2\theta-p_f,
\qquad
\tau=q\sin\theta\cos\theta,
$$

where the validation inputs use $p_f=(p_{\mathrm{in}}+p_{\mathrm{out}})/2$. The exact coefficients used in the four inputs are:

| Specimen | $\sin^2\theta$ | $\sin\theta\cos\theta$ | Output names |
|---|---:|---:|---|
| SW-T1 | 0.280814 | 0.449397 | `effective_normal_paper_frame_mpa_pp`, `shear_stress_paper_frame_mpa_pp` |
| SW-T2 | 0.265264 | 0.441474 | same |
| SW-S3 | 0.235040 | 0.424024 | same |
| SW-S4 | 0.250000 | 0.433013 | same |

Thus, two of the five Table 2 scoring channels come from the reaction chain:

1. effective normal stress, $\sigma_n'$; and
2. shear stress, $\tau$.

The remaining scoring channels do not come from the axial-boundary postprocessors:

3. shear displacement: `reported_czm_shear_slip_mm_pp`;
4. normal displacement: `czm_normal_dilation_paper_mm_pp`; and
5. flow rate: `flow_rate_validation_ml_min_pp`.

Hydraulic aperture and permeability are retained as constitutive diagnostics but are not scored independently because Ye and Ghassemi inferred them from the measured flow.

## Illustration from the currently available completed CSV files

The following values show how a fixed command can coexist with an evolving displacement and reaction. Values are taken from the final row of completed local copies.

| Case | Time (s) | Command (mm) | Mean top displacement (mm) | Spring gap (mm) | Spring stress (MPa) | Reaction stress (MPa) |
|---|---:|---:|---:|---:|---:|---:|
| SW-T1 MC, 116_02 | 3500 | -0.748076 | -0.493813 | 0.254263 | 100.967 | 100.679 |
| SW-S3 BB, 116_05 | 4802 | -0.216230 | -0.122220 | 0.094010 | 37.316 | 37.210 |
| SW-S4 BB, 116_07 | 3500 | -0.198236 | -0.104919 | 0.093317 | 37.070 | 36.965 |
| SW-S4 MC, 116_08 | 3500 | -0.198236 | -0.095698 | 0.102538 | 40.734 | 40.618 |

For example, the SW-S4 BB command remains at -0.198236 mm after 55 s. The mean specimen-top displacement changes from approximately -0.0485 mm just after preload to -0.1049 mm at 3500 s. The spring gap consequently decreases from about 0.1497 to 0.0933 mm, and the axial stress decreases from about 59.5 to 37.1 MPa. This is the intended fixed-command, finite-stiffness response.

At the time of this audit, the local SW-T1 BB CSV ends at 2834 s instead of its requested 3500 s, and the SW-S3 MC CSV ends at 1628.94 s instead of 4802 s. No SWT2 116-series CSV is present in the local validation folder. These particular files should not be treated as completed full-cycle validations unless newer HPC outputs exist elsewhere.

## Initial-row caution

The $t=0$ CSV rows currently show zero for the boundary postprocessors, although the command function specifies $u_0\approx-0.078$ mm. These postprocessors were not explicitly executed on `INITIAL`; their zero entries are default initialization values. The first accepted time-step row shows the applied spring state. The $t=0$ row should be excluded from boundary validation unless future inputs explicitly add `execute_on = 'INITIAL TIMESTEP_END'` and verify the initialization sequence.

## Recommended checks

For every completed BB and MC case:

1. verify that `axial_command_m_pp` equals $u_f$ and remains constant after 55 s;
2. calculate $|F_z^R|/A_{\mathrm{FE}}$ and compare it with `machine_spring_sigma1_mpa_pp`;
3. verify that no plastic slip develops during the preload stage unless it is experimentally intended;
4. compare the reaction-based $\sigma_n'$ and $\tau$ with the eleven Table 2 stages;
5. compare BB and MC only after confirming that both used the same command, stiffness, pressure history, and confinement; and
6. do not interpret the zero-valued initial CSV row as the physical initial spring state.
