# Boundary penalty loading and inference of the adopted values

## Purpose and scope

This note explains the finite-stiffness axial boundary used in the Orca triaxial simulations and documents how the values in the Ye and Ghassemi protocol-consistency cases were obtained. The boundary formulation is general to Orca models that use `FunctionPenaltyDirichletBC`. The numerical values given here are specific to the four Sierra White specimens.

The penalty in this boundary condition represents the stiffness of the external loading system. It should not be confused with the normal or tangential penalties used by the internal fracture-contact law.

## Boundary formulation

Let $\bar u_z(t)$ denote the imposed actuator command and $u_z$ the calculated displacement of the specimen top. The weak contribution of the penalty boundary can be written as

$$
R_i^{\Gamma_t}=\int_{\Gamma_t}N_i k_p\left(u_z-\bar u_z\right)\,\mathrm d\Gamma,
$$

where $N_i$ is the test function and $k_p$ is the areal penalty stiffness. The corresponding traction acting on the specimen is

$$
t_z=k_p\left(\bar u_z-u_z\right).
$$

Compression is negative in the input files. It is therefore convenient to report the compressive axial-stress magnitude as

$$
\sigma_1^{\mathrm{spring}}=k_p\left|u_z-\bar u_z\right|.
$$

The boundary is equivalent to a distributed set of axial springs. If the top displacement is approximately uniform, its resultant force is

$$
F_z=A k_p\left(\bar u_z-u_z\right),
$$

where $A$ is the top-surface area. Equivalence with a testing system having total stiffness $K_{\mathrm{sys}}$ requires

$$
k_p=\frac{K_{\mathrm{sys}}}{A}.
$$

This conversion is important because `FunctionPenaltyDirichletBC` requires stiffness per unit area, whereas testing-machine stiffness is normally reported as force per displacement.

## Numerical penalty versus physical boundary stiffness

The name `FunctionPenaltyDirichletBC` can lead to two different interpretations. In its usual numerical use, the class weakly approximates the essential condition

$$
u_z=\bar u_z \qquad \text{on }\Gamma_t.
$$

The penalty is then an artificial numerical parameter. It should be large enough that the difference between the calculated displacement and the prescribed value is acceptably small, but not so large that the Jacobian becomes ill-conditioned. The MOOSE documentation sometimes expresses the perturbed boundary condition using a small compliance parameter $\varepsilon$. The input parameter is its inverse,

$$
k_p=\frac{1}{\varepsilon}.
$$

Therefore, it is $\varepsilon$ that must be small, whereas the MOOSE input parameter `penalty` must be large when the purpose is to approximate an exact Dirichlet condition. The two statements are equivalent and should not be confused.

The present simulations use the same weak term for a different purpose. Here, $k_p$ is assigned the finite stiffness of the loading system per unit area. The resulting condition is then a physical Robin, or spring, boundary rather than a numerical approximation that is intended to satisfy $u_z=\bar u_z$. The use of a class with `DirichletBC` in its name does not change the mathematical boundary represented by a finite value of $k_p$.

## Variational derivation

Let $\boldsymbol{u}$ be the displacement field and let $\boldsymbol{w}$ be an admissible test function. For simplicity, only the axial component on the top surface is considered. Adding a distributed spring to the mechanical potential gives

$$
\Pi_{\mathrm{tot}}(\boldsymbol{u})
=\Pi_{\Omega}(\boldsymbol{u})
+\frac{1}{2}\int_{\Gamma_t}k_p\left(u_z-\bar u_z\right)^2\,\mathrm d\Gamma.
$$

The first variation of the spring energy is

$$
\delta\Pi_{\Gamma_t}
=\int_{\Gamma_t}k_p\left(u_z-\bar u_z\right)w_z\,\mathrm d\Gamma.
$$

After finite-element interpolation, $u_z=\sum_jN_jU_j$, this term contributes

$$
R_i^{\Gamma_t}
=\int_{\Gamma_t}N_i k_p\left(u_z-\bar u_z\right)\,\mathrm d\Gamma
$$

to the residual and

