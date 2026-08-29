#pragma once

#include "InterfaceMaterial.h"

/**
 * ADOrcaRoughnessDamageFracturePermeability
 *
 * Hydraulic aperture / permeability model coupled to roughness damage.
 *
 * Concept:
 *   a_h = a_h0
 *       + normal_compliance * (N_ref - N_eff)
 *       + aperture_scale * a_mech
 *       + dilation_scale * cumulative_dilation * retention_factor(R)
 *       + self_propping_scale * R^m_sp
 *       - slip_damage_scale * (1 - exp(-cumulative_plastic_slip / slip_damage_characteristic_slip))
 *       - closure_creep_aperture(t)   [OPT-IN, see below]
 *
 * where R is the roughness state from the coupled contact material, for example
 * ADOrcaBartonBandisContactTractionFastADHardening.
 * This lets rough fractures retain more hydraulic opening than smooth/degraded ones.
 *
 * The optional slip-damage (gouge-fill) term (use_slip_damage=true) subtracts a
 * shear-driven aperture reduction that saturates with cumulative plastic slip: as the
 * joint shears, wear/gouge progressively fills the void space, so the HYDRAULIC aperture
 * stops tracking the sigma'_n-driven mechanical re-opening 1:1. This decouples the
 * reported permeability from the closure (effective-stress) response without changing the
 * baseline (the term is zero at zero slip).
 *
 * The optional closure-creep term (use_closure_creep=true) is the ONLY term in this budget
 * that advances with time alone. Every other term is a function of the current effective
 * normal stress, the current mechanical gap, or a history variable that is monotone in slip,
 * so a joint held at constant pressure is stationary to machine precision and a long-hold
 * experiment returns a flat line by construction. The creep term supplies the missing
 * time scale -- pressure solution / asperity indentation closing a loaded joint at constant
 * stress over 1e5-1e7 s:
 *
 *   da_c/dt = (1/closure_creep_time) * (<N_eff>_+ / closure_creep_reference_stress)^q
 *             * (closure_creep_max_aperture - a_c),   a_c(0) = 0
 *
 * Like the gouge-fill it is HYDRAULIC only: it subtracts from a_h and does not feed back on
 * the traction, so it models the loss of connected void space rather than a mechanical
 * convergence of the two surfaces. Default off, in which case a_c is identically zero.
 */
class ADOrcaRoughnessDamageFracturePermeability : public InterfaceMaterial
{
public:
  static InputParameters validParams();

  ADOrcaRoughnessDamageFracturePermeability(const InputParameters & parameters);

protected:
  virtual void initQpStatefulProperties() override;
  virtual void computeQpProperties() override;

  /// Reversible ("backbone") normal-stress aperture opening as a function of the compression-positive
  /// effective normal stress. Subclasses override this to add path-dependence (e.g. hysteresis) and
  /// call the base implementation as the single-path backbone.
  virtual ADReal computeStressAperture(const ADReal & effective_normal_compression);

  const std::string _base_name;

  // --- inputs ---
  const ADMaterialProperty<Real> & _mechanical_aperture;
  // Optional: only coupled when NOT in kinematic mode. In kinematic mode the dilation lives in
  // the mechanical gap and roughness retention is unused, so these contact-material interface
  // properties are not required -- which lets the model pair with contact laws (e.g.
  // OrcaCZMMohrCoulombFriction) that do not export roughness_state / dilation_jump_increment.
  const ADMaterialProperty<Real> * const _dilation_jump_increment;
  const ADMaterialProperty<Real> * const _roughness_state;
  // Cumulative plastic (shear) slip from the contact material. The gouge-fill uses its raw value
  // explicitly. Exactly one of these two is non-null when use_slip_damage is on, selected by
  // cumulative_plastic_slip_is_ad (AD laws, e.g. the decoupled family, vs non-AD FastAD BB laws).
  const ADMaterialProperty<Real> * const _cumulative_plastic_slip;
  const MaterialProperty<Real> * const _cumulative_plastic_slip_nonad;
  const ADMaterialProperty<Real> * const _effective_normal_traction;

