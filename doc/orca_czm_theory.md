# ORCA 3.0

## Theory, Algorithms and Implementation Manual

*Hydro-mechanical modelling of fracture opening, closure and injection-induced shear slip with cohesive-zone interface elements*

> This Markdown edition was converted from `orca_czm_theory.tex`. Display equations use LaTeX/MathJax syntax. TikZ and PGFPlots diagrams retain their original source in collapsible blocks.

### How to read this manual

This document is organised so that it can be read straight through by someone
who knows the finite element method and continuum mechanics, but nothing about
this code.

- **Part I.** The physical problem and the software framework. What a
    *kernel*, a *material* and an *interface kernel* are, and how
    residuals are assembled. Read this first even if you know MOOSE.
- **Part II.** The bulk continuum: Biot poroelasticity, the weak forms, and
    the exact residual each bulk kernel contributes.
- **Part III.** The fracture as a zero-thickness internal interface: how the
    mesh is split, how the displacement jump is defined and rotated, and how the
    interface kernels inject surface tractions into the bulk momentum balance.
- **Part IV.** Interface constitutive theory: unilateral contact, the penalty
    method, interface elasto-plasticity (yield surface, flow rule, hardening),
    dilatancy and the thermodynamic constraint on it.
- **Part V.** The four constitutive laws implemented, in full, with the reason
    each exists.
- **Part VI.** Numerics: global and local Newton, the return map, consistent
    tangents, automatic differentiation, and the regularisations --- what each one
    does to convergence and why.
- **Part VII.** Hydraulics: aperture, the cubic law, permeability, and the
    hydro-mechanical coupling loop.
- **Part VIII.** The verification suite: what each test asserts and what a
    correct answer looks like.
- **Part IX.** Practical guide: which parameter moves which feature of the
    response, and how to back-analyse a result.
- **Supplement** (after the appendices). The reference experiment,
    Ye & Ghassemi (2018): geometry, protocol, the exact reduction equations, the
    complete data tables, quantities derived from those data that the paper does
    not tabulate, and a point-by-point correspondence between what was measured
    and what the code computes. Read it before scoring any validation run --- four
    of the observables are *not* the same quantity in the paper and in the model.

Throughout, `monospace` names refer to actual C++ classes or input-file
parameters, so the manual doubles as a map of the source tree.

## Part I: Foundations

### The physical problem

#### What is being modelled

A cylindrical rock specimen contains a single planar fracture inclined at an
angle $\theta$ to its axis. The specimen is held under a confining pressure
$\sigma_3$ and an axial stress $\sigma_1$. Fluid is injected into one end of the
fracture and produced from the other. As the injection pressure rises, the
effective normal stress clamping the fracture falls; at some point the fracture
slips, dilates, and its transmissivity increases.

Four coupled processes must be represented:

1. **Bulk poroelasticity.** The rock matrix deforms elastically and
    carries a pore fluid. Pressure changes produce strain and strain produces
    pressure (Biot coupling).
1. **Fracture normal mechanics.** The two fracture walls are in
    contact. They must not interpenetrate. The contact is highly nonlinear:
    the joint stiffens dramatically as it closes (asperities engage) and
    carries no tension when it opens.
1. **Fracture shear mechanics.** The fracture slips frictionally once
    the shear traction reaches a strength that depends on the effective normal
    stress and on the accumulated slip (weakening). Slip on a rough surface
    forces the walls apart: *dilatancy*.
1. **Fracture flow.** Fluid flows along the fracture much faster than
    through the matrix, with a transmissivity that depends on the cube of the
    aperture. Aperture depends on the mechanics; the mechanics depends on the
    pressure. The loop is two-way.

**Figure.** The laboratory configuration. Confining pressure $\sigma_3$, axial stress $\sigma_1$, injection pressure $P_i$ rising, production pressure $P_o$ fixed. The fracture is inclined at $\theta$ to the specimen axis.

<details>
<summary>Original TikZ/PGFPlots source</summary>

```latex
\begin{tikzpicture}[scale=1.0]
  \draw[thick,fill=gray!12] (0,0) rectangle (3.2,6);
  \draw[very thick,red] (0,1.4) -- (3.2,4.6);
  \node[red] at (2.5,2.6) {\small fracture};
  \foreach \y in {0.6,1.6,2.6,3.6,4.6,5.4}{
    \draw[-{Latex[length=2mm]},blue] (-0.9,\y) -- (-0.15,\y);
    \draw[-{Latex[length=2mm]},blue] (4.1,\y) -- (3.35,\y);
  }
  \node[blue] at (-1.35,3) {$\sigma_3$};
  \node[blue] at (4.6,3) {$\sigma_3$};
  \foreach \x in {0.5,1.2,1.9,2.6}{
    \draw[-{Latex[length=2mm]},black!70] (\x,7.0) -- (\x,6.15);
    \draw[-{Latex[length=2mm]},black!70] (\x,-1.0) -- (\x,-0.15);
  }
  \node at (1.6,7.35) {$\sigma_1$};
  \fill[cyan] (0.35,1.75) circle (0.10);
  \node[cyan!60!black,left] at (0.3,1.75) {\small $P_i$};
  \fill[cyan] (2.85,4.25) circle (0.10);
  \node[cyan!60!black,right] at (2.95,4.25) {\small $P_o$};
  \draw[dashed] (0,1.4) -- (2.0,1.4);
  \draw[-{Latex[length=1.5mm]}] (1.0,1.4) arc (0:45:1.0);
  \node at (1.35,1.85) {\small $\theta$};
\end{tikzpicture}
```

</details>

#### Resolved stresses on the fracture

For a fracture whose normal makes an angle $\theta$ with the $\sigma_1$
direction, elementary Mohr circle algebra gives the normal and shear tractions

$$
\begin{aligned}
\sigma_n &= \tfrac{1}{2}(\sigma_1+\sigma_3) + \tfrac{1}{2}(\sigma_1-\sigma_3)\cos 2\theta,\\
\tau     &= \tfrac{1}{2}(\sigma_1-\sigma_3)\sin 2\theta,
\end{aligned}
$$

and the effective normal stress is

<a id="eq-effstress"></a>

$$
\sigma'_n = \sigma_n - p ,
$$