$$
J_{ij}^{\Gamma_t}
=\frac{\partial R_i^{\Gamma_t}}{\partial U_j}
=\int_{\Gamma_t}N_i k_pN_j\,\mathrm d\Gamma
$$

to the Jacobian. These expressions agree with the MOOSE implementation, which evaluates a quadrature-point residual proportional to $k_pN_i(u_z-\bar u_z)$ and a diagonal Jacobian contribution proportional to $k_pN_iN_j$.

Combining the spring contribution with the natural mechanical boundary term gives

$$
t_z=k_p\left(\bar u_z-u_z\right).
$$

Consequently, the displacement mismatch is not zero for a finite penalty:

$$
e_z=u_z-\bar u_z=-\frac{t_z}{k_p},
\qquad
\left|e_z\right|=\frac{\left|t_z\right|}{k_p}.
$$

This equation provides the clearest interpretation of the boundary. If $k_p$ is increased while $t_z$ remains bounded, $|e_z|$ decreases and the exact Dirichlet limit is approached. If $k_p$ represents a finite machine stiffness, the nonzero mismatch represents deformation of the loading system and must not be treated as an enforcement error.

A useful normalized measure for a numerical Dirichlet penalty is

$$
\epsilon_D
=\frac{\left|u_z-\bar u_z\right|}{u_{\mathrm{ref}}}
=\frac{\left|t_z\right|}{k_pu_{\mathrm{ref}}},
$$

where $u_{\mathrm{ref}}$ is a relevant displacement scale. The approximation $u_z\approx\bar u_z$ is justified only when $\epsilon_D$ is small over the loading history. For an elasticity problem, a common numerical scaling is $k_p\sim\gamma E_{\mathrm{eff}}/h$, where $h$ is the boundary-element size and $\gamma$ is a dimensionless factor. Increasing $\gamma$ reduces the boundary mismatch but increases the contrast between the penalty and bulk Jacobian terms. This explains the practical requirement that the penalty be large enough for accuracy but not excessively large for conditioning.

## One-dimensional stiffness interpretation

The distinction can be shown using a one-dimensional specimen. Let its stiffness be

$$
K_s=\frac{E_{\mathrm{eff}}A}{L},
$$

and let the distributed boundary have total stiffness $K_p=Ak_p$. Force equilibrium gives

$$
K_su_z=K_p\left(\bar u_z-u_z\right).
$$

It follows that

$$
\frac{u_z}{\bar u_z}=\frac{K_p}{K_s+K_p},
\qquad
\frac{\bar u_z-u_z}{\bar u_z}=\frac{K_s}{K_s+K_p},
$$

and the combined stiffness seen by the actuator is

$$
K_{\mathrm{eq}}
=\left(\frac{1}{K_s}+\frac{1}{K_p}\right)^{-1}.
$$

Thus, $K_p\gg K_s$ gives $u_z\approx\bar u_z$ and approaches an exact displacement boundary. When $K_p$ is comparable to $K_s$, the specimen and boundary spring share the commanded displacement, and the condition is intentionally compliant.

For the 116-series cases, $E=67$ GPa and $k_p\approx3.97\times10^{11}$ Pa/m. Using the reported specimen lengths gives the following intact-bar estimates:

| Specimen | $L$ (mm) | $E/L$ (Pa/m) | $k_p/(E/L)$ | Estimated $u_z/\bar u_z$ |
|---|---:|---:|---:|---:|
| SW-T1 | 128.80 | $5.20\times10^{11}$ | 0.763 | 0.433 |
| SW-T2 | 132.70 | $5.05\times10^{11}$ | 0.786 | 0.440 |
| SW-S3 | 123.40 | $5.43\times10^{11}$ | 0.731 | 0.422 |
| SW-S4 | 118.70 | $5.64\times10^{11}$ | 0.704 | 0.413 |

These estimates ignore the inclined fracture and three-dimensional stress state, so they are explanatory rather than predictive. However, they show that the adopted $k_p$ is comparable to, rather than much larger than, the specimen stiffness. The 116-series boundary should therefore be described as a finite-stiffness spring boundary implemented with `FunctionPenaltyDirichletBC`. It should not be described as a nearly exact Dirichlet condition.

