# Hosseini, Paluszny & Zimmerman (2025) — reading notes, technical foundations, and what to take from it

> Hosseini, N., Paluszny, A., & Zimmerman, R. W. (2025). Dynamics of fluid-driven slip on a 3D
> heterogeneous fault with rate-and-state friction. *JGR: Solid Earth*, 130, e2025JB031221.
> Imperial College London. Code: Imperial College Geomechanics Toolkit (ICGT), Zenodo.

Prepared 2026-08-07. Three purposes: (1) summarise the paper, (2) build the technical
foundations behind it to comprehensive-exam depth, (3) extract what is transferable to your own
writing and what would make a paper 2 of your own genuinely distinct rather than derivative.

---

# Part 1 — What the paper is

## 1.1 One paragraph

A 3D quasi-dynamic finite-element model of fluid-driven slip on a *heterogeneous* fault:
velocity-weakening (VW) asperities embedded in a velocity-strengthening (VS) creeping matrix,
with rate-and-state friction, solved monolithically with fault fluid flow. The numerical
contributions are an augmented-Lagrangian treatment of the frictional contact constraints in 3D
and a stick-predictor/slip-corrector return map for RSF with a consistent Jacobian. The physical
result is a **geometry–material diagram**: the seismic behaviour of the whole fault — isolated
events versus cascading sequences — is organised by just two measurable parameters, the areal
density $\rho_a$ of asperities and the friction ratio $(a/b)_s$ of the creeping barriers between
them.

## 1.2 The chain of argument

1. Fluid injection raises $p_f$ on the fault, lowering $\sigma'_n$.
2. An **aseismic slip front** nucleates and propagates *ahead of* the pressure front. How far ahead
   is controlled by $(a-b)_s$ of the creeping region.
3. When that aseismic front reaches a VW asperity, it destabilises it → a co-seismic event.
4. The co-seismic stress drop imposes a Coulomb stress change $\Delta\mathrm{CFS}$ on the
   surrounding creeping barrier, driving **post-seismic slip** (afterslip).
5. That afterslip loads *neighbouring* asperities and can trigger them → **secondary events,
   cascading**.
6. Whether the cascade happens is set by how far the afterslip reaches (governed by $(a/b)_s$)
   relative to how far apart the asperities are (governed by $\rho_a$). Hence the diagram.

That is a clean, self-contained mechanical story, and the paper's structure follows it exactly:
§4.1 the front, §4.2 one asperity, §4.2.1 the afterslip, §4.3 many asperities. **Note this
structure — it is worth copying.** Each section adds exactly one ingredient and nothing else.

## 1.3 Headline numbers

| Quantity | Value |
|---|---|
| Fault | circular strike-slip, $D = 600$ m, in a 900 m cube at 3 km depth, plane rotated 30° |
| Elastic | $G = 20$ GPa, $\nu = 0.25$ |
| Stress | $\sigma_v = 45$, $\sigma_H = 60.1$, $\sigma_h = 19.33$ MPa; on the fault $\tau_0 = 17.65$, $\sigma_0 = 29.52$ MPa |
| Criticality | $\tau_0/(\mu_0\sigma_0) = 0.9965$ — deliberately critically stressed |
| Friction | $\mu_0 = 0.6$, $D_c = 0.2$ mm, $V_0 = 10^{-9}$ m/s |
| Asperities | $a_w = 0.003$, $b_w = 0.008$, so $(a-b)_w = -0.005$; $R_a = 30$ m |
| Barriers | $a_s = 0.003$; $b_s \in \{0.001, 0.002, 0.0029\}$ → $(a/b)_s \in \{3.0, 1.5, 1.035\}$ |
| Injection | $\dot p = 10$ MPa/day $= 115.74$ Pa/s at the fault centre; $D_f = 0.1$ m²/s |
| Damping | $\xi = 330$ MPa·s/m, i.e. $\beta_\xi = 0.01$ — **100× the physical value** |
| Mesh | $\Delta x = 10$ m, second-order interpolation; $L_{cr} = 27.2$ m |
| Penalty | $\epsilon_T = 2$ GPa/m, $\epsilon_N = 2000\,\epsilon_T$ |

---

# Part 2 — My assessment

## 2.1 Is this a good template for your paper 2?

**Yes, with one important caveat.** The strengths worth emulating:

- The **two-parameter phase diagram** is the paper's real product. It converts a
  high-dimensional parameter study into a single figure a reader remembers. Numerical papers that
  present "we ran 20 cases, here are 20 figures" are forgettable; this one is not.
- It **derives analytical scalings and then tests the numerics against them** —
  $r_a/r_p \propto 1/\sqrt{(a-b)_s}$, $\Delta\mathrm{CFS}[R]$, the Perfettini–Avouac afterslip law.
  This is what separates a *mechanistic* study from a parameter sweep. A reviewer who sees a model
  reproduce an independent analytical prediction stops asking whether the code works.
- It **states numerical admissibility as inequalities**, not as reassurance: $\epsilon_T > \epsilon_{cr}$,
  $\Delta x < L_{cr}$, $\Delta t < \beta_t D_c/V_{\max}$. Every one is checkable.
- It **verifies against a community benchmark (SCEC SEAS) before doing any science**, and cross-checks
  against an independent code (EQquasi).
- It is **honest about a regularisation that distorts the answer**: $\beta_\xi = 0.01$ makes the
  co-seismic duration 782 s against a physical ~8 s, and the paper says outright that event timing
  "should not be compared with real data".

**The caveat.** If you write the same paper with a different code, you have written a replication.
The gap you should occupy is in §2.3.

## 2.2 What the paper does *not* do — and this is your opening

Read §2.2 of the paper carefully:

