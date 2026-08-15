#include "ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile.h"
#include "OrcaNormalClosure.h"

#include "MooseException.h"
#include "metaphysicl/raw_type.h"

#include <algorithm>
#include <cmath>
#include <limits>
#include <vector>

using std::exp;
using std::pow;
using std::sqrt;
using std::tan;

registerMooseObject("OrcaApp", ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile);
registerMooseObjectAliased("OrcaApp",
                           ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile,
                           "ADOrcaDecoupledMCRoughnessDilationContactTraction");

namespace
{
constexpr Real orca_pi = 3.141592653589793238462643383279502884;
}

InputParameters
ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile::validParams()
{
  InputParameters params = OrcaCZMComputeLocalTractionIncrementalBase::validParams();

  params.addClassDescription(
      "Cohesive-contact-friction composite interface law. A bilinear mixed-mode cohesive "
      "branch carries the intact area fraction, unilateral contact carries compression, and a "
      "roughness-dependent Coulomb return map carries the damaged frictional area fraction. "
      "The local friction-dilation update is solved in gamma and irreversible normal opening "
      "with event-aware local substepping.");

  params.addParam<std::string>("base_name", "Material property base name");

  params.addRangeCheckedParam<Real>(
      "penalty_normal", "penalty_normal > 0.0", "Contact normal stiffness K_n [Pa/m].");
  params.addRangeCheckedParam<Real>(
      "penalty_tangent",
      0.0,
      "penalty_tangent >= 0.0",
      "Contact tangential stiffness K_t [Pa/m]. A value of zero uses penalty_normal.");
  params.addParam<bool>(
      "use_hyperbolic_normal_closure",
      false,
      "Use the pre-seated recoverable power-law Barton--Bandis mechanical normal response. "
      "False preserves the legacy linear penalty law exactly.");
  params.addRangeCheckedParam<Real>("initial_normal_stiffness",
                                    1e13,
                                    "initial_normal_stiffness > 0.0",
                                    "Initial stiffness K_ni [Pa/m] of the power-law closure.");
  params.addRangeCheckedParam<Real>("maximum_closure",
                                    1e-4,
                                    "maximum_closure > 0.0",
                                    "Maximum mechanical closure V_m [m].");
  params.addRangeCheckedParam<Real>("maximum_closure_fraction",
                                    0.999,
                                    "maximum_closure_fraction > 0.0 & maximum_closure_fraction < 1.0",
                                    "Numerical cap on mechanical closure/V_m.");
  params.addRangeCheckedParam<Real>("normal_closure_stress_exponent",
                                    1.0,
                                    "normal_closure_stress_exponent >= 1.0",
                                    "Power-law closure stress exponent p.");
  params.addRangeCheckedParam<Real>(
      "normal_closure_offset",
      0.0,
      "normal_closure_offset >= 0.0",
      "Pre-seating closure c0 [m], so a zero displacement jump may carry the in-situ preload.");

  params.addRangeCheckedParam<Real>(
      "normal_traction_tolerance",
      0.0,
      "normal_traction_tolerance >= 0.0",
      "DEPRECATED legacy traction tolerance [Pa]. It must remain zero in the revised model; "
      "opening is controlled by opening_gap_tolerance [m].");
  params.addRangeCheckedParam<Real>(
      "tangential_traction_tolerance",
      1e-12,
      "tangential_traction_tolerance >= 0.0",
      "Tangential traction norm tolerance [Pa] used only to avoid defining a slip direction "
      "at zero shear.");
  params.addRangeCheckedParam<Real>(
      "opening_gap_tolerance",
      0.0,
      "opening_gap_tolerance >= 0.0",
      "Gap tolerance [m] for the semismooth active-set contact/open decision.");
  params.addRangeCheckedParam<Real>(
      "return_mapping_stiffness_tolerance",
      1e-12,
      "return_mapping_stiffness_tolerance > 0.0",
      "Minimum admissible determinant magnitude in the local Newton solve [Pa/m].");
  params.addRangeCheckedParam<Real>("local_newton_stress_tolerance",
                                    1e-8,
                                    "local_newton_stress_tolerance > 0.0",
                                    "Absolute local yield-residual tolerance [Pa].");
  params.addRangeCheckedParam<Real>("local_newton_gap_tolerance",
                                    1e-14,
                                    "local_newton_gap_tolerance > 0.0",
                                    "Absolute local normal-plastic-jump residual tolerance [m].");
  params.addRangeCheckedParam<unsigned int>(
      "max_local_newton_iterations",
      30,
      "max_local_newton_iterations > 0",
      "Maximum iterations for each local friction-dilation return map.");
  params.addRangeCheckedParam<unsigned int>(
      "max_local_substeps",
      32,
      "max_local_substeps > 0",
      "Maximum bisection depth used by event-aware material substepping.");
  params.addRangeCheckedParam<Real>(
      "event_fraction_tolerance",
      1e-10,
      "event_fraction_tolerance > 0.0",
      "Fraction tolerance for merging local substep events on the displacement-jump path.");
  params.addRangeCheckedParam<Real>(
      "contact_gap_regularization",
      1e-14,
      "contact_gap_regularization > 0.0",
      "Smooth-positive regularization length [m] used inside closed-contact local solves and "
      "for the smooth irreversible-target maximum.");
  params.addRangeCheckedParam<Real>(
      "stress_regularization",
      1e-8,
      "stress_regularization > 0.0",
      "Smooth-maximum regularization stress [Pa] for strength-memory, retained-support, and "
      "dissipation-limit denominators.");

  params.addParam<bool>(
      "enable_tensile_cohesion",
      false,
      "Enable the bilinear mixed-mode cohesive branch. False initializes the interface fully "
      "damaged and reproduces a pre-existing frictional joint/fault.");
  params.addRangeCheckedParam<Real>("cohesive_peak_traction",
                                    0.0,
                                    "cohesive_peak_traction >= 0.0",
                                    "Peak effective cohesive traction T0 [Pa]. Required and >0 "
                                    "when tensile cohesion is enabled.");
  params.addRangeCheckedParam<Real>(
      "cohesive_initial_separation",
      0.0,
      "cohesive_initial_separation >= 0.0",
      "Effective separation delta_0 [m] at cohesive damage initiation. Required and >0 when "
      "tensile cohesion is enabled.");
  params.addRangeCheckedParam<Real>(
      "cohesive_final_separation",
      0.0,
      "cohesive_final_separation >= 0.0",
      "Effective separation delta_f [m] at complete cohesive failure. Required and greater "
      "than cohesive_initial_separation when tensile cohesion is enabled.");
  params.addRangeCheckedParam<Real>(
      "cohesive_shear_weight",
      1.0,
      "cohesive_shear_weight > 0.0",
      "Dimensionless mixed-mode separation weight beta_c. Equivalent separation is "
      "sqrt(<g_n>_+^2 + beta_c^2 ||g_t||^2).");
  params.addRangeCheckedParam<Real>(
      "cohesive_damage_viscosity",
      0.0,
      "cohesive_damage_viscosity >= 0.0",
      "Duvaut-Lions damage relaxation time [s]. Zero gives rate-independent cohesive damage.");
  params.addRangeCheckedParam<Real>(
      "cohesive_failure_tolerance",
      1e-10,
      "cohesive_failure_tolerance > 0.0",
      "DEPRECATED compatibility tolerance. The revised mixture law does not use a hard "
      "cohesive-to-frictional switch.");
  params.addRangeCheckedParam<Real>(
      "cohesive_gap_regularization",
      1e-14,
      "cohesive_gap_regularization > 0.0",
      "Smooth-positive regularization length [m] for the cohesive effective separation.");

  params.addParam<bool>(
      "use_dilatancy", true, "Enable irreversible shear-induced normal plastic opening.");
  params.addParam<bool>(
      "dilation_opens_joint",
      true,
      "Must be true in the revised model. Positive plastic slip produces positive irreversible "
      "normal opening.");
  params.addParam<bool>(
      "use_normal_memory_for_dilation_support",
      false,
      "Use pressure memory rather than current contact pressure in the dilation support factor. "
      "Default false keeps geometric dilation tied to current contact pressure.");
  params.addRangeCheckedParam<Real>(
      "tangential_viscosity",
      0.0,
      "tangential_viscosity >= 0.0",
      "Frictional overstress viscosity eta_t [Pa.s/m]. The slip residual includes "
      "eta_t*delta_gamma/dt.");
  params.addRangeCheckedParam<Real>(
      "dissipation_margin",
      1e-8,
      "dissipation_margin >= 0.0 & dissipation_margin < 1.0",
      "Margin epsilon_D in p*Delta g_np <= (1-epsilon_D)*tau*Delta gamma.");

  params.addRangeCheckedParam<Real>("initial_roughness",
                                    1.0,
                                    "initial_roughness >= 0.0 & initial_roughness <= 1.0",
                                    "Initial normalized roughness R0 [-].");
  params.addRangeCheckedParam<Real>("residual_roughness",
                                    0.2,
                                    "residual_roughness >= 0.0 & residual_roughness <= 1.0",
                                    "Residual normalized roughness Rr [-]. Must be < 1.");
  params.addRangeCheckedParam<Real>("roughness_decay_distance",
                                    1e-5,
                                    "roughness_decay_distance > 0.0",
                                    "Roughness degradation distance L_R [m].");
  params.addRangeCheckedParam<Real>("friction_coefficient_rough",
                                    0.6,
                                    "friction_coefficient_rough >= 0.0",
                                    "Friction coefficient at R=1 [-].");
  params.addRangeCheckedParam<Real>("friction_coefficient_smooth",
                                    0.4,
                                    "friction_coefficient_smooth >= 0.0",
                                    "Friction coefficient at R=Rr [-].");
  params.addRangeCheckedParam<Real>("friction_roughness_exponent",
                                    1.0,
                                    "friction_roughness_exponent >= 1.0",
                                    "Exponent in mu(Rbar); >=1 avoids a singular derivative.");
  // Frictional Coulomb shear-strength intercept at R=1 / R=Rr [Pa]. This is the intercept of the
  // frictional strength envelope tau = c + mu*sigma_n, NOT a tensile strength (the tensile branch is
  // governed by cohesive_peak_traction, which must be >= 0). A NEGATIVE intercept is admissible: it
  // is the standard linearization of a curved (Barton-Bandis) shear-strength envelope fitted over a
  // finite normal-stress range, equivalent to a threshold normal stress below which the joint has no
  // shear strength. The strength is floored at zero internally so a negative intercept never yields a
  // negative yield stress.
  params.addParam<Real>("cohesion_rough", 0.0, "Coulomb shear-strength intercept at R=1 [Pa].");
  params.addParam<Real>("cohesion_smooth", 0.0, "Coulomb shear-strength intercept at R=Rr [Pa].");
  params.addRangeCheckedParam<Real>("cohesion_roughness_exponent",
                                    1.0,
                                    "cohesion_roughness_exponent >= 1.0",
                                    "Exponent in c(Rbar); >=1 avoids a singular derivative.");

  params.addRangeCheckedParam<Real>(
      "secondary_weakening_strength", 0.0, "secondary_weakening_strength >= 0.0",
      "Magnitude dS [Pa] of an additional, large-slip strength loss applied on TOP of the roughness "
      "weakening: strength -= dS*(1 - exp(-<s - s*>/w)), s = accumulated plastic slip. Models the sharp "
      "'gradual then sudden' drop (e.g. asperity/cohesion collapse near peak injection). Irreversible "
      "(keyed on cumulative slip) so the residual stays low. Default 0 disables (behavior byte-identical).");
  params.addRangeCheckedParam<Real>(
      "secondary_weakening_onset_slip", 0.0, "secondary_weakening_onset_slip >= 0.0",
      "Accumulated-plastic-slip threshold s* [m] at which the secondary weakening switches on. Sets the "
      "TIMING of the drop. Only used when secondary_weakening_strength > 0.");
  params.addRangeCheckedParam<Real>(
      "secondary_weakening_distance", 1.0e-5, "secondary_weakening_distance > 0.0",
      "Slip distance w [m] over which the secondary drop develops past s*. Sets the SHARPNESS (smaller = "
      "steeper cliff). Only used when secondary_weakening_strength > 0.");

  params.addRangeCheckedParam<Real>("dilation_angle_peak_degrees",
                                    2.0,
                                    "dilation_angle_peak_degrees >= 0.0 & "
                                    "dilation_angle_peak_degrees < 89.9",
                                    "Peak dilation angle psi_p [degrees].");
  params.addRangeCheckedParam<Real>("dilation_angle_residual_degrees",
                                    0.0,
                                    "dilation_angle_residual_degrees >= 0.0 & "
                                    "dilation_angle_residual_degrees < 89.9",
                                    "Residual dilation angle psi_r [degrees].");
  params.addRangeCheckedParam<Real>("dilation_decay_distance",
                                    1e-4,
                                    "dilation_decay_distance > 0.0",
                                    "Dilation decay distance L_psi [m].");
  params.addRangeCheckedParam<Real>("dilation_decay_exponent",
                                    1.0,
                                    "dilation_decay_exponent >= 1.0",
                                    "Dilation decay exponent m_psi.");
  params.addRangeCheckedParam<Real>(
      "dilation_support_reference",
      0.0,
      "dilation_support_reference >= 0.0",
      "Low-normal-pressure support scale sigma_low [Pa]. Zero disables low-pressure suppression.");
  params.addRangeCheckedParam<Real>("dilation_support_exponent",
                                    1.0,
                                    "dilation_support_exponent >= 1.0",
                                    "Low-normal-pressure support exponent.");
  params.addRangeCheckedParam<Real>("dilation_high_normal_reference",
                                    0.0,
                                    "dilation_high_normal_reference >= 0.0",
                                    "High-normal-pressure crushing scale sigma_high [Pa]. Zero "
                                    "disables high-pressure suppression.");
  params.addRangeCheckedParam<Real>("dilation_high_normal_exponent",
                                    1.0,
                                    "dilation_high_normal_exponent >= 1.0",
                                    "High-normal-pressure suppression exponent.");

  params.addParam<bool>(
      "use_irreversible_dilation_target",
      false,
      "Use a support-modulated cumulative-slip target for irreversible dilation.");
  params.addRangeCheckedParam<Real>("max_irreversible_dilation",
                                    0.0,
                                    "max_irreversible_dilation >= 0.0",
                                    "Asymptotic irreversible normal opening d_max [m].");
  params.addRangeCheckedParam<Real>("irreversible_dilation_distance",
                                    1e-4,
                                    "irreversible_dilation_distance > 0.0",
                                    "Target-growth distance L_d [m].");
  params.addRangeCheckedParam<Real>("irreversible_dilation_exponent",
                                    1.0,
                                    "irreversible_dilation_exponent >= 1.0",
                                    "Target-growth exponent m_d.");

  params.addRangeCheckedParam<Real>(
      "normal_strength_retention_factor",
      0.0,
      "normal_strength_retention_factor >= 0.0 & normal_strength_retention_factor <= 1.0",
      "Fraction of normal-strength memory remaining after one memory decay distance of opening.");
  params.addRangeCheckedParam<Real>(
      "normal_strength_memory_decay_distance",
      1e-4,
      "normal_strength_memory_decay_distance > 0.0",
      "Opening distance L_m [m] controlling normal-strength-memory decay.");
  params.addRangeCheckedParam<Real>(
      "retained_shear_support_factor",
      0.0,
      "retained_shear_support_factor >= 0.0 & retained_shear_support_factor <= 1.0",
      "Fraction of decaying historical shear support retained as a lower strength floor.");
  params.addRangeCheckedParam<Real>(
      "retained_shear_support_decay_distance",
      1e-4,
      "retained_shear_support_decay_distance > 0.0",
      "Slip distance L_H [m] controlling retained shear-support decay.");

  params.addRangeCheckedParam<Real>(
      "reversible_normal_compliance",
      0.0,
      "reversible_normal_compliance >= 0.0",
      "Reversible elastic joint-normal compliance C_n [m/Pa]. Adds a recoverable normal opening "
      "d_rev = C_n*max(0, sigma_ref - sigma'_n) to the REPORTED normal opening (irreversible g_np + "
      "d_rev). Decoupled: computed from the converged effective normal stress, not fed into the "
      "residual/Jacobian. Zero (default) disables the term.");
  params.addRangeCheckedParam<Real>(
      "reversible_normal_reference_stress",
      0.0,
      "reversible_normal_reference_stress >= 0.0",
      "Reference effective normal stress sigma_ref [Pa] at which the reversible opening is zero "
      "(typically the initial/preload sigma'_n). Only used when reversible_normal_compliance > 0.");
  params.addRangeCheckedParam<Real>(
      "reversible_normal_opening_activation_slip",
      0.0,
      "reversible_normal_opening_activation_slip >= 0.0",
      "Output-only cumulative plastic-slip onset [m] for the reversible normal opening. A "
      "positive value suppresses stress-driven opening before shear failure; zero (default) "
      "preserves the previous always-active diagnostic exactly.");
  params.addRangeCheckedParam<Real>(
      "reversible_normal_opening_activation_distance",
      1e-5,
      "reversible_normal_opening_activation_distance > 0.0",
      "Plastic-slip distance [m] over which the reversible-opening activation gate rises from "
      "zero toward one after its onset. This affects reported opening only.");
  params.addRangeCheckedParam<Real>(
      "reversible_normal_opening_activation_exponent",
      2.0,
      "reversible_normal_opening_activation_exponent >= 1.0",
      "Shape exponent m of the output gate 1-exp(-((s-s0)/D)^m).");
  params.addRangeCheckedParam<Real>(
      "reversible_normal_opening_retention_fraction",
      0.0,
      "reversible_normal_opening_retention_fraction >= 0.0 & "
      "reversible_normal_opening_retention_fraction <= 1.0",
      "Output-only reclosure hysteresis. During normal reclosure, retain this fraction of the "
      "difference between the largest reversible opening reached and the instantaneous elastic "
      "opening. Zero preserves the legacy fully reversible diagnostic; one retains the peak "
      "reversible opening. The contact residual and hydraulic aperture are unchanged.");
  params.addRangeCheckedParam<Real>(
      "reversible_normal_opening_retention_activation_slip",
      0.0,
      "reversible_normal_opening_retention_activation_slip >= 0.0",
      "Cumulative plastic slip [m] at which reversible-opening peak memory is activated. Before "
      "activation the stored maximum is reset to the instantaneous opening, preventing preload or "
      "pressure-cycling history from being mistaken for post-failure hysteresis. Zero preserves "
      "the previous behavior.");

  params.addParam<bool>(
      "use_rate_and_state",
      false,
      "Enable a regularized rate-and-state friction term, referenced to steady sliding at V0 so it "
      "is a PERTURBATION about the roughness Coulomb strength (which plays the role of the reference "
      "friction f0), not an absolute add-on: strength += p*a*(asinh[(V/(2 V0))*(V0*theta/Dc)^(b/a)] "
      "- asinh(1/2)), V=slip rate, theta the state variable (aging law dtheta/dt = 1 - V*theta/Dc). "
      "At V=V0, theta=Dc/V0 the term vanishes; it strengthens for V>V0 (spreading the slip-weakening "
      "burst) and mildly weakens for V<V0. Default false leaves behavior byte-identical. Set V0 near "
      "the characteristic slip rate so asinh stays O(1); a>b => velocity-strengthening (stable).");
  params.addRangeCheckedParam<Real>(
      "rate_and_state_a", 0.0, "rate_and_state_a >= 0.0",
      "RSF direct-effect coefficient a (dimensionless). Zero disables the term.");
  params.addRangeCheckedParam<Real>(
      "rate_and_state_b", 0.0, "rate_and_state_b >= 0.0",
      "RSF state-evolution coefficient b (dimensionless).");
  params.addRangeCheckedParam<Real>(
      "rate_and_state_Dc", 1.0e-5, "rate_and_state_Dc > 0.0",
      "RSF characteristic state-evolution slip distance Dc [m].");
  params.addRangeCheckedParam<Real>(
      "rate_and_state_V0", 1.0e-6, "rate_and_state_V0 > 0.0",
      "RSF reference slip velocity V0 [m/s].");
  params.addRangeCheckedParam<Real>(
      "rate_and_state_theta0", 0.0, "rate_and_state_theta0 >= 0.0",
      "Initial RSF state theta0 [s]. Zero (default) auto-initialises to the steady state Dc/V0.");
  params.addParam<bool>(
      "rate_and_state_nonnegative",
      false,
      "Clamp the referenced RSF term at zero (strengthening only). The raw referenced form "
      "a*(asinh(z)-asinh(1/2)) is NEGATIVE as V->0 (-0.481*a*p), so the slip-branch strength at "
      "vanishing slip rate sits BELOW the stick limit: the stick<->slip transition is a non-monotone "
      "jump of 0.481*a*p and the global Newton can limit-cycle across it exactly at slip onset and "
      "at re-stick/arrest (observed: 52_15/52_16 dt-collapse stalls at t~1830-1880 s, both at "
      "V~1.4e-8 m/s while re-sticking). With the clamp the slip strength at V->0+ equals the stick "
      "limit (continuous transition, monotone response); only the mild V<V0 weakening (~0.1-0.2 MPa) "
      "is given up. Default false = legacy behavior (byte-identical).");

  params.addRangeCheckedParam<Real>("max_plastic_slip_increment",
                                    0.0,
                                    "max_plastic_slip_increment >= 0.0",
                                    "DEPRECATED. Must be zero. Use timestep control, substepping, "
                                    "or viscosity.");
  params.addRangeCheckedParam<Real>("max_dilation_increment",
                                    0.0,
                                    "max_dilation_increment >= 0.0",
                                    "DEPRECATED. Must be zero. Use timestep control, substepping, "
                                    "or viscosity.");

  return params;
}

ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile::
    ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile(
        const InputParameters & parameters)
  : OrcaCZMComputeLocalTractionIncrementalBase(parameters),
    _penalty_normal(getParam<Real>("penalty_normal")),
    _penalty_tangent(getParam<Real>("penalty_tangent") > 0.0 ? getParam<Real>("penalty_tangent")
                                                             : getParam<Real>("penalty_normal")),
    _use_hyperbolic_normal_closure(getParam<bool>("use_hyperbolic_normal_closure")),
    _initial_normal_stiffness(getParam<Real>("initial_normal_stiffness")),
    _maximum_closure(getParam<Real>("maximum_closure")),
    _maximum_closure_fraction(getParam<Real>("maximum_closure_fraction")),
    _normal_closure_stress_exponent(getParam<Real>("normal_closure_stress_exponent")),
    _normal_closure_offset(getParam<Real>("normal_closure_offset")),
    _normal_traction_tolerance_legacy(getParam<Real>("normal_traction_tolerance")),
    _tangential_traction_tolerance(getParam<Real>("tangential_traction_tolerance")),
    _opening_gap_tolerance(getParam<Real>("opening_gap_tolerance")),
    _return_mapping_stiffness_tolerance(getParam<Real>("return_mapping_stiffness_tolerance")),
    _local_newton_stress_tolerance(getParam<Real>("local_newton_stress_tolerance")),
    _local_newton_gap_tolerance(getParam<Real>("local_newton_gap_tolerance")),
    _max_local_newton_iterations(getParam<unsigned int>("max_local_newton_iterations")),
    _max_local_substeps(getParam<unsigned int>("max_local_substeps")),
    _event_fraction_tolerance(getParam<Real>("event_fraction_tolerance")),
    _contact_gap_regularization(getParam<Real>("contact_gap_regularization")),
    _stress_regularization(getParam<Real>("stress_regularization")),
    _enable_tensile_cohesion(getParam<bool>("enable_tensile_cohesion")),
    _cohesive_peak_traction(getParam<Real>("cohesive_peak_traction")),
    _cohesive_initial_separation(getParam<Real>("cohesive_initial_separation")),
    _cohesive_final_separation(getParam<Real>("cohesive_final_separation")),
    _cohesive_shear_weight(getParam<Real>("cohesive_shear_weight")),
    _cohesive_damage_viscosity(getParam<Real>("cohesive_damage_viscosity")),
    _cohesive_failure_tolerance(getParam<Real>("cohesive_failure_tolerance")),
    _cohesive_gap_regularization(getParam<Real>("cohesive_gap_regularization")),
    _use_dilatancy(getParam<bool>("use_dilatancy")),
    _dilation_opens_joint(getParam<bool>("dilation_opens_joint")),
    _use_normal_memory_for_dilation_support(
        getParam<bool>("use_normal_memory_for_dilation_support")),
    _tangential_viscosity(getParam<Real>("tangential_viscosity")),
    _dissipation_margin(getParam<Real>("dissipation_margin")),
    _initial_roughness(getParam<Real>("initial_roughness")),
    _residual_roughness(getParam<Real>("residual_roughness")),
    _roughness_decay_distance(getParam<Real>("roughness_decay_distance")),
    _friction_coefficient_rough(getParam<Real>("friction_coefficient_rough")),
    _friction_coefficient_smooth(getParam<Real>("friction_coefficient_smooth")),
    _friction_roughness_exponent(getParam<Real>("friction_roughness_exponent")),
    _cohesion_rough(getParam<Real>("cohesion_rough")),
    _cohesion_smooth(getParam<Real>("cohesion_smooth")),
    _cohesion_roughness_exponent(getParam<Real>("cohesion_roughness_exponent")),
    _secondary_weakening_strength(getParam<Real>("secondary_weakening_strength")),
    _secondary_weakening_onset_slip(getParam<Real>("secondary_weakening_onset_slip")),
    _secondary_weakening_distance(getParam<Real>("secondary_weakening_distance")),
    _dilation_angle_peak_degrees(getParam<Real>("dilation_angle_peak_degrees")),
    _dilation_angle_residual_degrees(getParam<Real>("dilation_angle_residual_degrees")),
    _dilation_decay_distance(getParam<Real>("dilation_decay_distance")),
    _dilation_decay_exponent(getParam<Real>("dilation_decay_exponent")),
    _dilation_support_reference(getParam<Real>("dilation_support_reference")),
    _dilation_support_exponent(getParam<Real>("dilation_support_exponent")),
    _dilation_high_normal_reference(getParam<Real>("dilation_high_normal_reference")),
    _dilation_high_normal_exponent(getParam<Real>("dilation_high_normal_exponent")),
    _use_irreversible_dilation_target(getParam<bool>("use_irreversible_dilation_target")),
    _max_irreversible_dilation(getParam<Real>("max_irreversible_dilation")),
    _irreversible_dilation_distance(getParam<Real>("irreversible_dilation_distance")),
    _irreversible_dilation_exponent(getParam<Real>("irreversible_dilation_exponent")),
    _normal_strength_retention_factor(getParam<Real>("normal_strength_retention_factor")),
    _normal_strength_memory_decay_distance(getParam<Real>("normal_strength_memory_decay_distance")),
    _retained_shear_support_factor(getParam<Real>("retained_shear_support_factor")),
    _retained_shear_support_decay_distance(getParam<Real>("retained_shear_support_decay_distance")),
    _reversible_normal_compliance(getParam<Real>("reversible_normal_compliance")),
    _reversible_normal_reference_stress(getParam<Real>("reversible_normal_reference_stress")),
    _reversible_normal_opening_activation_slip(
        getParam<Real>("reversible_normal_opening_activation_slip")),
    _reversible_normal_opening_activation_distance(
        getParam<Real>("reversible_normal_opening_activation_distance")),
    _reversible_normal_opening_activation_exponent(
        getParam<Real>("reversible_normal_opening_activation_exponent")),
    _reversible_normal_opening_retention_fraction(
        getParam<Real>("reversible_normal_opening_retention_fraction")),
    _reversible_normal_opening_retention_activation_slip(
        getParam<Real>("reversible_normal_opening_retention_activation_slip")),
    _use_rate_and_state(getParam<bool>("use_rate_and_state")),
    _rate_and_state_a(getParam<Real>("rate_and_state_a")),
    _rate_and_state_b(getParam<Real>("rate_and_state_b")),
    _rate_and_state_Dc(getParam<Real>("rate_and_state_Dc")),
    _rate_and_state_V0(getParam<Real>("rate_and_state_V0")),
    _rate_and_state_theta0(getParam<Real>("rate_and_state_theta0")),
    _rate_and_state_nonnegative(getParam<bool>("rate_and_state_nonnegative")),
    _fracture_state(declareADProperty<Real>(_base_name + "fracture_state")),
    _limit_tau(declareADProperty<Real>(_base_name + "limit_tau")),
    _plastic_slip_increment(declareADProperty<Real>(_base_name + "plastic_slip_increment")),
    _dilation_jump_increment(declareADProperty<Real>(_base_name + "dilation_jump_increment")),
    _cumulative_plastic_slip(declareADProperty<Real>(_base_name + "cumulative_plastic_slip")),
    _cumulative_plastic_slip_old(
        getMaterialPropertyOld<Real>(_base_name + "cumulative_plastic_slip")),
    _roughness_state(declareADProperty<Real>(_base_name + "roughness_state")),
    _roughness_state_old(getMaterialPropertyOld<Real>(_base_name + "roughness_state")),
    _roughness_damage(declareADProperty<Real>(_base_name + "roughness_damage")),
    _friction_coefficient_effective(
        declareADProperty<Real>(_base_name + "friction_coefficient_effective")),
    _cohesion_effective(declareADProperty<Real>(_base_name + "cohesion_effective")),
    _dilation_angle_effective(declareADProperty<Real>(_base_name + "dilation_angle_effective")),
    _dilation_state(declareADProperty<Real>(_base_name + "dilation_state")),
    _dilation_support_factor(declareADProperty<Real>(_base_name + "dilation_support_factor")),
    _strength_normal_memory_magnitude(
        declareADProperty<Real>(_base_name + "strength_normal_memory_magnitude")),
    _strength_normal_memory_magnitude_old(
        getMaterialPropertyOld<Real>(_base_name + "strength_normal_memory_magnitude")),
    _strength_normal_memory(declareADProperty<Real>(_base_name + "strength_normal_memory")),
    _retained_shear_support(declareADProperty<Real>(_base_name + "retained_shear_support")),
    _retained_shear_support_old(
        getMaterialPropertyOld<Real>(_base_name + "retained_shear_support")),
    _normal_plastic_jump(declareADProperty<Real>(_base_name + "normal_plastic_jump")),
    _normal_plastic_jump_old(getMaterialPropertyOld<Real>(_base_name + "normal_plastic_jump")),
    _irreversible_dilation(declareADProperty<Real>(_base_name + "irreversible_dilation")),
    _normal_contact_pressure(declareADProperty<Real>(_base_name + "normal_contact_pressure")),
    _reversible_normal_opening(declareADProperty<Real>(_base_name + "reversible_normal_opening")),
    _normal_opening_total(declareADProperty<Real>(_base_name + "normal_opening_total")),
    _maximum_reversible_normal_opening(
        declareADProperty<Real>(_base_name + "maximum_reversible_normal_opening")),
    _maximum_reversible_normal_opening_old(
        getMaterialPropertyOld<Real>(_base_name + "maximum_reversible_normal_opening")),
    _rate_state_theta(declareADProperty<Real>(_base_name + "rate_state_theta")),
    _rate_state_theta_old(getMaterialPropertyOld<Real>(_base_name + "rate_state_theta")),
    _frictional_sliding_work_increment(
        declareADProperty<Real>(_base_name + "frictional_sliding_work_increment")),
    _dilation_work_increment(declareADProperty<Real>(_base_name + "dilation_work_increment")),
    _frictional_dilatant_dissipation_increment(
        declareADProperty<Real>(_base_name + "frictional_dilatant_dissipation_increment")),
    _cohesive_dissipation_increment(
        declareADProperty<Real>(_base_name + "cohesive_dissipation_increment")),
    _plastic_tangential_jump(
        declareADProperty<RealVectorValue>(_base_name + "plastic_tangential_jump")),
    _plastic_tangential_jump_old(
        getMaterialPropertyOld<RealVectorValue>(_base_name + "plastic_tangential_jump")),
    _cohesive_damage(declareADProperty<Real>(_base_name + "cohesive_damage")),
    _cohesive_damage_old(getMaterialPropertyOld<Real>(_base_name + "cohesive_damage")),
    _cohesive_history(declareADProperty<Real>(_base_name + "cohesive_history")),
    _cohesive_history_old(getMaterialPropertyOld<Real>(_base_name + "cohesive_history")),
    _cohesive_damage_target(declareADProperty<Real>(_base_name + "cohesive_damage_target"))
{
  if (!_use_hyperbolic_normal_closure && _normal_closure_stress_exponent != 1.0)
    paramError("normal_closure_stress_exponent",
               "A non-unit exponent requires use_hyperbolic_normal_closure=true.");

  if (_residual_roughness > _initial_roughness)
    paramError("residual_roughness", "Must be less than or equal to initial_roughness.");

  if (_residual_roughness >= 1.0)
    paramError("residual_roughness",
               "Must be strictly less than one because normalized roughness divides by 1-Rr.");

  if (_dilation_angle_peak_degrees < _dilation_angle_residual_degrees)
    paramError("dilation_angle_peak_degrees",
               "Must be greater than or equal to dilation_angle_residual_degrees.");

  if (!_dilation_opens_joint)
    paramError("dilation_opens_joint",
               "The revised law only supports physically consistent joint-opening dilation.");

  if (_normal_traction_tolerance_legacy != 0.0)
    paramError("normal_traction_tolerance",
               "This legacy parameter must be zero. Use opening_gap_tolerance [m].");

  if (getParam<Real>("max_plastic_slip_increment") > 0.0)
    paramError("max_plastic_slip_increment",
               "Increment caps are incompatible with a return map on the yield surface. "
               "Use material substepping, timestep control, or tangential_viscosity.");

  if (getParam<Real>("max_dilation_increment") > 0.0)
    paramError("max_dilation_increment",
               "Increment caps are incompatible with an exact local state update. "
               "Use material substepping, timestep control, or tangential_viscosity.");

  if (_enable_tensile_cohesion)
  {
    if (_cohesive_peak_traction <= 0.0)
      paramError("cohesive_peak_traction", "Must be > 0 when enable_tensile_cohesion=true.");
    if (_cohesive_initial_separation <= 0.0)
      paramError("cohesive_initial_separation", "Must be > 0 when enable_tensile_cohesion=true.");
    if (_cohesive_final_separation <= _cohesive_initial_separation)
      paramError("cohesive_final_separation",
                 "Must exceed cohesive_initial_separation when enable_tensile_cohesion=true.");
  }
}

