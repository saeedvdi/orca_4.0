# ORCA 4.0 hydromechanical theory and numerical implementation

**Purpose.** This is a personal, implementation-level reference. Part I preserves the complete methodology supplied on 3 September 2026. Part II adds source-audited derivations, weak forms, constitutive updates, regularization, return mapping, finite-stiffness loading, hydraulic coupling, implementation cautions, and verification checks. Equations in Part II use Markdown display-math delimiters so they render in Markdown viewers with MathJax or KaTeX support.

**Authoritative-document rule.** This is the only maintained theory document in the ORCA 4.0 project. It consolidates and supersedes the former class-specific constitutive note, the August 2026 coupled-theory note, the older ORCA CZM manual, the boundary-penalty note, and the fracture-pressure-coefficient note. Where a retired document disagreed with the inspected source, the source-audited formulation in this file was retained.

**Source status.** The implementation notes were checked against the current ORCA 4.0 source tree, including `OrcaPoroMechKernel`, `OrcaFullySaturatedSinglePhaseMassTimeDerivativeKernel`, `OrcaFullySaturatedSinglePhaseDarcyKernel`, `OrcaMechInterfaceKernel`, `OrcaCZMFluidPressureInterfaceKernel`, `OrcaFractureFlowInterfaceKernel`, `ADOrcaBartonBandisContactTractionFastADHardening`, `ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile`, `ADOrcaRoughnessDamageFracturePermeability`, and `OrcaNormalClosure`.

---

## Part I — Complete supplied methodology text

The material below is retained exactly as supplied, including manuscript comments and LaTeX environments.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%% METHODOLOGY %%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

\section{Hydromechanical Model}

The model solves quasi-static Biot poroelasticity in the rock matrix. The fracture is represented as a zero-thickness interface across which the displacement field may be discontinuous. The primary unknowns are the displacement vector \(\boldsymbol u\) and pore pressure \(p\), which are solved monolithically over the whole domain. No separate fracture-pressure unknown is introduced. The implementation uses the MOOSE finite-element framework \cite{Gaston_etal_2009,harbour2025moose}, and forward-mode automatic differentiation provides the Jacobian. The archived model repository maps the equations below to their source objects (Open Research Section).

The notation distinguishes quantities that have related but different meanings. The matrix Biot coefficient is denoted by \(\alpha_B\), whereas the fracture pressure--area coefficient is denoted by \(\chi_f\). The latter represents the fraction of the nominal fracture plane on which fluid pressure acts. The mechanical aperture \(a_m\) is the geometric wall separation obtained from the mechanical solution. The hydraulic aperture \(a_h\) is the equivalent smooth-plate separation that transmits the same flow. Throughout the paper, \(\phi\) denotes porosity, \(\varphi\) denotes a friction angle, \(\boldsymbol{\kappa}\) denotes the matrix permeability tensor, and \(\kappa_f\) denotes scalar fracture permeability.

% these can be used to explain why these samples were used: 
% The four specimens should not be treated simply as repetitions of the same test. The tensile and saw-cut fractures activate different parts of the constitutive model. The surfaces of a tensile fracture are initially well matched because they were created from the same intact rock. Their relatively high roughness produces strong asperity interlocking. When shear slip begins, the surfaces must move over the asperities, producing dilation and a corresponding increase in hydraulic aperture. Slip can also damage the asperities and modify the mechanical and hydraulic response after reactivation.

% The saw-cut specimens are much smoother. Their surfaces were produced mechanically and have substantially lower JRC values. As a result, shear dilation and asperity interlocking are expected to be smaller. These specimens provide a simpler test of normal closure and frictional sliding before the stronger roughness effects observed in the tensile fractures are considered.

% The experimental behavior supports this distinction. SW-T1, SW-T2, and SW-S3 show relatively little shear displacement during the early injection stages followed by a much larger slip increment near the maximum injection pressure. In contrast, SW-S4 begins to slip at a lower injection pressure and accumulates displacement more gradually. SW-S4 therefore provides an important test of whether the model can represent progressive sliding rather than only a sudden slip event.

\subsection{Governing equations}

With \(\boldsymbol\sigma\) the total Cauchy stress tensor (tension positive), \(\boldsymbol\varepsilon=\tfrac12[\nabla\boldsymbol u+(\nabla\boldsymbol u)^{\mathsf T}]\) the infinitesimal strain tensor, and \(\varepsilon_v=\operatorname{tr}\boldsymbol\varepsilon\) the volumetric strain, the matrix is governed by

\begin{linenomath*}
\begin{align}
\nabla\cdot\boldsymbol\sigma+\rho_b\boldsymbol b&=\boldsymbol 0,
\qquad
\boldsymbol\sigma=\mathbb C:\boldsymbol\varepsilon-\alpha_B p\boldsymbol I,
\label{eq:effective-stress}\\
\frac{\dot p}{M}+\alpha_B\dot\varepsilon_v+\nabla\cdot\boldsymbol q&=0,
\qquad
\boldsymbol q=-\frac{1}{\mu_f}\boldsymbol{\kappa}\cdot\left(\nabla p-\rho_f\boldsymbol b\right),
\label{eq:mass-conservation}
\end{align}
\end{linenomath*}

where \(\rho_b\) is the bulk density, \(\boldsymbol b\) is gravitational acceleration, \(\mathbb C\) is the drained isotropic elasticity tensor, \(\boldsymbol{\kappa}\) is the intrinsic permeability tensor, and \(\mu_f\) is the fluid viscosity. An overdot denotes a time derivative. The Biot modulus is \(1/M=(\alpha_B-\phi)/K_s+\phi/K_f\), where \(\phi\) is porosity and \(K_s\) and \(K_f\) are the grain and fluid bulk moduli. The same Biot coefficient \(\alpha_B\) is used in the effective-stress and storage terms, as required by the symmetric poroelastic formulation \cite{Biot1941,ZHAO2020113225,zhang2021poroelastic}. Equation~\eqref{eq:mass-conservation} is written in volumetric form. In the implementation, its storage and flux terms are multiplied by \(\rho_f\) to assemble mass conservation. They are also tagged into an auxiliary residual vector, allowing injected and produced mass fluxes to be recovered from nodal reactions.

The fracture is a surface \(\Gamma\) across which \(\boldsymbol u\) may be discontinuous. The mesh is split along \(\Gamma\) so that coincident node pairs exist on either side, and the displacement jump

\begin{linenomath*}
\begin{equation}
[\![\boldsymbol u]\!]=\boldsymbol u^+-\boldsymbol u^-,
\qquad
\boldsymbol g=\boldsymbol R^{\mathsf T}\cdot[\![\boldsymbol u]\!]=(g_n,g_{t1},g_{t2}),
\end{equation}
\end{linenomath*}

is available pointwise. Here, the rotation tensor \(\boldsymbol R=[\boldsymbol n,\boldsymbol s_1,\boldsymbol s_2]\) defines a local orthonormal frame. Its first column is the interface-normal vector \(\boldsymbol n\), so \(g_n>0\) denotes opening and \(\boldsymbol g_t\) denotes in-plane slip. Sections~\ref{sec:closure}--\ref{sec:dilation} define the constitutive law in this frame and map \(\boldsymbol g\) and the stored state to the local traction vector \(\boldsymbol t^{\mathrm{loc}}\). A zero-thickness interface avoids the poor element aspect ratios that can occur in a thin equivalent-continuum layer. It also allows aperture to remain a direct kinematic quantity rather than an inferred strain \cite{giambanco2012interphase,cerfontaine20153d}.

The interface is coupled back to the bulk in weak form. Rotating the local traction to global coordinates and adding the fluid pressure acting normal to the walls, the interface contributes to the momentum residual of displacement component \(i\) on the two sides,

\begin{linenomath*}
\begin{equation}
R_i^-=-\int_\Gamma N^-t_i\,\mathrm d\Gamma,
\qquad
R_i^+=\int_\Gamma N^+t_i\,\mathrm d\Gamma,
\qquad
\boldsymbol t=\boldsymbol R\cdot\boldsymbol t^{\mathrm{loc}}-\chi_fp_f\boldsymbol n,
\label{eq:interface-residual}
\end{equation}
\end{linenomath*}

where the equal and opposite signs enforce traction equilibrium across \(\Gamma\). Because the mesh is split, the pore pressure has two traces there and the fracture uses their mean, \(p_f=\tfrac12(p^++p^-)\).