The same conclusion follows directly from the spring gap. With $k_p=3.97\times10^{11}$ Pa/m, axial stresses of 31, 60, and 180 MPa require displacement differences of approximately 0.078, 0.151, and 0.453 mm, respectively. These differences are mechanically significant at laboratory-specimen scale. They are part of the imposed compliance model, not small numerical violations of a prescribed displacement.

## Physical meaning

A strong displacement boundary would impose $u_z=\bar u_z$ exactly and would represent an infinitely stiff loading frame. A prescribed-force boundary would represent the opposite limit and would maintain the axial force while the fracture weakens. Neither limit represents a remote actuator command held fixed through a compliant load train.

The finite-stiffness boundary is a Robin-type condition between these two limits. During the injection stage, $\bar u_z$ is held constant, but $u_z$ may change because of bulk deformation, fracture slip, dilation, closure, and poroelastic deformation. The spring gap and axial reaction can therefore change even though the remote command does not. This permits the stress relaxation expected when a specimen slips in a testing system with finite stiffness.

The numerical reaction provides a direct implementation check. The stress obtained from the summed top reaction should agree with $k_p|u_z-\bar u_z|$, apart from discretization and averaging differences.

## Source of the common system stiffness

The protocol-consistency cases use

$$
K_{\mathrm{sys}}=796\ \mathrm{kN/mm}=7.96\times10^8\ \mathrm{N/m}.
$$

Kalantar et al. (2025) reported this value for their MTS 815 loading system and used it when converting piston movement into specimen shortening. Ye and Ghassemi (2018) used an MTS 816 system but did not report its stiffness. The value of 796 kN/mm is therefore not a measurement from the Ye and Ghassemi experiments. It is a provisional common-stiffness assumption used to remove the earlier specimen-dependent penalty values and to test all four specimens under one transparent loading-system model.

The manuscript should describe this choice as a protocol-consistency sensitivity. It should not state that 796 kN/mm is the measured stiffness of the MTS 816.

## Conversion to the four areal penalties

The cross-sectional area is calculated from the model radius,

$$
A=\pi R^2,
$$

and the boundary stiffness is then $k_p=K_{\mathrm{sys}}/A$. The values used in the generated 116-series inputs are:

| Specimen | Radius $R$ (m) | Area $A$ (m$^2$) | $k_p$ (Pa/m) |
|---|---:|---:|---:|
| SW-T1 | 0.025260 | 0.0020045485 | $3.9709691\times10^{11}$ |
| SW-T2 | 0.025260 | 0.0020045485 | $3.9709691\times10^{11}$ |
| SW-S3 | 0.025265 | 0.0020053421 | $3.9693975\times10^{11}$ |
| SW-S4 | 0.025255 | 0.0020037550 | $3.9725416\times10^{11}$ |

The small differences among the areal penalties arise only from the specimen areas. All four correspond to the same total system stiffness.

## Initial actuator command

The inherited models begin with an isotropic compressive stress of 31 MPa. The initial command was set from

$$
u_0=-\frac{31\ \mathrm{MPa}}{k_p}.
$$

This gives approximately $-0.078$ mm for each specimen. It is a numerical initialization consistent with the inherited initial stress, rather than a piston displacement reported by Ye and Ghassemi.

## Transformation of the final preload command

Changing $k_p$ while retaining the earlier actuator command would change the axial preload. To isolate the loading-system correction, the final command was transformed to preserve two quantities from each adopted parent calculation at approximately 55 s:

1. the calculated top-surface displacement, $u_z^{55}$; and
2. the compressive machine-spring stress, $\sigma_{1,\mathrm{spring}}^{55}$.

Using $\sigma_{1,\mathrm{spring}}=k_p(u_z-\bar u_z)$ in compression-magnitude form gives

$$
u_f=u_z^{55}-\frac{\sigma_{1,\mathrm{spring}}^{55}}{k_p}.
$$

The source values and transformed commands are:

| Specimen | $u_z^{55}$ (mm) | $\sigma_{1,\mathrm{spring}}^{55}$ (MPa) | Transformed $u_f$ (mm) |
|---|---:|---:|---:|
| SW-T1 | -0.290774 | 181.593 | -0.748076 |
| SW-T2 | -0.339739 | 202.290 | -0.849161 |
| SW-S3 | -0.057849 | 62.868 | -0.216230 |
| SW-S4 | -0.048992 | 59.288 | -0.198236 |

These final commands were not inferred directly from the experimental piston records. They were calculated to preserve the adopted near-critical numerical preload after introducing the common $K_{\mathrm{sys}}$. Consequently, the short preload gate remains necessary: plastic slip should remain negligible at 55 s, the intended differential stress should be recovered, and the top reaction should agree with the spring-stress calculation.

## Applied history

The corrected command is

$$
\bar u_z(t)=
\begin{cases}
u_0, & 0\le t<2\ \mathrm{s},\\
u_0+(u_f-u_0)(t-2)/53, & 2\le t<55\ \mathrm{s},\\
u_f, & t\ge55\ \mathrm{s}.
\end{cases}
$$

The 2--55 s ramp establishes the required axial preload. The constant value after 55 s represents the reported fixed-piston stage. In the corrected cases, the radial confinement also remains constant at 30 MPa throughout the injection and unloading history.

## Evaluation during a nonlinear time step

The boundary is not applied once at the beginning of the calculation. It is evaluated at every boundary quadrature point during every Newton iteration. At a trial solution within time step $t_{n+1}$, the following sequence occurs:

1. `axial_disp_ramp` evaluates the current remote command $\bar u_z(t_{n+1})$.
2. MOOSE evaluates the current trial displacement $u_z^{(k)}$ on each quadrature point of the top surface.
3. `FunctionPenaltyDirichletBC` adds

$$
R_i^{\Gamma_t,(k)}
=\int_{\Gamma_t}N_i k_p
\left(u_z^{(k)}-\bar u_z(t_{n+1})\right)\,\mathrm d\Gamma
$$

to the residual and

$$
J_{ij}^{\Gamma_t}
=\int_{\Gamma_t}N_i k_pN_j\,\mathrm d\Gamma
$$

to the Jacobian.
4. The global Newton update changes the displacement, pressure, and coupled fracture fields until the internal forces, fracture tractions, pore-pressure forces, external confinement, and boundary-spring force satisfy equilibrium.
5. After convergence, the accepted $u_z$ generally differs from $\bar u_z$. Their difference gives the deformation and force of the loading-system spring.
6. The postprocessors evaluate the accepted solution and write selected results to the CSV output.

The boundary therefore does not first impose a displacement and then calculate a reaction. The displacement and reaction are obtained together as part of the coupled equilibrium solution. Once $\bar u_z$ is held constant, changes in $u_z$ arise from the specimen response. If the specimen accommodates more axial shortening during slip, $u_z$ moves toward the fixed compressive command, the spring gap decreases, and the axial reaction normally falls. Dilation or another mechanism that increases the spring gap can instead increase the reaction.

## Boundary postprocessor chain

The 116-series inputs contain the following loading-boundary diagnostics:

| Postprocessor | Operation | Interpretation |
|---|---|---|
| `axial_command_m_pp` | Evaluates `axial_disp_ramp` | Remote command $\bar u_z(t)$, m |
| `top_disp_z_mean_m_pp` | Side average of `disp_z` on `top_nodeset` | Mean specimen-top displacement $\langle u_z\rangle_{\Gamma_t}$, m |
| `machine_spring_gap_m_pp` | `top_disp_z_mean_m_pp - axial_command_m_pp` | Mean spring deformation $\langle u_z\rangle-\bar u_z$, m |
| `machine_spring_sigma1_mpa_pp` | $k_p|\langle u_z\rangle-\bar u_z|$ | Compressive spring traction magnitude, MPa |
| `top_reaction_z_raw` | Nodal sum of `react_disp_z` on the top | Total axial reaction magnitude before sign processing, N |
| `top_reaction_z_abs` | Absolute value of the raw reaction | Unsigned axial force, N |
| `top_boundary_area_pp` | Area integral on the meshed top | Finite-element top-surface area, m$^2$ |
| `sigma1_reaction_mpa_pp` | `top_reaction_z_abs / sample_area` | Axial reaction stress using the nominal input area, MPa |
| `differential_stress_reaction_mpa_pp` | $\sigma_1^{R}-30$ MPa | Reaction-based differential stress $q=\sigma_1-\sigma_3$, MPa |
| `reaction_vs_machine_spring_mpa_pp` | $\sigma_1^{R}-\sigma_1^{\mathrm{spring}}$ | Signed consistency diagnostic, MPa |

