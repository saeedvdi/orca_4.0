# Constitutive law for ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile

## 1. Scope

This object is a zero-thickness cohesive-contact-friction interface law. It combines:

1. a mixed-mode bilinear cohesive branch for the intact area;
2. unilateral normal contact over the full interface;
3. a damaged-area tangential branch governed by roughness-dependent
   Mohr--Coulomb friction; and
4. a non-associative, irreversible dilation law coupled to the friction return map.

The scalar cohesive damage $d\in[0,1]$ also acts as the damaged contact-area fraction.
The intact fraction $1-d$ weights the cohesive branch, while $d$ weights the frictional
tangential branch. Normal contact is not multiplied by $d$.

With <code>enable_tensile_cohesion = false</code>, the interface is initialized with
$d=1$. It is then a pre-existing frictional joint without tensile or intact cohesive
resistance. This is the usual Mohr--Coulomb baseline configuration.

This formulation follows the implementation in:

- <code>src/InterfaceMaterial/ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile.C</code>
- <code>include/InterfaceMaterial/ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile.h</code>
- <code>include/utils/OrcaNormalClosure.h</code>

## 2. Local kinematics and signs

The local displacement jump and traction are

$$
\boldsymbol g=
\begin{bmatrix}g_n & \boldsymbol g_t\end{bmatrix}^{\mathsf T},
\qquad
\boldsymbol g_t=(g_{t1},g_{t2}),
$$

$$
\boldsymbol t=
\begin{bmatrix}t_n & \boldsymbol t_t\end{bmatrix}^{\mathsf T}.
$$

Orca uses

$$
g_n>0\ \text{for opening},\qquad
t_n>0\ \text{for tension},\qquad
t_n<0\ \text{for compression}.
$$

The irreversible variables are the tangential plastic jump
$\boldsymbol g_t^p$, normal plastic opening $g_n^p\ge0$, and cumulative plastic
slip $s\ge0$. During a material substep,

$$
\boldsymbol g_{t,n+1}^p
=\boldsymbol g_{t,n}^p+\Delta\gamma\,\boldsymbol m,
\qquad
s_{n+1}=s_n+\Delta\gamma,
\qquad
\Delta\gamma\ge0,
$$

where $\boldsymbol m$ is the trial shear-traction direction. The normal plastic
opening is solved simultaneously with $\Delta\gamma$.

The regularized positive part and maximum used below are

$$
\langle x\rangle_{\epsilon,+}
=\frac12\left(x+\sqrt{x^2+\epsilon^2}\right),
$$

$$
\max_{\epsilon}(a,b)
=\frac12\left(a+b+\sqrt{(a-b)^2+\epsilon^2}\right).
$$

Other transitions, including contact, stick/slip, cohesive thresholds, and the
dilation limiter, use semismooth active-set decisions.

## 3. Normal contact

Define the mechanical overlap

$$
o=g_n^p-g_n.
$$

### 3.1 Linear penalty branch

With <code>use_hyperbolic_normal_closure = false</code>,

$$
c=\langle o\rangle_{\epsilon_g,+},
\qquad
p_c=K_n c,
\qquad
t_n^{\mathrm{contact}}=-p_c,
$$

where $K_n$ is <code>penalty_normal</code> and $p_c\ge0$ is compression
positive.

### 3.2 Power-law closure branch

With <code>use_hyperbolic_normal_closure = true</code>,

$$
c=\operatorname{clamp}
\left(
\langle o+c_0\rangle_{\epsilon_g,+},
0,
f_cV_m
\right),
$$

and the implemented closure law is

$$
\boxed{
p_c=K_{ni}V_m
\left(\frac{c}{V_m-c}\right)^{1/p_n}
}.
$$

The parameters are

- $K_{ni}$: <code>initial_normal_stiffness</code>;
- $V_m$: <code>maximum_closure</code>;
- $p_n$: <code>normal_closure_stress_exponent</code>;
- $c_0$: <code>normal_closure_offset</code>; and
- $f_c$: <code>maximum_closure_fraction</code>.

The exact inverse of the implemented expression is

$$
c=V_m\frac{q}{1+q},
\qquad
q=\left(\frac{p_c}{K_{ni}V_m}\right)^{p_n}.
$$

For $p_n>1$, the exact tangent is singular as $c\rightarrow0^+$. The code uses
a secant linearization below

$$
c_{\mathrm{lin}}=\min(10^{-9}\ {\rm m},\,0.01V_m).
$$

At the upper closure cap, the algorithmic tangent is set to zero. This is numerical
protection and should not become active in a calibrated physical solution.

## 4. Mixed-mode tensile cohesive branch