with $p$ the fluid pressure in the fracture. Equation [`eq:effstress`](#eq-effstress) is
the heart of injection-induced slip: raising $p$ reduces $\sigma'_n$, reduces
the frictional strength $\mu\sigma'_n$, and eventually triggers slip.

> **Remark.**
>
> The effective-stress coefficient on an *open* fracture is exactly $1$,
> because the fluid acts on the entire fracture area. This is different from the
> Biot coefficient $\alpha<1$ of the porous matrix, where the fluid acts only on
> the pore fraction. Both appear in the model and must not be confused.

### The software framework

#### Weak forms, residuals and the MOOSE abstraction

Every problem is written as: find the vector of nodal unknowns $\mathbf{u}$ such
that

$$
\mathbf{R}(\mathbf{u}) = \mathbf{0},
$$

where $\mathbf{R}$ is assembled by numerical quadrature from contributions of
three kinds of object:

- **Kernel.** contributes a *volume* integral over elements:
    $R_i \mathrel{+}= \int_\Omega f(\mathbf{u},\nabla\mathbf{u})\,\psi_i \,\mathrm{d}\Omega$
    or $\int_\Omega \boldsymbol{g}\cdot\nabla\psi_i \,\mathrm{d}\Omega$.
- **BoundaryCondition.** contributes a *surface* integral over an external
    boundary.
- **InterfaceKernel.** contributes a surface integral over an *internal*
    boundary that separates two element blocks, and can write into the rows of
    both the “element” side and the “neighbor” side.

 A fourth kind of object carries no residual at all:

- **Material.** computes quantities at quadrature points (stress, permeability,
    aperture, tractions) that kernels then consume. Materials can depend on each
    other; the framework resolves the dependency graph automatically. An
    `InterfaceMaterial` is a material evaluated on an internal interface,
    with access to quantities from *both* sides.

The essential idea to internalise is this:

**Materials compute physics. Kernels turn physics into residual entries.**  
The constitutive laws in this code are all `InterfaceMaterial`s. They
never touch the residual. They produce one thing --- the interface traction
vector --- and a single small interface kernel turns it into forces on the two
fracture walls.

#### Automatic differentiation and the Jacobian
<a id="sec-ad"></a>
Newton's method needs $\mathbf{J} = \partial\mathbf{R}/\partial\mathbf{u}$.
Deriving this by hand for a nonlinear contact/friction law is error-prone. The
code instead uses *forward-mode automatic differentiation* (AD): the scalar
type `ADReal` is a dual number

$$
\hat a = \big(a,\; \nabla_{\mathbf{u}} a\big),
$$

carrying its value and its derivatives with respect to all local degrees of
freedom. Arithmetic is overloaded so that the chain rule is applied
automatically:

$$
\hat a \hat b = \big(ab,\; a\,\nabla b + b\,\nabla a\big), \qquad
\sqrt{\hat a} = \Big(\sqrt a,\; \tfrac{\nabla a}{2\sqrt a}\Big).
$$

If a residual is computed entirely in `ADReal`, the Jacobian is exact and
free.

> **Remark: The trap that AD sets.**
>
> <a id="rem-adtrap"></a>
> AD is exact but not robust at non-smooth points. $\sqrt{\hat a}$ has an infinite
> derivative at $a=0$. $\hat a^{\hat b}$ is worse: its derivative contains
> $b'\log a$, which is $0\cdot(-\infty)=\mathrm{NaN}$ at $a=0$ even for a constant
> exponent. A NaN in the derivative leaves the *value* finite --- so the
> residual looks healthy and only the Jacobian is poisoned. The symptom is a
> linear solver reporting `DIVERGED_NANORINF` while the Newton residual
> converges quadratically. Every $\sqrt{\cdot}$ and $(\cdot)^p$ acting on a
> quantity that can reach exactly zero must be guarded. This is discussed
> concretely in Section [`sec:powguard`](#sec-powguard).

#### Map of the source tree

| Directory | Contents |
| --- | --- |
| `src/kernels/` | Bulk residuals: momentum balance, fluid mass balance, Darcy flux. |
| `src/interfacekernels/` | The three interface residuals: mechanical traction, fluid pressure on the walls, in-plane fracture flow. |
| `src/InterfaceMaterial/` | Fracture kinematics, the four constitutive laws, the aperture/permeability law, scalar extraction helpers. |
| `src/materials/` | Bulk elasticity, poroelastic/fluid properties, Biot coefficient. |
| `src/meshgenerators/` | `OrcaFaultInterface3DGenerator`: turns a conforming mesh into one with a split fracture surface. |
| `include/utils/` | Shared closed-form pieces (`OrcaNormalClosure`). |
| `test/tests/` | Verification suite. |

## Part II: The bulk continuum

### Biot poroelasticity

#### Governing equations

Let $\boldsymbol{\sigma}$ be the total Cauchy stress (tension positive), $p$ the pore
pressure, $\boldsymbol{u}$ the displacement, $\boldsymbol{\varepsilon}=\tfrac12(\nabla\boldsymbol{u}+\nabla\boldsymbol{u}^T)$
the small strain, and $\varepsilon_v=\operatorname{tr}\boldsymbol{\varepsilon}$ the volumetric
strain. Quasi-static linear Biot poroelasticity is

<a id="eq-mom"></a>
<a id="eq-effstress2"></a>
<a id="eq-mass"></a>
<a id="eq-darcy"></a>

$$
\begin{aligned}
\nabla\!\cdot\!\boldsymbol{\sigma} &= \boldsymbol{0}, &&\text{momentum balance}\\
\boldsymbol{\sigma} &= \mathbb{C}:\boldsymbol{\varepsilon} - \alpha p\,\boldsymbol{I}, &&\text{effective stress}\\
\frac{1}{M}\dot p + \alpha\dot\varepsilon_v + \nabla\!\cdot\!\boldsymbol{q} &= 0,
   &&\text{fluid mass balance}\\
\boldsymbol{q} &= -\frac{\mathbf{k}}{\mu_f}\big(\nabla p - \rho_f \boldsymbol{g}\big), &&\text{Darcy}
\end{aligned}
$$

with $\alpha$ the Biot coefficient, $\mathbf{k}$ the intrinsic permeability
tensor, $\mu_f$ the fluid viscosity, and $M$ the *Biot modulus*

<a id="eq-biotmodulus"></a>

$$
\frac{1}{M} = \frac{\alpha-\phi}{K_s} + \frac{\phi}{K_f}
            = \frac{(1-\alpha)(\alpha-\phi)}{K_d} + \frac{\phi}{K_f},
$$

where $\phi$ is porosity, $K_f$ the fluid bulk modulus, $K_s$ the solid grain
bulk modulus and $K_d$ the drained bulk modulus. The second form uses the
identity $K_s = K_d/(1-\alpha)$.

> **Remark: Two different coefficients, easily confused.**
>
> $\alpha$ appears *twice* and they are not the same term:
> in [`eq:effstress2`](#eq-effstress2) it converts pressure into stress; in [`eq:mass`](#eq-mass) it
> converts volumetric strain rate into fluid content. The system is symmetric only
> if the same $\alpha$ is used in both. Using the porosity $\phi$ in place of
> $\alpha$ in [`eq:mass`](#eq-mass) --- an easy mistake, because $\phi\rho_f$ is the
> fluid mass per unit volume --- makes the consolidation coefficient wrong by the
> factor $\alpha/\phi$. For a granite with $\alpha=0.6$, $\phi=0.001$ that is a
> factor of $600$.

#### Weak forms and the bulk kernels

Multiply [`eq:mom`](#eq-mom) by a test function $\boldsymbol{\psi}$ and integrate by parts:

$$
\int_\Omega \boldsymbol{\sigma} : \nabla\boldsymbol{\psi} \,\mathrm{d}\Omega
 \;-\; \int_{\partial\Omega} (\boldsymbol{\sigma}\!\cdot\!\boldsymbol{n})\cdot\boldsymbol{\psi} \,\mathrm{d}\Gamma = 0 .
$$

Substituting [`eq:effstress2`](#eq-effstress2) and taking $\boldsymbol{\psi} = \psi_i \boldsymbol{e}_c$ for
component $c$ gives the residual implemented by `OrcaPoroMechKernel`:

<a id="eq-poromechkernel"></a>

$$
\boxed{\;
R_i^{(c)} = \int_\Omega \Big[ \boldsymbol{\sigma}^{\text{eff}}_{c\,\bullet}\cdot\nabla\psi_i
   \;-\; \alpha\, p \,\partial_c \psi_i \Big] \,\mathrm{d}\Omega \;}
$$

where $\boldsymbol{\sigma}^{\text{eff}}=\mathbb{C}:\boldsymbol{\varepsilon}$ is the material's
`stress` property. Note that the code stores the *effective* stress in
`stress` and subtracts $\alpha p$ inside the kernel.

The mass balance [`eq:mass`](#eq-mass) is split across three kernels, all acting on
the pressure variable, all optionally multiplied by $\rho_f$ to work in mass
rather than volume form (write $\gamma=\rho_f$ or $\gamma=1$):

<a id="eq-storagekernel"></a>
<a id="eq-volexpkernel"></a>
<a id="eq-darcykernel"></a>

$$
\begin{aligned}
\mathtt{OrcaSinglePhaseMassTimeDerivativeKernel:}\quad
  & R_i \mathrel{+}= \int_\Omega \gamma\,\frac{1}{M}\,\dot p\; \psi_i \,\mathrm{d}\Omega,
  \\[2pt]
\mathtt{OrcaSinglePhaseMassVolumetricExpansionKernel:}\quad
  & R_i \mathrel{+}= \int_\Omega \gamma\,\alpha\,\dot\varepsilon_v\; \psi_i \,\mathrm{d}\Omega,
  \\[2pt]
\mathtt{OrcaFullySaturatedSinglePhaseDarcySUPGKernel:}\quad
  & R_i \mathrel{+}= \int_\Omega \gamma\,\frac{\mathbf{k}}{\mu_f}
      \big(\nabla p - \rho_f\boldsymbol{g}\big)\cdot\nabla\psi_i \,\mathrm{d}\Omega.
\end{aligned}
$$

The Darcy kernel is in divergence (integrated-by-parts) form, which is why it
appears with $\nabla\psi_i$ and no explicit divergence. $1/M$ is supplied by the
material as `one_over_biot_modulus_qp` and $\alpha$ as
`biot_coefficient_qp`.

#### Strain and stress algorithm
<a id="sec-strainalgo"></a>
`OrcaMechMaterial` offers two kinematic paths.

**Total small strain.** Directly

$$
\boldsymbol{\varepsilon} = \tfrac12\!\left(\nabla\boldsymbol{u} + \nabla\boldsymbol{u}^T\right),\qquad
\boldsymbol{\varepsilon}^{\text{mech}} = \boldsymbol{\varepsilon} - \sum_k \boldsymbol{\varepsilon}^{*}_k ,
$$

with $\boldsymbol{\varepsilon}^{*}_k$ any eigenstrains (e.g. thermal).

**Incremental strain.** The strain increment
$\Delta\boldsymbol{\varepsilon}$ is computed from the displacement increment, then

$$
\boldsymbol{\varepsilon}_{n+1} = \boldsymbol{\varepsilon}_n + \Delta\boldsymbol{\varepsilon},\qquad
\boldsymbol{\varepsilon}^{\text{mech}}_{n+1} = \boldsymbol{\varepsilon}^{\text{mech}}_n
   + \Delta\boldsymbol{\varepsilon} - \Delta\boldsymbol{\varepsilon}^{*} .
$$

This path also produces the strain rate $\dot{\boldsymbol{\varepsilon}}=\Delta\boldsymbol{\varepsilon}/\Delta t$
and the volumetric strain rate

$$
\dot\varepsilon_v = \frac{\operatorname{tr}\boldsymbol{\varepsilon}_{n+1}-\operatorname{tr}\boldsymbol{\varepsilon}_{n}}{\Delta t},
$$

which is the `vol_strain_rate` property consumed
by [`eq:volexpkernel`](#eq-volexpkernel). **The incremental path is required whenever
the flow problem is coupled**, because the total-strain path does not produce
$\dot\varepsilon_v$.

In both paths the stress is

$$
\boldsymbol{\sigma}^{\text{eff}} = \mathbb{C}:\boldsymbol{\varepsilon}^{\text{mech}} + \boldsymbol{\sigma}_0 ,
$$

where $\boldsymbol{\sigma}_0$ is a user-specified initial (in-situ) stress. The bulk is
*linear elastic*: all plasticity in this framework lives on the fracture.

> **Remark: Initial stress must equal the boundary condition.**
>
> $\boldsymbol{\sigma}_0$ is added to the constitutive stress but does not by itself satisfy
> equilibrium with the applied tractions. If the deck sets
> $\boldsymbol{\sigma}_0 = -31\,\text{MPa}\,\boldsymbol{I}$ but applies a $30$ MPa confining traction,
> the specimen starts $1$ MPa out of equilibrium and relaxes during the first
> steps, contaminating the “initial” state. Set them consistently.

**Volumetric locking correction.** For nearly incompressible response,
low-order elements lock. The optional correction replaces the element's
volumetric strain by its element average,

$$
\boldsymbol{\varepsilon} \leftarrow \boldsymbol{\varepsilon}
  + \tfrac13\Big(\overline{\varepsilon_v} - \operatorname{tr}\boldsymbol{\varepsilon}\Big)\boldsymbol{I},
\qquad
\overline{\varepsilon_v} = \frac{\int_{\Omega_e}\varepsilon_v \,\mathrm{d}\Omega}{\int_{\Omega_e}\,\mathrm{d}\Omega},
$$

i.e. a $\bar B$ method.

## Part III: The fracture as an internal interface

### Discrete representation of a fracture

#### Why a zero-thickness interface

There are three common ways to put a fracture in a finite element model.

1. **Equivalent continuum / smeared.** Represent the fracture by
    softening a band of elements. Cheap, but the displacement jump is smeared over
    the band width, so aperture and slip are mesh-dependent and contact cannot be
    enforced.
1. **XFEM / embedded discontinuity.** Enrich the shape functions so a
    jump can occur inside an element. Powerful for propagating cracks, but the
    enrichment, integration and contact treatment are all substantially more
    complex.
1. **Zero-thickness cohesive interface (used here).** Duplicate the
    nodes on the fracture surface so that the mesh has two coincident faces. The
    displacement jump is then an exact, mesh-independent kinematic quantity, and
    the interface carries a traction-separation law.

For a *pre-existing, non-propagating* fracture of known geometry --- which
is exactly the laboratory configuration --- option 3 is the right choice: the
fracture path is known, so no enrichment is needed, and the jump is precisely
what the experiment measures (LVDT slip and dilation).

#### Splitting the mesh: `OrcaFaultInterface3DGenerator`
<a id="sec-splitter"></a>
The input mesh is *conforming*: elements on both sides of the fracture
share the same nodes. The generator turns it into a mesh with two coincident
surfaces. The algorithm is:

1. **Build a node$\to$element map** over all active elements.
1. **Resolve the interface** from either a sideset or a nodeset name. If
    a nodeset is given, a sideset is reconstructed from it, because interface
    kernels act on element *sides*, not nodes.
1. **Select the nodes to duplicate.** A node is duplicated only if it is
    an *interior* interface node --- i.e. it belongs to at least one
    interface face whose element has a neighbour across the interface. Nodes with
    no cross-neighbour lie on a true crack front and are left welded, which is
    what keeps a partially-cut fracture attached at its tip. Optionally,
    non-manifold nodes (belonging to edges shared by more than two interface
    faces, i.e. junctions) are also excluded.
1. **Duplicate.** For each selected node, create a new node at the same
    coordinates, and *copy its nodeset memberships* so that boundary
    conditions applied to the original node also apply to the copy. This matters:
    if the fracture mouth lies on a pressure-inlet boundary, both copies must
    carry the Dirichlet condition, or only one wall is pressurised.
1. **Re-point elements.** All elements on one chosen side of the
    interface are re-pointed from the original node to its duplicate. Which side
    is “primary” is decided once, before any re-pointing, so that the resulting
    interface normal is consistent everywhere.
1. **Tag the sidesets.** The primary interface sideset is retained, and
    optionally a secondary sideset is added on the other side.

After this the two walls are geometrically coincident but topologically
independent: they can separate, slide, and carry different pressures.

**Figure.** Node duplication. The gap in (b) is drawn only for clarity --- the two surfaces are geometrically coincident.

<details>
<summary>Original TikZ/PGFPlots source</summary>

```latex
\begin{tikzpicture}[scale=1.15]
\begin{scope}
  \draw[step=0.7,gray!50,very thin] (0,0) grid (2.8,1.4);
  \draw[very thick,red] (0,0.7) -- (2.8,0.7);
  \foreach \x in {0,0.7,1.4,2.1,2.8}{\fill[black] (\x,0.7) circle (0.055);}
  \node at (1.4,-0.4) {\small (a) conforming: shared nodes};
\end{scope}
\begin{scope}[xshift=4.6cm]
  \draw[step=0.7,gray!50,very thin] (0,0.78) grid (2.8,1.48);
  \draw[step=0.7,gray!50,very thin] (0,0) grid (2.8,0.62);
  \draw[very thick,red] (0,0.78) -- (2.8,0.78);
  \draw[very thick,red] (0,0.62) -- (2.8,0.62);
  \foreach \x in {0,0.7,1.4,2.1,2.8}{
    \fill[blue] (\x,0.78) circle (0.055);
    \fill[orange] (\x,0.62) circle (0.055);}
  \node at (1.4,-0.4) {\small (b) split: duplicated nodes};
  \node[blue,right] at (2.9,0.85) {\scriptsize neighbor};
  \node[orange,right] at (2.9,0.55) {\scriptsize element};
\end{scope}
\end{tikzpicture}
```

</details>

### Interface kinematics

#### The displacement jump

Let the two coincident faces be labelled “element” ($-$) and “neighbor”
($+$). The *global* displacement jump is

$$
[\![\boldsymbol{u}]\!] = \boldsymbol{u}^{+} - \boldsymbol{u}^{-} \in \mathbb{R}^3 ,
$$

computed by `OrcaCZMComputeDisplacementJump` and stored as
`displacement_jump_global`.

#### The local frame and the rotation matrix
<a id="sec-rotation"></a>
Constitutive laws are written in a frame aligned with the fracture:

$$
\text{component } 0 = \text{normal},\qquad
\text{components } 1,2 = \text{in-plane tangents}.
$$

Let $\boldsymbol{n}$ be the interface unit normal at the quadrature point. The rotation
matrix $\boldsymbol{R}$ is built by `OrcaCZMTools::computeReferenceRotation` so that

$$
\boldsymbol{R}\, \boldsymbol{e}_1 = \boldsymbol{n} ,
$$

i.e. $\boldsymbol{R}$ maps the *local* frame into the *global* frame. In 3D it
is the minimal rotation taking $\boldsymbol{e}_x$ onto $\boldsymbol{n}$; in 2D it is the
corresponding planar rotation. The local jump is therefore

<a id="eq-localjump"></a>

$$
\boxed{\;\boldsymbol{g} \;=\; \boldsymbol{R}^{T}\,[\![\boldsymbol{u}]\!]\;}
\qquad
g_n \equiv g_0,\quad \boldsymbol{g}_t \equiv (g_1,g_2).
$$

Sign convention: $g_n>0$ is **opening**, $g_n<0$ is interpenetration.

Conversely, a local traction $\boldsymbol{t}^{\text{loc}}$ is mapped back by

<a id="eq-globaltraction"></a>

$$
\boldsymbol{t}^{\text{glob}} = \boldsymbol{R}\, \boldsymbol{t}^{\text{loc}},
$$

which is what `OrcaComputeGlobalTractionSmallStrain` does. Tension-positive
convention: $t^{\text{loc}}_0<0$ means the interface is in compression.

> **Remark: Why the rotation is computed from the reference normal.**
>
> The rotation is evaluated on the *undeformed* geometry. For the small
> strains of a laboratory specimen ($10^{-4}$--$10^{-3}$) the difference is
> negligible. For large rotations it would not be, and a finite-strain CZM would
> need $\boldsymbol{R}$ to be a function of the deformation gradient (the machinery for
> this exists in `OrcaCZMTools` but is unused here).

#### Scalar extraction helpers

Two small materials turn vectors into the scalars used for output and for
downstream laws:

- `OrcaCZMRealVectorCartesianComponent` extracts component $i$ of a
    vector property. Applied to `interface_traction` with $i=0$ this gives
    $\sigma_n$ in the local frame (the property conventionally named
    `czm_sigma_n`); with $i=1,2$ the two shear tractions.
- `OrcaCZMRealVectorScalar` extracts the normal *magnitude*
    $(\boldsymbol{n}\cdot\boldsymbol{v})$ or the tangential magnitude
    $\lVert \boldsymbol{v} - (\boldsymbol{n}\cdot\boldsymbol{v})\boldsymbol{n}\rVert$ of a global vector.

> **Remark.**
>
> The tangential option computes a Euclidean norm and therefore inherits the
> $\sqrt{\cdot}$ derivative singularity of Remark [`rem:adtrap`](#rem-adtrap) when the
> tangential component is exactly zero. It is safe as an output-only diagnostic
> but should not be fed into a residual.

### The interface kernels
<a id="ch-ifk"></a>
Three interface kernels exist. Together they are the *entire* coupling
between the fracture and the rest of the problem.

#### Mechanical traction: `OrcaMechInterfaceKernel`

The cohesive interface contributes the surface term

$$
\int_{\Gamma} \boldsymbol{t} \cdot [\![\boldsymbol{\psi}]\!] \,\mathrm{d}\Gamma
$$

to the momentum weak form. With $[\![\boldsymbol{\psi}]\!] = \psi^{+} - \psi^{-}$, and
writing $\boldsymbol{t} = \boldsymbol{t}^{\text{glob}}$ from [`eq:globaltraction`](#eq-globaltraction), the
residual rows are

<a id="eq-mechifk"></a>

$$
\boxed{\;
R^{-}_i \mathrel{+}= -\,t_c\,\psi^{-}_i,
\qquad
R^{+}_i \mathrel{+}= +\,t_c\,\psi^{+}_i \;}
$$

for displacement component $c$. Equal and opposite forces on the two walls:
Newton's third law is built in, not imposed.

This kernel contains *no physics*. It reads one material property,
`traction_global`, and distributes it. All the mechanics is in whichever
`InterfaceMaterial` produced that property.

#### Fluid pressure on the walls: `OrcaCZMFluidPressureInterfaceKernel`

The fluid inside the fracture pushes the walls apart. In the tension-positive
local frame the total traction is

$$
t^{\text{loc}}_0\big|_{\text{total}} = t^{\text{loc}}_0\big|_{\text{contact}} - c_p\, p_f ,
$$

where $p_f$ is the fracture fluid pressure and $c_p$ is the effective-stress
coefficient (`pressure_traction_coefficient`, entered as $-c_p$). The
kernel forms $\boldsymbol{R}\,(-c_p p_f,0,0)^T$ and distributes it exactly
as [`eq:mechifk`](#eq-mechifk).

$p_f$ comes from `OrcaCZMInterfacePressure`, which simply averages the
pressure variable across the interface,

$$
p_f = \tfrac12\big(p^{-} + p^{+}\big).
$$

> **Remark: $c_p$ is not a fitting parameter.**
>
> For an open fracture the fluid acts on the whole area, so $c_p=1$ exactly. Any
> other value is an empirical adjustment of the effective normal stress and should
> be declared as such.

#### In-plane flow: `OrcaFractureFlowInterfaceKernel`

Discussed in full in Chapter [`ch:flow`](#ch-flow).

#### How it all fits together

<a id="fig-pipeline"></a>

**Figure.** The fracture pipeline. Green = solution variables, blue = materials (physics), orange = kernels (residual assembly). The constitutive law is a pure function of the local jump and the stored state; it never sees the mesh or the residual.

<details>
<summary>Original TikZ/PGFPlots source</summary>

```latex
\begin{tikzpicture}[
   node distance=6mm,
   box/.style={draw,rounded corners=2pt,align=center,inner sep=4pt,font=\small},
   mat/.style={box,fill=blue!8},
   ker/.style={box,fill=orange!12},
   var/.style={box,fill=green!10},
   ar/.style={-{Latex[length=2mm]},thick}
]
\node[var] (u) {$\bs u$ (displacements)};
\node[var,right=22mm of u] (p) {$p$ (pressure)};

\node[mat,below=of u] (jump) {\code{OrcaCZMComputeDisplacementJump}\\
  $\jump{\bs u}$, $\bs g=\bs R^T\jump{\bs u}$, $\bs R$};
\node[mat,below=of jump] (law) {\textbf{constitutive law}\\
  $\bs g \mapsto \bs t^{\text{loc}}$, state};
\node[mat,below=of law] (glob) {\code{OrcaComputeGlobalTractionSmallStrain}\\
  $\bs t^{\text{glob}} = \bs R\,\bs t^{\text{loc}}$};
\node[ker,below=of glob] (mifk) {\code{OrcaMechInterfaceKernel}\\ residual on $\bs u$};

\node[mat,right=16mm of law] (ap) {\code{ADOrcaCZMComputeMechanicalAperture}\\
  \code{ADOrcaRoughnessDamageFracturePermeability}\\ $a_h$, $k_f$, $T$};
\node[ker,below=16mm of ap] (fifk) {\code{OrcaFractureFlowInterfaceKernel}\\ residual on $p$};
\node[mat,above=14mm of ap] (ip) {\code{OrcaCZMInterfacePressure}\\ $p_f$};
\node[ker,right=14mm of glob] (pifk) {\code{OrcaCZMFluidPressure}\\\code{InterfaceKernel}\\ residual on $\bs u$};

\draw[ar] (u) -- (jump);
\draw[ar] (jump) -- (law);
\draw[ar] (law) -- (glob);
\draw[ar] (glob) -- (mifk);
\draw[ar] (law) -- (ap);
\draw[ar] (ap) -- (fifk);
\draw[ar] (p) -- (ip);
\draw[ar] (ip) -- (pifk);
\draw[ar] (ip.east) to[out=0,in=90] (ap.north east);
\draw[ar] (mifk.west) to[out=180,in=180] node[left,font=\scriptsize] {assemble} (u.west);
\draw[ar] (fifk.east) to[out=0,in=0] node[right,font=\scriptsize] {assemble} (p.east);
\draw[ar] (pifk.north) to[out=90,in=-40] (u.south east);
\end{tikzpicture}
```

</details>

## Part IV: Interface constitutive theory

### Unilateral contact and the penalty method

#### The contact problem

The two walls must not interpenetrate. Writing the gap as $g_n$ and the contact
pressure as $p_c\ge 0$ (compression positive, so $t_0 = -p_c$), the exact
statement is the Karush--Kuhn--Tucker (Signorini) system

<a id="eq-kkt"></a>

$$
g_n \ge 0,\qquad p_c \ge 0,\qquad p_c\, g_n = 0 .
$$

“Either the gap is open and there is no pressure, or there is pressure and the
gap is closed.” This is a variational inequality, not an equation, and it is
not differentiable.

#### Why penalty, and what it costs

Three standard treatments:

| Method | Idea | Trade-off |
| --- | --- | --- |
| Lagrange multipliers | Add $p_c$ as an unknown field, enforce [`eq:kkt`](#eq-kkt) exactly. | Exact; but adds unknowns, needs an inf–sup stable space, and gives a saddle-point system. |
| Augmented Lagrangian | Penalty + multiplier update loop. | Exact in the limit with moderate stiffness; needs an outer loop. |
| **Penalty (used here)** | Allow a small interpenetration and generate a restoring pressure $p_c = K_n\left\langle -g_n \right\rangle_{+}$. | No extra unknowns, no saddle point, trivially compatible with a displacement-only Newton solve; but only approximate, and stiff. |

The penalty regularisation replaces [`eq:kkt`](#eq-kkt) by the single smooth-ish
relation

<a id="eq-penalty"></a>

$$
p_c = K_n \left\langle -g_n \right\rangle_{+},\qquad \left\langle x \right\rangle_{+}=\max(x,0),
$$

which is exactly [`eq:kkt`](#eq-kkt) in the limit $K_n\to\infty$.

**Choosing $K_n$.** The physical meaning of $K_n$ is a joint normal
stiffness. Numerically, the relevant group is

$$
\Pi = \frac{K_n\,h}{E},
$$

with $h$ the element size and $E$ the bulk modulus. $\Pi\ll 1$ makes the
interface artificially compliant and the answer wrong; $\Pi\gg 1$ makes the
matrix ill-conditioned. In the shear-compression verification case,
$\Pi\approx 2000$ gives a $4%$ error against the closed form while $\Pi\approx 20$
gives $19%$ --- the excess compliance shows up directly as excess slip. Aim for
$\Pi = 10^2$--$10^3$.

> **Remark: Penalty and iterative solvers do not mix.**
>
> A penalty stiffness $10^3$ times the bulk stiffness produces a matrix whose
> condition number is dominated by the interface. Algebraic multigrid tends to
> fail on such operators. Direct solvers are the reliable choice for these
> problems at laboratory scale.

#### Smoothing the active set
<a id="sec-smoothing"></a>
Equation [`eq:penalty`](#eq-penalty) has a kink at $g_n=0$: the tangent jumps from $0$ to
$K_n$. Newton's method oscillates across such a kink. The code therefore
replaces $\left\langle x \right\rangle_{+}$ by a smooth positive part

<a id="eq-smoothpos"></a>

$$
\boxed{\;
\left\langle x \right\rangle_{+}_\epsilon = \tfrac12\Big(x + \sqrt{x^2+\epsilon^2}\Big) \;}
\qquad
\frac{\,\mathrm{d} \left\langle x \right\rangle_{+}_\epsilon}{\,\mathrm{d} x} = \tfrac12\left(1 + \frac{x}{\sqrt{x^2+\epsilon^2}}\right),
$$

controlled by `contact_gap_regularization` $=\epsilon$. Properties:

- $\left\langle x \right\rangle_{+}_\epsilon \to \left\langle x \right\rangle_{+}$ as $\epsilon\to0$;
- at $x=0$ the tangent is exactly $K_n/2$, never zero --- so an interface
    sitting exactly at zero gap (which is the initial state of every fracture
    in a pre-stressed specimen) still contributes stiffness to the Jacobian;
- the price is a spurious traction of order $K_n\epsilon/2$ on a genuinely
    open interface, so $\epsilon$ must be small compared with any aperture of
    interest.

A related smooth maximum is used for state variables:

<a id="eq-smoothmax"></a>

$$
\max{}_\epsilon(a,b) = \tfrac12\Big(a+b+\sqrt{(a-b)^2+\epsilon^2}\Big),
\qquad
w_a = \frac{\partial \max_\epsilon}{\partial a} = \tfrac12\left(1+\frac{a-b}{\sqrt{(a-b)^2+\epsilon^2}}\right).
$$

The weight $w_a$ is used to blend derivatives consistently across the switch.

**Figure.** The smooth positive part [`eq:smoothpos`](#eq-smoothpos). Smaller $\epsilon$ is more accurate but restores the stiff kink.

<details>
<summary>Original TikZ/PGFPlots source</summary>

```latex
\begin{tikzpicture}
\begin{axis}[width=11cm,height=6cm,
  xlabel={$x$}, ylabel={$\langle x\rangle_+$},
  domain=-1:1, samples=200, legend pos=north west,
  grid=both, grid style={gray!20}]
\addplot[black,thick,domain=-1:1,samples=400]{max(x,0)};
\addlegendentry{exact $\max(x,0)$}
\addplot[red,thick,dashed]{0.5*(x+sqrt(x^2+0.04))};
\addlegendentry{$\epsilon=0.2$}
\addplot[blue,thick,dotted]{0.5*(x+sqrt(x^2+0.0025))};
\addlegendentry{$\epsilon=0.05$}
\end{axis}
\end{tikzpicture}
```

</details>

### Nonlinear normal closure
<a id="ch-closure"></a>
#### Why linear penalty is not enough

A real rock joint does not have a constant normal stiffness. As it closes, more
asperities come into contact and the stiffness rises steeply. Bandis, Lumsden
and Barton (1983) showed the closure–stress relation is well described by a
hyperbola

<a id="eq-bbclosure"></a>

$$
c(\sigma_n) = \frac{V_m \sigma_n}{\sigma_0 + \sigma_n},
\qquad \sigma_0 = K_{ni} V_m ,
$$

where $c$ is the closure, $V_m$ the maximum closure, and $K_{ni}$ the initial
(low-stress) normal stiffness. Inverting,

$$
\sigma_n(c) = \sigma_0 \left(\frac{c}{V_m - c}\right),
$$

which the code generalises to a power law

<a id="eq-powerlawclosure"></a>

$$
\boxed{\;
\sigma_n(c) = \big(K_{ni}V_m\big)\left(\frac{c}{V_m-c}\right)^{1/p} \;}
$$

with exponent $p\ge1$ (`normal_closure_stress_exponent`). The tangent
stiffness is

$$
K_n(c) = \frac{\,\mathrm{d}\sigma_n}{\,\mathrm{d} c}
 = \frac{\sigma_0}{p}\left(\frac{c}{V_m-c}\right)^{1/p-1}\frac{V_m}{(V_m-c)^2}.
$$

**Why the exponent matters.** At $\sigma_n\gg\sigma_0$, $p=1$ gives
$K_n\propto\sigma_n^2$, so the stiffness can rise by at most $(\sigma_{hi}/\sigma_{lo})^2$
over a stress range. Measured unloading branches often stiffen faster than this.
A power law with $p>1$ gives $K_n\propto\sigma_n^{p+1}$ --- a ceiling of
$(\sigma_{hi}/\sigma_{lo})^{p+1}$ --- while remaining bounded by $V_m$, which an
exponential law is not. Boundedness matters because the aperture feeds the
permeability, which feeds the pressure, which feeds back on the aperture: an
unbounded closure law makes that loop unstable.

**Figure.** Normal closure laws. All are bounded by $c\to V_m$. Larger $p$ gives a softer response at low stress and a much stiffer one near $V_m$.

<details>
<summary>Original TikZ/PGFPlots source</summary>

```latex
\begin{tikzpicture}
\begin{axis}[width=12cm,height=6.4cm,
  xlabel={normal closure $c/V_m$}, ylabel={$\sigma_n/\sigma_0$},
  domain=0.001:0.9, samples=200, ymax=12, legend pos=north west,
  grid=both, grid style={gray!20}]
\addplot[blue,thick]{x/(1-x)};
\addlegendentry{$p=1$ (hyperbola)}
\addplot[red,thick,dashed]{(x/(1-x))^(1/2)};
\addlegendentry{$p=2$}
\addplot[green!50!black,thick,dotted]{(x/(1-x))^(1/3.28)};
\addlegendentry{$p=3.28$}
\addplot[black,thin,domain=0:0.9]{8*x};
\addlegendentry{linear penalty}
\end{axis}
\end{tikzpicture}
```

</details>

#### Pre-seating

A fracture in a specimen that has already been loaded to the in-situ stress is
*not* at zero closure when the simulation starts. The
`normal_closure_offset` $c_0$ shifts the origin:

$$
c = c_0 - g_n \;(+\,g_n^{p}\ \text{if dilation is kinematic}),
$$

so that at $g_n=0$ the joint already carries $\sigma_n(c_0)$. This is important:
without it, the first time step must generate the entire in-situ closure from
scratch, dumping a large transient into the model.

**Consequence for interpretation:** once $c_0\neq0$, the displacement jump
$g_n$ measures *change* in aperture relative to the pre-loaded state, not
absolute aperture. This is exactly what an LVDT measures, so it is the right
quantity to compare with experiment --- but it must be remembered when
constructing the hydraulic aperture.

#### Numerical guards in the closure law

`OrcaNormalClosure` is the single shared implementation. Three guards:

1. **Cap.** $c$ is limited to $f_{\max}V_m$ (default $f_{\max}=0.999$),
    beyond which the tangent is set to zero. Without this, $\sigma_n\to\infty$
    as $c\to V_m$.
1. **Linearisation at small closure.** For $c$ below
    $\min(10^{-9}, 0.01V_m)$ the law is replaced by a straight line through
    the origin with the secant stiffness at that point, because for $p>1$ the
    exact tangent $c^{1/p-1}$ is singular as $c\to0$.
1. **Smooth positive part.** The closure is computed
    through [`eq:smoothpos`](#eq-smoothpos).

### Interface elasto-plasticity
<a id="ch-plasticity"></a>
This chapter is the conceptual core. It is written assuming you know
elasto-plasticity of continua but have not seen the interface version.

#### Additive decomposition

Exactly as in continuum plasticity, the local jump is split into recoverable and
irrecoverable parts:

$$
\boldsymbol{g} = \boldsymbol{g}^{e} + \boldsymbol{g}^{p},
\qquad
\boldsymbol{g}^{p} = \big(g_n^{p},\; \boldsymbol{g}_t^{p}\big).
$$

The interface tractions are generated by the *elastic* part only,

<a id="eq-elasticlaw"></a>

$$
\boldsymbol{t}_t = K_t\big(\boldsymbol{g}_t - \boldsymbol{g}_t^{p}\big),
\qquad
t_n = -\,\sigma_n\big(c\big),\quad c = c_0 + g_n^p - g_n .
$$

Here $K_t$ is the tangential penalty (`penalty_tangent`), the shear
analogue of $K_n$. Note the asymmetry: the shear response is a linear spring,
the normal response is the nonlinear closure law of Chapter [`ch:closure`](#ch-closure).

#### The yield surface

Frictional sliding begins when the shear traction magnitude reaches the
Mohr--Coulomb strength:

<a id="eq-yield"></a>

$$
\boxed{\;
F(\boldsymbol{t},\boldsymbol{q}) \;=\; \lVert \boldsymbol{t}_t\rVert \;-\; Y(\boldsymbol{q}) \;\le\; 0,
\qquad
Y = c_{\text{coh}} + \mu\,\sigma'_n \;}
$$

where $\sigma'_n = p_c$ is the effective contact pressure (compression positive),
$\mu$ the friction coefficient, $c_{\text{coh}}$ the cohesion, and $\boldsymbol{q}$ the
set of internal (hardening) variables.

In the traction plane $(\sigma'_n, \tau)$ this is a *cone*: a wedge opening
to the right with half-angle $\arctan\mu$, apex at $\sigma'_n=-c_{\text{coh}}/\mu$.

<a id="fig-yieldsurface"></a>

**Figure.** Yield surfaces in the traction plane. Injection moves the state *left* at constant $\tau$ (raising $p$ lowers $\sigma'_n$) until it meets the envelope. A linear Mohr--Coulomb envelope and a curved Barton--Bandis envelope can be tangent at one stress but diverge badly elsewhere --- which is precisely why the choice of envelope matters for a test that sweeps $\sigma'_n$ over a wide range.

<details>
<summary>Original TikZ/PGFPlots source</summary>

```latex
\begin{tikzpicture}[scale=1.0]
\begin{axis}[width=12.5cm,height=7cm,
  xlabel={effective normal stress $\sigma'_n$ (compression $+$)},
  ylabel={shear traction $\tau$},
  xmin=0,xmax=40,ymin=0,ymax=26,
  grid=both,grid style={gray!20},legend pos=north west]
\addplot[blue,very thick,domain=0:40]{0.8*x + 2};
\addlegendentry{Mohr--Coulomb peak, $Y=c+\mu_p\sigma'_n$}
\addplot[blue,thick,dashed,domain=0:40]{0.35*x};
\addlegendentry{Mohr--Coulomb residual, $Y=\mu_r\sigma'_n$}
\addplot[red,very thick,domain=0.6:40,samples=120]
  {x*tan(30 + 12*log10(150/x))};
\addlegendentry{Barton--Bandis, $Y=\sigma'_n\tan(\phi_r+\mathrm{JRC}\log_{10}\frac{\mathrm{JCS}}{\sigma'_n})$}
\addplot[black,thick,-{Latex[length=2.5mm]}] coordinates {(31,12.2) (16,12.2)};
\node at (23,13.4) {\small stress path: injection};
\fill (31,12.2) circle (2.2pt);
\fill (16,12.2) circle (2.2pt);
\node[below right] at (31,12.2) {\scriptsize start};
\node[above left] at (16,12.2) {\scriptsize slip};
\end{axis}
\end{tikzpicture}
```

</details>

#### The flow rule: associative vs non-associative
<a id="sec-flowrule"></a>
The flow rule states the *direction* of the plastic jump increment. An
*associative* rule takes the gradient of the yield function itself,

$$
\Delta\boldsymbol{g}^{p} = \Delta\gamma\,\frac{\partial F}{\partial \boldsymbol{t}}
 \quad\Longrightarrow\quad
\Delta g_n^p = \Delta\gamma\,\frac{\partial F}{\partial \sigma'_n} = \Delta\gamma\,\mu .
$$

That is, associativity would force the dilation rate to equal the friction
coefficient, $\,\mathrm{d} g_n^p/\,\mathrm{d}\gamma = \mu$. For rock joints this is
*physically wrong* --- measured dilation angles $\psi$ are much smaller than
friction angles $\phi$. So the code uses a **non-associative** rule with a
separate plastic potential

$$
G = \lVert\boldsymbol{t}_t\rVert - \tan\psi\,\sigma'_n ,
$$

giving

<a id="eq-flowrule"></a>

$$
\boxed{\;
\Delta\boldsymbol{g}_t^{p} = \Delta\gamma\,\boldsymbol{m},\qquad
\boldsymbol{m} = \frac{\boldsymbol{t}_t^{\,\text{trial}}}{\lVert \boldsymbol{t}_t^{\,\text{trial}}\rVert},
\qquad
\Delta g_n^{p} = \Delta\gamma\,\tan\psi \;}
$$

with $\psi\neq\phi$ in general.

> **Remark: The price of non-associativity.**
>
> Non-associative plasticity has a non-symmetric consistent tangent and can lose
> uniqueness. In practice this shows up as harder convergence near the slip
> threshold, which is one reason the viscous regularisation of
> Section [`sec:viscosity`](#sec-viscosity) exists.

**The slip direction.** $\Delta\gamma\ge0$ is the plastic multiplier ---
the **equivalent plastic slip increment**. Its accumulation

$$
s = \int \Delta\gamma
$$

is the interface analogue of equivalent plastic strain, and it is the single
scalar that drives all the hardening/softening laws. It is exported as
`cumulative_plastic_slip`. It is monotonically non-decreasing by
construction, even under reversed loading, which is exactly what you want for a
wear/damage measure.

#### Hardening and softening
<a id="sec-hardening"></a>
The strength $Y$ is not constant. Two mechanisms are used.

**Roughness degradation (Model A).** A normalised roughness state
$R\in[R_r,1]$ decays exponentially with slip,

<a id="eq-roughdecay"></a>

$$
R(s) = R_r + (R_0 - R_r)\exp\!\left(-\frac{s}{L_R}\right),
$$

and the friction and cohesion interpolate between “rough” and “smooth”
endpoints through a normalised variable $\bar R$:

<a id="eq-roughinterp"></a>

$$
\bar R = \frac{R-R_r}{1-R_r},\qquad
\mu(\bar R) = \mu_s + (\mu_r - \mu_s)\,\bar R^{\,m_\mu},\qquad
c(\bar R) = c_s + (c_r - c_s)\,\bar R^{\,m_c}.
$$

This is *softening*: $\mu$ falls from a peak to a residual over a
characteristic slip distance $L_R$.

**JRC mobilisation and Barton--Bandis (Models B--D).** Barton's
empirical envelope

<a id="eq-barton"></a>

$$
\boxed{\;
\tau_{\text{peak}} = \sigma'_n \tan\!\left[\phi_r + \mathrm{JRC}\,\log_{10}\!\left(\frac{\mathrm{JCS}}{\sigma'_n}\right)\right] \;}
$$

makes the friction angle itself stress-dependent: at low $\sigma'_n$ the
roughness term is large (asperities override), at high $\sigma'_n$ it vanishes
(asperities shear through). This is the curved envelope in
Fig. [`fig:yieldsurface`](#fig-yieldsurface). Scale corrections
$\mathrm{JRC}_n = \mathrm{JRC}_0 (L_n/L_0)^{-0.02\,\mathrm{JRC}_0}$ and
$\mathrm{JCS}_n = \mathrm{JCS}_0 (L_n/L_0)^{-0.03\,\mathrm{JRC}_0}$ translate
laboratory-scale values to the modelled joint length.

<a id="fig-shearcurve"></a>

**Figure.** Schematic shear response. Before yield the interface is a linear spring of stiffness $K_t$ (“stick”); at $Y_p$ it yields; thereafter the strength decays toward $Y_r$ over the characteristic distance $L_R$. **This is the curve to compare with a direct-shear experiment.** The peak is set by $\mu_r$/JRC, the residual by $\mu_s$/$\phi_r$, and the decay rate by $L_R$.

<details>
<summary>Original TikZ/PGFPlots source</summary>

```latex
\begin{tikzpicture}
\begin{axis}[width=13cm,height=6.6cm,
  xlabel={equivalent plastic slip $s$ ($\mu$m)},
  ylabel={shear traction $\tau$ (MPa)},
  xmin=0,xmax=120,ymin=0,ymax=15,
  grid=both,grid style={gray!20},legend pos=north east]
\addplot[black,very thick,samples=300,domain=0:120]
  { x<2 ? 6*x : 12*(0.35 + 0.65*exp(-(x-2)/35)) };
\addlegendentry{$\tau(s)$}
\addplot[gray,dashed,domain=0:120]{12};
\addlegendentry{peak strength $Y_p$}
\addplot[gray,dotted,domain=0:120]{4.2};
\addlegendentry{residual strength $Y_r$}
\node[anchor=west] at (axis cs:3,13.4) {\scriptsize elastic (stick): slope $K_t$};
\draw[-{Latex[length=2mm]}] (axis cs:20,13) -- (axis cs:8,12.4);
\node[anchor=west] at (axis cs:45,9.5) {\scriptsize slip-weakening, distance $L_R$};
\end{axis}
\end{tikzpicture}
```

</details>

> **Remark: Softening and stability.**
>
> Softening plasticity is conditionally stable. If the strength drop per unit slip
> exceeds the elastic unloading stiffness of the surrounding system,
>
> $$
> \left|\frac{\,\mathrm{d} Y}{\,\mathrm{d} s}\right| > k_{\text{sys}} ,
> $$
>
> the quasi-static problem has no stable solution branch --- the fracture wants to
> run away dynamically. In a quasi-static code this appears as a collapsing time
> step. Any calibration that sets a large strength drop $\Delta Y$ over a short
> distance $w$ is flirting with $\Delta Y/w > k_{\text{sys}}$; check that ratio
> before blaming the solver.

#### Dilatancy and its thermodynamic limit
<a id="sec-dilatancy"></a>
Slip over asperities pushes the walls apart. The geometric statement is
[`eq:flowrule`](#eq-flowrule): $\Delta g_n^p = \Delta\gamma\tan\psi$. The dilation angle
itself decays with slip as the asperities wear,

$$
\psi(s) = \psi_r + (\psi_p - \psi_r)\exp\!\left[-\left(\frac{s}{L_\psi}\right)^{m_\psi}\right].
$$

**The dissipation constraint.** Plastic work must be non-negative. The
frictional sliding does work $\tau\,\Delta\gamma$; the dilation does work
*against* the normal stress, $p_c\,\Delta g_n^p$. The second law requires

<a id="eq-dissipation"></a>

$$
\boxed{\;
p_c\,\Delta g_n^{p} \;\le\; (1-\epsilon_D)\; Y\,\Delta\gamma \;}
$$

with a margin $\epsilon_D\in[0,1)$ (`dissipation_margin`). Rearranged,

<a id="eq-dilationbound"></a>

$$
\frac{\Delta g_n^{p}}{\Delta\gamma} \le (1-\epsilon_D)\frac{Y}{p_c}
\approx (1-\epsilon_D)\,\mu
\quad\Longrightarrow\quad
\tan\psi \le (1-\epsilon_D)\,\mu .
$$

**This is a genuine physical bound, and it is often the active constraint.**
If the user specifies $\psi$ larger than $\arctan[(1-\epsilon_D)\mu]$, the
limiter --- not the dilation angle --- sets the realised dilation. In that regime
the reported $\psi$ is decorative and $\,\mathrm{d} g_n^p/\,\mathrm{d}\gamma \approx (1-\epsilon_D)\mu$.
Always check the realised ratio against the nominal $\tan\psi$ before quoting a
calibrated dilation angle.

> **Scope: which laws enforce this.** Added 2026-08-16, because the manuscript
> draft had generalised it and should not have. `dissipation_margin` is declared in
> exactly one material —
> `ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile` (Model A) —
> and its header and implementation are the only place
> [`eq:dissipation`](#eq-dissipation) appears in the code. **The Barton--Bandis
> FastAD family does not enforce it.** That law bounds $\psi$ with
> `min_dilation_angle_degrees` / `max_dilation_angle_degrees` and evolves it through
> the mobilisation/decay law above; the dissipation inequality is never formed. So
> for every Ye & Ghassemi production deck, all of which run
> `OrcaBartonBandisContactTractionFastADHardening`, this bound is *not* active and
> the "often the active constraint" sentence does not apply. The only decks that set
> `dissipation_margin` are the Mohr--Coulomb baselines `67_11` and `83_11`. SW-S3's
> Barton--Bandis decks mention the parameter only in comments, one of which reads
> `# UNUSED after PST swap`.
>
> The bound remains a useful *diagnostic* even where it is not enforced. Applied to
> Ye & Ghassemi's Table 2, $\arctan(|d_n|/d_s)$ over the loading path gives 16.4°
> (SW-T1) and 14.0° (SW-T2) against mobilised $\arctan\mu$ of 49.4° and 51.7° —
> comfortable — but 31.8° (SW-S3) and 28.7° (SW-S4) against 31.3° and 24.6°. On both
> saw cuts the published dilation angle **exceeds** the friction angle the specimen
> mobilises, which read as pure shear dilation would be inadmissible. The resolution
> is that on a low-$\mu$ saw cut the measured $d_n$ is not shear dilation alone: it
> contains the elastic decompression of the joint as $\sigma'_n$ halves over the
> injection cycle. A rough tensile fracture with $\mu > 1$ has the headroom for the
> distinction not to matter; a lapped saw cut with $\mu \approx 0.46$ does not.

> **Remark: What belongs in the work budget.**
>
> The right-hand side of [`eq:dissipation`](#eq-dissipation) must be the *Coulomb friction*
> work $Y\Delta\gamma$. If instead one uses the full branch traction
> $\tau^{\text{trial}} - K_t\Delta\gamma$, which at convergence equals
> $Y + \eta_t\Delta\gamma/\Delta t + \tau_{rs}$, then the viscous and
> rate-and-state regularisations inflate the admissible dilation --- a numerical
> parameter silently controlling a physical one.

#### Kinematic vs compliant dilation
<a id="sec-kinematicdilation"></a>
There are two ways to make dilation act, and they give opposite signs.

- **Compliant (softening).** Treat the accumulated dilation as a reduction of
    the contact stress at fixed jump. Then as the fracture dilates, $\sigma_n$
    *falls*, strength falls, slip accelerates. The fracture does not visibly
    open.
- **Kinematic (hardening, `dilation_opens_joint = true`).** Treat the
    accumulated dilation $g_n^p$ as a normal *eigen-opening*: the closure
    becomes $c = c_0 + g_n^p - g_n$. At fixed jump, dilating *increases*
    closure and hence $\sigma_n$; the fracture must physically push its walls
    apart to relieve it, so the displacement field opens.

The kinematic form is the physical one: riding up an asperity separates the
walls. It is also the only one that produces a normal displacement jump
comparable with an LVDT dilation measurement.

> **Remark: Consequence for the aperture bookkeeping.**
>
> Under kinematic dilation, $g_n$ *already contains* the dilation. Adding a
> separate “cumulative dilation” term to the hydraulic aperture therefore counts
> it twice. This is the single most common wiring error in this framework.

#### Cohesive damage (the tensile branch)

For an initially intact interface, a bilinear traction–separation law is
available. Define an effective separation mixing normal opening and shear,

$$
\delta = \sqrt{\left\langle g_n \right\rangle_{+}^2 + \beta_c^2\lVert\boldsymbol{g}_t\rVert^2},
$$

track its monotone maximum $\kappa=\max_t \delta$, and define damage

<a id="eq-damage"></a>

$$
D(\kappa) =
\begin{cases}
0, & \kappa\le\delta_0,\\[4pt]
\dfrac{\delta_f(\kappa-\delta_0)}{\kappa(\delta_f-\delta_0)}, & \delta_0<\kappa<\delta_f,\\[8pt]
1, & \kappa\ge\delta_f .
\end{cases}
$$

The cohesive traction is then $(1-D)K_c\,\left\langle g_n - g_n^p \right\rangle_{+}$ in the normal
direction and $(1-D)K_c\beta_c^2\boldsymbol{g}_t$ in shear, with
$K_c = T_0/\delta_0$. The fracture energy is $G_c = \tfrac12 T_0\delta_f$.

For a *pre-existing* fracture (the laboratory case) one sets
`enable_tensile_cohesion = false`, which initialises $D=1$: the interface
is fully damaged from the start and behaves as a pure frictional contact. The
cohesive machinery is then inert.

**Figure.** Bilinear cohesive law. Unloading follows a secant to the origin (damage, not plasticity): no permanent separation is left behind.

<details>
<summary>Original TikZ/PGFPlots source</summary>

```latex
\begin{tikzpicture}
\begin{axis}[width=8.5cm,height=5.4cm,
  xlabel={effective separation $\delta$},ylabel={cohesive traction},
  xmin=0,xmax=1.1,ymin=0,ymax=1.15,xtick={0,0.2,1.0},
  xticklabels={$0$,$\delta_0$,$\delta_f$},ytick={0,1},yticklabels={$0$,$T_0$},
  grid=both,grid style={gray!20}]
\addplot[blue,very thick] coordinates {(0,0) (0.2,1) (1.0,0)};
\addplot[red,dashed,thick] coordinates {(0,0) (0.55,0.5625)};
\node at (axis cs:0.62,0.85) {\scriptsize secant unloading};
\node at (axis cs:0.5,0.15) {\scriptsize $G_c=\tfrac12 T_0\delta_f$};
\end{axis}
\end{tikzpicture}
```

</details>

#### Rate-and-state friction
<a id="sec-rsf"></a>
To reproduce the transition between stable creep and unstable slip, a
regularised rate-and-state term can be added. Its standard form is

$$
\mu_{rs} = a \,\operatorname{arcsinh}\!\left[\frac{V}{2V_0}
   \exp\!\left(\frac{\mu_0 + b\ln(V_0\theta/D_c)}{a}\right)\right],
$$

with $V=\Delta\gamma/\Delta t$ the slip rate and $\theta$ a state variable
obeying the ageing law

<a id="eq-aging"></a>

$$
\dot\theta = 1 - \frac{V\theta}{D_c}
\quad\Longrightarrow\quad
\theta_{n+1} = \theta_n e^{-x} + \frac{D_c}{V}\big(1-e^{-x}\big),\quad x = \frac{\Delta\gamma}{D_c},
$$

integrated exactly over a step at constant $V$.

In Model A the term is written as a *perturbation about* the Coulomb
strength rather than an absolute addition:

<a id="eq-rsfref"></a>

$$
\Delta Y_{rs} = p_c\,a\left[\operatorname{arcsinh}\!\left(\frac{V}{2V_0}
  \Big(\frac{V_0\theta}{D_c}\Big)^{b/a}\right) - \operatorname{arcsinh}\tfrac12\right],
$$

so that at steady sliding $V=V_0$, $\theta=D_c/V_0$ the term vanishes exactly and
the roughness law alone sets the strength. Without the reference subtraction, a
constant multi-MPa offset would be added at every slip rate.

**Stability.** $a>b$ gives velocity strengthening (stable creep);
$a<b$ velocity weakening (potential stick–slip). Because the raw referenced form
is *negative* as $V\to0$ (by $0.481\,a\,p_c$), the stick/slip transition is
non-monotone and the global Newton can limit-cycle across it during re-sticking.
An optional clamp at zero removes this at the cost of the small $V<V_0$
weakening.

## Part V: The four constitutive laws

### Overview and rationale

| Class | Strength law | Why it exists |
| --- | --- | --- |
| `...CompressionTensile` (Model A) | linear Mohr--Coulomb with roughness-interpolated $\mu,c$ | The baseline. Simple, transparent, few parameters. Its *failure* mode --- a straight envelope cannot fit a curved one across a wide $\sigma'_n$ sweep --- is the scientific point being made. |
| `...BartonBandisContactTractionFastAD(Hardening)` (Model B) | Barton--Bandis curved envelope $+$ exponential slip weakening | The physically-motivated alternative: nonlinear closure *and* nonlinear strength from the same JRC/JCS pair. |
| `...BartonBandisFlowRSFContactTraction` (Model C) | BB with mobilised JRC, staircase shelves, rate-and-state | Adds slip-history mobilisation and RSF for burst timing. |
| `...PeakShelfTailFlowRSFContactTraction` (Model D) | three-stage $\mu$: peak $\to$ shelf $\to$ tail, plus RSF | A phenomenological law that decouples the three observed stages of the strength history so each can be fitted independently. |

### Model A: cohesive–contact–friction with decoupled dilation
<a id="ch-modelA"></a>
This is the most fully documented law and the one whose algorithm is worth
learning first.

#### Composite traction

The interface is a *mixture* of an intact cohesive fraction $(1-D)$ and a
damaged frictional fraction $D$:

<a id="eq-tA0"></a>
<a id="eq-tA12"></a>

$$
\begin{aligned}
t_0 &= \underbrace{(1-D)K_c\left\langle g_n-g_n^p \right\rangle_{+}}_{\text{cohesive tension}}
       \;-\; \underbrace{p_c}_{\text{contact}} , \\
t_{1,2} &= \underbrace{(1-D)K_c\beta_c^2\,g_{t\,1,2}}_{\text{cohesive shear}}
       \;+\; \underbrace{D\,K_t\big(g_{t\,1,2}-g^{p}_{t\,1,2}\big)}_{\text{frictional shear}} .
\end{aligned}
$$

Note that the cohesive normal tension acts only on the gap *beyond* the
dilated contact surface, $\left\langle g_n-g_n^p \right\rangle_{+}$: cohesion and contact are mutually
exclusive in the normal direction, which is both physical and necessary for the
dilation work to be conjugate to the full contact traction.

#### The local residual system
<a id="sec-localsystem"></a>
Given the trial state, the unknowns of the local problem are the plastic
multiplier $\Delta\gamma$ and the normal plastic jump $g_n^p$. Two equations:

<a id="eq-F1"></a>
<a id="eq-F2"></a>

$$
\begin{aligned}
F_1 &= \tau^{\text{trial}} - K_t\Delta\gamma - Y(\Delta\gamma,g_n^p)
       - \frac{\eta_t}{\Delta t}\Delta\gamma - \tau_{rs}(\Delta\gamma,g_n^p) = 0,
       \\
F_2 &= g_n^{p} - g_{n,\text{old}}^{p} - \Delta g_n^{p}(\Delta\gamma,g_n^p) = 0 .
\end{aligned}
$$

$F_1$ is the *consistency condition*: the state must return exactly onto
the yield surface. $F_2$ is the *flow rule* for the normal direction,
including the dissipation limiter of Section [`sec:dilatancy`](#sec-dilatancy). The two are coupled
because $\Delta g_n^p$ changes the closure, which changes $p_c$, which changes
$Y$.

The Jacobian is

<a id="eq-localjac"></a>

$$
\mathbf{J} =
\begin{bmatrix}
\dfrac{\partial F_1}{\partial \Delta\gamma} & \dfrac{\partial F_1}{\partial g_n^p}\\[10pt]
\dfrac{\partial F_2}{\partial \Delta\gamma} & \dfrac{\partial F_2}{\partial g_n^p}
\end{bmatrix}
=
\begin{bmatrix}
-\Big(K_t + \dfrac{\eta_t}{\Delta t} + \dfrac{\partial Y}{\partial\Delta\gamma}
  + \dfrac{\partial\tau_{rs}}{\partial\Delta\gamma}\Big) &
-\Big(\dfrac{\partial Y}{\partial g_n^p} + \dfrac{\partial\tau_{rs}}{\partial g_n^p}\Big)\\[10pt]
-\dfrac{\partial \Delta g_n^p}{\partial\Delta\gamma} &
1-\dfrac{\partial \Delta g_n^p}{\partial g_n^p}
\end{bmatrix},
$$

and the Newton update is

$$
\begin{bmatrix}\delta(\Delta\gamma)\\ \delta g_n^p\end{bmatrix}
= -\mathbf{J}^{-1}\begin{bmatrix}F_1\\F_2\end{bmatrix},
\qquad
\mathbf{J}^{-1} = \frac{1}{\det\mathbf J}
\begin{bmatrix} J_{22} & -J_{12}\\ -J_{21} & J_{11}\end{bmatrix}.
$$

#### Algorithm

**Algorithm A: local return map (per quadrature point, per substep)**

1. Restore the converged state of the previous step:
    $s$, $R$, $g_n^p$, $\boldsymbol{g}_t^p$, $\theta$, $D$, $\kappa$, $\boldsymbol{t}$.
1. Update cohesive damage from the current $\delta$ (Eq. [`eq:damage`](#eq-damage)),
    optionally with Duvaut--Lions relaxation.
1. Compute the contact overlap $c = c_0 + g_{n,\text{old}}^p - g_n$.
    If $c \le$ tolerance **or** $D=0$: the interface is open or fully
    intact --- assemble the traction, mark `Open`/`Stick`, return.
1. Compute the elastic trial shear
    $\boldsymbol{t}_t^{\text{trial}} = K_t(\boldsymbol{g}_t - \boldsymbol{g}_{t,\text{old}}^p)$,
    $\tau^{\text{trial}} = \lVert\boldsymbol{t}_t^{\text{trial}}\rVert$.
1. Evaluate $F_1$ at $\Delta\gamma=0$. If $F_1\le \text{tol}$: elastic
    (`Stick`) --- assemble and return.
1. Otherwise solve [`eq:F1`](#eq-F1)--[`eq:F2`](#eq-F2) by damped Newton with the
    Jacobian [`eq:localjac`](#eq-localjac), clamping $\Delta\gamma\in[0,\tau^{\text{trial}}/K_t]$
    and $g_n^p \ge g^p_{n,\text{old}}$, with a backtracking line search on the
    scaled residual norm.
1. Apply one exact AD Newton step at the converged point to inject the
    implicit sensitivities (Section [`sec:ift`](#sec-ift)).
1. Enforce irreversibility exactly: $g_n^p \ge g^p_{n,\text{old}}$.
1. Update $\boldsymbol{g}_t^p \mathrel{+}= \Delta\gamma\,\boldsymbol{m}$, assemble the
    traction [`eq:tA0`](#eq-tA0)--[`eq:tA12`](#eq-tA12), store state.

#### Event-aware substepping
<a id="sec-substep"></a>
A single global time step may take the interface across a *state boundary*
--- damage initiation, complete failure, or contact activation. Integrating
straight through such a boundary with one return map is inaccurate.

The code therefore parameterises the jump path

$$
\boldsymbol{g}(\lambda) = \boldsymbol{g}_{\text{old}} + \lambda\big(\boldsymbol{g}_{\text{new}} - \boldsymbol{g}_{\text{old}}\big),
\qquad \lambda\in[0,1],
$$

locates the $\lambda$ at which each event occurs (by bisection on
$\delta(\lambda)=\delta_0$, $\delta(\lambda)=\delta_f$, and on the sign change of
the contact overlap), sorts and de-duplicates them, and integrates the return map
segment by segment. If a segment fails to converge it is bisected recursively up
to `max_local_substeps` times; total failure raises a
`MooseException`, which MOOSE catches and converts into a time-step cut.

> **Remark.**
>
> Rate-dependent terms must use the *substep* time increment
> $\Delta t\,(\lambda_{i+1}-\lambda_i)$, not the full $\Delta t$; otherwise the
> answer depends on how many substeps happened to be taken.

### Models B--D

#### Model B: Barton--Bandis FastAD

Same physical skeleton, different strength law and a different numerical
strategy.

**Strength.** $\phi_{\text{peak}} = \phi_r + \mathrm{JRC}_{\text{mob}}\log_{10}(\mathrm{JCS}/\sigma'_n)$,
clamped to $[\phi_{\min},\phi_{\max}]$, with $\mu = \tan\phi_{\text{peak}}$ and
$Y = \sigma'_n\mu$. Optionally the JRC is *mobilised*, ramping from $0$ to
its full value over a peak shear displacement:
$\mathrm{JRC}_{\text{mob}} = \mathrm{JRC}\,\bar s^{\,m}$, $\bar s = \min(s/\delta_p,1)$.

**Slip weakening (the `Hardening` subclass).** On top of the BB
peak, an exponential decay toward a residual:

$$
\mu_{\text{eff}} = \mu_r + (\mu_{\text{BB}} - \mu_r)\exp\!\left[-\left(\frac{s}{D_c}\right)^{m}\right].
$$

**Numerics: the “FastAD” strategy.** Rather than solving the local
problem in AD, this law:

1. solves a *scalar* return map $R(\Delta\gamma)=0$ in plain
    `Real` arithmetic, using a safeguarded Newton bracketed in
    $[0, \tau^{\text{trial}}/(K_t+\eta_t/\Delta t)]$ with bisection fallback;
1. reconstructs the consistent AD tangent *once* after convergence by
    the implicit function theorem (Section [`sec:ift`](#sec-ift)).

This is much cheaper than carrying dual numbers through every iteration. The
cost is that the residual and its AD reconstruction must be kept exactly
consistent by hand.

Inside each residual evaluation, the dilation and the contact pressure are
coupled ($\psi$ depends on $\sigma_n$, which depends on the dilation), so a
small inner fixed-point iteration resolves them:

$$
\psi^{(j+1)} \leftarrow \Psi\big(\sigma_n(\psi^{(j)})\big),
$$

converged on a *relative* tolerance in $\tan\psi$.

#### Model C: Barton--Bandis flow / rate-and-state

Adds to Model B: a multi-shelf “staircase” JRC mobilisation (mobilisation
freezes over prescribed slip windows and then resumes), an apparent cohesion, a
late friction increment, slip-dependent tangential viscosity, and a full
rate-and-state term with an $\operatorname{arcsinh}$ formulation guarded by a
logarithmic branch for large arguments.

#### Model D: peak--shelf--tail

Replaces the physically-derived envelope by a three-stage phenomenological
friction history:

$$
\mu(s):\quad \mu_{\text{peak}} \;\longrightarrow\;
\mu_{\text{shelf}} \;\longrightarrow\; \mu_{\text{tail}},
$$

with a concentration function controlling the first transition and a tail slip
distance the second, plus optional additional “tread” drops at prescribed
slips. Dilation is specified as a fraction of the friction coefficient
(`dilation_work_fraction`) rather than as an angle.

> **Remark: Both RSF laws require $a>0$.**
>
> Models C and D range-check $a>0$ and have no switch to disable rate-and-state.
> Consequently *neither can represent a rate-independent Coulomb interface
> exactly*, and neither can be verified against a rate-independent closed form in
> the strict sense. Setting $a=10^{-9}$ makes the term negligible
> ($\sim0.1$ Pa against $\sim10$ MPa) but it is a workaround, not a reduction.

## Part VI: Numerical algorithms

### Newton--Raphson at two levels

#### The global solve

At each time step, solve $\mathbf R(\mathbf u)=\mathbf 0$ by

$$
\mathbf J(\mathbf u^{(k)})\,\delta\mathbf u = -\mathbf R(\mathbf u^{(k)}),
\qquad
\mathbf u^{(k+1)} = \mathbf u^{(k)} + \alpha\,\delta\mathbf u .
$$

Convergence is quadratic *if* $\mathbf J$ is the exact derivative of
$\mathbf R$. This is why the consistent tangent matters so much: an approximate
Jacobian degrades Newton to linear convergence or stalls it entirely.

Typical healthy output looks like

```text
0 Nonlinear |R| = 6.324147e+05
 1 Nonlinear |R| = 8.573518e+03
 2 Nonlinear |R| = 6.430031e-02
 3 Nonlinear |R| = 1.458056e-05
```

--- roughly squaring the number of correct digits each iteration.

#### The local solve (return map)

At each quadrature point the constitutive law solves its own small nonlinear
system. This is the classical *elastic predictor / plastic corrector*
scheme:

**Diagram.** Source retained from the LaTeX manual.

<details>
<summary>Original TikZ/PGFPlots source</summary>

```latex
\begin{tikzpicture}[scale=1.0]
\begin{axis}[width=10.5cm,height=6.2cm,
  xlabel={$\sigma'_n$},ylabel={$\tau$},
  xmin=0,xmax=30,ymin=0,ymax=22,grid=both,grid style={gray!20},
  legend pos=north west]
\addplot[blue,very thick,domain=0:30]{0.6*x+2};
\addlegendentry{yield surface $F=0$}
\addplot[black,thick,-{Latex[length=2.5mm]}] coordinates {(20,12) (20,19)};
\node[right] at (axis cs:20.4,16.4) {\scriptsize elastic predictor};
\addplot[red,thick,-{Latex[length=2.5mm]}] coordinates {(20,19) (20,14)};
\node[right] at (axis cs:20.4,13.0) {\scriptsize plastic corrector};
\fill (20,12) circle (2pt); \node[below right] at (axis cs:20,12) {\scriptsize $n$};
\fill (20,19) circle (2pt); \node[above right] at (axis cs:20,19) {\scriptsize trial};
\fill[red] (20,14) circle (2pt); \node[below left] at (axis cs:20,14) {\scriptsize $n+1$};
\end{axis}
\end{tikzpicture}
```

</details>

1. **Elastic predictor.** Freeze the plastic state, apply the whole jump
    increment elastically: $\boldsymbol{t}^{\text{trial}} = K_t(\boldsymbol{g}_t - \boldsymbol{g}_{t}^{p,\text{old}})$.
1. **Yield check.** If $F(\boldsymbol{t}^{\text{trial}})\le 0$ the step is
    elastic; accept it.
1. **Plastic corrector.** Otherwise find $\Delta\gamma>0$ such that the
    updated state satisfies $F=0$ exactly. Because the corrector direction is
    fixed by the flow rule, this is a scalar (Model B) or $2\times2$
    (Model A) root-find.

**Why a bracketed method.** $R(\Delta\gamma)$ is monotone decreasing in
$\Delta\gamma$ for a hardening law but need not be for a softening one. Model B
therefore brackets the root in
$[0,\ \tau^{\text{trial}}/(K_t+\eta_t/\Delta t)]$ --- the upper limit being the
slip that would relax the entire trial overstress --- and falls back to bisection
whenever the Newton step leaves the bracket. This is slower per iteration than
pure Newton but cannot diverge.

#### Scale-aware convergence tolerances

An absolute tolerance of $10^{-8}$ Pa on a residual formed as the difference of
two $10^{7}$ Pa quantities is below the double-precision round-off floor
($\sim10^{-9}\times10^7 = 10^{-2}$ Pa) and can never be met. The local solvers
therefore use

$$
\text{tol} = \text{tol}_{\text{abs}} + 10^{-9}\max\big(\tau^{\text{trial}}, \sigma_{\text{reg}}\big),
$$

so the criterion is meaningful at both laboratory (MPa) and unit-test (Pa)
scales. **Any pre-check that decides “elastic vs plastic” must use the
same tolerance as the loop**, or states in between will be routed into the return
map, converge at $\Delta\gamma=0$, and be misreported as slipping.

### Consistent tangents and automatic differentiation
<a id="sec-ift"></a>
#### The problem

The global Jacobian needs $\partial \boldsymbol{t}/\partial [\![\boldsymbol{u}]\!]$. But $\boldsymbol{t}$ is
the output of an *iterative* algorithm, so the naive derivative of the
algorithm is not the derivative of the solution.

#### The implicit function theorem

Let the local system be $\mathbf F(\mathbf x; \boldsymbol{g})=\mathbf 0$ with
$\mathbf x = (\Delta\gamma, g_n^p)$. At a converged point,

<a id="eq-ift"></a>

$$
\frac{\partial\mathbf F}{\partial\mathbf x}\,\frac{\,\mathrm{d}\mathbf x}{\,\mathrm{d} \boldsymbol{g}}
 + \frac{\partial\mathbf F}{\partial \boldsymbol{g}} = \mathbf 0
\quad\Longrightarrow\quad
\boxed{\;\frac{\,\mathrm{d}\mathbf x}{\,\mathrm{d} \boldsymbol{g}} = -\mathbf J^{-1}\frac{\partial\mathbf F}{\partial\boldsymbol{g}}\;}
$$

This is the *consistent* (algorithmic) tangent, and it is what makes global
Newton converge quadratically.

**Two ways to get it.** 

- **Model A: “raw solve + AD corrector”.** Solve the local system on raw
    values (fast, and the line search can make non-differentiable decisions), then
    perform *one* exact Newton step in AD at the converged point. The residual
    values are already below tolerance so the solution barely moves --- but their
    nonzero AD derivatives supply exactly the $-\mathbf J^{-1}\partial\mathbf F/\partial\boldsymbol{g}$
    term that the value-only loop omitted.
- **Model B: explicit IFT.** Evaluate the residual as an `ADReal` at the
    converged $\Delta\gamma$ (treating $\Delta\gamma$ as a constant), then set

    $$
    \widehat{\Delta\gamma} = \Delta\gamma - \frac{\widehat R}{\,\mathrm{d} R/\,\mathrm{d}\Delta\gamma},
    $$

    which carries the right derivatives while leaving the value unchanged to
    round-off.

> **Remark: Guard the corrector.**
>
> Near an ill-conditioned local Jacobian the corrector step can grow far beyond
> the residual-tolerance scale and leave the admissible set (e.g. pushing
> $g_n^p$ below $g_{n,\text{old}}^p$, violating irreversibility). Apply it only
> when its magnitude is consistent with tolerance-scale motion.

#### Guarding $\mathrm{pow}$ and $\sqrt{\cdot}$
<a id="sec-powguard"></a>
Every derivative of the form $p\,x^{p-1}$ must be guarded. For $p=1$ the factor
is exactly $1$, but evaluating it as $\mathrm{pow}(x,0)$ gives NaN at $x=0$ under
*both* dual-number overloads:

$$
\begin{aligned}
\mathrm{pow}(\hat a,\hat b):&\quad \text{derivative} \ni b'\log a
 \;=\; 0\cdot(-\infty) = \mathrm{NaN},\\
\mathrm{pow}(\hat a, b):&\quad \text{derivative} \ni b\,a^{b-1}
 \;=\; 0\cdot(+\infty) = \mathrm{NaN}.
\end{aligned}
$$

The safe form returns the constant directly:

$$
\text{powerRuleFactor}(x,p) =
\begin{cases}
1, & p = 1,\\
p\,\max(x,\varepsilon)^{p-1}, & \text{otherwise.}
\end{cases}
$$

This matters because normalised state variables reach *exactly* zero, not
approximately zero: $\bar R = (R-R_r)/(1-R_r)$ becomes bit-identical to zero as
soon as $(R_0-R_r)e^{-s/L_R}$ underflows below the floating-point spacing of
$R_r$, which happens after only a few slipping steps for a short $L_R$.

> **Remark: The signature to recognise.**
>
> A NaN in the Jacobian leaves the residual finite. The symptom is
> `DIVERGED_NANORINF` reported by the *linear* solver at iteration 0
> while the nonlinear residual converges quadratically, at *every* time-step
> size, under a *direct* solver. If you see that combination, look for an
> unguarded $\mathrm{pow}$ or $\sqrt{\cdot}$ on a quantity that can hit exactly
> zero --- not for a conditioning or step-size problem.

### Regularisation: what it buys and what it costs

#### Viscous (Perzyna) overstress
<a id="sec-viscosity"></a>
Add $\eta_t\Delta\gamma/\Delta t$ to the yield residual [`eq:F1`](#eq-F1). Effects:

- removes the stick/slip kink: the transition becomes smooth in
    $\Delta\gamma$;
- makes the consistent tangent positive-definite near the softening
    instability, so a quasi-static solver can advance *through* a limit
    point instead of collapsing $\Delta t$;
- introduces a rate dependence that is *not* physical: the strength is
    inflated by $\eta_t V$.

Choose $\eta_t$ so that $\eta_t V \ll Y$ at the slip rates of interest, and
always report the value used. It is a numerical parameter with physical
consequences.

#### Smooth active sets

Discussed in Section [`sec:smoothing`](#sec-smoothing). Every hard `if` in a constitutive law is
a kink in the Jacobian. Replacing $\max(a,b)$ by $\max_\epsilon(a,b)$ and
blending the derivatives with the weight $w_a$ of [`eq:smoothmax`](#eq-smoothmax) makes the
law *semismooth* rather than discontinuous, which is enough for Newton.

#### Substepping

Discussed in Section [`sec:substep`](#sec-substep). Cost is linear in the number of substeps;
benefit is that a large displacement increment can be integrated accurately
without cutting the global time step.

#### Why regularisation speeds things up

It is counter-intuitive that adding work per step makes the simulation faster.
The mechanism is:

$$
\text{smoother Jacobian}\;\Rightarrow\;\text{fewer Newton iterations}\;\Rightarrow\;
\text{fewer step rejections}\;\Rightarrow\;\text{larger stable }\Delta t .
$$

A single failed step costs the whole step's work plus a $\Delta t$ cut whose
effect persists for many subsequent steps. Empirically, removing a Jacobian NaN
from one benchmark in this code turned a run that failed after $5.5$ minutes at
$10%$ of the load into one that completed in $27$ seconds --- a $12\times$
speed-up purely from eliminating step rejections.

## Part VII: Fracture hydraulics

### Aperture, permeability and flow
<a id="ch-flow"></a>
#### Two different apertures

This distinction is essential and routinely confused.

- **Mechanical aperture $a_m$.** The actual geometric separation of the walls
    --- what the mechanics solves, i.e. (a function of) the normal jump $g_n$.
- **Hydraulic aperture $a_h$.** The aperture of an equivalent pair of smooth
    parallel plates that would transmit the same flow. Because a real fracture has
    contact areas, tortuosity and roughness, $a_h < a_m$ always, and the ratio is
    not constant.

#### The cubic law

For laminar flow between smooth parallel plates separated by $a_h$, integrating
the Navier--Stokes equations gives the volumetric flux per unit width

<a id="eq-cubiclaw"></a>

$$
\boxed{\;
\boldsymbol{q}_f = -\frac{a_h^3}{12\mu_f}\,\nabla_t p
\;\equiv\; -T\,\nabla_t p ,
\qquad T = \frac{a_h^3}{12\mu_f} \;}
$$

where $\nabla_t$ is the in-plane (tangential) gradient and $T$ is the
*transmissivity* $[\mathrm{m^3/(Pa\,s)}]$. The equivalent fracture
permeability is

$$
k_f = \frac{a_h^2}{12}.
$$

The cubic dependence is why permeability is so sensitive to slip: a $40%$
increase in aperture nearly triples the flow.

#### The aperture model, and why it is written that way

The physically consistent statement, given that the mechanics already solves both
the elastic closure (Chapter [`ch:closure`](#ch-closure)) and the shear dilation
(Section [`sec:kinematicdilation`](#sec-kinematicdilation)), is

<a id="eq-aperture"></a>

$$
\boxed{\;
a_h = a_{h0} \;+\; \left\langle g_n \right\rangle_{+} \;-\; a_{\text{gouge}}(s) \;}
$$

with

<a id="eq-gouge"></a>

$$
a_{\text{gouge}}(s) = a_g\left[1-\exp\!\left(-\frac{\left\langle s-s^* \right\rangle_{+}}{s_c}\right)\right].
$$

**Term by term.** 

- **$a_{h0}$.** The reference hydraulic aperture at the initial stress state.
    This is *not* a geometric quantity: it is back-calculated from the
    measured initial flow rate through [`eq:cubiclaw`](#eq-cubiclaw). It absorbs all the
    roughness/tortuosity reduction at the reference condition.
- **$\left\langle g_n \right\rangle_{+}$.** The *change* in mechanical aperture relative to the
    pre-seated reference state (see Section [`ch:closure`](#ch-closure)). Under kinematic dilation
    this already contains both the stress-driven elastic opening and the
    shear-driven dilation. Clamped at zero: further closure below the reference is
    handled by the mechanics, not by driving $a_h$ negative.
- **$a_{\text{gouge}}$.** Wear products progressively fill the void as the joint
    shears. This is what decouples the hydraulic aperture from the mechanical one
    on the unloading branch: a fracture that has slipped does not recover its
    original conductivity when re-clamped. The onset $s^*$ delays the effect so
    that early slip does not immediately block flow.

> **Remark: What *not* to do.**
>
> It is tempting to add, on top of [`eq:aperture`](#eq-aperture), (i) a separate
> “cumulative dilation” term, and (ii) a second, independently fitted
> Barton--Bandis closure law inside the hydraulic model. Both are already in
> $\left\langle g_n \right\rangle_{+}$. Doing so double-counts the physics and, worse, gives the appearance
> of three independent mechanisms fitting the data when in fact one mechanism is
> being fitted three times.

**Bounds.** A lower bound `min_hydraulic_aperture` prevents
$a_h\le 0$; it must be a small numerical floor, *not* equal to $a_{h0}$,
which would forbid the fracture from ever closing hydraulically. An upper bound
prevents a transient mechanical excursion from blowing up $a_h^3$ and wrecking
the coupled Newton solve.

#### The Reynolds equation on the interface

Mass conservation for the fluid contained between the walls, per unit fracture
area, is

<a id="eq-reynolds"></a>

$$
\frac{\partial}{\partial t}\big(\rho_f a_h\big)
 + \nabla_t\!\cdot\!\big(\rho_f \boldsymbol{q}_f\big) = 0 .
$$

The storage term expands as

$$
\frac{\partial(\rho_f a_h)}{\partial t}
 = \underbrace{\rho_f\frac{\partial a_h}{\partial t}}_{\text{aperture change}}
 + \underbrace{a_h\frac{\rho_f}{K_f}\frac{\partial p}{\partial t}}_{\text{fluid compressibility}} ,
$$

so assembling $\partial(\rho_f a_h)/\partial t$ directly captures both exactly.

`OrcaFractureFlowInterfaceKernel` therefore contributes, on the “element”
side of the interface,

<a id="eq-flowifk"></a>

$$
R^{-}_i \mathrel{+}=
 \underbrace{\frac{(\rho_f a_h)^{n+1}-(\rho_f a_h)^{n}}{\Delta t}\,\psi_i}_{\text{storage}}
 \;+\; \underbrace{\rho_f\,T\,\big(\nabla_t p\cdot\nabla_t\psi_i\big)}_{\text{transport}}
 \;+\; \underbrace{\kappa_p\,(p^- - p^+)\,\psi_i}_{\text{continuity tie}},
$$

and on the neighbour side only the tie, with opposite sign:

$$
R^{+}_i \mathrel{+}= -\,\kappa_p\,(p^- - p^+)\,\psi^{+}_i ,
\qquad
\kappa_p = \frac{\rho_f T}{a_h\,L_p} .
$$

**Why a tie at all.** The two walls bound the *same* fluid body, so
$p^-=p^+$ physically. Rather than introducing a constraint, the code enforces
continuity by a stiff penalty with a length scale $L_p$
(`pressure_penalty_length`). This keeps the system displacement/pressure
only, at the cost of one more numerical parameter whose insensitivity should be
demonstrated.

**Tangential projection.** The in-plane gradient is obtained by removing
the normal component,

$$
\nabla_t p = \nabla p - (\nabla p\cdot\boldsymbol{n})\,\boldsymbol{n} .
$$

> **Remark: Roughness does not steer the flow.**
>
> $T$ is a *scalar*. The model therefore has no in-plane flow anisotropy and
> cannot represent channelling along preferential paths on a rough surface.
> Roughness enters the magnitude of the aperture but not the direction of flow.
> For a laboratory specimen with a well-mated fracture this is defensible; for a
> field-scale rough fracture it is a real limitation and would require a tensorial
> transmissivity.

#### The hydro-mechanical loop

**Diagram.** Source retained from the LaTeX manual.

<details>
<summary>Original TikZ/PGFPlots source</summary>

```latex
\begin{tikzpicture}[node distance=9mm,
  b/.style={draw,rounded corners,align=center,inner sep=5pt,font=\small},
  a/.style={-{Latex[length=2.4mm]},thick}]
\node[b,fill=cyan!10] (p) {injection pressure $\uparrow$};
\node[b,fill=cyan!10,right=14mm of p] (pf) {fracture pressure $p_f\uparrow$};
\node[b,fill=orange!12,right=14mm of pf] (sn) {$\sigma'_n = \sigma_n - p_f \downarrow$};
\node[b,fill=orange!12,below=of sn] (Y) {strength $Y=\mu\sigma'_n \downarrow$};
\node[b,fill=orange!12,left=14mm of Y] (slip) {slip $\Delta\gamma\uparrow$};
\node[b,fill=orange!12,left=14mm of slip] (dil) {dilation $g_n^p\uparrow$};
\node[b,fill=green!12,below=of dil] (ah) {aperture $a_h\uparrow$};
\node[b,fill=green!12,right=14mm of ah] (T) {$T = a_h^3/12\mu_f \uparrow$};
\node[b,fill=green!12,right=14mm of T] (q) {flow rate $\uparrow$};
\draw[a] (p)--(pf); \draw[a] (pf)--(sn); \draw[a] (sn)--(Y);
\draw[a] (Y)--(slip); \draw[a] (slip)--(dil); \draw[a] (dil)--(ah);
\draw[a] (ah)--(T); \draw[a] (T)--(q);
\draw[a,dashed,red] (q.east) to[out=0,in=-40] node[right,font=\scriptsize,align=left]{feedback:\\ easier flow\\ $\Rightarrow$ higher $p_f$} (pf.south east);
\end{tikzpicture}
```

</details>

The dashed path is a *positive feedback*: more aperture means easier flow
means higher pressure deeper into the fracture means lower $\sigma'_n$ means more
slip. Because $T\propto a_h^3$, this loop can run away if the aperture law is
unbounded. This is the practical reason the closure law must saturate at $V_m$
and the aperture must be capped.

## Part VIII: Verification

### The test suite

#### Philosophy: verification vs validation

- **Verification.** --- “are we solving the equations right?” Compare against
    an exact solution of the *same* equations. Errors should be at
    discretisation level and should *converge* under refinement.
- **Validation.** --- “are we solving the right equations?” Compare against
    experiment. Errors reflect model adequacy and calibration.

A code paper needs both, and must not present the second as the first. Every
test below is verification.

#### Bulk poroelasticity

**Terzaghi 1D consolidation.** A saturated column, drained at the top,
loaded instantaneously by $q$. The excess pressure obeys

$$
\frac{\partial p}{\partial t} = c_v\frac{\partial^2 p}{\partial z^2},
\qquad
c_v = \frac{k/\mu_f}{S + \alpha^2 m},\quad
S=\frac1M,\quad m=\frac{1}{K+\tfrac43 G},
$$

with initial value $p_0 = \alpha m q/(S+\alpha^2 m)$ and series solution

$$
p(z,t) = p_0\sum_{n=0}^{\infty}\frac{2}{M_n}\sin\!\Big(M_n\frac{z}{H}\Big)e^{-M_n^2 T_v},
\quad M_n = \frac{(2n+1)\pi}{2},\quad T_v=\frac{c_v t}{H^2}.
$$

**What to expect:** first-order convergence in time (halving $\Delta t$
halves the error), mesh-insensitivity once the spatial error is below the
temporal one. **What it catches:** any error in the storage coefficient
$1/M$ or the coupling coefficient $\alpha$ --- both appear in $c_v$.

**Mandel.** A drained strip compressed between rigid impermeable
platens. The diagnostic feature is the **Mandel--Cryer effect**: the
centre pressure *rises above* its initial undrained value before decaying,
because the stiffer drained edges shed load onto the still-undrained core.
**This overshoot is unreachable unless the poromechanical coupling
coefficient is correct**, which makes Mandel a far sharper test of the coupling
than Terzaghi.

#### Interface constitutive laws (single element)

- **Normal closure.** Load/unload a pre-seated joint. Assert
    $\sigma_n$ equals [`eq:powerlawclosure`](#eq-powerlawclosure) evaluated on the *solved*
    $g_n$. Expect machine precision ($\sim10^{-16}$): the law is algebraic, so any
    deviation is a bug, not discretisation.
- **Coulomb return mapping.** Constant-normal-load direct shear. Assert three
    things: (i) $\tau = Y$ on every slipping step; (ii) $\mu_{\text{eff}}$ matches
    the roughness interpolation [`eq:roughinterp`](#eq-roughinterp); (iii) the dissipation
    bound [`eq:dissipation`](#eq-dissipation) is never violated. Expect $\sim10^{-15}$.
- **Barton--Bandis envelope.** Constant-normal-displacement direct shear.
    Assert closure, the peak envelope [`eq:barton`](#eq-barton), the slip-weakening tail,
    and $\tau=Y$. Expect $\sim10^{-16}$.

> **Remark: Design the driver so the closed form applies.**
>
> Constant-normal-*load* keeps $\sigma_n$ fixed and lets the joint dilate
> freely --- appropriate when testing the friction law. Constant-normal-*displacement* pins the kinematics and lets $\sigma_n$ evolve ---
> appropriate when testing the closure law. Choosing the wrong one makes the
> closed form inapplicable and the “error” meaningless.

#### Fracture flow

Cubic-law test: assert $a_h(t=0)=a_{h0}$ exactly (this pins the stateful
initialisation --- an uninitialised $a_h^{\text{old}}$ injects the entire
reference aperture as a spurious source on the first step), assert
$k_f=a_h^2/12$ and $T=a_h^3/12\mu_f$, and assert the steady pressure profile
along the fracture is linear in the absence of leak-off.

#### Cross-model benchmarks

Two classical problems, each run with *all four* laws reduced to the same
idealised interface. The point is that four independent implementations must
land on the same closed-form answer.

**Sneddon: pressurised crack in an infinite medium.** 

$$
w(s) = \frac{4(1-\nu^2)p_f}{E}\sqrt{b^2-s^2}
\quad\Longrightarrow\quad
w_{\max} = \frac{4(1-\nu^2)p_f b}{E}.
$$

The crack is *open* everywhere, so this tests the CZM kinematics, the
interface-kernel sign convention, the fluid-pressure kernel, and that each law
correctly returns a traction-free open state. Expect a few percent error from
the finite domain and the $\sqrt{r}$-singular tip, but *identical* values
across the four laws.

**Inclined fracture under far-field compression.** 

$$
g_t(s) = \frac{4(1-\nu^2)}{E}\,\sigma\sin\psi\big[\cos\psi-\sin\psi\tan\theta\big]\sqrt{b^2-s^2},
\qquad \sigma_n = -\sigma\sin^2\psi .
$$

Here the fracture is *closed and sliding*, so the amplitude depends on the
friction coefficient through the bracket --- this is the benchmark that actually
exercises the Coulomb return map. Expect a few percent from the same sources,
again identical across laws.

> **Remark: Interpreting the residual error.**
>
> A common offset across all four laws is a property of the *benchmark*
> (finite domain, element order, tip singularity), not of the constitutive laws.
> A *difference between* laws is a code issue. Report both separately, and
> demonstrate the common offset shrinks under refinement.

## Part IX: Practical guide

### What each parameter does, and why

This chapter is the reference for every parameter of the interface constitutive laws: what
equation it enters, what it moves in the output, what it does at each extreme, and — the part
usually missing — which parameters it interacts with, so that a calibration change is not made in
the belief that it is isolated when it is not.

#### How to read this chapter

Each family is presented as a short derivation of *why* the parameter has the effect it has,
followed by a table. The tables carry six columns:

| column | meaning |
| --- | --- |
| **Parameter** | input name, symbol, units |
| **Enters** | the equation it appears in |
| **Moves** | the observable it changes first |
| **Too small** | the failure mode at the low extreme |
| **Too large** | the failure mode at the high extreme |
| **Coupled to** | other parameters whose effect it changes or masks |

Three warnings apply throughout and are repeated where they bite.

1. **A parameter that is saturated against a limiter has no effect.** The dissipation bound
   (§[`sec:dilatancy`](#sec-dilatancy)) and the aperture bounds are the two that most often bind.
   Always check the *realised* quantity, not the nominal input.
2. **Characteristic distances interact through stability, not only through fit.** Shortening any
   weakening distance raises $|\mathrm{d}Y/\mathrm{d}s|$ and moves the calibration toward the
   instability threshold $|\mathrm{d}Y/\mathrm{d}s| > k_{\rm sys}$, with no warning in the
   parameters themselves.
3. **Some parameters are output-only.** They change the reported diagnostic and nothing in the
   residual. Calibrating against them is safe; concluding that the *mechanics* improved is not.

#### The families

| Family | Parameters | Role |
| --- | --- | --- |
| Normal contact | $K_n$, $K_{ni}$, $V_m$, $p$, $c_0$, closure fraction | how the joint closes under $\sigma'_n$ |
| Shear strength | $\mu_r$, $\mu_s$, $c_r$, $c_s$, $m_\mu$, $m_c$, $R_0$, $R_r$, $L_R$ | where the yield surface sits and how it weakens |
| Secondary weakening | $\delta S$, $s^*$, $w$ | a second, sharper strength loss on top of roughness decay |
| Dilation | $\psi_p$, $\psi_r$, $L_\psi$, $m_\psi$, $\epsilon_D$ | how much the joint opens per unit slip |
| Dilation modifiers | $\sigma_{\rm low}$, $\sigma_{\rm high}$ and exponents, $d_{\max}$, $L_d$, $m_d$ | stress-dependent suppression of dilation |
| Strength memory | $\zeta$, $L_m$, $H$, $L_H$ | what strength survives after opening or long slip |
| Rate-and-state | $a$, $b$, $\theta_0$, clamp | optional rate dependence, as a perturbation |
| Reported-only | $C_n$, $\sigma_{\rm ref}$, gates, retention | decomposition of the reported normal displacement |
| Cohesive branch | $T_0$, $\delta_0$, $\delta_f$, $\beta_c$, $\eta_D$ | intact-rock tensile branch, off for a pre-existing joint |
| Hydraulic | $a_{h0}$, $\chi$, $a_g$, $s^*_g$, $s_c$, bounds | mechanical gap $\to$ conductivity |
| Regularisation | $\epsilon_g$, $\epsilon_c$, $\sigma_{\rm reg}$, $\eta_t$, tolerances | numerical admissibility |

---

#### IX.1 Normal contact and closure

**Why it matters more than it looks.** The normal response fixes $\sigma'_n$, and $\sigma'_n$ is
the argument of the strength envelope. An error in the closure law is therefore an error in the
strength, delivered indirectly and easy to misattribute to friction. It also fixes how much of the
axial load path passes through the joint rather than the rock — the series-compliance argument of
the Supplement.

Two branches are available. The **linear penalty** $p_c = K_n\langle -g_n\rangle_+$ is adequate
only when $\sigma'_n$ varies little. The **pre-seated power-law Barton–Bandis** closure

$$
v(\sigma'_n) = V_m\left[1 - \left(1 + \frac{\sigma'_n}{K_{ni}V_m}\right)^{-1/p}\right],
\qquad
\text{closure} = c_0 + \langle -g_n\rangle_+ ,
$$

is required whenever the experiment sweeps $\sigma'_n$ by a factor of two or more, as an injection
test does. Its tangent stiffness at closure $v$ is
$\mathrm{d}\sigma/\mathrm{d}v \simeq K_{ni}(1 - v/V_m)^{-(p+1)}$, so the joint stiffens
dramatically as it approaches $V_m$ — which is the physical behaviour and the reason a single
linear $K_n$ cannot represent both ends of the stress path.

**Pre-seating is not optional.** $c_0$ is the closure the joint has already accumulated under the
in-situ confining stress. Without it, applying $\sigma_3$ at $t = 0$ drives a large closure
transient that a compliant loading frame converts into a spurious axial stress excursion, and the
simulation never starts from the state the experiment started from. Set $c_0 = v(\sigma_{n,0})$.

| Parameter | Enters | Moves | Too small | Too large | Coupled to |
| --- | --- | --- | --- | --- | --- |
| `penalty_normal` $K_n$ [Pa/m] | $p_c = K_n\langle -g_n\rangle_+$ | interpenetration; $\sigma'_n$ | excess closure, joint too compliant, $\sigma'_n$ underestimated | ill-conditioning, Newton failure. Target $K_n h/E \sim 10^2$–$10^3$ | $K_t$ (the ratio sets implicit dilation, §[`sec:kinematicdilation`](#sec-kinematicdilation)) |
| `penalty_tangent` $K_t$ [Pa/m] | $\boldsymbol{t}_t = K_t(\boldsymbol{g}_t-\boldsymbol{g}_t^p)$ | pre-yield shear stiffness: the slope of $\tau$ vs $s$ before yield | shear too compliant; apparent pre-slip creep that is numerical | ill-conditioning; and the $K_t/K_n$ ratio sets the spurious implicit dilation | $K_n$; $\eta_t$ (the bracket for the local root-find is $\tau^{\rm trial}/(K_t+\eta_t/\Delta t)$). Zero uses $K_n$. |
| `use_hyperbolic_normal_closure` | selects the branch | the whole $\sigma'_n$ path | — | — | makes $K_n$ a numerical floor rather than the physical stiffness |
| `initial_normal_stiffness` $K_{ni}$ [Pa/m] | closure law | stiffness at low $\sigma'_n$ | joint too soft at the start of unloading; over-recovery | joint effectively rigid; no closure signal | $V_m$: only the product $\sigma_0 = K_{ni}V_m$ sets the half-closure stress |
| `maximum_closure` $V_m$ [m] | closure law | total recoverable closure; **caps** the unload recovery | recovery bounded below the measurement (the SW-T1 BB case) | unbounded closure, joint can be squeezed shut | $K_{ni}$; `normal_unload_retention_fraction` |
| `normal_closure_stress_exponent` $p$ | closure law | curvature | closer to a hyperbola: too stiff at low stress | very soft at low stress, very stiff near $V_m$; strong unload/reload asymmetry | $c_0$ — the pre-seat sits on a steeper part of the curve |
| `normal_closure_offset` $c_0$ [m] | closure $= c_0 + \langle -g_n\rangle_+$ | $\sigma'_n$ at zero jump | $t=0$ not in equilibrium; initial transient | joint starts near $V_m$, tangent stiffness enormous | the applied $\sigma_3$; must equal $v(\sigma_{n,0})$ |
| `maximum_closure_fraction` | numerical cap on $v/V_m$ | — | premature stiffening | division by near-zero in the tangent | $p$ (the tangent diverges as $v\to V_m$) |

**How to recognise a wrong closure law in the output.** The signature is a *stress* error that
tracks the pressure schedule rather than the slip: $\sigma'_n$ drifts from the paper-frame value
during the hold stages, before any slip has occurred. If $\sigma'_n$ is right pre-slip and wrong
post-slip, the closure law is fine and the problem is dilation or the frame.

---

#### IX.2 Shear strength: friction, cohesion, roughness

The Coulomb envelope is $Y = c(\bar R) + \mu(\bar R)\,\sigma'_n$, with both coefficients
interpolating between rough and smooth end members through the normalised roughness

$$
\bar R = \frac{R - R_r}{1 - R_r},
\qquad
R(s) = R_r + (R_0 - R_r)\exp\!\left(-\frac{s}{L_R}\right),
$$

$$
\mu(\bar R) = \mu_s + (\mu_r - \mu_s)\bar R^{\,m_\mu},
\qquad
c(\bar R) = c_s + (c_r - c_s)\bar R^{\,m_c} .
$$

**The division of labour, and it is clean.** Three things are set by three different parameters and
confusing them is the most common calibration error:

- **Onset time** is set by the *peak* strength, i.e. by $\mu_r$ and $c_r$ (and $R_0$), because
  onset happens while $\bar R \approx 1$. It is *not* set by $L_R$.
- **Final slip magnitude** is set by the *strength drop*, $Y_{\rm peak} - Y_{\rm res}$, through the
  load-line balance $s_{\rm final} \approx (Y_{\rm peak} - Y_{\rm res})/k_{\rm sys}$. So it is set
  by $\mu_s$ and $c_s$ and by the system stiffness — again not by $L_R$.
- **The shape of the transition** is set by $L_R$, with little effect on either endpoint.

Calibrate in that order. Adjusting $L_R$ to fix an onset error is a common and futile move.

**Why $\mu_r$ and $c_r$ should be scaled together.** At onset $\bar R \approx 1$, so
$Y = c_r + \mu_r\sigma'_n$. Scaling both by the same factor scales the envelope by that factor
*exactly*, at every $\sigma'_n$. Scaling only one rotates the envelope, which changes the relative
onset time of specimens at different confining stress — an unintended coupling if several
specimens are being calibrated with one philosophy.

**The exponents.** $m_\mu, m_c > 1$ delay the weakening: strength stays near peak for longer and
then falls faster. They are a shape control of last resort — prefer $L_R$, which is interpretable
as a physical wear distance.

**$R_0$ and $R_r$.** $R_0 = 1$ means the joint starts fully rough. $R_0 < 1$ represents a surface
already partially worn, and for the saw-cut specimens it is the natural place to encode the
polishing. $R_r$ is the floor; it must be $< 1$ or the interpolation is degenerate.

| Parameter | Enters | Moves | Too small | Too large | Coupled to |
| --- | --- | --- | --- | --- | --- |
| `friction_coefficient_rough` $\mu_r$ | $Y$ at $\bar R = 1$ | **onset time** | slip fires early | slip fires late or never | $c_r$: together they are the envelope. $\sigma'_n$ through the closure law |
| `cohesion_rough` $c_r$ [Pa] | $Y$ at $\bar R = 1$ | onset time, more at low $\sigma'_n$ | as above | as above | $\mu_r$; matters most for the smooth specimens where $\sigma'_n$ is small |
| `friction_coefficient_smooth` $\mu_s$ | $Y$ at $\bar R = R_r$ | **residual strength, final slip** | strength drop too large; slip overshoots; may exceed the stability bound | drop too small; slip arrests early | $k_{\rm sys}$ through the load line |
| `cohesion_smooth` $c_s$ [Pa] | $Y$ at $\bar R = R_r$ | residual strength | — | residual too high | $\mu_s$ |
| `friction_roughness_exponent` $m_\mu$ | $\mu(\bar R)$ | shape of weakening | — | weakening delayed then abrupt; raises $|\mathrm{d}Y/\mathrm{d}s|$ | $L_R$ and the stability bound |
| `cohesion_roughness_exponent` $m_c$ | $c(\bar R)$ | shape | — | as above | $L_R$ |
| `initial_roughness` $R_0$ | $R(0)$ | initial strength | starts partly weakened; earlier onset | — | $\mu_r$: $R_0<1$ means the peak is not $\mu_r$ |
| `residual_roughness` $R_r$ | floor of $R$ | residual strength | approaches $\mu_s$ | never reaches $\mu_s$; residual too high | $\mu_s$ |
| `roughness_decay_distance` $L_R$ [m] | $R(s)$ | **rate of the drop** | $\lvert\mathrm{d}Y/\mathrm{d}s\rvert > k_{\rm sys}$: no stable branch, $\Delta t$ collapses | drop too gradual; slip continues into later stages | $k_{\rm sys}$, $\eta_t$, $m_\mu$ |

**Identifiability.** $L_R$ is constrained only by an observable that resolves the transition. In a
specimen whose stress drop occupies a single hold stage, any $L_R$ shorter than that stage gives an
identical tabulated result, and a fitted value is not a measurement. Report which specimens
constrain it.

---

#### IX.3 Secondary weakening

An optional second strength loss applied *on top of* the roughness weakening:

$$
Y \;\mathrel{-}=\; \delta S\left[1 - \exp\!\left(-\frac{\langle s - s^{*}\rangle_+}{w}\right)\right].
$$

It exists because a single exponential cannot produce a "gradual, then sudden" drop — the pattern
seen when an asperity population collapses near peak injection. Keyed on cumulative slip, so it is
irreversible and the residual stays low.

| Parameter | Enters | Moves | Too small | Too large | Coupled to |
| --- | --- | --- | --- | --- | --- |
| `secondary_weakening_strength` $\delta S$ [Pa] | $Y$ | magnitude of the second drop | no second drop | residual driven toward zero or negative | $\mu_s$, $c_s$ — the residual is now $Y_{\rm res} - \delta S$ |
| `secondary_weakening_onset_slip` $s^{*}$ [m] | gate | **timing** of the drop | fires during the first weakening; indistinguishable from a smaller $L_R$ | never fires within the test | $L_R$: keep $s^{*} \gtrsim 3L_R$ or the two merge |
| `secondary_weakening_distance` $w$ [m] | gate | **sharpness** | a cliff; almost certainly violates the stability bound | indistinguishable from a slow $L_R$ | $k_{\rm sys}$ |

Use it only when the data genuinely shows two timescales. Otherwise it adds three parameters to fit
one feature.

---

#### IX.4 Dilation, and the limiter that usually overrides it

The flow rule gives $\Delta g_n^p = \Delta\gamma\tan\psi(s)$ with

$$
\tan\psi(s) = \tan\psi_r + (\tan\psi_p - \tan\psi_r)\exp\!\left[-\left(\frac{s}{L_\psi}\right)^{m_\psi}\right],
$$

subject to the dissipation bound [`eq:dilationbound`](#eq-dilationbound),
$\tan\psi \le (1-\epsilon_D)\mu$.

**Read that bound before touching $\psi$.** For a saw cut with $\mu \approx 0.4$–$0.5$ the bound is
$\psi \le 22$–$27^\circ$. A deck specifying $\psi_p = 50^\circ$ does not produce
$\tan 50^\circ = 1.19$; it produces the limiter value $\approx \mu$, and the nominal angle is
inert. In that regime:

- changing $\psi_p$ has **no effect** on the answer;
- changing $\mu$ changes the **dilation**, not only the strength;
- the calibrated $\psi$ reported in a paper is not a property of the joint.

The diagnostic is one line: compare the realised $\Delta g_n^p/\Delta\gamma$ against both
$\tan\psi$ and $(1-\epsilon_D)\mu$. If it equals the second, the limiter is active.

| Parameter | Enters | Moves | Too small | Too large | Coupled to |
| --- | --- | --- | --- | --- | --- |
| `use_dilatancy` | on/off | everything below | no dilation; aperture responds only to $\sigma'_n$ | — | the aperture model |
| `dilation_angle_peak_degrees` $\psi_p$ | flow rule | $\mathrm{d}d_n/\mathrm{d}s$ early | dilation under-predicted; aperture growth short | **no effect once above the bound** | $\mu$, $\epsilon_D$ — the bound |
| `dilation_angle_residual_degrees` $\psi_r$ | flow rule | $\mathrm{d}d_n/\mathrm{d}s$ late | dilation saturates | dilation grows through unloading, where data shows recovery | $L_\psi$ |
| `dilation_decay_distance` $L_\psi$ [m] | $\psi(s)$ | curvature of $d_n$ vs $d_s$ | saturates before peak slip: $d_n$ peak low while $d_s$ is right | keeps growing on unloading | $\psi_p$, $\psi_r$ |
| `dilation_decay_exponent` $m_\psi$ | $\psi(s)$ | shape | — | delayed then abrupt transition | $L_\psi$ |
| `dissipation_margin` $\epsilon_D$ | the bound | the cap itself | bound sits at $\mu$ exactly; marginal admissibility | dilation suppressed below the physical value | $\mu$ — **the bound is $(1-\epsilon_D)\mu$, so $\mu$ controls dilation whenever it binds** |
| `dilation_opens_joint` | routing | **sign of the feedback** | — | — | must be `true`; see §[`sec:kinematicdilation`](#sec-kinematicdilation) |

**Kinematic routing, restated because it is the single most consequential switch.** With
`dilation_opens_joint = true`, $g_n^p$ is a normal eigen-opening: dilating *increases* the contact
overlap and hence $\sigma'_n$, so dilation is *hardening* and the walls physically separate. The
alternative (compliant) routing subtracts dilation from the contact stress, making dilation
*softening* and producing no visible opening. The two give opposite signs for the feedback on
strength, and only the kinematic form produces a normal displacement comparable with an LVDT
record. It also means $g_n$ already contains the dilation — so the hydraulic aperture must not add
a separate cumulative-dilation term.

---

#### IX.5 Dilation support and suppression modifiers

Optional, and off by default. They express that asperity override is not equally available at all
normal stresses: at very low $\sigma'_n$ there is little contact to ride over, and at very high
$\sigma'_n$ asperities crush rather than override.

$$
\text{support} = \left(\frac{p_c}{p_c + \sigma_{\rm low}}\right)^{n_{\rm low}}
\times \left(\frac{\sigma_{\rm high}}{p_c + \sigma_{\rm high}}\right)^{n_{\rm high}}
$$

| Parameter | Enters | Moves | Too small | Too large | Coupled to |
| --- | --- | --- | --- | --- | --- |
| `dilation_support_reference` $\sigma_{\rm low}$ [Pa] | support | dilation at low $\sigma'_n$ | (0 disables) | dilation suppressed over the whole range | $\psi_p$ |
| `dilation_support_exponent` $n_{\rm low}$ | support | sharpness of that suppression | — | near-switch behaviour, kink in the tangent | $\sigma_{\rm low}$ |
| `dilation_high_normal_reference` $\sigma_{\rm high}$ [Pa] | support | dilation at high $\sigma'_n$ | (0 disables) | dilation suppressed everywhere | $\psi_p$ |
| `dilation_high_normal_exponent` $n_{\rm high}$ | support | sharpness | — | as above | $\sigma_{\rm high}$ |
| `use_normal_memory_for_dilation_support` | which pressure | whether support follows current or peak $\sigma'_n$ | — | — | the strength-memory family |
| `use_irreversible_dilation_target` | alternative law | replaces the incremental rule with a target | — | — | $d_{\max}$, $L_d$, $m_d$ |
| `max_irreversible_dilation` $d_{\max}$ [m] | target law | asymptotic opening | dilation capped early | no cap | $L_d$ |
| `irreversible_dilation_distance` $L_d$ [m] | target law | approach rate to $d_{\max}$ | reaches $d_{\max}$ immediately | never reaches it | $d_{\max}$ |
| `irreversible_dilation_exponent` $m_d$ | target law | shape | — | delayed then abrupt | $L_d$ |

**Advice.** Every one of these adds a parameter and each is weakly identifiable from a single
specimen. Use them only when a *set* of specimens at different confining stress shows a systematic
trend the base law cannot follow — which is exactly the situation the four Ye & Ghassemi specimens
create, and the reason the family exists.

---

#### IX.6 Strength memory and retained shear support

Two mechanisms for what survives after the joint has opened or slipped a long way.

$$
\text{normal-strength memory: } \sigma_{\rm mem} \text{ decays toward } \zeta\,\sigma_{\rm mem}
\text{ over an opening } L_m ,
$$
$$
\text{retained shear support: } Y \ge H \cdot Y_{\rm hist}, \text{ decaying over a slip } L_H .
$$

| Parameter | Enters | Moves | Too small | Too large | Coupled to |
| --- | --- | --- | --- | --- | --- |
| `normal_strength_retention_factor` $\zeta$ | memory decay | strength after opening | memory lost immediately | opened joint retains strength indefinitely | $L_m$ |
| `normal_strength_memory_decay_distance` $L_m$ [m] | memory decay | how far it survives | as above | as above | $\zeta$ |
| `retained_shear_support_factor` $H$ | strength floor | residual after large slip | no floor; $Y\to 0$ as $\sigma'_n\to 0$ | strength propped artificially high | $\mu_s$ |
| `retained_shear_support_decay_distance` $L_H$ [m] | floor decay | how long the floor lasts | floor gone before it helps | permanent floor | $H$ |

**A limitation worth knowing.** $H$ decays with *slip*, so it is useless as a guard against
$\sigma'_n \to 0$ occurring long after slip has stopped — which is the SW-S3/SW-S4 failure mode.
The Barton–Bandis family has `min_tau_limit` for that; the Coulomb family does not.

---

#### IX.7 Rate-and-state (optional)

$$
Y \;\mathrel{+}=\; p_c\,a\left(\operatorname{asinh}\!\left[\frac{V}{2V_0}\left(\frac{V_0\theta}{D_c}\right)^{b/a}\right] - \operatorname{asinh}\tfrac{1}{2}\right),
\qquad
\dot\theta = 1 - \frac{V\theta}{D_c}.
$$

Written as a **perturbation about** the Coulomb strength, which plays the role of the reference
friction $f_0$ — not as an absolute friction law. At $V = V_0$, $\theta = D_c/V_0$ the term
vanishes identically.

| Parameter | Enters | Moves | Too small | Too large | Coupled to |
| --- | --- | --- | --- | --- | --- |
| `use_rate_and_state` | on/off | rate dependence | — | — | $\eta_t$ — both damp the burst; do not use both blindly |
| `rate_and_state_a` | direct effect | burst damping | no effect | persistent strength offset; onset delayed | $\mu_r$ (the offset masquerades as strength) |
| `rate_and_state_b` | evolution effect | velocity weakening/strengthening | — | $a<b$ gives velocity weakening and possible runaway | $a$: the sign of $a-b$ is the regime |
| `rate_and_state_theta0` [s] | initial state | initial strength | — | — | auto-initialises to $D_c/V_0$ if zero — prefer that |
| `rate_and_state_nonnegative` | clamp | stick/slip continuity | **non-monotone jump of $0.481\,a\,p_c$ at $V\to0$; Newton limit-cycles at onset and re-stick** | — | $a$ (the jump scales with it) |

**Set $V_0$ near the characteristic slip rate** so that $\operatorname{asinh}$ is $O(1)$ there.
$a > b$ gives velocity strengthening, which is what is wanted if the purpose is to damp a burst.

---

#### IX.8 Reported-output-only parameters

These change the reported normal displacement and nothing else — not the residual, not the
Jacobian, not the hydraulic aperture. They exist to decompose the measured $d_n$ into permanent and
recoverable parts, which the mechanics does not do for you because $g_n^p$ is monotone by
construction.

$$
d_{\rm rev} = \underbrace{G(s)}_{\text{gate}}\, C_n\left\langle \sigma_{\rm ref} - \sigma'_n\right\rangle_+ ,
\qquad
G(s) = 1 - \exp\!\left[-\left(\frac{\langle s - s_0\rangle_+}{D_{\rm rev}}\right)^{m}\right],
$$

with an optional reclosure hysteresis retaining a fraction $f_{\rm ret}$ of the peak.

| Parameter | Enters | Moves | Too small | Too large | Coupled to |
| --- | --- | --- | --- | --- | --- |
| `reversible_normal_compliance` $C_n$ [m/Pa] | $d_{\rm rev}$ | **magnitude of the unload recovery** | panel flat after the peak | recovery over-predicted; peak $d_n$ overshoots | $\psi$ — the peak is $g_n^p + d_{\rm rev}$, so raising $C_n$ requires lowering $\psi$ |
| `reversible_normal_reference_stress` $\sigma_{\rm ref}$ [Pa] | $d_{\rm rev}$ | where $d_{\rm rev}$ vanishes | recovery incomplete at the end | $d_{\rm rev}$ large at the peak; overshoot | $C_n$. Set it to $\sigma'_n$ at the **final** stage and $g_n^p$ then calibrates against the permanent dilation |
| `..._activation_slip` $s_0$ [m] | gate | pre-slip flatness | elastic opening appears before yield | recovery switches on after unloading has begun | the measured pre-slip $d_n$, which should be $\approx 0$ |
| `..._activation_distance` $D_{\rm rev}$ | gate | sharpness of activation | — | gate never fully opens | $s_0$ |
| `..._activation_exponent` $m$ | gate | shape | — | — | $D_{\rm rev}$ |
| `..._retention_fraction` $f_{\rm ret}$ | hysteresis | how much recovery is suppressed | full recovery | none; panel flat again | $C_n$ — **effective recovery is $(1-f_{\rm ret})C_n\Delta\sigma'_n$; read them together** |
| `..._retention_activation_slip` | hysteresis gate | prevents preload cycling being read as post-failure hysteresis | preload history mistaken for hysteresis | memory never activates | $f_{\rm ret}$ |

**The trap.** Quoting $C_n$ without $f_{\rm ret}$ is meaningless: a compliance that looks $2.3\times$
too soft is exactly right once a retention fraction of $0.525$ beside it is accounted for. We have
made this error and corrected it.

---

#### IX.9 The cohesive (tensile) branch

Off by default. When disabled the interface is initialised fully damaged and reproduces a
pre-existing frictional joint exactly, which is the correct configuration for every case in this
manual. Enable it only to model an intact bridge that must break.

| Parameter | Enters | Moves | Too small | Too large | Coupled to |
| --- | --- | --- | --- | --- | --- |
| `enable_tensile_cohesion` | on/off | whether an intact branch exists | — | — | all of the below |
| `cohesive_peak_traction` $T_0$ [Pa] | bilinear law | tensile strength | breaks immediately | never breaks | $\delta_0$: initial stiffness is $T_0/\delta_0$ |
| `cohesive_initial_separation` $\delta_0$ [m] | bilinear law | initial stiffness | very stiff, ill-conditioned | soft intact response | $T_0$ |
| `cohesive_final_separation` $\delta_f$ [m] | bilinear law | fracture energy $G_c = \tfrac12 T_0\delta_f$ | brittle; snap-back | very ductile | $T_0$; must exceed $\delta_0$ |
| `cohesive_shear_weight` $\beta_c$ | mixed-mode measure | mode mixity | shear does not damage | shear dominates | $\delta_0,\delta_f$ |
| `cohesive_damage_viscosity` $\eta_D$ [s] | Duvaut–Lions | rate dependence of damage | rate-independent, possible snap-back | damage lags loading | $\Delta t$ |

---

#### IX.10 Hydraulic parameters

$$
a_h = a_{h0} + \chi\left\langle g_n \right\rangle_+ + a_{\rm stress}(\sigma'_n) - a_{\rm gouge}(s),
\qquad
a_{\rm gouge}(s) = a_g\left[1 - \exp\!\left(-\frac{\langle s - s^{*}_g\rangle_+}{s_c}\right)\right].
$$

| Parameter | Enters | Moves | Too small | Too large | Coupled to |
| --- | --- | --- | --- | --- | --- |
| `initial_hydraulic_aperture` $a_{h0}$ [m] | $a_h$ | **initial flow rate**, as $Q \propto a_{h0}^3$ | initial $Q$ low by the cube | high by the cube | back-calculate from measured initial $Q$; never guess |
| `aperture_scale` $\chi$ | $a_h$ | how much mechanical opening becomes hydraulic | aperture barely grows with slip | aperture over-responds; $Q$ blows up | $\psi$ — **if $\psi$ is reduced, $\chi$ must rise by the reciprocal to hold $a_h$** |
| `dilation_scale` | legacy separate term | — | — | double-counts dilation | must be 0 under kinematic routing |
| `slip_damage_scale` $a_g$ [m] | gouge | **permeability hysteresis** | aperture recovers fully on unloading; measured hysteresis lost | conductivity collapses | $s_c$, $s^{*}_g$ |
| `slip_damage_onset_slip` $s^{*}_g$ [m] | gouge gate | loading/unloading asymmetry | gouge fills during the burst itself | gouge never accumulates | $a_g$ |
| `slip_damage_characteristic_slip` $s_c$ [m] | gouge | how fast gouge saturates | abrupt conductivity loss | gradual | $a_g$ |
| `min_hydraulic_aperture` [m] | bound | numerical floor | — | **if set equal to $a_{h0}$ the fracture can never close hydraulically** — an unphysical constraint that looks like a good fit to the first data point | $a_{h0}$ |
| `max_hydraulic_aperture` [m] | bound | numerical cap | clips real growth | a transient mechanical excursion blows up $a_h^3$ and wrecks the coupled solve | $\chi$ |
| `retention_residual` | roughness retention | how much dilation-propping survives wear | — | — | $R$ |
| `pressure_penalty_length` $L_p$ [m] | wall pressure continuity | — | ill-conditioning | wall pressures decouple | numerical only — demonstrate insensitivity |

**Calibrate $a_{h0}$ first and alone.** It is the only hydraulic parameter identifiable from a
single pre-slip measurement, and everything downstream depends on it. Then $\chi$ from the peak
aperture, then $a_g$ from the unloading branch.

---

#### IX.11 Regularisation and numerical tolerances

Covered in full in §[`sec:viscosity`](#sec-viscosity) and the manuscript's numerical
implementation chapter. Summarised here for completeness.

| Parameter | Enters | Effect | Guidance |
| --- | --- | --- | --- |
| `contact_gap_regularization` $\epsilon_g$ [m] | $\langle x\rangle_+^\epsilon = \tfrac12(x+\sqrt{x^2+\epsilon^2})$ | smooths the contact/open branch; **biases by $\epsilon/2$ even at exact contact** | size against a physical length; $10^{-14}$ m against a $10^{-6}$ m aperture is $10^{-8}$ relative |
| `cohesive_gap_regularization` $\epsilon_c$ [m] | cohesive separation | as above | as above |
| `stress_regularization` $\sigma_{\rm reg}$ [Pa] | smooth max in memory/support/dissipation denominators | avoids division by zero | $10^{-8}$ Pa against $10^{7}$ Pa strengths |
| `tangential_viscosity` $\eta_t$ [Pa·s/m] | $Y \to Y + \eta_t V$ | removes the stick/slip kink; **allows advance through the softening limit point** | require $\eta_t V \ll Y$ at the rates of interest and **report the ratio** |
| `opening_gap_tolerance` [m] | active-set decision | contact/open threshold | keep at 0 unless diagnosing |
| `tangential_traction_tolerance` [Pa] | slip direction | avoids an undefined $\mathbf{m}$ at $\lVert\mathbf{t}_t\rVert = 0$ | $10^{-12}$ Pa |
| `local_newton_stress_tolerance` [Pa] | local convergence | absolute yield-residual tolerance | must match the pre-check tolerance, or near-yield states are misreported as slipping |
| `local_newton_gap_tolerance` [m] | local convergence | normal-plastic-jump residual | $10^{-14}$ m |
| `return_mapping_stiffness_tolerance` [Pa/m] | local Jacobian | minimum admissible determinant | guards the $2\times2$ solve at a limit point |
| `max_local_newton_iterations` | local solve | iteration budget | 30 is ample; hitting it signals a bad state, not a small budget |
| `max_local_substeps` | substepping | bisection depth | 32; raising it is the correct response to a local failure |
| `event_fraction_tolerance` | substepping | merges nearby events on the jump path | $10^{-10}$ |

**The one that changes physics is $\eta_t$.** The others change conditioning. Note also that
refining $\Delta t$ does *not* remove the viscous inflation, because $V = \Delta\gamma/\Delta t$ and
both shrink together — only reducing $\eta_t$ does, and that reinstates the instability it was
added to survive.

---

#### IX.12 Deprecated and refused

| Parameter | Status | Why |
| --- | --- | --- |
| `max_plastic_slip_increment` | **refused at parsing** | A cap that binds is a constitutive law whose parameters are the time step and the cap value. Measured: in one calibration it bound on 14 time steps and supplied ~30 % of total slip. |
| `max_dilation_increment` | **refused at parsing** | as above |
| `normal_traction_tolerance` | deprecated, must be 0 | opening is decided by `opening_gap_tolerance` in metres, not by a traction |
| `cohesive_failure_tolerance` | deprecated | the mixture law has no hard cohesive-to-frictional switch |
| `dilation_scale` (in the permeability material) | must be 0 | double-counts the dilation already in $\langle g_n\rangle_+$ under kinematic routing |

The legitimate substitutes for the increment caps act on the *integration*, not on the answer:
reduce $\Delta t$, subdivide within the step, or add viscosity and report it. All three converge
under refinement; a cap does not.

---

#### IX.13 Which observable identifies which parameter

The practical summary. A parameter absent from this table is not identifiable from a
Ye & Ghassemi-type protocol and should be fixed from literature or from an independent test.

| Observable | Identifies | Does **not** identify |
| --- | --- | --- |
| Pre-slip $\sigma'_n$ history | $c_0$, $K_{ni}$, $V_m$, $p$ | anything about strength or dilation |
| Pre-slip $\tau$ at stage 1 | the axial preload (via the gate) | any constitutive parameter — the joint is stuck |
| Onset time | $\mu_r$, $c_r$, $R_0$ (or $\phi_r$, JRC) | $L_R$, $\mu_s$, $\psi$ |
| Magnitude of the stress drop | $\mu_s$, $c_s$, $R_r$, together with $k_{\rm sys}$ | $L_R$ |
| Shape of the stress drop | $L_R$, $m_\mu$ — **only if the drop spans several stages** | anything, if the drop occupies one stage |
| Peak $d_n$ | $\psi_p$ **if below the bound**; otherwise $\mu$ | $\psi_p$ if the limiter is active |
| $d_n$ recovery on unloading | $C_n$ **with** $f_{\rm ret}$; or the BB unload retention | $\psi$ |
| Initial $Q$ | $a_{h0}$ | everything else hydraulic |
| Peak $a_h$ | $\chi$ | $a_{h0}$ |
| $a_h$ hysteresis between branches | $a_g$, $s_c$, $s^{*}_g$ | $\chi$ |
| Failure to reach `end_time` | that a stability or tolerance bound has been crossed | which one — check $\lvert\mathrm{d}Y/\mathrm{d}s\rvert$ vs $k_{\rm sys}$ first |

### Back-analysing a result

#### A diagnostic order of operations

When a simulated history does not match an experiment, work outward from the
boundary conditions, not inward from the constitutive law:

1. **Is the imposed loading right?** Compare $\sigma_1$, $\sigma_3$ and
    the injection history against the reported protocol. These are prescribed;
    if they disagree, nothing downstream is meaningful.
1. **Is the initial state in equilibrium?** Check that the reported
    $\sigma'_n$ and $\tau$ at $t=0^+$ match the resolved
    values [`eq:effstress`](#eq-effstress). A drift over the first steps means
    $\boldsymbol{\sigma}_0$ and the boundary tractions disagree.
1. **Is the onset time right?** Slip begins when the stress path meets
    the envelope (Fig. [`fig:yieldsurface`](#fig-yieldsurface)). Onset is controlled by
    *peak* strength ($\mu_r$, cohesion, JRC), not by the weakening law.
1. **Is the final slip magnitude right?** For a compliant system, the
    arrested slip satisfies the load-line balance

    $$
    s_{\text{final}} \approx \frac{Y_{\text{peak}} - Y_{\text{residual}}}{k_{\text{sys}}},
    $$

    with $k_{\text{sys}}$ the system unloading stiffness in
    $(\tau,s)$ space. This means final slip is set by the *strength drop*,
    i.e. by $\mu_s$, not by $L_R$.
1. **Is the weakening *shape* right?** Now, and only now, adjust
    $L_R$ --- it controls how the transition is distributed in time, with
    little effect on the endpoints.
1. **Is the dilation right?** Check the realised $\,\mathrm{d} g_n^p/\,\mathrm{d}\gamma$
    against both $\tan\psi$ and $(1-\epsilon_D)\mu$. If it equals the latter,
    the limiter is active and $\psi$ is inert.
1. **Is the permeability right?** Only after the mechanics is right,
    because $a_h$ depends on $g_n$. Fit $a_{h0}$ to the initial flow, then the
    gouge parameters to the unloading branch.

#### Sensitivity relations worth memorising

$$
\begin{aligned}
\frac{\delta Q}{Q} &\approx 3\,\frac{\delta a_h}{a_h}
  &&\text{(cubic law --- permeability is very sensitive to aperture)}\\
\frac{\delta k}{k} &\approx 2\,\frac{\delta a_h}{a_h}
  &&\text{(permeability }a_h^2\text{)}\\
\delta s_{\text{final}} &\approx \frac{\delta Y_{\text{res}}}{k_{\text{sys}}}
  &&\text{(final slip follows the residual strength)}\\
\delta t_{\text{onset}} &\approx \frac{\delta Y_{\text{peak}}}{\,\mathrm{d}\tau_{\text{driving}}/\,\mathrm{d} t}
  &&\text{(onset follows the peak strength and the loading rate)}
\end{aligned}
$$

#### Warning signs in a calibration

- A parameter that must be changed *per sample* for samples of the same
    material (e.g. a different Biot coefficient for each specimen) is fitting,
    not physics.
- A boundary-condition parameter used as a fitting knob (a “poroelastic
    piston compensation”, a “late confinement unload”) removes the
    experiment's independence entirely.
- An effective-stress coefficient on an open fracture different from $1$.
- A comparison quantity that is computed analytically from a calibrated
    quantity rather than solved for. If the reported “flow rate” is
    $(W/L)a_h^3\Delta p/12\mu_f$ with $a_h$ calibrated and $W/L$ fitted, then
    the agreement is close to algebraically guaranteed and carries no
    information.
- More free parameters than independent features in the data. Count them.

## Appendices

### Notation

| Symbol | Units | Meaning |
| --- | --- | --- |
| $\boldsymbol{u}$ | m | displacement |
| $p$ | Pa | pore pressure |
| $\boldsymbol{\sigma}$ | Pa | total stress (tension positive) |
| $\alpha$ | -- | Biot coefficient |
| $M$ | Pa | Biot modulus, Eq. [`eq:biotmodulus`](#eq-biotmodulus) |
| $\phi$ | -- | porosity |
| $\mathbf k$ | m$^2$ | matrix permeability |
| $[\![\boldsymbol{u}]\!]$ | m | displacement jump across the fracture |
| $\boldsymbol{R}$ | -- | local$\to$global rotation, $\boldsymbol{R}\boldsymbol{e}_1=\boldsymbol{n}$ |
| $\boldsymbol{g}$ | m | local jump, $(g_n, g_{t1}, g_{t2})$ |
| $g_n^p$, $\boldsymbol{g}_t^p$ | m | plastic (irreversible) normal / tangential jump |
| $\Delta\gamma$ | m | plastic multiplier = equivalent plastic slip increment |
| $s$ | m | cumulative equivalent plastic slip |
| $K_n$, $K_t$ | Pa/m | normal / tangential penalty stiffness |
| $c$ | m | normal closure |
| $V_m$, $K_{ni}$, $p$ | m, Pa/m, -- | Barton--Bandis closure parameters |
| $c_0$ | m | pre-seating closure offset |
| $\sigma'_n \equiv p_c$ | Pa | effective contact normal stress (compression $+$) |
| $\tau$ | Pa | shear traction magnitude |
| $Y$ | Pa | shear strength (yield stress) |
| $\mu$, $\phi_r$ | --, deg | friction coefficient / basic friction angle |
| $\psi$ | deg | dilation angle |
| $R$, $R_r$, $L_R$ | --, --, m | roughness state, residual, decay distance |
| $D$, $\kappa$ | --, m | cohesive damage, separation history |
| $\theta$, $a$, $b$, $D_c$, $V_0$ | s, --, --, m, m/s | rate-and-state variables |
| $a_m$, $a_h$, $a_{h0}$ | m | mechanical / hydraulic / reference aperture |
| $T$, $k_f$ | m$^3$/(Pa s), m$^2$ | transmissivity, fracture permeability |
| $\mu_f$, $\rho_f$, $K_f$ | Pa s, kg/m$^3$, Pa | fluid viscosity, density, bulk modulus |
| $\eta_t$ | Pa s/m | tangential viscosity (regularisation) |
| $\epsilon_D$ | -- | dissipation margin |

### Material property names

Properties flow between objects by name. The important ones:

| Property | Produced by | Consumed by |
| --- | --- | --- |
| `displacement_jump_global` | jump material | scalar extraction |
| `interface_displacement_jump` | jump material | all constitutive laws |
| `czm_total_rotation` | jump material | global traction, fluid-pressure kernel |
| `interface_traction` | constitutive law | global traction, `czm_sigma_n` |
| `traction_global` | global traction material | `OrcaMechInterfaceKernel` |
| `interface_pore_pressure` | interface pressure material | fluid-pressure kernel |
| `mechanical_aperture` | aperture material | permeability material |
| `hydraulic_aperture` | permeability material | flow kernel (current *and* old) |
| `fracture_transmissivity` | permeability material | flow kernel |
| `cumulative_plastic_slip` | constitutive law | permeability (gouge) |
| `one_over_biot_modulus_qp` | TH material | storage kernel |
| `biot_coefficient_qp` | Biot material | poromech + volumetric expansion kernels |
| `vol_strain_rate` | mech material | volumetric expansion kernel |

### Minimum input deck skeleton

```ini
[Mesh]
  # ... generate or read, then split the fracture:
  [split]
    type = OrcaFaultInterface3DGenerator   # 3D, from a nodeset
    nodesets = 'fracture_interface'
  []
[]

[Variables]  [disp_x][] [disp_y][] [disp_z][] [pore_pressure][]  []

[Kernels]                       # bulk residuals
  [mech_x] type = OrcaPoroMechKernel  variable = disp_x  component = 0
           pore_pressure = pore_pressure []
  # ... y, z
  [storage]   type = OrcaSinglePhaseMassTimeDerivativeKernel       variable = pore_pressure []
  [vol_exp]   type = OrcaSinglePhaseMassVolumetricExpansionKernel  variable = pore_pressure []
  [darcy]     type = OrcaFullySaturatedSinglePhaseDarcySUPGKernel  variable = pore_pressure []
[]

[InterfaceKernels]              # fracture residuals
  [czm_x]   type = OrcaMechInterfaceKernel  variable = disp_x  neighbor_var = disp_x
            component = 0  boundary = fracture_interface []
  # ... y, z
  [pf_x]    type = OrcaCZMFluidPressureInterfaceKernel  variable = disp_x
            neighbor_var = disp_x component = 0 boundary = fracture_interface
            pressure_traction_coefficient = -1.0 []
  # ... y, z
  [flow]    type = OrcaFractureFlowInterfaceKernel  variable = pore_pressure
            neighbor_var = pore_pressure  boundary = fracture_interface []
[]

[Materials]
  [mech]     type = OrcaMechMaterial   strain_model = incremental  ... []
  [rockHM]   type = OrcaTHMaterial     ... []
  [biot]     type = OrcaBiotCoefficientMaterial  biot_coefficient = 0.6 []
  [gravity]  type = OrcaGravityVectorMaterial    gravity = '0 0 0' []

  [czm_jump] type = OrcaCZMComputeDisplacementJump  boundary = fracture_interface []
  [czm_p]    type = OrcaCZMInterfacePressure  pore_pressure = pore_pressure
             boundary = fracture_interface []
  [czm]      type = ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile
             boundary = fracture_interface  ... []
  [czm_glob] type = OrcaComputeGlobalTractionSmallStrain  boundary = fracture_interface []

  [sigma_n]  type = OrcaCZMRealVectorCartesianComponent  index = 0
             real_vector_value = interface_traction  property_name = czm_sigma_n
             boundary = fracture_interface []
  [ap]       type = ADOrcaCZMComputeMechanicalAperture  boundary = fracture_interface []
  [perm]     type = ADOrcaRoughnessDamageFracturePermeability
             use_kinematic_aperture = true  aperture_scale = 1.0  dilation_scale = 0.0
             boundary = fracture_interface  ... []
[]
```

### Checklist for reproducing this framework from scratch

1. Implement the bulk: linear elasticity with incremental strain, Biot
    effective stress, and the three mass-balance kernels. **Verify
    against Terzaghi and Mandel before anything else.** Mandel in particular,
    because the Mandel--Cryer overshoot is impossible to get right by accident.
1. Implement the mesh splitter. Verify by checking that the two walls can
    separate and that nodeset memberships were copied to duplicated nodes.
1. Implement the jump material and the rotation. Verify with a rigid-body
    translation (jump must be zero) and a uniform stress patch test (traction
    must be transmitted exactly at any interface orientation).
1. Implement `OrcaMechInterfaceKernel` with a trivial elastic
    traction-separation law. Verify with Sneddon.
1. Implement the penalty contact and the Barton--Bandis closure. Verify
    against the closed form on a single element, load and unload.
1. Implement the Coulomb return map with a constant $\mu$. Verify with the
    inclined-fracture-under-compression benchmark.
1. Add hardening/softening, then dilatancy with the dissipation limiter.
    Verify that the limiter is never violated and that the realised
    $\,\mathrm{d} g_n^p/\,\mathrm{d}\gamma$ matches expectation.
1. Add the aperture and cubic-law flow. Verify $a_h(0)=a_{h0}$,
    $k=a_h^2/12$, $T=a_h^3/12\mu_f$, and a linear steady profile.
1. Only now attempt a coupled injection simulation.
1. Guard every $\mathrm{pow}$ and $\sqrt{\cdot}$ that can see an exactly-zero
    argument (Section [`sec:powguard`](#sec-powguard)), and make every convergence tolerance
    scale-aware.

---

## Supplement: the reference experiment (Ye & Ghassemi, 2018)

<a id="sup-top"></a>

> **Source.** Ye, Z., & Ghassemi, A. (2018). *Injection-induced shear slip and
> permeability enhancement in granite fractures.* **Journal of Geophysical
> Research: Solid Earth**, **123**, 9009–9032.
> [doi:10.1029/2018JB016045](https://doi.org/10.1029/2018JB016045)
>
> This supplement is a self-contained extraction of everything in that paper that
> bears on the ORCA validation: the geometry, the control protocol, the exact
> reduction equations, the complete data tables, and a set of quantities *derived*
> here that the paper does not tabulate but that the model needs. It closes with a
> point-by-point correspondence between the experiment and the code, and an honest
> account of what the data can and cannot constrain.
>
> Everything marked **[derived]** was computed here from the paper's own numbers
> and is not stated in the paper. Every derivation is shown so it can be checked.

### Why this supplement exists

The main manual describes what the code *does*. It does not describe what the
code is being asked to *reproduce*. Without that, three failure modes are easy:

1. **Comparing incommensurable quantities.** The paper's $\sigma'_n$, $d_n$,
    $d_s$ and $a_h$ are not the model's $\sigma'_n$, $g_n$, $\gamma$ and $a_h$.
    They are *different operators applied to different objects*. Four of the
    seven validation observables need a translation step, and the translation is
    not the identity (Chapter [`sup:operators`](#sup-operators)).
1. **Treating fitted parameters as measured ones.** The paper reports 5 bulk
    properties and 4 fracture roughness values. The model needs on the order of
    30 numbers. Which are pinned by the experiment and which are free is the
    single most important thing to be honest about in a validation paper
    (Chapter [`sup:constrained`](#sup-constrained)).
1. **Missing checks the data already supports.** The paper's Table 2 is
    internally over-determined: $\sigma'_n$ and $\tau$ at eleven hold stages are
    two functions of one unknown ($\sigma_1$), so the geometry can be recovered
    and verified. Doing that here found one inconsistency in the paper's own
    Table 1 (Section [`sup:thetacheck`](#sup-thetacheck)) and produced the flow
    geometry factor that the decks need
    (Section [`sup:flowgeom`](#sup-flowgeom)).

---

### The experiment

<a id="sup-experiment"></a>

#### What was done, in one paragraph

Four ~50 mm diameter cylindrical Sierra White granite cores, each containing a
single fracture inclined at $\theta \approx 30^\circ$ to the core axis, were
loaded in a triaxial cell at constant confining pressure. Water was injected
into one end of the fracture through a small borehole and produced from the
other. The injection pressure was raised **stepwise**, holding at each step long
enough to measure a steady-state flow rate, until the fracture slipped; it was
then lowered stepwise through the same steps to test whether the permeability
gain survived. The distinguishing feature versus earlier work is the control
mode: **constant piston displacement**, not constant axial stress, so the
differential stress *relaxes* as the fracture slips and the slip arrests on its
own.

#### The four samples

| | SW-T1 | SW-T2 | SW-S3 | SW-S4 |
|---|---|---|---|---|
| Fracture type | tensile (split) | tensile (split) | saw cut | saw cut + **polished** |
| Length $L_s$ (mm) | 128.80 | 132.70 | 123.40 | 118.70 |
| Diameter $D$ (mm) | 50.52 | 50.52 | 50.53 | 50.51 |
| Fracture angle $\theta$ (Table 1) | 32° | **31°** | 29° | 30° |
| $\theta$ implied by Table 2 **[derived]** | 32.0° | **30.0°** | 29.0° | 30.0° |
| Mean JRC, before test | 15.32 | 14.63 | 1.96 | 1.19 |
| Mean JRC, after test | 10.21 | 11.27 | (not reported) | (not reported) |
| Max surface relief (mm) | 6.43 | 5.86 | 0.62 | 0.25 |
| Joint matching coefficient | ≈1.0 | ≈1.0 | 1.0 | 1.0 |
| Descriptor used in the paper | *very rough* | *very rough* | *rough* | *smooth* |
| Fracture area $A$ **[derived]**, ×10⁻³ m² | 3.783 | 4.009 | 4.136 | 4.008 |

$\theta$ is measured **from the long axis of the core** to the fracture plane, so
$\theta = 0$ would be a fracture parallel to $\sigma_1$ and $\theta = 90^\circ$ a
fracture normal to it. This is the opposite of the convention used in most
fault-mechanics papers; getting it backwards inverts $\sigma_n$ and $\tau$.

The fracture ellipse area follows from cutting a cylinder of diameter $D$ at
$\theta$ to its axis:

$$
A = \frac{\pi D^{2}}{4\sin\theta}.
$$

For SW-S4 this gives $4.008\times10^{-3}\,\mathrm{m^2}$, which is exactly the
value the `AreaPostprocessor` on `fracture_interface` must report. If it reports
twice that, the sideset has been doubled — see the note in the deck header, and
Section [`sup:traps`](#sup-traps).

#### Bulk material properties (all four samples, same granite)

| Property | Value | Where it enters ORCA |
|---|---|---|
| Young's modulus $E$ | 67 GPa | `youngs_modulus` |
| Poisson's ratio $\nu$ | 0.32 | `poissons_ratio` |
| Uniaxial compressive strength | 150 MPa | best available proxy for **JCS** |
| Internal friction angle (intact) | 46° | **not** the joint $\phi_r$ — see below |
| Tensile strength | 11 MPa | tensile cohesion cap, if enabled |
| Matrix permeability | $5\times10^{-19}$ to $1\times10^{-18}$ m² | `matrix_permeability` |
| Mean crystal size | ≈0.5 mm | sets the asperity wavelength floor |
| Mineralogy | 43.5% quartz, 46.1% albite, 4.8% sanidine, 2.7% biotite, 2.0% illite, 0.9% clinochlore | — |
| Fluid | deionized water, $\mu_f = 1.002\times10^{-3}$ Pa·s at 20 °C | `fluid_viscosity_ref` |

Two cautions on this table.

- **The 46° is the intact rock's internal friction angle**, measured in triaxial
    compression on unfractured cores. It is *not* the basic/residual friction
    angle $\phi_r$ of a saw-cut joint surface, which is the quantity the
    Barton–Bandis law needs. The paper does not report $\phi_r$. It is a free
    parameter (Chapter [`sup:constrained`](#sup-constrained)).
- **JCS is not reported either.** The 150 MPa UCS is the conventional stand-in
    for an unweathered joint, but it is a substitution, not a measurement.

#### Roughness characterization

Surfaces were scanned with a 2 μm-resolution 3-D laser scanner. Along each 2-D
profile, at a **0.5 mm sampling span**, the RMS slope is

<a id="sup-eq-z2"></a>

$$
Z_2 = \left[\frac{1}{(n-1)(\Delta x)^{2}}\sum_{i=1}^{n-1}\left(z_{i+1}-z_i\right)^{2}\right]^{1/2}
\tag{Ye Eq. 1}
$$

and JRC follows the Yu & Vayssade (1991) correlation

<a id="sup-eq-jrc"></a>

$$
\boxed{\;\mathrm{JRC} = 61.79\,Z_2 - 3.47\;}
\tag{Ye Eq. 2}
$$

The sample JRC is the average over all 2-D profiles of *both* surfaces. The
distributions are approximately normal (their Figure 3), which matters: **the
JRC entering a Barton–Bandis law is a mean of a distribution with real spread**,
not a material constant. For SW-T1 the histogram runs from about 10 to 20.

The correlation is sampling-span dependent. Using a 1 mm or 1.27 mm span with
the coefficients above would give a different JRC for the same surface. If the
ORCA roughness parameters are ever re-derived from a scan, the span must match.

#### Apparatus and protocol

| Item | Value |
|---|---|
| Frame | MTS 816, 1000 kN axial, 138 MPa cell limit |
| Axial displacement | mean of **two** LVDTs mounted on the sample, ±0.05% error |
| Radial displacement | one LVDT on a radial ring, ±0.05% error |
| Load cell | inside the vessel, ≤1 kN error |
| Pumps | 2 × Teledyne ISCO 100DM; ±0.5% pressure, ±0.3% flow rate; 103 mL capacity |
| Boreholes | 3.5 mm diameter, vertical, **6 mm from the sidewall**, one from each end |
| End caps | 50.8 mm × 3.2 mm porous metal discs, 60 μm pore size |

Sequence:

1. Apply $\sigma_3 = 30$ MPa. **The same 30 MPa was used for all four
    samples** — this is stated once in the text and is easy to miss; it is
    confirmed independently in Section [`sup:thetacheck`](#sup-thetacheck).
1. Set production pressure $P_o = 5$ MPa (held constant for the entire test) and
    injection $P_i = 5$ MPa, to saturate the fracture.
1. **Five loading–unloading cycles of differential stress to 10–20 MPa**, to
    remove the plastic seating deformation between fracture, porous discs and
    platens.
1. Load axially to a *near-critical* differential stress, identified from the
    deflection of the stress–strain curve.
1. Switch to **constant piston displacement** control.
1. Raise $P_i$ stepwise at 0.03 MPa/s: 8, 12, 16, 20, 24, 28 MPa. Each step
    lasts 300–500 s — a 150–250 s buildup plus a 150–250 s constant-pressure
    hold. Flow rate is recorded only after ≥100 s of hold, and only once the
    inlet and outlet flow rates agree to within 5%.
1. Lower $P_i$ stepwise through 24, 20, 16, 12, 8 MPa with the same increment.

$P_i$ was kept at least 2 MPa below $\sigma_3$ throughout, so the treatment
pressure never exceeded the minimum principal stress — this is the whole premise
of hydroshearing as opposed to hydraulic fracturing.

**Step 3 is the experimental justification for the pre-seating offset $c_0$ in
the code's Barton–Bandis closure** (Chapter [`ch:closure`](#ch-closure)). The
joint the model sees at $t=0$ is not a virgin joint; it has already been cycled
five times and its seating plasticity has been consumed. A closure law fitted
from $c=0$ without an offset is fitting the wrong branch.

#### Why constant piston displacement matters

Under **constant axial stress** control, $\sigma_d = \sigma_1 - \sigma_3$ is
fixed, so by Eq. (Ye 4) below the shear traction $\tau$ is *also* fixed. Raising
$P_i$ lowers $\sigma'_n$, hence lowers the strength $\mu\sigma'_n$, and nothing
lowers the driving traction. Once the strength envelope is touched, slip cannot
arrest: the authors report that a previous test in this mode produced >2 mm of
audible slip and burst the jacket.

Under **constant piston displacement**, the loading column is a spring in series
with the specimen. Slip shortens the specimen along the axis, the spring
unloads, $\sigma_d$ falls, and both $\tau$ and $\sigma'_n$ fall together. The
stress path moves *down along* the envelope and the slip arrests at a lower
stress state. This is the mechanism that produces the observed stress relaxation
and the finite, self-limiting slip — and it is the reason the ORCA decks use a
`FunctionPenaltyDirichletBC` (a spring) rather than a `DirichletBC` (a rigid
frame) on the top surface. **A rigid Dirichlet cannot reproduce this
experiment**; it caps slip and dilation below the measured values.

The paper does **not** report the machine stiffness. The penalty in the decks is
therefore a fitted quantity — arguably the single most consequential fitted
quantity in the whole calibration, because it sets the slope of the unloading
line and hence the arrest point.

---

### The measurement chain

<a id="sup-operators"></a>

Everything in Table 2 except $Q$ is *computed*, not measured. This chapter gives
the exact reduction, because reproducing the reduction — rather than comparing
against raw model fields — is what makes a comparison meaningful.

#### Stress on the fracture plane

<a id="sup-eq-sn"></a>

$$
\boxed{\;\sigma'_n = \left(\sigma_3 - P_p\right) + \left(\sigma_1-\sigma_3\right)\sin^{2}\theta\;}
\tag{Ye Eq. 3}
$$

<a id="sup-eq-tau"></a>

$$
\boxed{\;\tau = \left(\sigma_1-\sigma_3\right)\sin\theta\cos\theta = \tfrac{1}{2}\sigma_d\sin 2\theta\;}
\tag{Ye Eq. 4}
$$

<a id="sup-eq-pp"></a>

$$
P_p = \tfrac{1}{2}\left(P_i + P_o\right)
\tag{Ye Eq. 5}
$$

Three things follow immediately, and all three matter for the model comparison.

- **The effective-stress coefficient on the fracture is 1.** Eq. (3) subtracts
    the *full* pore pressure. There is no Biot $\alpha$ in it. So the model's
    fracture effective normal stress must also use a coefficient of 1, even
    though the bulk uses $\alpha = 0.6$. The decks do this.
- **$\tau$ does not depend on $P_p$ at all.** In the stick stage the shear
    traction falls only slightly (because $\sigma_d$ creeps down slightly), while
    $\sigma'_n$ falls by 8–9 MPa. Any model that shows $\tau$ responding
    strongly to injection before slip has a bug, not a calibration problem.
- **$P_p$ is a scalar proxy, not a field.** It is the arithmetic mean of the
    inlet and outlet pressures. On the real fracture the pressure varies from
    $P_i$ at the injection borehole to $P_o$ at the production borehole, and the
    profile is not linear once the aperture varies in space. The model has the
    full field. **To compare with Table 2, the model must report
    $\sigma_n - \tfrac12 (P_i + P_o)$, not $\sigma_n - \bar p_{\text{fracture}}$.**
    These differ by however much the true mean pressure departs from the
    endpoint average, which for a strongly aperture-graded fracture is not
    small.

#### Displacement on the fracture plane

<a id="sup-eq-dn"></a>

$$
\boxed{\;d_n = \Delta z\,\sin\theta - \Delta x\,\cos\theta\;}
\tag{Ye Eq. 6}
$$

<a id="sup-eq-ds"></a>

$$
\boxed{\;d_s = \Delta z\,\cos\theta + \Delta x\,\sin\theta\;}
\tag{Ye Eq. 7}
$$

with $\Delta z$ the axial and $\Delta x$ the radial specimen deformation.
**Rock-mechanics sign convention: compression positive.** Therefore in Table 2
**opening/dilation appears as a negative $d_n$** and slip as a positive $d_s$.
The ORCA convention is the opposite for the normal component: component 0 of the
local gap is positive in *opening*. A sign flip is required, and it is the single
most common way to get a plausible-looking but wrong dilation comparison.

$\Delta z$ and $\Delta x$ are whole-specimen LVDT readings. The paper states
that the matrix contribution was **neglected**, on the argument that subtracting
an intact-modulus estimate would over-subtract (stress concentrates on the
fracture, so the matrix in a fractured sample deforms less than an intact one
would). The consequence for validation is unambiguous:

> **The paper's $d_n$ and $d_s$ are upper bounds on the true fracture
> deformation.** They contain an unremoved elastic matrix component. A model
> that reports the *fracture* jump and matches Table 2 exactly is, strictly,
> over-predicting the fracture jump by the matrix share.

For an order of magnitude on SW-S4: the differential stress drops ~22 MPa during
slip; over a ~119 mm specimen at $E = 67$ GPa that is $\sim$39 μm of axial
elastic recovery, against a measured $d_s$ of 75 μm. **This is not a small
correction.** Either the model should report an LVDT-proxy (the relative
displacement of the two end faces, matrix included) or the comparison should
carry this as a stated systematic. The decks contain an LVDT-proxy
postprocessor; use it, and say which one the paper number is being compared to.

#### Aperture, flow and permeability

<a id="sup-eq-k"></a>

$$
k = \frac{a_h^{2}}{12}
\tag{Ye Eq. 8}
$$

<a id="sup-eq-q"></a>

$$
Q = -\frac{W a_h^{3}}{12\mu_f}\,\frac{\Delta P}{L}
\tag{Ye Eq. 9}
$$

<a id="sup-eq-ah"></a>

$$
\boxed{\;a_h = \left(-\frac{12\,\mu_f\,L\,Q}{W\,\Delta P}\right)^{1/3}\;}
\tag{Ye Eq. 10}
$$

The elliptical fracture is replaced by an **equivalent rectangle of the same
area**: $L$ is the borehole separation on the fracture surface and $W = A/L$.

Note carefully what this makes $k$: **the reported permeability is not an
independent measurement.** It is $a_h^2/12$, and $a_h$ is itself back-computed
from $Q$ by Eq. (10). So $k \propto Q^{2/3}$ and carries no information beyond
the flow rate. Scoring a model against *both* $a_h$ and $k$ double-counts one
measurement. The independent observables are $Q$, $\sigma'_n$, $\tau$, $d_n$,
$d_s$ — five, not seven.

#### The flow geometry factor $W/L$ — [derived]

<a id="sup-flowgeom"></a>

The paper never states $L$ or $W$. But Eq. (10) can be inverted using $W = A/L$
and the tabulated $(Q, \Delta P, a_h)$ triples:

$$
L^{2} = \frac{a_h^{3}\,A\,\Delta P}{12\,\mu_f\,Q},
\qquad
\frac{W}{L} = \frac{A}{L^{2}} .
$$

Applied to the pre-slip hold stages of each sample (where $a_h$ is steady and
the rounding in Table 2 hurts least):

| Sample | $A$ (×10⁻³ m²) | $L$ (mm) | $W$ (mm) | $W/L$ |
|---|---|---|---|---|
| SW-T1 | 3.783 | 68.0–68.5 | 55.5 | **0.814** |
| SW-T2 | 4.009 | 70.0–70.2 | 57.2 | **0.816** |
| SW-S3 | 4.136 | 70.9–71.5 | 58.0 | **0.813** |
| SW-S4 | 4.008 | 69.7–70.2 | 57.3 | **0.817** |

The four agree to within ±1%, which is a strong indication the inversion is right
rather than an accident of rounding. $W/L$ is also insensitive to $\theta$
(both $A$ and $L$ scale as $1/\sin\theta$), so the SW-T2 angle ambiguity below
does not disturb it.

**Consequence.** Eq. (10) collapses to a one-line reduction that the model can
apply to its own computed flow rate:

$$
\boxed{\;a_h^{\text{model}} = \left(\frac{12\,\mu_f\,Q^{\text{model}}}{0.81\,\Delta P}\right)^{1/3}\;}
$$

Check on SW-S4, first hold stage: $Q = 0.005$ mL/min $= 8.333\times10^{-11}$
m³/s, $\Delta P = 3$ MPa gives $a_h = 0.744$ μm against the tabulated 0.74 μm.
This is also exactly where the SW-S4 deck's $a_{h0} = 0.7451$ μm comes from.

**Caveat, stated plainly.** A purely *geometric* estimate of $L$ disagrees. The
boreholes sit 6 mm inside the sidewall, i.e. at radius $D/2 - 6 = 19.26$ mm on
opposite sides, so their separation measured **in the fracture plane** should be
$2(D/2-6)/\sin\theta = 77.0$ mm for SW-S4, not 70 mm. Using 77 mm would raise
every reported $a_h$ by about 7% and every $k$ by 14%. The paper does not say
whether $L$ was measured in-plane or as a projection. **Use 0.81 for
consistency with Table 2** — that is the number the published data was reduced
with — but treat $a_h$ as carrying a $\sim$7% systematic and do not present
aperture agreement tighter than that as meaningful.

---

### The data

<a id="sup-data"></a>

The tables below are Table 2 of the paper, transcribed in full, plus derived
columns. Injection pressure steps are 8→28 MPa on loading and 24→8 MPa on
unloading; $P_o = 5$ MPa throughout, so $P_p = \tfrac12(P_i+5)$ and
$\Delta P = P_i - 5$.

#### SW-T1 (tensile, JRC 15.32, $\theta = 32^\circ$)

| $P_i$ (MPa) | 8 | 12 | 16 | 20 | 24 | **28** | 24 | 20 | 16 | 12 | 8 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| $Q$ (mL/min) | 0.053 | 0.114 | 0.190 | 0.280 | 0.389 | **6.220** | 4.270 | 2.870 | 1.900 | 1.120 | 0.462 |
| $d_n$ (mm) | 0.000 | 0.000 | 0.000 | −0.001 | −0.003 | **−0.157** | −0.139 | −0.130 | −0.123 | −0.118 | −0.113 |
| $d_s$ (mm) | 0.000 | 0.000 | 0.001 | 0.002 | 0.008 | **0.532** | 0.539 | 0.534 | 0.529 | 0.525 | 0.521 |
| $\sigma'_n$ (MPa) | 65.47 | 63.35 | 61.27 | 59.14 | 56.94 | **31.79** | 33.45 | 35.35 | 37.29 | 39.22 | 41.14 |
| $\tau$ (MPa) | 67.16 | 66.96 | 66.82 | 66.63 | 66.32 | **29.35** | 28.72 | 28.57 | 28.48 | 28.36 | 28.23 |
| $a_h$ (μm) | 1.63 | 1.59 | 1.62 | 1.66 | 1.72 | **4.05** | 3.81 | 3.61 | 3.49 | 3.40 | 3.36 |
| $k$ (10⁻¹² m²) | 0.22 | 0.21 | 0.22 | 0.23 | 0.25 | **1.37** | 1.21 | 1.09 | 1.02 | 0.97 | 0.94 |
| $\sigma_d$ **[der.]** | 149.4 | 149.0 | 148.7 | 148.3 | 147.6 | **65.3** | 63.9 | 63.6 | 63.4 | 63.1 | 62.8 |
| $\sigma_1$ **[der.]** | 179.4 | 179.0 | 178.7 | 178.3 | 177.6 | **95.3** | 93.9 | 93.6 | 93.4 | 93.1 | 92.8 |
| $\tau/\sigma'_n$ **[der.]** | 1.026 | 1.057 | 1.091 | 1.127 | **1.165** | 0.923 | 0.859 | 0.808 | 0.764 | 0.723 | 0.686 |

#### SW-T2 (tensile, JRC 14.63, $\theta = 30^\circ$ **[derived]**, Table 1 says 31°)

| $P_i$ (MPa) | 8 | 12 | 16 | 20 | 24 | **28** | 24 | 20 | 16 | 12 | 8 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| $Q$ (mL/min) | 0.115 | 0.276 | 0.450 | 0.750 | 1.505 | **11.100** | 7.200 | 5.150 | 3.540 | 2.160 | 0.910 |
| $d_n$ (mm) | 0.000 | −0.001 | −0.002 | −0.003 | −0.005 | **−0.142** | −0.142 | −0.139 | −0.139 | −0.133 | −0.130 |
| $d_s$ (mm) | 0.000 | 0.001 | 0.003 | 0.007 | 0.015 | **0.571** | 0.572 | 0.566 | 0.565 | 0.557 | 0.552 |
| $\sigma'_n$ (MPa) | 66.74 | 64.53 | 62.37 | 60.19 | 57.88 | **29.36** | 31.26 | 33.23 | 35.23 | 37.18 | 39.14 |
| $\tau$ (MPa) | 74.87 | 74.54 | 74.25 | 73.94 | 73.40 | **27.48** | 27.29 | 27.24 | 27.25 | 27.15 | 27.09 |
| $a_h$ (μm) | 2.11 | 2.13 | 2.16 | 2.31 | 2.69 | **4.92** | 4.54 | 4.39 | 4.30 | 4.24 | 4.21 |
| $k$ (10⁻¹² m²) | 0.37 | 0.38 | 0.39 | 0.44 | 0.60 | **2.02** | 1.72 | 1.61 | 1.54 | 1.50 | 1.48 |
| $\sigma_d$ **[der.]** | 172.9 | 172.1 | 171.5 | 170.8 | 169.5 | **63.5** | 63.0 | 62.9 | 62.9 | 62.7 | 62.6 |
| $\sigma_1$ **[der.]** | 202.9 | 202.1 | 201.5 | 200.8 | 199.5 | **93.5** | 93.0 | 92.9 | 92.9 | 92.7 | 92.6 |
| $\tau/\sigma'_n$ **[der.]** | 1.122 | 1.155 | 1.190 | 1.228 | **1.268** | 0.936 | 0.873 | 0.820 | 0.773 | 0.730 | 0.692 |

#### SW-S3 (saw cut, JRC 1.96, $\theta = 29^\circ$)

| $P_i$ (MPa) | 8 | 12 | 16 | 20 | 24 | **28** | 24 | 20 | 16 | 12 | 8 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| $Q$ (mL/min) | 0.022 | 0.050 | 0.078 | 0.121 | 0.150 | **0.860** | 0.460 | 0.310 | 0.210 | 0.130 | 0.054 |
| $d_n$ (mm) | 0.000 | 0.000 | 0.000 | 0.000 | 0.000 | **−0.044** | −0.044 | −0.044 | −0.043 | −0.042 | −0.041 |
| $d_s$ (mm) | 0.000 | 0.000 | 0.000 | 0.001 | 0.001 | **0.071** | 0.072 | 0.072 | 0.073 | 0.073 | 0.073 |
| $\sigma'_n$ (MPa) | 31.65 | 29.58 | 27.53 | 25.48 | 23.42 | **15.25** | 17.27 | 19.14 | 21.01 | 22.86 | 24.79 |
| $\tau$ (MPa) | 14.70 | 14.57 | 14.48 | 14.38 | 14.26 | **3.55** | 3.19 | 2.95 | 2.68 | 2.44 | 2.31 |
| $a_h$ (μm) | 1.22 | 1.21 | 1.20 | 1.26 | 1.25 | **2.10** | 1.81 | 1.72 | 1.68 | 1.66 | 1.64 |
| $k$ (10⁻¹³ m²) | 1.24 | 1.21 | 1.21 | 1.32 | 1.30 | **3.66** | 2.74 | 2.47 | 2.34 | 2.30 | 2.25 |
| $\sigma_d$ **[der.]** | 34.7 | 34.4 | 34.1 | 33.9 | 33.6 | **8.4** | 7.5 | 7.0 | 6.3 | 5.8 | 5.4 |
| $\sigma_1$ **[der.]** | 64.7 | 64.4 | 64.1 | 63.9 | 63.6 | **38.4** | 37.5 | 37.0 | 36.3 | 35.8 | 35.4 |
| $\tau/\sigma'_n$ **[der.]** | 0.464 | 0.493 | 0.526 | 0.564 | **0.609** | 0.233 | 0.185 | 0.154 | 0.128 | 0.107 | 0.093 |

#### SW-S4 (polished saw cut, JRC 1.19, $\theta = 30^\circ$) — the baseline case

| $P_i$ (MPa) | 8 | 12 | 16 | 20 | 24 | **28** | 24 | 20 | 16 | 12 | 8 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| $Q$ (mL/min) | 0.005 | 0.012 | 0.022 | 0.035 | 0.056 | **0.113** | 0.064 | 0.037 | 0.024 | 0.013 | 0.005 |
| $d_n$ (mm) | 0.000 | 0.000 | −0.001 | −0.008 | −0.021 | **−0.041** | −0.038 | −0.036 | −0.034 | −0.033 | −0.032 |
| $d_s$ (mm) | 0.000 | 0.000 | 0.000 | 0.017 | 0.041 | **0.075** | 0.077 | 0.078 | 0.079 | 0.079 | 0.079 |
| $\sigma'_n$ (MPa) | 30.75 | 28.73 | 26.51 | 22.92 | 19.25 | **15.31** | 17.13 | 19.00 | 20.89 | 22.82 | 24.81 |
| $\tau$ (MPa) | 12.56 | 12.53 | 12.14 | 9.38 | 6.48 | **3.12** | 2.82 | 2.59 | 2.41 | 2.28 | 2.27 |
| $a_h$ (μm) | 0.74 | 0.75 | 0.79 | 0.83 | 0.90 | **1.07** | 0.94 | 0.85 | 0.81 | 0.77 | 0.74 |
| $k$ (10⁻¹³ m²) | 0.46 | 0.47 | 0.52 | 0.58 | 0.67 | **0.95** | 0.74 | 0.60 | 0.55 | 0.49 | 0.46 |
| $\sigma_d$ **[der.]** | 29.0 | 28.9 | 28.0 | 21.7 | 15.0 | **7.2** | 6.5 | 6.0 | 5.6 | 5.3 | 5.2 |
| $\sigma_1$ **[der.]** | 59.0 | 58.9 | 58.0 | 51.7 | 45.0 | **37.2** | 36.5 | 36.0 | 35.6 | 35.3 | 35.2 |
| $\tau/\sigma'_n$ **[der.]** | 0.408 | 0.436 | **0.458** | 0.409 | 0.337 | 0.204 | 0.165 | 0.136 | 0.115 | 0.100 | 0.091 |

**SW-S4 is qualitatively different from the other three and that is the point of
including it.** It has no burst. Slip begins above $P_i = 16$ MPa and
accumulates gradually across three pressure steps, and $\tau$ falls continuously
from 12.1 to 3.1 MPa *while slipping*. The other three sit at nearly constant
$\tau$ through five steps and then collapse in one step. A model that produces a
burst for SW-S4, or a gradual ramp for SW-T1, has the wrong stability regime
even if its endpoints match.


#### Canonical machine-readable extraction — all four samples

<a id="sup-table2csv"></a>

The four tables above are the human-readable form. This block is the same data in
one place, in a form that can be pasted straight into a script — it is the
single source of truth for scoring a run, and everything in it has been
cross-checked (Chapter [`sup:thetacheck`](#sup-thetacheck)).

**Columns.** `t_s` is the hold-stage time **[derived]**, recovered by locating the
eleven pressure plateaus in the digitized $P_i(t)$ curve for each sample (split at
the peak so the loading and unloading branches are matched in order, then the
midpoint of the longest contiguous run within 0.8 MPa of each target). Every
recovered time interpolates back to its target $P_i$ within 0.3 MPa. Use it only
to place Table 2 markers on a time axis; the *values* are the paper's, the
*times* are inferred from a digitization.

`Pp_MPa` $=\tfrac12(P_i+P_o)$ with $P_o = 5$ MPa; `dP_MPa` $= P_i - P_o$ is the
head driving the flow. `sigma_d_MPa`, `sigma_1_MPa` and `tau_over_sigma_n` are
**[derived]** — $\sigma_d = \tau/\sin\theta\cos\theta$,
$\sigma_1 = \sigma_d + \sigma_3$ with $\sigma_3 = 30$ MPa, using the
**data-derived** angles (SW-T2 at 30°, not Table 1's 31°). `k_m2` is in absolute
m², not the paper's per-sample $10^{-12}$/$10^{-13}$ scaling.

Sign convention is the paper's — **compression positive, so `dn_mm` is negative in
dilation.** Flip it before comparing against an ORCA normal gap.

```csv
sample,segment,stage,t_s,Pi_MPa,Pp_MPa,dP_MPa,Q_ml_min,dn_mm,ds_mm,sigma_n_eff_MPa,tau_MPa,ah_um,k_m2,sigma_d_MPa,sigma_1_MPa,tau_over_sigma_n
SW-T1,load,1,225.2,8,6.5,3,0.053,0.000,0.000,65.47,67.16,1.63,2.2000e-13,149.44,179.44,1.026
SW-T1,load,2,556.9,12,8.5,7,0.114,0.000,0.000,63.35,66.96,1.59,2.1000e-13,149.00,179.00,1.057
SW-T1,load,3,838.6,16,10.5,11,0.19,0.000,0.001,61.27,66.82,1.62,2.2000e-13,148.69,178.69,1.091
SW-T1,load,4,1164.2,20,12.5,15,0.28,-0.001,0.002,59.14,66.63,1.66,2.3000e-13,148.27,178.27,1.127
SW-T1,load,5,1436.6,24,14.5,19,0.389,-0.003,0.008,56.94,66.32,1.72,2.5000e-13,147.58,177.58,1.165
SW-T1,load,6,1704.7,28,16.5,23,6.22,-0.157,0.532,31.79,29.35,4.05,1.3700e-12,65.31,95.31,0.923
SW-T1,unload,7,2063.5,24,14.5,19,4.27,-0.139,0.539,33.45,28.72,3.81,1.2100e-12,63.91,93.91,0.859
SW-T1,unload,8,2336.9,20,12.5,15,2.87,-0.130,0.534,35.35,28.57,3.61,1.0900e-12,63.57,93.57,0.808
SW-T1,unload,9,2629.0,16,10.5,11,1.9,-0.123,0.529,37.29,28.48,3.49,1.0200e-12,63.37,93.37,0.764
SW-T1,unload,10,2952.2,12,8.5,7,1.12,-0.118,0.525,39.22,28.36,3.40,9.7000e-13,63.11,93.11,0.723
SW-T1,unload,11,3256.8,8,6.5,3,0.462,-0.113,0.521,41.14,28.23,3.36,9.4000e-13,62.82,92.82,0.686
SW-T2,load,1,319.6,8,6.5,3,0.115,0.000,0.000,66.74,74.87,2.11,3.7000e-13,172.90,202.90,1.122
SW-T2,load,2,766.3,12,8.5,7,0.276,-0.001,0.001,64.53,74.54,2.13,3.8000e-13,172.14,202.14,1.155
SW-T2,load,3,1223.5,16,10.5,11,0.45,-0.002,0.003,62.37,74.25,2.16,3.9000e-13,171.47,201.47,1.190
SW-T2,load,4,1628.8,20,12.5,15,0.75,-0.003,0.007,60.19,73.94,2.31,4.4000e-13,170.76,200.76,1.228
SW-T2,load,5,1992.5,24,14.5,19,1.505,-0.005,0.015,57.88,73.40,2.69,6.0000e-13,169.51,199.51,1.268
SW-T2,load,6,2319.3,28,16.5,23,11.1,-0.142,0.571,29.36,27.48,4.92,2.0200e-12,63.46,93.46,0.936
SW-T2,unload,7,2537.1,24,14.5,19,7.2,-0.142,0.572,31.26,27.29,4.54,1.7200e-12,63.02,93.02,0.873
SW-T2,unload,8,2587.8,20,12.5,15,5.15,-0.139,0.566,33.23,27.24,4.39,1.6100e-12,62.91,92.91,0.820
SW-T2,unload,9,2638.3,16,10.5,11,3.54,-0.139,0.565,35.23,27.25,4.30,1.5400e-12,62.93,92.93,0.773
SW-T2,unload,10,2657.6,12,8.5,7,2.16,-0.133,0.557,37.18,27.15,4.24,1.5000e-12,62.70,92.70,0.730
SW-T2,unload,11,2766.4,8,6.5,3,0.91,-0.130,0.552,39.14,27.09,4.21,1.4800e-12,62.56,92.56,0.692
SW-S3,load,1,335.9,8,6.5,3,0.022,0.000,0.000,31.65,14.70,1.22,1.2400e-13,34.67,64.67,0.464
SW-S3,load,2,868.4,12,8.5,7,0.05,0.000,0.000,29.58,14.57,1.21,1.2100e-13,34.36,64.36,0.493
SW-S3,load,3,1364.0,16,10.5,11,0.078,0.000,0.000,27.53,14.48,1.20,1.2100e-13,34.15,64.15,0.526
SW-S3,load,4,1804.7,20,12.5,15,0.121,0.000,0.001,25.48,14.38,1.26,1.3200e-13,33.91,63.91,0.564
SW-S3,load,5,2236.5,24,14.5,19,0.15,0.000,0.001,23.42,14.26,1.25,1.3000e-13,33.63,63.63,0.609
SW-S3,load,6,2522.5,28,16.5,23,0.86,-0.044,0.071,15.25,3.55,2.10,3.6600e-13,8.37,38.37,0.233
SW-S3,unload,7,3019.0,24,14.5,19,0.46,-0.044,0.072,17.27,3.19,1.81,2.7400e-13,7.52,37.52,0.185
SW-S3,unload,8,3475.3,20,12.5,15,0.31,-0.044,0.072,19.14,2.95,1.72,2.4700e-13,6.96,36.96,0.154
SW-S3,unload,9,3854.0,16,10.5,11,0.21,-0.043,0.073,21.01,2.68,1.68,2.3400e-13,6.32,36.32,0.128
SW-S3,unload,10,4241.6,12,8.5,7,0.13,-0.042,0.073,22.86,2.44,1.66,2.3000e-13,5.75,35.75,0.107
SW-S3,unload,11,4674.7,8,6.5,3,0.054,-0.041,0.073,24.79,2.31,1.64,2.2500e-13,5.45,35.45,0.093
SW-S4,load,1,252.5,8,6.5,3,0.005,0.000,0.000,30.75,12.56,0.74,4.6000e-14,29.01,59.01,0.408
SW-S4,load,2,570.5,12,8.5,7,0.012,0.000,0.000,28.73,12.53,0.75,4.7000e-14,28.94,58.94,0.436
SW-S4,load,3,849.3,16,10.5,11,0.022,-0.001,0.000,26.51,12.14,0.79,5.2000e-14,28.04,58.04,0.458
SW-S4,load,4,1157.5,20,12.5,15,0.035,-0.008,0.017,22.92,9.38,0.83,5.8000e-14,21.66,51.66,0.409
SW-S4,load,5,1471.4,24,14.5,19,0.056,-0.021,0.041,19.25,6.48,0.90,6.7000e-14,14.96,44.96,0.337
SW-S4,load,6,1703.9,28,16.5,23,0.113,-0.041,0.075,15.31,3.12,1.07,9.5000e-14,7.21,37.21,0.204
SW-S4,unload,7,2046.8,24,14.5,19,0.064,-0.038,0.077,17.13,2.82,0.94,7.4000e-14,6.51,36.51,0.165
SW-S4,unload,8,2359.3,20,12.5,15,0.037,-0.036,0.078,19.00,2.59,0.85,6.0000e-14,5.98,35.98,0.136
SW-S4,unload,9,2668.7,16,10.5,11,0.024,-0.034,0.079,20.89,2.41,0.81,5.5000e-14,5.57,35.57,0.115
SW-S4,unload,10,2968.5,12,8.5,7,0.013,-0.033,0.079,22.82,2.28,0.77,4.9000e-14,5.27,35.27,0.100
SW-S4,unload,11,3293.5,8,6.5,3,0.005,-0.032,0.079,24.81,2.27,0.74,4.6000e-14,5.24,35.24,0.091
```

Loading it:

```python
import io, pandas as pd
TABLE2 = pd.read_csv(io.StringIO(CSV_TEXT))          # 44 rows = 4 samples x 11 stages
sw_s4  = TABLE2[TABLE2["sample"] == "SW-S4"]
```

**Self-checks this block passes.**

| Check | Result |
|---|---|
| Row count | 44 = 4 samples × 11 hold stages |
| $k$ against $a_h^2/12$ | agrees to 1.4% worst case — entirely the 2-decimal rounding of $a_h$ |
| $\tan\theta = (\sigma'_n-\sigma_3+P_p)/\tau$ | within 0.40° of the sample angle at 43 of 44 rows |
| The 44th row | SW-S3 stage 6 (peak slip), which returns 26.2° instead of 29° — see [`sup:thetacheck`](#sup-thetacheck). Down-weight it; do not delete it |
| Recovered hold times | every one interpolates back to its target $P_i$ within 0.3 MPa |
| Against `SWT_TABLE2` in the analysis notebook | all eight data columns of SW-T1 and SW-T2 agree **exactly** (worst mismatch 0.0), an independent confirmation of this transcription |

One caveat on the time column. The analysis notebook carries its own SW-T1 and SW-T2
hold times from an earlier digitization; they differ from the values above by up to
90 s. Both sit inside the same pressure plateau, which is 150–250 s wide, so neither
is wrong — but do not treat a sub-100 s difference in these times as meaningful. The
notebook's SW-S3 and SW-S4 times are the ones derived here.

**Do not score $k$ and $a_h$ as separate observables.** $k$ is $a_h^2/12$ by
construction and $a_h$ is back-computed from $Q$, so both are $Q$ in disguise. The
independent observables are $Q$, $\sigma'_n$, $\tau$, $d_n$, $d_s$.

#### Slip and stress-relaxation rates (Table 3)

| Sample | $\dot d_s$ quasi-static 1 (m/s) | $\dot d_s$ **dynamic** (m/s) | $\dot d_s$ quasi-static 2 (m/s) | $\dot\sigma_d$ q-s 1 (MPa/s) | $\dot\sigma_d$ **dyn** (MPa/s) | $\dot\sigma_d$ q-s 2 (MPa/s) |
|---|---|---|---|---|---|---|
| SW-T1 | 1.76×10⁻⁶ | **4.89×10⁻⁵** | 1.07×10⁻⁶ | −0.33 | **−7.69** | −0.15 |
| SW-T2 | 1.61×10⁻⁶ | **9.81×10⁻⁵** | 1.01×10⁻⁶ | −0.25 | **−19.51** | +0.20 |
| SW-S3 | 2.35×10⁻⁸ | **1.05×10⁻⁵** | 1.21×10⁻⁶ | −0.03 | **−6.56** | −0.16 |
| SW-S4 | 2.38×10⁻⁹ | **3.22×10⁻⁷** | 1.47×10⁻⁸ | −5.14×10⁻⁴ | **−0.08** | −5.03×10⁻⁴ |

Both $d_s(t)$ and $\sigma_d(t)$ are **piecewise linear** in the slip period —
three straight segments, not a smooth curve. The dynamic interval lasts <10 s
for the rough fractures and ~100 s for SW-S4. The paper adopts Nemoto et al.
(2008)'s threshold of $5\times10^{-5}$ m/s to separate quasi-static from
dynamic, and notes that the rough-fracture rates match Guglielmi et al. (2015)'s
in-situ measurements of $10^{-6}$–$10^{-5}$ m/s at the onset of microseismicity.

Note SW-T2's **positive** $\dot\sigma_d$ in the second quasi-static interval: the
differential stress recovers slightly after the burst. That is a re-loading of
the frame as the slip arrests, and a model with a correct series-compliance BC
should reproduce it.

#### Retention — [derived]

Three different retention measures give three different pictures, and conflating
them is the mistake that cost this project a bad SW-S4 run.

| Sample | JRC | $k$ retention ratio (paper) | $k$ ratio recomputed **[der.]** | $a_h$ **increase** retained **[der.]** | $d_n$ retained **[der.]** | $d_s$ retained **[der.]** |
|---|---|---|---|---|---|---|
| SW-T1 | 15.32 | ≈5 | 4.6 | **71%** | 72% | 98% |
| SW-T2 | 14.63 | ≈4 | 3.7 | **75%** | 92% | 97% |
| SW-S3 | 1.96 | ≈2 | 1.9 | **48%** | 93% | 103% |
| SW-S4 | 1.19 | ≈1 | 1.05 | **0%** | 78% | 105% |

Definitions: the *$k$ retention ratio* is $k_{\text{unload}}/k_{\text{load}}$ at
the same $P_i$, averaged over the five common steps — the paper's own measure.
The *$a_h$ increase retained* is
$(a_h^{\text{end}}-a_h^{\text{init}})/(a_h^{\text{peak}}-a_h^{\text{init}})$.
The displacement retentions are $|d^{\text{end}}|/|d^{\text{peak}}|$.

The recomputed ratios reproduce the paper's rounded 5/4/2/≈1 exactly, which
validates the transcription.

**The decisive row is SW-S4: 78% of the mechanical dilation is retained while
0% of the hydraulic aperture increase is.** The fracture stays geometrically
propped open by ~32 μm and yet conducts exactly as it did before it slipped.
Any aperture law of the form $a_h = a_{h0} + \chi\,d_n$ with $\chi$ of order 1
is therefore *structurally wrong for this sample*: it predicts a 32 μm
conducting aperture where the data says 0.74 μm — a factor of 43. The paper
states the physical reason directly: for an ideally smooth fracture with
insufficient asperities the permeability increase is negligible. The
self-propping mechanism requires asperities, and SW-S4 has almost none.

This is why the four samples need different $\chi$, and why that is a **result**
rather than a fudge: $\chi$ tracks the retention column, which is measured.

#### Enhancement summary — [derived]

| Sample | $Q$ increase | $k$ increase | peak $d_s$ (mm) | peak $d_n$ (mm) | $\sigma_d$ drop (MPa) | slip style |
|---|---|---|---|---|---|---|
| SW-T1 | 117× | 6.2× | 0.532 | −0.157 | 149→65 (−84) | burst, <10 s |
| SW-T2 | 97× | 5.5× | 0.571 | −0.142 | 173→63 (−110) | burst, <10 s |
| SW-S3 | 39× | 3.0× | 0.071 | −0.044 | 35→8 (−27) | burst, <10 s |
| SW-S4 | 23× | 2.1× | 0.075 | −0.041 | 29→7 (−22) | **gradual, 3 steps** |

Dilation-to-slip ratio $|d_n|/d_s$ at peak **[derived]**: 0.295 (T1), 0.249
(T2), 0.620 (S3), 0.547 (S4). Interpreted as a dilation angle
$\psi = \arctan(|d_n|/d_s)$ this is 16.4°, 14.0°, 31.8°, 28.7° — **the *smooth*
fractures show the larger apparent dilation angle**, which is the opposite of
the naive expectation and is worth thinking about before tuning
`dilation_angle_peak_degrees`. The most likely reading is that the rough
fractures' slip includes a large component accommodated by asperity *damage*
(chips and gouge, observed) rather than override, whereas the saw cuts slide
over their small asperities without destroying them. This is testable against
the model's damage/roughness state variable.

#### The friction the data implies — [derived]

<a id="sup-friction"></a>

Reading $\tau/\sigma'_n$ *only at stages where the fracture is actually
slipping* gives points on the strength envelope. At stages where it is stuck,
$\tau/\sigma'_n$ is merely a stress ratio below the strength — a lower bound.

| Sample | $\mu$ at last stick stage (lower bound on peak) | $\mu$ at slip arrest | $\mu$ at end of unload (stuck, lower bound) |
|---|---|---|---|
| SW-T1 | **1.165** | 0.923 | 0.686 |
| SW-T2 | **1.268** | 0.936 | 0.692 |
| SW-S3 | **0.609** | 0.233 | 0.093 |
| SW-S4 | **0.458** | 0.204 | 0.091 |

For SW-S4, which slips gradually, the whole weakening curve is visible directly:

| $d_s$ (μm) | 0 | 17 | 41 | 75 |
|---|---|---|---|---|
| $\tau/\sigma'_n$ | 0.458 | 0.409 | 0.337 | 0.204 |

That is a **measured slip-weakening law**: $\mu$ falls from 0.46 to 0.20 over
75 μm of slip. It is arguably the most directly usable constitutive constraint
in the entire paper, and it comes free — no fitting.

**A single Barton–Bandis $\phi_r$ cannot fit all four samples.** With
JCS = 150 MPa, $\tau_p = \sigma'_n\tan[\phi_r + \mathrm{JRC}\log_{10}(\mathrm{JCS}/\sigma'_n)]$
requires $\phi_r \approx 42$–43° to reach $\mu = 1.17$ on SW-T1 (the roughness
term supplies only 6.4° at JRC 15.32 and $\sigma'_n = 57$ MPa). The same
$\phi_r$ applied to SW-S4 predicts $\mu \approx 0.93$ against a measured 0.46,
because at JRC 1.19 the roughness term contributes under 1°. **The spread
between samples is far larger than JRC alone can explain**, so the polished
saw-cut surface must have a genuinely lower basic friction angle — which is
physically sensible (a ground surface is not a fresh tensile surface) but is not
something the JRC/JCS framework represents. Per-sample friction is not a
calibration convenience here; it is forced by the data.

---

### Correspondence with ORCA

<a id="sup-correspondence"></a>

#### What matches directly

| Quantity | Paper | ORCA deck | Status |
|---|---|---|---|
| $E$ | 67 GPa | `youngs_modulus = 67e9` | exact |
| $\nu$ | 0.32 | `poissons_ratio = 0.32` | exact |
| $\sigma_3$ | 30 MPa, all samples | `confining_pressure = 30e6` | exact, and independently confirmed [`sup:thetacheck`](#sup-thetacheck) |
| $P_o$ | 5 MPa constant | `production_pressure = 5e6`, `DirichletBC` | exact |
| $P_i(t)$ | stepwise 5→28→8 MPa | digitized `PiecewiseLinear`, 120 points to $t=3405$ s | matches the published time series |
| $\mu_f$ | 1.002×10⁻³ Pa·s | `fluid_viscosity_ref` | exact |
| $k_{\text{matrix}}$ | 5×10⁻¹⁹–1×10⁻¹⁸ m² | `matrix_permeability = 5e-19` | lower bound taken; leakoff is 5–6 orders below fracture flow either way |
| Sample radius | $D/2 = 25.255$ mm (SW-S4) | `sample_radius = 0.025255` | exact |
| Borehole radial position | $D/2 - 6 = 19.255$ mm | source nodes at $x = \pm 0.019255$ | exact |
| Fracture area | 4.008×10⁻³ m² **[derived]** | `AreaPostprocessor` target | exact |
| Effective-stress coefficient on the fracture | 1 (Eq. 3) | 1 | matches |
| Confinement applied as a traction | $\sigma_3$ on the cylindrical surface | `FunctionNeumannBC` with analytic outward normal | matches |
| Series machine compliance | constant piston displacement | `FunctionPenaltyDirichletBC` (spring) | correct *structure*, fitted *magnitude* |
| Run duration | ~3405 s | `end_time = 3500` | covers the full cycle |

#### What is structurally different, and why

| # | Experiment | Model | Consequence |
|---|---|---|---|
| 1 | Injection through a 3.5 mm borehole | Pressure imposed at the **single closest node** (`ExtraNodesetGenerator`, `use_closest_node`) | Point source. The near-source pressure gradient is mesh-dependent and the flux into the fracture is not mesh-convergent. Known open item. |
| 2 | $P_p = \tfrac12(P_i+P_o)$, a scalar proxy | Full pressure field on the fracture | $\sigma'_n$ is a different operator. The model must report the *proxy* form for any Table 2 comparison. |
| 3 | $d_n, d_s$ from whole-specimen LVDTs, matrix contribution not removed | Fracture-plane jump | Different operators, differing by the elastic matrix share — ~39 μm axial for SW-S4's stress drop, against $d_s = 75$ μm. Not negligible. |
| 4 | $a_h$ from a steady-state $Q$ through an equivalent rectangle | Local, spatially varying $a_h$ field | Must be reduced through the *same* $W/L = 0.81$ and evaluated only at hold stages. |
| 5 | Dynamic slip at $10^{-5}$ m/s over <10 s | Quasi-static, no inertia; regularized by $\eta = 5\times10^{12}$ Pa·s/m and rate-and-state | The burst is *smoothed by construction*. The peak flow-rate spike cannot be fully recovered. This is structural, not a mesh or tolerance issue. |
| 6 | Slip arrests by frame unloading through the real machine stiffness | Arrests by unloading through a fitted penalty stiffness | The arrest point — and hence final slip, final $\tau$ — is set by an unmeasured number. |
| 7 | Asperity damage: chips up to 5×10 mm, gouge 0.1–1.0 mm, JRC 15.32→10.21 | Roughness state variable $R(\gamma)$ with `roughness_decay_distance`; gouge as a scalar aperture fill $a_g$ | **Currently unexploited.** See below. |
| 8 | Five pre-seating cycles before the test | Pre-seating offset $c_0$ in the BB closure | Matching intent; $c_0$ is fitted, the cycles are described but their resulting seating displacement is not reported. |
| 9 | Fracture is a real surface with a JRC *distribution* (SW-T1: ~10 to ~20) | Single scalar `jrc` | A mean over a distribution with substantial spread. Heterogeneity is not represented. |
| 10 | 3-D flow over an ellipse between two point boreholes | 3-D flow on the split interface | Structurally the same; the *reduction* to $W$, $L$ is the idealization, not the model. |

#### An unexploited validation opportunity

Item 7 above is worth pulling out. The paper reports a **measured change in
roughness**:

| Sample | JRC before | JRC after | Change | Max asperity height reduction |
|---|---|---|---|---|
| SW-T1 | 15.32 | 10.21 | **−33%** | 0.51–1.22 mm |
| SW-T2 | 14.63 | 11.27 | **−23%** | 0.30–1.45 mm |
| SW-S3 | 1.96 | not reported | (minor damage, fine gouge <0.3 mm) | — |
| SW-S4 | 1.19 | not reported | (minor damage, fine gouge <0.3 mm) | — |

The `CompressionTensile` law carries a roughness state
$R(\gamma) = R_{\text{res}} + (R_0-R_{\text{res}})e^{-\gamma/L_R}$ that is
supposed to represent exactly this. With `roughness_decay_distance` = 115 μm and
SW-T1's 532 μm of slip, $R$ would be almost fully decayed to residual — which
would have to be reconciled with a measured 33% JRC reduction, not 100%. **This
is an independent, currently unused observable that constrains $L_R$ directly**,
and it is available for the two samples where roughness matters most. It would
strengthen the paper considerably: it converts a fitted decay length into a
calibrated one.

The paper also reports *where* the damage occurred — large chips at the fracture
edges near the sidewall, fine gouge in the interior, which the authors attribute
to the interior experiencing a longer shearing/crushing history. A model with a
spatially varying roughness field could be compared against that pattern
qualitatively.

#### The paper does not report

Everything in this list is a **free parameter** in the model. Stating it
explicitly, in the paper, in a table, is the difference between a validation and
a curve fit.

| Missing quantity | Needed by | Current handling |
|---|---|---|
| Joint basic/residual friction angle $\phi_r$ | all four laws | fitted per sample; strongly constrained by [`sup:friction`](#sup-friction) |
| JCS | Barton–Bandis laws | UCS = 150 MPa substituted on SW-T1/T2; **300 MPa on SW-S3/S4** — see below |
| Joint normal stiffness $K_{ni}$, max closure $V_m$ | BB closure | fitted to Table 2 $a_h(\sigma'_n)$ |
| Machine/frame stiffness | the arrest mechanism | fitted penalty (1.2×10¹² Pa/m for SW-S4) |
| Initial $\sigma_1$ at start of injection | the whole stress path | **recoverable** — see the $\sigma_1$ rows in [`sup:data`](#sup-data) |
| Biot coefficient $\alpha$ | bulk poroelasticity | 0.6 from literature for granite |
| Porosity $\phi$ | storage | 0.001 assumed |
| Dilation angle | dilatancy | fitted; but $|d_n|/d_s$ is measured, see [`sup:data`](#sup-data) |
| Rate-and-state $a$, $b$, $D_c$, $V_0$ | RSF laws | fitted; the *rates* in Table 3 constrain them |
| Slip-weakening distance | all laws | fitted; measured directly for SW-S4 |
| Gouge fill parameters $a_g$, $s_c$ | permeability model | fitted to the unloading branch |

Of these, five (initial $\sigma_1$, dilation ratio, SW-S4's weakening curve, the
slip rates, and the JRC reduction) are **recoverable from the published data and
are not currently being used as constraints**. Using them would convert five
fitted parameters into calibrated ones.

#### JRC is reported — and two decks do not use the reported value

<a id="sup-jrcmismatch"></a>

Added 2026-08-16. JRC is *not* in the list above: Ye and Ghassemi measure it by
3-D laser scan (their Section 2.2, Figure 3) and report 15.32, 14.63, 1.96 and
1.19. SW-T1 and SW-T2 use the measured values. **SW-S3 and SW-S4 do not.**

| | JRC deck | JRC paper | JCS deck | UCS paper | $\phi_r$ deck |
|---|---|---|---|---|---|
| SW-T1 | 15.32 | 15.32 | 150 MPa | 150 MPa | 44.10° |
| SW-T2 | 14.63 | 14.63 | 150 MPa | 150 MPa | 46.29° |
| SW-S3 | **23.35** | **1.96** | **300 MPa** | 150 MPa | **8.45°** |
| SW-S4 | **17.50** | **1.19** | **300 MPa** | 150 MPa | **7.50°** |

SW-S3's 23.35 is outside Barton's 0–20 scale altogether. The sub-8.5° residual
friction angles are the compensation: the three errors cancel at the calibration
point, so both saw cuts still reproduce their measured peak $\tau$. What does not
cancel is $\mathrm{d}\tau/\mathrm{d}\sigma'_n$ — 0.423 against 0.589 for SW-S3 and
0.322 against 0.447 for SW-S4, i.e. **28% too flat on both** — and that derivative
is the whole point of an experiment in which injection halves $\sigma'_n$.

Refitting $\phi_r$ with the paper's own JRC and JCS = UCS, holding the envelope
through each specimen's last stick stage, gives $\phi_r = 29.76°$ for SW-S3 —
textbook granite basic friction — and $23.71°$ for SW-S4, low but defensible for a
lapped surface. That the paper's constants land on ordinary numbers is good
evidence they are the right ones.

The tensile pair is a different problem: both already use the measured JRC and
JCS, and both require $\phi_r \approx 44$–46° because they sustain
$\mu = \tau/\sigma'_n$ of 1.17–1.27 *while still stuck*. That is the interlock of
a perfectly mated Mode-I surface, and until 2026-08-16 it had nowhere to go,
because `computeCohesionEffective()` returned a hard-coded `0.0`. SW-T2's 46.29°
is essentially the paper's **intact-rock** friction angle of 46°.

##### Why Barton's law cannot express this, and what was added

<a id="sup-cohesion"></a>

The failure is structural, not a calibration accident. Barton's roughness term is
**mobilisation-limited**: $\mathrm{JRC}\log_{10}(\mathrm{JCS}/\sigma'_n)$ decays to
zero as $\sigma'_n \to \mathrm{JCS}$, encoding the physical fact that at high
normal stress asperities shear *through* rather than ride over. The tensile
specimens sit at $\sigma'_n/\mathrm{JCS} \approx 0.38$–0.39, where the measured
JRC = 15.32 buys only 6.44° of roughness angle. A $\mu$ of 1.17 then has nowhere
to live except $\phi_r$.

But shearing *through* asperities is a cohesion, not a friction: its strength does
not scale with $\sigma'_n$. So the law was given the missing term (branch
`orca_v5`, 2026-08-16):

<a id="eq-bbcohesion"></a>

$$
\boxed{\;\tau_{\lim} = c(s) + \sigma'_n\tan\!\left[\phi_r + \mathrm{JRC}\log_{10}\!\left(\frac{\mathrm{JCS}}{\sigma'_n}\right)\right],
\qquad c(s) = c_{\text{res}} + (c - c_{\text{res}})\,W\;}
$$

with $W = \exp[-(s^p/D_c)^m]$ — the *same* weakening factor that acts on friction,
because the asperities that carry $c$ are the ones the slip destroys. Parameters
`cohesion` and `residual_cohesion`, both defaulting to zero, so every existing
calibration is bit-identical. Regression test:
`test/tests/materials/bb_cohesion/`, which pins $c_{\text{eff}} = c\,W$ to
2.4 × 10⁻¹² % and keeps the cohesionless case as a legacy guard.

Refitting the tensile pair with $\phi_r$ fixed at the basic friction angle
measured on **this campaign's own saw cut** (SW-S3's refitted 29.756°) gives:

| | $c$ peak | as % of $c_{\text{intact}}$ | $c_{\text{res}}$ | replaces $\phi_r$ |
|---|---|---|---|---|
| SW-T1 | 24.65 MPa | 81 % | 11.18 MPa | 44.10° |
| SW-T2 | 31.65 MPa | 104 % | 10.70 MPa | 46.29° |

where $c_{\text{intact}} = \mathrm{UCS}\,(1-\sin\phi)/(2\cos\phi) = 30.30$ MPa
follows from the paper's own UCS = 150 MPa and intact $\phi = 46°$. **The two
cohesions straddle the intact value.** Nothing in the derivation knows about
$c_{\text{intact}}$, so this is a result rather than a fit — and it is exactly what
a fully mated Mode-I fracture should show, since its asperities *are* intact rock.
The $\phi_r = 44$–46° parameterisation it replaces admits no such reading.

The tail friction angle goes to $\phi_r$ as well: slip destroys **roughness**, not
the rock's basic friction angle, which is Barton's own picture. The residual
cohesion is then pinned on the post-burst stage, and comes out at 34–45 % of the
peak — consistent with Table 2 showing these two joints retaining 72–92 % of their
dilation through the burst.

This changes $\mathrm{d}\tau/\mathrm{d}\sigma'_n$ from 0.928 to 0.554 (SW-T1) and
0.999 to 0.553 (SW-T2), so the two decks that use it (`89_04`, `89_05`) are
**candidates that must be scored**, not drop-in corrections.

Full working: `doc/paper_vs_model_audit_2026-08-16.md` §2 and
`scripts/refit_joint_constants_from_paper.py`.

---

### Internal-consistency checks on the published data

<a id="sup-thetacheck"></a>

Table 2 reports both $\sigma'_n$ and $\tau$ at every stage. Given $\sigma_3$ and
$P_p$, these are two functions of the single unknown $\sigma_d$, so their ratio
depends on $\theta$ alone. Dividing Eq. (3) by Eq. (4):

$$
\boxed{\;\tan\theta = \frac{\sigma'_n - \sigma_3 + P_p}{\tau}\;}
$$

This is a strong test: it must return the same $\theta$ at all eleven hold
stages, and it must agree with Table 1.

**Result for all four samples, all stages, with $\sigma_3 = 30$ MPa:**

| Sample | $\tan\theta$ recovered (range over 11 stages) | $\theta$ | Table 1 | verdict |
|---|---|---|---|---|
| SW-T1 | 0.6232–0.6251 | **32.0°** | 32° | ✅ agrees |
| SW-T2 | 0.5771–0.5775 | **30.0°** | 31° | ⚠️ **disagrees** |
| SW-S3 | 0.4930–0.5634 | **29.0°** | 29° | ✅ agrees (one outlier) |
| SW-S4 | 0.5768–0.5801 | **30.0°** | 30° | ✅ agrees |

Three consequences.

1. **$\sigma_3 = 30$ MPa for all four samples is confirmed.** The recovered
    angles land on the tabulated integers to four significant figures only for
    the correct $\sigma_3$; a 2 MPa error would shift them by ~1°.
1. **SW-T2's fracture angle is 30°, not the 31° in Table 1.** The value 0.5774
    ($=\tan 30^\circ$) is reproduced at every one of the eleven stages, loading
    and unloading, to four digits; $\tan 31^\circ = 0.6009$ is nowhere near.
    Either Table 1 has a typographical error or the data reduction used 30°.
    **Either way, the SW-T2 mesh must be built at 30°** — using 31° would put
    the model's $\tau$ and $\sigma'_n$ on a stress path the reported data was
    never on. This is a real and easily-missed input error.
1. **One outlier: SW-S3 at $P_i = 28$ MPa** returns $\tan\theta = 0.493$
    (26.2°) instead of 0.554. Every other SW-S3 stage is consistent. The
    numerator is a difference of large numbers (1.75 from 15.25, 30, 16.5), so it
    is sensitive, but not this sensitive — reproducing the correct angle would
    need $\tau = 3.16$ rather than 3.55, or $\sigma'_n = 15.97$ rather than
    15.25. The most likely explanation is that during a <10 s burst the two
    quantities were sampled at slightly different instants. **Do not weight the
    SW-S3 peak-slip point heavily in scoring**; treat it as carrying ~10%
    uncertainty rather than the ~1% of the other stages.

#### Applied to the ORCA meshes

Running the same test against the shipped Exodus files (least-squares fit of
$z(x)$ over the `fracture_interface` nodeset) found that **two of the four
meshes are cut at the wrong angle**:

| Sample | mesh $\theta$ | Table 1 | recovered from Table 2 | plane centred? |
|---|---|---|---|---|
| SW-T1 | 32.000° | 32° | 32.0° | yes |
| SW-S3 | 29.000° | 29° | 29.0° | yes |
| SW-S4 | **28.990°** | 30° | **30.0°** | **no — 2.85 mm low** |
| SW-T2 | **31.000°** | 31° | **30.0°** | yes |

SW-S4's journal is a copy of SW-S3's: the plane's $z$-span is bit-identical
(`0.09115854`), and the shift applied was 5.70 mm, exactly twice the 2.85 mm
required — so both the angle and the centring went wrong in one edit. SW-T2
faithfully reproduces the printed 31°, which is the problem, because the data it
is compared against was reduced at 30°.

Cost, at fixed $\sigma_d$: $\tau$ 2.1% low (SW-S4) / 2.0% high (SW-T2), and the
deviatoric part of $\sigma'_n$ 6.1% low / high.

> **Status in this repository — RESOLVED 2026-08-16.** Corrected meshes, SW-S4 and
> SW-T2 both at 30.000° and both centred, are now **here**:
>
> ```
> SWS4/mesh/ye2018_sw_s4_theta30_size{3,5}_mesh.e     theta = 30.000, centred
> SWT2/mesh/ye2018_sw_T2_theta30_mesh_size_{3,5}.e    theta = 30.000, centred
> ```
>
> They were built in `orca_3.0_claude_edit/.../final_simulation_runs_v3/meshes/` and
> had never been ported into a repo the production decks run from. An earlier
> edition of this manual said the fix had been applied "in both campaign
> directories" and cited `README_fracture_angle.md` and `PHYSICS_FIXES.md` as
> though they were paths in this tree; that was true of `orca_3.0_claude_edit` and
> was never true of `orca_4.0`. The angle in each `.e` was re-derived here by
> fitting a plane to the nodes shared by the two element blocks, not taken on trust
> from the journal.
>
> The 68/86/87 decks still load the as-found meshes, deliberately, so their results
> stay reproducible. The 89-series decks load the corrected ones. Inventory and the
> full verification procedure: `Examples/YeGhasemmi2018/MESHES.md`.
>
> **SW-S3's length is still outstanding**: the mesh is 124.40 mm against Table 1's
> 123.40 mm. `SWS3/mesh/sw3_mesh_L123p4.jou` is the corrected journal but has not
> been built, because that needs Cubit and Cubit is not installed here. The effect
> is 0.8 % on the core's axial stiffness and nothing else — the fracture ellipse
> area $\pi D^2/(4\sin\theta)$ does not contain $L$, and the deck takes $W/L$ from
> Table 2 rather than from the mesh.
>
> **After any mesh rebuild, run `scripts/check_source_nodes.py`.** It is not
> optional. `ExtraNodesetGenerator ... use_closest_node = true` never errors: if the
> requested injection coordinate misses the fracture plane it silently pins the
> source to the nearest *bulk* node and the run drives the matrix instead of the
> joint. On the corrected SW-S4 size-5 mesh the ideal borehole position has a bulk
> node 1.734 mm away and the nearest interface node 1.776 mm away — the bulk node
> wins. The 89-series decks therefore carry exact interface-node coordinates.
>
> Re-derive the angles themselves with `scripts/paper_parameter_audit.py`, which
> carries this check and re-reads the decks so it cannot go stale.

A second check confirms the transcription: $k$ recomputed as $a_h^2/12$
reproduces every tabulated $k$ (e.g. SW-S4 stage 1:
$(0.74\times10^{-6})^2/12 = 4.56\times10^{-14}$ against 0.46×10⁻¹³ ✓), and the
retention ratios recomputed from the $k$ columns reproduce the paper's stated
5/4/2/≈1.

---

### What the data can and cannot constrain

<a id="sup-constrained"></a>

#### Eleven points per sample

Each sample yields **11 hold stages**. At each stage there are five independent
measurements ($Q$, $\sigma'_n$, $\tau$, $d_n$, $d_s$) — $a_h$ and $k$ are
algebraic functions of $Q$, not independent. That is 55 numbers per sample, but
they are far from independent of each other: $\sigma'_n$ and $\tau$ are two
views of one $\sigma_d(t)$, and $d_n$, $d_s$ are strongly correlated through the
dilation angle.

Against that, the model carries on the order of 30 parameters, of which perhaps
12–15 are genuinely free. **The system is not comfortably over-determined.**
This is the central honest limitation and it should be stated in the paper
rather than discovered by a reviewer.

#### Known degeneracies

- **Aperture law.** The terms $\chi\,d_n$ (dilation propping) and
    $V_m[g(\sigma_{\text{ref}})-g(\sigma'_n)]$ (stress closure) are partly
    collinear over 11 points, because $d_n$ and $\sigma'_n$ move together for
    most of the test. The *split* between the two mechanisms is not uniquely
    determined by these data. The **retention ratios**, however, are directly
    observed, and they are what makes $\chi \approx 0$ for SW-S4 and
    $\chi > 0$ for the rough samples defensible.
- **Friction versus frame stiffness.** The arrest point is set jointly by the
    weakening law and the unloading stiffness. Different $(\mu(s), k_{\text{sys}})$
    pairs give the same arrest. Table 3's *rates* break some of this degeneracy
    and should be used.
- **Dilation angle versus dilation limiter.** The dissipation constraint
    $\tan\psi \le (1-\varepsilon_D)\mu$ means that for SW-S4, with
    $\mu \approx 0.2$–0.46 during slip, the limiter caps $\mathrm{d}g_n^p/\mathrm{d}\gamma$
    well below the *measured* $|d_n|/d_s = 0.547$. **The measured dilation ratio
    exceeds what a purely plastic, dissipation-limited dilation can produce.**
    Some of the measured $d_n$ must therefore be elastic/reversible opening (as
    the data's own unloading recovery, 41→32 μm, independently indicates), or
    matrix deformation leaking into the LVDT reading. This is a genuine physical
    finding, not a modelling failure — but it means $\psi$ is *not* identifiable
    from $|d_n|/d_s$ alone.
- **$V_m$ and $K_{ni}$ appear only as the product $\sigma_0 = V_m K_{ni}$** in
    the closure's shape, plus $V_m$ as the amplitude. With 11 points spanning a
    factor-2 range in $\sigma'_n$, the two are weakly separated and some fits
    sit at their bounds.

#### What is genuinely well constrained

- The **stress path** $(\sigma'_n, \tau)$ — over-determined, checkable, and
    reproduced to four digits by the geometry (Chapter [`sup:thetacheck`](#sup-thetacheck)).
- The **retention contrast across roughness** — four samples spanning
    JRC 1.19–15.32 with retention 1×–5×. This is the paper's headline result and
    the strongest thing to validate against.
- The **stability regime contrast** — burst versus gradual. Binary, unambiguous,
    and hard to fake.
- **SW-S4's slip-weakening curve** — four points on $\mu(d_s)$, measured.
- The **slip and stress-drop rates** — Table 3, three regimes per sample.

A validation that reproduces the stress path, the retention contrast and the
stability regime is a strong validation even if individual apertures carry 10%
error. A validation that matches apertures but produces a burst for SW-S4 is a
weak one. **Weight the scoring accordingly.**

---

### Traps

<a id="sup-traps"></a>

Collected in one place, because each of these has already produced a wrong
answer at least once in this project.

1. **$\theta$ is measured from the core *axis*, not from the horizontal.**
    Getting this backwards swaps $\sigma_n$ and $\tau$.
1. **Compression is positive in Table 2, so dilation is a *negative* $d_n$.**
    ORCA's normal gap is positive in opening. Flip the sign.
1. **$\sigma'_n$ uses $P_p = \tfrac12(P_i+P_o)$, not the local pressure.**
    Report the proxy for comparison.
1. **$k$ is not an independent measurement.** It is $a_h^2/12$ with $a_h$ from
    $Q$. Do not score it as a seventh observable.
1. **$d_n$ and $d_s$ include an unremoved elastic matrix component.** Compare
    against an LVDT-proxy or state the systematic.
1. **$W/L = 0.81$, derived from Table 2, not from geometry.** A geometric $L$
    gives 0.68 and 7% larger apertures.
1. **SW-T2 is 30°, not 31°.**
1. **The doubled sideset.** `construct_side_list_from_node_list = true` runs
    *after* the fault split, and the split copies nodeset membership to both new
    node copies — so the sideset area doubles to ~8.24×10⁻³ m² against the
    correct 4.008×10⁻³, and every side-average on the fracture reports half its
    true value. Convert `top`/`bottom`/`sides` to sidesets explicitly *before*
    the split and leave the blanket flag off. Verify with an
    `AreaPostprocessor` against the $\pi D^2/(4\sin\theta)$ value in
    Chapter [`sup:experiment`](#sup-experiment).
1. **The mechanical gap is not the hydraulic aperture.** SW-S4 retains 78% of
    its dilation and 0% of its conductivity gain. Setting
    `aperture_scale = 1.0` for that sample produces a 43× aperture error.
1. **Flow rate units.** Table 2 is mL/min. 1 mL/min = 1/6×10⁻⁷ m³/s;
    the decks carry `ml_per_m3_per_min = 6.0e7`.
1. **Compare only at hold stages.** The paper's $Q$ is a steady-state value
    measured after ≥100 s of constant pressure. Instantaneous model flux during
    a pressure ramp is not the same quantity.
1. **The five pre-seating cycles mean the joint is not virgin at $t=0$.**

---

### Quick reference

<a id="sup-quickref"></a>

```
GEOMETRY            theta from CORE AXIS; A = pi D^2 / (4 sin theta)
                    SW-T1 32.0deg  SW-T2 30.0deg [not 31]  SW-S3 29.0deg  SW-S4 30.0deg
                    D ~ 50.5 mm; boreholes at r = D/2 - 6 mm, diametrically opposed

STRESS              sigma'_n = (sigma_3 - Pp) + (sigma_1 - sigma_3) sin^2(theta)
                    tau      = (sigma_1 - sigma_3) sin(theta) cos(theta)
                    Pp       = (Pi + Po)/2         Po = 5 MPa,  sigma_3 = 30 MPa (all)
                    check    : tan(theta) = (sigma'_n - sigma_3 + Pp)/tau

DISPLACEMENT        d_n = dz sin(theta) - dx cos(theta)    [NEGATIVE = dilation]
                    d_s = dz cos(theta) + dx sin(theta)
                    both from whole-specimen LVDTs, matrix NOT removed

FLOW                k   = a_h^2 / 12
                    Q   = W a_h^3 dP / (12 mu L)
                    a_h = (12 mu Q / (0.81 dP))^(1/3)      W/L = 0.81 for all four
                    mu  = 1.002e-3 Pa.s;  1 mL/min = 1/6e7 m^3/s

PROTOCOL            Pi: 5 -> 8,12,16,20,24,28 -> 24,20,16,12,8 MPa, 0.03 MPa/s ramps
                    each step 300-500 s; Q read after >=100 s of hold
                    control: CONSTANT PISTON DISPLACEMENT (series spring, not Dirichlet)
                    5 pre-seating cycles to 10-20 MPa differential before the test

BULK                E = 67 GPa, nu = 0.32, UCS = 150 MPa, T = 11 MPa
                    phi_intact = 46 deg  (NOT the joint phi_r)
                    k_matrix = 5e-19 .. 1e-18 m^2,  crystal size ~0.5 mm

INITIAL sigma_1     SW-T1 179.4   SW-T2 202.9   SW-S3 64.7   SW-S4 59.0   MPa  [derived]
FINAL   sigma_1     SW-T1  95.3   SW-T2  93.5   SW-S3 38.4   SW-S4 37.2   MPa  [derived]

MU AT LAST STICK    SW-T1 1.165   SW-T2 1.268   SW-S3 0.609  SW-S4 0.458        [derived]
MU AT ARREST        SW-T1 0.923   SW-T2 0.936   SW-S3 0.233  SW-S4 0.204        [derived]

RETENTION (k)       SW-T1 ~5      SW-T2 ~4      SW-S3 ~2     SW-S4 ~1
RETENTION (a_h inc) SW-T1  71%    SW-T2  75%    SW-S3  48%   SW-S4   0%         [derived]
RETENTION (d_n)     SW-T1  72%    SW-T2  92%    SW-S3  93%   SW-S4  78%         [derived]

SLIP STYLE          T1/T2/S3: burst < 10 s      S4: gradual over 3 pressure steps
SLIP RATE (dyn)     4.9e-5 / 9.8e-5 / 1.1e-5 / 3.2e-7 m/s
```

---

### Bibliographic note

Related work cited by the paper that is worth having to hand when writing the
validation:

- **Barton (1973)** — the JRC concept and the 0–20 range.
- **Yu & Vayssade (1991)** — the $Z_2\!\to\!$ JRC correlation actually used
    (Eq. 2), at a 0.5 mm sampling span.
- **Witherspoon et al. (1980)**, **Zimmerman & Bodvarsson (1996)** — the cubic
    law as applied here.
- **Nemoto et al. (2008)** — the $5\times10^{-5}$ m/s quasi-static/dynamic
    threshold, and the earlier stepwise injection tests on a saw-cut Iidate
    granite fracture.
- **Guglielmi, Cappa, et al. (2015)** — in-situ fault reactivation, slip rates
    $10^{-6}$–$10^{-5}$ m/s at microseismicity onset; the field-scale comparison
    point for Table 3.
- **Bauer et al. (2016)** — cold-water injection into a hot Westerly granite
    saw cut; the closest prior experiment.
- **French et al. (2016)**, **Rutter & Hackston (2017)** — triaxial-injection
    shear on sandstone saw cuts; stress-path and pressurization-rate effects.
- **Zhao et al. (2012)** — asperity failure by abrasion, the mechanism invoked
    for the observed chips.
- **Zhao (1997a, 1997b)** — the joint matching coefficient, ≈1.0 for these
    samples.

The experimental data are stated by the authors to be available through OpenEI
under the University of Oklahoma Reservoir Geomechanics & Seismicity Research
Group. If the raw time series can be obtained, the continuous $d_s(t)$ and
$\sigma_d(t)$ curves would constrain the model far more tightly than the 11
hold-stage points, particularly for the rate-and-state parameters.
