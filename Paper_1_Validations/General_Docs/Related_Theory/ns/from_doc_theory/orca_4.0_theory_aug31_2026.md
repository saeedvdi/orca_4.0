# Orca 4.0 coupled rough-fracture contact, aperture, and flow theory

**Implementation documented:** `OrcaBartonBandisContactTractionFastADHardening` and its coupled cohesive-zone, aperture, pressure, mechanics, and fracture-flow components

**Source basis:** Orca 4.0 source tree and the `SWS4_OrcaBartonBandisContactTractionFastADHardening.i` production example
**Document date:** 2026-08-31

## 1. Purpose and scope

This document is a theory-to-code specification for the Orca 4.0 small-strain hydro-mechanical interface formulation built around:

- `OrcaBartonBandisContactTractionFastADHardening`
- `ADOrcaCZMComputeMechanicalAperture`
- `ADOrcaRoughnessDamageFracturePermeability`
- `OrcaComputeGlobalTractionSmallStrain`
- `OrcaCZMInterfacePressure`
- `OrcaCZMComputeDisplacementJump`
- `OrcaMechInterfaceKernel`
- `OrcaCZMFluidPressureInterfaceKernel`
- `OrcaFractureFlowInterfaceKernel`

The presentation follows the executed implementation, including sign conventions, branch logic, state, regularization, return mapping, automatic-differentiation reconstruction, and current limitations. Where an object description or older theory note differs from the source, the source behavior is stated explicitly and the difference is recorded in Section 16.

The constitutive model is a compression-contact and frictional-slip law. It has no cohesive tensile normal branch: when contact is open, its mechanical traction is zero. The parameter named `cohesion` is the shear-strength intercept, not tensile cohesion.

## 2. Dependency and data-flow map

~~~mermaid
flowchart TD
  UE[Element displacement] --> J[OrcaCZMComputeDisplacementJump]
  UN[Neighbor displacement] --> J
  N[Reference interface normal] --> J
  J -->|local jump and increment| C[OrcaBartonBandisContactTractionFastADHardening]
  PE[Element pressure] --> P[OrcaCZMInterfacePressure]
  PN[Neighbor pressure] --> P
  P -->|mean interface pressure| C
  C -->|local mechanical traction| G[OrcaComputeGlobalTractionSmallStrain]
  J -->|reference rotation| G
  G -->|global mechanical traction| KM[OrcaMechInterfaceKernel]
  P --> KP[OrcaCZMFluidPressureInterfaceKernel]
  J --> KP
  KM --> BULK[Bulk displacement equations]
  KP -->|pressure traction| BULK
  J --> A[ADOrcaCZMComputeMechanicalAperture]
  A -->|mechanical aperture| H[ADOrcaRoughnessDamageFracturePermeability]
  C -->|dilation roughness slip normal traction| H
  H -->|hydraulic aperture and transmissivity| KF[OrcaFractureFlowInterfaceKernel]
  PE --> KF
  PN --> KF
  KF -->|storage tangential flow pressure transfer| FLOW[Pressure equations]
~~~

Two architectural facts are essential:

1. `OrcaComputeGlobalTractionSmallStrain` does **not** calculate a traction from a bulk stress tensor. It rotates the already-computed local interface traction into global coordinates.
2. Mechanical contact traction and pore-pressure traction are assembled by separate interface kernels. The latter is not embedded automatically in the former.

## 3. Notation, units, and conventions

| Symbol | Meaning | Units / convention |
|---|---|---|
| $\mathbf u^-$, $\mathbf u^+$ | element- and neighbor-side displacement | m |
| $\llbracket\mathbf u\rrbracket$ | global jump, $\mathbf u^+-\mathbf u^-$ | m |
| $\mathbf n$ | reference unit normal, element to neighbor | dimensionless |
| $\mathbf R$ | local-to-global orthogonal rotation | dimensionless |
| $\mathbf g=\mathbf R^T\llbracket\mathbf u\rrbracket$ | local displacement jump | m |
| $g_n=g_0$ | normal jump; positive is opening | m |
| $\mathbf g_t$ | local tangential jump | m |
| $\mathbf t=(t_n,\mathbf t_t)$ | local interface traction | Pa |
| $\mathbf t^G=\mathbf R\mathbf t$ | global interface traction | Pa |
| $c$ | nonnegative compressive closure | m |
| $\sigma_c$ | nonnegative compressive contact magnitude | Pa |
| $t_n=-\sigma_c$ | tension-positive local normal traction | Pa |
| $\bar p$ | arithmetic mean interface pressure | Pa |
| $s$ | accumulated plastic tangential slip | m |
| $\gamma$ | plastic-slip increment | m |
| $d$ | irreversible accumulated dilation | m |
| $R_r$ | retained roughness state | dimensionless |
| $a_m$, $a_h$ | mechanical and hydraulic aperture | m |
| $T=a_h^3/(12\mu)$ | cubic-law transmissivity | m$^3$ Pa$^{-1}$ s$^{-1}$ |

Compression is represented by $t_n<0$, while $\sigma_c=-t_n\ge0$. A positive normal displacement jump opens the interface. Components 0, 1, and 2 are the normal and two local tangential components. Property names may be prefixed with `base_name`; the prefix is omitted below.

## 4. Surrounding small-strain poromechanics

### 4.1 Bulk kinematics and effective stress

`OrcaMechMaterial` uses

$$
\boldsymbol\varepsilon=\tfrac12(\nabla\mathbf u+\nabla\mathbf u^T),
$$

and, after subtracting configured eigenstrains including optional thermal strain,

$$
\boldsymbol\varepsilon_m=\boldsymbol\varepsilon-\sum_k\boldsymbol\varepsilon_k^*.
$$

For the total small-strain form,

$$
\boldsymbol\sigma'=\mathbb C:\boldsymbol\varepsilon_m+\boldsymbol\sigma_0.
$$

The material also supports incremental strain, volumetric-locking correction, and global-strain contributions. Those options affect the surrounding continuum, not the local interface equations.

### 4.2 Bulk pressure coupling

`OrcaPoroMechKernel` represents

$$
\boldsymbol\sigma^{\mathrm{tot}}=\boldsymbol\sigma'-\alpha p\mathbf I
$$

through the displacement residual

$$
R_i^{\mathrm{bulk}}=\int_\Omega \boldsymbol\sigma'_{i\bullet}\cdot\nabla N_i\,d\Omega
-\int_\Omega\alpha p\,\partial_iN_i\,d\Omega.
$$

This bulk stress is not passed to the interface contact material. Bulk-to-interface equilibrium arises from assembled interface tractions and neighboring displacements, not from an explicit $\boldsymbol\sigma\mathbf n$ calculation inside `OrcaComputeGlobalTractionSmallStrain`.

## 5. Interface kinematics and pressure

### 5.1 `OrcaCZMComputeDisplacementJump`

The global jump and reference-frame transformation are

$$
\llbracket\mathbf u\rrbracket=\mathbf u^+-\mathbf u^-,
\qquad
\mathbf g=\mathbf R^T\llbracket\mathbf u\rrbracket,
$$

with

$$
\mathbf R\mathbf e_0=\mathbf n,
\qquad
\mathbf R^T\mathbf R=\mathbf I.
$$

The material supplies the current local jump and the local jump increment required by the incremental cohesive-zone base. In 3-D the utility constructs the minimal rotation taking the global x axis to $\mathbf n$; the 2-D construction is the consistent in-plane rotation; 1-D uses the identity. This is a reference-normal, small-strain construction, not a finite-deformation current-normal update.

### 5.2 Incremental traction framework

`OrcaCZMComputeLocalTractionIncrementalBase` provides old jump and traction state. A derived material returns an increment so that

$$
\mathbf t_{n+1}=\mathbf t_n+\Delta\mathbf t.
$$

The Barton--Bandis implementation reconstructs its current total traction from the converged current contact and slip state, then supplies the corresponding increment.

### 5.3 `OrcaCZMInterfacePressure`

The interface pressure is the arithmetic trace average

