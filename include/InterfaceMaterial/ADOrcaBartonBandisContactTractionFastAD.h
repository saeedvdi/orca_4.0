#pragma once

#include "OrcaCZMComputeLocalTractionIncrementalBase.h"

/**
 * ADOrcaBartonBandisContactTractionFastAD
 *
 * Identical physics to ADOrcaBartonBandisContactTractionMoosePlasticUpdate but with
 * two performance optimizations:
 *
 * (1) Non-AD output properties
 *     All diagnostic/stateful material properties that are not consumed as ADReal by
 *     downstream kernels are declared as MaterialProperty<Real> rather than
 *     ADMaterialProperty<Real>.  Only _interface_traction_inc (inherited) and
 *     _dilation_jump_increment (consumed by ADOrcaCZMComputeMechanicalAperture) remain AD.
 *     This eliminates unnecessary derivative propagation for ~13 properties per QP call.
 *
 * (2) Real-arithmetic Newton-Raphson + IFT consistent tangent
 *     The return-mapping NR loop runs entirely in Real (double) arithmetic — no ADReal
 *     overhead per iteration.  After the loop converges to the scalar delta_gamma_p, the
 *     consistent tangent is recovered analytically via the implicit function theorem:
 *
 *       d(delta_gamma_p)/d(DOF_k) = -(dR/d(DOF_k)) / (dR/d(delta_gamma_p))
 *
 *     where R = |tau_trial| - K_t*delta_gamma_p - tau_limit(delta_gamma_p, closure_old).
 *     dR/d(DOF_k) is obtained by evaluating tau_norm_trial and tau_limit as ADReal at the
 *     converged scalar delta_gamma_p (one ADReal pass, not per-iteration).
 *     dR/d(delta_gamma_p) = dR_dg is the analytical derivative already computed for NR.
 *
 * Use in input files with:
 *   type = OrcaBartonBandisContactTractionFastAD
 */
class ADOrcaBartonBandisContactTractionFastAD : public OrcaCZMComputeLocalTractionIncrementalBase
{
public:
  static InputParameters validParams();
  ADOrcaBartonBandisContactTractionFastAD(const InputParameters & parameters);

protected:
  virtual void initQpStatefulProperties() override;
  virtual void computeInterfaceTractionIncrement() override;

  // ---- ADReal helpers (used for IFT ADReal pass and diagnostics) ----
  ADReal log10AD(const ADReal & x) const;
  ADReal clampAD(const ADReal & x, Real lo, Real hi) const;
  ADReal regularizedPositive(const ADReal & x) const;
  Real regularizedPositiveReal(Real x) const;
  Real regularizedPositiveDerivativeReal(Real x) const;
  virtual Real computeRoughnessState() const;
  virtual Real computeCohesionEffective() const;

  void computeNormalStressAndTangent(const ADReal & closure,
                                     ADReal & sigma_n,
                                     ADReal & kn_tangent) const;

  ADReal computeEffectiveNormalStressForStrength(const ADReal & contact_normal_stress) const;
  Real computeEffectiveNormalStressForStrengthReal(Real contact_normal_stress) const;
  Real computeEffectiveNormalStressTangentScale(Real contact_normal_stress) const;

  virtual void computeBartonBandisProperties(const ADReal & sigma_n,
                                             const ADReal & cumulative_slip,
                                             ADReal & jrc_mobilized,
                                             ADReal & roughness_angle_deg,
                                             ADReal & peak_friction_angle_deg,
                                             ADReal & friction_coefficient,
                                             ADReal & dilation_angle_deg,
                                             ADReal & dilation_coefficient,
                                             ADReal & shear_strength) const;

  ADReal computeDilationIncrement(const ADReal & dilation_coefficient,
                                  const ADReal & plastic_slip_increment,
                                  const ADReal & available_closure) const;

  // ---- Real helpers (used inside the NR loop — no AD overhead) ----
  void computeNormalStressAndTangentReal(Real closure, Real & sigma_n, Real & kn_tangent) const;

  bool normalUnloadRetentionEnabled() const;
  void updateNormalUnloadState(Real raw_closure, Real cumulative_slip);
  void updateReportedNormalOpening(const ADReal & total_opening,
                                   Real irreversible_opening,
                                   Real cumulative_slip);

  virtual void computeBartonBandisPropertiesReal(Real sigma_n,
                                                 Real cumulative_slip,
                                                 Real & jrc_mobilized,
                                                 Real & roughness_angle_deg,
                                                 Real & peak_friction_angle_deg,
                                                 Real & friction_coefficient,
                                                 Real & dilation_angle_deg,
                                                 Real & dilation_coefficient,
                                                 Real & shear_strength) const;

  Real computeDilationIncrementReal(Real dilation_coefficient,
                                    Real plastic_slip_increment,
                                    Real available_closure) const;

