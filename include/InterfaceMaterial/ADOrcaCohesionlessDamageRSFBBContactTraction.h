#pragma once

#include "ADOrcaBartonBandisContactTractionFastAD.h"

/**
 * Cohesionless damage-RSF joint with Barton-Bandis mechanical normal closure.
 *
 * The normal contact response, tangential return map, dilation routing, and downstream CZM property
 * names are inherited from ADOrcaBartonBandisContactTractionFastAD.  The shear strength is replaced
 * by a direct, cohesionless damage law
 *
 *   tau_y = sigma_n [mu_r + (mu_p - mu_r) A(s)] + c_app
 *   A(s)  = exp[-(s / D_w)^m]
 *
 * An optional two-stage damage law splits the strength loss into fast asperity
 * polish and slower gouge/roughness evolution:
 *
 *   mu(s) = mu_r + (mu_i - mu_r) A_slow(s) + (mu_p - mu_i) A_fast(s)
 *   A_branch(s) = exp[-(<s - s0_branch>+ / D_branch)^m_branch]
 *
 * and dilation is bounded by a configurable dilation friction coefficient:
 *
 *   dg_n^p / ds <= dilation_work_fraction * max(mu(s), dilation_friction_coefficient_floor)
 *
 * The optional dilation friction floor affects only dilation; shear strength still uses mu(s).
 * Optional rate-and-state adds a Dieterich-Ruina perturbation around steady sliding at V0.
 * Optional roughness-scaled parameters interpolate the damage/dilation coefficients between
 * smooth- and rough-joint endpoints using roughness_state_initial, so one law can represent
 * SW-S4 gradual polishing and SW-S3 rough burst/propping without changing the constitutive form.
 */
class ADOrcaCohesionlessDamageRSFBBContactTraction
    : public ADOrcaBartonBandisContactTractionFastAD
{
public:
  static InputParameters validParams();
  ADOrcaCohesionlessDamageRSFBBContactTraction(const InputParameters & parameters);

protected:
  void initQpStatefulProperties() override;

  void computeBartonBandisProperties(const ADReal & sigma_n,
                                     const ADReal & cumulative_slip,
                                     ADReal & jrc_mobilized,
                                     ADReal & roughness_angle_deg,
                                     ADReal & peak_friction_angle_deg,
                                     ADReal & friction_coefficient,
                                     ADReal & dilation_angle_deg,
                                     ADReal & dilation_coefficient,
                                     ADReal & shear_strength) const override;

  void computeBartonBandisPropertiesReal(Real sigma_n,
                                         Real cumulative_slip,
                                         Real & jrc_mobilized,
                                         Real & roughness_angle_deg,
                                         Real & peak_friction_angle_deg,
                                         Real & friction_coefficient,
                                         Real & dilation_angle_deg,
                                         Real & dilation_coefficient,
                                         Real & shear_strength) const override;

  Real computeReturnMappingDerivative(Real sigma_n,
                                      Real kn_tangent,
                                      Real jrc_mobilized,
                                      Real roughness_angle_deg,
                                      Real peak_friction_angle_deg,
                                      Real mu,
                                      Real dilation_coefficient,
                                      Real dilation_increment,
                                      Real closure_new,
                                      Real cumulative_slip_new) const override;

  ADReal computeAdditionalShearStrength(const ADReal & sigma_n,
                                        Real plastic_slip_increment) const override;

  Real computeAdditionalShearStrengthReal(Real sigma_n,
                                          Real plastic_slip_increment,
                                          Real d_sigma_n_d_plastic_slip,
                                          Real & dstrength_dslip) const override;

  void carryAdditionalState() override;
  void commitAdditionalState(Real plastic_slip_increment) override;

  Real computeRoughnessState() const override;
  Real computeCohesionEffective() const override;

  ADReal damageWeight(const ADReal & cumulative_slip) const;
  Real damageWeightReal(Real cumulative_slip) const;
  Real damageWeightDerivativeReal(Real cumulative_slip) const;
  ADReal weakeningWeight(const ADReal & cumulative_slip,
                         Real slip_distance,
                         Real exponent,
                         Real onset_slip = 0.0) const;
  Real weakeningWeightReal(Real cumulative_slip,
                           Real slip_distance,
                           Real exponent,
                           Real onset_slip = 0.0) const;
  Real weakeningWeightDerivativeReal(Real cumulative_slip,
                                     Real slip_distance,
                                     Real exponent,
                                     Real onset_slip = 0.0) const;
  ADReal frictionCoefficient(const ADReal & cumulative_slip) const;
  Real frictionCoefficientReal(Real cumulative_slip) const;
  Real frictionCoefficientDerivativeReal(Real cumulative_slip) const;
  Real roughnessWeightReal(Real cumulative_slip) const;
  ADReal dilationCoefficient(const ADReal & friction_coefficient) const;
  Real dilationCoefficientReal(Real friction_coefficient) const;
  Real evolveRateStateTheta(Real plastic_slip_increment) const;
  Real roughnessParameterWeight() const;
  Real roughnessScaledParameter(Real direct_value, Real smooth_value, Real rough_value) const;
  Real peakFrictionCoefficient() const;
  Real residualFrictionCoefficient() const;
  Real intermediateFrictionCoefficient() const;
  Real damageSlipDistance() const;
  Real fastDamageSlipDistance() const;
  Real slowDamageSlipDistance() const;
  Real dilationWorkFraction() const;
  Real dilationFrictionCoefficientFloor() const;
  Real maximumDilationCoefficient() const;

  const Real _peak_friction_coefficient;
  const Real _residual_friction_coefficient;
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
  const Real _dilation_work_fraction;
  const Real _dilation_friction_coefficient_floor;
  const Real _maximum_dilation_coefficient;
  const Real _apparent_cohesion;
  const Real _roughness_state_initial;
  const Real _roughness_state_residual;
  const bool _use_roughness_scaled_parameters;
  const Real _roughness_parameter_smooth_state;
  const Real _roughness_parameter_rough_state;
  const Real _roughness_parameter_exponent;
  const Real _smooth_peak_friction_coefficient;
  const Real _rough_peak_friction_coefficient;
  const Real _smooth_residual_friction_coefficient;
  const Real _rough_residual_friction_coefficient;
  const Real _smooth_intermediate_friction_coefficient;
  const Real _rough_intermediate_friction_coefficient;
  const Real _smooth_damage_slip_distance;
  const Real _rough_damage_slip_distance;
  const Real _smooth_fast_damage_slip_distance;
  const Real _rough_fast_damage_slip_distance;
  const Real _smooth_slow_damage_slip_distance;
  const Real _rough_slow_damage_slip_distance;
  const Real _smooth_dilation_work_fraction;
  const Real _rough_dilation_work_fraction;
  const Real _smooth_dilation_friction_coefficient_floor;
  const Real _rough_dilation_friction_coefficient_floor;
  const Real _smooth_maximum_dilation_coefficient;
  const Real _rough_maximum_dilation_coefficient;

  const bool _use_rate_and_state;
  const Real _rate_and_state_a;
  const Real _rate_and_state_b;
  const Real _rate_and_state_Dc;
  const Real _rate_and_state_V0;
  const Real _rate_and_state_theta0;
  // Clamp the referenced RSF term >= 0 so the slip-branch strength at V->0+ equals the stick
  // limit tl (continuous stick<->slip transition; cures the onset Newton limit cycle).
  const bool _rate_and_state_nonnegative;

  MaterialProperty<Real> & _rate_state_theta;
  const MaterialProperty<Real> & _rate_state_theta_old;
};