$$
\bar p=\tfrac12(p^-+p^+).
$$

The property is initialized to zero. There is no upwinding, aperture weighting, Biot coefficient, or effective-stress transformation in this object.

## 6. Barton--Bandis contact and friction law

### 6.1 Constitutive summary and state

The local law is

$$
\mathbf t=\begin{cases}
\mathbf0, & \text{open},\\
(-\sigma_c,\mathbf t_t), & \text{closed}.
\end{cases}
$$

The state includes tangential plastic jump $\mathbf g_t^p$, accumulated plastic slip $s$, accumulated irreversible dilation $d$, retained minimum raw closure, recoverable closure amplitude, and diagnostic/reporting history. Old state is used at the beginning of each time step; only a converged solution is committed.

The registered hardening object extends the fast-AD Barton--Bandis base. Despite the suffix `Hardening`, its principal added strength evolution is an exponential transition from peak to residual strength. With JRC mobilization enabled at the same time, the combined response can first harden and later soften.

### 6.2 Raw gap and dilation sign mode

Let $d_n$ be the old irreversible dilation offset; it is taken as zero when `accumulate_irreversible_dilation=false`. The effective gap and raw closure are

$$
g_{\mathrm{eff}}=g_n+s_gd_n-c_0,
\qquad
c_{\mathrm{raw}}=-g_{\mathrm{eff}},
$$

where $c_0$ is `normal_closure_offset` and

$$
s_g=\begin{cases}
1,&\text{legacy mode: `dilation_opens_joint=false`},\\
-1,&\text{kinematic mode: `dilation_opens_joint=true`}.
\end{cases}
$$

In legacy mode a dilation increment directly reduces closure at fixed displacement. In kinematic mode dilation is a rest-opening offset: at fixed total jump it raises elastic closure, and global equilibrium must open the faces to realize dilation.

### 6.3 Normal unloading, retention, and reclosure

Once its slip threshold is reached, the optional unloading transformation is

$$
c_*=c_{\mathrm{raw}}+(m_r-1)\langle c_{\mathrm{raw}}-c_{\min}\rangle_+-a_r,
$$

where $m_r$ is `normal_reclosure_stiffness_multiplier`, $c_{\min}$ is retained minimum raw closure, and $a_r$ is recoverable closure. The recovered amount and target are

$$
c_{\mathrm{rec}}=\max(0,c_{\mathrm{raw}}-c_{\min}),
\qquad
a_{r,\mathrm{tar}}=\min(c_{\mathrm{raw}},\zeta c_{\mathrm{rec}}),
$$

where $\zeta=$ `normal_unload_retention_fraction`. If `normal_unload_retention_time` is positive,

$$
a_{r,n+1}=a_{r,n}+[1-\exp(-\Delta t/\tau_r)](a_{r,\mathrm{tar}}-a_{r,n});
$$

otherwise the target is applied immediately.

### 6.4 Gap regularization

For `contact_gap_regularization=0`, $c_*\le0$ is a hard-open branch and traction is exactly zero. For positive $\epsilon_g$, the code uses a numerically stable form of

$$
\langle x\rangle_{\epsilon_g}=\tfrac12(x+\sqrt{x^2+\epsilon_g^2}),
$$

with rationalized evaluation on the negative side. The regularized law therefore has a small compressive tail in nominal opening.

### 6.5 Normal closure law

Active closure is capped to $0\le c\le f_{\max}V_m$. When `use_hyperbolic_normal_closure=false`,

$$
\sigma_c=K_{ni}c,
\qquad
\frac{d\sigma_c}{dc}=K_{ni}.
$$

Thus `initial_normal_stiffness` is the physical linear stiffness and the fallback tangential penalty; there is no independent normal-penalty parameter.

With hyperbolic closure enabled,

$$
\sigma_c=K_{ni}V_m\left(\frac{c}{V_m-c}\right)^{1/p_n},
$$

where $p_n=$ `normal_closure_stress_exponent`. Its inverse is

$$
c=V_m\frac{q}{1+q},
\qquad
q=\left(\frac{\sigma_c}{K_{ni}V_m}\right)^{p_n}.
$$

Below $c_{\mathrm{lin}}=\min(10^{-9}\,\mathrm m,0.01V_m)$ the implementation uses a secant linearization, preventing a singular or ill-conditioned derivative near zero when $p_n>1$. At the closure cap it returns zero tangent. The signed normal traction is

$$
t_n=-\sigma_c.
$$

`normal_traction_tolerance` is used only in the post-dilation open test; it is not a general complementarity tolerance.

### 6.6 Effective compression for shear strength

The compression used in shear strength is

$$
\sigma_s=\begin{cases}
\max(0,\sigma_c-\beta_p\bar p),&\beta_p>0,\\
\sigma_c,&\beta_p\le0,
\end{cases}
$$

where $\beta_p=$ `pore_pressure_strength_coefficient`. This can reduce shear strength, but never changes the mechanical normal traction $-\sigma_c$. If a separate pressure interface kernel is also used, nonzero $\beta_p$ adds another pressure effect. The production SWS4 input deliberately sets $\beta_p=0$ while using the separate pressure kernel.

### 6.7 Scale-corrected Barton--Bandis peak strength

When scale correction is enabled,

$$
\mathrm{JRC}_n=\mathrm{JRC}_0\left(\frac{L_n}{L_0}\right)^{-0.02\mathrm{JRC}_0},
$$

$$
\mathrm{JCS}_n=\mathrm{JCS}_0\left(\frac{L_n}{L_0}\right)^{-0.03\mathrm{JRC}_0}.
$$

Otherwise input JRC and JCS are used. For the logarithm,

$$
\sigma_{\log}=\max(\sigma_{\mathrm{floor}},\sigma_s),
$$

and the JCS/stress ratio receives an additional numerical floor of $10^{-30}$. With mobilization enabled,

$$
\mathrm{JRC}_{\mathrm{mob}}=\mathrm{JRC}_n
\left[\operatorname{clamp}(s/\delta_p,0,1)\right]^{m_J};
$$

otherwise it equals $\mathrm{JRC}_n$. The roughness and peak angles are

$$
i=\mathrm{JRC}_{\mathrm{mob}}\log_{10}\left(\frac{\mathrm{JCS}_n}{\sigma_{\log}}\right),
$$

$$
\phi_{\mathrm{BB}}=\operatorname{clamp}(\phi_r+i,\phi_{\min},\phi_{\max}),
\qquad
\mu_{\mathrm{BB}}=\tan\phi_{\mathrm{BB}}.
$$

Unless `allow_negative_roughness_angle=true`, $i$ is clipped below at zero. Input angles are degrees and converted internally before trigonometric evaluation.

### 6.8 Slip weakening in the hardening subclass

With `use_slip_weakening=true`,

$$
W(s)=\exp[-(s/D_c)^{m_w}].
$$

The residual angle is `slip_weakening_residual_friction_angle_degrees` when nonnegative; otherwise the code falls back to `residual_friction_angle_degrees`. Defining $\mu_r=\tan\phi_{r,\mathrm{tail}}$,

$$
\mu_{\mathrm{eff}}=\mu_r+(\mu_{\mathrm{BB}}-\mu_r)W,
$$

$$
c_{\mathrm{eff}}=c_{\mathrm{res}}+(c_0^\tau-c_{\mathrm{res}})W,
$$

and

$$
Y=c_{\mathrm{eff}}+\sigma_s\mu_{\mathrm{eff}}.
$$

Here $c_0^\tau$ is the input shear cohesion, not the normal closure offset. If weakening is disabled, $Y=c_0^\tau+\sigma_s\mu_{\mathrm{BB}}$. In either case, a positive `min_tau_limit` is imposed as a floor.

JRC mobilization and slip weakening are evaluated together. Increasing mobilized JRC can cause early hardening while $W(s)$ later drives friction and cohesion toward their residual values.

### 6.9 Roughness degradation exported to hydraulics

The subclass can export

