#pragma once

#include "OrcaCZMComputeLocalTractionIncrementalBase.h"

#include <cmath>
#include <vector>

namespace OrcaCompressionTensile
{
template <typename T>
T
normalizedResidualRoughness(const T & roughness, const Real residual_roughness)
{
  return (roughness - T(residual_roughness)) / T(1.0 - residual_roughness);
}

template <typename T>
T
roughnessPowerInterpolation(const T & roughness,
                            const Real residual_roughness,
                            const Real rough_value,
                            const Real smooth_value,
                            const Real exponent)
{
  using std::pow;

  const T normalized_roughness = normalizedResidualRoughness(roughness, residual_roughness);
  return T(smooth_value) + T(rough_value - smooth_value) * pow(normalized_roughness, T(exponent));
}
}

/**
 * Cohesive-contact-friction composite interface law.
 *
 * Local sign convention:
 *   g_n > 0 : opening
 *   t_n > 0 : tension
 *   t_n < 0 : compression
 *
 * The interface is treated as a parallel mixture of an intact cohesive area fraction (1-d) and a
 * damaged frictional/contact area fraction d. Normal contact is unilateral and based on the total
 * effective overlap p = K_n <g_n^p - g_n>_+. Tangential traction is the continuous mixture
 * (1-d) K_t^coh g_t + d K_t (g_t - g_t^p). The active-set transitions are semismooth; centered
 * finite-difference tangent checks should avoid evaluating exactly on those event surfaces.
 */
class ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile final
  : public OrcaCZMComputeLocalTractionIncrementalBase
{
public:
  static InputParameters validParams();

  ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile(
      const InputParameters & parameters);

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

  struct LocalState
  {
    ADReal cumulative_plastic_slip;
    ADReal plastic_slip_increment;
    ADReal dilation_jump_increment;

    ADReal roughness;
    ADReal roughness_damage;
    ADReal friction;
    ADReal cohesion;
    ADReal dilation_angle_deg;
    ADReal dilation_state;
    ADReal dilation_support;

    ADReal normal_pressure_memory;
    ADReal retained_shear_support;
    ADReal normal_plastic_jump;
    ADReal irreversible_dilation;
    ADReal normal_contact_pressure;
    ADReal limit_tau;
    ADReal rate_state_theta;   // rate-and-state state variable theta [s] (carried between steps)

    ADReal cohesive_damage;
    ADReal cohesive_history;
    ADReal cohesive_damage_target;

    ADReal frictional_sliding_work_increment;
    ADReal dilation_work_increment;
    ADReal frictional_dilatant_dissipation_increment;
    ADReal cohesive_dissipation_increment;

    ADRealVectorValue plastic_tangential_jump;
    ADRealVectorValue traction;
    FractureState fracture_state;
  };

  struct CohesiveState
  {
    ADReal equivalent_separation;
    ADReal history;
    ADReal damage_target;
    ADReal damage;
    ADReal normal_traction;
    ADReal shear_scale;
    ADReal dissipation_increment;
  };

  struct FrictionEvaluation
  {
    ADReal residual;
    ADReal dilation_residual;

    // Exact local partial derivatives with respect to gamma and g_np.
    ADReal dres_dgamma;
    ADReal dres_dgnp;
    ADReal ddil_dgamma;
    ADReal ddil_dgnp;

    ADReal roughness;
    ADReal friction;
    ADReal cohesion;
    ADReal cumulative_slip;
    ADReal dilation_state;
    ADReal dilation_angle_deg;
    ADReal dilation_slope;
    ADReal dilation_support;
    ADReal normal_pressure;
    ADReal normal_pressure_memory;
    ADReal raw_strength;
    ADReal retained_strength;
    ADReal strength;
    ADReal rate_state_theta;   // evolved theta (aging law) for storage to the next step
    ADReal normal_plastic_jump;
    ADReal raw_dilation_increment;
    ADReal dilation_increment;
    ADReal frictional_sliding_work;
    ADReal dilation_work;
    ADReal frictional_dilatant_dissipation;
  };

  ADReal smoothPositive(const ADReal & x, Real eps) const;
  ADReal smoothPositiveDerivative(const ADReal & x, Real eps) const;
  ADReal smoothMaximum(const ADReal & a, const ADReal & b, Real eps) const;
  ADReal smoothMaximumWeightA(const ADReal & a, const ADReal & b, Real eps) const;

  LocalState oldLocalState() const;
  void storeFinalState(const LocalState & state);

  Real rawEquivalentSeparation(const RealVectorValue & jump) const;
  Real locateEquivalentSeparationEvent(const RealVectorValue & jump_start,
                                       const RealVectorValue & jump_end,
                                       Real threshold) const;
  std::vector<Real> collectEventFractions(const LocalState & old_state,
                                          const RealVectorValue & jump_start,
                                          const RealVectorValue & jump_end) const;

  CohesiveState updateCohesiveState(const ADRealVectorValue & jump,
                                    const LocalState & old_state,
                                    Real substep_fraction) const;
  ADReal cohesiveDamageFromHistory(const ADReal & history) const;
  ADReal cohesiveDissipation(const ADReal & history) const;

  void strengthFromRoughness(const ADReal & roughness,
                             ADReal & friction,
                             ADReal & cohesion,
                             ADReal & dfriction_dgamma,
                             ADReal & dcohesion_dgamma,
                             const ADReal & droughness_dgamma) const;

  void dilationFromSlip(const ADReal & cumulative_slip,
                        ADReal & state,
                        ADReal & angle_deg,
                        ADReal & slope,
                        ADReal & dslope_dgamma) const;

  void
  dilationSupport(const ADReal & pressure, ADReal & support, ADReal & dsupport_dpressure) const;

  void normalPressureMemory(const ADReal & pressure,
                            const ADReal & current_normal_jump,
                            const ADReal & previous_normal_jump,
                            const ADReal & old_memory,
                            ADReal & memory,
                            ADReal & dmemory_dpressure) const;

  ADReal dilationTarget(const ADReal & cumulative_slip) const;
  ADReal dilationTargetDerivative(const ADReal & cumulative_slip) const;

  FrictionEvaluation evaluateFriction(const ADReal & gamma,
                                      const ADReal & normal_plastic_jump,
                                      const ADReal & tau_trial,
                                      const ADReal & current_normal_jump,
                                      const ADReal & previous_normal_jump,
                                      const LocalState & old_state,
                                      const ADReal & damage_fraction,
                                      Real substep_fraction) const;

  void storeFrictionHistory(LocalState & state,
                            const LocalState & old_state,
                            const FrictionEvaluation & friction,
                            const ADReal & gamma,
                            const ADReal & normal_plastic_increment) const;

  bool updateSubstep(const LocalState & old_state,
                     const ADRealVectorValue & jump_start,
                     const ADRealVectorValue & jump_end,
                     Real substep_fraction,
                     LocalState & new_state) const;
  bool advanceSubstep(LocalState & state,
                      const ADRealVectorValue & global_jump_start,
                      const ADRealVectorValue & global_jump_end,
                      Real fraction_start,
                      Real fraction_end,
                      unsigned int depth) const;

  // Material parameters
  const Real _penalty_normal;
  const Real _penalty_tangent;
  const bool _use_hyperbolic_normal_closure;
  const Real _initial_normal_stiffness;
  const Real _maximum_closure;
  const Real _maximum_closure_fraction;
  const Real _normal_closure_stress_exponent;
  const Real _normal_closure_offset;
  const Real _normal_traction_tolerance_legacy;
  const Real _tangential_traction_tolerance;
  const Real _opening_gap_tolerance;
  const Real _return_mapping_stiffness_tolerance;
  const Real _local_newton_stress_tolerance;
  const Real _local_newton_gap_tolerance;
  const unsigned int _max_local_newton_iterations;
  const unsigned int _max_local_substeps;
  const Real _event_fraction_tolerance;
  const Real _contact_gap_regularization;
  const Real _stress_regularization;

  const bool _enable_tensile_cohesion;
  const Real _cohesive_peak_traction;
  const Real _cohesive_initial_separation;
  const Real _cohesive_final_separation;
  const Real _cohesive_shear_weight;
  const Real _cohesive_damage_viscosity;
  const Real _cohesive_failure_tolerance;
  const Real _cohesive_gap_regularization;

  const bool _use_dilatancy;
  const bool _dilation_opens_joint;
  const bool _use_normal_memory_for_dilation_support;
  const Real _tangential_viscosity;
  const Real _dissipation_margin;

  const Real _initial_roughness;
  const Real _residual_roughness;
  const Real _roughness_decay_distance;
  const Real _friction_coefficient_rough;
  const Real _friction_coefficient_smooth;
  const Real _friction_roughness_exponent;
  const Real _cohesion_rough;
  const Real _cohesion_smooth;
  const Real _cohesion_roughness_exponent;

  // Secondary (large-slip) weakening stage: an additional strength loss dS that switches on once the
  // accumulated plastic slip passes secondary_weakening_onset_slip, over distance
  // secondary_weakening_distance. Captures the sharp "gradual then sudden" drop; default dS=0 disables.
  const Real _secondary_weakening_strength;
  const Real _secondary_weakening_onset_slip;
  const Real _secondary_weakening_distance;

  const Real _dilation_angle_peak_degrees;
  const Real _dilation_angle_residual_degrees;
  const Real _dilation_decay_distance;
  const Real _dilation_decay_exponent;
  const Real _dilation_support_reference;
  const Real _dilation_support_exponent;
  const Real _dilation_high_normal_reference;
  const Real _dilation_high_normal_exponent;

  const bool _use_irreversible_dilation_target;
  const Real _max_irreversible_dilation;
  const Real _irreversible_dilation_distance;
  const Real _irreversible_dilation_exponent;

  const Real _normal_strength_retention_factor;
  const Real _normal_strength_memory_decay_distance;
  const Real _retained_shear_support_factor;
  const Real _retained_shear_support_decay_distance;

  // Reversible (elastic) joint-normal compliance. Decoupled: computed from the converged effective
  // normal stress, added to the REPORTED normal opening only (not fed into the residual/Jacobian).
  // Default 0 disables the term, leaving all existing behavior byte-identical.
  const Real _reversible_normal_compliance;
  const Real _reversible_normal_reference_stress;
  // Output-only activation gate for reversible opening. When the onset is positive,
  // elastic opening is suppressed until plastic slip begins, then smoothly approaches
  // the stress-derived value over the specified slip distance.
  const Real _reversible_normal_opening_activation_slip;
  const Real _reversible_normal_opening_activation_distance;
  const Real _reversible_normal_opening_activation_exponent;
  // Fraction of the largest reversible opening retained during subsequent normal
  // reclosure. This is output-only hysteresis: it changes the reported joint opening,
  // not the contact residual or the hydraulic aperture.
  const Real _reversible_normal_opening_retention_fraction;
  const Real _reversible_normal_opening_retention_activation_slip;

  // Rate-and-state friction (regularized, additive to the roughness strength). Default off:
  // use_rate_and_state=false / a=0 makes the term vanish, leaving existing behavior byte-identical.
  // Strength += p * a * asinh[ (V/(2 V0)) * (V0*theta_old/Dc)^(b/a) ], V = gamma/dt (slip rate);
  // theta evolves by the aging law dtheta/dt = 1 - V*theta/Dc (state healing / memory).
  const bool _use_rate_and_state;
  const Real _rate_and_state_a;
  const Real _rate_and_state_b;
  const Real _rate_and_state_Dc;
  const Real _rate_and_state_V0;
  const Real _rate_and_state_theta0;
  // Clamp the referenced RSF term >= 0 so the slip-branch strength at V->0+ equals the stick
  // limit (continuous stick<->slip transition; cures the onset/re-stick Newton limit cycle).
  const bool _rate_and_state_nonnegative;

  // Stateful and output properties
  ADMaterialProperty<Real> & _fracture_state;
  ADMaterialProperty<Real> & _limit_tau;
  ADMaterialProperty<Real> & _plastic_slip_increment;
  ADMaterialProperty<Real> & _dilation_jump_increment;
  ADMaterialProperty<Real> & _cumulative_plastic_slip;
  const MaterialProperty<Real> & _cumulative_plastic_slip_old;

  ADMaterialProperty<Real> & _roughness_state;
  const MaterialProperty<Real> & _roughness_state_old;
  ADMaterialProperty<Real> & _roughness_damage;
  ADMaterialProperty<Real> & _friction_coefficient_effective;
  ADMaterialProperty<Real> & _cohesion_effective;
  ADMaterialProperty<Real> & _dilation_angle_effective;
  ADMaterialProperty<Real> & _dilation_state;
  ADMaterialProperty<Real> & _dilation_support_factor;

  ADMaterialProperty<Real> & _strength_normal_memory_magnitude;
  const MaterialProperty<Real> & _strength_normal_memory_magnitude_old;
  ADMaterialProperty<Real> & _strength_normal_memory;
  ADMaterialProperty<Real> & _retained_shear_support;
  const MaterialProperty<Real> & _retained_shear_support_old;

  ADMaterialProperty<Real> & _normal_plastic_jump;
  const MaterialProperty<Real> & _normal_plastic_jump_old;
  ADMaterialProperty<Real> & _irreversible_dilation;
  ADMaterialProperty<Real> & _normal_contact_pressure;

  // Reversible elastic normal opening d_rev, and the reported total normal opening
  // (irreversible g_np + reversible d_rev). Output-only diagnostics.
  ADMaterialProperty<Real> & _reversible_normal_opening;
  ADMaterialProperty<Real> & _normal_opening_total;
  ADMaterialProperty<Real> & _maximum_reversible_normal_opening;
  const MaterialProperty<Real> & _maximum_reversible_normal_opening_old;

  // Rate-and-state theta (stateful): carries the state variable between steps.
  ADMaterialProperty<Real> & _rate_state_theta;
  const MaterialProperty<Real> & _rate_state_theta_old;

  ADMaterialProperty<Real> & _frictional_sliding_work_increment;
  ADMaterialProperty<Real> & _dilation_work_increment;
  ADMaterialProperty<Real> & _frictional_dilatant_dissipation_increment;
  ADMaterialProperty<Real> & _cohesive_dissipation_increment;

  ADMaterialProperty<RealVectorValue> & _plastic_tangential_jump;
  const MaterialProperty<RealVectorValue> & _plastic_tangential_jump_old;

  ADMaterialProperty<Real> & _cohesive_damage;
  const MaterialProperty<Real> & _cohesive_damage_old;
  ADMaterialProperty<Real> & _cohesive_history;
  const MaterialProperty<Real> & _cohesive_history_old;
  ADMaterialProperty<Real> & _cohesive_damage_target;
};