This branch is inactive when <code>enable_tensile_cohesion = false</code>.
Let

$$
K_c=\frac{T_0}{\delta_0},
$$

$$
\delta=
\sqrt{
\langle g_n\rangle_{\epsilon_c,+}^2
+\beta_c^2\lVert\boldsymbol g_t\rVert^2
},
\qquad
\kappa_{n+1}=\max(\kappa_n,\delta).
$$

Here $T_0$ is <code>cohesive_peak_traction</code>, $\delta_0$ is
<code>cohesive_initial_separation</code>, $\delta_f$ is
<code>cohesive_final_separation</code>, and $\beta_c$ is
<code>cohesive_shear_weight</code>.

The damage target is

$$
d^*(\kappa)=
\begin{cases}
0, & \kappa\le\delta_0,\\[2mm]
\displaystyle
\frac{\delta_f(\kappa-\delta_0)}
{\kappa(\delta_f-\delta_0)},
& \delta_0<\kappa<\delta_f,\\[3mm]
1, & \kappa\ge\delta_f.
\end{cases}
$$

For zero damage viscosity,

$$
d_{n+1}=\max(d_n,d^*).
$$

With Duvaut--Lions relaxation time $\eta_d>0$ and substep duration
$\Delta t_s$,

$$
\widehat d=
\frac{d_n+(\Delta t_s/\eta_d)d^*}
{1+\Delta t_s/\eta_d},
\qquad
d_{n+1}=\max(d_n,\widehat d).
$$

The cohesive tractions are

$$
t_n^{\mathrm{coh}}
=(1-d)K_c
\langle g_n-g_{n,\mathrm{old}}^p\rangle_{\epsilon_c,+},
$$

$$
\boldsymbol t_t^{\mathrm{coh}}
=(1-d)K_c\beta_c^2\boldsymbol g_t.
$$

Damage is driven by the absolute mixed-mode separation $\delta$, but recoverable
normal tension acts only on the opening beyond the old dilated contact surface. This
makes cohesive tension and contact compression mutually exclusive apart from the narrow
regularization zone.

For monotonic loading, the total cohesive fracture energy is

$$
G_c=\frac12T_0\delta_f.
$$

## 5. Roughness-dependent Mohr--Coulomb strength

Roughness degrades irreversibly with plastic slip. Incrementally,

$$
R_{n+1}
=R_r+(R_n-R_r)
\exp\left(-\frac{\Delta\gamma}{L_R}\right),
$$

which integrates to

$$
R(s)=R_r+(R_0-R_r)e^{-s/L_R}.
$$

Define

$$
\bar R=\frac{R-R_r}{1-R_r}.
$$

The friction coefficient and Coulomb intercept are

$$
\mu(R)
=\mu_s+(\mu_r-\mu_s)\bar R^{m_\mu},
$$

$$
c_f(R)
=c_s+(c_r-c_s)\bar R^{m_c}.
$$

Subscripts $r$ and $s$ on $\mu$ and $c_f$ identify the user-specified rough
and smooth end members. The roughness floor is separately denoted $R_r$.

With memory features disabled, the raw strength is

$$
Y_{\mathrm{raw}}=c_f(R)+\mu(R)p_c.
$$

### 5.1 Optional normal-pressure memory

When <code>normal_strength_retention_factor</code> is zero, $p_m=p_c$.
Otherwise,

$$
\Delta g_n^+
=\langle g_{n,n+1}-g_{n,n}\rangle_{\epsilon_g,+},
$$

$$
p_{\mathrm{ret}}
=p_{m,n}
\exp\left(
\frac{\ln\zeta}{L_m}\Delta g_n^+
\right),
$$

$$
p_m=\max_{\epsilon_\sigma}(p_c,p_{\mathrm{ret}}).
$$

Here $\zeta$ is the fraction retained after one opening distance $L_m$. The
raw strength becomes

$$
Y_{\mathrm{raw}}=c_f+\mu p_m.
$$

### 5.2 Optional retained shear support

When enabled, a decaying historical candidate supplies a lower strength envelope
before secondary weakening:

$$
Y_{\mathrm{pre}}
=\max_{\epsilon_\sigma}
\left[
Y_{\mathrm{raw}},
H Y_{H,n}e^{-\Delta\gamma/L_H}
\right].
$$

When disabled, $Y_{\mathrm{pre}}=Y_{\mathrm{raw}}$.

### 5.3 Optional secondary weakening

The additional large-slip weakening is

$$
W_2(s)=
\begin{cases}
0, & s\le s^*,\\
\Delta S\left[1-e^{-(s-s^*)/w}\right], & s>s^*.
\end{cases}
$$