$$
R_r(s)=R_{\mathrm{res}}+(R_{\mathrm{ini}}-R_{\mathrm{res}})\exp(-s/D_r),
\qquad
D_r^{\mathrm{rough}}=1-R_r.
$$

If degradation is disabled, the base reports one for positive scaled JRC and zero otherwise. This state is mechanically decoupled: it does not reduce JRC, roughness angle, dilation angle, or strength in this contact class. It is intended for downstream permeability/aperture evolution.

### 6.10 Dilation

The legacy dilation angle is

$$
\psi=\operatorname{clamp}(f_di,\psi_{\min},\psi_{\max}),
$$

where $f_d=$ `dilation_factor`. With the decoupled law,

$$
\psi(s)=\operatorname{clamp}\left[
\psi_{\mathrm{res}}+(\psi_{\mathrm{peak}}-\psi_{\mathrm{res}})\exp(-s/D_d),
\psi_{\min},\psi_{\max}\right].
$$

There is no independent decay exponent. When dilatancy is active,

$$
\mu_d=\tan\psi,
\qquad
\Delta d_{\mathrm{trial}}=\mu_d\gamma;
$$

otherwise both are zero. The nonnegative increment may be limited by `max_dilation_increment` and, when requested, closure available at the start of the step. The production input disables the available-closure cap in kinematic mode.

With accumulation enabled, $d_{n+1}=d_n+\Delta d$; otherwise the stored irreversible state is zero. At each trial $\gamma$, the contact/dilation feedback is resolved by a fixed point, with at most 50 internal iterations:

$$
c=\langle c_{\mathrm{start}}+s_c\Delta d\rangle,
\qquad
s_c=\begin{cases}-1,&\text{legacy mode},\\+1,&\text{kinematic mode}.\end{cases}
$$

No energetic dissipation limiter is applied to dilation in this Barton--Bandis class.

### 6.11 Tangential predictor

The tangential penalty is the positive `penalty_tangent`, or $K_{ni}$ when that parameter is zero. With stress dependence enabled it becomes

$$
K_t=K_{t0}\max\left[f_{Kt},(\sigma_{s,n}/\sigma_{Kt})^{m_{Kt}}\right].
$$

It is evaluated with start-of-step effective compression and held constant inside the return map. The trial state is

$$
\mathbf t_t^{\mathrm{tr}}=K_t(\mathbf g_t-\mathbf g_{t,n}^p),
\qquad
\tau_{\mathrm{tr}}=\|\mathbf t_t^{\mathrm{tr}}\|,
\qquad
\mathbf m=\mathbf t_t^{\mathrm{tr}}/\tau_{\mathrm{tr}}.
$$

The direction is used only when the norm exceeds `tangential_traction_tolerance`.

### 6.12 Open, stick, and slip branches

Hard-open contact, or a post-dilation contact magnitude not exceeding `normal_traction_tolerance`, gives $\mathbf t=\mathbf0$ and state code 2. A closed point sticks if the trial norm is below the tangential tolerance or start-of-step strength; then $\mathbf t_t=\mathbf t_t^{\mathrm{tr}}$ and the state code is 0. Otherwise it slips and the code is 1.

### 6.13 Scalar return map

Slip is governed by

$$
\mathcal R(\gamma)=\tau_{\mathrm{tr}}
-\left(K_t+\frac{\eta}{\Delta t}\right)\gamma
-Y(\gamma)-Y_{\mathrm{extra}}=0.
$$

Here $\eta=$ `tangential_viscosity`, and the extra-strength hook is zero in this subclass. The bracket is

$$
0\le\gamma\le\frac{\tau_{\mathrm{tr}}}{K_t+\eta/\Delta t},
$$

and may be narrowed by `max_plastic_slip_increment`. Every residual evaluation updates slip-dependent strength, dilation, closure, and compression. A safeguarded Newton method with bisection fallback uses `max_return_mapping_iterations` and `relative_tolerance`.

A required root beyond the user cap, or failure to converge, throws a recoverable material exception for global time-step reduction; the class has no local substepping. After convergence,

$$
\mathbf g_{t,n+1}^p=\mathbf g_{t,n}^p+\gamma\mathbf m,
\qquad
s_{n+1}=s_n+\gamma,
$$

$$
\mathbf t_t=(\tau_{\mathrm{tr}}-K_t\gamma)\mathbf m,
\qquad
t_n=-\sigma_c.
$$

### 6.14 AD reconstruction and tangent approximations

The scalar root is solved using raw real numbers. Its automatic derivatives are reconstructed by the implicit-function theorem:

$$
\gamma_{AD}=\gamma-\frac{\mathcal R_{AD}}{d\mathcal R/d\gamma}.
$$

This avoids differentiating through the iterative root solver. The Jacobian is nevertheless approximate in two documented ways: stress-dependent $K_t$ is lagged at the old effective compression, and the return derivative omits the derivative of decoupled $\psi(s)$ in dilation/contact feedback. Values and the scalar root follow the implemented nonlinear law; those dependencies are not fully represented in its tangent.

### 6.15 Reported normal opening

A separate diagnostic opening is formed from

$$
a_{\mathrm{rev,raw}}=S_a(g_n-d),
$$

where $S_a=$ `reported_reversible_normal_opening_scale`. After activation, `reported_reversible_normal_opening_retention_fraction` retains a fraction of the maximum historical reversible opening. The optional elastic recovery is

$$
a_e=A_s(s)C_n\max(0,\sigma_{e,\mathrm{ref}}-\sigma_c),
$$

with

$$
A_s(s)=\begin{cases}
1-\exp[-((s-s_a)/D_a)^{n_a}],&s>s_a,\\
0,&s\le s_a,
\end{cases}
$$

when a positive activation slip is configured; otherwise $A_s=1$. The reported total combines irreversible, retained reversible, and elastic terms. It is output-only and does not affect contact traction, mechanical aperture, or hydraulic aperture.

### 6.16 Initialization

Local traction, plastic jump, plastic increment, accumulated slip, dilation increment, irreversible dilation, unloading states, and opening-history states initialize to zero. Diagnostic friction/dilation values initialize from parameters. The pressure-area coefficient initializes to one. With subclass roughness degradation active, roughness starts from `roughness_state_initial`; otherwise the base constant state applies.

## 7. Global traction rotation and mechanical assembly

### 7.1 `OrcaComputeGlobalTractionSmallStrain`

This material performs only

$$
\mathbf t^G=\mathbf R\mathbf t.
$$

It neither reads a bulk stress nor evaluates $\boldsymbol\sigma\mathbf n$. The name “SmallStrain” refers to its use of the reference interface rotation.

### 7.2 `OrcaMechInterfaceKernel`

For displacement component $i$, its quadrature-point residuals are

$$
R_i^-=-N^-t_i^G,
\qquad
R_i^+=+N^+t_i^G.
$$

The signs impose equal and opposite interface forces. Automatic differentiation propagates material-property derivatives into the coupled displacement Jacobian. The kernel supplies no constitutive physics of its own.

### 7.3 `OrcaCZMFluidPressureInterfaceKernel`

The local pressure traction is

$$
\mathbf t_p^{L}=(c_p\bar p,0,0)^T,
$$

with default `pressure_traction_coefficient=-1`. It is rotated and assembled using

$$
\mathbf t_p^G=\mathbf R\mathbf t_p^L,
\qquad
R_{p,i}^-=-N^-t_{p,i}^G,
\qquad
R_{p,i}^+=+N^+t_{p,i}^G.
$$

The constant coefficient supplies the intended pressure-opening/effective-traction correction under the interface residual convention. This kernel is independent of both the contact-law pressure strength coefficient and the bulk Biot term.

The contact material exports an AD property named `fault_pressure_area_coefficient`, but this pressure kernel has no `alpha_property_name` parameter and never reads that property. Therefore `use_state_dependent_pressure_area=true` changes the exported diagnostic coefficient but, through the documented kernel, has no mechanical effect.

## 8. Mechanical aperture

`ADOrcaCZMComputeMechanicalAperture` reads the normal component of the current local jump:

$$
a_{m,\mathrm{raw}}=g_n.
$$

With the default `clamp_to_zero=true`,

$$
a_m=\max(0,g_n);
$$

otherwise $a_m=g_n$. It includes no reference aperture, residual aperture, initial closure, history, contact closure inversion, or explicit dilation term. Dilation appears in this geometric aperture only if kinematic dilation causes the solved displacement jump itself to open.

The material also publishes the raw aperture. Both outputs are AD properties.

## 9. Roughness-damage hydraulic aperture and permeability

### 9.1 State inputs

`ADOrcaRoughnessDamageFracturePermeability` combines a baseline aperture, stress response, mechanical opening, dilation, roughness self-propping, slip/gouge loss, and creep closure. When non-kinematic dilation is used,

$$
d_{n+1}^{\mathrm{cum}}=d_n^{\mathrm{cum}}+\max(0,\Delta d).
$$

When `use_kinematic_aperture=true`, the constructor deliberately does not couple the dilation-increment property. In the present source this also means the cumulative-dilation diagnostic does not keep accumulating, despite an inline description suggesting it would remain tracked.

Roughness is clamped to $0\le R_r\le1$. The retained dilation fraction and self-propping aperture are

$$
r_d=r_{\mathrm{res}}+(1-r_{\mathrm{res}})R_r,
\qquad
a_{\mathrm{prop}}=a_{\mathrm{prop},0}R_r^{n_r}.
$$

The dilation contribution is

$$
a_d=\begin{cases}
0,&\text{kinematic aperture},\\
\lambda_d d_{n+1}^{\mathrm{cum}}r_d,&\text{non-kinematic aperture}.
\end{cases}
$$

### 9.2 Slip/gouge reduction

If enabled, accumulated slip reduces aperture through

$$
a_g=A_g\left[1-\exp\left(-\frac{\max(0,s-s_*)}{D_g}\right)\right].
$$

The slip source may be configured as AD or non-AD, but the implementation extracts its raw value for this calculation. Consequently the current Jacobian contains no derivative of $a_g$ with respect to slip/displacement.

### 9.3 Effective normal compression

The optional traction input follows the tension-positive convention. The compression magnitude is

$$
N=\max(0,-t_n).
$$

Its sign branch is evaluated from the raw value. The property is fetched only if stress aperture, creep, or explicit diagnostic output requires it.

### 9.4 Stress-dependent aperture options

The linear compliance option is

$$
a_\sigma=C_n(N_{\mathrm{ref}}-N),
$$

which may be negative for compression above the reference.

The Barton--Bandis hydraulic closure option defines

$$
\sigma_0=V_m^{h}K_{ni}^{h},
\qquad
G(N)=\frac{N^{p_h}}{\sigma_0^{p_h}+N^{p_h}},
$$

and

$$
a_\sigma=\max\{0,V_m^{h}[G(N_{\mathrm{ref}})-G(N)]\}.
$$

It produces extra opening only as compression falls below the reference; it does not add further closure above that reference.

The exponential option is

$$
a_\sigma=A_\sigma\exp[-(N-N_{\exp,\mathrm{ref}})/\sigma_c^h].
$$

Unlike the other forms, this is not reference-subtracted: it equals $A_\sigma$ at its reference stress.

### 9.5 Creep closure

With creep enabled, a raw-value implicit update is

$$
r_c=\frac{1}{\tau_c}\left(\frac{N}{N_c}\right)^{q_c},
\qquad
a_{c,n+1}=\frac{a_{c,n}+r_c\Delta t\,a_{c,\max}}{1+r_c\Delta t},
$$

followed by a cap at $a_{c,\max}$. For the special implemented branch $q_c=0$, $r_c=1/\tau_c$ even at $N=0$; thus creep does not vanish in an open/stress-free state in that case. Creep derivatives are not carried by AD.

### 9.6 Final aperture and flow properties

The unbounded composition is

$$
a_h^*=a_{h0}+a_\sigma+\chi_m a_m+a_d+a_{\mathrm{prop}}-a_g-a_c.
$$

The code then applies

$$
a_h=\max(a_{\min},a_h^*),
$$

and, when `max_hydraulic_aperture>0`, also $a_h\le a_{\max}$. The cubic-law outputs are

$$
k_f=\frac{a_h^2}{12},
\qquad
T=\frac{a_h^3}{12\mu}.
$$

`fault_thickness` is accepted for compatibility but unused. `compute_transmissibility` is a legacy/misleading switch name: when true it declares and calculates the transmissivity output. It must remain true if `OrcaFractureFlowInterfaceKernel` is present, because that kernel unconditionally requests `fracture_transmissivity`.

Initialization assumes $R_r=1$, zero stress contribution, and therefore $a_{h,\mathrm{init}}=a_{h0}+a_{\mathrm{prop},0}$ before bounds. If the actual initial roughness differs from one, the first compute changes aperture. The exponential stress law likewise contributes $A_\sigma$ at its reference but initialization omits it. Either mismatch can create a first-step storage transient.

## 10. Fracture-flow interface equation

### 10.1 `OrcaFractureFlowInterfaceKernel`

Let $P_t=\mathbf I-\mathbf n\otimes\mathbf n$ and $\nabla_t=P_t\nabla$. The kernel uses

$$
\kappa_p=\frac{\Gamma T}{a_hL_p},
\qquad
q_p=\kappa_p(p^--p^+),
$$

where $L_p=$ `pressure_penalty_length` and

$$
\Gamma=\begin{cases}\rho_f,&\text{mass form},\\1,&\text{volumetric form}.\end{cases}
$$

The element-side residual is

$$
R_p^-=N^-\left(S_f+q_p\right)
+\Gamma T\nabla_t p^-\cdot\nabla_tN^-,
$$

and the neighbor-side residual is only

$$
R_p^+=-N^+q_p.
$$

Thus the element side carries fracture storage and in-plane Reynolds transport; the neighbor side is tied to it by the pressure-continuity penalty. Sideset orientation therefore determines which trace carries the lower-dimensional flow equation.

In mass form,

$$
S_f=\frac{\rho_fa_h-\rho_{f,n}a_{h,n}}{\Delta t}.
$$

In volumetric form,

$$
S_f=\frac{a_h-a_{h,n}}{\Delta t}+C_fa_h\dot p.
$$

`fluid_compressibility` is ignored in mass form because density evolution already carries compressive storage; the constructor emits a warning if both are requested.

The kernel contains no gravity, explicit leakoff/source term, or matrix Darcy transport. Surrounding bulk flow kernels supply the matrix equation, and the pressure penalty couples its two traces to the same hydraulically thin fracture. Since $\kappa_p$ divides by $a_h$, allowing `min_hydraulic_aperture=0` can cause division by zero even though that value passes the aperture material's range check.

## 11. Per-step constitutive algorithm

At each interface quadrature point, the executed sequence is:

1. Obtain $\mathbf g$, $\Delta\mathbf g$, $\mathbf R$, and $\bar p$.
2. Recover old plastic jump, slip, dilation, unloading, and opening-history state.
3. Construct the old-dilation-adjusted gap, raw closure, and optional unloading transform.
4. Apply hard or regularized unilateral contact and evaluate the start-of-step normal state.
5. Evaluate effective compression, scaled JRC/JCS, mobilized JRC, friction, weakening, dilation, and tangential stiffness.
6. Form the tangential elastic trial state.
7. Return immediately as open or stick when the corresponding test is satisfied.
8. For slip, bracket $\gamma$; at every trial value resolve dilation/contact feedback and recompute strength.
9. Solve $\mathcal R(\gamma)=0$ using safeguarded Newton/bisection; request global time-step reduction on a recoverable failure.
10. Reconstruct $\gamma_{AD}$, current traction, and AD-dependent outputs.
11. Update plastic jump, accumulated slip, dilation, unloading, roughness, and diagnostic state.
12. Rotate local traction, assemble mechanical and pressure interface forces, calculate aperture/transmissivity, and assemble fracture flow.