void
ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile::initQpStatefulProperties()
{
  OrcaCZMComputeLocalTractionIncrementalBase::initQpStatefulProperties();

  _fracture_state[_qp] = static_cast<Real>(FractureState::Stick);
  _limit_tau[_qp] = 0.0;
  _plastic_slip_increment[_qp] = 0.0;
  _dilation_jump_increment[_qp] = 0.0;
  _cumulative_plastic_slip[_qp] = 0.0;

  _roughness_state[_qp] = _initial_roughness;
  _roughness_damage[_qp] = 1.0 - _initial_roughness;
  _friction_coefficient_effective[_qp] = _friction_coefficient_rough;
  _cohesion_effective[_qp] = _cohesion_rough;
  _dilation_angle_effective[_qp] = _dilation_angle_peak_degrees;
  _dilation_state[_qp] = _use_dilatancy ? 1.0 : 0.0;
  _dilation_support_factor[_qp] = 0.0;

  _strength_normal_memory_magnitude[_qp] = 0.0;
  _strength_normal_memory[_qp] = 0.0;
  _retained_shear_support[_qp] = 0.0;
  _normal_plastic_jump[_qp] = 0.0;
  _irreversible_dilation[_qp] = 0.0;
  _normal_contact_pressure[_qp] = 0.0;
  _reversible_normal_opening[_qp] = 0.0;
  _normal_opening_total[_qp] = 0.0;
  _maximum_reversible_normal_opening[_qp] = 0.0;
  _rate_state_theta[_qp] =
      _rate_and_state_theta0 > 0.0 ? _rate_and_state_theta0 : _rate_and_state_Dc / _rate_and_state_V0;
  _frictional_sliding_work_increment[_qp] = 0.0;
  _dilation_work_increment[_qp] = 0.0;
  _frictional_dilatant_dissipation_increment[_qp] = 0.0;
  _cohesive_dissipation_increment[_qp] = 0.0;
  _plastic_tangential_jump[_qp] = RealVectorValue(0.0, 0.0, 0.0);

  _cohesive_damage[_qp] = _enable_tensile_cohesion ? 0.0 : 1.0;
  _cohesive_history[_qp] = 0.0;
  _cohesive_damage_target[_qp] = _enable_tensile_cohesion ? 0.0 : 1.0;
}

