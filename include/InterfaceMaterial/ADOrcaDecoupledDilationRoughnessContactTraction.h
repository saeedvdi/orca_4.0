#pragma once

#include "OrcaCZMComputeLocalTractionIncrementalBase.h"

/**
 * ADOrcaDecoupledDilationRoughnessContactTraction
 *
 * Stable roughness-damage Coulomb law with one targeted change:
 *   - friction/cohesion still evolve with roughness (or can be fixed by setting rough = smooth)
 *   - dilation evolves with its own independent decay law based on cumulative plastic slip
 *
 * This preserves the proven stable return mapping of the roughness model while decoupling
 * the dilation response from the strength response.
 *
 * Optional Duvaut-Lions/Perzyna tangential viscous (rate) regularization (tangential_viscosity,
 * default 0 = original rate-independent behavior) can be enabled to let a quasi-static Newton
 * solve traverse a stick->slip snap-through instability, using the same pattern already validated
 * in OrcaCZMMohrCoulombFriction and ADOrcaBartonBandisContactTractionFastAD.
 */
class ADOrcaDecoupledDilationRoughnessContactTraction
  : public OrcaCZMComputeLocalTractionIncrementalBase
{
public:
  static InputParameters validParams();

  ADOrcaDecoupledDilationRoughnessContactTraction(const InputParameters & parameters);

protected:
  virtual void initQpStatefulProperties() override;
  virtual void computeInterfaceTractionIncrement() override;

  enum class FractureState : unsigned int
  {
    Stick = 0,
    Slip = 2,
    Open = 3
  };

  void computeStrengthDependentProperties(const ADReal & roughness,
                                          ADReal & friction_eff,
                                          ADReal & cohesion_eff) const;

  void computeDilationDependentProperties(const ADReal & cumulative_plastic_slip,
                                          ADReal & dilation_state,
                                          ADReal & dilation_angle_deg_eff,
                                          ADReal & tan_dilation_eff) const;

  ADReal computeIrreversibleDilationTarget(const ADReal & cumulative_plastic_slip,
                                           const ADReal & dilation_support_factor) const;
  ADReal updateRoughness(const ADReal & roughness_old, const ADReal & plastic_slip_increment) const;
  ADReal updateStrengthNormalMemory(const ADReal & memory_old,
                                    const ADReal & traction_normal_current) const;
  ADReal computeDilationSupportFactor(const ADReal & strength_normal_memory) const;
  ADReal updateRetainedShearSupport(const ADReal & support_old,
                                    const ADReal & reference_support,
                                    const ADReal & plastic_slip_increment) const;
  void computeReversibleClosureState(const ADReal & normal_traction,
                                     const ADReal & cumulative_plastic_slip,
                                     const ADReal & dilation_opening_bound,
                                     ADReal & reversible_closure,
                                     ADReal & min_compression) const;

  const Real _penalty_normal;
  const Real _penalty_tangent;
  const Real _normal_traction_tolerance;
  const Real _tangential_traction_tolerance;

  const bool _use_dilatancy;
  const Real _tangential_viscosity;

  // Kinematic dilation routing. false (default) = legacy "dilation softens normal compression"
  // (the kinematic gap closes as the joint dilates). true = dilatant HARDENING: dilation is
  // routed into the joint opening so the kinematic normal jump (dn) physically opens by
  // ~tan(psi)*slip against the surrounding stiffness, as in a standard non-associated joint.
  const bool _dilation_opens_joint;
  const Real _dil_sign; // +1 legacy (softening), -1 kinematic (hardening -> opens the gap)

  // Roughness controls strength / hydraulic retention
  const Real _initial_roughness;
  const Real _residual_roughness;
  const Real _roughness_decay_distance;

  const Real _friction_coefficient_rough;
  const Real _friction_coefficient_smooth;
  const Real _friction_roughness_exponent;

  const Real _cohesion_rough;
  const Real _cohesion_smooth;
  const Real _cohesion_roughness_exponent;

  // Separate dilation evolution
  const Real _dilation_angle_peak_degrees;
  const Real _dilation_angle_residual_degrees;
  const Real _dilation_decay_distance;
  const Real _dilation_decay_exponent;
  const Real _dilation_support_reference;
  const Real _dilation_support_exponent;
  const Real _max_plastic_slip_increment;
  const Real _max_dilation_increment;
  const Real _normal_strength_retention_factor;
  const Real _retained_shear_support_factor;
  const Real _retained_shear_support_decay_distance;
  const bool _use_irreversible_dilation_target;
  const Real _max_irreversible_dilation;
  const Real _irreversible_dilation_distance;
  const Real _irreversible_dilation_exponent;
  const Real _reversible_closure_compliance;
  const Real _reversible_closure_activation_slip;
  const Real _max_reversible_closure;

  ADMaterialProperty<Real> & _fracture_state;
  ADMaterialProperty<Real> & _limit_tau;
  ADMaterialProperty<Real> & _plastic_slip_increment;
  ADMaterialProperty<Real> & _dilation_jump_increment;
  ADMaterialProperty<Real> & _cumulative_plastic_slip;
  const MaterialProperty<Real> & _cumulative_plastic_slip_old;

  ADMaterialProperty<Real> & _friction_coefficient_effective;
  ADMaterialProperty<Real> & _cohesion_effective;
  ADMaterialProperty<Real> & _dilation_angle_effective;
  ADMaterialProperty<Real> & _dilation_state;
  ADMaterialProperty<Real> & _dilation_support_factor;

  ADMaterialProperty<Real> & _roughness_state;
  const MaterialProperty<Real> & _roughness_state_old;
  ADMaterialProperty<Real> & _roughness_damage;
  ADMaterialProperty<Real> & _strength_normal_memory;
  const MaterialProperty<Real> & _strength_normal_memory_old;
  ADMaterialProperty<Real> & _retained_shear_support;
  const MaterialProperty<Real> & _retained_shear_support_old;
  ADMaterialProperty<Real> & _irreversible_dilation;
  const MaterialProperty<Real> & _irreversible_dilation_old;
  ADMaterialProperty<Real> & _reversible_closure;
  const MaterialProperty<Real> & _reversible_closure_old;
  ADMaterialProperty<Real> & _reversible_closure_min_compression;
  const MaterialProperty<Real> & _reversible_closure_min_compression_old;

  ADMaterialProperty<RealVectorValue> & _plastic_tangential_jump;
  const MaterialProperty<RealVectorValue> & _plastic_tangential_jump_old;
};