The order matters. In particular, the stress-dependent tangential stiffness uses the start-of-step compression, while strength and dilation/contact feedback are reevaluated inside the scalar return map.

## 12. Parameter reference

Defaults below are the defaults in the inspected Orca 4.0 source, not necessarily recommended calibration values.

### 12.1 Contact numerics and normal closure

| Input parameter | Default | Units | Implemented role |
|---|---:|---|---|
| `base_name` | empty | -- | Shared interface-material property prefix inherited from the base. |
| `penalty_tangent` | 0 | Pa/m | Tangential stiffness; zero falls back to `initial_normal_stiffness`. |
| `normal_traction_tolerance` | 0 | Pa | Post-dilation open-state threshold; no range check. |
| `tangential_traction_tolerance` | $10^{-16}$ | Pa | Minimum tangential norm for slip direction/detection. |
| `max_plastic_slip_increment` | 0 | m | Optional per-step cap; zero disables. |
| `max_dilation_increment` | 0 | m | Optional per-step cap; zero disables. |
| `max_return_mapping_iterations` | 50 | -- | Safeguarded scalar-solver iteration limit. |
| `return_mapping_iterations` | 8 | -- | Deprecated name; use `max_return_mapping_iterations`. |
| `relative_tolerance` | $10^{-8}$ | -- | Return-map relative tolerance. |
| `contact_gap_regularization` | 0 | m | Smooth positive-part length; zero selects hard active set. |
| `tangential_viscosity` | 0 | Pa s/m | Viscous term $\eta\gamma/\Delta t$. |
| `min_tau_limit` | 0 | Pa | Optional closed-contact shear-strength floor; open branches reset the limit to zero. |
| `use_hyperbolic_normal_closure` | true | -- | Hyperbolic/power closure rather than linear. |
| `initial_normal_stiffness` | $10^{13}$ | Pa/m | $K_{ni}$. |
| `maximum_closure` | $10^{-4}$ | m | $V_m$. |
| `maximum_closure_fraction` | 0.999 | -- | Numerical closure cap as fraction of $V_m$. |
| `normal_closure_stress_exponent` | 1 | -- | $p_n\ge1$ in the generalized closure relation. |
| `normal_closure_offset` | 0 | m | Pre-seating closure $c_0$. |
| `normal_unload_retention_fraction` | 0 | -- | $\zeta$, optional recovered-closure retention. |
| `normal_unload_retention_time` | 0 | s | First-order lag; zero is immediate. |
| `normal_reclosure_stiffness_multiplier` | 1 | -- | $m_r\ge1$ transformed reclosure slope. |
| `normal_unload_activation_slip` | 0 | m | Slip gate for unloading/reclosure evolution. |

### 12.2 Barton--Bandis strength, pressure, and tangential stiffness

| Input parameter | Default | Units | Implemented role |
|---|---:|---|---|
| `jrc` | 10 | -- | Laboratory JRC. |
| `jcs` | $10^8$ | Pa | Laboratory JCS. |
| `residual_friction_angle_degrees` | 30 | degrees | Base/residual friction angle. |
| `cohesion` | 0 | Pa | Shear intercept; not tensile cohesion. |
| `use_scale_correction` | true | -- | Apply length corrections to JRC/JCS. |
| `laboratory_length` | 0.1 | m | $L_0$. |
| `joint_length` | 0.1 | m | $L_n$. |
| `compressive_normal_stress_floor` | $10^3$ | Pa | Stress floor inside logarithm. |
| `pore_pressure_property_name` | `interface_pore_pressure` | -- | Pressure property used only for nonzero strength coefficient. |
| `pore_pressure_strength_coefficient` | 0 | -- | $\beta_p$ in $\sigma_s$. |
| `allow_negative_roughness_angle` | false | -- | Whether $i<0$ is retained. |
| `min_friction_angle_degrees` | 0 | degrees | Lower peak-angle cap. |
| `max_friction_angle_degrees` | 85 | degrees | Upper peak-angle cap. |
| `use_state_dependent_fault_pressure_coefficient` | false | -- | Export $\alpha_f=\sigma_0/(\sigma_0+\sigma_c)$. Currently unconsumed by pressure kernel. |
| `fault_pressure_area_reference_stress` | $1.897751\times10^8$ | Pa | $\sigma_0$ in exported $\alpha_f$. |
| `use_mobilized_jrc` | false | -- | Ramp mobilized JRC with accumulated slip. |
| `peak_shear_displacement` | $10^{-3}$ | m | Slip for full JRC mobilization. |
| `mobilized_jrc_exponent` | 1 | -- | Mobilization exponent. |
| `use_stress_dependent_tangential_stiffness` | false | -- | Activate old-stress-dependent $K_t$. |
| `tangential_stiffness_reference_stress` | $10^6$ | Pa | Reference compression. |
| `tangential_stiffness_exponent` | 1 | -- | Stress exponent. |
| `min_tangential_stiffness_fraction` | 0.05 | -- | Lower stiffness fraction. |

### 12.3 Dilation, subclass weakening, and roughness

| Input parameter | Default | Units | Implemented role |
|---|---:|---|---|
| `use_dilatancy` | true | -- | Enable slip dilation. |
| `dilation_factor` | 0.5 | -- | Multiplier on BB roughness angle in legacy law. |
| `min_dilation_angle_degrees` | 0 | degrees | Lower angle cap. |
| `max_dilation_angle_degrees` | 30 | degrees | Upper angle cap. |
| `accumulate_irreversible_dilation` | true | -- | Store dilation history. |
| `cap_dilation_to_available_closure` | true | -- | Limit increment by starting closure. |
| `use_decoupled_dilation` | false | -- | Use independent exponential angle decay. |
| `dilation_angle_peak_degrees` | 1.5 | degrees | Decoupled peak angle. |
| `dilation_angle_residual_degrees` | 0.3 | degrees | Decoupled residual angle. |
| `dilation_decay_distance` | $10^{-4}$ | m | Decoupled decay length. |
| `dilation_opens_joint` | false | -- | Choose kinematic rather than legacy dilation sign/path. |
| `use_slip_weakening` | true | -- | Activate hardening-subclass weakening. |
| `characteristic_slip_distance` | $10^{-3}$ | m | $D_c$. |
| `slip_weakening_exponent` | 1 | -- | $m_w\ge1$. |
| `slip_weakening_residual_friction_angle_degrees` | -1 | degrees | Negative selects the base residual angle. |
| `residual_cohesion` | 0 | Pa | Large-slip cohesion; must not exceed `cohesion`. |
| `use_roughness_degradation` | false | -- | Export slip-degrading $R_r$. |
| `roughness_characteristic_slip` | $10^{-3}$ | m | $D_r$. |
| `roughness_state_initial` | 1 | -- | $R_{\mathrm{ini}}$. |
| `roughness_state_residual` | 0 | -- | $R_{\mathrm{res}}\le R_{\mathrm{ini}}$. |

### 12.4 Output-only normal-opening parameters

| Input parameter | Default | Units | Implemented role |
|---|---:|---|---|
| `reported_reversible_normal_opening_scale` | 1 | -- | Scale on reconstructed reversible opening. |
| `reported_reversible_normal_opening_retention_fraction` | 0 | -- | Peak-opening memory fraction. |
| `reported_reversible_normal_opening_retention_activation_slip` | 0 | m | Activation threshold for memory. |
| `reversible_normal_compliance` | 0 | m/Pa | Elastic recovery compliance. |
| `reversible_normal_reference_stress` | 0 | Pa | Stress at which elastic recovery vanishes. |
| `reversible_normal_opening_activation_slip` | 0 | m | Compliance activation threshold. |
| `reversible_normal_opening_activation_distance` | $10^{-5}$ | m | Activation ramp distance. |
| `reversible_normal_opening_activation_exponent` | 1 | -- | Activation ramp exponent. |

All quantities in this table affect diagnostics only.

### 12.5 Mechanical-aperture parameters