ADReal
ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile::smoothPositive(
    const ADReal & x, const Real eps) const
{
  return ADReal(0.5) * (x + sqrt(x * x + ADReal(eps * eps)));
}

ADReal
ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile::smoothPositiveDerivative(
    const ADReal & x, const Real eps) const
{
  return ADReal(0.5) * (ADReal(1.0) + x / sqrt(x * x + ADReal(eps * eps)));
}

ADReal
ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile::smoothMaximum(
    const ADReal & a, const ADReal & b, const Real eps) const
{
  const ADReal difference = a - b;
  return ADReal(0.5) * (a + b + sqrt(difference * difference + ADReal(eps * eps)));
}

ADReal
ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile::smoothMaximumWeightA(
    const ADReal & a, const ADReal & b, const Real eps) const
{
  const ADReal difference = a - b;
  return ADReal(0.5) *
         (ADReal(1.0) + difference / sqrt(difference * difference + ADReal(eps * eps)));
}

ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile::LocalState
ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile::oldLocalState() const
{
  LocalState state;

  state.cumulative_plastic_slip = ADReal(_cumulative_plastic_slip_old[_qp]);
  state.plastic_slip_increment = 0.0;
  state.dilation_jump_increment = 0.0;
  state.roughness = ADReal(_roughness_state_old[_qp]);
  state.roughness_damage = ADReal(1.0) - state.roughness;

  ADReal unused_mu_derivative;
  ADReal unused_c_derivative;
  strengthFromRoughness(state.roughness,
                        state.friction,
                        state.cohesion,
                        unused_mu_derivative,
                        unused_c_derivative,
                        ADReal(0.0));

  ADReal unused_slope;
  ADReal unused_dslope;
  dilationFromSlip(state.cumulative_plastic_slip,
                   state.dilation_state,
                   state.dilation_angle_deg,
                   unused_slope,
                   unused_dslope);
  state.dilation_support = 0.0;

  state.normal_pressure_memory = ADReal(_strength_normal_memory_magnitude_old[_qp]);
  state.retained_shear_support = ADReal(_retained_shear_support_old[_qp]);
  state.normal_plastic_jump = ADReal(_normal_plastic_jump_old[_qp]);
  state.irreversible_dilation = state.normal_plastic_jump;
  state.normal_contact_pressure = 0.0;
  state.limit_tau = 0.0;
  state.rate_state_theta = ADReal(_rate_state_theta_old[_qp]);

  state.cohesive_damage = ADReal(_cohesive_damage_old[_qp]);
  state.cohesive_history = ADReal(_cohesive_history_old[_qp]);
  state.cohesive_damage_target =
      _enable_tensile_cohesion ? ADReal(_cohesive_damage_old[_qp]) : ADReal(1.0);

  state.frictional_sliding_work_increment = 0.0;
  state.dilation_work_increment = 0.0;
  state.frictional_dilatant_dissipation_increment = 0.0;
  state.cohesive_dissipation_increment = 0.0;

  state.plastic_tangential_jump = ADRealVectorValue(0.0,
                                                    ADReal(_plastic_tangential_jump_old[_qp](1)),
                                                    ADReal(_plastic_tangential_jump_old[_qp](2)));
  state.traction = ADRealVectorValue(ADReal(_interface_traction_old[_qp](0)),
                                     ADReal(_interface_traction_old[_qp](1)),
                                     ADReal(_interface_traction_old[_qp](2)));
  state.fracture_state = FractureState::Stick;

  return state;
}