  Real computeDNormalStressDPlasticSlipReal(Real kn_tangent,
                                            Real dilation_coefficient,
                                            Real dilation_increment,
                                            Real closure_new) const;

  virtual ADReal computeAdditionalShearStrength(const ADReal & sigma_n,
                                                Real plastic_slip_increment) const;

  virtual Real computeAdditionalShearStrengthReal(Real sigma_n,
                                                  Real plastic_slip_increment,
                                                  Real d_sigma_n_d_plastic_slip,
                                                  Real & dstrength_dslip) const;

  virtual void carryAdditionalState();
  virtual void commitAdditionalState(Real plastic_slip_increment);

  // ---- Return-mapping analytical derivative (used for NR step and IFT) ----
  virtual Real computeReturnMappingDerivative(Real sigma_n,
                                              Real kn_tangent,
                                              Real jrc_mobilized,
                                              Real roughness_angle_deg,
                                              Real peak_friction_angle_deg,
                                              Real mu,
                                              Real dilation_coefficient,
                                              Real dilation_increment,
                                              Real closure_new,
                                              Real cumulative_slip_new) const;

  enum class FractureState : int
  {
    Stick = 0,
    Slip = 1,
    Open = 2
  };

  // ---- Numerical parameters ----
  const Real _normal_traction_tolerance;
  const Real _tangential_traction_tolerance;
  const Real _penalty_tangent_input;
  const Real _penalty_tangent;
  const Real _max_plastic_slip_increment;
  const Real _max_dilation_increment;
  const unsigned int _max_return_mapping_iterations;
  const Real _relative_tolerance;

  // Smooth Macaulay bracket used at the unilateral contact/open transition. Zero preserves the
  // legacy active-set switch; a small positive length retains a bounded contact Jacobian while
  // normal and tangential tractions decay continuously as the interface opens.
  const Real _contact_gap_regularization;

  // ---- Perzyna tangential viscous regularization (OPT-IN; default 0 = legacy) ----
  // Adds a rate-dependent overstress term  eta * (delta_gamma_p / dt)  to the return-mapping
  // residual  R = |tau_trial| - K_t*delta_gamma_p - tau_limit - eta*delta_gamma_p/dt.
  // This removes the stick/slip kink at |tau| = tau_limit and makes the consistent tangent
  // strictly positive-definite near a softening (slip-weakening / dilatant) slip front,
  // letting a quasi-static solver crawl through the limit point instead of stalling at dt->0.
  // Units: Pa.s/m. Default 0.0 reproduces the un-regularized (legacy) return map exactly.
  const Real _tangential_viscosity;

  // ---- Residual shear-strength floor (OPT-IN; default 0 = legacy) ----
  // When > 0, the BB shear-strength limit (tau_limit) is never allowed below this floor,
  // even when the joint opens and sigma_n -> 0. Physically this represents the residual
  // asperity / self-propping shear resistance that keeps a rough joint from having
  // literally zero strength when it dilates open. Numerically it removes the
  // tau_limit -> 0 (mobilization ratio -> inf) singularity that makes the quasi-static
  // solver fail at the dynamic slip event. Default 0.0 reproduces legacy behavior exactly.
  const Real _min_tau_limit;

  // ---- Normal closure parameters ----
  const bool _use_hyperbolic_normal_closure;
  const Real _initial_normal_stiffness;
  const Real _maximum_closure;
  const Real _maximum_closure_fraction;

  // ---- Power-law closure exponent (OPT-IN; default 1.0 = standard BB hyperbola) ----
  // Generalizes the hyperbolic closure to the power-law Barton-Bandis form
  //   closure(sigma_n) = V_m * sigma_n^p / (sigma_0^p + sigma_n^p),  sigma_0 = K_ni * V_m,
  // inverted for the traction update as
  //   sigma_n(closure) = sigma_0 * (closure / (V_m - closure))^(1/p).
  // Motivation (Ye & Ghassemi 2018 SW-S4 back-analysis): the Table-2 unload branch stiffens
  // ~3.2-4x across sigma'_n 17->25 MPa, while a p=1 hyperbola's tangent-stiffness ratio over
  // that range is capped at (25/17)^2 ~ 2.1. The power-law tangent stiffness scales like
  // sigma^(p+1) at sigma >> sigma_0, so p ~ 2-3 reproduces the measured stiffening while
  // remaining bounded by V_m (the deck-42/43 aperture-closure lesson, applied to the
  // mechanical contact). p = 1.0 runs the exact legacy hyperbola code path.
  const Real _normal_closure_stress_exponent;

