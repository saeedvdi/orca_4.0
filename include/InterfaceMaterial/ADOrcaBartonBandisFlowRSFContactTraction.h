#pragma once

#include "OrcaCZMComputeLocalTractionIncrementalBase.h"

#include <array>

/**
 * ADOrcaBartonBandisFlowRSFContactTraction
 *
 * Barton--Bandis joint strength driving the flow-form (always-creeping) regularized
 * rate-and-state solve of ADOrcaPeakShelfTailFlowRSFContactTraction.  Where the
 * peak-shelf-tail law supplies a calibrated mu_qs(s) backbone, this material derives the
 * quasi-static friction from the Barton (1982) / Barton--Bandis (1985) model:
 *
 * 1. Quasi-static backbone (normal-stress dependent):
 *
 *      mu_qs(s, sigma'_n) = tan( phi_r + JRC_mob(s) * log10(JCS_n / sigma'_n) )   [deg]
 *
 *    with the laboratory->field scale corrections JRC_n = JRC0 (Ln/L0)^{-0.02 JRC0},
 *    JCS_n = JCS0 (Ln/L0)^{-0.03 JRC0} (Barton & Bandis 1982).  JRC_mob(s) follows the
 *    dimensionless post-peak branch of Barton's (1982) mobilization table,
 *
 *      x = delta/delta_p:   1     2     4     10    25    100
 *      JRC_mob/JRC_n:       1.00  0.85  0.70  0.50  0.40  0.00
 *
 *    interpolated by a monotone (Fritsch--Carlson) cubic in log10(x) with a flat landing
 *    at x = 100 (C1 into the residual plateau), and JRC_mob = 0 beyond.  The coordinate
 *    is PLASTIC slip: x = 1 + s/delta_p, i.e. s = 0 is the fully interlocked peak.  The
 *    pre-peak part of Barton's curve (0 <= x < 1) is intentionally NOT used: in a
 *    penalty-contact frame pre-peak compliance is carried by K_t elasticity plus the
 *    velocity-strengthening creep of the flow-form RSF, and a stuck natural fracture
 *    starts fully interlocked.  delta_p defaults to Barton's (1982) estimate
 *    (L/500)(JRC_n/L)^0.33 when peak_shear_displacement = 0.
 *
 *    The sigma'_n argument of the log10 (and of the dilation angle) is the pre-dilation
 *    contact pressure of the step (old normal plastic jump, current normal displacement
 *    jump): gamma-independent inside the local solve, which breaks the
 *    angle->dilation->pressure cycle; the MULTIPLICATIVE sigma'_n in the strength stays
 *    fully implicit exactly as in the PST law.  The lag is second order (the angle sees
 *    sigma'_n only through log10).
 *
 * 2. Flow-form regularized rate-and-state, identical to the PST material: the plastic
 *    increment gamma solves
 *
 *      tau_trial - K_t gamma = a p asinh[ (V/2V0) exp( (mu_qs + b ln(V0 theta/D_rs))/a ) ]
 *                              + eta_t V,   V = gamma/dt,
 *
 *    aging law with exact-exponential theta update, theta heals during holds, and the
 *    stick_velocity_floor numerical guard (exact elastic stick below ~1 nm/min bridged by
 *    a half-decade smoothstep in ln V) carries over unchanged.
 *
 * 3. Mobilized Barton dilation instead of the energy-fraction rule:
 *
 *      psi_mob(s, sigma'_n) = dilation_factor * JRC_mob(s) * log10(JCS_n / sigma'_n) [deg]
 *      d g_np / ds = tan(psi_mob),   smooth-capped at max_dilation_angle_degrees.
 *
 *    Barton's damage coefficient M enters as dilation_factor = 1/M (0.5 standard).
 *
 * Exported property names match the PST / cohesionless-damage MC laws (plus
 * bb_jrc_mobilized), so decks swap in with only the [Materials] block; roughness_state
 * for the permeability material is the mobilized-JRC fraction mapped onto
 * [roughness_state_residual, roughness_state_initial].
 *
 * Use in input files with:
 *   type = OrcaBartonBandisFlowRSFContactTraction
 */