void
ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile::storeFinalState(
    const LocalState & state)
{
  _fracture_state[_qp] = static_cast<Real>(state.fracture_state);
  _limit_tau[_qp] = state.limit_tau;
  _plastic_slip_increment[_qp] = state.plastic_slip_increment;
  _dilation_jump_increment[_qp] = state.dilation_jump_increment;
  _cumulative_plastic_slip[_qp] = state.cumulative_plastic_slip;

  _roughness_state[_qp] = state.roughness;
  _roughness_damage[_qp] = state.roughness_damage;
  _friction_coefficient_effective[_qp] = state.friction;
  _cohesion_effective[_qp] = state.cohesion;
  _dilation_angle_effective[_qp] = state.dilation_angle_deg;
  _dilation_state[_qp] = state.dilation_state;
  _dilation_support_factor[_qp] = state.dilation_support;

  _strength_normal_memory_magnitude[_qp] = state.normal_pressure_memory;
  _strength_normal_memory[_qp] = -state.normal_pressure_memory;
  _retained_shear_support[_qp] = state.retained_shear_support;
  _normal_plastic_jump[_qp] = state.normal_plastic_jump;
  _irreversible_dilation[_qp] = state.irreversible_dilation;
  _normal_contact_pressure[_qp] = state.normal_contact_pressure;

  // Reversible (elastic) joint-normal opening, computed from the converged effective normal stress:
  // d_rev = C_n * <sigma_ref - sigma'_n>_+  (opening as sigma'_n falls below the reference, closing as
  // it recovers). Output-only: does not enter the residual, so no Jacobian contribution. C_n=0 -> 0.
  Real reversible_opening_activation = 1.0;
  if (_reversible_normal_opening_activation_slip > 0.0)
  {
    const Real activated_slip =
        std::max(Real(0.0),
                 MetaPhysicL::raw_value(state.cumulative_plastic_slip) -
                     _reversible_normal_opening_activation_slip);
    reversible_opening_activation =
        1.0 -
        std::exp(-std::pow(activated_slip / _reversible_normal_opening_activation_distance,
                           _reversible_normal_opening_activation_exponent));
  }
  const ADReal raw_reversible_opening =
      ADReal(reversible_opening_activation * _reversible_normal_compliance) *
      smoothPositive(ADReal(_reversible_normal_reference_stress) - state.normal_contact_pressure,
                     _stress_regularization);
  const bool retain_opening_history = MetaPhysicL::raw_value(state.cumulative_plastic_slip) >=
                                      _reversible_normal_opening_retention_activation_slip;
  const ADReal maximum_reversible_opening =
      retain_opening_history
          ? std::max(ADReal(_maximum_reversible_normal_opening_old[_qp]), raw_reversible_opening)
          : raw_reversible_opening;
  const ADReal reversible_opening =
      raw_reversible_opening +
      ADReal(retain_opening_history ? _reversible_normal_opening_retention_fraction : 0.0) *
          (maximum_reversible_opening - raw_reversible_opening);
  _maximum_reversible_normal_opening[_qp] = maximum_reversible_opening;
  _reversible_normal_opening[_qp] = reversible_opening;
  // Reported total normal opening = irreversible shear-dilation g_np + reversible elastic opening.
  // Same "positive = opening" native sign convention as _normal_plastic_jump.
  _normal_opening_total[_qp] = state.normal_plastic_jump + reversible_opening;

  _rate_state_theta[_qp] = state.rate_state_theta;

  _frictional_sliding_work_increment[_qp] = state.frictional_sliding_work_increment;
  _dilation_work_increment[_qp] = state.dilation_work_increment;
  _frictional_dilatant_dissipation_increment[_qp] = state.frictional_dilatant_dissipation_increment;
  _cohesive_dissipation_increment[_qp] = state.cohesive_dissipation_increment;

  _plastic_tangential_jump[_qp] = state.plastic_tangential_jump;

  _cohesive_damage[_qp] = state.cohesive_damage;
  _cohesive_history[_qp] = state.cohesive_history;
  _cohesive_damage_target[_qp] = state.cohesive_damage_target;
}

Real
ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile::rawEquivalentSeparation(
    const RealVectorValue & jump) const
{
  const Real normal_opening = std::max(0.0, jump(0));
  const Real shear_norm = std::sqrt(jump(1) * jump(1) + jump(2) * jump(2));
  return std::sqrt(normal_opening * normal_opening +
                   _cohesive_shear_weight * _cohesive_shear_weight * shear_norm * shear_norm);
}

Real
ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile::locateEquivalentSeparationEvent(
    const RealVectorValue & jump_start,
    const RealVectorValue & jump_end,
    const Real threshold) const
{
  Real lo = 0.0;
  Real hi = 1.0;

  for (unsigned int i = 0; i < 60; ++i)
  {
    const Real mid = 0.5 * (lo + hi);
    const RealVectorValue jump_mid = jump_start + mid * (jump_end - jump_start);
    const Real value_mid = rawEquivalentSeparation(jump_mid) - threshold;
    const Real value_lo =
        rawEquivalentSeparation(jump_start + lo * (jump_end - jump_start)) - threshold;
    if (value_lo * value_mid <= 0.0)
      hi = mid;
    else
      lo = mid;
  }

  return 0.5 * (lo + hi);
}

std::vector<Real>
ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile::collectEventFractions(
    const LocalState & old_state,
    const RealVectorValue & jump_start,
    const RealVectorValue & jump_end) const
{
  std::vector<Real> fractions;

  if (_enable_tensile_cohesion)
  {
    const Real delta_start = rawEquivalentSeparation(jump_start);
    const Real delta_end = rawEquivalentSeparation(jump_end);
    for (const Real threshold : {_cohesive_initial_separation, _cohesive_final_separation})
      if ((delta_start - threshold) * (delta_end - threshold) < 0.0)
        fractions.push_back(locateEquivalentSeparationEvent(jump_start, jump_end, threshold));
  }

  const Real gnp_old = MetaPhysicL::raw_value(old_state.normal_plastic_jump);
  const Real closure_offset = _use_hyperbolic_normal_closure ? _normal_closure_offset : 0.0;
  const Real overlap_start = gnp_old - jump_start(0) + closure_offset;
  const Real overlap_end = gnp_old - jump_end(0) + closure_offset;
  if (overlap_start * overlap_end < 0.0 && std::abs(jump_end(0) - jump_start(0)) > 0.0)
  {
    const Real fraction = (gnp_old + closure_offset - jump_start(0)) /
                          (jump_end(0) - jump_start(0));
    fractions.push_back(fraction);
  }

  fractions.push_back(1.0);
  std::sort(fractions.begin(), fractions.end());

  std::vector<Real> unique_fractions;
  Real previous = 0.0;
  for (const Real fraction : fractions)
    if (fraction > _event_fraction_tolerance && fraction <= 1.0 &&
        fraction - previous > _event_fraction_tolerance)
    {
      unique_fractions.push_back(fraction);
      previous = fraction;
    }

  if (unique_fractions.empty() || unique_fractions.back() < 1.0 - _event_fraction_tolerance)
    unique_fractions.push_back(1.0);
  else
    unique_fractions.back() = 1.0;

  return unique_fractions;
}

ADReal
ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile::cohesiveDamageFromHistory(
    const ADReal & history) const
{
  if (!_enable_tensile_cohesion)
    return ADReal(1.0);

  // The damage initiation/final-failure checks are active-set branches. They are intentionally
  // semismooth; tangent verification must avoid centered differences exactly at delta0/deltaf.
  if (MetaPhysicL::raw_value(history) <= _cohesive_initial_separation)
    return ADReal(0.0);

  if (MetaPhysicL::raw_value(history) >= _cohesive_final_separation)
    return ADReal(1.0);

  const ADReal numerator =
      ADReal(_cohesive_final_separation) * (history - ADReal(_cohesive_initial_separation));
  const ADReal denominator =
      history * ADReal(_cohesive_final_separation - _cohesive_initial_separation);
  return numerator / denominator;
}