The reaction route deserves clarification. `react_disp_z` is filled by a `TagVectorAux` that reads the `mech_reaction` residual tag with variable scaling removed. The mechanical volume and interface kernels contribute to this tag. Summing it on the top boundary gives the internal nodal force required to balance the penalty-boundary traction. This makes the reaction calculation independent of simply reusing the spring formula and provides a useful equilibrium check.

For constant $k_p$ and a spatially uniform command, integration of the spring traction gives

$$
F_z^{\mathrm{spring}}
=k_p\int_{\Gamma_t}\left(\bar u_z-u_z\right)\,\mathrm d\Gamma
=A_{\mathrm{FE}}k_p
\left(\bar u_z-\langle u_z\rangle_{\Gamma_t}\right),
$$

where $A_{\mathrm{FE}}$ is the meshed top area. Exact global equilibrium therefore implies

$$
\frac{|F_z^{R}|}{A_{\mathrm{FE}}}
\approx k_p\left|\bar u_z-\langle u_z\rangle_{\Gamma_t}\right|.
$$

The current `sigma1_reaction_mpa_pp` divides the force by the nominal area $A=\pi R^2$, whereas the spring traction is an average over $A_{\mathrm{FE}}$. Consequently,

$$
\sigma_1^{R,A}
=\frac{|F_z^R|}{A}
\approx\frac{A_{\mathrm{FE}}}{A}
\sigma_1^{\mathrm{spring}}.
$$

In the available 116-series outputs, $A_{\mathrm{FE}}/A\approx0.997147$. The existing `reaction_vs_machine_spring_mpa_pp` therefore has a systematic relative difference of approximately $-0.2853\%$. This is an area-normalization effect, not a failure of equilibrium. An area-consistent validation should calculate

$$
\sigma_1^{R,\mathrm{FE}}
=\frac{|F_z^R|}{A_{\mathrm{FE}}}
$$

and compare it with $\sigma_1^{\mathrm{spring}}$. Both quantities needed for this correction are already present in the CSV files, so no rerun is required.

The row written at $t=0$ in the present CSV files contains zeros for the boundary postprocessors even though the command function is defined as $u_0$. These postprocessors are evaluated after accepted time steps and were not explicitly requested on `INITIAL`. The zero row must therefore not be interpreted as the applied initial boundary condition. If a nonzero initial diagnostic row is required in future runs, the relevant postprocessors should use `execute_on = 'INITIAL TIMESTEP_END'` and the initialization sequence should then be checked.

## Which validation quantities follow from the boundary

The boundary diagnostics directly establish four facts: the command that was requested, the specimen-top displacement that was obtained, the resulting spring deformation, and the axial reaction that equilibrates the specimen. They provide the reaction-based axial stress and differential stress. They do not directly provide fracture slip, dilation, aperture, permeability, or flow rate.

For a fracture plane at angle $\theta$ to the specimen axis, the reaction-based differential stress $q$ is transformed to the paper coordinate system as

$$
\sigma_n'
=\sigma_3+q\sin^2\theta-p_f,
\qquad
\tau=q\sin\theta\cos\theta,
$$

where $p_f$ is represented in the validation inputs by the mean of inlet and outlet pressure. These transformations are written by `effective_normal_paper_frame_mpa_pp` and `shear_stress_paper_frame_mpa_pp`. Therefore, two of the five Table 2 scoring channels---effective normal stress and shear stress---depend directly on the boundary reaction. The other three channels are obtained elsewhere:

- shear displacement from `reported_czm_shear_slip_mm_pp`;
- normal displacement from `czm_normal_dilation_paper_mm_pp`; and
- flow rate from `flow_rate_validation_ml_min_pp`.

Hydraulic aperture and permeability are useful derived diagnostics, but they are not scored again because the experimental values were themselves inferred from flow.

## Limitations and recommended interpretation

The boundary reproduces the principal control mode of the experiment: finite-stiffness axial loading followed by a fixed piston command during pressure cycling. It does not reproduce every component of the apparatus. In particular, the MTS 816 stiffness is unknown, and platen friction, jacket compliance, seals, controller dynamics, and local nonuniformities are idealized.

The selected stiffness should therefore be treated as an explicit modelling assumption. If the predicted slip or stress drop changes strongly when $K_{\mathrm{sys}}$ is varied over a defensible range, machine stiffness is an uncertainty that must be reported. Constitutive parameters should not be adjusted until the response under the common boundary has first been evaluated without refitting.

The reference point of the experimental displacement measurement is also important. The spring formulation is appropriate if $\bar u_z$ represents a command or displacement measured on the machine side of the compliant load train. If the reported displacement instead represents the motion of the platen directly at the specimen top, assigning that motion to $\bar u_z$ and adding a separate machine spring would count part of the apparatus compliance twice. Ye and Ghassemi reported a fixed piston during injection but did not report the MTS 816 stiffness or a complete compliance correction. This is another reason to present the finite-stiffness boundary as a sensitivity assumption rather than as a uniquely reconstructed experimental condition.

## Clarification: stiffness, fixed piston, and the LVDT

In mechanics, a stiff component develops a large force for a small deformation. Finite stiffness does not mean that a displacement value must be satisfied exactly. For the axial spring,

$$
F_z=K_{\mathrm{sys}}(\bar u_z-u_z).
$$

A larger $K_{\mathrm{sys}}$ produces a larger restoring force for the same difference between the actuator command and specimen displacement. Only the limiting case $K_{\mathrm{sys}}\rightarrow\infty$ approaches an exact displacement constraint, $u_z=\bar u_z$. A finite penalty deliberately permits a nonzero difference.

The corrected simulations hold the actuator command $\bar u_z$ constant after 55 s; they do not hold the axial load constant. If the specimen shortens, dilates, slips, or closes, $u_z$ changes relative to the fixed command. The spring deformation and axial force then change. This is how stress relaxation can occur under a fixed piston command.

The other boundaries are not mechanically free. The bottom is fixed axially, and minimal lateral pins remove rigid-body motion. The curved surface is subjected to a constant 30 MPa inward traction rather than a prescribed radial displacement. It can therefore move radially while remaining pressure-loaded. The specimen may contract or expand until its internal stresses, fracture tractions, pore pressure, and the applied boundary tractions are in equilibrium.

The finite-stiffness formulation is chosen because of the physical compliance and control mode of the testing machine, not because of the LVDT. An LVDT is a displacement sensor; it measures motion but does not impose the mechanical boundary condition. LVDT or piston-displacement measurements are used to compare calculated and measured deformation and, where necessary, to remove loading-frame deformation from the recorded actuator movement. The machine-stiffness correction and the LVDT measurement are therefore related through data interpretation, but they have different roles: machine compliance motivates the spring boundary, whereas the LVDT supplies an observed displacement.

## Assessment of the current appendix text

The current text contains the correct residual, traction, and stiffness conversion, but it needs several changes before submission:

1. `FunctionPenaltyDirichletBC` does not impose an exact Dirichlet condition for finite $k_p$. It adds a weak penalty term that is mathematically equivalent to a Robin spring boundary.
2. The MOOSE input `penalty` must be large, not small, to approximate $u_z=\bar u_z$. A small parameter in the theoretical discussion is the compliance $\varepsilon=1/k_p$.
3. In the present model, $k_p$ is deliberately finite and is not large relative to $E/L$. Therefore, $u_z\approx\bar u_z$ should not be claimed for the 116-series simulations.
4. Juntunen and Stenberg (2009) can support the distinction among penalty, Robin, and Nitsche formulations, but the implementation is a penalty method, not Nitsche's method. The MOOSE framework references should also accompany the class name.
5. The appendix must state that $K_{\mathrm{sys}}=796$ kN/mm is borrowed from Kalantar et al. (2025) as a sensitivity assumption. It was not measured for the MTS 816 system used by Ye and Ghassemi (2018).
6. In the LaTeX manuscript, use `\texttt{FunctionPenaltyDirichletBC}` instead of Markdown backticks and use `equation` or `align` environments instead of `$$` delimiters.

## Recommended replacement appendix

```latex
\appendix
\section{Finite-stiffness axial boundary}
\label{app:boundary-stiffness}

Axial loading was applied on the specimen top using the MOOSE
\texttt{FunctionPenaltyDirichletBC} object
\cite{Gaston_etal_2009,harbour2025moose}. This object is commonly used to
enforce a prescribed displacement weakly. However, the coefficient used here
was assigned a finite physical value so that the boundary represents the
compliance of the loading system rather than an exact displacement constraint.

Let $\bar u_z(t)$ be the remote actuator command, $u_z$ the calculated axial
displacement of the specimen top, and $\Gamma_t$ the top surface. An exact
Dirichlet boundary would require $u_z=\bar u_z$ on $\Gamma_t$. In the penalty
formulation, a quadratic boundary energy is added to the mechanical potential:

\begin{equation}
\Pi_{\mathrm{tot}}(\boldsymbol{u})
=\Pi_{\Omega}(\boldsymbol{u})
+\frac{1}{2}\int_{\Gamma_t}k_p
\left(u_z-\bar u_z\right)^2\,\mathrm{d}\Gamma,
\label{eq:penalty-potential}
\end{equation}

where $k_p$ is the areal boundary stiffness. Taking the first variation and
using $u_z=\sum_jN_jU_j$ gives the boundary contributions to the residual and
Jacobian:

\begin{align}
R_i^{\Gamma_t}
&=\int_{\Gamma_t}N_i k_p
\left(u_z-\bar u_z\right)\,\mathrm{d}\Gamma,
\label{eq:penalty-residual}\\
J_{ij}^{\Gamma_t}
&=\int_{\Gamma_t}N_i k_pN_j\,\mathrm{d}\Gamma.
\label{eq:penalty-jacobian}
\end{align}

The corresponding axial traction is

\begin{equation}
t_z=k_p\left(\bar u_z-u_z\right).
\label{eq:penalty-traction}
\end{equation}

Therefore, a finite penalty does not impose $u_z=\bar u_z$ exactly. The
displacement difference is

\begin{equation}
\left|u_z-\bar u_z\right|=\frac{|t_z|}{k_p}.
\label{eq:penalty-gap}
\end{equation}

When a penalty method is used only as a numerical approximation to a Dirichlet
condition, $k_p$ must be sufficiently large for this difference to be small,
but not so large that the Jacobian becomes ill-conditioned
\cite{juntunen2009nitsche}. This is not the limiting case adopted here. The
finite displacement difference in Equation~\ref{eq:penalty-gap} represents
deformation of the loading system.

The boundary is equivalent to a distributed set of axial springs. If the top
displacement is nearly uniform, the resultant force is

\begin{equation}
F_z=A k_p\left(\bar u_z-u_z\right).
\label{eq:penalty-force}
\end{equation}

Equivalence with a loading system having total stiffness $K_{\mathrm{sys}}$
then requires

\begin{equation}
k_p=\frac{K_{\mathrm{sys}}}{A}.
\label{eq:penalty-conversion}
\end{equation}

The protocol-consistency simulations used
$K_{\mathrm{sys}}=796~\mathrm{kN\,mm^{-1}}$, giving
$k_p\simeq3.97\times10^{11}~\mathrm{Pa\,m^{-1}}$ for the four specimens. This
system stiffness was reported for the MTS 815 apparatus used by
\citeA{Kalantar_etal_2025}. It was not reported for the MTS 816 apparatus used
by \citeA{Ye_Ghassemi_2018}; it is therefore treated here as a common-stiffness
sensitivity rather than a measured property of the original tests.

The physical distinction from an exact displacement boundary can be shown by
considering a one-dimensional specimen with stiffness
$K_s=E_{\mathrm{eff}}A/L$ and a boundary spring with stiffness $K_p=Ak_p$.
Force equilibrium gives

\begin{equation}
\frac{u_z}{\bar u_z}=\frac{K_p}{K_s+K_p},
\qquad
K_{\mathrm{eq}}=
\left(\frac{1}{K_s}+\frac{1}{K_p}\right)^{-1}.
\label{eq:series-stiffness}
\end{equation}

For the present specimens, $k_p/(E/L)$ is approximately 0.70--0.79. Hence,
$k_p$ is comparable to the intact-specimen areal stiffness and the boundary is
not in the nearly exact Dirichlet limit. The specimen and loading system share
the imposed displacement, as expected for two stiffnesses acting in series.

For each specimen, the actuator command followed

\begin{equation}
\bar u_z(t)=
\begin{cases}
u_0, & 0\leq t<2~\mathrm{s},\\
u_0+(u_f-u_0)(t-2)/53, & 2\leq t<55~\mathrm{s},\\
u_f, & t\geq55~\mathrm{s}.
\end{cases}
\label{eq:axial-command-history}
\end{equation}

The initial command $u_0=-31~\mathrm{MPa}/k_p$ balanced the inherited
isotropic initial stress. The command was then ramped to the specimen-specific
preload and held constant during fluid-pressure cycling. The values of $u_f$
were $-0.748076$, $-0.849161$, $-0.216230$, and $-0.198236$~mm for SW-T1,
SW-T2, SW-S3, and SW-S4, respectively. Radial confinement was maintained at
30~MPa.

At each Newton iteration, the command in
Equation~\ref{eq:axial-command-history} and the current trial displacement were
used to assemble Equations~\ref{eq:penalty-residual} and
\ref{eq:penalty-jacobian}. The displacement and reaction were therefore solved
together with the coupled pressure and fracture fields. Although $\bar u_z$
remained constant after 55~s, $u_z$ could change in response to elastic
deformation, fracture slip, dilation, closure, and poroelastic deformation.
The spring gap and axial reaction consequently evolved during injection,
allowing stress relaxation under a fixed remote actuator command.

The boundary diagnostics recorded the command, mean top displacement, spring
gap, spring traction, and summed top reaction. The reaction-based axial stress
was calculated as $\sigma_1^R=|F_z^R|/A$, and the differential stress was
$q=\sigma_1^R-\sigma_3$. The stresses acting on a fracture inclined by
$\theta$ to the specimen axis were then evaluated as

\begin{equation}
\sigma_n'=\sigma_3+q\sin^2\theta-p_f,
\qquad
\tau=q\sin\theta\cos\theta,
\label{eq:paper-frame-stress}
\end{equation}

where $p_f$ was represented by the mean inlet and outlet pressure. Hence, the
effective normal stress and shear stress used in the Table~2 comparison were
obtained from the axial-boundary reaction. Shear displacement, normal
displacement, and flow rate were obtained from separate fracture and flow
postprocessors.

As an implementation check, the spring traction was compared with the summed
reaction divided by the meshed top area. The nominal circular area is about
0.285\% larger than the meshed top area in these models; using the nominal area
on only the reaction side therefore produces an expected difference of about
$-0.285\%$ and should not be interpreted as a force-balance error.
```

## Sources checked

- [MOOSE `PenaltyDirichletBC` documentation](https://mooseframework.inl.gov/source/bcs/PenaltyDirichletBC.html)
- [MOOSE `FunctionPenaltyDirichletBC` implementation](https://mooseframework.inl.gov/docs/doxygen/moose/FunctionPenaltyDirichletBC_8C_source.html)
- Juntunen, M., and R. Stenberg (2009), *Nitsche's method for general boundary conditions*, Mathematics of Computation, 78(267), 1353--1374.