  // ---- Closure pre-seating offset (OPT-IN; default 0 = legacy) ----
  // Adds a constant closure offset c_0 [m] to the effective gap, so at zero displacement
  // jump the joint already carries sigma_n(c_0). Use c_0 = closure(sigma_n0) to start a
  // pre-stressed in-situ joint in equilibrium with the bulk initial stress WITHOUT the
  // startup seating transient (the joint would otherwise have to interpenetrate by ~V_m to
  // build the preload, dumping the compensated axial preload into a compliant loading
  // frame). The displacement jump then measures opening/closure RELATIVE to the pre-seated
  // in-situ state, which is also the natural reference for validation-dilation curves.
  const Real _normal_closure_offset;

  // ---- Normal unloading retention (OPT-IN; default 0 = legacy) ----
  // After activated slip, a fraction of closure recovered during unloading can be retained as
  // an eigen-opening/mismatch of the normal closure law. This gives the reloading branch a small
  // hysteresis: sigma_n is evaluated at (raw closure - retained opening). It targets the Ye &
  // Ghassemi SW-S4 normal-stress rebound residual without moving the loading-path pressure curve.
  const Real _normal_unload_retention_fraction;
  const Real _normal_unload_retention_time;
  const Real _normal_reclosure_stiffness_multiplier;
  const Real _normal_unload_activation_slip;

  // ---- Reported normal-opening reconstruction (OUTPUT ONLY) ----
  // Split the converged kinematic jump into irreversible dilation and a reversible
  // remainder. The remainder may be scaled and partially retained on reclosure without
  // changing contact traction, displacement, aperture, permeability, or flow.
  const Real _reported_reversible_normal_opening_scale;
  const Real _reported_reversible_normal_opening_retention_fraction;
  const Real _reported_reversible_normal_opening_retention_activation_slip;

  // ---- Slip-activated reversible joint-normal compliance (OUTPUT ONLY) ----
  // The reconstruction above can only report opening the mechanics actually produced. The
  // power-law closure is pre-seated (c/V_m = 0.96-0.997 at the reported initial sigma'_n),
  // so it is effectively rigid over the post-slip unloading branch and reports no rebound
  // even when the experiment measures tens of micrometres of it. This adds the same
  // slip-activated elastic term the Mohr-Coulomb law carries, so the two laws report the
  // same physical quantity and can be compared. See
  // ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile::storeFinalState.
  const Real _reversible_normal_compliance;
  const Real _reversible_normal_reference_stress;
  const Real _reversible_normal_opening_activation_slip;
  const Real _reversible_normal_opening_activation_distance;
  const Real _reversible_normal_opening_activation_exponent;

  // ---- BB shear/strength parameters ----
  const Real _jrc0;
  const Real _jcs0;
  const Real _residual_friction_angle_deg;
  const bool _use_scale_correction;
  const Real _laboratory_length;
  const Real _joint_length;
  const Real _jrc_scaled_const;
  const Real _jcs_scaled_const;
  const Real _compressive_normal_stress_floor;
  const Real _pore_pressure_strength_coefficient;
  const ADMaterialProperty<Real> * const _interface_pore_pressure;
  const bool _allow_negative_roughness_angle;
  const Real _min_friction_angle_deg;
  const Real _max_friction_angle_deg;

  // ---- Physically-motivated fault-pressure area coefficient (OPT-IN; default false = legacy) ----
  // alpha = sigma_0 / (sigma_0 + sigma_n), a saturating hyperbola in the current effective
  // contact stress (Greenwood-Williamson-style real-contact-area growth: 0 at sigma_n=0, ->1 as
  // sigma_n->infinity), multiplying OrcaCZMFluidPressureInterfaceKernel's
  // pressure_traction_coefficient via alpha_property_name = fault_pressure_area_coefficient.
  // Ports the state-dependent alpha already implemented and locally validated on the MC contact
  // law (ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile, task #22) to this
  // Barton-Bandis law, so the BBFast decks (10/11/12/13) can get the same physically-motivated,
  // state-dependent pore-pressure coupling instead of the flat empirical constant
  // fault_pressure_coefficient = 0.86. sigma_0 (fault_pressure_area_reference_stress) is a
  // fitted-per-sample reference stress, calibrated so alpha = 0.86 at that sample's own initial
  // (Pi=8 MPa) effective normal stress -- see the MC material's identical parameter for the
  // derivation and the two failed "zero new constants" attempts (K_ni/K(closure), K_ni*V_m).
  // Default false reproduces legacy behavior exactly: this property is declared but simply
  // unused unless a deck's interface kernel blocks set alpha_property_name explicitly. Task #24.
  const bool _use_state_dependent_fault_pressure_coefficient;
  const Real _fault_pressure_area_reference_stress;

  // ---- Dilatancy parameters ----
  const Real _dilation_factor;
  const Real _min_dilation_angle_deg;
  const Real _max_dilation_angle_deg;
  const bool _accumulate_irreversible_dilation;
  const bool _cap_dilation_to_available_closure;
  const bool _use_dilatancy;