ADReal
ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile::cohesiveDissipation(
    const ADReal & history) const
{
  // Cumulative cohesive (damage) energy density dissipated up to the monotone equivalent-separation
  // history kappa, for the bilinear traction-separation law. Derived as the work done along the
  // softening envelope up to kappa minus the recoverable secant energy. It is a monotone function
  // of history, so the per-step increment cohesiveDissipation(kappa) - cohesiveDissipation(kappa_old)
  // is non-negative. Used only as an energy-audit output (see M5 in the audit report).
  if (!_enable_tensile_cohesion)
    return ADReal(0.0);

  const Real d0 = _cohesive_initial_separation;
  const Real df = _cohesive_final_separation;
  const Real t0 = _cohesive_peak_traction;
  const Real fracture_energy = 0.5 * t0 * df; // G_c = 0.5 T0 delta_f

  if (MetaPhysicL::raw_value(history) <= d0)
    return ADReal(0.0);
  if (MetaPhysicL::raw_value(history) >= df)
    return ADReal(fracture_energy);

  const ADReal k = history;
  const ADReal work_elastic = ADReal(0.5 * t0 * d0);
  const ADReal work_softening =
      ADReal(t0 / (df - d0)) *
      (ADReal(df) * (k - ADReal(d0)) - ADReal(0.5) * (k * k - ADReal(d0 * d0)));
  const ADReal envelope_traction = ADReal(t0) * (ADReal(df) - k) / ADReal(df - d0);
  const ADReal recoverable = ADReal(0.5) * envelope_traction * k;
  return work_elastic + work_softening - recoverable;
}

ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile::CohesiveState
ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile::updateCohesiveState(
    const ADRealVectorValue & jump, const LocalState & old_state, const Real substep_fraction) const
{
  CohesiveState state;

  if (!_enable_tensile_cohesion)
  {
    state.equivalent_separation = 0.0;
    state.history = old_state.cohesive_history;
    state.damage_target = 1.0;
    state.damage = 1.0;
    state.normal_traction = 0.0;
    state.shear_scale = 0.0;
    state.dissipation_increment = 0.0;
    return state;
  }

  const ADReal normal_opening = smoothPositive(jump(0), _cohesive_gap_regularization);
  const ADReal shear_norm = sqrt(jump(1) * jump(1) + jump(2) * jump(2));
  state.equivalent_separation =
      sqrt(normal_opening * normal_opening +
           ADReal(_cohesive_shear_weight * _cohesive_shear_weight) * shear_norm * shear_norm);

  state.history = old_state.cohesive_history;
  if (MetaPhysicL::raw_value(state.equivalent_separation) >
      MetaPhysicL::raw_value(old_state.cohesive_history))
    state.history = state.equivalent_separation;

  state.damage_target = cohesiveDamageFromHistory(state.history);

  if (_cohesive_damage_viscosity > 0.0 && _dt > 0.0)
  {
    const ADReal relaxation = ADReal((_dt * substep_fraction) / _cohesive_damage_viscosity);
    const ADReal viscous =
        (old_state.cohesive_damage + relaxation * state.damage_target) / (ADReal(1.0) + relaxation);
    state.damage = old_state.cohesive_damage;
    if (MetaPhysicL::raw_value(viscous) > MetaPhysicL::raw_value(old_state.cohesive_damage))
      state.damage = viscous;
  }
  else
  {
    state.damage = old_state.cohesive_damage;
    if (MetaPhysicL::raw_value(state.damage_target) >
        MetaPhysicL::raw_value(old_state.cohesive_damage))
      state.damage = state.damage_target;
  }

  const ADReal initial_stiffness = ADReal(_cohesive_peak_traction / _cohesive_initial_separation);

  // M4 fix: cohesive damage is driven by the absolute equivalent separation (above), but the
  // recoverable cohesive normal *tension* only acts on the truly-open gap, i.e. the opening beyond
  // the (possibly dilated) unilateral contact surface g_np. This makes cohesive tension and contact
  // compression mutually exclusive in the normal direction and removes the nonphysical
  // 0 < g_n < g_np window in which both were simultaneously active. With no accumulated dilation
  // (g_np = 0) this reduces exactly to <g_n>_+, so the pure Mode I / Mode II responses are
  // unchanged. Because the closed interface then carries no cohesive normal traction, the dilation
  // work p * Delta g_np is again conjugate to the full normal contact traction (M5).
  const ADReal open_gap =
      smoothPositive(jump(0) - old_state.normal_plastic_jump, _cohesive_gap_regularization);
  state.normal_traction = (ADReal(1.0) - state.damage) * initial_stiffness * open_gap;
  state.shear_scale = (ADReal(1.0) - state.damage) * initial_stiffness *
                      ADReal(_cohesive_shear_weight * _cohesive_shear_weight);

  state.dissipation_increment =
      cohesiveDissipation(state.history) - cohesiveDissipation(old_state.cohesive_history);

  return state;
}

void
ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile::strengthFromRoughness(
    const ADReal & roughness,
    ADReal & friction,
    ADReal & cohesion,
    ADReal & dfriction_dgamma,
    ADReal & dcohesion_dgamma,
    const ADReal & droughness_dgamma) const
{
  const ADReal normalized_roughness =
      OrcaCompressionTensile::normalizedResidualRoughness(roughness, _residual_roughness);

  // Residual-to-rough interpolation:
  // Rbar = (R - R_res)/(1 - R_res), so R=R_res gives smooth strength and R=1
  // gives rough strength. The local derivatives below include dRbar/dgamma.
  friction = OrcaCompressionTensile::roughnessPowerInterpolation(roughness,
                                                                 _residual_roughness,
                                                                 _friction_coefficient_rough,
                                                                 _friction_coefficient_smooth,
                                                                 _friction_roughness_exponent);
  cohesion = OrcaCompressionTensile::roughnessPowerInterpolation(roughness,
                                                                 _residual_roughness,
                                                                 _cohesion_rough,
                                                                 _cohesion_smooth,
                                                                 _cohesion_roughness_exponent);

  const ADReal dnormalized_dgamma = droughness_dgamma / ADReal(1.0 - _residual_roughness);
  dfriction_dgamma = ADReal(_friction_coefficient_rough - _friction_coefficient_smooth) *
                     ADReal(_friction_roughness_exponent) *
                     pow(normalized_roughness, ADReal(_friction_roughness_exponent - 1.0)) *
                     dnormalized_dgamma;
  dcohesion_dgamma =
      ADReal(_cohesion_rough - _cohesion_smooth) * ADReal(_cohesion_roughness_exponent) *
      pow(normalized_roughness, ADReal(_cohesion_roughness_exponent - 1.0)) * dnormalized_dgamma;
}

void
ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile::dilationFromSlip(
    const ADReal & cumulative_slip,
    ADReal & state,
    ADReal & angle_deg,
    ADReal & slope,
    ADReal & dslope_dgamma) const
{
  if (!_use_dilatancy)
  {
    state = 0.0;
    angle_deg = 0.0;
    slope = 0.0;
    dslope_dgamma = 0.0;
    return;
  }

  const ADReal x = cumulative_slip / ADReal(_dilation_decay_distance);
  const ADReal xm = pow(x, ADReal(_dilation_decay_exponent));
  state = exp(-xm);
  angle_deg = ADReal(_dilation_angle_residual_degrees) +
              ADReal(_dilation_angle_peak_degrees - _dilation_angle_residual_degrees) * state;

  const ADReal angle_rad = angle_deg * ADReal(orca_pi / 180.0);
  slope = tan(angle_rad);

  const ADReal dstate_dkappa = -state * ADReal(_dilation_decay_exponent) *
                               pow(x, ADReal(_dilation_decay_exponent - 1.0)) /
                               ADReal(_dilation_decay_distance);
  const ADReal dangle_dkappa =
      ADReal(_dilation_angle_peak_degrees - _dilation_angle_residual_degrees) * dstate_dkappa;
  dslope_dgamma = (ADReal(1.0) + slope * slope) * ADReal(orca_pi / 180.0) * dangle_dkappa;
}

void
ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile::dilationSupport(
    const ADReal & pressure, ADReal & support, ADReal & dsupport_dpressure) const
{
  ADReal low = 1.0;
  ADReal dlow = 0.0;
  if (_dilation_support_reference > 0.0)
  {
    const ADReal denom = pressure + ADReal(_dilation_support_reference);
    const ADReal z = pressure / denom;
    low = pow(z, ADReal(_dilation_support_exponent));
    const ADReal dzdp = ADReal(_dilation_support_reference) / (denom * denom);
    dlow = ADReal(_dilation_support_exponent) * pow(z, ADReal(_dilation_support_exponent - 1.0)) *
           dzdp;
  }

  ADReal high = 1.0;
  ADReal dhigh = 0.0;
  if (_dilation_high_normal_reference > 0.0)
  {
    const ADReal denom = pressure + ADReal(_dilation_high_normal_reference);
    const ADReal z = ADReal(_dilation_high_normal_reference) / denom;
    high = pow(z, ADReal(_dilation_high_normal_exponent));
    const ADReal dzdp = -ADReal(_dilation_high_normal_reference) / (denom * denom);
    dhigh = ADReal(_dilation_high_normal_exponent) *
            pow(z, ADReal(_dilation_high_normal_exponent - 1.0)) * dzdp;
  }

  support = low * high;
  dsupport_dpressure = dlow * high + low * dhigh;
}

void
ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile::normalPressureMemory(
    const ADReal & pressure,
    const ADReal & current_normal_jump,
    const ADReal & previous_normal_jump,
    const ADReal & old_memory,
    ADReal & memory,
    ADReal & dmemory_dpressure) const
{
  if (_normal_strength_retention_factor <= 0.0)
  {
    memory = pressure;
    dmemory_dpressure = 1.0;
    return;
  }

  const ADReal opening_increment =
      smoothPositive(current_normal_jump - previous_normal_jump, _contact_gap_regularization);
  const Real log_retention = std::log(_normal_strength_retention_factor);
  const ADReal retained =
      old_memory *
      exp(ADReal(log_retention / _normal_strength_memory_decay_distance) * opening_increment);

  memory = smoothMaximum(pressure, retained, _stress_regularization);
  dmemory_dpressure = smoothMaximumWeightA(pressure, retained, _stress_regularization);
}

ADReal
ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile::dilationTarget(
    const ADReal & cumulative_slip) const
{
  if (!_use_irreversible_dilation_target || !_use_dilatancy || _max_irreversible_dilation <= 0.0)
    return ADReal(0.0);

  const ADReal x = cumulative_slip / ADReal(_irreversible_dilation_distance);
  return ADReal(_max_irreversible_dilation) *
         (ADReal(1.0) - exp(-pow(x, ADReal(_irreversible_dilation_exponent))));
}