Equation~\eqref{eq:interface-residual} avoids double counting fluid pressure. Pressure is added directly to the momentum residual and is not subtracted again inside the constitutive law. The contact law therefore receives the skeleton traction, whose normal component is \(\sigma'_n=\sigma_n-\chi_fp_f\). Accordingly, the additional pore-pressure coefficient available inside the interface law is set to zero in every simulation.

The pressure--area coefficient \(\chi_f\) is constant within each specimen simulation. Its calibrated values are 1.00 for SW-T1 and SW-T2, 0.87 for SW-S3, and 0.86 for SW-S4. The common assumption \(\chi_f=1\) means that pressure acts over the entire nominal fracture area. This remains an approximation because load-bearing contact patches reduce the area exposed to fluid pressure. No attenuation is applied to the tensile fractures, while the reduction for the saw cuts is less than 15\%. A state-dependent alternative is implemented but disabled in all reported simulations because it would represent a different physical model that is not tested here.

\subsection{Unilateral contact and nonlinear normal closure}
\label{sec:closure}

The contact pressure satisfies \(p_c\ge0\), with compression taken as positive. Therefore, \(t_n=-p_c\) and \(p_c\equiv\sigma'_n\) on the interface. Non-interpenetration follows the Signorini conditions \(g_n\ge0\), \(p_c\ge0\), and \(g_np_c=0\). A penalty regularization is used, and the non-smooth point at \(g_n=0\) is smoothed over a width \(\epsilon_g\). This gives Newton's method a continuous tangent during contact and separation.

A constant normal stiffness is inadequate here, because injection sweeps the effective normal stress over a factor of two to four. We use a Bandis-type closure with a stress exponent \cite{Bandis_Lumsden_Barton_1983},

\begin{linenomath*}
\begin{equation}
p_c=K_{ni}V_m\left(\frac{c}{V_m-c}\right)^{1/p_n},
\qquad
c=\left\langle g_n^p-g_n+c_0\right\rangle_{\epsilon_g,+},
\label{eq:normal-closure}
\end{equation}
\end{linenomath*}

where \(V_m\) is the maximum closure, \(K_{ni}\) the initial normal stiffness, \(g_n^p\ge0\) the irreversible normal opening produced by dilation, and \(c_0\) a pre-seating offset representing closure already accumulated at the reference confining stress. Without \(c_0\), applying the 30~MPa confinement at the start of the simulation would drive a closure transient that the compliant loading frame would convert into a spurious axial stress excursion.

Setting \(p_n=1\) recovers the classical Bandis hyperbola. The present simulations use \(p_n>1\) because the tangent stiffness increases as \(p_c^{\,(p_n+1)}\) at high load. Values between 2 and 4 reproduce the threefold to fourfold unloading stiffening required by the measured normal-displacement recovery, which could not be obtained using the classical hyperbola by changing \(K_{ni}\) alone. The calibrated values are \(p_n=4\) for SW-T1, SW-T2, and SW-S3 and \(p_n=2\) for SW-S4.

An unloading-hysteresis branch is active in the reported Barton--Bandis cases and controls the post-slip stress recovery. It retains part of the recovered closure, representing a joint that does not return to its original closure state after slip and re-clamping. The Mohr--Coulomb baseline uses Equation~\eqref{eq:normal-closure} without this branch. Therefore, unloading differences between the two formulations cannot be attributed only to their shear-strength envelopes.

\subsection{Interface elastoplasticity}

\subsubsection{Kinematics and yield}

The tangential response is rate-independent elastoplasticity in the local frame,

\begin{linenomath*}
\begin{equation}
\boldsymbol g_t=\boldsymbol g_t^e+\boldsymbol g_t^p,
\qquad
\boldsymbol t_t=K_t\left(\boldsymbol g_t-\boldsymbol g_t^p\right),
\qquad
s=\int_0^t\lVert\dot{\boldsymbol g}_t^p(\xi)\rVert\,\mathrm d\xi,
\end{equation}
\end{linenomath*}

with \(K_t\) the tangential stiffness and \(s\) the cumulative plastic slip, a single scalar internal variable that drives every history-dependent quantity in the law. Sliding obeys the Kuhn--Tucker conditions

\begin{linenomath*}
\begin{equation}
F=\lVert\boldsymbol t_t\rVert-Y\le0,
\qquad
\Delta\gamma\ge0,
\qquad
F\,\Delta\gamma=0,
\label{eq:yield}
\end{equation}
\end{linenomath*}

where \(Y\) is the shear strength and \(\Delta\gamma\) is the plastic multiplier. Each increment is advanced using the elastic-predictor/plastic-corrector procedure described in Section~\ref{sec:numerics}. Two forms of \(Y\) are compared. Barton--Bandis is the main model, while the linear envelope is used as a baseline to quantify the effect of nonlinear normal-stress dependence.

\subsubsection{Barton--Bandis strength with a slip-weakening cohesion}

The reported simulations use a Barton--Bandis envelope built on the rough-joint form of \citeA{Barton_Choubey_1977},

\begin{linenomath*}
\begin{equation}
\varphi_{\mathrm{BB}}=
\varphi_r+\mathrm{JRC}\log_{10}\left(\frac{\mathrm{JCS}}{p_c}\right),
\end{equation}
\end{linenomath*}

where angles are expressed in degrees, \(\varphi_r\) is the residual friction angle, JRC is the joint roughness coefficient, and JCS is the joint wall compressive strength. The frictional part is concave in \(\sigma'_n\). The mobilized friction angle increases as effective normal stress decreases because asperities are more likely to override than to shear through at low confinement. A single cumulative-slip factor controls peak-to-residual weakening of both friction and cohesion,

\begin{linenomath*}
\begin{align}
W(s)&=\exp\left[-\left(s/D_c\right)^{m_w}\right],
\qquad
\mu_{\mathrm{BB}}(s)=\tan\varphi_{r,w}+\left(\tan\varphi_{\mathrm{BB}}-\tan\varphi_{r,w}\right)W(s),\notag\\
c_{\mathrm{BB}}(s)&=c_{\mathrm{res}}+(c_0^\tau-c_{\mathrm{res}})W(s),
\qquad
Y_{\mathrm{BB}}=c_{\mathrm{BB}}(s)+p_c\,\mu_{\mathrm{BB}}(s),
\label{eq:bb-strength}
\end{align}
\end{linenomath*}

where \(D_c\) and \(m_w\) define the weakening distance and shape, \(\varphi_{r,w}\) is the large-slip friction angle, and \(c_0^\tau\) and \(c_{\mathrm{res}}\) are the peak and residual shear-strength intercepts. A separate roughness state,

\begin{linenomath*}
\begin{equation}
\mathcal R(s)=\mathcal R_{\mathrm{res}}+(\mathcal R_0-\mathcal R_{\mathrm{res}})\exp(-s/D_R),
\label{eq:roughness-state}
\end{equation}
\end{linenomath*}

is used by the hydraulic model of Section~\ref{sec:aperture} and by the baseline envelope, but is not fed back into Equation~\eqref{eq:bb-strength}.

The cohesion term is the only departure from the original Barton law. Barton's roughness contribution approaches zero as \(\sigma'_n\to\mathrm{JCS}\), representing asperities that shear through instead of overriding at high normal stress. However, all terms in the original form remain proportional to \(\sigma'_n\). The strength of rock bridges produced by asperity shear-through does not necessarily scale with confinement and is represented here by cohesion. For the fully mated Mode-I fractures SW-T1 and SW-T2, \(\sigma'_n/\mathrm{JCS}\approx0.4\), and this contribution is important. A purely frictional fit would instead absorb this strength into \(\varphi_r\), leading to values above measured basic friction angles for granite. We therefore include cohesion explicitly and weaken it on the same curve as friction because slip damages the asperities that carry both contributions. Setting \(c_0^\tau=c_{\mathrm{res}}=0\) recovers the original Barton law.

The present loading path provides limited information about the exact envelope shape. Injection reduces \(\sigma'_n\) from 66 to 30~MPa in the rough specimens and from 31 to 15~MPa in the smooth specimens. Across these ranges, parameterizations matched at one stress differ by only about 3\% in \(\mathrm d\tau/\mathrm d\sigma'_n\). JRC, JCS, and \(c\) are therefore not separately identifiable and should be interpreted as one calibrated combination. Section~\ref{sec:envelopes} compares how well the two envelopes reproduce the measured stages under a matched calibration. It does not claim that the experiments uniquely determine the envelope shape.

\subsubsection{The Mohr--Coulomb baseline}

The comparison envelope is linear in normal stress. Friction and cohesion are interpolated between rough and smooth end members through the roughness state in Equation~\eqref{eq:roughness-state}. With \(\bar{\mathcal R}=(\mathcal R-\mathcal R_{\mathrm{res}})/(1-\mathcal R_{\mathrm{res}})\),

\begin{linenomath*}
\begin{equation}
Y_{\mathrm{MC}}=c_{\mathrm{MC}}(\bar{\mathcal R})+\mu(\bar{\mathcal R})\,p_c,
\qquad
\mu(\bar{\mathcal R})=\mu_s+(\mu_r-\mu_s)\bar{\mathcal R}^{m_\mu},
\qquad
c_{\mathrm{MC}}(\bar{\mathcal R})=c_s+(c_r-c_s)\bar{\mathcal R}^{m_c},
\label{eq:mc-strength}
\end{equation}
\end{linenomath*}

where subscripts \(r\) and \(s\) denote rough and smooth end members, not residual and peak values. At fixed \(\mathcal R\), this envelope is linear in normal compression. Equation~\eqref{eq:bb-strength} is curved because its apparent friction angle depends on \(\mathrm{JCS}/p_c\). The baseline is used to evaluate the effect of this nonlinear stress dependence over the range covered by injection. Its cohesive-tension branch, rate-and-state friction, normal-strength memory, and secondary weakening are disabled. The interface therefore begins as a fully damaged pre-existing joint. Throughout this paper, ``Mohr--Coulomb'' refers to Equation~\eqref{eq:mc-strength}, not to a constant-parameter law.

\subsubsection{Flow rule and dilation}
\label{sec:dilation}

The flow rule is non-associative. The tangential direction follows the shear traction, \(\Delta\boldsymbol g_t^p=\Delta\gamma\boldsymbol m\) with \(\boldsymbol m=\boldsymbol t_t/\lVert\boldsymbol t_t\rVert\), while the normal component is governed by a separate dilation angle decaying on its own characteristic distance,

\begin{linenomath*}
\begin{equation}
\Delta g_n^p=\Delta\gamma\tan\psi(s),
\qquad
\psi(s)=\psi_{\mathrm{res}}+(\psi_{\mathrm{peak}}-\psi_{\mathrm{res}})
\exp\left[-\left(s/D_\psi\right)^{m_\psi}\right],
\label{eq:dilation}
\end{equation}
\end{linenomath*}

with \(m_\psi=1\) in the Barton--Bandis runs. A non-associative flow rule is needed because setting \(\psi=\varphi\) would strongly overpredict dilation. For example, the mobilized friction angle for SW-T1 at slip onset is \(49.4^\circ\), whereas the measured displacement ratio implies a dilation angle of \(16.4^\circ\).

Because \(\psi\) is prescribed independently of the friction coefficient, Equation~\eqref{eq:dilation} alone does not guarantee non-negative plastic dissipation. Requiring \(\tau\Delta\gamma-p_c\Delta g_n^p\ge0\) gives the bound \(\tan\psi\le(1-\epsilon_D)\mu\). The Mohr--Coulomb baseline enforces this bound, whereas the Barton--Bandis implementation does not. This is a structural difference between the two implementations. When the bound is active, the friction coefficient controls the realized dilation increment. We therefore report \(\Delta g_n^p/\Delta\gamma\) together with the prescribed \(\psi\).

Dilation can be made to act in two ways. Under a compliant treatment, accumulated dilation reduces the contact stress at fixed jump, so strength falls and slip accelerates while the fracture never visibly opens. Under kinematic routing, which we adopt, \(g_n^p\) enters Equation~\eqref{eq:normal-closure} as a normal eigen-opening, so dilating at fixed jump increases the overlap and the walls must physically separate to relieve it. This is the physical statement --- riding up an asperity separates the walls --- and it is the only form producing a normal displacement jump comparable with the LVDT measurement the experiment reports. Both \(g_n^p\) and \(s\) are history variables and cannot decrease. Kinematic routing also fixes the aperture bookkeeping below: because \(g_n\) already contains the dilation, adding a separate cumulative-dilation term to the hydraulic aperture counts the same mechanism twice.

\subsection{Aperture, transmissivity, and interface flow}
\label{sec:aperture}

Contact patches, tortuosity, and surface roughness make the hydraulic and mechanical apertures different, and their ratio is generally not constant. The hydraulic aperture is represented by the bounded additive relation

\begin{linenomath*}
\begin{equation}
a_h=\operatorname{clamp}\Big[a_{h0}+a_\sigma(\sigma'_n)+\chi_ma_m
+\chi_d\,d_{\mathrm{cum}}\,r_d(\mathcal R)-a_g(s)\,;\,a_{\min},a_{\max}\Big],
\label{eq:hydraulic-aperture}
\end{equation}
\end{linenomath*}

with \(a_m=\max(0,g_n)\). The reference aperture \(a_{h0}\) is back-calculated from the initial measured flow rate. It therefore includes the effects of roughness and tortuosity at the initial stress. Let \(N=\max(0,-t'_n)\) denote compression-positive effective normal traction. The reversible stress-aperture contribution is

\begin{linenomath*}
\begin{equation}
a_\sigma(N)=
\begin{cases}
C_n(N_{\mathrm{ref}}-N), & \text{linear branch},\\[2mm]
\left\langle V_m^h\left[G(N_{\mathrm{ref}})-G(N)\right]\right\rangle_+,
& \text{Barton--Bandis branch},
\end{cases}
\qquad
G(N)=\frac{N^{p_h}}{\sigma_0^{p_h}+N^{p_h}},
\quad \sigma_0=V_m^hK_{ni}^h .
\label{eq:hydraulic-elastic-closure}
\end{equation}
\end{linenomath*}

Here, \(C_n\) is the hydraulic normal compliance, while \(V_m^h\), \(K_{ni}^h\), and \(p_h\) control the bounded nonlinear hydraulic closure. The superscript \(h\) distinguishes these calibrated hydraulic quantities from the parameters in the mechanical contact law. Equation~\eqref{eq:hydraulic-elastic-closure} is single-valued and contains no history variable. It is therefore the elastic fracture-closure term: depressurization increases \(N\), which decreases \(a_\sigma\), and repressurization follows the same path if slip, dilation, roughness, and gouge state do not evolve. The nonlinear term is zero for \(N\ge N_{\mathrm{ref}}\), whereas the linear term can become negative and is limited only through the bound on total aperture in Equation~\eqref{eq:hydraulic-aperture}. The selected models use the nonlinear branch for SW-T2, SW-S3, and SW-S4, and the linear branch for SW-T1.

The term \(\chi_ma_m\) transfers part of the solved mechanical opening to the hydraulic aperture. The optional contribution \(\chi_dd_{\mathrm{cum}}r_d(\mathcal R)\) transfers accumulated shear dilation and is modified by \(r_d(\mathcal R)=r_{\mathrm{res}}+(1-r_{\mathrm{res}})\mathcal R\). Finally, \(a_g(s)\) represents progressive filling by wear products after a slip threshold and helps decouple hydraulic aperture from mechanical opening during unloading. A self-propping term and a closure-creep term are implemented but inactive in all four calibrations. Thus, the time-dependent closure option is not used in the elastic-closure test. The implementation separately outputs \(N\) and \(a_\sigma\), allowing the reversible term to be checked without inferring it from total flow.

The aperture bounds are numerically important because transmissivity scales with \(a_h^3\). A transient mechanical opening before contact is established could otherwise increase permeability by several orders of magnitude and prevent convergence. For SW-S3 and SW-S4, \(a_{\min}\) is set to the reported initial hydraulic aperture, 1.22 and 0.74~\(\mu\)m, respectively. These values are consistent with the measured cycles, in which final permeability does not fall below the initial value. However, this choice also prevents these two calibrated cases from predicting a post-stimulation aperture below the initial state.

The selected configurations use two alternative routes for dilation. For SW-T1 and SW-T2, \texttt{use\_kinematic\_aperture=true} and \(\chi_d=0\); dilation is already included in \(a_m\), and a separate cumulative-dilation contribution would count it twice. For SW-S3 and SW-S4, \texttt{use\_kinematic\_aperture=false}; their hydraulic aperture instead includes the fitted retained-dilation term in Equation~\eqref{eq:hydraulic-aperture}. The fitted dilation scale was reduced during calibration, by about a factor of 17 for SW-S4, to match the measured flow response. Slip-damage loss is disabled for the tensile fractures and enabled for the saw cuts. The maximum losses are 0.40 and 0.28~\(\mu\)m, the onset slips are 30 and 20~\(\mu\)m, and the characteristic slip is 30~\(\mu\)m for SW-S3 and SW-S4, respectively. This term is a calibrated hydraulic contribution rather than an independently validated particle-transport law. Section~\ref{sec:mechanisms} evaluates the aperture contributions separately.

Transmissivity follows the cubic law, and mass conservation between the walls gives a Reynolds equation on the fracture plane,

\begin{linenomath*}
\begin{equation}
T=\frac{a_h^3}{12\mu_f},
\qquad
\kappa_f=\frac{a_h^2}{12},
\qquad
\frac{\partial}{\partial t}\left(\rho_fa_h\right)
+\nabla_t\cdot\left(-\rho_fT\,\nabla_tp_f\right)=0,
\label{eq:reynolds}
\end{equation}
\end{linenomath*}

At each interface quadrature point, Equation~\eqref{eq:reynolds} defines the local intrinsic permeability \(\kappa_f\). The model values reported in the permeability tables and mechanism figures are surface averages, \(\langle\kappa_f\rangle_\Gamma\). By contrast, the experimental permeability and the validation-equivalent flow rate are specimen-scale quantities inferred from the measured discharge. These reductions are closely related but are not identical when aperture is spatially heterogeneous because \(\langle a_h^2\rangle_\Gamma\neq\langle a_h\rangle_\Gamma^2\). We therefore use the directly measured flow rate as the primary hydraulic validation channel and treat hydraulic aperture and permeability as derived consistency measures.

with \(\nabla_t=(\boldsymbol I-\boldsymbol n\otimes\boldsymbol n)\cdot\nabla\). Thus, transport remains in the fracture plane for any interface orientation. The fracture equation is assembled as an interface residual and added to the bulk mass balance on both pressure traces. Fracture storage, in-plane transport, and matrix Darcy flow therefore remain in the same monolithic system. Storage is evaluated directly from the change in \(\rho_fa_h\) between consecutive time steps. This treatment retains both fluid compressibility and the aperture-rate storage generated by dilation. The two pressure traces are tied using the penalty conductance \(C_p=\rho_fT/(a_h\ell_p)\), which is based on the fracture mobility. Because the fracture is only a few micrometers wide, a pressure difference between its two walls would be a discretization artifact. Defining \(C_p\) from \(T\) prevents this tie from limiting transport as the fracture closes.

Because the matrix and the fracture share the field \(p\), leak-off is not a separate term. The normal exchange between them is already carried by the bulk Darcy flux of Equation~\eqref{eq:mass-conservation} evaluated on the two elements adjacent to \(\Gamma\), and a separate leak-off term written on top of a shared field would double-count it. Its size is reported rather than assumed, as the fraction of injected mass not leaving through the outlet port.

We also tested, and do not adopt, the closed form \(a_h\propto a_m^2/\mathrm{JRC}^{2.5}\) \cite{Barton_Bandis_Bakhtar_1985}, which destabilized the coupled solve at the slip--arrest transition in two independent implementations. The obvious explanation is the wrong one: over the range these specimens visit, \(\mathrm d\ln T/\mathrm d\ln a_m\) reaches only 0.74, the aperture clamp never binds, and the ratio of the two transmissivities stays between 1.00 and 1.45. What the substitution does is remove Equation~\eqref{eq:hydraulic-aperture}'s entire negative-feedback stack at once --- the bounded closure, the retention-modulated dilation term, and the gouge reduction disappear together --- leaving the aperture--pressure coupling without a restoring mechanism at the limit point. This is a statement about which feedbacks a two-way coupled solve requires, not a claim that the closed form is wrong at the joint scale to which it was fitted.

Taken together, the equations above form one positive feedback and three opposing effects. Injection raises \(p_f\) and lowers \(\sigma'_n\) through Equation~\eqref{eq:interface-residual}. This reverses part of \(a_\sigma\) and reduces shear strength until slip begins. Slip then dilates the fracture through Equation~\eqref{eq:dilation}. Because \(T\propto a_h^3\), even a modest opening can spread pressure farther along the fracture and reduce \(\sigma'_n\) over a larger area. Without opposing mechanisms, this feedback can become unstable. Three effects limit it. First, the closure law saturates and limits the recovery of \(a_\sigma\). Second, the gouge term reduces \(a_h\) as slip accumulates. Third, the compliant loading frame releases differential stress as the inclined fracture slips, reducing the driving shear stress. The loading-frame effect is strongest in these experiments, but it is a boundary condition rather than a constitutive property. Section~\ref{sec:field-scale} therefore considers carefully which mechanisms may transfer to field conditions.

For completeness: there is no temperature field, and hence no thermally driven aperture change; no chemistry beyond the lumped gouge fill, so no dissolution or pressure-solution kinetics; matrix permeability is constant rather than a function of strain or damage; and the fracture is a fixed surface, so the model cannot propagate, branch, or open a new one. The last is not a limitation for these four experiments, in which the fracture pre-exists and loading is well below the tensile strength of the intact rock, but it bounds what can be claimed at field scale.

\subsection{Numerical implementation}
\label{sec:numerics}

Displacement and pore pressure are solved monolithically using Newton iteration. During each global iteration, a local return map is solved at every interface quadrature point. An elastic predictor first holds the plastic state fixed and calculates a trial traction. If Equation~\eqref{eq:yield} is violated, a plastic corrector returns the traction to the current strength. The residual of a softening law is not always monotonic. Therefore, the local solver brackets the root and uses bisection when a Newton step leaves the bracket. The jump path is also divided at state changes, including contact activation and yield onset, so that one substep does not cross an event without resolving it. If the substep limit is reached, the framework reduces the global time step and repeats the calculation. Adaptive time stepping targets a fixed number of nonlinear iterations per step.

The global Jacobian requires \(\partial\boldsymbol t/\partial[\![\boldsymbol u]\!]\), including the sensitivity of the converged plastic state. Forward-mode automatic differentiation is carried through the local solve. One exact Newton step is then applied at the converged point to include the implicit sensitivities in the tangent. This also includes the sensitivity of \(T\propto a_h^3\) to the displacement jump. Three terms are evaluated explicitly from the converged state at the beginning of the time step and do not contribute to the Jacobian: gouge filling \(a_g(s)\), inactive closure creep, and inactive stress-dependent tangential stiffness. Thus, the tangent is consistent for the active coupled terms, with these three stated exceptions.

Two numerical choices have physical consequences and are reported here. First, the yield residual includes the Perzyna overstress term \(\eta_t\Delta\gamma/\Delta t\) \cite{Perzyna_1966}. It smooths the stick--slip transition and allows the solver to pass the limit point of the softening response. At slip rate \(V\), this term increases the mobilized strength by \(\eta_tV\). The effect is negligible during pre-slip creep but can affect the slip burst. For SW-S4, where \(\eta_t\) is 8.75 times larger than for the other specimens, the mean overstress during the burst is 0.31~MPa compared with a shear strength of about 10~MPa. The overstress approaches zero during the hold stages used for scoring, but it can affect the duration of the transient. It is therefore listed as a calibrated parameter rather than a solver setting. Second, the current formulation does not permit per-step caps on \(\Delta\gamma\) or \(\Delta g_n^p\). In an earlier SW-S4 calibration, the slip cap was active during 14 time steps and contributed about 30\% of accumulated slip. A binding cap changes the constitutive response and does not disappear under time-step refinement in the same way as an explicit viscosity.

\subsection{Numerical setup and parameter determination}

Each specimen is represented as a three-dimensional cylinder with its measured dimensions. A planar elliptical interface follows the experimentally constrained fracture inclination and contains the injection and production nodes. A confining pressure of 30~MPa is applied as a radial traction, and the base is fixed axially. The axial load is applied to the top face through the penalized Dirichlet condition \(t_z=K_{\mathrm{pen}}[u_z-\bar u_z(t)]\). The stiffness \(K_{\mathrm{pen}}\) represents the servo-controlled piston and the compliance of the loading system. It is physically important because the experiment uses constant piston displacement; a rigid condition would suppress the measured stress drop. The injection pressure follows the eleven experimental stages, while the production and initial pore pressures are both 5~MPa.

Parameter classification is part of the validation because a measured input provides a different level of evidence from a calibrated input. Young's modulus, Poisson's ratio, specimen dimensions, confining and production pressures, fluid properties, and reported JRC values are taken directly from the experiment. Fracture orientation, loading-system compliance, the flow geometry factor, the reference hydraulic aperture, and reversible normal compliance are derived from published measurements without adjustment. Several of these quantities are overdetermined; for example, the fracture angle is recovered independently at all eleven hold stages. The axial preload is gated rather than calibrated. It is adjusted so that the pre-slip shear traction matches the stage-1 value, when the fracture remains stuck and the constitutive parameters do not yet control slip. Parameters that cannot be determined independently are calibrated against the experimental response. These include parts of the closure, dilation, weakening, pressure--area, and hydraulic-aperture relations. Effective JRC values that differ from profilometer measurements, including the SW-S4 value, are classified as calibrated transfer parameters. The parameter inventory labels each quantity as measured, derived, assumed, literature-based, or calibrated.

The two comparisons use the same geometry, mesh, loading schedule, bulk properties, pressure coupling, tangential stiffness, viscosity, time-step controls, and specimen-level hydraulic calibration, with the same functional forms and characteristic states wherever the two implementations permit; the Mohr--Coulomb end-member friction and cohesion were transferred to approximate the corresponding Barton--Bandis peak and residual states under an equal calibration budget. The Barton--Bandis unloading-retention branch and the Mohr--Coulomb dissipation limiter remain structural differences and are treated as such in the interpretation.

Agreement is evaluated at the eleven ordered pressure stages reported by \citeA{Ye_Ghassemi_2018}. For an observable \(x\), the range-normalized root-mean-square error is

\begin{linenomath*}
\begin{equation}
\mathrm{nRMSE}_x=\frac{100}{\max(x^{\mathrm{obs}})-\min(x^{\mathrm{obs}})}
\left[\frac{1}{N_x}\sum_{i=1}^{N_x}\left(x_i^{\mathrm{sim}}-x_i^{\mathrm{obs}}\right)^2\right]^{1/2}.
\end{equation}
\end{linenomath*}

Five observables are scored: \(Q\), \(\sigma'_n\), \(\tau\), \(d_n\), and \(d_s\). Hydraulic aperture and permeability are reported but not scored because \(\kappa_f=a_h^2/12\) by definition, while the published \(a_h\) is back-calculated from measured \(Q\) using the cubic law. Scoring all three would therefore count one measurement three times. Displacements are referenced to the first pressure stage, consistent with the tabulated experimental data. Because the first value is then zero by construction, this stage is excluded from the \(d_n\) and \(d_s\) errors. Normal displacement is taken from the global kinematic fracture jump for both formulations rather than from a law-specific opening decomposition. The case-mean nRMSE is the arithmetic mean of the five observables. The study-wide mean is the unweighted average of the five across-specimen means: 3.47\% for Barton--Bandis and 5.60\% for Mohr--Coulomb, corresponding to a 38.1\% reduction before rounding.

\subsection{Numerical verification}

Verification asks whether the equations are solved correctly; validation asks whether they describe the experiment. We keep the two separate.

The bulk operators were checked against closed-form problems. Equations~\eqref{eq:effective-stress}--\eqref{eq:mass-conservation} reproduce one-dimensional Terzaghi consolidation with a maximum pressure error below 0.35\% of the undrained pressure away from the drained boundary and a final-settlement error below 0.02\%. The plane-strain Mandel test reproduces the Mandel--Cryer pressure rise. Its peak centre pressure differs from the analytical series by 0.16\%, and its maximum pressure error is 1.5\% of the undrained pressure. A pressure-diffusion test reproduces the complementary-error-function solution with a maximum error of 0.66\% of the imposed pressure step and shows first-order convergence under combined spatial and temporal refinement. The storage term is checked against the exact response \(p(t)=Mq_vt\) for a constant volumetric source \(q_v\). For the interface, a direct-shear regression test holds the normal load fixed and compares the Barton--Bandis peak strength, friction weakening, and cohesion interpolation in Equation~\eqref{eq:bb-strength} with hand calculations. Model-level verification includes mesh convergence of the pre-slip elastic state and peak slip, global mass balance across the injection and production boundaries, and an independent flow-rate check that uses neither a boundary reaction nor a fitted geometry factor. It also confirms the discretized fracture area, orientation, injection-node placement, and preload gate.

These tests verify the individual algebraic branches and the discretization; they do not constitute independent analytical verification of the complete coupled contact--dilation--aperture--flow system, for which no closed-form solution exists. The four laboratory experiments therefore provide the principal validation of the assembled system, and the distinction between code verification and experimental validation is maintained throughout.

\subsection{Extended-depressurization test of elastic closure}
\label{sec:extended-depressurization}

To test elastic fracture closure separately from further slip damage, we extend the final post-slip pressure history for all four specimens without changing their constitutive parameters. The extensions inherit the relaxed 1-nm aperture-bound controls used for the mechanism tests, so the original calibration floor cannot hide closure. Because the final inlet pressure differs slightly among specimens, the added path is defined by the normalized pressure difference

\begin{linenomath*}
\begin{equation}
\Pi_p=\frac{p_{\mathrm{in}}-p_{\mathrm{out}}}
{p_{\mathrm{in},f}-p_{\mathrm{out}}}.
\label{eq:normalized-pressure-drop}
\end{equation}
\end{linenomath*}

Here, \(p_{\mathrm{in},f}\) is the inlet pressure at the end of the published cycle and \(p_{\mathrm{out}}=5\)~MPa. Each extension first holds \(\Pi_p=1\), then reduces it to 0.50 and 0.15, with a 200-s hold at each level. The corresponding inlet pressures are 8.00, 6.50, and 5.45~MPa for SW-T1 and SW-T2; 7.883, 6.441, and 5.432~MPa for SW-S3; and 7.970, 6.485, and 5.446~MPa for SW-S4. The final pressure difference remains positive in every case, so the test does not reverse the flow direction.

Elastic closure is accepted as the cause of a permeability decrease only when three conditions are satisfied over the added path: effective normal compression increases; \(a_\sigma\), \(a_h\), and \(\kappa_f\) decrease; and cumulative plastic slip, irreversible dilation, roughness, and gouge loss remain numerically unchanged. If any history variable evolves, the response is classified as coupled reactivation or damage rather than purely elastic closure. Reporting the absolute changes together with the fractional permeability loss from \(\Pi_p=1\) allows comparison from the rough tensile fractures to the unpolished and polished saw cuts.

---

# Part II — Source-audited theoretical and implementation supplement

## 1. Reading guide and corrections to the compact methodology

The methodology above is a compact manuscript description. The following distinctions are important when using it as a code reference.

1. ORCA does not differentiate through every iteration of every local nonlinear solver. The Barton--Bandis implementation solves the scalar plastic increment in ordinary floating-point arithmetic and reconstructs its derivative with the implicit-function theorem. The Mohr--Coulomb composite law performs a local AD Newton solve and then applies a final AD corrector to recover the implicit sensitivities. These approaches give a consistent global tangent without carrying a large AD graph through all local iterations.
2. The Barton--Bandis and Mohr--Coulomb updates do not use the same local algorithm. Barton--Bandis uses a bracketed scalar return map in the plastic slip increment, with a nested scalar dilation/contact fixed point. The composite Mohr--Coulomb law solves a coupled two-variable system for plastic slip and irreversible normal opening, with event-aware substepping and line search.
3. `FunctionPenaltyDirichletBC` is used here with a finite physical stiffness. Therefore it represents a Robin spring boundary. It is not being used merely as a very large numerical penalty that approximates an exact Dirichlet condition.
4. The fracture pressure-continuity penalty in `OrcaFractureFlowInterfaceKernel` is a different penalty. It ties the two pressure traces of a hydraulically thin interface. It is numerical and has hydraulic, not mechanical, units.
5. In the source, the Darcy kernel evaluates a quantity with the sign of \((\boldsymbol\kappa/\mu_f)(\nabla p-\rho_f\boldsymbol b)\). This is the negative of the conventional physical Darcy flux. Its positive weak-form contribution is nevertheless consistent with the conventional equation because integration by parts introduces the second minus sign.
6. The gouge-fill and closure-creep terms are read through raw values and therefore do not contribute AD derivatives. The stress-dependent tangential stiffness in the fast Barton--Bandis model, when enabled, is evaluated from the start-of-step normal stress and held constant inside that step.

## 2. Notation and sign conventions

| Symbol | Meaning | Units or convention |
|---|---|---|
| \(\boldsymbol u\) | Matrix displacement | m |
| \(p\) | Pore pressure | Pa |
| \(\boldsymbol\varepsilon=\operatorname{sym}\nabla\boldsymbol u\) | Infinitesimal strain | dimensionless |
| \(\boldsymbol\sigma'\) | Skeleton or effective stress | Pa; tension positive |
| \(\boldsymbol\sigma=\boldsymbol\sigma'-\alpha_Bp\boldsymbol I\) | Total stress | Pa; tension positive |
| \(\alpha_B\) | Matrix Biot coefficient | dimensionless |
| \(\chi_f\) | Fracture pressure--area coefficient | dimensionless |
| \(\boldsymbol\kappa\) | Matrix intrinsic-permeability tensor | m\(^2\) |
| \(\kappa_f=a_h^2/12\) | Scalar fracture intrinsic permeability | m\(^2\) |
| \(T=a_h^3/(12\mu_f)\) | Fracture transmissivity used by ORCA | m\(^3\)/(Pa s) |
| \(\boldsymbol g=\boldsymbol R^{\mathsf T}[\![\boldsymbol u]\!]\) | Local interface displacement jump | m; \(g_n>0\) is opening |
| \(p_c\) or \(N\) | Compression-positive contact pressure | Pa |
| \(t_n=-p_c\) | Local mechanical normal traction | Pa |
| \(\boldsymbol g_t^p\) | Plastic tangential displacement jump | m |
| \(s\) | Cumulative plastic slip | m |
| \(g_n^p\) | Irreversible normal opening from dilation | m; nondecreasing |
| \(\Delta\gamma\) | Incremental plastic-slip magnitude | m |
| \(D\) | Cohesive damage | \(0\) intact, \(1\) fully damaged |
| \(\mathcal R\) | Normalized roughness state | dimensionless |
| \(a_m\), \(a_h\) | Mechanical and hydraulic aperture | m |

The local rotation is

$$
\boldsymbol R=[\boldsymbol n,\boldsymbol s_1,\boldsymbol s_2],
\qquad
\boldsymbol g=\boldsymbol R^{\mathsf T}(\boldsymbol u^+-\boldsymbol u^-).
$$

Thus the first local component is normal and the remaining components are tangential. The traction passed to the mechanical interface kernel is rotated back by \(\boldsymbol t^{\mathrm{glob}}=\boldsymbol R\boldsymbol t^{\mathrm{loc}}\).

## 3. Bulk poromechanics: strong form, weak form, and finite-element residual

### 3.1 Momentum balance

Under quasi-static conditions, the balance of linear momentum is

$$
\nabla\!\cdot\boldsymbol\sigma+\rho_b\boldsymbol b=\boldsymbol 0
\quad\text{in }\Omega,
$$

with

$$
\boldsymbol\sigma
=\boldsymbol\sigma'-\alpha_Bp\boldsymbol I,
\qquad
\boldsymbol\sigma'=\mathbb C:\boldsymbol\varepsilon,
\qquad
\boldsymbol\varepsilon=\frac12(\nabla\boldsymbol u+\nabla\boldsymbol u^{\mathsf T}).
$$

Let \(\boldsymbol w\) be a virtual displacement that vanishes on the essential boundary. Multiplication by \(\boldsymbol w\) and integration give

$$
\int_\Omega \boldsymbol w\cdot(\nabla\!\cdot\boldsymbol\sigma)\,\mathrm d\Omega
+\int_\Omega \rho_b\boldsymbol w\cdot\boldsymbol b\,\mathrm d\Omega=0.
$$

Using

$$
\boldsymbol w\cdot(\nabla\!\cdot\boldsymbol\sigma)
=\nabla\!\cdot(\boldsymbol\sigma^{\mathsf T}\boldsymbol w)
-\nabla\boldsymbol w:\boldsymbol\sigma
$$

and the divergence theorem yields

$$
\int_\Omega \nabla\boldsymbol w:\boldsymbol\sigma\,\mathrm d\Omega
-\int_{\Gamma_t}\boldsymbol w\cdot\bar{\boldsymbol t}\,\mathrm d\Gamma
-\int_\Omega \rho_b\boldsymbol w\cdot\boldsymbol b\,\mathrm d\Omega=0.
$$

Substituting the effective-stress split gives

$$
\int_\Omega \nabla\boldsymbol w:\boldsymbol\sigma'\,\mathrm d\Omega
-\int_\Omega \alpha_Bp\,\nabla\!\cdot\boldsymbol w\,\mathrm d\Omega
-\int_{\Gamma_t}\boldsymbol w\cdot\bar{\boldsymbol t}\,\mathrm d\Gamma
-\int_\Omega \rho_b\boldsymbol w\cdot\boldsymbol b\,\mathrm d\Omega=0.
$$

For component \(i\), shape/test function \(N_a\), and no body-force term inside this particular kernel, `OrcaPoroMechKernel` contributes

$$
R_{a,i}^{\mathrm{bulk}}
=\int_{\Omega_e}\boldsymbol\sigma'_{i\bullet}\cdot\nabla N_a\,\mathrm d\Omega
-\int_{\Omega_e}\alpha_Bp\,\frac{\partial N_a}{\partial x_i}\,\mathrm d\Omega.
$$

The material property named `stress` is the skeleton stress in this split; the kernel adds the \(-\alpha_Bp\boldsymbol I\) term itself. Optional volumetric-locking correction replaces the local volumetric part of the test gradient with its element average. The kernel is restricted to Cartesian coordinates in its current implementation.

### 3.2 Fluid-content equation

For an isothermal saturated porous solid, the increment of fluid content per reference bulk volume is

$$
\zeta=\frac{p}{M}+\alpha_B\varepsilon_v,
\qquad
\varepsilon_v=\operatorname{tr}\boldsymbol\varepsilon.
$$

The Biot modulus satisfies

$$
\frac1M=\frac{\alpha_B-\phi}{K_s}+\frac{\phi}{K_f}.
$$

Volumetric conservation is

$$
\dot\zeta+\nabla\!\cdot\boldsymbol q=q_v,
\qquad
\boldsymbol q=-\frac{\boldsymbol\kappa}{\mu_f}
\left(\nabla p-\rho_f\boldsymbol b\right).
$$

Multiplying by a scalar test function \(w\), integrating, and integrating the divergence term by parts gives

$$
\int_\Omega w\left(\frac{\dot p}{M}+\alpha_B\dot\varepsilon_v\right)\mathrm d\Omega
-\int_\Omega \nabla w\cdot\boldsymbol q\,\mathrm d\Omega
+\int_{\Gamma_q}w\,\bar q_n\,\mathrm d\Gamma
-\int_\Omega wq_v\,\mathrm d\Omega=0.
$$

Substitution of Darcy's law gives the interior residual

$$
R_a^{p}=\int_{\Omega_e}N_a
\left(\frac{\dot p}{M}+\alpha_B\dot\varepsilon_v\right)\mathrm d\Omega
+\int_{\Omega_e}\nabla N_a\cdot
\frac{\boldsymbol\kappa}{\mu_f}
\left(\nabla p-\rho_f\boldsymbol b\right)\mathrm d\Omega.
$$

With `multiply_by_fluid_density = true`, both storage and mobility are multiplied by \(\rho_f\), producing the mass form. The current storage kernel evaluates

$$
R_{a,\mathrm{stor}}^p
=\int_{\Omega_e}N_a\rho_f
\left(\frac{\dot p}{M}+\alpha_B\dot\varepsilon_v-\alpha_T^{\mathrm{eff}}\dot T\right)\mathrm d\Omega,
$$

where the thermal term is present only in TH or THM coupling. `biot_modulus_qp` stores \(M\), not \(1/M\); the implementation therefore divides \(\dot p\) by that property.

The source method called `computeDarcyFlux()` returns

$$
\boldsymbol d=\gamma_f\boldsymbol\kappa\mu_f^{-1}
(\nabla p-\rho_f\boldsymbol b),
\qquad
\gamma_f=1\ \text{or}\ \rho_f,
$$

and assembles \(\int\nabla N_a\cdot\boldsymbol d\). Therefore \(\boldsymbol d=-\boldsymbol q\) in the conventional flux notation. This is a naming/sign detail in the source, not a change in the governing equation.

### 3.3 SUPG helper

The base Darcy-SUPG kernel does **not** add SUPG to the pressure residual. It only provides helper functions for derived advection kernels. For an advective vector \(\boldsymbol a\), the helper uses

$$
\tau_{\mathrm{SUPG}}=
\begin{cases}
\tau_{\mathrm{user}}, & \tau_{\mathrm{user}}\ge0,\\[1mm]
\displaystyle\alpha_{\mathrm{SUPG}}\frac{h_{\min}}{2\lVert\boldsymbol a\rVert+10^{-14}},
& \tau_{\mathrm{user}}<0,
\end{cases}
$$

and returns

$$
R_{a,\mathrm{SUPG}}
=\tau_{\mathrm{SUPG}}
(\boldsymbol a\cdot\nabla N_a)
(\boldsymbol a\cdot\nabla u)\,s_c.
$$

This stabilization is opt-in and should not be claimed for the pressure equation merely because the Darcy-SUPG base class is present.

## 4. Interface mechanics: weak-form derivation

Let the fracture divide the domain into sides \(\Omega^-\) and \(\Omega^+\). Define

$$
[\![\boldsymbol u]\!]=\boldsymbol u^+-\boldsymbol u^-.
$$

The interface internal virtual work is

$$
\delta W_\Gamma
=\int_\Gamma \boldsymbol t\cdot\delta[\![\boldsymbol u]\!]\,\mathrm d\Gamma
=\int_\Gamma \boldsymbol t\cdot\delta\boldsymbol u^+\,\mathrm d\Gamma
-\int_\Gamma \boldsymbol t\cdot\delta\boldsymbol u^-\,\mathrm d\Gamma.
$$

Taking the element side as \(-\) and the neighbor side as \(+\) gives

$$
R_{a,i}^{-}=-\int_\Gamma N_a^-t_i\,\mathrm d\Gamma,
\qquad
R_{a,i}^{+}=+\int_\Gamma N_a^+t_i\,\mathrm d\Gamma.
$$

These are exactly the signs assembled by `OrcaMechInterfaceKernel`. Equal and opposite residuals enforce traction equilibrium and conserve linear momentum across the zero-thickness interface.

The mechanical material supplies \(\boldsymbol t_{\mathrm{mech}}=\boldsymbol R\boldsymbol t^{\mathrm{loc}}\). Fluid pressure is added by a separate interface kernel:

$$
\boldsymbol t_p=-\chi_fp_f\boldsymbol n,
\qquad
\boldsymbol t=\boldsymbol t_{\mathrm{mech}}+\boldsymbol t_p.
$$

With the default `pressure_traction_coefficient = -1`, positive pressure produces compression in the tension-positive traction convention. Keeping pressure in a separate kernel avoids subtracting it twice inside the contact law.

The interface pressure is normally obtained from the two traces as

$$
p_f=\frac12(p^-+p^+).
$$

The distinction between the pressure acting on the fracture walls and pressure affecting frictional strength must be explicit. If the external pressure-traction kernel already supplies \(-\chi_fp_f\boldsymbol n\), an additional internal pore-pressure subtraction should be disabled unless a deliberately different effective-area model is intended.

### 4.1 Effective-area interpretation of the fracture pressure coefficient

The constant \(\chi_f\) used by the pressure-traction kernel has a simple homogenized interpretation. Consider a nominal fracture area \(A\), with a real solid--solid contact area \(A_c\). Let \(S\) be the total compressive force divided by \(A\), \(\sigma_c\) the mean stress carried on the contact patches, and \(p_f\) the fluid pressure acting on the remaining area. Nominal force balance gives

$$
S=\frac{A_c}{A}\sigma_c+left(1-\frac{A_c}{A}\right)p_f.
$$

The solid-borne effective compression per unit nominal area is

$$
N=\frac{A_c}{A}\sigma_c
=S-\left(1-\frac{A_c}{A}\right)p_f.
$$

Comparison with \(N=S-\chi_fp_f\) gives

$$
\boxed{\chi_f=1-\frac{A_c}{A}}.
$$

This identity is exact for the stated effective-area idealization: uniform pressure acts on the non-contact area, pressure does not act inside the solid contact patches, and the scalar area fraction is sufficient to homogenize the traction. It should not be interpreted as a universal microscopic law if contact patches are hydraulically penetrated, spatial pressure is strongly heterogeneous, or contact stress and aperture require a tensorial description.

The limiting cases are

$$
A_c/A=0\Longrightarrow\chi_f=1,
\qquad
A_c/A=1\Longrightarrow\chi_f=0.
$$

Thus, \(\chi_f\simeq1\) is appropriate for an almost fully open fracture, while a well-mated interface with appreciable real contact area has a smaller coefficient. In a frictionally loaded fracture, the exact value \(\chi_f=1\) is an ideal limit because transmitting a finite solid load requires nonzero contact area.

### 4.2 Hardness bound and stress dependence

If the contact-patch stress cannot exceed an indentation hardness \(H\), then

$$
\sigma_c\le H,
\qquad
N=\frac{A_c}{A}\sigma_c,
$$

so that

$$
\frac{A_c}{A}\ge\frac{N}{H},
\qquad
\boxed{\chi_f\le1-\frac{N}{H}}.
$$

The inequality is an upper bound on \(\chi_f\), not a lower bound. Reducing the contact area forces the remaining asperities to carry a larger local stress. At \(N=30\) MPa, illustrative hardness choices give

| Hardness assumption | Minimum \(A_c/A\) | Maximum \(\chi_f\) |
|---:|---:|---:|
| \(H=450\) MPa, approximately three times a 150 MPa UCS | 0.0667 | 0.933 |
| \(H=2\) GPa | 0.0150 | 0.985 |
| \(H=5\) GPa | 0.0060 | 0.994 |

The broad range shows why hardness alone does not determine a unique coefficient. It also shows that a small-load elastic contact estimate can be misleading at the applied granite stresses. If an elastic estimate implies contact stresses above a credible hardness, the asperities yield, the real contact area grows, and the purely elastic contact fraction is no longer admissible.

Because \(A_c/A\) evolves with normal compression, a constant \(\chi_f\) is an effective approximation over the tested path. The expected trend is

$$
N\downarrow\quad\Longrightarrow\quad A_c/A\downarrow
\quad\Longrightarrow\quad\chi_f\uparrow,
$$

although the exact relation depends on roughness, irreversible damage, and the contact law. A possible hardness-limited model is \(\chi_f(N)=1-N/H\) over its admissible range, but it is not the active model in the reported simulations.

### 4.3 Values used in the Ye and Ghassemi validation

| Specimen | \(\chi_f\) | Implied \(A_c/A=1-\chi_f\) | Interpretation |
|---|---:|---:|---|
| SW-T1 | 1.00 | 0 | Standard open-fracture idealization |
| SW-T2 | 1.00 | 0 | Standard open-fracture idealization |
| SW-S3 | 0.87 | 0.13 | Fitted pressure attenuation for a saw cut |
| SW-S4 | 0.86 | 0.14 | Fitted pressure attenuation for the polished saw cut |

The ordering is physically plausible: the tensile fractures are treated as having less real contact area than the better-mated saw cuts. The numerical values were calibrated coupling coefficients rather than measured contact-area fractions. In particular, \(\chi_f=1\) should be described as an idealization, not as proof of exactly zero contact area during frictional loading.

### 4.4 Identifiability and verification

For a compression-positive Coulomb representation,

$$
Y=c+\mu(S-\chi_fp_f).
$$

At one confining stress, a pressure-dependent strength path primarily identifies the intercept \(c+\mu S\) and the product \(\mu\chi_f\). It does not independently identify all three quantities \(c\), \(\mu\), and \(\chi_f\). For example,

$$
0.5774\times0.86\simeq0.4965\times1.00.
$$

These pairs produce essentially the same pressure sensitivity even though their friction and pressure-area coefficients differ. Independent friction/cohesion information or tests at two or more confining stresses are needed to reduce this degeneracy. All four Ye and Ghassemi specimens were tested at 30 MPa confinement, so their pressure cycles alone cannot uniquely separate \(\chi_f\) from friction and cohesion. The saw-cut coefficients must therefore be reported as calibrated timing/coupling parameters.

The effective-area identity has been checked with two ORCA benchmarks. A homogeneous-coefficient problem recovers an imposed \(\chi_f=0.86\) to numerical precision. A resolved alternating-contact problem applies no homogenized coefficient and recovers \(\chi_f=1-A_c/A\) from force balance to approximately eight significant figures. The inputs and gold results are stored in [`Examples/Validaitons/benchmarks/effective_stress_coefficient`](../../../Examples/Validaitons/benchmarks/effective_stress_coefficient). These tests verify the operator and homogenization identity; they do not validate a particular \(\chi_f\) for a natural fracture.

## 5. Finite-stiffness axial boundary

### 5.1 Why a penalty object can represent either Dirichlet enforcement or a spring

Let \(\bar u_z(t)\) be the remote actuator command and \(u_z\) the calculated displacement of the specimen top \(\Gamma_t\). Add the boundary energy

$$
\Pi_{\Gamma_t}
=\frac12\int_{\Gamma_t}k_p(u_z-\bar u_z)^2\,\mathrm d\Gamma.
$$

Its first variation is

$$
\delta\Pi_{\Gamma_t}
=\int_{\Gamma_t}k_p(u_z-\bar u_z)\,\delta u_z\,\mathrm d\Gamma.
$$

With \(\delta u_z=N_i\delta U_i\), the residual and tangent are

$$
R_i^{\Gamma_t}
=\int_{\Gamma_t}N_i k_p(u_z-\bar u_z)\,\mathrm d\Gamma,
$$

$$
J_{ij}^{\Gamma_t}
=\frac{\partial R_i^{\Gamma_t}}{\partial U_j}
=\int_{\Gamma_t}N_i k_pN_j\,\mathrm d\Gamma.
$$

The corresponding traction acting on the specimen is

$$
t_z=k_p(\bar u_z-u_z).
$$

For finite \(k_p\), this is a Robin boundary condition. The difference \(u_z-\bar u_z\) is the spring deformation and is generally nonzero. An exact Dirichlet condition appears only in the limit

$$
k_p\rightarrow\infty
\quad\Longrightarrow\quad
u_z\rightarrow\bar u_z,
$$

provided the discrete problem remains well conditioned. Therefore, the usual MOOSE statement that a penalty must be “large enough” refers to using the class as an approximate Dirichlet condition. In the present model, the finite mismatch is intentional because \(k_p\) represents apparatus compliance.

### 5.2 Conversion from machine stiffness

For a nearly uniform top displacement,

$$
F_z=A k_p(\bar u_z-u_z).
$$

Equivalence with a loading system of total force/displacement stiffness \(K_{\mathrm{sys}}\) requires

$$
k_p=\frac{K_{\mathrm{sys}}}{A}.
$$

The units are

$$
[K_{\mathrm{sys}}]=\mathrm{N/m},
\qquad
[k_p]=\mathrm{N/m^3}=\mathrm{Pa/m}.
$$

The common provisional value used for the protocol-consistency cases is

$$
K_{\mathrm{sys}}=796\ \mathrm{kN/mm}
=7.96\times10^8\ \mathrm{N/m},
$$

which gives \(k_p\simeq3.97\times10^{11}\ \mathrm{Pa/m}\) for the four specimens. This value was reported for the MTS 815 system of Kalantar et al. (2025), not measured for the MTS 816 apparatus used by Ye and Ghassemi (2018). It must therefore be described as a provisional common-stiffness sensitivity assumption.

For a one-dimensional specimen with axial stiffness \(K_s=EA/L\), the loading spring and specimen act in series:

$$
K_{\mathrm{eq}}
=\left(\frac1{K_s}+\frac1{K_p}\right)^{-1},
\qquad K_p=Ak_p.
$$

The fraction of a remote command transmitted to the specimen is

$$
\frac{u_s}{\bar u}
=\frac{K_p}{K_s+K_p}
=\frac{k_p}{E/L+k_p}.
$$

Thus \(k_p\gg E/L\) approximates an exact displacement boundary, whereas \(k_p\sim E/L\) gives intentional load sharing. In the current cases \(k_p\) is comparable to \(E/L\), so the boundary is physically compliant.

### 5.3 Evolution over time

The command follows

$$
\bar u_z(t)=
\begin{cases}
u_0, & 0\le t\le2\ \mathrm{s},\\
u_0+\dfrac{t-2}{53}(u_f-u_0), & 2<t<55\ \mathrm{s},\\
u_f, & t\ge55\ \mathrm{s}.
\end{cases}
$$

At every global Newton iteration, MOOSE evaluates the current command and the current trial top displacement. The boundary force is not prescribed separately; it follows from their difference. During injection \(\bar u_z\) is fixed, but \(u_z\) can change because of poroelastic strain, slip, dilation, closure, and bulk deformation. Consequently, the spring gap and axial stress can relax even under a fixed actuator command.

The direct equilibrium check is

$$
\sigma_{1,\mathrm{spring}}
=k_p\left|\bar u_z-\langle u_z\rangle_{\Gamma_t}\right|
\approx\frac{|F_{z,\mathrm{reaction}}|}{A_{\mathrm{FE}}}.
$$

If nominal circular area is used instead of the meshed top area, the available meshes introduce a known difference of about \(0.285\%\). That is an area-normalization effect rather than a loss of equilibrium.

### 5.4 Numerical penalty versus physical boundary stiffness

`FunctionPenaltyDirichletBC` can be used in two mathematically distinct ways. When it approximates an exact essential condition, introduce the compliance \(\varepsilon_p=1/k_p\). The perturbed boundary is

$$
u_z-\bar u_z=-\varepsilon_p t_z.
$$

The Dirichlet limit requires \(\varepsilon_p\rightarrow0\), or equivalently \(k_p\rightarrow\infty\). A useful normalized enforcement error is

$$
\epsilon_D
=\frac{|u_z-\bar u_z|}{u_{\mathrm{ref}}}
=\frac{|t_z|}{k_pu_{\mathrm{ref}}}.
$$

In a purely numerical penalty method, \(k_p\) is made large enough that \(\epsilon_D\) is acceptable, often using a scaling \(k_p\sim\gamma E_{\mathrm{eff}}/h\). Excessive \(\gamma\) increases the contrast between the boundary and bulk Jacobian blocks and can damage conditioning.

In the ORCA protocol-consistency simulations, \(k_p\) is not chosen to make \(\epsilon_D\) negligible. It is assigned a finite physical value. The resulting displacement difference is apparatus deformation, not a numerical enforcement error. Calling this boundary an exact Dirichlet condition would therefore be incorrect even though the implementing MOOSE object has `DirichletBC` in its class name.

For a one-dimensional specimen,

$$
K_s=\frac{E_{\mathrm{eff}}A}{L},
\qquad
K_p=Ak_p,
$$

and equilibrium gives

$$
\frac{u_z}{\bar u_z}=\frac{K_p}{K_s+K_p},
\qquad
\frac{\bar u_z-u_z}{\bar u_z}=\frac{K_s}{K_s+K_p}.
$$

Using \(E=67\) GPa and the 116-series penalty gives the following explanatory intact-bar estimates:

| Specimen | \(L\) (mm) | \(E/L\) (Pa/m) | \(k_p/(E/L)\) | Estimated \(u_z/\bar u_z\) |
|---|---:|---:|---:|---:|
| SW-T1 | 128.80 | \(5.20\times10^{11}\) | 0.763 | 0.433 |
| SW-T2 | 132.70 | \(5.05\times10^{11}\) | 0.786 | 0.440 |
| SW-S3 | 123.40 | \(5.43\times10^{11}\) | 0.731 | 0.422 |
| SW-S4 | 118.70 | \(5.64\times10^{11}\) | 0.704 | 0.413 |

The estimate ignores the inclined fracture and three-dimensional stress state, but it shows that the boundary spring and specimen have comparable stiffness. The simulations are intentionally compliant rather than nearly Dirichlet.

### 5.5 Inference of the 116-series boundary values

The provisional total system stiffness is

$$
K_{\mathrm{sys}}=796\ \mathrm{kN/mm}=7.96\times10^8\ \mathrm{N/m}.
$$

Kalantar et al. (2025) reported this value for their MTS 815 loading system. Ye and Ghassemi (2018) used an MTS 816 but did not report its stiffness. Therefore, 796 kN/mm is a common-stiffness sensitivity assumption, not a measured property of the Ye and Ghassemi apparatus.

With \(A=\pi R^2\) and \(k_p=K_{\mathrm{sys}}/A\), the generated values are

| Specimen | Radius \(R\) (m) | Area \(A\) (m\(^2\)) | \(k_p\) (Pa/m) |
|---|---:|---:|---:|
| SW-T1 | 0.025260 | 0.0020045485 | \(3.9709691\times10^{11}\) |
| SW-T2 | 0.025260 | 0.0020045485 | \(3.9709691\times10^{11}\) |
| SW-S3 | 0.025265 | 0.0020053421 | \(3.9693975\times10^{11}\) |
| SW-S4 | 0.025255 | 0.0020037550 | \(3.9725416\times10^{11}\) |

The initial command balances the inherited 31 MPa isotropic compressive state:

$$
u_0=-\frac{31\ \mathrm{MPa}}{k_p},
$$

which is approximately \(-0.078\) mm. This is a numerical initialization, not an experimentally reported piston displacement.

Changing \(k_p\) without changing the final actuator command would change the preload. The transformed final command preserves the parent calculation's accepted top displacement \(u_z^{55}\) and spring stress \(\sigma_{1,\mathrm{spring}}^{55}\) at approximately 55 s:

$$
u_f=u_z^{55}-\frac{\sigma_{1,\mathrm{spring}}^{55}}{k_p}.
$$

| Specimen | \(u_z^{55}\) (mm) | \(\sigma_{1,\mathrm{spring}}^{55}\) (MPa) | Transformed \(u_f\) (mm) |
|---|---:|---:|---:|
| SW-T1 | -0.290774 | 181.593 | -0.748076 |
| SW-T2 | -0.339739 | 202.290 | -0.849161 |
| SW-S3 | -0.057849 | 62.868 | -0.216230 |
| SW-S4 | -0.048992 | 59.288 | -0.198236 |

These commands preserve the adopted near-critical numerical preload; they were not inferred directly from the experimental piston records. A preload gate must confirm negligible plastic slip at 55 s, recovery of the intended differential stress, and agreement between the reaction and spring-stress routes.

### 5.6 Newton assembly and boundary postprocessors

During every Newton iteration at \(t_{n+1}\), the command function supplies \(\bar u_z(t_{n+1})\), the current trial solution supplies \(u_z^{(k)}\), and the boundary residual and Jacobian are assembled with those current values. The global update then solves displacement, pressure, and fracture state together. The method does not first impose a displacement and calculate a reaction afterward; both are part of the coupled equilibrium solution.

The 116-series diagnostic chain is

| Postprocessor | Operation | Meaning |
|---|---|---|
| `axial_command_m_pp` | evaluates the command function | \(\bar u_z(t)\), m |
| `top_disp_z_mean_m_pp` | mean `disp_z` on the top | \(\langle u_z\rangle_{\Gamma_t}\), m |
| `machine_spring_gap_m_pp` | top displacement minus command | mean spring deformation, m |
| `machine_spring_sigma1_mpa_pp` | \(k_p|\langle u_z\rangle-\bar u_z|\) | compressive spring stress, MPa |
| `top_reaction_z_raw` | sum of tagged top nodal reactions | signed total reaction, N |
| `top_reaction_z_abs` | absolute reaction | axial force magnitude, N |
| `top_boundary_area_pp` | top-surface integral | meshed area \(A_{\mathrm{FE}}\), m\(^2\) |
| `sigma1_reaction_mpa_pp` | reaction divided by nominal area | reaction-based axial stress, MPa |
| `differential_stress_reaction_mpa_pp` | \(\sigma_1^R-30\) MPa | differential stress, MPa |
| `reaction_vs_machine_spring_mpa_pp` | reaction stress minus spring stress | equilibrium diagnostic, MPa |

`react_disp_z` is filled from the tagged mechanical residual rather than from the spring equation. It therefore provides an independent balance check. For uniform \(k_p\) and command,

$$
F_z^{\mathrm{spring}}
=A_{\mathrm{FE}}k_p
\left(\bar u_z-\langle u_z\rangle_{\Gamma_t}\right).
$$

Dividing the reaction by nominal \(A=\pi R^2\) while averaging the spring traction over \(A_{\mathrm{FE}}\) produces the expected factor \(A_{\mathrm{FE}}/A\simeq0.997147\), or approximately \(-0.2853\%\). An area-consistent check uses \(|F_z^R|/A_{\mathrm{FE}}\).

The row currently written at \(t=0\) contains zeros for these postprocessors because they execute after accepted steps rather than on `INITIAL`. It must not be interpreted as a zero initial command. If an initial diagnostic row is required, request `execute_on = 'INITIAL TIMESTEP_END'` and verify the initialization order.

The boundary directly provides the command, top displacement, spring gap, reaction, axial stress, and differential stress. Effective normal and shear stress on a plane at angle \(\theta\) follow from

$$
\sigma_n'=\sigma_3+q\sin^2\theta-p_f,
\qquad
\tau=q\sin\theta\cos\theta.
$$

Slip, dilation, hydraulic aperture, permeability, and flow come from separate interface and flow postprocessors.

### 5.7 Physical interpretation and limitations

Holding \(\bar u_z\) fixed after preload does not hold the load fixed and does not prevent the specimen from deforming. Slip, closure, dilation, poroelastic strain, or bulk strain changes \(u_z\), which changes the spring gap and reaction. This is how stress relaxation occurs under a fixed remote piston command.

The curved specimen surface is traction-loaded by constant confinement, not fixed radially. It may contract or expand until internal and external forces balance. The bottom axial constraint and minimal lateral pins remove rigid-body modes; they do not make the remaining boundaries rigid.

The finite-stiffness formulation is motivated by apparatus compliance and control mode, not by the LVDT. An LVDT measures displacement but does not impose a mechanical boundary condition. Its reference location matters: if the measured displacement already excludes loading-frame deformation and represents platen-to-specimen motion, assigning it to a remote command while also adding a machine spring may double count compliance.

The model does not explicitly represent platen friction, jacket and seal compliance, controller dynamics, or local nonuniformities. Because the MTS 816 stiffness is unknown, sensitivity to a defensible range of \(K_{\mathrm{sys}}\) should be reported before reinterpreting constitutive parameters.

## 6. Thermodynamic and plasticity foundations

### 6.1 Interface free energy and elastic traction

For the frictional branch, decompose the tangential jump as

$$
\boldsymbol g_t=\boldsymbol g_t^e+\boldsymbol g_t^p.
$$

A simple elastic interface energy per unit area is

$$
\Psi_t=\frac12K_t\boldsymbol g_t^e\cdot\boldsymbol g_t^e,
$$

which gives

$$
\boldsymbol t_t=\frac{\partial\Psi_t}{\partial\boldsymbol g_t^e}
=K_t(\boldsymbol g_t-\boldsymbol g_t^p).
$$

The cumulative plastic slip is

$$
s_{n+1}=s_n+\Delta\gamma,
\qquad
\Delta\gamma=\lVert\Delta\boldsymbol g_t^p\rVert\ge0.
$$

The yield function is

$$
F(\boldsymbol t_t,\boldsymbol z)
=\lVert\boldsymbol t_t\rVert-Y(\boldsymbol z)\le0,
$$

where \(\boldsymbol z\) collects roughness, normal-pressure memory, damage, and other internal variables. Rate-independent plasticity satisfies

$$
\Delta\gamma\ge0,
\qquad
F\le0,
\qquad
\Delta\gamma F=0.
$$

The tangential flow direction is radial:

$$
\boldsymbol m=\frac{\boldsymbol t_t^{\mathrm{tr}}}
{\lVert\boldsymbol t_t^{\mathrm{tr}}\rVert},
\qquad
\Delta\boldsymbol g_t^p=\Delta\gamma\boldsymbol m.
$$

For isotropic tangential stiffness this keeps the updated traction parallel to the trial traction and reduces the tangential vector correction to a scalar plastic increment.

### 6.2 Non-associative dilation and dissipation

The normal plastic opening is governed separately from the friction angle:

$$
\Delta g_n^p=\Delta\gamma\tan\psi(s).
$$

This is non-associative because \(\psi\ne\varphi\) in general. The frictional-dilatant work increment is

$$
\Delta\mathcal D_{fd}
=\underbrace{Y\Delta\gamma}_{\text{frictional work}}
-\underbrace{p_c\Delta g_n^p}_{\text{work required to dilate against compression}}.
$$

Nonnegative dissipation requires

$$
p_c\Delta g_n^p\le Y\Delta\gamma.
$$

The composite Mohr--Coulomb implementation applies the stricter bound

$$
p_c\Delta g_n^p
\le(1-\epsilon_D)D,Y\Delta\gamma,
$$

where \(D\) is the damaged frictional area fraction. The admissible normal increment is therefore

$$
\Delta g_{n,\mathrm{adm}}^p
=\frac{(1-\epsilon_D)D,Y\Delta\gamma}
{p_c+\epsilon_\sigma}.
$$

The actual increment is the smaller of the raw dilation increment and this admissible value. The Barton--Bandis fast implementation caps dilation by available closure and optional absolute increments, but it does not use this energy limiter. This is a structural difference, not merely a parameter difference.

### 6.3 Perzyna-type viscous regularization

The rate-independent consistency equation is regularized by a tangential overstress

$$
\tau_\eta=\eta_t\frac{\Delta\gamma}{\Delta t}.
$$

The plastic consistency equation becomes

$$
F_\eta
=\tau^{\mathrm{tr}}-K_t\Delta\gamma-Y
-\eta_t\frac{\Delta\gamma}{\Delta t}=0.
$$

Because \([\Delta\gamma/\Delta t]=\mathrm{m/s}\), the parameter units are

$$
[\eta_t]=\mathrm{Pa\,s/m}.
$$

The local algorithm sees the effective correction stiffness

$$
K_t^{\mathrm{alg}}=K_t+\frac{\eta_t}{\Delta t}.
$$

This term smooths rapid slip and can improve global convergence at a limit point, but it changes the transient constitutive response. It should be checked by time-step and viscosity sensitivity. In the composite MC law, a local substep uses \(\Delta t_{\mathrm{sub}}=f_{\mathrm{sub}}\Delta t\), not the full global step.

## 7. Unilateral contact and cohesive damage

### 7.1 Smooth positive part

ORCA uses the smooth Macaulay bracket

$$
\langle x\rangle_{\epsilon,+}
=\frac12\left(x+\sqrt{x^2+\epsilon^2}\right),
$$

with derivative

$$
\frac{\mathrm d\langle x\rangle_{\epsilon,+}}{\mathrm dx}
=\frac12\left(1+\frac{x}{\sqrt{x^2+\epsilon^2}}\right).
$$

For large negative \(x\), the implementation evaluates the algebraically equivalent rationalized expression to avoid cancellation. This smoothing gives a continuous contact tangent; it also creates a small transition-zone pressure of order \(K_n\epsilon\), so \(\epsilon\) must be small relative to physical gaps.

### 7.2 Recoverable normal closure

Define the contact overlap

$$
o=g_n^p-g_n+c_0,
\qquad
c=\langle o\rangle_{\epsilon_g,+}.
$$

The linear branch is

$$
p_c=K_nc.
$$

The power-law Barton--Bandis closure branch is

$$
p_c=K_{ni}V_m
\left(\frac{c}{V_m-c}\right)^{1/p_n}.
$$

Its tangent before applying smoothing is

$$
\frac{\partial p_c}{\partial c}
=\frac{K_{ni}V_m^2}{p_n(V_m-c)^2}
\left(\frac{c}{V_m-c}\right)^{1/p_n-1}.
$$

The code caps \(c\) at `maximum_closure_fraction` \(\times V_m\). For \(p_n>1\), the analytical tangent is singular as \(c\to0^+\); ORCA therefore linearly extends the law below

$$
c_{\mathrm{lin}}=\min(10^{-9}\ \mathrm m,0.01V_m)
$$

using the secant stiffness \(p_c(c_{\mathrm{lin}})/c_{\mathrm{lin}}\). The full derivative with respect to overlap is the closure-law tangent multiplied by the derivative of the smooth positive part.

### 7.3 Bilinear mixed-mode cohesive law

When tensile cohesion is enabled, define the regularized opening and equivalent separation

$$
g_n^+=\langle g_n\rangle_{\epsilon_c,+},
\qquad
\delta=\sqrt{(g_n^+)^2+\beta_c^2\lVert\boldsymbol g_t\rVert^2}.
$$

The history variable is irreversible:

$$
\kappa_{n+1}=\max(\kappa_n,\delta_{n+1}).
$$

For peak traction \(T_0\), initiation separation \(\delta_0\), and final separation \(\delta_f\), the damage target is

$$
D_*(\kappa)=
\begin{cases}
0, & \kappa\le\delta_0,\\[1mm]
\displaystyle
\frac{\delta_f(\kappa-\delta_0)}
{\kappa(\delta_f-\delta_0)},
& \delta_0<\kappa<\delta_f,\\[3mm]
1, & \kappa\ge\delta_f.
\end{cases}
$$

The initial cohesive stiffness is

$$
K_c=\frac{T_0}{\delta_0}.
$$

To prevent simultaneous cohesive tension and contact compression after dilation, the cohesive normal traction acts on the opening beyond the plastic contact surface:

$$
t_n^{\mathrm{coh}}
=(1-D)K_c\langle g_n-g_n^p\rangle_{\epsilon_c,+},
$$

while

$$
\boldsymbol t_t^{\mathrm{coh}}
=(1-D)K_c\beta_c^2\boldsymbol g_t.
$$

The fracture energy of the bilinear envelope is

$$
G_c=\frac12T_0\delta_f.
$$

If a Duvaut--Lions relaxation time \(\eta_D\) is specified, the backward-Euler update is

$$
D_{n+1}^{\mathrm{vis}}
=\frac{D_n+(\Delta t_{\mathrm{sub}}/\eta_D)D_*}
{1+\Delta t_{\mathrm{sub}}/\eta_D},
$$

followed by the irreversibility constraint \(D_{n+1}\ge D_n\). Setting \(\eta_D=0\) gives rate-independent damage. For the pre-existing-joint validations, tensile cohesion is disabled and the interface starts with \(D=1\).

## 8. Source-level Mohr--Coulomb composite law

This section documents `ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile`.

### 8.1 Roughness evolution and strength

Within a local substep, roughness evolves from the previous state as

$$
\mathcal R_{n+1}
=\mathcal R_{\mathrm{res}}
+(\mathcal R_n-\mathcal R_{\mathrm{res}})
\exp\left(-\frac{\Delta\gamma}{L_R}\right).
$$

Its local derivative is

$$
\frac{\partial\mathcal R_{n+1}}{\partial\Delta\gamma}
=-\frac{\mathcal R_{n+1}-\mathcal R_{\mathrm{res}}}{L_R}.
$$

Normalize the state as

$$
\bar{\mathcal R}
=\frac{\mathcal R-\mathcal R_{\mathrm{res}}}
{1-\mathcal R_{\mathrm{res}}}.
$$

The friction coefficient and cohesion are

$$
\mu(\mathcal R)
=\mu_s+(\mu_r-\mu_s)\bar{\mathcal R}^{m_\mu},
$$

$$
c(\mathcal R)
=c_s+(c_r-c_s)\bar{\mathcal R}^{m_c}.
$$

Here \(r\) and \(s\) mean rough and smooth end members. They do not mean peak and residual. The raw Coulomb strength is

$$
Y_{\mathrm{raw}}=c(\mathcal R)+\mu(\mathcal R)p_m,
$$

where \(p_m\) is either current contact pressure or an optional decaying pressure memory. A smooth maximum with zero ensures nonnegative strength:

$$
Y=\operatorname{smax}_{\epsilon_\sigma}(Y_{\mathrm{raw}},0).
$$

At fixed roughness, \(Y=c+\mu p_m\) is linear in normal compression. Along a loading history it can nevertheless appear nonlinear because \(\mathcal R\), pressure memory, retained support, or secondary weakening evolves with slip.

An optional secondary weakening subtracts

$$
\Delta Y_{\mathrm{sec}}
=\Delta S\left[1-exp\left(-\frac{\langle s-s_*\rangle_+}{w}\right)\right].
$$

Because it depends on cumulative slip, this loss is irreversible. Negative Coulomb intercepts are allowed as local linearizations of a curved envelope, but the final strength is floored smoothly at zero.

### 8.2 Normal-pressure memory and retained support

If memory is disabled, \(p_m=p_c\). If enabled, the historical pressure decays with incremental opening:

$$
p_{\mathrm{ret}}
=p_{m,n}
\exp\left[
\frac{\ln r_m}{L_m}
\langle g_{n,n+1}-g_{n,n}\rangle_{\epsilon_g,+}
\right],
$$

$$
p_m=\operatorname{smax}_{\epsilon_\sigma}(p_c,p_{\mathrm{ret}}).
$$

Optional retained shear support similarly compares current raw strength with a decaying fraction of historical support. These switches are phenomenological history models; they are not inherent parts of classical Mohr--Coulomb friction.

The material can also export a state-dependent fracture pressure--area coefficient,

$$
\chi_f(p_c)=\frac{\sigma_A}{\sigma_A+p_c}.
$$

The option is activated by the power-law mechanical closure or by the explicit state-dependent switch. The reference stress \(\sigma_A\) is a separate fitted contact-area scale; it is not automatically equal to \(K_{ni}V_m\). A pressure-traction kernel must consume the exported property for this state dependence to affect momentum. **Source-audit warning:** the current `OrcaCZMFluidPressureInterfaceKernel` examined for this document accepts only the constant `pressure_traction_coefficient`; it does not expose the `alpha_property_name` parameter mentioned in comments in the BB header. Unless another kernel or a newer source version consumes `fault_pressure_area_coefficient`, the state-dependent value is diagnostic only. The reported constant-\(\chi_f\) validation cases are unaffected.

### 8.3 Dilation law

The dilation state and angle are

$$
h_\psi(s)=\exp\left[-\left(\frac{s}{L_\psi}\right)^{m_\psi}\right],
$$

$$
\psi(s)=\psi_{\mathrm{res}}
+(\psi_{\mathrm{peak}}-\psi_{\mathrm{res}})h_\psi(s),
\qquad
d_\psi(s)=\tan\psi(s).
$$

Low-pressure support and high-pressure crushing factors are

$$
S_{\mathrm{low}}(p)
=\left(\frac{p}{p+\sigma_{\mathrm{low}}}\right)^{m_{\mathrm{low}}},
$$

$$
S_{\mathrm{high}}(p)
=\left(\frac{\sigma_{\mathrm{high}}}{p+\sigma_{\mathrm{high}}}\right)^{m_{\mathrm{high}}},
\qquad
S(p)=S_{\mathrm{low}}S_{\mathrm{high}}.
$$

A zero reference disables the corresponding factor and sets it to one.

In direct mode, the raw substep increment is

$$
\Delta g_{n,\mathrm{raw}}^p
=D\,d_\psi(s_{n+1})S(p)\Delta\gamma.
$$

In target mode,

$$
g_{n,*}^p
=D\,S(p)d_{\max}
\left[1-\exp\left(-\left(\frac{s}{L_d}\right)^{m_d}\right)\right],
$$

$$
g_{n,n+1}^p
=\operatorname{smax}_{\epsilon_g}(g_{n,n}^p,g_{n,*}^p).
$$

In both modes, the dissipation limiter described above may reduce the raw increment. The final state is clamped exactly so that \(g_{n,n+1}^p\ge g_{n,n}^p\).

### 8.4 Composite traction

The total mechanical traction combines the intact cohesive fraction, unilateral contact, and damaged frictional fraction:

$$
t_n=t_n^{\mathrm{coh}}-p_c,
$$

$$
\boldsymbol t_t
=\boldsymbol t_t^{\mathrm{coh}}
+D K_t(\boldsymbol g_t-\boldsymbol g_t^p).
$$

The external pressure-traction kernel then adds \(-\chi_fp_f\boldsymbol n\) in global coordinates.

### 8.5 Elastic predictor and coupled return map

Holding the old plastic tangential jump fixed gives

$$
\boldsymbol t_t^{\mathrm{tr}}
=K_t(\boldsymbol g_{t,n+1}-\boldsymbol g_{t,n}^p),
\qquad
\tau^{\mathrm{tr}}=\lVert\boldsymbol t_t^{\mathrm{tr}}\rVert.
$$

If the contact is closed and the trial state violates the yield limit, the local unknowns are

$$
\boldsymbol y=
\begin{bmatrix}
\Delta\gamma\\
g_{n,n+1}^p
\end{bmatrix}.
$$

The two residuals are

$$
F_1
=\tau^{\mathrm{tr}}-K_t\Delta\gamma
-Y(\Delta\gamma,g_{n,n+1}^p)
-\eta_t\frac{\Delta\gamma}{\Delta t_{\mathrm{sub}}}
-\tau_{\mathrm{RSF}},
$$

$$
F_2
=g_{n,n+1}^p-g_{n,n}^p
-\Delta g_n^p(\Delta\gamma,g_{n,n+1}^p).
$$

For the paper's baseline configuration, rate-and-state friction is disabled and \(\tau_{\mathrm{RSF}}=0\). The local Newton system is

$$
\begin{bmatrix}
F_{1,\gamma} & F_{1,g_n^p}\\
F_{2,\gamma} & F_{2,g_n^p}
\end{bmatrix}
\begin{bmatrix}
\delta\gamma\\
\delta g_n^p
\end{bmatrix}
=-
\begin{bmatrix}
F_1\\F_2
\end{bmatrix}.
$$

For determinant

$$
\Delta_J
=F_{1,\gamma}F_{2,g_n^p}
-F_{1,g_n^p}F_{2,\gamma},
$$

the explicit Newton corrections are

$$
\delta\gamma
=\frac{-F_1F_{2,g_n^p}+F_{1,g_n^p}F_2}{\Delta_J},
$$

$$
\delta g_n^p
=\frac{-F_{1,\gamma}F_2+F_{2,\gamma}F_1}{\Delta_J}.
$$

The admissible local bounds are

$$
0\le\Delta\gamma\le\frac{\tau^{\mathrm{tr}}}{K_t},
\qquad
g_{n,n+1}^p\ge g_{n,n}^p.
$$

A backtracking line search accepts a step only when the normalized sum of the stress and gap residuals decreases. The determinant is also checked against a stiffness tolerance.

When the optional regularized rate-and-state term is active, the slip rate and direct-effect argument are

$$
V=\frac{\Delta\gamma}{\Delta t_{\mathrm{sub}}},
\qquad
z=\frac{V}{2V_0}
\left(\frac{V_0\theta_n}{D_c^{\mathrm{RSF}}}\right)^{b/a}.
$$

The additive shear-strength perturbation is

$$
\tau_{\mathrm{RSF}}
=p_m a\left[\operatorname{asinh}(z)-\operatorname{asinh}\left(\frac12\right)\right].
$$

The reference subtraction makes the perturbation zero at steady sliding with \(V=V_0\) and \(\theta=D_c^{\mathrm{RSF}}/V_0\). An optional nonnegative clamp suppresses negative perturbations near zero rate. The aging-law state is integrated exactly over a constant-rate substep:

$$
x=\frac{\Delta\gamma}{D_c^{\mathrm{RSF}}},
$$

$$
\theta_{n+1}
=\theta_n e^{-x}
+\Delta t_{\mathrm{sub}}\frac{1-e^{-x}}{x},
$$

with the regular limit \((1-e^{-x})/x\rightarrow1\) as \(x\rightarrow0\).

### 8.6 Consistent tangent through the implicit-function theorem

At convergence,

$$
\boldsymbol F(\boldsymbol y,\boldsymbol x)=\boldsymbol0,
$$

where \(\boldsymbol x\) denotes the global degrees of freedom through the displacement jump and pressure. Differentiation gives

$$
\frac{\partial\boldsymbol F}{\partial\boldsymbol y}
\frac{\mathrm d\boldsymbol y}{\mathrm d\boldsymbol x}
+\frac{\partial\boldsymbol F}{\partial\boldsymbol x}=\boldsymbol0,
$$

and hence

$$
\frac{\mathrm d\boldsymbol y}{\mathrm d\boldsymbol x}
=-\left(\frac{\partial\boldsymbol F}{\partial\boldsymbol y}\right)^{-1}
\frac{\partial\boldsymbol F}{\partial\boldsymbol x}.
$$

The source implements this idea by taking one AD Newton correction at the converged local point. The value residual is already below tolerance, so the correction barely changes the values; its AD derivative supplies the missing \(-\boldsymbol J_{\mathrm{loc}}^{-1}\boldsymbol F_{,x}\) sensitivity. The correction is skipped if its value motion is too large relative to the convergence tolerances.

### 8.7 Event-aware substepping

The code first finds fractions of the displacement-jump path that cross:

- cohesive initiation \(\delta=\delta_0\);
- cohesive completion \(\delta=\delta_f\); and
- contact opening or closing.

It advances each segment independently. If the local solve fails, the segment is recursively bisected. If the maximum depth is reached, the material throws a recoverable exception; MOOSE can then reject the global time step, reduce \(\Delta t\), and retry. This is material substepping within a constitutive evaluation, not the same as global adaptive time stepping.

## 9. Source-level Barton--Bandis fast hardening law

This section documents `ADOrcaBartonBandisContactTractionFastADHardening` and its base class.

### 9.1 Mobilized roughness and nonlinear strength envelope

The effective compression used for strength is bounded below:

$$
p_* = \max(p_{\min},p_c).
$$

If JRC mobilization is enabled,

$$
\mathrm{JRC}_{\mathrm{mob}}
=\mathrm{JRC}
\left[\min\left(1,\max\left(0,\frac{s}{s_{\mathrm{peak}}}\right)\right)\right]^{m_J};
$$

otherwise \(\mathrm{JRC}_{\mathrm{mob}}=\mathrm{JRC}\). The roughness angle is

$$
\theta_R
=\mathrm{JRC}_{\mathrm{mob}}
\log_{10}\left(\frac{\mathrm{JCS}}{p_*}\right).
$$

Unless negative roughness angles are explicitly allowed, \(\theta_R\) is floored at zero. The mobilized peak friction angle is then clamped:

$$
\varphi_p
=\operatorname{clamp}
(\varphi_r+\theta_R,\varphi_{\min},\varphi_{\max}),
\qquad
\mu_p=\tan\varphi_p.
$$

The hardening subclass applies exponential slip weakening:

$$
W(s)=\exp\left[-\left(\frac{s}{D_c}\right)^{m_w}\right],
$$

$$
\mu_{\mathrm{eff}}
=\mu_{r,w}+(\mu_p-\mu_{r,w})W,
$$

$$
c_{\mathrm{eff}}
=c_{\mathrm{res}}+(c-c_{\mathrm{res}})W,
$$

$$
Y_{\mathrm{BB}}
=c_{\mathrm{eff}}+p_c\mu_{\mathrm{eff}}.
$$

An optional `min_tau_limit` places a lower floor on \(Y_{\mathrm{BB}}\). The subclass correctly includes derivatives of both friction weakening and cohesion weakening in its return-map Jacobian.

The exported hydraulic roughness state is independent of the JRC mobilization used in the strength envelope:

$$
\mathcal R(s)
=\mathcal R_{\mathrm{res}}
+(\mathcal R_0-\mathcal R_{\mathrm{res}})
\exp(-s/D_R).
$$

### 9.2 Decoupled dilation

When decoupled dilation is enabled,

$$
\psi(s)
=\psi_{\mathrm{res}}
+(\psi_{\mathrm{peak}}-\psi_{\mathrm{res}})
\exp(-s/D_\psi).
$$

Otherwise, dilation is proportional to the BB roughness angle:

$$
\psi=\operatorname{clamp}(f_d\theta_R,\psi_{\min},\psi_{\max}).
$$

The raw increment is

$$
\Delta d=\tan\psi\,\Delta\gamma.
$$

It may be limited by an absolute maximum dilation increment and by the currently available closure. The closure update has the general coded form

$$
c_{n+1}
=\left\langle c_n+s_d\Delta d\right\rangle_{\epsilon_g,+},
$$

where `dil_closure_sign` supplies \(s_d\). The legacy sign is \(-1\), so dilation reduces closure. Kinematic routing choices must therefore be documented together with this sign.

### 9.3 Scalar return map

The tangential trial traction is

$$
\boldsymbol t_t^{\mathrm{tr}}
=K_t(\boldsymbol g_{t,n+1}-\boldsymbol g_{t,n}^{p}),
\qquad
\tau^{\mathrm{tr}}=\lVert\boldsymbol t_t^{\mathrm{tr}}\rVert.
$$

The scalar residual is

$$
\mathcal R(\Delta\gamma)
=\tau^{\mathrm{tr}}
-\left(K_t+\frac{\eta_t}{\Delta t}\right)\Delta\gamma
-Y_{\mathrm{BB}}(\Delta\gamma)
-Y_{\mathrm{additional}}(\Delta\gamma).
$$

For each trial \(\Delta\gamma\), the code solves a small dilation/contact fixed point because the dilation angle, closure, contact pressure, and BB strength can depend on one another. It then brackets the root over

$$
0\le\Delta\gamma\le
\frac{\tau^{\mathrm{tr}}}{K_t+\eta_t/\Delta t},
$$

further limited by `max_plastic_slip_increment` if that option is active. Safeguarded Newton is used inside the bracket; a Newton step that is invalid or leaves the bracket is replaced by bisection. If the residual remains positive at the upper limit, the code requests a smaller global time step.

Unlike the MC composite law, this BB implementation does not recursively substep the material path. Its robustness comes from the scalar physical bracket, the nested dilation fixed point, and global time-step rejection.

### 9.4 Implicit derivative reconstruction

The scalar consistency equation at convergence is

$$
\mathcal R(\Delta\gamma,\boldsymbol x)=0.
$$

Therefore

$$
\frac{\mathrm d\Delta\gamma}{\mathrm d\boldsymbol x}
=-\frac{\partial\mathcal R/\partial\boldsymbol x}
{\partial\mathcal R/\partial\Delta\gamma}.
$$

The code first solves for the real-valued root. It then evaluates an AD residual at the converged root while treating the root value as temporarily constant and constructs

$$
\Delta\gamma_{\mathrm{AD}}
=\Delta\gamma
-\frac{\mathcal R_{\mathrm{AD}}}
{\left.\partial\mathcal R/\partial\Delta\gamma\right|_{\mathrm{conv}}}.
$$

Because the value of \(\mathcal R\) is nearly zero, this expression preserves the converged value but carries the implicit derivative. The final dilation, normal pressure, plastic jump, and traction are reconstructed using \(\Delta\gamma_{\mathrm{AD}}\).

### 9.5 Optional history and output-only opening

The fast BB family contains optional normal unload retention, reclosure stiffening, residual shear support, and rate-and-state variants. These features are separate from the classical Barton--Bandis envelope and must be listed if active.

The reversible normal-opening diagnostic has the form

$$
d_{\mathrm{rev}}
=a(s)C_n\langle\sigma_{\mathrm{ref}}-p_c\rangle_+,
$$

possibly with a retained maximum-opening fraction. It is evaluated downstream of the constitutive update and is output-only: it does not modify traction, displacement, aperture, permeability, or the Jacobian unless a different hydraulic property explicitly consumes it.

## 10. Regularization and active-set choices

### 10.1 Smooth maximum

A typical smooth maximum used by the MC model is

$$
\operatorname{smax}_\epsilon(a,b)
=\frac12\left(a+b+\sqrt{(a-b)^2+\epsilon^2}\right).
$$

Its weight on \(a\) is

$$
w_a=\frac12\left(1+\frac{a-b}{\sqrt{(a-b)^2+\epsilon^2}}\right),
$$

which is used to differentiate pressure memory, retained support, the strength floor, and the irreversible dilation target.

### 10.2 Semismooth branches

Not every branch is fully smooth. Cohesive initiation and failure, event detection, contact-state classification, dilation limiting, and some final irreversibility clamps use active-set decisions based on raw values. The response is piecewise differentiable or semismooth. Tangent verification must therefore avoid centered finite differences taken exactly at a switching point; use one-sided perturbations or states clearly inside each branch.

### 10.3 Meaning of regularization parameters

| Parameter type | Role | Physical interpretation |
|---|---|---|
| `contact_gap_regularization` | Smooths \(\langle o\rangle_+\) and related gap maxima | Primarily numerical; creates a small transition width in metres |
| `cohesive_gap_regularization` | Smooths cohesive positive opening | Primarily numerical |
| `stress_regularization` | Smooths maxima/floors in strength and memory | Primarily numerical; units Pa |
| `tangential_viscosity` | Adds \(\eta_t\dot\gamma\) | Constitutive regularization with measurable transient effect |
| `cohesive_damage_viscosity` | Relaxes damage toward its target | Constitutive regularization with time scale |
| `max_plastic_slip_increment` | Caps BB slip per global step | A numerical/constitutive limiter; if active it affects the result |
| aperture lower/upper bounds | Prevent nonphysical or ill-conditioned cubic-law values | Physical-numerical model bounds; can affect predictions if active |

A regularization study should demonstrate that numerical smoothing parameters are small enough not to change scored hold values. Viscosity and binding caps should be reported rather than hidden as solver settings.

## 11. Hydraulic aperture and permeability

This section documents `ADOrcaRoughnessDamageFracturePermeability`.

### 11.1 State updates

Negative dilation increments are discarded before accumulation:

$$
d_{\mathrm{cum},n+1}
=d_{\mathrm{cum},n}+\max(0,\Delta d).
$$

The roughness retention factor and self-propping aperture are

$$
r_d(\mathcal R)
=r_{\mathrm{res}}+(1-r_{\mathrm{res}})\mathcal R,
$$

$$
a_{\mathrm{sp}}
=a_{\mathrm{sp},0}\mathcal R^{m_{\mathrm{sp}}}.
$$

### 11.2 Reversible stress-aperture branches

Let

$$
N=\max(0,-t_n')
$$

be compression-positive effective normal traction.

The linear option is

$$
a_\sigma=C_h(N_{\mathrm{ref}}-N).
$$

The bounded BB power option is

$$
a_\sigma
=\left\langle V_m^h[G(N_{\mathrm{ref}})-G(N)]\right\rangle_+,
$$

$$
G(N)=\frac{N^{p_h}}{\sigma_0^{p_h}+N^{p_h}},
\qquad
\sigma_0=V_m^hK_{ni}^h.
$$

The exponential option is

$$
a_\sigma
=A_h\exp\left[-\frac{N-N_{\mathrm{ref}}}{\sigma_c}\right].
$$

These hydraulic closure parameters are independent of the mechanical closure parameters unless a calibration explicitly constrains them to be equal.

### 11.3 Gouge/slip-damage aperture

When enabled,

$$
s_{\mathrm{eff}}=\max(0,s-s_*),
$$

$$
a_g(s)
=a_{g,\max}\left[1-\exp\left(-\frac{s_{\mathrm{eff}}}{D_g}\right)\right].
$$

The source reads cumulative slip through a raw value. This makes \(a_g\) an explicit history contribution with no Jacobian derivative in the current implementation.

### 11.4 Closure creep

The optional creep law is

$$
\dot a_c=r(N)(a_{c,\max}-a_c),
$$

$$
r(N)=\frac1{\tau_c}
\left(\frac{N}{\sigma_{\mathrm{ref}}}\right)^q.
$$

Backward Euler gives

$$
a_{c,n+1}
=\frac{a_{c,n}+r\Delta t\,a_{c,\max}}
{1+r\Delta t}.
$$

This update is monotone and unconditionally stable for \(r\Delta t\ge0\). It freezes when \(N=0\) for \(q>0\). Like gouge filling, it uses the raw normal stress and does not contribute an AD Jacobian term.

### 11.5 Full aperture budget

In non-kinematic mode,

$$
a_h^*
=a_{h0}+a_\sigma
+\chi_ma_m
+\chi_d d_{\mathrm{cum}}r_d(\mathcal R)
+a_{\mathrm{sp}}
-a_g-a_c.
$$

In kinematic mode, dilation is already present in the solved mechanical gap, so the separate \(\chi_dd_{\mathrm{cum}}r_d\) contribution is omitted:

$$
a_h^*
=a_{h0}+a_\sigma+\chi_ma_m+a_{\mathrm{sp}}-a_g-a_c.
$$

Finally,

$$
a_h=\operatorname{clamp}(a_h^*,a_{\min},a_{\max}).
$$

The constitutive outputs are

$$
\kappa_f=\frac{a_h^2}{12},
\qquad
T=\frac{a_h^3}{12\mu_f}.
$$

At initialization the material explicitly sets the old hydraulic aperture to its reference value, including the initial self-propping term. This prevents the first storage update from incorrectly treating the full initial aperture as newly created fluid volume.

## 12. Fracture-flow weak form and pressure-trace tie

### 12.1 Surface conservation

The physical tangential mass flux per unit fracture width is

$$
\boldsymbol j_t=-\rho_fT\nabla_tp_f,
\qquad
\nabla_t=(\boldsymbol I-\boldsymbol n\otimes\boldsymbol n)\nabla.
$$

Surface mass conservation is

$$
\frac{\partial(\rho_fa_h)}{\partial t}
+\nabla_t\!\cdot\boldsymbol j_t=s_\Gamma.
$$

Multiplication by a surface test function \(w\) and tangential integration by parts give

$$
\int_\Gamma w\frac{\partial(\rho_fa_h)}{\partial t}\,\mathrm d\Gamma
+\int_\Gamma\rho_fT\nabla_tp_f\cdot\nabla_tw\,\mathrm d\Gamma
-\int_{\partial\Gamma}w\rho_fT\nabla_tp_f\cdot\boldsymbol\nu_t\,\mathrm d\ell
-\int_\Gamma ws_\Gamma\,\mathrm d\Gamma=0.
$$

The volumetric version omits \(\rho_f\). In `OrcaFractureFlowInterfaceKernel`, the element side carries this surface equation. The mass-form backward difference is

$$
S_f^{m}
=\frac{\rho_f^{n+1}a_h^{n+1}-\rho_f^na_h^n}{\Delta t}.
$$

The volumetric form is

$$
S_f^{v}
=\frac{a_h^{n+1}-a_h^n}{\Delta t}
+C_fa_h^{n+1}\dot p.
$$

The first includes fluid compressibility through density; the second adds it through the user-supplied \(C_f=1/K_f\).

### 12.2 Numerical pressure-continuity penalty

The zero-thickness interface has two pressure traces, but both walls bound the same fluid body. ORCA defines

$$
\kappa_p
=\frac{\gamma_fT}{a_h\ell_p},
\qquad
q_p=\kappa_p(p^- - p^+),
$$

where \(\gamma_f=1\) in volumetric form and \(\rho_f\) in mass form. The residuals are

$$
R_{a}^{-,\Gamma}
=\int_\Gamma N_a^-(S_f+q_p)\,\mathrm d\Gamma
+\int_\Gamma\gamma_fT
\nabla_tp^-\cdot\nabla_tN_a^-\,\mathrm d\Gamma,
$$

$$
R_{a}^{+,\Gamma}
=-\int_\Gamma N_a^+q_p\,\mathrm d\Gamma.
$$

The pressure tie is equal and opposite, so it transfers fluid numerically between traces without creating net mass. The length \(\ell_p\) controls how tightly the pressure traces are tied; smaller values improve continuity but worsen conditioning.

This penalty is not the axial boundary stiffness. The axial penalty has units Pa/m and represents mechanical apparatus stiffness. The pressure penalty has conductance units and represents numerical continuity across a hydraulically thin interface.

### 12.3 Orientation dependence

Only the element side carries surface storage and tangential transport. The neighbor side carries the opposing trace-tie residual. Mesh/interface orientation must therefore remain consistent so that the intended fracture side is always the element side. Reversing the interface changes which trace owns the surface equation even though the physical pressure tie remains conservative.

### 12.4 Matrix-fracture exchange

Because the fracture uses the same pressure unknown as the adjacent matrix and the bulk Darcy operator is assembled in both neighboring elements, normal matrix-fracture exchange is already represented by the bulk flux balance at the interface. An additional empirical leak-off source would double count exchange unless the formulation were changed to use an independent fracture-pressure variable.

### 12.5 Do not confuse the two flow interface kernels

`OrcaFractureFlowInterfaceKernel` carries the fracture's own surface storage and in-plane Reynolds transport, in addition to tying its two pressure traces. By contrast, `OrcaFaultFlowInterfaceKernel` only transfers pressure across the split interface:

$$
q_\perp=\mathcal T_\perp(p^- - p^+),
\qquad
R^-_a=\int_\Gamma N_a^-q_\perp\,\mathrm d\Gamma,
\qquad
R^+_a=-\int_\Gamma N_a^+q_\perp\,\mathrm d\Gamma.
$$

Its transmissibility can be constant, mechanical-aperture cubic, or constructed from a permeability property divided by viscosity and a fault thickness. This object is a cross-interface transfer law; it is not the same equation as tangential fracture-plane flow. Documentation and input audits must name which one is active.

## 13. Monolithic nonlinear solution

At global time step \(n+1\), the unknown vector is

$$
\boldsymbol X=
\begin{bmatrix}
\boldsymbol U\\ \boldsymbol P
\end{bmatrix}.
$$

The assembled residual is

$$
\boldsymbol R(\boldsymbol X)=
\begin{bmatrix}
\boldsymbol R_u^{\mathrm{bulk}}
+\boldsymbol R_u^{\Gamma,\mathrm{mech}}
+\boldsymbol R_u^{\Gamma,p}
+\boldsymbol R_u^{\mathrm{BC}}\\[1mm]
\boldsymbol R_p^{\mathrm{storage}}
+\boldsymbol R_p^{\mathrm{Darcy}}
+\boldsymbol R_p^{\Gamma,\mathrm{flow}}
+\boldsymbol R_p^{\mathrm{BC}}
\end{bmatrix}
=\boldsymbol0.
$$

Newton's method solves

$$
\boldsymbol J^{(k)}\Delta\boldsymbol X^{(k)}
=-\boldsymbol R^{(k)},
\qquad
\boldsymbol X^{(k+1)}
=\boldsymbol X^{(k)}+\lambda\Delta\boldsymbol X^{(k)},
$$

where

$$
\boldsymbol J=
\begin{bmatrix}
\partial\boldsymbol R_u/\partial\boldsymbol U &
\partial\boldsymbol R_u/\partial\boldsymbol P\\
\partial\boldsymbol R_p/\partial\boldsymbol U &
\partial\boldsymbol R_p/\partial\boldsymbol P
\end{bmatrix}.
$$

The off-diagonal terms include pressure traction and Biot coupling in the upper-right block, and strain-rate storage plus aperture-dependent fracture storage/transmissivity in the lower-left block. This is the sense in which the model is monolithic: mechanics and flow are not advanced as independent staggered solves.

The quadrature-point sequence for a typical nonlinear iteration is:

1. evaluate bulk strain, skeleton stress, Biot properties, density, viscosity, and mobility;
2. calculate interface jump and local rotation;
3. update cohesive damage, contact state, plastic slip, dilation, roughness, and traction;
4. calculate mechanical aperture and hydraulic aperture;
5. calculate \(\kappa_f\), \(T\), and fracture storage;
6. assemble bulk momentum and mass residuals;
7. assemble mechanical traction, pressure traction, fracture flow, and pressure-trace tie;
8. assemble the finite-stiffness axial boundary;
9. solve the global Newton correction;
10. accept and commit state only after nonlinear convergence.

## 14. Algorithm pseudocode

### 14.1 MC composite law

```text
for each interface quadrature point:
    read old state and current displacement-jump path
    locate cohesive/contact events on the path
    for each event-delimited segment:
        update cohesive history and damage
        determine open/closed contact state
        if open or frictional area is zero:
            assemble cohesive traction and smooth contact pressure
            carry plastic history
        else:
            form tangential trial traction
            evaluate yield residual at Delta_gamma = 0
            if admissible:
                stick; carry plastic tangential jump
            else:
                solve F1(Delta_gamma, g_n^p) = 0
                      F2(Delta_gamma, g_n^p) = 0
                using bounded Newton + backtracking
                apply one AD implicit-derivative corrector
                enforce exact normal-opening irreversibility
                update plastic jump, slip, roughness, dilation, work, and traction
        if local update fails:
            bisect the segment and retry
    return traction increment and state properties
```

### 14.2 BB fast hardening law

```text
for each interface quadrature point:
    read old plastic jump, slip, dilation, and unloading state
    evaluate start-of-step closure and contact pressure
    compute current tangential stiffness
    form tangential trial traction
    if trial traction is admissible:
        stick and carry/update auxiliary state
    else:
        bracket Delta_gamma in its physical interval
        for each scalar residual evaluation:
            solve dilation/contact fixed point
            evaluate BB strength and derivative
        solve scalar residual by safeguarded Newton/bisection
        reconstruct Delta_gamma_AD with the implicit-function theorem
        reconstruct final dilation, normal pressure, plastic jump, and traction
    return traction increment and diagnostics
```

## 15. Postprocessors and direct validation quantities

The finite-stiffness boundary postprocessors establish:

- commanded actuator displacement \(\bar u_z\);
- mean calculated top displacement \(\langle u_z\rangle\);
- spring gap \(\langle u_z\rangle-\bar u_z\);
- spring-derived axial stress;
- summed top reaction and reaction-derived axial stress;
- differential stress after combining the axial and confining stresses.

They do not directly establish fracture slip, normal displacement, aperture, permeability, or flow. Those require interface material properties, side averages, nodal jump reconstructions, or hydraulic boundary reactions.

The most important direct internal checks are

$$
\frac{|F_{z,\mathrm{reaction}}|}{A_{\mathrm{FE}}}
\approx
k_p\left|\bar u_z-\langle u_z\rangle\right|,
$$

$$
\kappa_f\stackrel{?}=\frac{a_h^2}{12},
\qquad
T\stackrel{?}=\frac{a_h^3}{12\mu_f},
$$

and the global mass balance

$$
M_{\mathrm{in}}-M_{\mathrm{out}}
-\Delta M_{\mathrm{matrix}}
-\Delta M_{\mathrm{fracture}}
\approx0.
$$

For elastic-closure interpretation, verify simultaneously that normal compression increases, \(a_\sigma\), \(a_h\), and \(\kappa_f\) decrease, and all irreversible variables remain constant.

## 16. Verification hierarchy

### 16.1 Unit and constitutive tests

- smooth-positive value and derivative on open, transition, and closed branches;
- normal closure pressure and analytical tangent, including linearization and closure cap;
- MC strength interpolation and its roughness derivatives;
- BB strength, JRC mobilization, slip weakening, and cohesion weakening;
- scalar BB return-map residual and implicit derivative;
- two-equation MC return map and finite-difference tangent away from active-set switches;
- cohesive bilinear envelope, damage irreversibility, and \(G_c=T_0\delta_f/2\);
- nonnegative frictional-dilatant dissipation;
- aperture-budget identity and cubic-law identities.

### 16.2 Operator tests

- one-dimensional storage test \(p(t)=Mq_vt\);
- pressure diffusion and Terzaghi consolidation;
- Mandel--Cryer response for coupled HM behavior;
- interface traction action/reaction balance;
- pressure traction sign test;
- fracture-flow tangential projection on a rotated plane;
- pressure-trace continuity and conservation;
- finite-stiffness boundary reaction identity.

### 16.3 Model-level convergence and sensitivity

- spatial mesh refinement;
- global time-step refinement through the slip event;
- local substep-depth sensitivity for the MC model;
- viscosity sensitivity for \(\eta_t\) and \(\eta_D\);
- gap/stress smoothing sensitivity;
- apparatus stiffness sensitivity;
- confirmation that aperture bounds and per-step caps are inactive, or explicit reporting when they are active.

## 17. Common implementation and interpretation pitfalls

1. **Double-counting pressure.** Do not add \(-\chi_fp_f\boldsymbol n\) externally and subtract the same pressure again in the strength law unless two distinct effective-area mechanisms are intended.
2. **Double-counting dilation in aperture.** If dilation changes the solved mechanical gap, do not also add full cumulative dilation to \(a_h\).
3. **Calling the finite spring an exact Dirichlet boundary.** A finite \(k_p\sim E/L\) permits a substantial command/specimen mismatch by design.
4. **Confusing the two penalties.** Axial stiffness and pressure-trace conductance solve different equations and have different units.
5. **Treating MC as always globally linear.** It is linear in normal compression at fixed state, but state evolution makes the path-dependent response nonlinear.
6. **Calling viscosity a neutral solver setting.** \(\eta_t\Delta\gamma/\Delta t\) changes transient strength and must be reported.
7. **Assuming all AD properties carry full history derivatives.** Gouge fill and closure creep currently use raw-value updates; the BB stress-dependent \(K_t\) is lagged within a step.
8. **Finite differences at kinks.** Active-set switches are semismooth; test inside branches or use one-sided derivatives.
9. **Ignoring element/neighbor orientation.** The fracture-flow surface equation is owned by the element side.
10. **Scoring dependent hydraulic observables as independent data.** If aperture and permeability were inferred from the same measured flow using the cubic law, scoring \(Q\), \(a_h\), and \(\kappa_f\) separately overweights one measurement.

## 18. Source-to-equation map

| Implementation object | Mathematical responsibility |
|---|---|
| `OrcaPoroMechKernel` | Skeleton-stress divergence and \(-\alpha_Bp\boldsymbol I\) contribution to momentum |
| `OrcaFullySaturatedSinglePhaseMassTimeDerivativeKernel` | \(\dot p/M+\alpha_B\dot\varepsilon_v-\alpha_T^{\mathrm{eff}}\dot T\), optionally multiplied by density |
| `OrcaFullySaturatedSinglePhaseDarcyKernel` | Weak Darcy diffusion/gravity term |
| `OrcaFullySaturatedSinglePhaseDarcySUPGKernel` | Darcy term plus optional SUPG helper routines for derived kernels |
| `OrcaMechInterfaceKernel` | Equal-and-opposite mechanical interface traction residual |
| `OrcaCZMFluidPressureInterfaceKernel` | Fracture pressure acting as normal traction |
| `OrcaFractureFlowInterfaceKernel` | Surface storage, tangential Reynolds flow, and pressure-trace tie |
| `OrcaFaultFlowInterfaceKernel` | Equal-and-opposite cross-interface pressure transfer; no in-plane storage/transport |
| `OrcaFaultPressureInterfaceKernel` | Constant-coefficient pressure traction coupled directly to the pressure traces |
| `OrcaCZMInterfacePressure` | Arithmetic mean \(p_f=(p^-+p^+)/2\) exported as an AD interface property |
| `OrcaNormalClosure` | Shared linear or power-law unilateral normal response and tangent |
| `ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile` | Cohesion/contact/friction mixture, MC strength, dilation, return map, local substepping |
| `ADOrcaBartonBandisContactTractionFastAD` | Nonlinear BB contact/friction, scalar return map, IFT tangent |
| `ADOrcaBartonBandisContactTractionFastADHardening` | BB slip weakening of friction/cohesion and exported roughness degradation |
| `ADOrcaRoughnessDamageFracturePermeability` | Aperture budget, gouge, creep, permeability, and transmissivity |
| `FunctionPenaltyDirichletBC` | Finite-stiffness actuator/spring boundary when \(k_p=K_{\mathrm{sys}}/A\) |

## 19. Final compact statement of the coupled model

The complete model can be summarized as

$$
\boxed{
\begin{aligned}
&\nabla\!\cdot(\mathbb C:\boldsymbol\varepsilon-\alpha_Bp\boldsymbol I)
+\rho_b\boldsymbol b=\boldsymbol0,\\
&\frac{\dot p}{M}+\alpha_B\dot\varepsilon_v+\nabla\!\cdot\boldsymbol q=0,
\qquad
\boldsymbol q=-\frac{\boldsymbol\kappa}{\mu_f}(\nabla p-\rho_f\boldsymbol b),\\
&\boldsymbol g=\boldsymbol R^{\mathsf T}[\![\boldsymbol u]\!],
\qquad
\boldsymbol t=\boldsymbol R\boldsymbol t^{\mathrm{loc}}-\chi_fp_f\boldsymbol n,\\
&F=\lVert\boldsymbol t_t\rVert-Y\le0,
\qquad
\Delta\gamma\ge0,
\qquad
F\Delta\gamma=0,\\
&\Delta\boldsymbol g_t^p=\Delta\gamma\boldsymbol m,
\qquad
\Delta g_n^p=\mathcal G(\Delta\gamma,p_c,s,D),\\
&a_h=\operatorname{clamp}\!\left[
a_{h0}+a_\sigma+\chi_ma_m+a_d+a_{\mathrm{sp}}-a_g-a_c;
a_{\min},a_{\max}\right],\\
&\kappa_f=\frac{a_h^2}{12},
\qquad
T=\frac{a_h^3}{12\mu_f},
\qquad
\partial_t(\rho_fa_h)-\nabla_t\!\cdot(\rho_fT\nabla_tp_f)=0,\\
&t_z=k_p(\bar u_z-u_z),
\qquad
k_p=K_{\mathrm{sys}}/A.
\end{aligned}}
$$

The constitutive distinction is concentrated in \(Y\) and the local history update. The Barton--Bandis envelope is nonlinear in normal stress because its mobilized angle contains \(\log_{10}(\mathrm{JCS}/p_c)\). The comparison Mohr--Coulomb envelope is linear in normal stress at fixed roughness but evolves through roughness degradation, dilation, and any optional memory terms. Both models are embedded in the same monolithic bulk-flow/interface-flow system and are subject to the same finite-stiffness loading boundary.

## 20. Mesh construction and constitutive-law inventory

### 20.1 Why ORCA uses a zero-thickness interface

For a known, pre-existing, non-propagating fracture, a split zero-thickness interface has two advantages over a smeared band: the displacement jump is an explicit kinematic quantity, and contact/sliding laws do not depend on an assumed band thickness. XFEM or embedded-discontinuity methods are more suitable when the fracture path must propagate through elements, but they add enrichment and contact complexity that is unnecessary for the present laboratory geometry.

`OrcaFaultInterface3DGenerator` converts a conforming internal surface into two coincident but topologically independent faces. Its essential operations are:

1. build the active node-to-element connectivity;
2. resolve the requested nodeset or sideset as element faces;
3. duplicate only interior interface nodes, leaving true crack-front nodes welded;
4. optionally exclude non-manifold junction nodes;
5. copy nodeset memberships to each duplicate, which is essential when both fracture walls meet a prescribed pressure boundary;
6. re-point all elements on one consistently selected side to the duplicate nodes; and
7. retain the primary sideset and optionally create a secondary sideset.

The two surfaces remain geometrically coincident at initialization. Separation is created by the solved displacement jump, not by inserting an artificial initial thickness.

The local frame is built from the reference interface normal. This is consistent with the small-strain formulation. A finite-rotation formulation would need the rotation to evolve with deformation.

### 20.2 Source-tree map

| Directory | Main responsibility |
|---|---|
| `src/kernels/` | Bulk momentum, storage, volumetric coupling, and Darcy residuals |
| `src/interfacekernels/` | Mechanical traction, pressure traction, in-plane fracture flow, and cross-interface transfer |
| `src/InterfaceMaterial/` | Interface kinematics, constitutive laws, aperture/permeability, and scalar helpers |
| `src/materials/` | Bulk elasticity, hydromechanical properties, and Biot quantities |
| `src/meshgenerators/` | Split-interface construction |
| `include/utils/` | Shared closed-form utilities such as `OrcaNormalClosure` |
| `test/tests/` | Regression and verification suite |

### 20.3 Registered interface-model families

| Family | Representative class | Purpose |
|---|---|---|
| A | `ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile` | Transparent roughness-evolving Mohr--Coulomb baseline with cohesive/contact mixture and explicit dissipation control |
| B | `ADOrcaBartonBandisContactTractionFastADHardening` | Production Barton--Bandis strength, nonlinear closure, slip weakening, and decoupled dilation |
| C | `ADOrcaBartonBandisFlowRSFContactTraction` | BB envelope with mobilized roughness, shelf-like history, and rate-and-state effects |
| D | `ADOrcaPeakShelfTailFlowRSFContactTraction` | Phenomenological peak--shelf--tail friction history with rate-and-state effects |

Additional registered variants include `ADOrcaBartonBandisRateStateHardening`, cohesionless damage-based MC and BB/RSF laws, the non-tensile decoupled-dilation law, the literal Barton--Bandis--Bakhtar permeability law, and a hysteretic permeability material. Utility materials include `OrcaCZMMohrCoulombFriction`, `OrcaCZMCubicLawAperture`, `OrcaCZMStressDependentAperture`, `ADOrcaCZMComputeMechanicalAperture`, and `OrcaCZMInterfacePressure`.

Model C adds staircase JRC mobilization, optional apparent cohesion and late friction increments, slip-dependent viscosity, and a guarded rate-and-state contribution. Model D replaces the derived envelope by

$$
\mu(s):\quad\mu_{\mathrm{peak}}
\longrightarrow\mu_{\mathrm{shelf}}
\longrightarrow\mu_{\mathrm{tail}},
$$

with separately controlled transitions. These models are intended for timing or multi-stage histories that Models A and B cannot represent. They should not be introduced as undocumented calibration alternatives. In the inspected source, their direct-effect RSF parameter must be strictly positive, so an arbitrarily small value can approximate, but not exactly reproduce, a rate-independent law.

## 21. Consolidated parameter and material-property reference

### 21.1 Core contact and normal-closure inputs

Defaults are source defaults, not recommended calibration values.

| Input | Default | Units | Role |
|---|---:|---|---|
| `penalty_tangent` | 0 | Pa/m | Tangential elastic stiffness; zero falls back to the initial normal stiffness |
| `tangential_traction_tolerance` | \(10^{-16}\) | Pa | Direction/branch safeguard near zero shear traction |
| `max_return_mapping_iterations` | 50 | -- | Safeguarded local scalar iterations |
| `relative_tolerance` | \(10^{-8}\) | -- | Relative local return-map tolerance |
| `contact_gap_regularization` | 0 | m | Smooth positive-part length; zero gives a hard active set |
| `tangential_viscosity` | 0 | Pa s/m | Perzyna-type tangential overstress |
| `initial_normal_stiffness` | \(10^{13}\) | Pa/m | \(K_{ni}\) in the nonlinear closure law |
| `maximum_closure` | \(10^{-4}\) | m | \(V_m\) |
| `maximum_closure_fraction` | 0.999 | -- | Numerical bound before the closure singularity |
| `normal_closure_stress_exponent` | 1 | -- | Generalized closure exponent |
| `normal_closure_offset` | 0 | m | Pre-seating closure |
| `normal_unload_retention_fraction` | 0 | -- | Retained recovered closure |
| `normal_reclosure_stiffness_multiplier` | 1 | -- | Reclosure slope multiplier |

The older names `return_mapping_iterations`, `normal_traction_tolerance`, and hard per-step slip/dilation caps should not be used as constitutive calibration controls. A cap that binds makes the response depend directly on time step and cap size. Prefer time-step refinement, local substepping, or explicitly reported viscosity.

### 21.2 BB strength, dilation, and roughness inputs

| Input | Default | Units | Role |
|---|---:|---|---|
| `jrc` | 10 | -- | Laboratory JRC |
| `jcs` | \(10^8\) | Pa | Laboratory JCS |
| `residual_friction_angle_degrees` | 30 | degrees | Basic/residual friction angle |
| `cohesion` | 0 | Pa | Shear intercept, not tensile cohesion |
| `use_scale_correction` | true | -- | Length correction of JRC/JCS |
| `laboratory_length`, `joint_length` | 0.1, 0.1 | m | Reference and modeled joint lengths |
| `compressive_normal_stress_floor` | \(10^3\) | Pa | Logarithm guard |
| `pore_pressure_strength_coefficient` | 0 | -- | Optional internal strength-pressure route; keep zero when pressure traction is external |
| `min_friction_angle_degrees`, `max_friction_angle_degrees` | 0, 85 | degrees | Angle bounds |
| `peak_shear_displacement` | \(10^{-3}\) | m | Full JRC-mobilization distance |
| `dilation_factor` | 0.5 | -- | Legacy BB dilation multiplier |
| `dilation_angle_peak_degrees` | 1.5 | degrees | Decoupled peak angle |
| `dilation_angle_residual_degrees` | 0.3 | degrees | Decoupled residual angle |
| `dilation_decay_distance` | \(10^{-4}\) | m | Dilation decay length |
| `characteristic_slip_distance` | \(10^{-3}\) | m | Slip-weakening distance \(D_c\) |
| `residual_cohesion` | 0 | Pa | Large-slip shear intercept |
| `roughness_characteristic_slip` | \(10^{-3}\) | m | Hydraulic roughness-decay distance |
| `roughness_state_initial`, `roughness_state_residual` | 1, 0 | -- | Roughness end states |

Model A also provides optional history and dilation-support families. They are inactive in the paper baseline but belong to the general constitutive definition:

| Input family | Mathematical effect |
|---|---|
| `normal_strength_retention_factor`, `normal_strength_memory_decay_distance` | retains a decaying historical normal compression during opening |
| `retained_shear_support_factor`, retained-support decay distance | supplies a decaying lower bound based on historical shear resistance |
| `secondary_weakening_strength`, `secondary_weakening_onset_slip`, `secondary_weakening_distance` | subtracts a second slip-activated exponential strength loss |
| `dilation_support_reference`, high-normal reference, and their exponents | suppresses dilation when normal contact is too weak or too strong |
| `use_irreversible_dilation_target`, `max_irreversible_dilation`, target distance and exponent | replaces incremental angle-based dilation by a bounded irreversible target |
| rate-and-state switch, \(a\), \(b\), \(D_c\), \(V_0\), and initial state | adds a referenced RSF resistance and exact aging-law update |

The optional normal-pressure memory is

$$
p_{\mathrm{ret}}
=p_{m,n}\exp\left(\frac{\ln\zeta}{L_m}\Delta g_n^+\right),
\qquad
p_m=\max_{\epsilon_\sigma}(p_c,p_{\mathrm{ret}}).
$$

Retained shear support and secondary weakening give

$$
Y_{\mathrm{pre}}
=\max_{\epsilon_\sigma}
\left[Y_{\mathrm{raw}},H_Y Y_{H,n}e^{-\Delta\gamma/L_H}\right],
$$

$$
W_2(s)=\Delta S
\left[1-\exp\left(-\frac{\langle s-s^*\rangle_+}{w}\right)\right],
\qquad
Y=\max_{\epsilon_\sigma}(Y_{\mathrm{pre}}-W_2,0).
$$

The normal-stress support multiplying dilation is

$$
S_p(p_s)=
\left(\frac{p_s}{p_s+\sigma_{\mathrm{low}}}\right)^{n_{\mathrm{low}}}
\left(\frac{\sigma_{\mathrm{high}}}{p_s+\sigma_{\mathrm{high}}}\right)^{n_{\mathrm{high}}},
$$

with a factor set to one when its reference stress is zero. The alternative target law is

$$
D(s)=d_{\max}
\left\{1-\exp\left[-\left(\frac{s}{L_d}\right)^{m_d}\right]\right\},
$$

and the irreversible update takes only the nonnegative increase toward \(dS_pD(s)\). In target mode, the specified dilation angles do not control the normal plastic increment.

### 21.3 Hydraulic-aperture inputs

| Input | Default | Units | Role |
|---|---:|---|---|
| `initial_hydraulic_aperture` | 0 | m | Reference aperture \(a_{h0}\) |
| `aperture_scale` | 1 | -- | Mechanical-to-hydraulic opening scale \(\chi_m\) |
| `normal_stress_aperture_compliance` | 0 | m/Pa | Linear reversible stress-aperture branch |
| `use_nonlinear_normal_closure` | false | -- | Select bounded nonlinear stress aperture |
| `bb_max_aperture_closure` | 0 | m | Hydraulic closure amplitude \(V_m^h\) |
| `bb_initial_normal_stiffness` | 0 | Pa/m | Hydraulic \(K_{ni}^h\) |
| `nonlinear_closure_type` | `barton_bandis` | -- | BB or exponential branch |
| `dilation_scale` | 1 | -- | Separate cumulative-dilation scale; omit in a strictly kinematic aperture route |
| `use_kinematic_aperture` | false | -- | Treat solved gap as containing dilation |
| `min_hydraulic_aperture` | \(10^{-12}\) | m | Positive flow safeguard |
| `retention_residual` | 0.2 | -- | Residual retained-dilation fraction |
| `use_slip_damage` | false | -- | Enable gouge/slip-loss term |
| `slip_damage_scale` | 0 | m | Maximum gouge-related aperture reduction |
| `slip_damage_characteristic_slip` | \(10^{-3}\) | m | Gouge saturation distance |
| `use_closure_creep` | false | -- | Enable time-dependent closure |
| `closure_creep_time` | \(10^5\) | s | Reference creep time |
| `fluid_viscosity` | \(1.002\times10^{-3}\) | Pa s | Viscosity used in transmissivity |

`fault_thickness` is accepted by the inspected permeability material but is not used in its aperture, permeability, or transmissivity calculation. It must not be presented as an active calibration parameter.

### 21.4 Principal state and coupling properties

| Property | AD/state status | Meaning or consumer |
|---|---|---|
| `interface_displacement_jump` | AD, current | Local jump consumed by contact and aperture laws |
| `displacement_jump_global` | AD, current | Global jump diagnostic |
| `czm_total_rotation` | AD, current | Local-to-global rotation |
| `interface_traction` | AD, incremental | Local constitutive traction |
| `traction_global` | AD, current | Consumed by `OrcaMechInterfaceKernel` |
| `interface_pore_pressure` | AD, current | Mean pressure trace |
| `plastic_tangential_jump` | non-AD, stateful | Irreversible tangential jump |
| `cumulative_plastic_slip` | non-AD, stateful | Accumulated equivalent slip |
| `irreversible_dilation` | non-AD, stateful | Accumulated dilation |
| `fracture_state` | non-AD diagnostic | Branch code; Model A uses 0 stick, 2 slip, 3 open, while BB-family codes must be read from their source/output definition |
| `limit_tau` | non-AD diagnostic | Current shear-strength limit |
| `roughness_state` | declared AD; derived from non-AD history | Hydraulic retention input |
| `mechanical_aperture` | AD, current | Nonnegative geometric gap |
| `hydraulic_aperture` | AD with partly lagged history | Consumed by storage/diagnostics |
| `fracture_permeability` | AD | \(a_h^2/12\) |
| `fracture_transmissivity` | AD | \(a_h^3/(12\mu_f)\) |

Property naming is not perfectly uniform. `base_name` is normalized with an underscore for most contact properties. In the permeability material, several input properties are prefixed, but `mechanical_aperture_name` and explicitly named outputs are used exactly as supplied. New decks must follow constructor behavior rather than assume that every property receives the same prefix.

### 21.5 Source-audit limitations that remain active

1. The state-dependent `fault_pressure_area_coefficient` exported by the contact law is not consumed by the inspected constant-coefficient pressure-traction kernel.
2. In kinematic aperture mode, cumulative-dilation tracking is disabled and evolving roughness is replaced by one in the inspected constructor. This suppresses more than the duplicate dilation term.
3. The closure-creep branch with zero stress exponent advances even at zero compression.
4. The exponential stress-aperture expression does not vanish at its nominal reference stress, while initialization assumes a zero reference contribution.
5. Initial hydraulic aperture assumes an initial roughness state of one; another initial roughness can create a first-step storage jump.
6. A zero minimum hydraulic aperture is unsafe because the pressure-trace conductance contains division by aperture.
7. Slip damage and creep use raw history values. Roughness is declared AD but depends on non-AD accumulated slip. Their present-step derivatives are therefore absent.
8. Stress-dependent tangential stiffness uses lagged normal stress, and the decoupled-dilation return-map derivative omits the derivative of its evolving angle.
9. The open branch resets `limit_tau` to zero even when a nonzero closed-contact strength floor is configured.

The selected SW-S4 configuration also combines mechanically kinematic dilation with `use_kinematic_aperture=false`, so the hydraulic material receives a separately accumulated dilation contribution. Because its scales were calibrated, this may be retained as an empirical composition, but it is not a strictly single-route kinematic aperture model. Changing it requires recalibration and a controlled comparison.

## 22. Verification status and required tests

Verification asks whether the equations are solved correctly; validation asks whether those equations represent an experiment. They must be reported separately.

As documented in the retired manual, the following regression families existed and passed on 18 August 2026:

| Area | Test | Status at that audit |
|---|---|---|
| Bulk | Terzaghi one-dimensional consolidation | Implemented |
| Bulk | Mandel problem | Implemented |
| Bulk | Pressure diffusion against an erfc solution | Implemented |
| Kernels | Mass storage, thermal storage, and simple diffusion | Implemented |
| Materials | BB cohesion/residual cohesion and Biot modulus | Implemented |
| Interface | Nonlinear normal closure | Specified, not yet implemented |
| Interface | MC return mapping and dissipation bound | Specified, not yet implemented |
| Interface | BB envelope and return mapping | Specified, not yet implemented |
| Flow | Cubic law and stateful aperture initialization | Specified, not yet implemented |
| Cross-model | Sneddon pressurized crack | Specified, not yet implemented |
| Cross-model | Inclined sliding fracture | Specified, not yet implemented |

This status is a dated record, not a guarantee of the present test tree. Run the current suite before making a verification claim.

The highest-priority additions are algebraic single-interface tests. For normal closure, compare the solved traction and tangent with the closed form during loading and unloading. For MC and BB, require \(\tau=Y\) at every sliding step and check the active history variables. For Model A, also verify the dissipation inequality. For flow, require

$$
a_h(0)=a_{h0},
\qquad
\kappa_f=\frac{a_h^2}{12},
\qquad
T=\frac{a_h^3}{12\mu_f},
$$

and a linear steady pressure profile without leak-off.

Two cross-model benchmarks remain especially useful. For an open pressurized crack of half-length \(b\), Sneddon's opening is

$$
w(s)=\frac{4(1-\nu^2)p_f}{E}\sqrt{b^2-s^2}.
$$

This checks jump orientation, pressure-traction sign, open-state handling, and agreement among constitutive laws in their common traction-free limit. An inclined closed fracture under far-field compression checks the Coulomb return map and load transformation. A common finite-domain error shared by all laws is a benchmark-discretization error; a difference among reduced laws identifies an implementation inconsistency.

The recommended implementation order is bulk verification, mesh splitting, jump/rotation patch tests, mechanical interface balance, normal closure, frictional return mapping, hardening/dilation, hydraulic aperture, and finally the fully coupled injection problem.

## 23. Calibration, observability, and validation guidance

### 23.1 Diagnostic order

When a history does not match an experiment, work from imposed conditions toward constitutive detail:

1. verify axial load/command, confinement, pressure history, mesh geometry, and port placement;
2. verify initial equilibrium and pre-seating;
3. use onset to examine the peak strength envelope;
4. use the stress drop and arrested slip to examine residual strength together with system stiffness;
5. use a resolved transition to examine weakening distance;
6. compare realized dilation with both the requested angle and the dissipation limit;
7. only after mechanics is acceptable, fit reference aperture, reversible opening, retention, and gouge loss; and
8. demonstrate time-step, local-substep, viscosity, penalty, and aperture-bound sensitivity.

Useful first-order relations are

$$
\frac{\delta Q}{Q}\simeq3\frac{\delta a_h}{a_h},
\qquad
\frac{\delta\kappa_f}{\kappa_f}\simeq2\frac{\delta a_h}{a_h},
$$

$$
\delta s_{\mathrm{final}}
\simeq\frac{\delta Y_{\mathrm{res}}}{k_{\mathrm{sys}}},
\qquad
\delta t_{\mathrm{onset}}
\simeq\frac{\delta Y_{\mathrm{peak}}}
{\mathrm d\tau_{\mathrm{driving}}/\mathrm dt}.
$$

### 23.2 Observable-to-parameter map

| Observable | Primarily constrains | Does not independently constrain |
|---|---|---|
| Pre-slip effective normal stress | pre-seating and normal closure | shear strength or dilation |
| Slip onset | peak friction/cohesion or BB peak envelope | weakening distance and residual strength |
| Stress-drop magnitude and arrested slip | residual strength together with system stiffness | weakening distance alone |
| Resolved drop shape | weakening distance and exponent | these parameters if the drop occupies one sampled stage |
| Peak normal displacement | dilation only when its limiter is inactive | nominal angle when the dissipation limiter binds |
| Unloading normal recovery | reversible compliance/closure and retention | shear dilation alone |
| Initial flow | reference hydraulic aperture | post-slip loss parameters |
| Peak hydraulic response | opening-transfer and reversible opening | reference aperture if not fixed first |
| Loading/unloading hysteresis | retention, gouge loss, or creep | a unique mechanism without independent aperture data |
| Long constant-pressure decay | creep rate parameters jointly | the ultimate closure amplitude unless the hold is long enough |

### 23.3 Reference-experiment boundary

The Ye and Ghassemi validation contains two tensile fractures (SW-T1 and SW-T2), a saw-cut fracture (SW-S3), and a polished saw cut (SW-S4), all from Sierra White granite and all tested at 30 MPa confinement. The protocol provides eleven loading/unloading stages and directly measured pressure, force/displacement, and discharge histories. Hydraulic aperture and permeability in the source comparison are derived from flow, so they are not independent validation observations.

The experiment strongly constrains onset, stress relaxation, slip, dilation, and net discharge for this short single-fracture cycle. It does not uniquely identify machine stiffness, the fracture pressure-area coefficient, separate friction/cohesion pairs, local aperture heterogeneity, long-term creep, gouge transport, thermal effects, or fracture-network connectivity. Those quantities require independent measurements or additional loading paths.

The current paper-case manifest is stored in [`Paper_1_Validations/Ye_and_Ghassemi_2018/PAPER_CASE_MANIFEST.tsv`](../../Ye_and_Ghassemi_2018/PAPER_CASE_MANIFEST.tsv). It is the authority for which numerical decks and CSV files support the manuscript. The legacy theory manuals are not authorities for the current deck selection.

### 23.4 Calibration warning signs

- A material parameter changed separately for specimens of the same material is acting as a fitted case parameter unless an independent measurement supports it.
- A fitted piston motion or confinement history removes part of the experiment's independence and must be disclosed as a calibrated boundary history.
- A nominal dilation angle above an active dissipation bound is not the realized dilation parameter.
- An aperture floor equal to the initial aperture prevents hydraulic closure and can imitate retention.
- Fitting flow, aperture, and permeability inferred from that same flow as three independent channels overweights one measurement.
- More free parameters than independent response features indicates non-identifiability even when nRMSE is small.

## 24. Documentation maintenance rule

When the source changes, update this file in the following order:

1. strong and weak forms;
2. state-variable definitions and signs;
3. local residual equations and admissible bounds;
4. consistent-tangent method;
5. AD-excluded or lagged terms;
6. active parameter switches in the input files;
7. verification tests and postprocessors.

The source code is authoritative for implementation behavior. The equations are authoritative only when their active branches match the input deck.

This file is maintained at `Paper_1_Validations/General_Docs/Related_Theory/theory.md`. Do not create a second general theory Markdown file. Add new constitutive derivations, weak forms, parameter definitions, source-audit findings, and numerical-algorithm notes here. Experiment-specific run audits and result discussions should remain in their corresponding validation directories and should link back to this file rather than copy its equations.

The consolidation completed on 3 September 2026 retired the following files:

| Retired document | Consolidated location |
|---|---|
| `ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile_CONSTITUTIVE_LAW.md` | Sections 7, 8, 10, 14, and 20 |
| `orca_4.0_theory_aug31_2026.md` | Sections 8--13 and 20--23 |
| `orca_czm_theory.md` | Parts I--II and Sections 20--23 |
| `BOUNDARY_PENALTY_LOADING_AND_VALUE_INFERENCE.md` | Section 5 |
| `FRACTURE_PRESSURE_COEFFICIENT.md` | Section 4 |

This table records provenance; the retired paths should not be recreated.