The final strength used by the return map is

$$
\boxed{
Y=\max_{\epsilon_\sigma}
\left(Y_{\mathrm{pre}}-W_2,0\right)
}.
$$

A negative cohesion intercept is permitted because it may be a linear fit to a
curved strength envelope. The smooth zero floor prevents a negative yield strength.

## 6. Non-associative dilation

The dilation angle is interpolated in angle space:

$$
\psi(s)
=\psi_{\mathrm{res}}
+(\psi_{\mathrm{peak}}-\psi_{\mathrm{res}})
\exp\left[
-\left(\frac{s}{L_\psi}\right)^{m_\psi}
\right].
$$

The code then evaluates $\tan\psi(s)$. It does not interpolate directly between
$\tan\psi_{\mathrm{peak}}$ and $\tan\psi_{\mathrm{res}}$.

The optional normal-stress support factor is

$$
S_p(p_s)
=
\left(\frac{p_s}{p_s+\sigma_{\mathrm{low}}}\right)^{n_{\mathrm{low}}}
\left(
\frac{\sigma_{\mathrm{high}}}
{p_s+\sigma_{\mathrm{high}}}
\right)^{n_{\mathrm{high}}}.
$$

A factor is replaced by one when its reference stress is zero. By default
$p_s=p_c$; with <code>use_normal_memory_for_dilation_support = true</code>,
$p_s=p_m$.

### 6.1 Direct incremental dilation

With <code>use_irreversible_dilation_target = false</code>,

$$
\Delta g_{n,\mathrm{raw}}^p
=d\,S_p\tan\psi(s_{n+1})\,\Delta\gamma.
$$

The factor $d$ restricts dilation to the damaged frictional area.

### 6.2 Irreversible target dilation

With <code>use_irreversible_dilation_target = true</code>, define

$$
D(s)
=d_{\max}
\left\{
1-\exp\left[
-\left(\frac{s}{L_d}\right)^{m_d}
\right]
\right\}.
$$

Then

$$
g_{n,\mathrm{tar}}^p=dS_pD(s_{n+1}),
$$

$$
\Delta g_{n,\mathrm{raw}}^p
=
\max_{\epsilon_g}
\left(
g_{n,n}^p,g_{n,\mathrm{tar}}^p
\right)
-g_{n,n}^p.
$$

In target mode, the specified dilation angles do not determine the normal plastic
increment; $d_{\max}$, $L_d$, and $m_d$ replace the direct angle law.

### 6.3 Dissipation limiter

The code constrains work against the contact pressure by the Coulomb friction-work
budget

$$
p_c\Delta g_n^p
\le
(1-\epsilon_D)dY\Delta\gamma.
$$

It computes

$$
\Delta g_{n,\mathrm{adm}}^p
=
\frac{(1-\epsilon_D)dY\Delta\gamma}
{p_c+\epsilon_\sigma},
$$

and applies

$$
\boxed{
\Delta g_n^p
=
\min
\left(
\Delta g_{n,\mathrm{raw}}^p,
\Delta g_{n,\mathrm{adm}}^p
\right)
}.
$$

If either candidate is not positive, the increment is set to zero. The corresponding
frictional-dilatant dissipation is

$$
\Delta\mathcal D_{fd}
=dY\Delta\gamma-p_c\Delta g_n^p
\ge0.
$$

The formulation is non-associative because the normal plastic flow is governed by a
separate dilation law rather than the gradient of the Mohr--Coulomb yield function.
When the limiter is active and cohesion is negligible,

$$
\frac{\Delta g_n^p}{\Delta\gamma}
\approx(1-\epsilon_D)\mu.
$$

Changing the nominal dilation angle then has no mechanical effect.

## 7. Tangential return mapping

The damaged-area trial traction is

$$
\boldsymbol t_t^{\mathrm{tr}}
=
K_t
\left(
\boldsymbol g_{t,n+1}-\boldsymbol g_{t,n}^p
\right),
$$

$$
\tau_{\mathrm{tr}}
=\lVert\boldsymbol t_t^{\mathrm{tr}}\rVert,
\qquad
\boldsymbol m
=
\frac{\boldsymbol t_t^{\mathrm{tr}}}
{\tau_{\mathrm{tr}}}.
$$

For the core rate-independent law,

$$
F^{\mathrm{tr}}=\tau_{\mathrm{tr}}-Y.
$$

If $F^{\mathrm{tr}}\le0$, the interface sticks and
$\boldsymbol g_{t,n+1}^p=\boldsymbol g_{t,n}^p$.