ADReal
ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile::dilationTargetDerivative(
    const ADReal & cumulative_slip) const
{
  if (!_use_irreversible_dilation_target || !_use_dilatancy || _max_irreversible_dilation <= 0.0)
    return ADReal(0.0);

  const ADReal x = cumulative_slip / ADReal(_irreversible_dilation_distance);
  return ADReal(_max_irreversible_dilation) *
         exp(-pow(x, ADReal(_irreversible_dilation_exponent))) *
         ADReal(_irreversible_dilation_exponent) *
         pow(x, ADReal(_irreversible_dilation_exponent - 1.0)) /
         ADReal(_irreversible_dilation_distance);
}

ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile::FrictionEvaluation
ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile::evaluateFriction(
    const ADReal & gamma,
    const ADReal & normal_plastic_jump,
    const ADReal & tau_trial,
    const ADReal & current_normal_jump,
    const ADReal & previous_normal_jump,
    const LocalState & old_state,
    const ADReal & damage_fraction,
    const Real substep_fraction) const
{
  FrictionEvaluation s;

  s.cumulative_slip = old_state.cumulative_plastic_slip + gamma;

  s.roughness = ADReal(_residual_roughness) + (old_state.roughness - ADReal(_residual_roughness)) *
                                                  exp(-gamma / ADReal(_roughness_decay_distance));
  const ADReal dR_dgamma =
      -(s.roughness - ADReal(_residual_roughness)) / ADReal(_roughness_decay_distance);

  ADReal dmu_dgamma;
  ADReal dc_dgamma;
  strengthFromRoughness(s.roughness, s.friction, s.cohesion, dmu_dgamma, dc_dgamma, dR_dgamma);

  ADReal dslope_dgamma;
  dilationFromSlip(
      s.cumulative_slip, s.dilation_state, s.dilation_angle_deg, s.dilation_slope, dslope_dgamma);

  const ADReal overlap = normal_plastic_jump - current_normal_jump;
  const auto normal_response = OrcaNormalClosure::evaluate(overlap,
                                                           _contact_gap_regularization,
                                                           _use_hyperbolic_normal_closure,
                                                           _penalty_normal,
                                                           _initial_normal_stiffness,
                                                           _maximum_closure,
                                                           _maximum_closure_fraction,
                                                           _normal_closure_stress_exponent,
                                                           _normal_closure_offset);
  s.normal_pressure = normal_response.pressure;
  const ADReal dp_dgnp = normal_response.tangent;

  ADReal dmemory_dp;
  normalPressureMemory(s.normal_pressure,
                       current_normal_jump,
                       previous_normal_jump,
                       old_state.normal_pressure_memory,
                       s.normal_pressure_memory,
                       dmemory_dp);
  const ADReal dmemory_dgnp = dmemory_dp * dp_dgnp;

  ADReal dsupport_dsource;
  const ADReal support_pressure =
      _use_normal_memory_for_dilation_support ? s.normal_pressure_memory : s.normal_pressure;
  const ADReal dsupport_source_dgnp =
      _use_normal_memory_for_dilation_support ? dmemory_dgnp : dp_dgnp;
  // Dilation support uses current contact pressure by default. The memory-controlled path is an
  // explicit phenomenological option and is not part of the default asperity-geometry model.
  dilationSupport(support_pressure, s.dilation_support, dsupport_dsource);
  const ADReal dsupport_dgnp = dsupport_dsource * dsupport_source_dgnp;

  ADReal raw_dilation_increment = 0.0;
  ADReal draw_dgamma = 0.0;
  ADReal draw_dgnp = 0.0;
  if (_use_dilatancy && MetaPhysicL::raw_value(damage_fraction) > 0.0)
  {
    if (_use_irreversible_dilation_target)
    {
      if (_max_irreversible_dilation <= 0.0)
      {
        raw_dilation_increment = 0.0;
        draw_dgamma = 0.0;
        draw_dgnp = 0.0;
      }
      else
      {
        // Target mode solves a true state target:
        // g_np = max(g_np_old, d*S(p)*D(kappa)). The max is smooth-regularized here; the
        // d_max=0 branch above remains exactly zero, including local derivatives.
        const ADReal target =
            damage_fraction * s.dilation_support * dilationTarget(s.cumulative_slip);
        const ADReal target_state =
            smoothMaximum(old_state.normal_plastic_jump, target, _contact_gap_regularization);
        const ADReal weight_old = smoothMaximumWeightA(
            old_state.normal_plastic_jump, target, _contact_gap_regularization);
        const ADReal weight_target = ADReal(1.0) - weight_old;

        raw_dilation_increment = target_state - old_state.normal_plastic_jump;
        draw_dgamma = weight_target * damage_fraction * s.dilation_support *
                      dilationTargetDerivative(s.cumulative_slip);
        draw_dgnp =
            weight_target * damage_fraction * dilationTarget(s.cumulative_slip) * dsupport_dgnp;
      }
    }
    else
    {
      // Direct mode scales the normal plastic opening increment by the damaged contact fraction.
      raw_dilation_increment = damage_fraction * s.dilation_slope * s.dilation_support * gamma;
      draw_dgamma = damage_fraction * (s.dilation_slope * s.dilation_support +
                                       gamma * dslope_dgamma * s.dilation_support);
      draw_dgnp = damage_fraction * gamma * s.dilation_slope * dsupport_dgnp;
    }
  }

  s.raw_dilation_increment = raw_dilation_increment;

  const ADReal branch_tau = tau_trial - ADReal(_penalty_tangent) * gamma;
  s.frictional_sliding_work = damage_fraction * branch_tau * gamma;

  ADReal limited_dilation_increment = 0.0;
  ADReal dlimited_dgamma = 0.0;
  ADReal dlimited_dgnp = 0.0;
  if (_use_dilatancy && MetaPhysicL::raw_value(raw_dilation_increment) > 0.0)
  {
    const ADReal denominator = s.normal_pressure + ADReal(_stress_regularization);
    const ADReal coefficient = ADReal(1.0 - _dissipation_margin);
    const ADReal admissible_increment = coefficient * s.frictional_sliding_work / denominator;

    if (MetaPhysicL::raw_value(admissible_increment) > 0.0)
    {
      const ADReal dsliding_work_dgamma =
          damage_fraction * (branch_tau - ADReal(_penalty_tangent) * gamma);
      const ADReal dlimit_dgamma = coefficient * dsliding_work_dgamma / denominator;
      const ADReal dlimit_dgnp =
          -coefficient * s.frictional_sliding_work * dp_dgnp / (denominator * denominator);

      // Enforce p*Delta g_np <= (1-epsilon_D)*d*tau*gamma with a semismooth min
      // active set. This keeps Delta g_np nonnegative exactly; the active limiter branch
      // contributes its derivatives to the F2 row of the local Jacobian.
      if (MetaPhysicL::raw_value(raw_dilation_increment) <=
          MetaPhysicL::raw_value(admissible_increment))
      {
        limited_dilation_increment = raw_dilation_increment;
        dlimited_dgamma = draw_dgamma;
        dlimited_dgnp = draw_dgnp;
      }
      else
      {
        limited_dilation_increment = admissible_increment;
        dlimited_dgamma = dlimit_dgamma;
        dlimited_dgnp = dlimit_dgnp;
      }
    }
  }

  s.dilation_increment = limited_dilation_increment;
  s.normal_plastic_jump = normal_plastic_jump;
  s.dilation_residual =
      normal_plastic_jump - old_state.normal_plastic_jump - limited_dilation_increment;
  s.ddil_dgamma = -dlimited_dgamma;
  s.ddil_dgnp = ADReal(1.0) - dlimited_dgnp;

  s.dilation_work = s.normal_pressure * limited_dilation_increment;
  s.frictional_dilatant_dissipation = s.frictional_sliding_work - s.dilation_work;

  s.raw_strength = s.cohesion + s.friction * s.normal_pressure_memory;
  const ADReal dYraw_dgamma = dc_dgamma + dmu_dgamma * s.normal_pressure_memory;
  const ADReal dYraw_dgnp = s.friction * dmemory_dgnp;

  ADReal dstrength_dgamma = dYraw_dgamma;
  ADReal dstrength_dgnp = dYraw_dgnp;
  if (_retained_shear_support_factor > 0.0)
  {
    const ADReal historical_candidate =
        ADReal(_retained_shear_support_factor) * old_state.retained_shear_support *
        exp(-gamma / ADReal(_retained_shear_support_decay_distance));
    const ADReal dhistorical_dgamma =
        -historical_candidate / ADReal(_retained_shear_support_decay_distance);
    s.strength = smoothMaximum(s.raw_strength, historical_candidate, _stress_regularization);
    const ADReal weight_raw =
        smoothMaximumWeightA(s.raw_strength, historical_candidate, _stress_regularization);
    dstrength_dgamma = weight_raw * dYraw_dgamma + (ADReal(1.0) - weight_raw) * dhistorical_dgamma;
    dstrength_dgnp = weight_raw * dYraw_dgnp;

    const ADReal decayed_old = old_state.retained_shear_support *
                               exp(-gamma / ADReal(_retained_shear_support_decay_distance));
    s.retained_strength = smoothMaximum(s.raw_strength, decayed_old, _stress_regularization);
  }
  else
  {
    s.strength = s.raw_strength;
    s.retained_strength = 0.0;
  }

  // --- Secondary (large-slip) weakening stage ---
  // The roughness law above gives a GRADUAL slip-weakening; this adds a sharper additional strength loss
  // once the accumulated plastic slip s = cumulative_slip passes s* (secondary_weakening_onset_slip),
  // developing over w (secondary_weakening_distance): strength -= dS*(1 - exp(-<s - s*>/w)). Together they
  // reproduce the observed "gradual then sudden" drop (SW-S4 near peak injection). Keyed on cumulative
  // slip (monotone, d/dgamma = 1, no g_np dependence), so it is well-posed and IRREVERSIBLE -- the drop
  // persists, holding the residual low. Applied before the >=0 floor so any over-drop is floored smoothly.
  // dS = 0 (default) leaves the block inert and behavior byte-identical.
  if (_secondary_weakening_strength > 0.0)
  {
    const ADReal excess = s.cumulative_slip - ADReal(_secondary_weakening_onset_slip);
    if (MetaPhysicL::raw_value(excess) > 0.0)
    {
      const ADReal decay = exp(-excess / ADReal(_secondary_weakening_distance));
      s.strength = s.strength - ADReal(_secondary_weakening_strength) * (ADReal(1.0) - decay);
      // d(excess)/dgamma = d(cumulative_slip)/dgamma = 1; d/dgnp = 0.
      dstrength_dgamma = dstrength_dgamma -
                         ADReal(_secondary_weakening_strength) * decay /
                             ADReal(_secondary_weakening_distance);
    }
  }

  // Frictional strength cannot be negative. For a pre-existing frictional joint the cohesion_*
  // parameters are the Coulomb shear-strength intercept (not a tensile strength), and a negative
  // intercept is a legitimate linearized Barton-Bandis envelope. At low normal pressure the raw
  // strength c + mu*p can then fall below zero; floor it smoothly so the joint simply loses shear
  // resistance there instead of acquiring a spurious negative yield stress. The floor weight scales
  // the local strength derivatives so the return-map Jacobian and the H2 corrector stay consistent.
  const ADReal strength_floor_weight =
      smoothMaximumWeightA(s.strength, ADReal(0.0), _stress_regularization);
  s.strength = smoothMaximum(s.strength, ADReal(0.0), _stress_regularization);
  dstrength_dgamma = strength_floor_weight * dstrength_dgamma;
  dstrength_dgnp = strength_floor_weight * dstrength_dgnp;

  // H3 fix: the frictional overstress rate must use the substep time increment dt*substep_fraction,
  // consistent with the cohesive Duvaut-Lions relaxation in updateCohesiveState. gamma here is the
  // plastic slip accumulated within the current substep, so dividing by the full step _dt would
  // understate the slip rate by 1/substep_fraction and make rate-dependent results depend on the
  // substep count.
  const Real substep_dt = _dt * substep_fraction;
  const bool viscous_active = (_tangential_viscosity > 0.0 && substep_dt > 0.0);
  const ADReal viscous_force =
      viscous_active ? ADReal(_tangential_viscosity / substep_dt) * gamma : ADReal(0.0);
  const ADReal viscous_tangent =
      viscous_active ? ADReal(_tangential_viscosity / substep_dt) : ADReal(0.0);

  // --- Rate-and-state friction (regularized, referenced to steady sliding at V0) ---
  // strength += p * a * ( asinh[ (V/(2 V0)) * (V0*theta_old/Dc)^(b/a) ] - asinh(1/2) ), V = gamma/dt.
  // The -asinh(1/2) reference makes this a PERTURBATION about the roughness Coulomb strength (which is
  // the reference friction f0), not an absolute add-on: at V=V0, theta=Dc/V0 the state factor is 1, the
  // argument is 1/2 and the term VANISHES. This decouples the burst-damping magnitude (a) from any
  // baseline strength offset, curing the raw-asinh pathology where a*asinh(z) added a persistent
  // multi-MPa offset at every slip rate (delaying onset, freezing the post-peak weakening). theta_old
  // (previous step) sets the state factor -> the in-step strength is rate-dependent only through
  // asinh(V) (stable, no singular local coupling); theta is then evolved by the aging law for storage.
  // Set V0 near the characteristic slip rate (asinh O(1) there); a>b => velocity-strengthening.
  ADReal rsf_force = 0.0;
  ADReal rsf_tangent_gamma = 0.0;
  ADReal rsf_tangent_gnp = 0.0;
  s.rate_state_theta = old_state.rate_state_theta; // carry state unchanged when disabled
  if (_use_rate_and_state && _rate_and_state_a > 0.0 && substep_dt > 0.0)
  {
    const ADReal V = gamma / ADReal(substep_dt);
    const ADReal theta_old = old_state.rate_state_theta;
    const ADReal state_factor =
        pow(ADReal(_rate_and_state_V0) * theta_old / ADReal(_rate_and_state_Dc),
            ADReal(_rate_and_state_b / _rate_and_state_a));
    const ADReal z = V / (ADReal(2.0) * ADReal(_rate_and_state_V0)) * state_factor;
    const ADReal root = sqrt(z * z + ADReal(1.0));
    // Reference to steady sliding at V0: z_ref = (V0/2V0)*(V0*(Dc/V0)/Dc)^(b/a) = 1/2, a constant, so
    // subtracting a*asinh(1/2) turns the direct effect into a perturbation about the roughness strength
    // (see block comment). The constant drops out of d/dgamma, so the local tangent is unchanged.
    const Real rsf_ref = 0.4812118250596035; // asinh(1/2) = ln((1+sqrt(5))/2)
    ADReal mu_rs =
        ADReal(_rate_and_state_a) * (log(z + root) - rsf_ref); // a*(asinh(z) - asinh(1/2))
    // Optional non-negative clamp (see param doc): the raw referenced form is -0.481*a at V->0,
    // a non-monotone drop below the stick limit that Newton limit-cycles across at onset/re-stick.
    // Clamped, the slip strength at V->0+ matches the stick limit (continuous transition). Hard
    // clamp with matching zero tangents (kink at z=1/2 is one-sided-bounded; NR handles it).
    if (_rate_and_state_nonnegative && MetaPhysicL::raw_value(mu_rs) <= 0.0)
    {
      rsf_force = 0.0;
      rsf_tangent_gamma = 0.0;
      rsf_tangent_gnp = 0.0;
    }
    else
    {
      rsf_force = s.normal_pressure_memory * mu_rs;
      // exact local partials: d(mu_rs)/dgamma = a/root * dz/dgamma, dz/dgamma = state_factor/(2 V0 dt)
      const ADReal dz_dgamma =
          state_factor / (ADReal(2.0) * ADReal(_rate_and_state_V0) * ADReal(substep_dt));
      rsf_tangent_gamma = s.normal_pressure_memory * ADReal(_rate_and_state_a) / root * dz_dgamma;
      rsf_tangent_gnp = mu_rs * dmemory_dgnp; // p_memory depends on g_np
    }
    // aging law over the substep at constant V: theta_new = theta_old*exp(-x) + (Dc/V)(1-exp(-x)),
    // x = gamma/Dc; (Dc/V)(1-exp(-x)) = dt*(1-exp(-x))/x, series-regularized as x->0.
    const ADReal x = gamma / ADReal(_rate_and_state_Dc);
    const ADReal ex = exp(-x);
    const ADReal one_minus_ex_over_x = (MetaPhysicL::raw_value(x) > 1.0e-8)
                                           ? (ADReal(1.0) - ex) / x
                                           : (ADReal(1.0) - ADReal(0.5) * x);
    s.rate_state_theta = theta_old * ex + ADReal(substep_dt) * one_minus_ex_over_x;
  }

  // Local residual system:
  // F1 = tau_trial - K_t*gamma - Y(gamma,g_np) - eta_t*gamma/dt - tau_rs(gamma,g_np)
  // F2 = g_np - g_np_old - Delta g_np(gamma,g_np)
  s.residual = tau_trial - ADReal(_penalty_tangent) * gamma - s.strength - viscous_force - rsf_force;
  s.dres_dgamma =
      -(ADReal(_penalty_tangent) + viscous_tangent + dstrength_dgamma + rsf_tangent_gamma);
  s.dres_dgnp = -(dstrength_dgnp + rsf_tangent_gnp);

  return s;
}