> "The fault opening in the above equation is equivalent to $h_f = g_N + h_{f0}$, and in the case
> of normal contact ($g_N = 0$), it is equal to a residual opening, $h_{f0}$, which will be assumed
> to be constant."

**The fault permeability does not evolve with slip.** In contact, $h_f = h_{f0} = $ constant, so
$k_f = h_{f0}^2/12$ is frozen. There is no dilation, no gouge, no shear-enhanced permeability. The
hydraulics is a *one-way* driver: pressure changes stress, but slip never changes the flow.

This is precisely the coupling your first paper spends its entire length validating. Ye & Ghassemi
(2018) exists *because* shear slip enhances permeability — the SW-T1 aperture triples across the
slip event, and the flow rate rises by a factor of 117. A model in which the fault conductivity is
constant cannot represent that at all.

Three further gaps, in descending order of how much a committee will care:

1. **The rock matrix is impermeable.** "Fluid diffusion into surrounding rock is ignored." All
   fluid stays on the fault. Leak-off would blunt the pressure front and change $r_a/r_p$.
2. **No explicit dilation.** The paper's Appendix B shows dilation appears *implicitly*, as a
   consequence of the ratio $\epsilon_T/\epsilon_N$ of the two penalty factors. That is defensible
   — the appendix argues penalty factors represent physical joint stiffnesses — but it means the
   dilation angle is not a constitutive property you can measure and set. In your framework it is,
   and it is bounded by the second law.