If $F^{\mathrm{tr}}>0$, the local unknowns are
$(\Delta\gamma,g_{n,n+1}^p)$. They solve

$$
\boxed{
F_1
=
\tau_{\mathrm{tr}}
-K_t\Delta\gamma
-Y(\Delta\gamma,g_{n,n+1}^p)
-\frac{\eta_t}{\Delta t_s}\Delta\gamma
-\tau_{\mathrm{rs}}
=0
},
$$

$$
\boxed{
F_2
=
g_{n,n+1}^p-g_{n,n}^p
-\Delta g_n^p(\Delta\gamma,g_{n,n+1}^p)
=0
}.
$$

The updated damaged-area shear traction is

$$
\boldsymbol t_t^{\mathrm{fr}}
=
K_t
\left(
\boldsymbol g_{t,n+1}
-\boldsymbol g_{t,n}^p
-\Delta\gamma\boldsymbol m
\right).
$$

The viscous term uses the material substep duration, not the full global time step. It
is a numerical overstress regularization and does not enter the physical friction-work
budget used by the dilation limiter.

### 7.1 Optional referenced rate-and-state perturbation

When enabled,

$$
V=\frac{\Delta\gamma}{\Delta t_s},
\qquad
z=
\frac{V}{2V_0}
\left(
\frac{V_0\theta_n}{D_c}
\right)^{b/a}.
$$

The added shear resistance is

$$
\tau_{\mathrm{rs}}
=
p_m a
\left[
\operatorname{asinh}(z)
-\operatorname{asinh}(1/2)
\right].
$$

The reference subtraction makes this term vanish at steady sliding
$V=V_0$, $\theta=D_c/V_0$. If
<code>rate_and_state_nonnegative = true</code>, the bracketed friction
coefficient is clamped at zero.

The state variable follows the aging law

$$
\dot\theta=1-\frac{V\theta}{D_c}.
$$

For constant $V$ over the substep, the implemented exact update is

$$
\theta_{n+1}
=
\theta_ne^{-x}
+\Delta t_s\frac{1-e^{-x}}{x},
\qquad
x=\frac{\Delta\gamma}{D_c},
$$

with a series expansion as $x\rightarrow0$.

## 8. Total local traction

The implemented parallel mixture is

$$
\boxed{
t_n=t_n^{\mathrm{coh}}-p_c
},
$$

$$
\boxed{
\boldsymbol t_t
=
\boldsymbol t_t^{\mathrm{coh}}
+d\,\boldsymbol t_t^{\mathrm{fr}}
}.
$$

Therefore:

- an intact interface, $d=0$, has cohesive shear resistance but no frictional
  shear contribution;
- a fully damaged interface, $d=1$, has no cohesive traction and carries the full
  frictional branch;
- partial damage gives a continuous parallel mixture; and
- compressive contact acts over the full interface in every case.

The material returns

$$
\Delta\boldsymbol t
=\boldsymbol t_{n+1}-\boldsymbol t_n.
$$

The CZM transformation rotates this local traction to the global frame, and the
mechanical interface kernel assembles equal and opposite contributions on the two faces.

## 9. Fluid-pressure coupling

Fluid pressure is not explicit in the two local return-map residuals. In the Orca input
decks, a separate pressure interface kernel applies an opening traction

$$
\boldsymbol t_p=-\alpha_p p_f\boldsymbol n.
$$

This load changes the solved $g_n$, which changes $p_c$, which changes the Coulomb
strength. Effective-stress coupling therefore occurs through the global mechanical
equilibrium. This material does not internally substitute
$p_c=\sigma_n-\alpha_pp_f$.

The material can also export

$$
\alpha_A
=
\frac{\sigma_A}{\sigma_A+p_c}
$$

when the power-law closure or state-dependent-area option is active; otherwise it
exports $\alpha_A=1$. Here $\sigma_A$ is
<code>fault_pressure_area_reference_stress</code>.

This exported property is not automatically used by
<code>OrcaCZMFluidPressureInterfaceKernel</code>, which accepts a constant
<code>pressure_traction_coefficient</code>. A manuscript must describe the
coefficient actually connected in the input file.

## 10. Output-only reversible opening

The optional reversible normal opening is deliberately excluded from equilibrium. With
an activation slip $s_a>0$, define

$$
A(s)
=
1-\exp
\left[
-\left(
\frac{\langle s-s_a\rangle_+}{L_a}
\right)^{m_a}
\right].
$$

If no activation slip is specified, $A=1$. The raw output is

$$
d_{\mathrm{rev}}^{\mathrm{raw}}
=
C_nA(s)
\langle\sigma_{\mathrm{ref}}-p_c\rangle_+.
$$