  // --- outputs / stateful ---
  ADMaterialProperty<Real> & _cumulative_dilation;
  const MaterialProperty<Real> & _cumulative_dilation_old;
  /// Accumulated time-dependent closure creep (m). Stateful: integrated implicitly from its
  /// own old value each step. Identically zero unless use_closure_creep is set.
  ADMaterialProperty<Real> & _closure_creep_aperture;
  const MaterialProperty<Real> & _closure_creep_aperture_old;
  ADMaterialProperty<Real> & _hydraulic_aperture;
  ADMaterialProperty<Real> & _fracture_permeability;
  ADMaterialProperty<Real> * _transmissivity;
  ADMaterialProperty<Real> & _roughness_retention_factor;
  ADMaterialProperty<Real> & _self_propping_aperture;
  ADMaterialProperty<Real> & _slip_damage_aperture; // diagnostic: gouge-fill reduction (m)
  ADMaterialProperty<Real> & _normal_stress_aperture; // diagnostic: reversible closure/opening term (m)
  ADMaterialProperty<Real> & _effective_normal_compression; // diagnostic: compression-positive (Pa)

  // --- parameters ---
  const Real _a_h0;
  const Real _aperture_scale;
  const Real _normal_stress_aperture_compliance;
  const Real _reference_effective_normal_stress;
  // Optional Barton-Bandis hyperbolic replacement for the linear normal-stress aperture term.
  const bool _use_nonlinear_normal_closure;
  const bool _compute_effective_normal_compression;
  const unsigned int _nonlinear_closure_type; // 0 = barton_bandis, 1 = exponential
  const Real _bb_max_aperture_closure;     // V_m: asymptotic reversible aperture range (m)
  const Real _bb_initial_normal_stiffness; // K_ni: sigma_0 = V_m*K_ni is the half-closure stress (Pa/m)
  const Real _bb_stress_exponent;          // p: power-law exponent on the closure fraction
  const Real _exp_closure_amplitude;       // A: opening at N = exp_closure_reference_stress (m)
  const Real _exp_closure_stress_scale;    // sigma_c: e-folding normal stress (Pa)
  const Real _exp_closure_reference_stress; // N_ref: stress where opening = A (Pa)
  const Real _dilation_scale;
  // OPT-IN (default false): pair with dilation_opens_joint=true in the contact material.
  // When true, the accumulated dilation already lives in the mechanical gap (it was routed
  // into the displacement field), so feeding it AGAIN here via dilation_scale would double
  // count it and over-predict permeability. With use_kinematic_aperture=true the dilation
  // term is dropped and the hydraulic aperture is the physical mechanical gap only:
  //     a_h = a_h0 + aperture_scale * mechanical_aperture (+ self-propping)
  const bool _use_kinematic_aperture;
  const Real _min_aperture;
  const Real _max_aperture; // upper bound on hydraulic aperture (m); 0 disables
  const Real _retention_residual;
  const Real _self_propping_scale;
  const Real _self_propping_exponent;
  const bool _compute_transmissivity;
  const Real _fluid_viscosity;
  const Real _fault_thickness;

  // --- slip-damage (gouge-fill) aperture reduction ---
  const bool _use_slip_damage;
  const Real _slip_damage_scale;       // max gouge-fill aperture reduction (m)
  const Real _slip_damage_char_slip;   // characteristic cumulative slip for saturation (m)
  const Real _slip_damage_onset_slip;  // cumulative-slip threshold s* below which no gouge accrues (m)

  // ---- Time-dependent closure creep (OPT-IN; default false = legacy, bit-identical) ----
  const bool _use_closure_creep;
  const Real _closure_creep_max_aperture;      // asymptotic creep closure a_c_max (m)
  const Real _closure_creep_time;              // tau_c at the reference stress (s)
  const Real _closure_creep_reference_stress;  // sigma_ref in the rate law (Pa)
  const Real _closure_creep_stress_exponent;   // q in rate ~ (N_eff/sigma_ref)^q
};