  // ---- Decoupled (mobilized) dilation angle (OPT-IN; default false = legacy) ----
  // Legacy BB welds dilation to the JRC strength term: psi = dilation_factor * roughness_angle,
  // so a smooth (low-JRC) joint gets ~0 dilation even when the friction match requires it.
  // When _use_decoupled_dilation is true, the dilation angle is instead governed by its OWN
  // Barton-1982-style mobilization/decay law, INDEPENDENT of the JRC strength term:
  //   psi_mob(s^p) = psi_residual + (psi_peak - psi_residual) * exp(-s^p / D_dilation)
  // This keeps the BB strength (tau_limit = sigma_strength*tan(phi_r +
  // JRC*log10(JCS/sigma_strength))) exactly as-is (stress match preserved), while letting dilation
  // be tuned to match dn. psi_peak at first slip, decaying toward psi_residual over characteristic
  // slip D_dilation.
  const bool _use_decoupled_dilation;
  const Real _dilation_angle_peak_deg;
  const Real _dilation_angle_residual_deg;
  const Real _dilation_decay_distance;

  // ---- Kinematic dilation routing (OPT-IN; default false = legacy) ----
  // When true, accumulated irreversible dilation is applied as a NORMAL EIGEN-OPENING
  // of the joint: it enters the displacement field (the fracture physically opens) and
  // the within-step feedback becomes dilatant HARDENING instead of stress softening.
  // When false, every code path is byte-identical to the legacy formulation.
  //   _dil_gap_sign     : sign of accumulated dilation in the start-of-step gap
  //                       legacy +1 (softens closure), kinematic -1 (opens joint)
  //   _dil_closure_sign : sign of the within-step dilation increment in the closure update
  //                       legacy -1 (closure - dil, softening), kinematic +1 (closure + dil,
  //                       hardening)
  const bool _dilation_opens_joint;
  const Real _dil_gap_sign;
  const Real _dil_closure_sign;

  // ---- JRC mobilization parameters ----
  const bool _use_mobilized_jrc;
  const Real _peak_shear_displacement;
  const Real _mobilized_jrc_exponent;

  // ---- Stateful properties (non-AD: only read as _old in next step) ----
  MaterialProperty<Real> & _fracture_state;
  MaterialProperty<Real> & _limit_tau;
  MaterialProperty<Real> & _plastic_slip_increment;

  // Must remain AD: consumed by ADOrcaCZMComputeMechanicalAperture as AD.
  ADMaterialProperty<Real> & _dilation_jump_increment;

  MaterialProperty<Real> & _cumulative_plastic_slip;
  const MaterialProperty<Real> & _cumulative_plastic_slip_old;

  MaterialProperty<Real> & _irreversible_dilation;
  const MaterialProperty<Real> & _irreversible_dilation_old;

  MaterialProperty<RealVectorValue> & _plastic_tangential_jump;
  const MaterialProperty<RealVectorValue> & _plastic_tangential_jump_old;

  MaterialProperty<Real> & _bb_unload_retained_opening;
  const MaterialProperty<Real> & _bb_unload_retained_opening_old;

  MaterialProperty<Real> & _bb_unload_min_closure;
  const MaterialProperty<Real> & _bb_unload_min_closure_old;

  MaterialProperty<Real> & _reversible_normal_opening;
  MaterialProperty<Real> & _normal_opening_total;
  MaterialProperty<Real> & _maximum_reversible_normal_opening;
  const MaterialProperty<Real> & _maximum_reversible_normal_opening_old;

  // ---- Diagnostic output properties (non-AD) ----
  MaterialProperty<Real> & _friction_coefficient_effective;
  MaterialProperty<Real> & _cohesion_effective;
  ADMaterialProperty<Real> & _roughness_state;
  MaterialProperty<Real> & _roughness_damage;
  MaterialProperty<Real> & _bb_compressive_normal_stress;
  MaterialProperty<Real> & _bb_effective_normal_stress;
  ADMaterialProperty<Real> & _bb_normal_closure;
  MaterialProperty<Real> & _bb_normal_stiffness_tangent;
  MaterialProperty<Real> & _bb_jrc_scaled;
  MaterialProperty<Real> & _bb_jcs_scaled;
  MaterialProperty<Real> & _bb_jrc_mobilized;
  MaterialProperty<Real> & _bb_roughness_angle_degrees;
  MaterialProperty<Real> & _bb_peak_friction_angle_degrees;
  MaterialProperty<Real> & _bb_peak_friction_coefficient;
  MaterialProperty<Real> & _bb_dilation_angle_degrees;
  MaterialProperty<Real> & _bb_dilation_coefficient;

  // Must remain AD: consumed by OrcaCZMFluidPressureInterfaceKernel::alpha_property_name as AD.
  ADMaterialProperty<Real> & _fault_pressure_area_coefficient;
};