An optional retention fraction preserves part of the maximum reversible opening during
reclosure. The reported total is

$$
g_{n,\mathrm{reported}}
=g_n^p+d_{\mathrm{rev}}.
$$

Neither $d_{\mathrm{rev}}$ nor its history enters the contact residual, return-map
Jacobian, or hydraulic aperture. It is an output reconstruction, not a mechanical
constitutive deformation.

## 11. Local solution algorithm

For each global displacement-jump increment, the material:

1. splits the path at cohesive initiation, cohesive failure, and contact
   opening/closure events;
2. updates cohesive history and damage on each substep;
3. selects open, stick, or slip;
4. for slip, solves the coupled $2\times2$ system
   $(F_1,F_2)=\boldsymbol0$ by Newton iteration with a line search;
5. enforces
   $0\le\Delta\gamma\le\tau_{\mathrm{tr}}/K_t$ and
   $g_{n,n+1}^p\ge g_{n,n}^p$;
6. bisects a material substep if the local solve fails;
7. applies a tolerance-limited AD corrector to recover the implicit sensitivities of
   $\Delta\gamma$ and $g_n^p$; and
8. throws a recoverable material exception after exhausting the permitted bisections,
   so the global time stepper can reduce $\Delta t$ and retry.

The exported state code is 0 for stick, 2 for slip, and 3 for open.

## 12. Paper-ready core formulation

The following paragraph describes the central law without the optional memory,
rate-and-state, and output-only extensions:

> The fracture was represented by a zero-thickness cohesive-contact interface with
> opening-positive jump $\boldsymbol g=(g_n,\boldsymbol g_t)$. The traction was the
> parallel mixture
> $t_n=(1-d)K_c\langle g_n-g_{n,\mathrm{old}}^p\rangle_+-p_c$ and
> $\boldsymbol t_t=(1-d)K_c\beta_c^2\boldsymbol g_t+
> dK_t(\boldsymbol g_t-\boldsymbol g_t^p)$, where $d$ is irreversible mixed-mode
> cohesive damage. Normal compression was unilateral. In the nonlinear-closure option,
> $p_c=K_{ni}V_m[c/(V_m-c)]^{1/p_n}$, with
> $c=\langle g_n^p-g_n+c_0\rangle_+$; otherwise
> $p_c=K_n\langle g_n^p-g_n\rangle_+$. Sliding obeyed the
> roughness-dependent Mohr--Coulomb condition
> $F=\lVert\boldsymbol t_t^{\mathrm{fr}}\rVert-
> [c_f(R)+\mu(R)p_c]\le0$, where
> $R=R_r+(R_0-R_r)e^{-s/L_R}$,
> $\mu=\mu_s+(\mu_r-\mu_s)[(R-R_r)/(1-R_r)]^{m_\mu}$, and the
> cohesion intercept was interpolated analogously. The cumulative plastic slip
> $s=\sum\Delta\gamma$ evolved with
> $\Delta\boldsymbol g_t^p=\Delta\gamma\boldsymbol m$. A separate
> non-associative dilation law prescribed
> $\Delta g_{n,\mathrm{raw}}^p=dS_p\tan\psi(s)\Delta\gamma$, and the
> realized opening was limited so that
> $p_c\Delta g_n^p\le(1-\epsilon_D)dY\Delta\gamma$. The coupled plastic
> multiplier and normal plastic opening were obtained from a local two-variable
> Newton return map. Fracture pressure was applied as a separate opening traction
> in the global interface equilibrium.

For a pre-existing joint, remove the cohesive terms and state explicitly that
<code>enable_tensile_cohesion = false</code>, so $d=1$ from the start.

## 13. Implementation cautions

1. The power-law closure and exact inverse in Section 3.2 are the implemented
   equations. A different inverse expression currently appears in the broad theory
   manual and should not be cited as this class's law without correction.
2. The code interpolates $\psi$ in degrees and then takes its tangent. Interpolating
   $\tan\psi$ would be a different law.
3. The dilation budget uses Coulomb work $dY\Delta\gamma$, not total shear work.
   Viscous overstress and rate-and-state resistance do not enlarge the admissible
   dilation.
4. In irreversible target mode, the target law replaces angle-based dilation.
5. <code>reversible_normal_opening</code> and
   <code>normal_opening_total</code> are output-only.
6. <code>fault_pressure_area_coefficient</code> affects mechanics only if another
   object is explicitly configured to consume it.
7. Because $d$ weights the total frictional traction but not the internal branch
   strength, paper equations should distinguish branch traction from total traction
   during partial cohesive damage.