| Input parameter | Default | Implemented role |
|---|---|---|
| `base_name` | empty | Optional property prefix. |
| `jump_property_name` | `interface_displacement_jump` | Local jump vector input. |
| `aperture_property_name` | `mechanical_aperture` | Clamped/output aperture name. |
| `raw_aperture_property_name` | `mechanical_aperture_raw` | Unclamped output name. |
| `clamp_to_zero` | true | Use $\max(0,g_n)$. |

### 12.6 Hydraulic-aperture and permeability parameters

| Input parameter | Default | Units / role |
|---|---|---|
| `base_name` | empty | Optional property prefix. |
| `mechanical_aperture_name` | `mechanical_aperture` | AD input. |
| `dilation_jump_increment_name` | `dilation_jump_increment` | AD input unless kinematic mode. |
| `roughness_name` | `roughness_state` | AD input unless kinematic mode. |
| `hydraulic_aperture_name` | `hydraulic_aperture` | AD output. |
| `fracture_permeability_name` | `fracture_permeability` | AD output. |
| `cumulative_dilation_name` | `cumulative_dilation` | Stateful AD output. |
| `transmissibility_name` | `fracture_transmissivity` | Cubic-law AD output. |
| `roughness_retention_factor_name` | `roughness_retention_factor` | Diagnostic output. |
| `self_propping_aperture_name` | `self_propping_aperture` | Diagnostic output. |
| `initial_hydraulic_aperture` | 0 m | $a_{h0}$. |
| `aperture_scale` | 1 | $\chi_m$; unrestricted real. |
| `normal_stress_aperture_compliance` | 0 m/Pa | Linear stress aperture. |
| `reference_effective_normal_stress` | 0 Pa | Linear/BB reference compression. |
| `use_nonlinear_normal_closure` | false | Select nonlinear stress aperture. |
| `bb_max_aperture_closure` | 0 m | Hydraulic $V_m^h$. |
| `bb_initial_normal_stiffness` | 0 Pa/m | Hydraulic $K_{ni}^h$. |
| `bb_stress_exponent` | 1 | Hydraulic $p_h\ge1$. |
| `nonlinear_closure_type` | `barton_bandis` | `barton_bandis` or `exponential`. |
| `exp_closure_amplitude` | 0 m | $A_\sigma$. |
| `exp_closure_stress_scale` | 1 Pa | $\sigma_c^h>0$. |
| `exp_closure_reference_stress` | 0 Pa | Exponential reference. |
| `effective_normal_traction_name` | `czm_sigma_n` | Tension-positive scalar input. |
| `normal_stress_aperture_name` | `normal_stress_aperture` | Diagnostic output. |
| `effective_normal_compression_name` | `effective_normal_compression` | Diagnostic output. |
| `compute_effective_normal_compression` | false | Fetch/export compression even if unused by aperture. |
| `dilation_scale` | 1 | $\lambda_d$, ignored in kinematic mode. |
| `use_kinematic_aperture` | false | Drop separate dilation input and replace evolving roughness input by $R_r=1$. |
| `min_hydraulic_aperture` | $10^{-12}$ m | Lower aperture bound. |
| `max_hydraulic_aperture` | 0 m | Upper bound; zero disables. |
| `retention_residual` | 0.2 | $r_{\mathrm{res}}\in[0,1]$. |
| `self_propping_scale` | 0 m | $a_{\mathrm{prop},0}$. |
| `self_propping_exponent` | 1 | $n_r>0$. |
| `use_slip_damage` | false | Enable gouge-fill reduction. |
| `slip_damage_scale` | 0 m | $A_g$. |
| `slip_damage_characteristic_slip` | $10^{-3}$ m | $D_g$. |
| `slip_damage_onset_slip` | 0 m | $s_*$. |
| `cumulative_plastic_slip_name` | `cumulative_plastic_slip` | Slip input property. |
| `cumulative_plastic_slip_is_ad` | true | Choose AD/non-AD lookup; computation uses raw value. |
| `slip_damage_aperture_name` | `slip_damage_aperture` | Diagnostic output. |
| `use_closure_creep` | false | Enable time-dependent closure. |
| `closure_creep_max_aperture` | 0 m | $a_{c,\max}$. |
| `closure_creep_time` | $10^5$ s | $\tau_c$. |
| `closure_creep_reference_stress` | $10^6$ Pa | $N_c$. |
| `closure_creep_stress_exponent` | 1 | $q_c\ge0$. |
| `closure_creep_aperture_name` | `closure_creep_aperture` | Stateful diagnostic output. |
| `compute_transmissibility` | true | Compatibility switch associated with transmissivity output. |
| `fluid_viscosity` | $1.002\times10^{-3}$ Pa s | $\mu$. |
| `fault_thickness` | $10^{-3}$ m | Accepted but unused. |

### 12.7 Rotation, mechanics, pressure, and flow object parameters

| Object | Parameter | Default / requirement |
|---|---|---|
| `OrcaCZMComputeDisplacementJump` | `displacements` | Required coupled displacement vector inherited by the CZM kinematics. |
| `OrcaCZMComputeDisplacementJump` | `base_name` | Optional property prefix. |
| `OrcaCZMInterfacePressure` | `pore_pressure` | Required coupled pressure. |
| `OrcaCZMInterfacePressure` | `base_name` | Optional property prefix. |
| `OrcaComputeGlobalTractionSmallStrain` | `base_name` | Optional property prefix; no bulk-stress parameter. |
| `OrcaMechInterfaceKernel` | `component` | Required displacement component. |
| `OrcaMechInterfaceKernel` | `displacements` | Required; count must equal mesh dimension. |
| `OrcaMechInterfaceKernel` | `base_name` | Optional prefix; traction name is set to `traction_global`. |
| `OrcaCZMFluidPressureInterfaceKernel` | `component` | Required displacement component. |
| `OrcaCZMFluidPressureInterfaceKernel` | `displacements` | Required; count must equal mesh dimension. |
| `OrcaCZMFluidPressureInterfaceKernel` | `base_name` | Optional prefix. |
| `OrcaCZMFluidPressureInterfaceKernel` | `pore_pressure_property_name` | `interface_pore_pressure`. |
| `OrcaCZMFluidPressureInterfaceKernel` | `pressure_traction_coefficient` | -1. |
| `OrcaFractureFlowInterfaceKernel` | `base_name` | Optional prefix. |
| `OrcaFractureFlowInterfaceKernel` | `pressure_penalty_length` | $10^{-4}$ m, strictly positive. |
| `OrcaFractureFlowInterfaceKernel` | `multiply_by_fluid_density` | false. |
| `OrcaFractureFlowInterfaceKernel` | `fluid_compressibility` | 0 Pa$^{-1}$; volumetric form only. |

### 12.8 Conditional checks and property naming

The constructor enforces subclass conditions not expressible through simple range checks: the slip-weakening tail angle must remain below 89.9 degrees; `residual_cohesion` cannot exceed `cohesion`; and `roughness_state_residual` cannot exceed `roughness_state_initial`. Nonlinear hydraulic Barton--Bandis closure requires positive `bb_max_aperture_closure` and `bb_initial_normal_stiffness`; exponential closure requires positive `exp_closure_amplitude`.

`base_name` is normalized by appending an underscore. Most contact/kinematic properties use that prefix. The permeability material is asymmetric: its dilation, roughness, slip, and effective-normal-traction inputs are prefixed, but `mechanical_aperture_name` is looked up exactly as supplied, and its named outputs are declared exactly as supplied without automatically adding `base_name`. Custom names should therefore be checked against the constructor rules rather than assumed to share one uniform prefix policy.

## 13. State and material-property reference

### 13.1 Principal contact outputs