3. **Idealised heterogeneity.** Asperities are equal-radius circles on a regular grid. Real fault
   heterogeneity is closer to power-law. The paper acknowledges this ("a simplified idealized
   model").

## 2.3 The paper 2 I would write

> **Shear-enhanced permeability changes the aseismic-slip-front and cascading behaviour that
> constant-aperture models predict.**

The pitch writes itself, and it makes paper 1 load-bearing rather than merely prior:

- Paper 1 validates, against four laboratory specimens spanning JRC 1.19–15.32, a fracture
  constitutive law in which dilation is thermodynamically bounded, kinematically routed, and feeds
  a hydraulic aperture that reproduces the measured permeability enhancement.
- Paper 2 takes *that validated law* to the 3D heterogeneous fault problem, and asks what changes
  when the fault's conductivity is allowed to respond to slip.

Specific, testable hypotheses you would be going after:

1. **The aseismic front should accelerate and change shape.** Slip dilates the fault behind the
   front, raising $k_f$ there, which raises the local hydraulic diffusivity $D_f = k_f/(\mu c_f)$
   and lets pressure chase the front faster. Hosseini finds $r_a/r_p \approx 1.5$ with constant
   $k_f$; with slip-enhanced $k_f$ the ratio should *fall* toward 1 as the pressure front catches
   up. That is a sharp, falsifiable prediction.
2. **Cascading should be easier.** Post-seismic slip on a barrier dilates it, raising conductivity
   between asperities, delivering pressure to the neighbour faster than diffusion alone. The
   geometry–material diagram should shift: the cascading region should expand toward lower
   $\rho_a$.
3. **Gouge should introduce irreversibility the constant-aperture model cannot have.** Your
   $a_{\rm gouge}(s)$ term means a barrier that has slipped does not recover its conductivity.
   Sequences should therefore depend on order, not just on parameters — a genuinely new degree of
   freedom.
4. **The dissipation bound should bite differently at field scale.** $\tan\psi \le (1-\epsilon_D)\mu$
   with $\mu \approx 0.6$ allows $\psi \le 31°$. Whether realised dilation saturates at the bound
   on a 600 m fault is an open question worth answering.

You would also be able to say something Hosseini cannot: your constitutive law has been validated
against measurements, not only against a benchmark and analytical limits.

**Honest risk.** RSF is not currently in your validated law family — ORCA has rate-and-state
parameters (`rate_and_state_a`, `_b`, `_theta0`) in the compression–tensile law and a dedicated
BB/RSF material, but your Ye & Ghassemi work used Coulomb and Barton–Bandis envelopes. Adding RSF,
verifying it against SEAS, *and* coupling it to the aperture model is a substantial piece of work.
Scope it deliberately; do not discover halfway through that the SEAS benchmark alone is a paper.

---

# Part 3 — Technical foundations for the comprehensive exam

This part assumes you will be asked to derive, not merely recall.

## 3.1 Rate-and-state friction

### 3.1.1 Where it comes from

Dieterich (1979) and Ruina (1983) observed in laboratory sliding that the friction coefficient is
not constant but depends on the sliding rate $V$ and on the *history* of contact, encoded in a
state variable $\theta$ with units of time. Two effects:

- **Direct effect.** An instantaneous step increase in $V$ produces an instantaneous *increase* in
  friction, with magnitude $a\ln(V_2/V_1)$. Physically: faster sliding means less time for contact
  junctions to grow, but the instantaneous response is dominated by the rate-dependence of the
  shear strength of the junctions themselves.
- **Evolution effect.** Friction then relaxes toward a new steady state over a slip distance
  $D_c$, with magnitude $b\ln(\cdot)$. Physically: the population of contacts re-equilibrates.

The steady-state friction is

$$
\mu_{ss}(V) = \mu_0 + (a-b)\ln\!\left(\frac{V}{V_0}\right),
$$

and the sign of $a-b$ is the whole game:

| | | Behaviour |
|---|---|---|
| $a - b > 0$ | velocity **strengthening** (VS) | stable, creeping. Perturbations decay. |
| $a - b < 0$ | velocity **weakening** (VW) | conditionally unstable. Can nucleate earthquakes. |

**This is the single most important fact in the paper.** The fault is VW patches (asperities, can
host earthquakes) in a VS matrix (barriers, creep).

### 3.1.2 The regularised form

The classical law $\mu = \mu_0 + a\ln(V/V_0) + b\ln(V_0\theta/D_c)$ is singular at $V = 0$ — the
logarithm diverges. Since a quasi-static simulation spends most of its time with locked patches at
$V = 0$, this is fatal. The regularised form used (Andrés et al., 2019; equation 2 in the paper) is

$$
\boxed{\;\mu[V,\theta] = \mu_0 + a\ln\!\left(\frac{V + V_0}{V_0}\right) + b\ln\!\left(\frac{\theta}{\theta_0}\right)\;}
$$

with $\theta_0 = D_c/V_0$ the steady-state value at the reference rate. At $V = 0$ this gives
$\mu = \mu_0$ exactly, which is why the paper can say "the steady-state friction coefficient is
equal to the static friction coefficient when the slip rate vanishes."

**Interpretation to have ready:** the regularisation says that a fault which is stationary at the
macroscopic level is still creeping microscopically at the reference speed $V_0$. It is a physical
statement, not only a numerical patch.

### 3.1.3 The aging law

$$
\boxed{\;\dot\theta = 1 - \frac{(V + V_0)\theta}{D_c},\qquad \theta[0] = \theta_0\;}
$$

Note the same $V \to V + V_0$ shift. **Consequence you must be able to state:** *the state variable
evolves even when the fault is not slipping.* At $V = 0$, $\dot\theta = 1 - V_0\theta/D_c$, which is
zero only at $\theta = \theta_0$. A locked patch is therefore not frozen — it heals, and its
strength grows. This is why the return map (§3.4) must advance $\theta$ in the *stick* predictor,
not only in the slip corrector. Missing this is a classic implementation bug.

**Aging vs slip law.** The alternative "slip law" is
$\dot\theta = -(V\theta/D_c)\ln(V\theta/D_c)$. Differences to know:

| | Aging (Dieterich) | Slip (Ruina) |
|---|---|---|
| Healing at $V=0$ | yes, $\theta$ grows linearly with time | no evolution without slip |
| Symmetry of step response | asymmetric (up-step vs down-step differ) | symmetric |
| Laboratory agreement | better for hold-and-slide (healing) tests | better for velocity-step tests |
| Nucleation | larger nucleation zones | smaller |

The paper uses **aging**, which is also what the SEAS benchmarks specify.

### 3.1.4 $D_c$, the critical slip distance

The distance over which the contact population is renewed. Laboratory values are $\mu$m to tens of
$\mu$m; the paper uses 0.2 mm, and field-inferred values are far larger. This scale-dependence of
$D_c$ is a known open problem — be ready for the question "why is your $D_c$ 0.2 mm when the lab
says 10 $\mu$m?" The honest answer is that $D_c$ sets the nucleation size (§3.5), and a laboratory
$D_c$ would demand a mesh no one can afford; the value is chosen to make nucleation resolvable and
the consequences must be stated.

## 3.2 The quasi-dynamic approximation and radiation damping

A fully dynamic simulation solves the elastodynamic wave equation and is expensive. The
**quasi-dynamic** approximation replaces inertia with a local damping term that mimics the energy
radiated as seismic waves:

$$
\boxed{\;\xi = \frac{G}{2 v_s}\;}\qquad\text{(Rice, 1993)}
$$

appearing in the failure criterion as $-\xi V$:

$$
f[\mathbf{t}_T, t'_N; V, \theta] = \lVert \mathbf{t}_T \rVert + \mu[V,\theta]\,t'_N - \xi V .
$$

(Recall the paper's sign convention: compression negative, so $t'_N < 0$ and $\mu t'_N$ is a
negative strength contribution.) The term acts as a velocity-dependent cohesion that prevents
unbounded slip rates.

**The honest caveat, which the paper states and you should too.** With $\beta_\xi = 1$ (physical),
$\xi \approx 3.3$ MPa·s/m and slip rates reach ~0.01 m/s, requiring tiny time steps. The paper uses
$\beta_\xi = 0.01$, i.e. $\xi = 330$ MPa·s/m — 100× over-damped — capping slip rate at $10^{-4}$
m/s. Consequences:

- co-seismic duration 782 s instead of ~8 s;
- Lapusta & Liu (2009) showed quasi-dynamic solutions with different $\beta_\xi$ *rescale* in time
  as $\beta_\xi t$, so the distortion is systematic rather than random;
- the paper therefore restricts itself to statements about *sequence* and *interaction*, and
  explicitly forbids comparing event timing to data.

**Exam question to expect:** "Your co-seismic durations are two orders of magnitude too long. Why
should I believe anything about the cascade?" Answer: because the cascade is controlled by the
*post-seismic* stage, where slip rates are of order the aseismic rate and radiation damping is
negligible — the paper says exactly this at the end of §4.2.1. That is the defensible boundary.

## 3.3 Enforcing contact: penalty, Lagrange, augmented Lagrangian

The Karush–Kuhn–Tucker conditions for unilateral contact are

$$
g_N \geq 0,\qquad t'_N \leq 0,\qquad g_N t'_N = 0,
$$

and for friction, $V \geq 0$, $f \leq 0$, $Vf = 0$.

| Method | Constraint | Extra unknowns | Conditioning | Penalty sensitivity |
|---|---|---|---|---|
| **Penalty** | approximate ($t'_N = \epsilon_N g_N$, small interpenetration) | none | degrades as $\epsilon_N \to \infty$ | accuracy depends on $\epsilon_N$ |
| **Lagrange multiplier** | exact | $\lambda_N$, $\boldsymbol{\lambda}_T$ | saddle-point system, can oscillate | none |
| **Augmented Lagrangian** | exact, in the limit of the augmentation loop | none in the linear solve | good | **result independent of $\epsilon$** |

The augmented form (Simo & Laursen, 1992) is

$$
t'_N = \lambda_N + \epsilon_N g_N,
\qquad
\dot{\mathbf{t}}_T = \dot{\boldsymbol\lambda}_T + \epsilon_T(\dot{\mathbf{g}}_T - \dot\gamma\mathbf{m}),
$$

solved by an **Uzawa-type outer loop** (their Algorithm 1):

1. Fix $\lambda$; solve the nonlinear system for $\mathbf{u}, p_f$.
2. Check $|g_N| < \mathrm{TOL}_N$ and $|\Delta\mathbf{g}_T - \Delta\gamma\mathbf{m}| < \mathrm{TOL}_T$.
3. If not converged, update $\lambda_N \leftarrow \lambda_N + \epsilon_N g_N$,
   $\boldsymbol\lambda_T \leftarrow \boldsymbol\lambda_T + \epsilon_T(\Delta\mathbf{g}_T - \Delta\gamma\mathbf{m})$,
   and repeat.

At convergence the multipliers carry the full traction and the penalty terms vanish — which is what
makes the answer independent of $\epsilon$.

**Contrast with your own code, which you will be asked about.** ORCA uses a *penalty* method with
smoothed active sets. The trade you accepted is: no outer loop (cheaper per step, and the smoothing
gives a semismooth Jacobian Newton can use), at the cost of a small interpenetration and a result
that depends weakly on $k_n$. The counter-argument you can make is that your normal response is not
a numerical penalty at all — it is a *physical* Bandis hyperbolic closure law with a measured
$K_{ni}$ and $v_m$, so the "penalty" is a constitutive stiffness, and driving it to infinity would
be wrong. Interestingly, **Hosseini's Appendix B ends up at the same place**: "penalty factors must
not be considered merely as numerical constants; they can represent the physical normal and
tangential stiffness of the fault."

## 3.4 The return map for rate-and-state friction

This is where the numerical contribution sits, and it is the part most likely to be probed.

### 3.4.1 Incremental forms

Backward Euler on slip and on the aging law:

$$
\gamma^{n+1} = \gamma^n + \Delta t\, V^{n+1}
\;\Rightarrow\;
\Delta\gamma = V^{n+1}\Delta t ,
$$

$$
\theta^{n+1} = \frac{\theta^n + \Delta t}{1 + \dfrac{\Delta t}{D_c}\bar V^{n+1}},
\qquad \bar V = V + V_0 .
$$

**The key structural observation:** $\theta^{n+1}$ is a closed-form function of $V^{n+1}$ alone.
Therefore $\mu[V^{n+1}]$ is a function of one unknown, and the whole local problem collapses to a
*scalar* root-find in $V^{n+1}$. This is why the method is efficient, and it is the answer to
"why don't you need a coupled 2×2 local system like other formulations?"

### 3.4.2 Stick predictor

Assume no slip: $V^{tr} = 0$, $\Delta\gamma^{tr} = 0$, and — critically —

$$
\theta^{tr} = \frac{\theta_0(\theta^n + \Delta t)}{\theta_0 + \Delta t} \neq \theta^n .
$$

The state **still evolves**. The trial shear traction is
$\mathbf{t}_T^{tr} = \mathbf{t}_T^n + \Delta\boldsymbol\lambda_T + \epsilon_T\Delta\mathbf{g}_T$.
If $f[\mathbf{t}_T^{tr}, t'^{n+1}_N; 0, \theta^{tr}] \leq 0$, accept the stick state.

### 3.4.3 Slip corrector

Otherwise solve the scalar equation

$$
\boxed{\;
f[V] = \lVert \mathbf{t}_T^{tr} - \epsilon_T \Delta t\, V^{n+1}\mathbf{m}\rVert
 + \mu[V^{n+1}]\, t'^{n+1}_N - \xi V^{n+1} = 0 \;}
$$

by Newton–Raphson, with

$$
f'[V] = -\epsilon_T\Delta t + \mu'[V]\,t'^{n+1}_N - \xi,
\qquad
\mu'[V] = \frac{a}{\bar V^{n+1}} - \frac{b\,\Delta t}{D_c + \Delta t\,\bar V^{n+1}} .
$$

Started from $V^{(0)} = 0$.

### 3.4.4 The convergence condition — derive this

Newton converges monotonically for arbitrary $\Delta t$ **iff $f' < 0$**. Examine the three terms:

- $-\epsilon_T\Delta t < 0$ always;
- $-\xi < 0$ always;
- $\mu' t'_N$: with $t'_N < 0$ in compression, this is $-|t'_N|\mu'$. So it is negative when
  $\mu' > 0$ and **positive when $\mu' < 0$**.

For a VS fault $\mu' > 0$ and convergence is unconditional. For a **VW** fault $\mu'$ can be
negative, and requiring $f' < 0$ in the limit $\xi \to 0$ gives

$$
\boxed{\;\epsilon_T > \frac{|(a-b)\,t'_N|}{D_c} \equiv \epsilon_{cr}\;}
$$

the **critical stiffness**. Take $\epsilon_T = G/\Delta x$ (the natural elastic scaling of a cell)
and this becomes a *mesh* requirement:

$$
\boxed{\;\Delta x < L_{cr} = \frac{G}{\epsilon_{cr}} = \frac{G D_c}{|(a-b)\,t'_N|}\;}
$$

**This is the single most exam-worthy derivation in the paper.** It says: the mesh must resolve
the length scale at which the elastic stiffness of a cell equals the weakening rate of the friction
law. Coarser than that and the numerical problem is not merely inaccurate — it is *ill-posed*, and
no amount of time-step reduction rescues it.

In the paper: $L_{cr} = 27.2$ m, $\Delta x = 10$ m. Satisfied with margin.

### 3.4.5 The other two length/time criteria

**Cohesive zone.** Independently, the mesh must resolve the process zone at the rupture tip
(Garagash, 2021):

$$
L_{co} = \frac{G D_c}{b\,|t'_N|},
$$

and the paper's convergence study varies $\Delta x/L_{co}$ from 0.1 to 0.6 and finds <5 %
difference in slip (their Figure 2). Note $L_{co} \le L_{cr}$ whenever $b \ge |a-b|$, so the
cohesive-zone condition is usually the binding one.

**Time step.** Following Lapusta & Liu (2009), Lapusta et al. (2000):

$$
\Delta t < \beta_t\,\frac{D_c}{V_{\max}},\qquad \beta_t < 0.25 ,
$$

i.e. slip in one step must not exceed a fraction of $D_c$ — otherwise the state variable jumps
across its own evolution scale. And to resolve dynamic rupture propagation,
$\Delta t_{\min} = 0.3\,\Delta x/(\beta_\xi v_s)$.

**Memorise the trio.** A committee asking "how do you know your simulation is resolved?" is asking
for exactly these three, and the answer "we did a mesh convergence study" alone is weak.

## 3.5 Nucleation length scales

Several appear; keep them straight.

| Symbol | Name | Expression | Meaning |
|---|---|---|---|
| $L_{co}$ | cohesive zone | $GD_c/(b\,\sigma'_n)$ | size of the process zone at the tip |
| $L_{cr}$ | critical stiffness length | $GD_c/(|a-b|\sigma'_n)$ | below this the return map is ill-posed |
| $R_\infty$ | 3D nucleation radius (upper bound) | $\dfrac{\pi}{4}\left(\dfrac{b_w}{(b-a)_w}\right)^2 L_{co}$ | largest nucleation patch assuming steady-state friction behind the tip |

The paper's use: $R_a = 30$ m against $R_\infty = 34$ m, so an asperity is *just* large enough to
host an event. It cites Cattania & Segall (2019): for $R_a > 6R_\infty$, asperities show complex
cycles of partial and full ruptures. **Design insight worth stealing:** they deliberately sized the
asperity near the nucleation limit so that each asperity produces one clean event, isolating the
*interaction* physics they wanted to study from the *intra-asperity* complexity they did not.

## 3.6 Fluid flow along the fault

Mass balance on the fault surface, with $h_f$ the opening:

$$
\frac{\partial}{\partial t}\left(h_f\rho_f\right) + \nabla\cdot\left(h_f\rho_f\mathbf{v}_f\right) = 0,
\qquad
\mathbf{v}_f = -\frac{h_f^2}{12\mu}\nabla p_f \;\;\text{(cubic law)} .
$$

For a slightly compressible fluid this reduces to a diffusion equation

$$
h_f c_f \frac{\partial p_f}{\partial t} - \nabla\cdot\left(\frac{h_f k_f}{\mu}\nabla p_f\right) = 0,
\qquad
k_f = \frac{h_f^2}{12},
\qquad
D_f = \frac{k_f}{\mu c_f}.
$$

**This is the same Reynolds/cubic-law formulation as in your own model** — compare §3.6 of your
manuscript. The difference, as flagged in §2.2 above, is that Hosseini freezes $h_f = h_{f0}$ in
contact while yours lets $a_h$ evolve with dilation and gouge.

Note also the different aperture philosophy: they use one opening $h_f$ for both mechanics and
hydraulics; you distinguish mechanical $a_m$ from hydraulic $a_h$ with a propping coefficient
$\chi$. Yours is the more defensible position (a real fracture has contact patches and tortuosity,
so $a_h < a_m$ always) and is worth defending explicitly if compared.

## 3.7 The aseismic slip front and the stress–injection parameter

### 3.7.1 The central observation

The aseismic slip front **outruns** the pore-pressure front: $r_a > r_p$. This is not obvious —
naively, slip should follow pressure. The reason is elastic stress transfer: slip at a point
loads the surrounding fault, and if the fault is close to failure, that transferred stress is
enough to trigger slip beyond where the pressure has reached.

Confirmed experimentally by Guglielmi et al. (2015) and analysed by Bhattacharya & Viesca (2019).

### 3.7.2 The controlling parameter

$$
T = \frac{(\mu_{ss} - \mu_0)\,\sigma_0}{\mu_{ss}\,\Delta p^{*}},
\qquad
\mu_{ss} = \mu_0 + (a-b)\ln(1 + V_a/V_0),
$$

with $\Delta p^{*}$ a characteristic pressure rise, taken as the rise at $r \approx \sqrt{D_f t}$.
For a critically stressed fault ($T < 1$) with negligible surface energy, Sáez et al. (2022) give

$$
\frac{r_a}{r_p} \leq \frac{1}{\sqrt{2T}} .
$$

Paper's numbers: $\Delta p^{*} \sim 1$ MPa, $T \approx 0.22$, so $r_a/r_p \lesssim 1.5$ — which
matches their Figure 3.

**The scaling to remember:** $r_a/r_p \propto 1/\sqrt{(a-b)_s}$. Weakly strengthening barriers
($(a/b)_s \to 1$, i.e. $a-b \to 0$) let the aseismic front run far ahead; strongly strengthening
barriers localise it. As $(a/b)_s \to 1$ the response approaches VW behaviour with runaway rupture
($T \to 0$, $r_a/r_p \to \infty$).

### 3.7.3 Front shape

The slipped region is an **oval elongated along $x'$** (the maximum-shear direction), aspect ratio
~1.15. Sáez et al. (2022) bound it: $1/(1-\nu) = 1.33$ upper, $(3-\nu)/(3-2\nu) = 1.1$ lower. The
paper uses this to explain why later seismic events also expand preferentially along $x'$.

### 3.7.4 Two thresholds worth distinguishing

- $p_{th} = \sigma_0 - \tau_0/\mu_0$: minimum overpressure to trigger slippage assuming constant
  shear stress. Here 0.1 MPa.
- The location of **first** slip is *not* a good indicator of the physical front, because the slip
  profile there is negligible. The paper argues the **maximum shear stress location** is the better
  marker. Useful methodological point — the same care applies to defining "onset" in your own work.

## 3.8 Post-seismic slip and the cascade

### 3.8.1 Coulomb stress change

$\mathrm{CFS} = \tau - \mu\sigma$. Ignoring normal-stress change, $\Delta\mathrm{CFS} \simeq \Delta\tau$.
The paper's fitted distribution, modified from Dieterich (1994):

$$
\boxed{\;\Delta\mathrm{CFS}[R] = \Delta\tau_{cs}\left[\left(\frac{R}{R_a}\right)^3 - 1\right]^{-1},\quad R > R_a\;}
$$

with maximum near $R \approx 2R_a$ giving $\Delta\mathrm{CFS}_{\max} \approx 0.14\,\Delta\tau_{cs}$.

### 3.8.2 Afterslip

Perfettini & Avouac (2004): the slip rate immediately after the co-seismic stage is

$$
V_+ = V_-\exp\!\left(\frac{\Delta\mathrm{CFS}}{a_s\sigma}\right),
$$

the post-seismic duration is $t_r = a_s\sigma/\dot\tau_{ps}$ with
$\dot\tau_{ps} = \dot\tau_0 - \mu\dot\sigma_{inj} = \mu\dot p$ when the background loading rate is
zero, and the spatio-temporal evolution is

$$
\boxed{\;U_{ps}[R,t] = V_- t_r \ln\left[1 + \frac{V_+}{V_-}\left(\exp\!\left(\frac{t}{t_r}\right) - 1\right)\right]\;}
$$

**Note what $\dot\tau_{ps} = \mu\dot p$ means:** in an injection problem with no tectonic loading,
*the injection rate itself sets the afterslip duration*. That is a genuinely nice observation and
distinguishes fluid-driven afterslip from tectonic afterslip.

The migration of a threshold slip level $U_{th} = V_- t_r$ gives

$$
R_{th} = R_a\left(1 - \frac{\Delta\tau_{cs}}{a_s\sigma\,\ln\!\big(F[t]/(e-1)\big)}\right)^{1/3},
\qquad F[t] = \exp(t/t_r) - 1 ,
$$

which accelerates outward and diverges as $t \to t_r$. **This is the trigger mechanism for
secondary events**: when $R_{th}$ reaches a neighbouring asperity, that asperity can fail.

### 3.8.3 Seismic moment

$$
M_0 = G\iint \gamma\, \mathrm{d}\Gamma,
\qquad
M_w = \tfrac{2}{3}\left(\log_{10} M_0 - 9.1\right)\;\;(M_0\text{ in N·m}),
$$

with an event declared when the moment *rate* exceeds
$\dot M_s = G\pi R_a^2 V_s$ at a threshold slip rate $V_s = 0.5\times10^{-4}$ m/s.

**Be ready to be asked why a slip-rate threshold and not a physical criterion.** The honest answer:
in a quasi-dynamic model with artificial damping there is no sharp seismic/aseismic boundary, so a
threshold must be *declared*; the paper says as much ("it is impossible to define a clear
transition point between different stages of a seismic event"). Declaring it explicitly is better
practice than hiding it.

## 3.9 The geometry–material diagram

$$
\rho_a = \frac{\pi R_a^2}{(2R_a + d_a)^2}
$$

Six cases, labelled $Cd_a\mathrm{M}$ where M $\in$ {W, M, S} is the strength of velocity
strengthening. Findings:

- **High density ($\rho_a = 0.35$):** $(a/b)_s$ dominates. Weak strengthening (C30W) → the whole
  fault slips at once, one main shock, all asperities contribute. Strong strengthening (C30S) →
  longer intervals, extended main shock, more isolated behaviour.
- **Low density ($\rho_a = 0.2$):** insensitive to $(a/b)_s$; asperities stay isolated and produce
  independent events.
- **Overall:** higher asperity density + weakly strengthening barriers → cascading and higher
  cumulative moment. Sparse asperities in strongly strengthening rock → isolated events, longer
  recurrence.

The mechanism, stated compactly: **post-seismic slip on the barrier is the messenger.** Its reach
is set by $(a/b)_s$; the distance it must cover is set by $\rho_a$.

## 3.10 Appendix B — implicit dilation, and why it matters to you

This short appendix is the most conceptually interesting part of the paper. Linearising the contact
relations gives

$$
\begin{bmatrix}\Delta t'_N\\ \Delta t_T\end{bmatrix}
=
\begin{bmatrix}\epsilon_N & 0\\ \mathcal{A}\mu\epsilon_N & (1+\mathcal{A})\epsilon_T\end{bmatrix}
\begin{bmatrix}\Delta g_N\\ \Delta g_T\end{bmatrix},
\qquad
\mathcal{A} = \frac{-\epsilon_T}{\epsilon_T + \dfrac{\mathrm{d}\mu}{\mathrm{d}\gamma}|t'_N|} < 0 .
$$

Under **force control** ($\Delta t_T = 0$, normal opening unconstrained),

$$
\boxed{\;\frac{\Delta g_N}{\Delta g_T} = -\frac{1+\mathcal{A}}{\mathcal{A}}\cdot\frac{\epsilon_T}{\mu\epsilon_N} \equiv \tan\psi\;}
$$

an **implicit dilation angle**, arising with no dilation in the constitutive law at all. Behaviour:

- $\mathcal{A} = -1$ exactly (constant friction) → $\tan\psi = 0$, no implicit dilation;
- $\epsilon_T/\epsilon_N \to 0$ → vanishes;
- slip-**weakening** ($\mathrm{d}\mu/\mathrm{d}\gamma < 0$, so $\mathcal{A} < -1$) → **compaction**;
- friction **increase** ($\mathcal{A} > -1$) → dilation.

During a co-seismic event $\mathrm{d}\mu/\mathrm{d}\gamma \to -\infty$, $\mathcal{A} \ll -1$, and
compaction dominates — which explains the abrupt *increase* in effective normal stress and the
"snap-back" in their Figure 5a, contradicting the usual assumption $\sigma' = \sigma_0 - p_f$.

**Why this matters for your defence.** Two things.

1. It is an argument that penalty factors are physical, which supports your use of a Bandis closure
   law as the "penalty".
2. It is also a **warning**: a spurious dilation/compaction of size $\epsilon_T/(\mu\epsilon_N)$
   contaminates any model with a penalty-regularised contact — *including yours*.

### 3.10.1 Checked, on your decks — it is negligible

Applying the Appendix B relations to the nine v2 decks. The slope
$\mathrm{d}\mu/\mathrm{d}s$ is taken at $s = 0$, where the exponential roughness decay is
steepest, so these are upper bounds. Two normal stiffnesses are used: the tangent of the Bandis
closure at the pre-seated state, $\mathrm{d}\sigma/\mathrm{d}v = K_{ni}(1 - v/v_m)^{-2} =
2.06\times10^{14}$ Pa/m, and — as a deliberately conservative floor — the raw `penalty_normal`
of $2\times10^{13}$ Pa/m.

| deck | $\mathrm{d}\mu/\mathrm{d}s$ (m⁻¹) | $\mathcal{A}$ | $\psi_{\rm implicit}$ (Bandis) | $\psi_{\rm implicit}$ (raw penalty) | $\psi_{\rm calibrated}$ | worst-case ratio |
|---|---|---|---|---|---|---|
| SW-T1 MC | −957 | −1.00305 | 0.009° | 0.089° | 12.36° | **0.7 %** |
| SW-T2 MC | −1 550 | −1.00458 | 0.012° | 0.121° | 11.89° | **1.0 %** |
| SW-S3 MC | −8 110 | −1.01252 | 0.026° | 0.270° | 55.0° | **0.5 %** |
| SW-S4 MC | −12 400 | −1.01932 | 0.041° | 0.420° | 30.9° | **1.4 %** |

So the implicit effect is at most 1.4 % of the calibrated dilation angle, and under the physically
correct stiffness it is 0.05–0.13 %. It is a compaction, as Appendix B predicts for slip-weakening
friction ($\mathcal{A} < -1$).

**Why it is so small here, and why it is large for Hosseini.** Two reasons, both worth being able
to state:

1. $\mathcal{A}$ departs from $-1$ only in proportion to $(\mathrm{d}\mu/\mathrm{d}\gamma)|t'_N|/\epsilon_T$.
   Your slip-weakening is spread over $L_R \sim 10^{-4}$ m with $\Delta\mu \sim 0.1$–$1.2$, giving
   $|\mathrm{d}\mu/\mathrm{d}s|$ of $10^3$–$10^4$ m⁻¹. In rate-and-state during a co-seismic event,
   $\mathrm{d}\mu/\mathrm{d}\gamma \to -\infty$, so $\mathcal{A} \ll -1$ and the effect is
   first-order. **The implicit dilation is a rate-and-state phenomenon, not a penalty-method
   phenomenon.** That is the correct reading of Appendix B, and it is a sharper statement than the
   paper itself makes.
2. Your $\epsilon_T/\epsilon_N$ is 0.05 against Hosseini's $1/2000 = 5\times10^{-4}$ — so on that
   factor alone yours is *worse* by 100×. It does not matter because factor 1 dominates.

Have this table ready. "Could implicit dilation contaminate your calibrated dilation angle?" is
exactly the question a Zimmerman-trained committee would ask, and the answer is quantitative: no,
at most 1.4 %, and here is why.

---

# Part 4 — What to take into your own paper

## 4.1 Structural lessons

1. **One ingredient per section.** §4.1 front alone → §4.2 one asperity → §4.2.1 afterslip → §4.3
   many asperities. Your §5 should do the same: verification → one specimen → the roughness
   comparison → all four.
2. **A single organising figure.** Their geometry–material diagram is what the paper is remembered
   for. Yours should be the roughness–stress-range diagram implied by Figure F2: two envelopes,
   four specimens, two disjoint $\sigma'_n$ ranges, and which envelope wins where.
3. **Derive, then verify numerically.** Every one of their scalings is checked against the model.
   You already have two such relations — the series-compliance identity and the softening-stability
   criterion. Present them as predictions the model must satisfy, not as calibration steps.
4. **State numerical admissibility as inequalities.** You have this in §3.7–3.9 of your draft.
   Keep it. It is what makes a numerical paper credible in JGR.
5. **Declare thresholds explicitly.** They declare $V_s$ for "seismic". You should declare what
   counts as "slip onset" and why — and note their point that the *first* slipping point is a poor
   marker.

## 4.2 The honesty lessons — these are worth the most

The paper twice says plainly that a modelling choice distorts a result, and it is stronger for it:

- $\beta_\xi = 0.01$: "the timing of the co-seismic events should not be compared with real data."
- The Coulomb-stress fit is described as "modified here to align with numerical results" — i.e.
  they say the fit was adjusted, rather than presenting it as a derivation.

Your equivalents, already in the draft, are the 0.52 flow geometry factor and the ~7 % systematic
in the published $a_h$. **Keep both prominent.** The instinct to bury them is exactly wrong: a
reviewer who finds an unstated limitation assumes there are others.

## 4.3 What you can claim that they cannot

Have these ready as one-liners:

| | Hosseini (2025) | Yours |
|---|---|---|
| Validation | SEAS benchmark + analytical limits | four laboratory specimens, five independent observables |
| Fault permeability | frozen at $h_{f0}$ in contact | evolves with dilation, gouge and closure |
| Matrix | impermeable | Biot poroelastic, with leak-off |
| Dilation | implicit, from the penalty ratio | explicit, non-associative, bounded by the second law |
| Aperture | one $h_f$ | mechanical $a_m$ and hydraulic $a_h$ distinguished |
| Friction | rate-and-state | Coulomb + roughness, and Barton–Bandis, compared |

The last row cuts both ways. RSF is the standard in the seismological community, and *not* having
it is the most likely question you will get on your paper 1. Prepared answer: RSF is designed for
the velocity dependence of *steady sliding*, and the Ye & Ghassemi protocol is a sequence of static
hold stages with one slip event — a regime in which the rate dependence is not excited and the
strength envelope is what the data constrains. Adding RSF would add two parameters the experiment
cannot identify. That is a good answer and it is true, but it works only if you have first shown
you know what RSF is, which is what Part 3 is for.

---

# Part 5 — Likely examination questions

**On rate-and-state**

1. *Write the regularised RSF law and explain what the regularisation fixes.* — §3.1.2. Singularity
   at $V=0$; the fault creeps microscopically at $V_0$.
2. *Why does the state variable evolve when the fault is locked?* — Aging law with the $V + V_0$
   shift; healing. Implementation consequence: $\theta$ must advance in the stick predictor.
3. *Aging vs slip law: when does it matter?* — §3.1.3 table. Healing at zero slip rate, asymmetry
   of step response, nucleation size.
4. *What is $a - b$ and why is its sign the whole problem?* — §3.1.1.
5. *Your $D_c$ is 0.2 mm; the laboratory says 10 µm. Defend it.* — §3.1.4. It sets nucleation size;
   a laboratory $D_c$ demands an unaffordable mesh; state the consequence.

**On numerics**

6. *Derive the mesh-size restriction for a velocity-weakening fault.* — §3.4.4. This is the one to
   be able to do at the board.
7. *Distinguish $L_{co}$, $L_{cr}$ and $R_\infty$.* — §3.5 table.
8. *Why an augmented Lagrangian rather than a penalty?* — §3.3. Exact constraint, no extra
   unknowns, result independent of $\epsilon$. Then: *and why does ORCA use a penalty anyway?* —
   because its normal stiffness is a physical Bandis law, not a numerical device.
9. *Your quasi-dynamic damping is 100× the physical value. What survives?* — §3.2. Sequence and
   interaction survive; timing does not; the post-seismic stage is where damping is negligible.
10. *How do you know the simulation is resolved?* — the trio: $\epsilon_T > \epsilon_{cr}$,
    $\Delta x < \min(L_{cr}, L_{co})$, $\Delta t < \beta_t D_c/V_{\max}$ — *then* a convergence study.

**On the physics**

11. *Why does aseismic slip outrun the pressure front?* — elastic stress transfer on a critically
    stressed fault. §3.7.1.
12. *What is the stress–injection parameter and what does it bound?* — §3.7.2.
13. *Explain the mechanism of cascading in one sentence.* — post-seismic slip on the barrier
    carries stress to the neighbour; its reach is set by $(a/b)_s$, the distance by $\rho_a$.
14. *What is implicit dilation and is it physical?* — §3.10. Be even-handed: it follows from the
    penalty ratio, and the defence that penalty factors are physical stiffnesses is reasonable but
    contestable.

**On your own work, by comparison**

15. *Why no rate-and-state in your paper 1?* — §4.3, last paragraph.
16. *Hosseini's fault permeability is constant. Does that matter?* — yes, and it is your opening
    (§2.2–2.3).
17. *Could implicit dilation contaminate your calibrated dilation angle?* — §3.10, second warning.
    **Check the $k_t/k_n$ ratio in your decks before the exam.**

---

# Part 6 — Immediate action items

1. ~~Compute the implicit dilation angle for your decks.~~ **Done — see §3.10.1.** At most 1.4 % of
   the calibrated $\psi$ under the most conservative stiffness assumption, 0.05–0.13 % under the
   physical one. Worth one sentence in the manuscript's §3.5.4 and a prepared answer in the exam;
   no action needed on the model.
2. **Read Sáez et al. (2022), Bhattacharya & Viesca (2019), and Perfettini & Avouac (2004)** before
   the exam. They supply the analytical backbone this paper leans on, and a committee will expect
   you to know the sources of the scalings, not just the paper that used them.
3. **Look at the SCEC SEAS benchmark suite** (strike.scec.org/cvws/seas). If paper 2 goes toward
   RSF, that is the verification gate, and it is a substantial piece of work in itself.
4. **Decide the scope of paper 2 now.** "Add RSF to ORCA, verify against SEAS, couple it to the
   validated aperture model, and produce a modified geometry–material diagram" is two papers'
   worth. The narrower and stronger version: keep your existing validated friction law, and show
   what slip-dependent permeability does to the aseismic-front and cascade results that
   constant-aperture models predict.