void
ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile::storeFrictionHistory(
    LocalState & state,
    const LocalState & old_state,
    const FrictionEvaluation & friction,
    const ADReal & gamma,
    const ADReal & normal_plastic_increment) const
{
  state.plastic_slip_increment = old_state.plastic_slip_increment + gamma;
  state.dilation_jump_increment = old_state.dilation_jump_increment + normal_plastic_increment;
  state.cumulative_plastic_slip = friction.cumulative_slip;
  state.roughness = friction.roughness;
  state.roughness_damage = ADReal(1.0) - friction.roughness;
  state.friction = friction.friction;
  state.cohesion = friction.cohesion;
  state.dilation_angle_deg = friction.dilation_angle_deg;
  state.dilation_state = friction.dilation_state;
  state.dilation_support = friction.dilation_support;

  state.normal_pressure_memory = friction.normal_pressure_memory;
  state.retained_shear_support = friction.retained_strength;
  state.normal_plastic_jump = friction.normal_plastic_jump;
  state.irreversible_dilation = friction.normal_plastic_jump;
  state.normal_contact_pressure = friction.normal_pressure;
  state.limit_tau = friction.strength;
  state.rate_state_theta = friction.rate_state_theta;

  state.frictional_sliding_work_increment =
      old_state.frictional_sliding_work_increment + friction.frictional_sliding_work;
  state.dilation_work_increment = old_state.dilation_work_increment + friction.dilation_work;
  state.frictional_dilatant_dissipation_increment =
      old_state.frictional_dilatant_dissipation_increment +
      friction.frictional_dilatant_dissipation;
}