| Property | AD? | Stateful? | Meaning |
|---|---|---|---|
| `interface_traction` | yes | through incremental base | Current local traction. |
| `fracture_state` | no | no | 0 stick, 1 slip, 2 open. |
| `limit_tau` | no | no | Current shear-strength limit. |
| `plastic_slip_increment` | no | no | Converged $\gamma$. |
| `dilation_jump_increment` | yes | no | Current nonnegative $\Delta d$. |
| `cumulative_plastic_slip` | no | yes | $s$. |
| `irreversible_dilation` | no | yes | $d$. |
| `plastic_tangential_jump` | no | yes | $\mathbf g_t^p$. |
| `bb_unload_retained_opening` | no | yes | $a_r$. |
| `bb_unload_min_closure` | no | yes | Retained minimum raw closure. |
| `reversible_normal_opening` | no | no | Reconstructed output component. |
| `normal_opening_total` | no | no | Output-only total opening. |
| `maximum_reversible_normal_opening` | no | yes | Peak-memory state. |
| `friction_coefficient_effective` | no | no | Current weakened/effective $\mu$. |
| `cohesion_effective` | no | no | Current weakened cohesion; zeroed in open diagnostics. |
| `roughness_state` | yes | no | Hydraulic retention input $R_r$. |
| `roughness_damage` | no | no | $1-R_r$. |
| `bb_compressive_normal_stress` | no | no | $\sigma_c$. |
| `bb_effective_normal_stress` | no | no | $\sigma_s$. |
| `bb_normal_closure` | yes | no | Active closure $c$. |
| `bb_normal_stiffness_tangent` | no | no | Returned normal-law tangent. |
| `bb_jrc_scaled`, `bb_jcs_scaled` | no | no | Scale-corrected inputs. |
| `bb_jrc_mobilized` | no | no | Mobilized JRC. |
| `bb_roughness_angle_degrees` | no | no | $i$. |
| `bb_peak_friction_angle_degrees` | no | no | $\phi_{\mathrm{BB}}$. |
| `bb_peak_friction_coefficient` | no | no | $\tan\phi_{\mathrm{BB}}$. |
| `bb_dilation_angle_degrees` | no | no | $\psi$. |
| `bb_dilation_coefficient` | no | no | $\tan\psi$. |
| `bb_tangential_stiffness` | no | no | Step value $K_t$. |
| `fault_pressure_area_coefficient` | yes | no | Exported $\alpha_f$; no current kernel consumer. |

The FastAD design deliberately declares output-only quantities as non-AD. They are suitable for diagnostics and downstream raw-value laws, not for adding new strongly coupled terms unless AD support is restored.

### 13.2 Coupling properties

| Producer | Property | Consumer |
|---|---|---|
| Displacement-jump material | `interface_displacement_jump`, `displacement_jump_global`, `czm_total_rotation` | Contact, aperture, traction/pressure rotation. |
| Incremental traction base | `interface_displacement_jump_inc` | Contact return mapping. |
| Interface-pressure material | `interface_pore_pressure` | Contact strength option and pressure traction kernel. |
| Contact material | `interface_traction` | Global-traction material. |
| Global-traction material | `traction_global` | Mechanical interface kernel. |
| Mechanical-aperture material | `mechanical_aperture`, `mechanical_aperture_raw` | Hydraulic-aperture material / diagnostics. |
| Contact material | `dilation_jump_increment`, `roughness_state`, `cumulative_plastic_slip` | Hydraulic-aperture extensions. |
| Hydraulic-aperture material | `hydraulic_aperture`, `fracture_transmissivity` | Fracture-flow kernel. |

## 14. Production SWS4 wiring

The inspected `SWS4_OrcaBartonBandisContactTractionFastADHardening.i` deck instantiates the complete chain:

- `OrcaCZMInterfacePressure` averages the two pressure traces.
- The hardening BB material reads jump/pressure and produces local traction, dilation, roughness, and slip.
- `OrcaComputeGlobalTractionSmallStrain` rotates contact traction.
- Three `OrcaMechInterfaceKernel` objects assemble its global components.
- Three `OrcaCZMFluidPressureInterfaceKernel` objects separately assemble pressure traction with coefficient $-0.86$.
- `ADOrcaCZMComputeMechanicalAperture` extracts $\max(0,g_n)$.
- `ADOrcaRoughnessDamageFracturePermeability` builds $a_h$, $k_f$, and $T$.
- `OrcaFractureFlowInterfaceKernel` uses $a_h$ and $T$ in mass form with $L_p=5\times10^{-4}$ m.

The contact block correctly sets `pore_pressure_strength_coefficient=0.0`, documenting that pressure enters mechanics through the pressure-traction kernels and should not also be subtracted inside the strength law.

The active controls include `dilation_opens_joint=true`, whereas the aperture block hard-codes `use_kinematic_aperture=false`, `aperture_scale=0.001`, and `dilation_scale=0.0117`. This is not the pairing prescribed by the source description. Kinematic dilation already influences the solved mechanical jump; non-kinematic aperture mode additionally integrates `dilation_jump_increment`. Therefore the configuration contains two dilation routes, albeit with fitted scale factors. It should be treated as an empirical calibrated composition, not as a strictly non-double-counted kinematic formulation. The structurally consistent kinematic pairing is:

~~~text
dilation_opens_joint = true
use_kinematic_aperture = true
~~~

followed by recalibration because this switch also suppresses the separate roughness-retention and dilation contributions in the current aperture constructor.

## 15. Limiting cases and verification identities

These checks isolate the implementation and are useful for regression tests.

### 15.1 Rigid opening

For $g_n$ sufficiently positive, zero gap regularization, and no initial offset that restores contact:

$$
c=0,\quad\sigma_c=0,\quad\mathbf t=\mathbf0,\quad\text{state}=2.
$$

Pressure traction may still be nonzero because it is assembled separately.

### 15.2 Linear closed stick

With hyperbolic closure disabled, no unloading transform, no slip, and $c>0$:

$$
t_n=-K_{ni}c,
\qquad
\mathbf t_t=K_t(\mathbf g_t-\mathbf g_t^p).
$$

### 15.3 Standard BB hyperbola

For $p_n=1$,

$$
\sigma_c=K_{ni}V_m\frac{c}{V_m-c},
\qquad
c=V_m\frac{\sigma_c}{K_{ni}V_m+\sigma_c}.
$$

Forward and inverse evaluations should recover each other away from the cap and near-zero secant region.

### 15.4 Dry strength

With `pore_pressure_strength_coefficient=0`, pressure changes must not directly change the local contact material at fixed displacement/state. They may still change it indirectly through the globally solved pressure traction and displacement.

### 15.5 Large-slip weakening

For $s\gg D_c$, $W\to0$, so

$$
\mu_{\mathrm{eff}}\to\mu_r,
\qquad
c_{\mathrm{eff}}\to c_{\mathrm{res}}.
$$

For $s\gg D_r$, $R_r\to R_{\mathrm{res}}$, but the mechanical strength is unchanged by that roughness-state limit.

### 15.6 Aperture identities

With every extension disabled and no bounds active:

$$
a_h=a_{h0}+\chi_ma_m.
$$

With $\chi_m=0$, no stress/slip/creep/self-propping term, and non-kinematic dilation:

$$
a_h=a_{h0}+\lambda_dd^{\mathrm{cum}}r_d.
$$

For any positive $a_h$, the outputs must satisfy

$$
k_f=a_h^2/12,
\qquad
T=a_hk_f/\mu.
$$

### 15.7 Interface conservation

For matching constant tests, mechanical and pressure interface residuals sum to zero across the two sides. The flow pressure-penalty terms also sum to zero, while storage and tangential transport intentionally remain on the element side.

## 16. Consistency and implementation audit

### 16.1 Confirmed, internally consistent behavior

- Local/global frames, jump sign, and traction rotation are mutually consistent.
- Mechanical and pressure traction kernels use equal-and-opposite side residuals.
- The contact normal traction is tension-positive and the aperture material converts it to compression with $N=\max(0,-t_n)$.
- The hardening subclass evaluates strength in both AD and raw-real paths, enabling IFT reconstruction.
- `cumulative_plastic_slip_is_ad=false` in the production deck matches the FastAD contact material's non-AD slip property.
- The flow kernel consumes `fracture_transmissivity`, matching the permeability material's default output name despite the compatibility spelling `transmissibility_name`.

