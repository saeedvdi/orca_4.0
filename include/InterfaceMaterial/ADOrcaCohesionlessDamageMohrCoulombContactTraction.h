#pragma once

#include "OrcaCZMComputeLocalTractionIncrementalBase.h"

/**
 * Cohesionless damage Mohr-Coulomb contact law with energy-bounded dilation.
 *
 * This is the simplified Mohr-Coulomb successor to
 * ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile for pre-existing
 * frictional joints.  It deliberately does not inherit from the Barton-Bandis law.
 *
 * Core law:
 *
 *   p        = K_n <g_np - g_n>_+
 *   tau_y   = c + p [mu_r + (mu_p - mu_r) A(s)]
 *   A(s)    = exp[-(s / D_w)^m]
 *   dg_np   = beta_d max(mu, mu_dil_floor) dgamma, with mu_dil_floor <= mu_r
 *
 * with beta_d < 1 so p dg_np is bounded by the frictional sliding work in the
 * Mohr-Coulomb branch.  The optional c term defaults to zero and represents only
 * an apparent shear-cohesion intercept; it does not create tensile normal cohesion.
 * Optional two-stage damage and referenced rate-and-state friction are retained as
 * compact, interpretable extensions.
 */
class ADOrcaCohesionlessDamageMohrCoulombContactTraction
  : public OrcaCZMComputeLocalTractionIncrementalBase
{
public:
  static InputParameters validParams();
  ADOrcaCohesionlessDamageMohrCoulombContactTraction(const InputParameters & parameters);

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

  struct FrictionState
  {
    ADReal residual;
    ADReal dres_dgamma;
    ADReal gamma;
    ADReal cumulative_slip;
    ADReal friction;
    ADReal dfriction_dgamma;
    ADReal dilation_coefficient;
    ADReal ddilation_dgamma;
    ADReal dilation_increment;
    ADReal normal_plastic_jump;
    ADReal normal_pressure;
    ADReal normal_pressure_tangent_gamma;
    ADReal cohesion;
    ADReal strength;
    ADReal rate_state_theta;
    ADReal rsf_strength;
    ADReal drsf_dgamma;
  };

  ADReal smoothPositive(const ADReal & x, Real eps) const;
  ADReal smoothPositiveDerivative(const ADReal & x, Real eps) const;

  ADReal weakeningWeight(const ADReal & cumulative_slip,
                         Real slip_distance,
                         Real exponent,
                         Real onset_slip = 0.0) const;
  ADReal weakeningWeightDerivative(const ADReal & cumulative_slip,
                                   Real slip_distance,
                                   Real exponent,
                                   Real onset_slip = 0.0) const;
  void frictionCoefficient(const ADReal & cumulative_slip,
                           ADReal & friction,
                           ADReal & dfriction_dgamma) const;
  void dilationCoefficient(const ADReal & friction,
                           const ADReal & dfriction_dgamma,
                           ADReal & coefficient,
                           ADReal & dcoefficient_dgamma) const;
  ADReal roughnessState(const ADReal & cumulative_slip) const;
  ADReal evolveRateStateTheta(const ADReal & gamma) const;

  FrictionState evaluateFriction(const ADReal & gamma,
                                 const ADReal & tau_trial,
                                 const ADReal & current_normal_jump,
                                 const ADReal & old_normal_plastic_jump,
                                 const ADReal & old_cumulative_slip,
                                 const ADReal & old_theta) const;

  // Numerical/contact parameters
  const Real _penalty_normal;
  const Real _penalty_tangent;
  const Real _opening_gap_tolerance;
  const Real _tangential_traction_tolerance;
  const Real _contact_gap_regularization;
  const Real _stress_regularization;
  const Real _local_newton_tolerance;
  const unsigned int _max_local_newton_iterations;
  const Real _tangential_viscosity;

  // Direct cohesionless damage strength
  const Real _peak_friction_coefficient;
  const Real _residual_friction_coefficient;
  const Real _apparent_cohesion;
  const Real _damage_slip_distance;
  const Real _damage_exponent;
  const bool _use_two_stage_damage;
  const Real _intermediate_friction_coefficient;
  const Real _fast_damage_slip_distance;
  const Real _fast_damage_exponent;
  const Real _fast_damage_onset_slip;
  const Real _slow_damage_slip_distance;
  const Real _slow_damage_exponent;
  const Real _slow_damage_onset_slip;

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
  const Real _reversible_normal_reference_stress;

  // Referenced rate-and-state friction perturbation
  const bool _use_rate_and_state;
  const Real _rate_and_state_a;
  const Real _rate_and_state_b;
  const Real _rate_and_state_Dc;
  const Real _rate_and_state_V0;
  const Real _rate_and_state_theta0;
  const bool _rate_and_state_nonnegative;

  // Stateful/output properties
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

  ADMaterialProperty<Real> & _rate_state_theta;
  const MaterialProperty<Real> & _rate_state_theta_old;

  ADMaterialProperty<Real> & _frictional_sliding_work_increment;
  ADMaterialProperty<Real> & _dilation_work_increment;
  ADMaterialProperty<Real> & _frictional_dilatant_dissipation_increment;
  ADMaterialProperty<Real> & _cohesive_dissipation_increment;

  ADMaterialProperty<RealVectorValue> & _plastic_tangential_jump;
  const MaterialProperty<RealVectorValue> & _plastic_tangential_jump_old;
};