bool
ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile::updateSubstep(
    const LocalState & old_state,
    const ADRealVectorValue & jump_start,
    const ADRealVectorValue & jump_end,
    const Real substep_fraction,
    LocalState & new_state) const
{
  new_state = old_state;

  const CohesiveState cohesive = updateCohesiveState(jump_end, old_state, substep_fraction);
  new_state.cohesive_history = cohesive.history;
  new_state.cohesive_damage_target = cohesive.damage_target;
  new_state.cohesive_damage = cohesive.damage;
  new_state.cohesive_dissipation_increment =
      old_state.cohesive_dissipation_increment + cohesive.dissipation_increment;

  // Composite traction starts with the intact cohesive area:
  // t_n^coh=(1-d)K_c<g_n>_+, t_t^coh=(1-d)K_c beta_c^2 g_t.
  // Contact compression p is subtracted below, and damaged-area friction d*t_t^fric is added
  // only when the interface is closed and d>0.
  ADRealVectorValue traction(0.0, 0.0, 0.0);
  traction(0) = cohesive.normal_traction;
  traction(1) = cohesive.shear_scale * jump_end(1);
  traction(2) = cohesive.shear_scale * jump_end(2);

  const ADReal damage_fraction = cohesive.damage;
  const ADReal contact_overlap_trial = old_state.normal_plastic_jump - jump_end(0);
  const ADReal active_overlap =
      contact_overlap_trial +
      ADReal(_use_hyperbolic_normal_closure ? _normal_closure_offset : 0.0);
  const bool contact_active =
      MetaPhysicL::raw_value(active_overlap) > _opening_gap_tolerance;

  if (!contact_active || MetaPhysicL::raw_value(damage_fraction) <= 0.0)
  {
    // Contact-Jacobian robustness: evaluate the unilateral pressure through the smooth positive
    // part in BOTH the open and closed sub-cases so the normal contact contributes a continuous
    // stiffness (K_n/2 exactly at overlap=0) to the global Jacobian. Previously the open sub-case
    // hard-zeroed the pressure, so at the initial state — where every interface quadrature point
    // sits exactly at overlap=0 — the interface added no normal stiffness; the global Newton step
    // then interpenetrated freely and the penalty traction blew up on the next residual. When the
    // interface is genuinely open (overlap << -contact_gap_regularization) smoothPositive is ~0
    // with ~0 derivative, so open interfaces still carry no spurious normal traction. Choose
    // contact_gap_regularization to trade capture width against the O(K_n*eps) boundary force.
    const ADReal pressure = OrcaNormalClosure::evaluate(contact_overlap_trial,
                                                        _contact_gap_regularization,
                                                        _use_hyperbolic_normal_closure,
                                                        _penalty_normal,
                                                        _initial_normal_stiffness,
                                                        _maximum_closure,
                                                        _maximum_closure_fraction,
                                                        _normal_closure_stress_exponent,
                                                        _normal_closure_offset)
                                .pressure;
    ADReal pressure_memory = old_state.normal_pressure_memory;
    ADReal unused_derivative;
    normalPressureMemory(contact_active ? pressure : ADReal(0.0),
                         jump_end(0),
                         jump_start(0),
                         old_state.normal_pressure_memory,
                         pressure_memory,
                         unused_derivative);

    traction(0) -= pressure;
    new_state.traction = traction;
    new_state.fracture_state = contact_active ? FractureState::Stick : FractureState::Open;
    new_state.normal_contact_pressure = pressure;
    new_state.normal_pressure_memory = pressure_memory;
    new_state.retained_shear_support = old_state.retained_shear_support;
    new_state.normal_plastic_jump = old_state.normal_plastic_jump;
    new_state.irreversible_dilation = old_state.normal_plastic_jump;
    new_state.plastic_tangential_jump = old_state.plastic_tangential_jump;
    new_state.limit_tau = 0.0;
    return true;
  }

  const ADReal tangential_trial_1 =
      ADReal(_penalty_tangent) * (jump_end(1) - old_state.plastic_tangential_jump(1));
  const ADReal tangential_trial_2 =
      ADReal(_penalty_tangent) * (jump_end(2) - old_state.plastic_tangential_jump(2));
  const ADReal tau_trial =
      sqrt(tangential_trial_1 * tangential_trial_1 + tangential_trial_2 * tangential_trial_2);

  FrictionEvaluation friction = evaluateFriction(ADReal(0.0),
                                                 old_state.normal_plastic_jump,
                                                 tau_trial,
                                                 jump_end(0),
                                                 jump_start(0),
                                                 old_state,
                                                 damage_fraction, substep_fraction);

  if (MetaPhysicL::raw_value(tau_trial) <= _tangential_traction_tolerance ||
      MetaPhysicL::raw_value(friction.residual) <= _local_newton_stress_tolerance)
  {
    traction(0) -= friction.normal_pressure;
    traction(1) += damage_fraction * tangential_trial_1;
    traction(2) += damage_fraction * tangential_trial_2;
    new_state.traction = traction;
    new_state.fracture_state = FractureState::Stick;
    new_state.plastic_tangential_jump = old_state.plastic_tangential_jump;
    storeFrictionHistory(new_state, old_state, friction, ADReal(0.0), ADReal(0.0));
    return true;
  }

  ADReal gamma = ADReal(0.0);
  ADReal normal_plastic_jump = old_state.normal_plastic_jump;
  const ADReal gamma_upper = tau_trial / ADReal(_penalty_tangent);

  // Scale-aware local convergence. The absolute tolerances (Pa, m) alone are far below the AD
  // round-off floor of the residuals at field scale: the yield residual is a difference of ~K_t*gamma
  // and ~tau_trial terms (10s of MPa here), whose double-precision round-off is ~1e-8..1e-3 Pa, so a
  // fixed 1e-8 Pa target is unreachable and the local Newton reports false non-convergence. Adding a
  // relative component tied to the trial stress / slip scale makes the criterion field-scale-robust
  // while still honoring the absolute floors on the small toy-scale tests.
  const Real stress_scale = std::max(MetaPhysicL::raw_value(tau_trial), _stress_regularization);
  const Real gap_scale =
      std::max(MetaPhysicL::raw_value(gamma_upper), _contact_gap_regularization);
  const Real res_tol = _local_newton_stress_tolerance + 1.0e-9 * stress_scale;
  const Real dil_tol = _local_newton_gap_tolerance + 1.0e-9 * gap_scale;

  bool converged = false;
  for (unsigned int iteration = 0; iteration < _max_local_newton_iterations; ++iteration)
  {
    friction = evaluateFriction(gamma,
                                normal_plastic_jump,
                                tau_trial,
                                jump_end(0),
                                jump_start(0),
                                old_state,
                                damage_fraction, substep_fraction);

    if (std::abs(MetaPhysicL::raw_value(friction.residual)) <= res_tol &&
        std::abs(MetaPhysicL::raw_value(friction.dilation_residual)) <= dil_tol)
    {
      converged = true;
      break;
    }

    const ADReal determinant =
        friction.dres_dgamma * friction.ddil_dgnp - friction.dres_dgnp * friction.ddil_dgamma;
    if (std::abs(MetaPhysicL::raw_value(determinant)) < _return_mapping_stiffness_tolerance)
      return false;

    const ADReal dgamma = (-friction.residual * friction.ddil_dgnp +
                           friction.dres_dgnp * friction.dilation_residual) /
                          determinant;
    const ADReal dgnp = (-friction.dres_dgamma * friction.dilation_residual +
                         friction.ddil_dgamma * friction.residual) /
                        determinant;

    const Real current_norm =
        std::abs(MetaPhysicL::raw_value(friction.residual)) / res_tol +
        std::abs(MetaPhysicL::raw_value(friction.dilation_residual)) / dil_tol;

    Real alpha = 1.0;
    bool accepted = false;
    for (unsigned int line_search = 0; line_search < 12; ++line_search)
    {
      ADReal gamma_candidate = gamma + ADReal(alpha) * dgamma;
      if (MetaPhysicL::raw_value(gamma_candidate) < 0.0)
        gamma_candidate = ADReal(0.0);
      if (MetaPhysicL::raw_value(gamma_candidate) > MetaPhysicL::raw_value(gamma_upper))
        gamma_candidate = gamma_upper;

      ADReal gnp_candidate = normal_plastic_jump + ADReal(alpha) * dgnp;
      if (MetaPhysicL::raw_value(gnp_candidate) <
          MetaPhysicL::raw_value(old_state.normal_plastic_jump))
        gnp_candidate = old_state.normal_plastic_jump;

      const FrictionEvaluation candidate = evaluateFriction(gamma_candidate,
                                                            gnp_candidate,
                                                            tau_trial,
                                                            jump_end(0),
                                                            jump_start(0),
                                                            old_state,
                                                            damage_fraction, substep_fraction);
      const Real candidate_norm =
          std::abs(MetaPhysicL::raw_value(candidate.residual)) / res_tol +
          std::abs(MetaPhysicL::raw_value(candidate.dilation_residual)) / dil_tol;

      if (candidate_norm < current_norm)
      {
        gamma = gamma_candidate;
        normal_plastic_jump = gnp_candidate;
        accepted = true;
        break;
      }
      alpha *= 0.5;
    }

    if (!accepted)
      return false;
  }

  friction = evaluateFriction(gamma,
                              normal_plastic_jump,
                              tau_trial,
                              jump_end(0),
                              jump_start(0),
                              old_state,
                              damage_fraction, substep_fraction);
  if (!converged &&
      (std::abs(MetaPhysicL::raw_value(friction.residual)) > res_tol ||
       std::abs(MetaPhysicL::raw_value(friction.dilation_residual)) > dil_tol))
    return false;

  // H2 fix: AD implicit-derivative corrector. The local Newton loop above breaks on the *value*
  // residuals and its line search makes accept/clamp decisions on raw (derivative-free) values, so
  // the converged (gamma, g_np) carry only an approximate seed derivative. One exact Newton step in
  // AD at the converged point injects the correct implicit sensitivities
  // d(gamma)/d(jump) and d(g_np)/d(jump): the residual *values* are already below tolerance so the
  // solution barely moves, but their nonzero AD derivatives supply the -J^{-1} dF/d(jump) term that
  // the value-only loop omitted. This is the standard "raw solve + AD corrector" pattern and it is
  // what makes the assembled interface_traction Jacobian consistent with a finite-difference tangent.
  {
    const ADReal determinant =
        friction.dres_dgamma * friction.ddil_dgnp - friction.dres_dgnp * friction.ddil_dgamma;
    if (std::abs(MetaPhysicL::raw_value(determinant)) >= _return_mapping_stiffness_tolerance)
    {
      const ADReal dgamma_corr = (-friction.residual * friction.ddil_dgnp +
                                  friction.dres_dgnp * friction.dilation_residual) /
                                 determinant;
      const ADReal dgnp_corr = (-friction.dres_dgamma * friction.dilation_residual +
                                friction.ddil_dgamma * friction.residual) /
                               determinant;

      // S2 fix (2026-07-03): the corrector exists purely to inject the implicit AD sensitivities;
      // its VALUE motion must stay at the residual-tolerance scale. Near an ill-conditioned local
      // Jacobian (e.g. strong dilation-support pressure feedback where the two determinant terms
      // nearly cancel) the unclamped step can grow orders of magnitude beyond that scale and leave
      // the admissible set - in particular pushing g_np BELOW g_np_old, violating dilation
      // irreversibility (observed as a 6e-10 m decrease in the target-dilation benchmark). Apply
      // the corrector only when its step is consistent with tolerance-scale motion; otherwise skip
      // it and keep the converged raw-solve values (the tangent there is semismooth anyway).
      const Real corr_gamma_limit = 1.0e3 * (res_tol / _penalty_tangent);
      const Real corr_gnp_limit = 1.0e3 * dil_tol;
      if (std::abs(MetaPhysicL::raw_value(dgamma_corr)) <= corr_gamma_limit &&
          std::abs(MetaPhysicL::raw_value(dgnp_corr)) <= corr_gnp_limit)
      {
        gamma += dgamma_corr;
        normal_plastic_jump += dgnp_corr;
        friction = evaluateFriction(gamma,
                                    normal_plastic_jump,
                                    tau_trial,
                                    jump_end(0),
                                    jump_start(0),
                                    old_state,
                                    damage_fraction,
                                    substep_fraction);
      }
    }
  }

  // S2b fix (2026-07-03): exact irreversibility of the normal plastic jump. The converged local
  // solution only satisfies |F2| <= dil_tol, which permits g_np to sit up to dil_tol BELOW
  // g_np_old on the irreversibility-floor branch (support-modulated target below the accumulated
  // opening). A single substep's leak is invisible, but failure-driven bisection can chain ~1e6
  // substeps inside one evaluation (observed: depth-20 recursion in the target-dilation benchmark)
  // and the systematically signed leak accumulates to ~1e-10 m of nonphysical reclosure. Clamp the
  // exit state exactly: on the floor branch g_np is genuinely insensitive to the displacement
  // jump, so the zero-derivative assignment is also the correct tangent there (semismooth at the
  // floor-activation boundary, like every other active-set decision in this model).
  if (MetaPhysicL::raw_value(normal_plastic_jump) <
      MetaPhysicL::raw_value(old_state.normal_plastic_jump))
  {
    normal_plastic_jump = old_state.normal_plastic_jump;
    friction = evaluateFriction(gamma,
                                normal_plastic_jump,
                                tau_trial,
                                jump_end(0),
                                jump_start(0),
                                old_state,
                                damage_fraction,
                                substep_fraction);
  }

  ADRealVectorValue slip_direction(0.0, 0.0, 0.0);
  slip_direction(1) = tangential_trial_1 / tau_trial;
  slip_direction(2) = tangential_trial_2 / tau_trial;

  ADRealVectorValue plastic_tangent_new(
      0.0,
      old_state.plastic_tangential_jump(1) + gamma * slip_direction(1),
      old_state.plastic_tangential_jump(2) + gamma * slip_direction(2));

  const ADReal branch_traction_1 =
      ADReal(_penalty_tangent) * (jump_end(1) - plastic_tangent_new(1));
  const ADReal branch_traction_2 =
      ADReal(_penalty_tangent) * (jump_end(2) - plastic_tangent_new(2));

  traction(0) -= friction.normal_pressure;
  traction(1) += damage_fraction * branch_traction_1;
  traction(2) += damage_fraction * branch_traction_2;

  new_state.traction = traction;
  new_state.fracture_state = FractureState::Slip;
  new_state.plastic_tangential_jump = plastic_tangent_new;
  storeFrictionHistory(
      new_state, old_state, friction, gamma, normal_plastic_jump - old_state.normal_plastic_jump);

  return true;
}

bool
ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile::advanceSubstep(
    LocalState & state,
    const ADRealVectorValue & global_jump_start,
    const ADRealVectorValue & global_jump_end,
    const Real fraction_start,
    const Real fraction_end,
    const unsigned int depth) const
{
  ADRealVectorValue jump_start;
  ADRealVectorValue jump_end;
  for (unsigned int i = 0; i < 3; ++i)
  {
    jump_start(i) =
        global_jump_start(i) + ADReal(fraction_start) * (global_jump_end(i) - global_jump_start(i));
    jump_end(i) =
        global_jump_start(i) + ADReal(fraction_end) * (global_jump_end(i) - global_jump_start(i));
  }

  LocalState candidate;
  if (updateSubstep(state, jump_start, jump_end, fraction_end - fraction_start, candidate))
  {
    state = candidate;
    return true;
  }

  if (depth >= _max_local_substeps || fraction_end - fraction_start <= _event_fraction_tolerance)
    return false;

  const Real fraction_mid = 0.5 * (fraction_start + fraction_end);
  LocalState first_half = state;
  if (!advanceSubstep(
          first_half, global_jump_start, global_jump_end, fraction_start, fraction_mid, depth + 1))
    return false;

  if (!advanceSubstep(
          first_half, global_jump_start, global_jump_end, fraction_mid, fraction_end, depth + 1))
    return false;

  state = first_half;
  return true;
}

void
ADOrcaDecoupledDilationRoughnessContactTractionCompressionTensile::
    computeInterfaceTractionIncrement()
{
  LocalState state = oldLocalState();

  ADRealVectorValue jump_start(ADReal(_interface_displacement_jump_old[_qp](0)),
                               ADReal(_interface_displacement_jump_old[_qp](1)),
                               ADReal(_interface_displacement_jump_old[_qp](2)));
  const ADRealVectorValue & jump_end = _interface_displacement_jump[_qp];

  const RealVectorValue raw_jump_start(_interface_displacement_jump_old[_qp](0),
                                       _interface_displacement_jump_old[_qp](1),
                                       _interface_displacement_jump_old[_qp](2));
  const RealVectorValue raw_jump_end(MetaPhysicL::raw_value(jump_end(0)),
                                     MetaPhysicL::raw_value(jump_end(1)),
                                     MetaPhysicL::raw_value(jump_end(2)));

  const std::vector<Real> event_fractions =
      collectEventFractions(state, raw_jump_start, raw_jump_end);

  Real previous_fraction = 0.0;
  for (const Real event_fraction : event_fractions)
  {
    if (!advanceSubstep(
            state, jump_start, jump_end, previous_fraction, event_fraction, /* depth */ 0))
      // L8 fix: signal a recoverable failure of the local return map rather than aborting the whole
      // solve. MOOSE catches MooseException thrown during residual/Jacobian assembly, marks the
      // nonlinear solve as failed, and lets the (adaptive) time stepper cut dt and retry. This is
      // the intended "burst-crawl" behavior for pressure-driven stick-slip: a trial displacement
      // increment that is too large for the local solver simply triggers a smaller step instead of
      // killing the run. A persistent failure at dtmin still surfaces as a genuine solve failure.
      throw MooseException(
          "Local cohesive-contact-friction return map did not converge during material "
          "substepping (qp ",
          _qp,
          "); requesting a smaller time step. If this persists at dtmin, reduce softening/dilation "
          "severity, add tangential_viscosity, or increase max_local_substeps.");
    previous_fraction = event_fraction;
  }

  storeFinalState(state);
  _interface_traction_inc[_qp] = state.traction - _interface_traction_old[_qp];
}