class ADOrcaBartonBandisFlowRSFContactTraction
  : public OrcaCZMComputeLocalTractionIncrementalBase
{
public:
  static InputParameters validParams();
  ADOrcaBartonBandisFlowRSFContactTraction(const InputParameters & parameters);

protected:
  void initQpStatefulProperties() override;
  void computeInterfaceTractionIncrement() override;

private:
  enum class FractureState : unsigned int
  {
    Stick = 0,
    Slip = 2,
    Open = 3
  };

  /// One evaluation of the flow residual F(gamma) and its slip derivative.
  template <typename T>
  struct FlowEval
  {
    T residual;
    T dres_dgamma;
    T cumulative_slip;
    T friction;            // mu_qs(s, sigma_arg)
    T dfriction_dgamma;
    T mobilization;        // JRC_mob / JRC_n in [0, 1]
    T dilation_coefficient;
    T dilation_increment;
    T normal_plastic_jump;
    T normal_pressure;
    T strength;            // flow-RSF shear strength (excl. viscosity)
    T rate_state_theta;    // evolved theta for storage
  };

  ADReal smoothPositive(const ADReal & x, Real eps) const;
  void storeReversibleOpening(const ADReal & raw_opening,
                              const ADReal & irreversible_opening,
                              const ADReal & cumulative_slip);

  /// Barton (1982) post-peak mobilization fraction y = JRC_mob/JRC_n and dy/ds.
  template <typename T>
  void mobilizationFraction(const T & cumulative_slip, T & fraction, T & dfraction_ds) const;
  /// mu_qs(s, sigma_arg) and its slip derivative (sigma_arg held fixed).
  template <typename T>
  void frictionCoefficient(const T & cumulative_slip,
                           const T & sigma_arg,
                           T & friction,
                           T & dfriction_ds) const;
  template <typename T>
  void dilationCoefficient(const T & mobilization,
                           const T & dmobilization_ds,
                           const T & sigma_arg,
                           T & coefficient,
                           T & dcoefficient_ds) const;
  template <typename T>
  T evolveRateStateTheta(const T & gamma, Real theta_old) const;

  template <typename T>
  FlowEval<T> evaluateFlow(const T & gamma,
                           const T & tau_trial,
                           const T & current_normal_jump,
                           Real old_normal_plastic_jump,
                           Real old_cumulative_slip,
                           Real old_theta) const;

  /// Bracketed safeguarded Newton on raw values (log-space bisection fallback).
  Real solveFlowRaw(Real tau_trial,
                    Real current_normal_jump,
                    Real old_normal_plastic_jump,
                    Real old_cumulative_slip,
                    Real old_theta) const;

  /// Max |d tau_y/ds| of the quasi-static backbone at the reference normal stress.
  Real maxWeakeningSlope(Real sigma_n_ref) const;

  // Numerical/contact parameters
  const Real _penalty_normal;
  const Real _penalty_tangent;
  const bool _use_hyperbolic_normal_closure;
  const Real _initial_normal_stiffness;
  const Real _maximum_closure;
  const Real _maximum_closure_fraction;
  const Real _normal_closure_stress_exponent;
  const Real _normal_closure_offset;
  const Real _opening_gap_tolerance;
  const Real _tangential_traction_tolerance;
  const Real _contact_gap_regularization;
  const Real _stress_regularization;
  const Real _local_newton_tolerance;
  const unsigned int _max_local_newton_iterations;
  const Real _tangential_viscosity;

  // Barton--Bandis strength
  const Real _jrc0;
  const Real _jcs0;
  const Real _residual_friction_angle_deg;
  const bool _use_scale_correction;
  const Real _laboratory_length;
  const Real _joint_length;
  const Real _jrc_scaled;
  const Real _jcs_scaled;
  const Real _peak_shear_displacement; // delta_p actually used (auto if param was 0)
  /// Plastic slip below which JRC_mob stays fully mobilized (pre-peak plasticity is
  /// non-damaging); without it the table's steepest decay sits at s = 0+ and flow-form
  /// creep self-accelerates onset on an initially stressed fault.
  const Real _mobilization_onset_slip;
  // Multi-shelf staircase: cumulative-slip intervals where JRC mobilization freezes (the
  // table's effective slip stops accruing), cutting one terminal cliff into arrested treads.
  const std::vector<Real> _mobilization_shelf_onsets;
  const std::vector<Real> _mobilization_shelf_widths;
  const Real _compressive_normal_stress_floor;
  const Real _max_friction_angle_deg;
  const Real _apparent_cohesion;
  // Optional late-slip strengthening, separated from phi_r so the onset envelope
  // and the post-event arrest level can be calibrated independently.
  const Real _late_friction_angle_increment_deg;
  const Real _late_friction_onset_slip;
  const Real _late_friction_distance;
  const Real _late_friction_exponent;
  // Slip-rate resistance activated only on the late branch. An optional release branch
  // makes the resistance a finite slip window, so it can damp the late burst and then
  // return to the unmodified quasi-static envelope before the terminal comparison.
  const Real _late_tangential_viscosity;
  const Real _late_tangential_viscosity_onset_slip;
  const Real _late_tangential_viscosity_distance;
  const Real _late_tangential_viscosity_exponent;
  const Real _late_tangential_viscosity_release_slip;
  const Real _late_tangential_viscosity_release_distance;
  const Real _late_tangential_viscosity_release_exponent;

  // Barton (1982) mobilization table, PCHIP in u = log10(x): knots, values, slopes
  std::array<Real, 6> _mob_u;
  std::array<Real, 6> _mob_y;
  std::array<Real, 6> _mob_m;

  // Flow-form rate-and-state
  const Real _rsf_a;
  const Real _rsf_b;
  const Real _rsf_Dc;
  const Real _rsf_V0;
  const Real _rsf_theta0;
  const Real _stick_report_velocity;
  /// Solved-velocity floor below which the step is exact elastic stick (numerical
  /// guard: sub-floor creep is negligible but floors global Newton at ~K_t*A*V*dt).
  const Real _stick_velocity_floor;

  // Mobilized Barton dilation
  const bool _use_dilatancy;
  const Real _dilation_factor;
  const Real _min_dilation_angle_deg;
  const Real _max_dilation_angle_deg;

  // Exported roughness state for the downstream permeability law
  const Real _roughness_state_initial;
  const Real _roughness_state_residual;

  // Optional output-only reversible normal opening diagnostic
  const Real _reversible_normal_compliance;
  const Real _damage_scaled_reversible_compliance;
  const Real _reversible_normal_reference_stress;
  const Real _reversible_normal_opening_retention_fraction;
  const Real _reversible_normal_opening_retention_activation_slip;

  // W/k stability diagnostic (printed once at construction when both are set)
  const Real _stability_reference_normal_stress;
  const Real _system_shear_stiffness;

  // Stateful/output properties (names mirror the PST / cohesionless damage MC laws)
  ADMaterialProperty<Real> & _fracture_state;
  ADMaterialProperty<Real> & _limit_tau;
  ADMaterialProperty<Real> & _plastic_slip_increment;
  ADMaterialProperty<Real> & _dilation_jump_increment;
  ADMaterialProperty<Real> & _cumulative_plastic_slip;
  const MaterialProperty<Real> & _cumulative_plastic_slip_old;

  ADMaterialProperty<Real> & _roughness_state;
  ADMaterialProperty<Real> & _roughness_damage;
  ADMaterialProperty<Real> & _friction_coefficient_effective;
  ADMaterialProperty<Real> & _cohesion_effective;
  ADMaterialProperty<Real> & _dilation_angle_effective;
  ADMaterialProperty<Real> & _dilation_state;
  ADMaterialProperty<Real> & _dilation_support_factor;
  ADMaterialProperty<Real> & _bb_jrc_mobilized;

  ADMaterialProperty<Real> & _strength_normal_memory_magnitude;
  ADMaterialProperty<Real> & _strength_normal_memory;
  ADMaterialProperty<Real> & _retained_shear_support;

  ADMaterialProperty<Real> & _normal_plastic_jump;
  const MaterialProperty<Real> & _normal_plastic_jump_old;
  ADMaterialProperty<Real> & _irreversible_dilation;
  ADMaterialProperty<Real> & _normal_contact_pressure;
  ADMaterialProperty<Real> & _reversible_normal_opening;
  ADMaterialProperty<Real> & _normal_opening_total;
  ADMaterialProperty<Real> & _maximum_reversible_normal_opening;
  const MaterialProperty<Real> & _maximum_reversible_normal_opening_old;

  ADMaterialProperty<Real> & _rate_state_theta;
  const MaterialProperty<Real> & _rate_state_theta_old;

  ADMaterialProperty<Real> & _frictional_sliding_work_increment;
  ADMaterialProperty<Real> & _dilation_work_increment;
  ADMaterialProperty<Real> & _frictional_dilatant_dissipation_increment;
  ADMaterialProperty<Real> & _cohesive_dissipation_increment;

  ADMaterialProperty<RealVectorValue> & _plastic_tangential_jump;
  const MaterialProperty<RealVectorValue> & _plastic_tangential_jump_old;
};