### 16.2 Source/documentation inconsistencies or inactive paths

1. **State-dependent pressure area is not wired.** The contact class description says `OrcaCZMFluidPressureInterfaceKernel` can read `fault_pressure_area_coefficient` through `alpha_property_name`; the inspected kernel has no such parameter and uses only its constant `pressure_traction_coefficient`. Enabling the contact flag therefore does not alter mechanics through this kernel.
2. **Kinematic-mode cumulative dilation is not tracked.** The permeability parameter description says cumulative dilation remains an output in kinematic mode, but the constructor does not couple the dilation increment and the update receives zero. The diagnostic stays unchanged.
3. **Evolving roughness is dropped in kinematic aperture mode.** The constructor nulls both dilation and roughness inputs and substitutes $R_r=1$. Consequently retention is locked at one and self-propping is locked at its maximum scale; evolving roughness cannot operate even though only double-counted dilation needs to be removed conceptually.
4. **Creep with exponent zero does not freeze when open.** The prose describes creep as frozen for an open joint, but the $q_c=0$ branch sets $r_c=1/\tau_c$ regardless of $N$.
5. **Exponential aperture is not zero at its reference.** It returns `exp_closure_amplitude` at $N=N_{\exp,\mathrm{ref}}$, while initialization assumes zero stress-aperture contribution.
6. **Initial hydraulic aperture assumes $R_r=1$.** A different contact `roughness_state_initial` causes a first-compute change and potentially artificial aperture-rate storage.
7. **Zero minimum aperture is unsafe for the flow kernel.** The aperture parameter accepts zero, but pressure-penalty conductance divides by $a_h$.
8. **Several hydraulic history derivatives are absent.** Slip damage and creep use raw values. The subclass roughness state is declared AD but is calculated from the non-AD accumulated-slip state, so it also carries no displacement derivative. Nonlinear tangents omit these feedbacks.
9. **Stress-dependent tangential stiffness is lagged.** Its present-step normal-displacement derivative is omitted.
10. **Decoupled dilation tangent is approximate.** The derivative of $\psi(s)$ is omitted in the return-map derivative.
11. **`fault_thickness` is unused.** It cannot tune permeability or transmissivity in this implementation.
12. **`return_mapping_iterations` is deprecated.** Its old default of 8 must not be confused with the active `max_return_mapping_iterations=50` default.
13. **The shear-strength floor does not survive an open branch.** The `min_tau_limit` description says the limit remains nonzero even when the joint opens, but both hard-open and dilation-open branches explicitly set `limit_tau=0` and total traction to zero. The floor applies only while contact remains closed.

These points are implementation observations, not silent corrections made by this document. Simulations should be interpreted according to the current source until the code is changed and regression-tested.

### 16.3 Configuration risk in the production deck

The production SWS4 deck combines kinematic mechanical dilation with non-kinematic hydraulic accumulation. This may have been retained as a calibrated empirical route, and the small `aperture_scale` limits its geometric contribution, but it is not the source-described no-double-counting configuration. Switching to `use_kinematic_aperture=true` changes more than one term because the current constructor also replaces evolving roughness by $R_r=1$; a controlled recalibration and mesh/time-step comparison is required.

## 17. Calibration and numerical guidance

1. Determine $K_{ni}$, $V_m$, $p_n$, and `normal_closure_offset` from normal loading/unloading before fitting shear parameters.
2. Determine JRC/JCS and the base residual angle from the compression-dependent peak envelope. Decide explicitly whether length-scale correction is applicable.
3. Fit JRC mobilization only if the pre-peak rise is resolved; otherwise leave it off to avoid confounding peak mobilization with slip weakening.
4. Fit $D_c$, $m_w$, the tail angle, and residual cohesion to the post-peak branch.
5. Fit dilation independently with the decoupled law when strength-derived roughness does not reproduce observed normal displacement.
6. Treat `tangential_viscosity`, plastic/dilation increment caps, and the time step as numerical/rate regularization parameters; demonstrate that conclusions are insensitive over a justified range.
7. Choose one primary pressure route. A separate pressure traction is needed for normal mechanical opening; a nonzero pressure strength coefficient additionally changes the friction envelope.
8. Use a strictly positive minimum hydraulic aperture when the fracture-flow kernel is active.
9. Check aperture initialization at the first time step, especially with $R_{\mathrm{ini}}\ne1$ or exponential normal closure.
10. Verify results under reversal of sideset orientation because the fracture flow equation resides only on the element side.

## 18. Compact implementation equations

For reference, the coupled model can be condensed to

$$
\mathbf g=\mathbf R^T(\mathbf u^+-\mathbf u^-),
\qquad
\bar p=(p^-+p^+)/2,
$$

$$
c=\mathcal C(g_n,d,\text{unloading}),
\qquad
t_n=-\mathcal N(c),
$$

$$
\sigma_s=\max(0,\sigma_c-\beta_p\bar p)\ \text{when }\beta_p>0,
$$

$$
Y=c_{\mathrm{eff}}(s)+\sigma_s\mu_{\mathrm{eff}}(s,\sigma_s),
$$

$$
\mathcal R(\gamma)=\tau_{\mathrm{tr}}-(K_t+\eta/\Delta t)\gamma-Y(\gamma)=0,
$$

$$
\mathbf t^G=\mathbf R\mathbf t,
\qquad
\mathbf t_p^G=\mathbf R(c_p\bar p,0,0)^T,
$$

$$
a_m=\max(0,g_n),
$$

$$
a_h=\operatorname{bounds}\left(
a_{h0}+a_\sigma+\chi_ma_m+a_d+a_{\mathrm{prop}}-a_g-a_c
\right),
$$

$$
k_f=a_h^2/12,
\qquad
T=a_h^3/(12\mu),
$$

with fracture storage, tangential transport, and trace coupling assembled by the residuals in Section 10.

## 19. Interpretation boundary

The formulation represents a zero-thickness, small-strain interface with unilateral compression contact, frictional slip, optional dilation and weakening, and a lower-dimensional cubic-law flow model. It does not by itself provide tensile cohesive fracture, finite-rotation contact, asperity-scale fluid mechanics, thermal pressurization, chemical alteration, or a fully consistent energy-based damage potential. Those effects require additional constitutive terms and validation rather than reinterpretation of the existing parameters.

## 20. Audited implementation sources

The equations and defaults above were reconciled against these Orca 4.0 files:

- `src/InterfaceMaterial/ADOrcaBartonBandisContactTractionFastAD.C` and its header
- `src/InterfaceMaterial/ADOrcaBartonBandisContactTractionFastADHardening.C` and its header
- `include/utils/OrcaNormalClosure.h`
- `src/InterfaceMaterial/OrcaCZMComputeLocalTractionIncrementalBase.C`
- `src/InterfaceMaterial/OrcaCZMComputeDisplacementJump.C` and `include/utils/OrcaCZMTools.h`
- `src/InterfaceMaterial/OrcaCZMInterfacePressure.C`
- `src/InterfaceMaterial/OrcaComputeGlobalTractionSmallStrain.C`
- `src/InterfaceMaterial/ADOrcaCZMComputeMechanicalAperture.C`
- `src/InterfaceMaterial/ADOrcaRoughnessDamageFracturePermeability.C`
- `src/interfacekernels/OrcaMechInterfaceKernel.C`
- `src/interfacekernels/OrcaCZMFluidPressureInterfaceKernel.C`
- `src/interfacekernels/OrcaFractureFlowInterfaceKernel.C`
- `src/materials/MechMaterial/OrcaMechMaterial.C` and `src/kernels/MechKernel/OrcaPoroMechKernel.C` for bulk context
- `doc/Theory/orca_czm_theory.md` for comparison with existing theory
- `Examples/YeGhasemmi2018/SWS4/SWS4_OrcaBartonBandisContactTractionFastADHardening.i` for production wiring

This document records the inspected source behavior. It does not modify the Orca implementation or silently reinterpret inactive parameters.
