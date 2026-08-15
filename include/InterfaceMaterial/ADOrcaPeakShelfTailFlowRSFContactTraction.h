#pragma once

#include "OrcaCZMComputeLocalTractionIncrementalBase.h"

/**
 * ADOrcaPeakShelfTailFlowRSFContactTraction
 *
 * Direct implementation of the hardening law back-derived from the Ye & Ghassemi (2018)
 * SW-S3 / SW-S4 injection-shear tests (see
 * Examples/YeGhasemmi2018/HARDENING_LAW_FROM_YE2018_SW_S3_SW_S4.md).  One functional form
 * covers both the rough saw cut (single dynamic burst) and the polished saw cut
 * (arrested creep staircase); the two samples are two parameter points.
 *
 * 1. Peak-shelf-tail quasi-static friction backbone (two stretched exponentials):
 *
 *      A_c(s) = exp[ -(<s - s0_c>+ / D_c)^{m_c} ]     concentration (peak -> shelf)
 *      A_t(s) = exp[ -(<s - s0_t>+ / D_t)^{m_t} ]     tail          (shelf -> tail)
 *      mu_qs(s) = mu_tail + (mu_shelf - mu_tail) A_t + (mu_peak - mu_shelf) A_c
 *
 *    m_c >= 1 is the surface-finish/roughness knob: it delays then concentrates the
 *    strength drop.  Together with D_c it sets the peak weakening slope
 *    W_max = sigma'_n |d tau_y/ds|_max whose ratio to the system unloading stiffness
 *    k_tau decides burst (W/k > 1, SW-S3) versus staircase creep (W/k < 1, SW-S4).
 *
 * 2. Flow-form (always-creeping) regularized rate-and-state friction instead of a
 *    stick/slip active set.  The plastic slip increment gamma solves
 *
 *      tau_trial - K_t gamma  =  c_app
 *        + a p asinh[ (V / 2V0) exp( ( mu_qs(s_old+gamma) + b ln(V0 theta_old / D_rs) ) / a ) ]
 *        + eta_t V ,             V = gamma / dt,
 *      d theta / dt = 1 - V theta / D_rs        (aging law, exact-exponential update)
 *
 *    which reduces to tau_y = p [ mu_qs + a ln(V/V0) + b ln(V0 theta / D_rs) ] for V >> V0
 *    and to an exponentially small creep rate below the quasi-static strength.  This
 *    replaces the non-negative-clamped *referenced* RSF of the damage laws: the fault can
 *    creep under residual overstress (SW-S4 unloading creep / hold relaxation), theta
 *    heals during holds, and there is no semismooth stick<->slip transition to chatter.
 *
 *    Numerical guard: below stick_velocity_floor (default 1e-11 m/s ~ 0.6 nm/min) the
 *    solved creep is physically nil but its log-curvature length V*dt undercuts the
 *    global Newton excursion scale and floors |R| at ~K_t*A*V*dt (dt-independent
 *    stagnation at ramp->hold transitions).  Such steps become exact elastic stick,
 *    bridged by a half-decade smoothstep in ln V so the switch is value- and
 *    slope-continuous; theta continues aging through stick.  All resolvable creep
 *    (>~ 1 nm/min) still flows; stick_velocity_floor = 0 recovers the pure flow form.
 *
 * 3. Energy-bounded wear/bulking dilation (identical in form to the cohesionless damage
 *    laws): d g_np / ds = beta_d max( mu_qs, mu_floor ), optional geometric cap; plus the
 *    output-only reversible normal-opening diagnostic.
 *
 * Exported property names match ADOrcaCohesionlessDamageMohrCoulombContactTraction, so
 * decks and the downstream permeability material swap in with only the [Materials] block.
 *
 * Use in input files with:
 *   type = OrcaPeakShelfTailFlowRSFContactTraction
 */
class ADOrcaPeakShelfTailFlowRSFContactTraction
  : public OrcaCZMComputeLocalTractionIncrementalBase
{
public:
  static InputParameters validParams();
  ADOrcaPeakShelfTailFlowRSFContactTraction(const InputParameters & parameters);

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
    T friction;            // mu_qs(s)
    T dfriction_dgamma;
    T dilation_coefficient;
    T dilation_increment;
    T normal_plastic_jump;
    T normal_pressure;
    T strength;            // c_app + flow-RSF shear strength (excl. viscosity)
    T rate_state_theta;    // evolved theta for storage
  };

  ADReal smoothPositive(const ADReal & x, Real eps) const;
  Real smoothPositiveReal(Real x, Real eps) const;
  void storeReversibleOpening(const ADReal & raw_opening,
                              const ADReal & irreversible_opening,
                              const ADReal & cumulative_slip);

  template <typename T>
  T weakeningWeight(const T & cumulative_slip,
                    Real slip_distance,
                    Real exponent,
                    Real onset_slip) const;
  template <typename T>
  T weakeningWeightDerivative(const T & cumulative_slip,
                              Real slip_distance,
                              Real exponent,
                              Real onset_slip) const;
  template <typename T>
  void frictionCoefficient(const T & cumulative_slip, T & friction, T & dfriction_dgamma) const;
  template <typename T>
  void dilationCoefficient(const T & friction,
                           const T & dfriction_dgamma,
                           T & coefficient,
                           T & dcoefficient_dgamma) const;
  template <typename T>
  T roughnessState(const T & cumulative_slip) const;
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

  // Peak-shelf-tail friction backbone
  const Real _peak_friction_coefficient;
  const Real _shelf_friction_coefficient;
  const Real _tail_friction_coefficient;
  const Real _concentration_slip_distance;
  const Real _concentration_exponent;
  const Real _concentration_onset_slip;
  const Real _tail_slip_distance;
  const Real _tail_exponent;
  const Real _tail_onset_slip;
  const Real _apparent_cohesion;

  // Optional multi-shelf treads: additive step-down branches so each injection-paced slip
  // episode supplies its own backbone drop and arrests on a flat shelf until the next onset
  // (a single stretched-exponential branch couples supply to arrest and cannot staircase).
  const std::vector<Real> _tread_friction_drops;
  const std::vector<Real> _tread_onset_slips;
  const std::vector<Real> _tread_slip_distances;
  std::vector<Real> _tread_exponents; // filled to all-1.0 in the ctor when left empty

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

  // Energy-bounded dilation
  const bool _use_dilatancy;
  const Real _dilation_work_fraction;
  const Real _dilation_friction_coefficient_floor;
  const Real _maximum_dilation_coefficient;

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

  // Stateful/output properties (names mirror the cohesionless damage MC law)
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
