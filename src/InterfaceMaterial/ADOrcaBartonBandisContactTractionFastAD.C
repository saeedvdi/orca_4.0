#include "ADOrcaBartonBandisContactTractionFastAD.h"
#include "OrcaNormalClosure.h"
#include "MooseException.h"
#include "metaphysicl/raw_type.h"
#include <algorithm>
#include <cmath>
#include <limits>

registerMooseObject("OrcaApp", ADOrcaBartonBandisContactTractionFastAD);
registerMooseObjectAliased("OrcaApp",
                           ADOrcaBartonBandisContactTractionFastAD,
                           "OrcaBartonBandisContactTractionFastAD");

InputParameters
ADOrcaBartonBandisContactTractionFastAD::validParams()
{
  InputParameters params = OrcaCZMComputeLocalTractionIncrementalBase::validParams();
  params.addClassDescription(
      "Barton--Bandis contact/traction-separation law with two performance optimizations: "
      "(1) output-only material properties are declared non-AD; "
      "(2) the return-mapping Newton loop runs in Real arithmetic and the consistent AD "
      "tangent is reconstructed once after convergence via the implicit function theorem.");

  params.addRangeCheckedParam<Real>(
      "penalty_tangent", 0.0, "penalty_tangent >= 0.0", "Tangential penalty stiffness [Pa/m].");
  params.addParam<Real>(
      "normal_traction_tolerance", 0.0, "Open-state threshold on normal traction [Pa].");
  params.addRangeCheckedParam<Real>("tangential_traction_tolerance",
                                    1e-16,
                                    "tangential_traction_tolerance >= 0.0",
                                    "Minimum tangential traction norm for slip detection [Pa].");
  params.addRangeCheckedParam<Real>(
      "max_plastic_slip_increment",
      0.0,
      "max_plastic_slip_increment >= 0.0",
      "Optional cap on plastic slip increment per step [m]. Zero = disabled.");
  params.addRangeCheckedParam<Real>(
      "max_dilation_increment",
      0.0,
      "max_dilation_increment >= 0.0",
      "Optional cap on dilation increment per step [m]. Zero = disabled.");
  params.addRangeCheckedParam<unsigned int>(
      "max_return_mapping_iterations",
      50,
      "max_return_mapping_iterations >= 1",
      "Maximum Newton-Raphson iterations for the return-mapping loop.");
  params.addDeprecatedParam<unsigned int>("return_mapping_iterations",
                                          8,
                                          "Renamed to max_return_mapping_iterations.",
                                          "Use max_return_mapping_iterations instead.");
  params.addRangeCheckedParam<Real>("relative_tolerance",
                                    1e-8,
                                    "relative_tolerance > 0.0",
                                    "Relative convergence tolerance for the NR loop.");
  params.addRangeCheckedParam<Real>(
      "contact_gap_regularization",
      0.0,
      "contact_gap_regularization >= 0.0",
      "Smooth-positive regularization length [m] for the unilateral contact/open transition. "
      "Zero preserves the legacy hard active-set switch. A small positive value makes closure, "
      "contact traction, and their Jacobian decay continuously through zero gap.");
  params.addRangeCheckedParam<Real>(
      "tangential_viscosity",
      0.0,
      "tangential_viscosity >= 0.0",
      "OPT-IN (default 0 = legacy) Perzyna-style tangential viscous overstress [Pa.s/m] added "
      "to the slip return-mapping residual as eta*(delta_gamma_p/dt). Regularizes the "
      "slip-weakening/dilatant return map: it removes the stick/slip kink and makes the "
      "consistent tangent positive-definite near the slip instability, so the quasi-static "
      "solver can advance through the limit point instead of collapsing dt. 0 reproduces the "
      "un-regularized behavior exactly.");
  params.addRangeCheckedParam<Real>(
      "min_tau_limit",
      0.0,
      "min_tau_limit >= 0.0",
      "OPT-IN residual shear-strength floor [Pa] (default 0 = legacy). The BB shear-strength "
      "limit is never allowed below this value, even when the joint opens and sigma_n -> 0. "
      "Represents residual asperity/self-propping shear resistance; numerically it removes the "
      "tau_limit -> 0 singularity that makes the quasi-static solver fail at the dynamic slip "
      "event. Try a few percent of peak tau (e.g. 1e5-5e5 Pa) to crawl through the instability.");

  params.addParam<bool>(
      "use_hyperbolic_normal_closure", true, "If true, use BB hyperbolic normal closure law.");
  params.addRangeCheckedParam<Real>("initial_normal_stiffness",
                                    1e13,
                                    "initial_normal_stiffness > 0.0",
                                    "Initial normal stiffness K_ni [Pa/m].");
  params.addRangeCheckedParam<Real>(
      "maximum_closure", 1e-4, "maximum_closure > 0.0", "Maximum BB normal closure v_m [m].");
  params.addRangeCheckedParam<Real>(
      "maximum_closure_fraction",
      0.999,
      "maximum_closure_fraction > 0.0 & maximum_closure_fraction < 1.0",
      "Numerical cap on closure/v_m.");
  params.addRangeCheckedParam<Real>(
      "normal_closure_stress_exponent",
      1.0,
      "normal_closure_stress_exponent >= 1.0",
      "OPT-IN power-law exponent p for the BB normal closure (default 1.0 = the standard "
      "hyperbola, exact legacy behavior). Generalizes closure(sigma_n) = "
      "V_m*sigma_n^p/(sigma_0^p + sigma_n^p) with sigma_0 = K_ni*V_m, i.e. sigma_n(closure) = "
      "sigma_0*(closure/(V_m-closure))^(1/p). The tangent normal stiffness then scales like "
      "sigma_n^(p+1) at sigma_n >> sigma_0, so p ~ 2-3 reproduces the ~3-4x unload stiffening "
      "measured on real joints (e.g. Ye & Ghassemi 2018 Table 2) that a p=1 hyperbola cannot "
      "exceed ~2x over the same stress range, while remaining bounded by V_m.");
  params.addRangeCheckedParam<Real>(
      "normal_closure_offset",
      0.0,
      "normal_closure_offset >= 0.0",
      "OPT-IN pre-seating closure offset c_0 [m] (default 0 = legacy). Added to the "
      "closure computed from the displacement jump, so at zero jump the joint already "
      "carries sigma_n(c_0). Set c_0 = closure(sigma_n0) of the in-situ preload so a "
      "pre-stressed joint starts in equilibrium WITHOUT the startup seating transient "
      "(which would otherwise dump a compensated axial preload into a compliant loading "
      "frame). The displacement jump then measures opening relative to the in-situ state.");
  params.addRangeCheckedParam<Real>(
      "normal_unload_retention_fraction",
      0.0,
      "normal_unload_retention_fraction >= 0.0 & normal_unload_retention_fraction < 1.0",
      "OPT-IN unloading hysteresis for BB normal closure (default 0 = legacy). After "
      "normal-unload activation, the material tracks the minimum raw closure and subtracts "
      "this fraction of recovered closure from the closure used by the BB normal-stress "
      "law. Small values provide a perturbative correction; larger values may be used when "
      "the measured unload branch retains a substantial fraction of the peak opening.");
  params.addRangeCheckedParam<Real>(
      "normal_unload_retention_time",
      0.0,
      "normal_unload_retention_time >= 0.0",
      "Relaxation time [s] for normal_unload_retention_fraction. Zero applies the target "
      "retained opening immediately; positive values lag it with a first-order update.");
  params.addRangeCheckedParam<Real>(
      "normal_reclosure_stiffness_multiplier",
      1.0,
      "normal_reclosure_stiffness_multiplier >= 1.0",
      "OPT-IN multiplier for the BB normal-law tangent after an activated joint starts "
      "reclosing from its minimum closure (default 1 = exact legacy behavior). The transformed "
      "closure is c_eff = c_raw + (m - 1) max(c_raw - c_min, 0), anchored at c_min. Unlike "
      "normal_unload_retention_fraction, m > 1 raises reclosure stress without requiring an "
      "excessive geometric closure/rebound.");
  params.addRangeCheckedParam<Real>(
      "normal_unload_activation_slip",
      0.0,
      "normal_unload_activation_slip >= 0.0",
      "Cumulative plastic slip [m] required before normal-unload retention or reclosure "
      "stiffening is allowed to evolve. Use this to keep pre-failure pressure cycling on the "
      "legacy closure path.");
  params.addRangeCheckedParam<Real>(
      "reported_reversible_normal_opening_scale",
      1.0,
      "reported_reversible_normal_opening_scale >= 0.0",
      "OUTPUT ONLY: multiplier applied to the reversible part of the converged kinematic normal "
      "jump when constructing normal_opening_total. One (default) reproduces the kinematic jump "
      "exactly when retention is zero. Contact, aperture, permeability, and flow are unchanged.");
  params.addRangeCheckedParam<Real>(
      "reported_reversible_normal_opening_retention_fraction",
      0.0,
      "reported_reversible_normal_opening_retention_fraction >= 0.0 & "
      "reported_reversible_normal_opening_retention_fraction <= 1.0",
      "OUTPUT ONLY: fraction of the peak scaled reversible opening retained during post-failure "
      "reclosure. Zero (default) disables retention.");
  params.addRangeCheckedParam<Real>(
      "reported_reversible_normal_opening_retention_activation_slip",
      0.0,
      "reported_reversible_normal_opening_retention_activation_slip >= 0.0",
      "Cumulative plastic slip [m] at which the output-only peak-opening memory is activated. "
      "Before activation, its maximum is reset to the instantaneous reversible opening.");

  params.addRangeCheckedParam<Real>(
      "reversible_normal_compliance",
      0.0,
      "reversible_normal_compliance >= 0.0",
      "OUTPUT ONLY: slip-activated elastic joint-normal compliance C_n [m/Pa]. Adds "
      "C_n <sigma_ref - sigma'_n>_+ to the reported normal opening, so the reconstruction can "
      "show the elastic reclosure the pre-seated power-law closure cannot produce. Zero "
      "(default) reproduces the previous output exactly. Contact traction, displacement, "
      "aperture, permeability and flow are unchanged.");
  params.addRangeCheckedParam<Real>(
      "reversible_normal_reference_stress",
      0.0,
      "reversible_normal_reference_stress >= 0.0",
      "Effective normal stress [Pa] at which the reversible opening above vanishes -- normally "
      "sigma'_n at the end of the unloading branch. Only used when "
      "reversible_normal_compliance > 0.");
  params.addRangeCheckedParam<Real>(
      "reversible_normal_opening_activation_slip",
      0.0,
      "reversible_normal_opening_activation_slip >= 0.0",
      "Cumulative plastic slip [m] below which the reversible compliance above is suppressed. A "
      "mated, unslipped joint is far stiffer normally than one whose asperities shear has "
      "mismatched; this keeps the pre-failure branch on the power-law closure alone.");
  params.addRangeCheckedParam<Real>(
      "reversible_normal_opening_activation_distance",
      1.0e-5,
      "reversible_normal_opening_activation_distance > 0.0",
      "Slip [m] over which the reversible compliance is switched on once the activation slip is "
      "passed.");
  params.addRangeCheckedParam<Real>(
      "reversible_normal_opening_activation_exponent",
      1.0,
      "reversible_normal_opening_activation_exponent > 0.0",
      "Exponent of the activation ramp 1 - exp(-(ds/d)^n).");

  params.addRangeCheckedParam<Real>(
      "jrc", 10.0, "jrc >= 0.0", "Laboratory-scale joint roughness coefficient JRC0.");
  params.addRangeCheckedParam<Real>(
      "jcs", 1e8, "jcs > 0.0", "Laboratory-scale joint wall compressive strength JCS0 [Pa].");
  params.addRangeCheckedParam<Real>(
      "residual_friction_angle_degrees",
      30.0,
      "residual_friction_angle_degrees >= 0.0 & residual_friction_angle_degrees < 89.9",
      "Residual friction angle phi_r [degrees].");
  params.addRangeCheckedParam<Real>(
      "cohesion",
      0.0,
      "cohesion >= 0.0",
      "OPT-IN sigma'_n-INDEPENDENT shear strength c [Pa] added to the Barton-Bandis envelope: "
      "tau_lim = c + sigma'_n*tan(phi_r + JRC*log10(JCS/sigma'_n)). Default 0 reproduces Barton "
      "exactly. Barton's roughness term is mobilization-limited -- it decays to zero as sigma'_n "
      "approaches JCS -- so a MATED tensile fracture held at sigma'_n/JCS ~ 0.4 has no way to "
      "express its asperity interlock except through phi_r, which then has to take values well "
      "above any measured granite basic friction angle. Setting c instead puts that strength "
      "where it physically belongs (asperity shear) and leaves phi_r measurable. In the Hardening "
      "subclass c is destroyed by slip on the same weakening curve W as friction, because the "
      "asperities that carry it are sheared through.");

  params.addParam<bool>(
      "use_scale_correction", true, "If true, apply BB scale corrections to JRC and JCS.");
  params.addRangeCheckedParam<Real>("laboratory_length",
                                    0.1,
                                    "laboratory_length > 0.0",
                                    "Reference laboratory sample length L0 [m].");
  params.addRangeCheckedParam<Real>(
      "joint_length", 0.1, "joint_length > 0.0", "Representative in-model joint length Ln [m].");
  params.addRangeCheckedParam<Real>("compressive_normal_stress_floor",
                                    1e3,
                                    "compressive_normal_stress_floor > 0.0",
                                    "Lower bound on sigma_n inside the BB log expression [Pa].");
  params.addParam<std::string>(
      "pore_pressure_property_name",
      "interface_pore_pressure",
      "Name of the fracture pore pressure material property. This property is only required "
      "when pore_pressure_strength_coefficient is nonzero.");
  params.addRangeCheckedParam<Real>(
      "pore_pressure_strength_coefficient",
      0.0,
      "pore_pressure_strength_coefficient >= 0.0",
      "Coefficient multiplying fracture pore pressure subtracted from contact normal stress "
      "inside the Barton-Bandis strength law. Default 0.0 keeps dry/mechanical behavior.");

  params.addParam<bool>("allow_negative_roughness_angle",
                        false,
                        "If false, clamp JRC*log10(JCS/sigma_n) to non-negative.");
  params.addRangeCheckedParam<Real>(
      "min_friction_angle_degrees",
      0.0,
      "min_friction_angle_degrees >= 0.0 & min_friction_angle_degrees < 89.9",
      "Lower cap on peak friction angle [degrees].");
  params.addRangeCheckedParam<Real>(
      "max_friction_angle_degrees",
      85.0,
      "max_friction_angle_degrees > 0.0 & max_friction_angle_degrees < 89.9",
      "Upper cap on peak friction angle [degrees].");
  params.addParam<bool>(
      "use_state_dependent_fault_pressure_coefficient",
      false,
      "OPT-IN (task #24). If true, this material exports an AD 'fault_pressure_area_coefficient' "
      "property (alpha = sigma_0/(sigma_0+sigma_n)) that OrcaCZMFluidPressureInterfaceKernel can "
      "read via alpha_property_name, replacing a flat empirical fault_pressure_coefficient with "
      "a state-dependent one. False (default) reproduces legacy behavior exactly.");
  params.addRangeCheckedParam<Real>(
      "fault_pressure_area_reference_stress",
      1.897751e8,
      "fault_pressure_area_reference_stress > 0.0",
      "Characteristic stress sigma_0 [Pa] in alpha = sigma_0/(sigma_0+sigma_n). Only used when "
      "use_state_dependent_fault_pressure_coefficient = true. Must be calibrated per sample so "
      "alpha = 0.86 (the empirically-validated constant value) at that sample's own initial "
      "(Pi=8 MPa) effective normal stress -- the default is only SW-S4's calibration and must "
      "not be left at default for other samples. See the MC material's identical parameter.");

  params.addParam<bool>("use_dilatancy", true, "If true, apply BB shear dilation during slip.");
  params.addRangeCheckedParam<Real>("dilation_factor",
                                    0.5,
                                    "dilation_factor >= 0.0",
                                    "Multiplier for BB roughness angle to obtain dilation angle.");
  params.addRangeCheckedParam<Real>(
      "min_dilation_angle_degrees",
      0.0,
      "min_dilation_angle_degrees >= 0.0 & min_dilation_angle_degrees < 89.9",
      "Lower cap on dilation angle [degrees].");
  params.addRangeCheckedParam<Real>(
      "max_dilation_angle_degrees",
      30.0,
      "max_dilation_angle_degrees >= 0.0 & max_dilation_angle_degrees < 89.9",
      "Upper cap on dilation angle [degrees].");
  params.addParam<bool>("accumulate_irreversible_dilation",
                        true,
                        "If true, dilation is stored as an irreversible opening offset.");
  params.addParam<bool>("cap_dilation_to_available_closure",
                        true,
                        "If true, dilation cannot exceed the available mechanical closure.");

  // --- Decoupled (mobilized) dilation angle: OPT-IN, default false = legacy ---
  params.addParam<bool>(
      "use_decoupled_dilation",
      false,
      "OPT-IN (default false = legacy). When false, the dilation angle is the legacy "
      "BB form psi = dilation_factor * roughness_angle (welded to the JRC strength term). "
      "When true, the dilation angle is governed by an INDEPENDENT Barton-1982-style "
      "mobilization/decay law: psi_mob(s^p) = psi_res + (psi_peak - psi_res)*exp(-s^p/D_dil), "
      "leaving the BB shear strength unchanged. Use this to give a smooth (low-JRC) fracture "
      "physical dilation (and dn) while keeping the matched friction/stress response.");
  params.addRangeCheckedParam<Real>(
      "dilation_angle_peak_degrees",
      1.5,
      "dilation_angle_peak_degrees >= 0.0 & dilation_angle_peak_degrees < 89.9",
      "Peak dilation angle at first slip [deg] (used when use_decoupled_dilation=true).");
  params.addRangeCheckedParam<Real>(
      "dilation_angle_residual_degrees",
      0.3,
      "dilation_angle_residual_degrees >= 0.0 & dilation_angle_residual_degrees < 89.9",
      "Residual dilation angle after large slip [deg] (used when use_decoupled_dilation=true).");
  params.addRangeCheckedParam<Real>(
      "dilation_decay_distance",
      1.0e-4,
      "dilation_decay_distance > 0.0",
      "Characteristic plastic slip [m] over which psi decays peak->residual "
      "(used when use_decoupled_dilation=true).");

  params.addParam<bool>(
      "dilation_opens_joint",
      false,
      "OPT-IN constitutive change (default false = legacy behavior). When false, accumulated "
      "irreversible dilation softens the normal contact stress only (it does NOT appear as joint "
      "opening in the displacement field), and the hydraulic aperture is fed by a separate "
      "dilation_scale term in the permeability material. When true, accumulated dilation is "
      "applied "
      "as a NORMAL EIGEN-OPENING: the joint physically separates (dilation enters the displacement "
      "field), the within-step normal feedback becomes dilatant HARDENING (closure + dilation), "
      "and "
      "the hydraulic aperture should be taken as the actual mechanical gap (set "
      "use_kinematic_aperture=true in the permeability material and remove the dilation_scale "
      "over-feed). WARNING: enabling this CHANGES the mechanical solution (hardening vs softening) "
      "and requires re-validation of the stress match and a convergence check.");

  params.addParam<bool>("use_mobilized_jrc",
                        false,
                        "If true, ramp JRC_mob from 0 to JRC_scaled as cumulative slip increases.");
  params.addRangeCheckedParam<Real>("peak_shear_displacement",
                                    1e-3,
                                    "peak_shear_displacement > 0.0",
                                    "Slip at which full JRC is mobilized [m].");
  params.addRangeCheckedParam<Real>("mobilized_jrc_exponent",
                                    1.0,
                                    "mobilized_jrc_exponent > 0.0",
                                    "Shape exponent for the JRC mobilization ramp.");

  // ---- Stress-dependent tangential stiffness (OPT-IN; default false = legacy) ----
  params.addParam<bool>(
      "use_stress_dependent_tangential_stiffness",
      false,
      "If true, scale the tangential stiffness with the start-of-step effective normal "
      "stress: k_t = max(min_tangential_stiffness_fraction, (sigma'_n/sigma_ref)^m) * "
      "penalty_tangent. Barton-Bandis shear stiffness for a rock joint scales with "
      "sigma'_n, so a joint held at constant shear stress creeps forward as sigma'_n "
      "falls; a CONSTANT tangential penalty cannot reproduce that at any value, because "
      "the elastic shear jump then follows tau alone. With this enabled, penalty_tangent "
      "is the stiffness AT tangential_stiffness_reference_stress, not a fixed stiffness. "
      "WARNING: this CHANGES the mechanical solution and requires re-validation.");
  params.addRangeCheckedParam<Real>(
      "tangential_stiffness_reference_stress",
      1.0e6,
      "tangential_stiffness_reference_stress > 0.0",
      "Effective normal stress [Pa] at which k_t equals penalty_tangent. Only read when "
      "use_stress_dependent_tangential_stiffness = true; the natural choice is the "
      "specimen's preload sigma'_n.");
  params.addRangeCheckedParam<Real>("tangential_stiffness_exponent",
                                    1.0,
                                    "tangential_stiffness_exponent >= 0.0",
                                    "Exponent m in k_t ~ sigma'_n^m. 1.0 is the Barton-Bandis "
                                    "linear-in-sigma'_n form; 0.0 recovers the constant penalty.");
  params.addRangeCheckedParam<Real>(
      "min_tangential_stiffness_fraction",
      0.05,
      "min_tangential_stiffness_fraction > 0.0 & min_tangential_stiffness_fraction <= 1.0",
      "Floor on k_t/penalty_tangent. Keeps the tangential penalty from collapsing (and the "
      "stick condition from going soft) when sigma'_n approaches zero at the slip event.");

  return params;
}

ADOrcaBartonBandisContactTractionFastAD::ADOrcaBartonBandisContactTractionFastAD(
    const InputParameters & parameters)
  : OrcaCZMComputeLocalTractionIncrementalBase(parameters),
    _normal_traction_tolerance(getParam<Real>("normal_traction_tolerance")),
    _tangential_traction_tolerance(getParam<Real>("tangential_traction_tolerance")),
    _penalty_tangent_input(getParam<Real>("penalty_tangent")),
    _penalty_tangent(_penalty_tangent_input > 0.0 ? _penalty_tangent_input
                                                  : getParam<Real>("initial_normal_stiffness")),
    _use_stress_dependent_tangential_stiffness(
        getParam<bool>("use_stress_dependent_tangential_stiffness")),
    _tangential_stiffness_reference_stress(getParam<Real>("tangential_stiffness_reference_stress")),
    _tangential_stiffness_exponent(getParam<Real>("tangential_stiffness_exponent")),
    _min_tangential_stiffness_fraction(getParam<Real>("min_tangential_stiffness_fraction")),
    _tangential_stiffness_qp(_penalty_tangent),
    _max_plastic_slip_increment(getParam<Real>("max_plastic_slip_increment")),
    _max_dilation_increment(getParam<Real>("max_dilation_increment")),
    _max_return_mapping_iterations(getParam<unsigned int>("max_return_mapping_iterations")),
    _relative_tolerance(getParam<Real>("relative_tolerance")),
    _contact_gap_regularization(getParam<Real>("contact_gap_regularization")),
    _tangential_viscosity(getParam<Real>("tangential_viscosity")),
    _min_tau_limit(getParam<Real>("min_tau_limit")),
    _use_hyperbolic_normal_closure(getParam<bool>("use_hyperbolic_normal_closure")),
    _initial_normal_stiffness(getParam<Real>("initial_normal_stiffness")),
    _maximum_closure(getParam<Real>("maximum_closure")),
    _maximum_closure_fraction(getParam<Real>("maximum_closure_fraction")),
    _normal_closure_stress_exponent(getParam<Real>("normal_closure_stress_exponent")),
    _normal_closure_offset(getParam<Real>("normal_closure_offset")),
    _normal_unload_retention_fraction(getParam<Real>("normal_unload_retention_fraction")),
    _normal_unload_retention_time(getParam<Real>("normal_unload_retention_time")),
    _normal_reclosure_stiffness_multiplier(getParam<Real>("normal_reclosure_stiffness_multiplier")),
    _normal_unload_activation_slip(getParam<Real>("normal_unload_activation_slip")),
    _reported_reversible_normal_opening_scale(
        getParam<Real>("reported_reversible_normal_opening_scale")),
    _reported_reversible_normal_opening_retention_fraction(
        getParam<Real>("reported_reversible_normal_opening_retention_fraction")),
    _reported_reversible_normal_opening_retention_activation_slip(
        getParam<Real>("reported_reversible_normal_opening_retention_activation_slip")),
    _reversible_normal_compliance(getParam<Real>("reversible_normal_compliance")),
    _reversible_normal_reference_stress(getParam<Real>("reversible_normal_reference_stress")),
    _reversible_normal_opening_activation_slip(
        getParam<Real>("reversible_normal_opening_activation_slip")),
    _reversible_normal_opening_activation_distance(
        getParam<Real>("reversible_normal_opening_activation_distance")),
    _reversible_normal_opening_activation_exponent(
        getParam<Real>("reversible_normal_opening_activation_exponent")),
    _jrc0(getParam<Real>("jrc")),
    _jcs0(getParam<Real>("jcs")),
    _residual_friction_angle_deg(getParam<Real>("residual_friction_angle_degrees")),
    _cohesion(getParam<Real>("cohesion")),
    _use_scale_correction(getParam<bool>("use_scale_correction")),
    _laboratory_length(getParam<Real>("laboratory_length")),
    _joint_length(getParam<Real>("joint_length")),
    _jrc_scaled_const(_use_scale_correction
                          ? _jrc0 * std::pow(_joint_length / _laboratory_length, -0.02 * _jrc0)
                          : _jrc0),
    _jcs_scaled_const(_use_scale_correction
                          ? _jcs0 * std::pow(_joint_length / _laboratory_length, -0.03 * _jrc0)
                          : _jcs0),
    _compressive_normal_stress_floor(getParam<Real>("compressive_normal_stress_floor")),
    _pore_pressure_strength_coefficient(getParam<Real>("pore_pressure_strength_coefficient")),
    _interface_pore_pressure(
        getParam<Real>("pore_pressure_strength_coefficient") > 0.0
            ? &getADMaterialPropertyByName<Real>(
                  _base_name + getParam<std::string>("pore_pressure_property_name"))
            : nullptr),
    _allow_negative_roughness_angle(getParam<bool>("allow_negative_roughness_angle")),
    _min_friction_angle_deg(getParam<Real>("min_friction_angle_degrees")),
    _max_friction_angle_deg(getParam<Real>("max_friction_angle_degrees")),
    _use_state_dependent_fault_pressure_coefficient(
        getParam<bool>("use_state_dependent_fault_pressure_coefficient")),
    _fault_pressure_area_reference_stress(
        getParam<Real>("fault_pressure_area_reference_stress")),
    _dilation_factor(getParam<Real>("dilation_factor")),
    _min_dilation_angle_deg(getParam<Real>("min_dilation_angle_degrees")),
    _max_dilation_angle_deg(getParam<Real>("max_dilation_angle_degrees")),
    _accumulate_irreversible_dilation(getParam<bool>("accumulate_irreversible_dilation")),
    _cap_dilation_to_available_closure(getParam<bool>("cap_dilation_to_available_closure")),
    _use_dilatancy(getParam<bool>("use_dilatancy")),
    _use_decoupled_dilation(getParam<bool>("use_decoupled_dilation")),
    _dilation_angle_peak_deg(getParam<Real>("dilation_angle_peak_degrees")),
    _dilation_angle_residual_deg(getParam<Real>("dilation_angle_residual_degrees")),
    _dilation_decay_distance(getParam<Real>("dilation_decay_distance")),
    _dilation_opens_joint(getParam<bool>("dilation_opens_joint")),
    // Sign threading: OFF reproduces legacy exactly (+1 gap, -1 closure-update).
    // ON routes dilation into the joint opening (-1 gap) and makes the within-step
    // normal feedback dilatant hardening (+1 closure-update: closure + dilation).
    _dil_gap_sign(_dilation_opens_joint ? -1.0 : 1.0),
    _dil_closure_sign(_dilation_opens_joint ? 1.0 : -1.0),
    _use_mobilized_jrc(getParam<bool>("use_mobilized_jrc")),
    _peak_shear_displacement(getParam<Real>("peak_shear_displacement")),
    _mobilized_jrc_exponent(getParam<Real>("mobilized_jrc_exponent")),
    _fracture_state(declareProperty<Real>(_base_name + "fracture_state")),
    _limit_tau(declareProperty<Real>(_base_name + "limit_tau")),
    _plastic_slip_increment(declareProperty<Real>(_base_name + "plastic_slip_increment")),
    _dilation_jump_increment(declareADProperty<Real>(_base_name + "dilation_jump_increment")),
    _cumulative_plastic_slip(declareProperty<Real>(_base_name + "cumulative_plastic_slip")),
    _cumulative_plastic_slip_old(
        getMaterialPropertyOld<Real>(_base_name + "cumulative_plastic_slip")),
    _irreversible_dilation(declareProperty<Real>(_base_name + "irreversible_dilation")),
    _irreversible_dilation_old(getMaterialPropertyOld<Real>(_base_name + "irreversible_dilation")),
    _plastic_tangential_jump(
        declareProperty<RealVectorValue>(_base_name + "plastic_tangential_jump")),
    _plastic_tangential_jump_old(
        getMaterialPropertyOld<RealVectorValue>(_base_name + "plastic_tangential_jump")),
    _bb_unload_retained_opening(declareProperty<Real>(_base_name + "bb_unload_retained_opening")),
    _bb_unload_retained_opening_old(
        getMaterialPropertyOld<Real>(_base_name + "bb_unload_retained_opening")),
    _bb_unload_min_closure(declareProperty<Real>(_base_name + "bb_unload_min_closure")),
    _bb_unload_min_closure_old(getMaterialPropertyOld<Real>(_base_name + "bb_unload_min_closure")),
    _reversible_normal_opening(declareProperty<Real>(_base_name + "reversible_normal_opening")),
    _normal_opening_total(declareProperty<Real>(_base_name + "normal_opening_total")),
    _maximum_reversible_normal_opening(
        declareProperty<Real>(_base_name + "maximum_reversible_normal_opening")),
    _maximum_reversible_normal_opening_old(
        getMaterialPropertyOld<Real>(_base_name + "maximum_reversible_normal_opening")),
    _friction_coefficient_effective(
        declareProperty<Real>(_base_name + "friction_coefficient_effective")),
    _cohesion_effective(declareProperty<Real>(_base_name + "cohesion_effective")),
    _roughness_state(declareADProperty<Real>(_base_name + "roughness_state")),
    _roughness_damage(declareProperty<Real>(_base_name + "roughness_damage")),
    _bb_compressive_normal_stress(
        declareProperty<Real>(_base_name + "bb_compressive_normal_stress")),
    _bb_effective_normal_stress(declareProperty<Real>(_base_name + "bb_effective_normal_stress")),
    _bb_normal_closure(declareADProperty<Real>(_base_name + "bb_normal_closure")),
    _bb_normal_stiffness_tangent(declareProperty<Real>(_base_name + "bb_normal_stiffness_tangent")),
    _bb_jrc_scaled(declareProperty<Real>(_base_name + "bb_jrc_scaled")),
    _bb_jcs_scaled(declareProperty<Real>(_base_name + "bb_jcs_scaled")),
    _bb_jrc_mobilized(declareProperty<Real>(_base_name + "bb_jrc_mobilized")),
    _bb_roughness_angle_degrees(declareProperty<Real>(_base_name + "bb_roughness_angle_degrees")),
    _bb_peak_friction_angle_degrees(
        declareProperty<Real>(_base_name + "bb_peak_friction_angle_degrees")),
    _bb_peak_friction_coefficient(
        declareProperty<Real>(_base_name + "bb_peak_friction_coefficient")),
    _bb_dilation_angle_degrees(declareProperty<Real>(_base_name + "bb_dilation_angle_degrees")),
    _bb_dilation_coefficient(declareProperty<Real>(_base_name + "bb_dilation_coefficient")),
    _bb_tangential_stiffness(declareProperty<Real>(_base_name + "bb_tangential_stiffness")),
    _fault_pressure_area_coefficient(
        declareADProperty<Real>(_base_name + "fault_pressure_area_coefficient"))
{
  if (_min_friction_angle_deg > _max_friction_angle_deg)
    paramError("min_friction_angle_degrees", "Must be <= max_friction_angle_degrees.");
  if (_normal_closure_stress_exponent != 1.0 && !_use_hyperbolic_normal_closure)
    paramError("normal_closure_stress_exponent",
               "The power-law closure exponent requires use_hyperbolic_normal_closure = true.");
  if (_min_dilation_angle_deg > _max_dilation_angle_deg)
    paramError("min_dilation_angle_degrees", "Must be <= max_dilation_angle_degrees.");
  if (_penalty_tangent_input <= 0.0)
    mooseWarning("ADOrcaBartonBandisContactTractionFastAD: 'penalty_tangent' was not set. "
                 "Falling back to 'initial_normal_stiffness' (",
                 _initial_normal_stiffness,
                 " Pa/m) as the tangential penalty.");
}

// =============================================================================
// initQpStatefulProperties
// =============================================================================
void
ADOrcaBartonBandisContactTractionFastAD::initQpStatefulProperties()
{
  OrcaCZMComputeLocalTractionIncrementalBase::initQpStatefulProperties();

  _fracture_state[_qp] = static_cast<Real>(FractureState::Stick);
  _limit_tau[_qp] = 0.0;
  _plastic_slip_increment[_qp] = 0.0;
  _dilation_jump_increment[_qp] = 0.0;
  _cumulative_plastic_slip[_qp] = 0.0;
  _irreversible_dilation[_qp] = 0.0;
  _plastic_tangential_jump[_qp] = RealVectorValue(0.0, 0.0, 0.0);
  _bb_unload_retained_opening[_qp] = 0.0;
  _bb_unload_min_closure[_qp] = 0.0;
  _reversible_normal_opening[_qp] = 0.0;
  _normal_opening_total[_qp] = 0.0;
  _maximum_reversible_normal_opening[_qp] = 0.0;
  _friction_coefficient_effective[_qp] = std::tan(_residual_friction_angle_deg * M_PI / 180.0);
  _cohesion_effective[_qp] = 0.0;
  _roughness_state[_qp] = ADReal(computeRoughnessState());
  _roughness_damage[_qp] = 1.0 - computeRoughnessState();
  _bb_compressive_normal_stress[_qp] = 0.0;
  _bb_effective_normal_stress[_qp] = 0.0;
  _bb_normal_closure[_qp] = ADReal(0.0);
  _bb_normal_stiffness_tangent[_qp] = 0.0;
  _bb_jrc_scaled[_qp] = _jrc_scaled_const;
  _bb_jcs_scaled[_qp] = _jcs_scaled_const;
  _bb_jrc_mobilized[_qp] = _use_mobilized_jrc ? 0.0 : _jrc_scaled_const;
  _bb_roughness_angle_degrees[_qp] = 0.0;
  _bb_peak_friction_angle_degrees[_qp] = _residual_friction_angle_deg;
  _bb_peak_friction_coefficient[_qp] = std::tan(_residual_friction_angle_deg * M_PI / 180.0);
  _bb_dilation_angle_degrees[_qp] = 0.0;
  _bb_dilation_coefficient[_qp] = 0.0;
  _bb_tangential_stiffness[_qp] = _penalty_tangent;
  _fault_pressure_area_coefficient[_qp] = ADReal(1.0);
}

// =============================================================================
// Small helpers
// =============================================================================
Real
ADOrcaBartonBandisContactTractionFastAD::computeRoughnessState() const
{
  return (_jrc_scaled_const > 0.0) ? 1.0 : 0.0;
}

Real
ADOrcaBartonBandisContactTractionFastAD::computeCohesionEffective() const
{
  // Reports the cohesion actually carried by the envelope. Was hard-coded to 0 while `cohesion`
  // did not exist, which is why every calibration that needed a sigma'_n-independent strength had
  // to hide it in phi_r. The Hardening subclass overrides this to report the slip-weakened value.
  return _cohesion;
}

ADReal
ADOrcaBartonBandisContactTractionFastAD::log10AD(const ADReal & x) const
{
  using std::log10;
  return log10(x);
}

ADReal
ADOrcaBartonBandisContactTractionFastAD::clampAD(const ADReal & x, Real lo, Real hi) const
{
  return std::max(ADReal(lo), std::min(ADReal(hi), x));
}

ADReal
ADOrcaBartonBandisContactTractionFastAD::regularizedPositive(const ADReal & x) const
{
  using std::sqrt;
  if (_contact_gap_regularization <= 0.0)
    return std::max(ADReal(0.0), x);

  const ADReal radius =
      sqrt(x * x + ADReal(_contact_gap_regularization * _contact_gap_regularization));
  // The equivalent expression 0.5*(x + radius) loses all significant digits for an open gap
  // much larger than the regularization length. Use its rationalized form on that side.
  return MetaPhysicL::raw_value(x) >= 0.0
             ? ADReal(0.5) * (x + radius)
             : ADReal(0.5 * _contact_gap_regularization * _contact_gap_regularization) /
                   (radius - x);
}

Real
ADOrcaBartonBandisContactTractionFastAD::regularizedPositiveReal(const Real x) const
{
  if (_contact_gap_regularization <= 0.0)
    return std::max(Real(0.0), x);

  const Real radius = std::sqrt(x * x + _contact_gap_regularization * _contact_gap_regularization);
  return x >= 0.0
             ? Real(0.5) * (x + radius)
             : Real(0.5) * _contact_gap_regularization * _contact_gap_regularization / (radius - x);
}

Real
ADOrcaBartonBandisContactTractionFastAD::regularizedPositiveDerivativeReal(const Real x) const
{
  if (_contact_gap_regularization <= 0.0)
    return x > 0.0 ? Real(1.0) : Real(0.0);
  return Real(0.5) * (Real(1.0) + x / std::sqrt(x * x + _contact_gap_regularization *
                                                            _contact_gap_regularization));
}

Real
ADOrcaBartonBandisContactTractionFastAD::computeTangentialStiffness(Real sigma_n_strength) const
{
  if (!_use_stress_dependent_tangential_stiffness)
    return _penalty_tangent;

  const Real ratio =
      std::max(Real(0.0), sigma_n_strength) / _tangential_stiffness_reference_stress;
  const Real scale = _tangential_stiffness_exponent == 0.0
                         ? Real(1.0)
                         : std::pow(ratio, _tangential_stiffness_exponent);
  return _penalty_tangent * std::max(_min_tangential_stiffness_fraction, scale);
}

bool
ADOrcaBartonBandisContactTractionFastAD::normalUnloadRetentionEnabled() const
{
  return _normal_unload_retention_fraction > 0.0 || _normal_reclosure_stiffness_multiplier > 1.0;
}

void
ADOrcaBartonBandisContactTractionFastAD::updateNormalUnloadState(Real raw_closure,
                                                                 Real cumulative_slip)
{
  const Real raw = std::max(Real(0.0), raw_closure);

  if (!normalUnloadRetentionEnabled() || cumulative_slip < _normal_unload_activation_slip)
  {
    _bb_unload_retained_opening[_qp] = 0.0;
    _bb_unload_min_closure[_qp] = raw;
    return;
  }

  const Real old_min = _bb_unload_min_closure_old[_qp];
  // Zero is a valid minimum after the joint has opened. Preserve the historical zero-as-
  // uninitialized convention for retention-only inputs, while the opt-in reclosure law keeps
  // a true running minimum so its anchor is not lost on the first closed step after opening.
  const Real min_closure = _normal_reclosure_stiffness_multiplier > 1.0
                               ? std::min(std::max(Real(0.0), old_min), raw)
                               : (old_min > 0.0 ? std::min(old_min, raw) : raw);
  const Real recovered_closure = std::max(Real(0.0), raw - min_closure);
  const Real target = std::min(raw, _normal_unload_retention_fraction * recovered_closure);

  Real retained = target;
  if (_normal_unload_retention_time > 0.0 && _dt > 0.0)
  {
    const Real retained_old =
        std::min(raw, std::max(Real(0.0), _bb_unload_retained_opening_old[_qp]));
    const Real alpha = Real(1.0) - std::exp(-_dt / _normal_unload_retention_time);
    retained = retained_old + alpha * (target - retained_old);
  }

  _bb_unload_retained_opening[_qp] = std::min(raw, std::max(Real(0.0), retained));
  _bb_unload_min_closure[_qp] = min_closure;
}

void
ADOrcaBartonBandisContactTractionFastAD::updateReportedNormalOpening(const ADReal & total_opening,
                                                                     Real irreversible_opening,
                                                                     Real cumulative_slip)
{
  // This reconstruction is deliberately downstream of the constitutive update. It changes only
  // diagnostic material properties and therefore cannot perturb traction, displacement, hydraulic
  // aperture, permeability, or flow. With scale=1 and retention=0, total = irreversible +
  // (kinematic total - irreversible) exactly, including the pre-failure compression baseline.
  const Real raw_reversible_opening =
      _reported_reversible_normal_opening_scale *
      (MetaPhysicL::raw_value(total_opening) - irreversible_opening);
  const bool retain_opening_history =
      cumulative_slip >= _reported_reversible_normal_opening_retention_activation_slip;
  const Real maximum_reversible_opening =
      retain_opening_history
          ? std::max(_maximum_reversible_normal_opening_old[_qp], raw_reversible_opening)
          : raw_reversible_opening;
  const Real reversible_opening =
      raw_reversible_opening +
      (retain_opening_history ? _reported_reversible_normal_opening_retention_fraction : 0.0) *
          (maximum_reversible_opening - raw_reversible_opening);

  // Slip-activated elastic joint-normal compliance, on top of whatever the closure law
  // produced. d_elastic = a(s) C_n <sigma_ref - sigma'_n>_+, with a(s) ramping from 0 to 1
  // once the joint has slipped: a mated joint is stiff normally, a sheared one is not. The
  // power-law closure is pre-seated onto its asymptote at these stresses and cannot supply
  // this branch, which is why the Barton-Bandis runs reported a flat post-peak dilation
  // while the experiment measured tens of micrometres of reclosure. C_n = 0 (default) is a
  // no-op, so decks that do not set it are bit-identical.
  Real elastic_opening = 0.0;
  if (_reversible_normal_compliance > 0.0)
  {
    Real activation = 1.0;
    if (_reversible_normal_opening_activation_slip > 0.0)
    {
      const Real activated_slip =
          std::max(Real(0.0), cumulative_slip - _reversible_normal_opening_activation_slip);
      activation = 1.0 - std::exp(-std::pow(activated_slip /
                                                _reversible_normal_opening_activation_distance,
                                            _reversible_normal_opening_activation_exponent));
    }
    const Real overstress =
        _reversible_normal_reference_stress - _bb_compressive_normal_stress[_qp];
    elastic_opening =
        activation * _reversible_normal_compliance * std::max(Real(0.0), overstress);
  }

  _maximum_reversible_normal_opening[_qp] = maximum_reversible_opening;
  _reversible_normal_opening[_qp] = reversible_opening + elastic_opening;
  _normal_opening_total[_qp] = irreversible_opening + reversible_opening + elastic_opening;
}

ADReal
ADOrcaBartonBandisContactTractionFastAD::computeEffectiveNormalStressForStrength(
    const ADReal & contact_normal_stress) const
{
  ADReal sigma_eff = std::max(ADReal(0.0), contact_normal_stress);
  if (_interface_pore_pressure && _pore_pressure_strength_coefficient > 0.0)
    sigma_eff = contact_normal_stress -
                ADReal(_pore_pressure_strength_coefficient) * (*_interface_pore_pressure)[_qp];
  return std::max(ADReal(0.0), sigma_eff);
}

Real
ADOrcaBartonBandisContactTractionFastAD::computeEffectiveNormalStressForStrengthReal(
    Real contact_normal_stress) const
{
  Real sigma_eff = std::max(Real(0.0), contact_normal_stress);
  if (_interface_pore_pressure && _pore_pressure_strength_coefficient > 0.0)
    sigma_eff =
        contact_normal_stress - _pore_pressure_strength_coefficient *
                                    MetaPhysicL::raw_value((*_interface_pore_pressure)[_qp]);
  return std::max(Real(0.0), sigma_eff);
}

Real
ADOrcaBartonBandisContactTractionFastAD::computeEffectiveNormalStressTangentScale(
    Real contact_normal_stress) const
{
  Real sigma_eff = contact_normal_stress;
  if (_interface_pore_pressure && _pore_pressure_strength_coefficient > 0.0)
    sigma_eff -= _pore_pressure_strength_coefficient *
                 MetaPhysicL::raw_value((*_interface_pore_pressure)[_qp]);
  return sigma_eff > 0.0 ? 1.0 : 0.0;
}

// =============================================================================
// ADReal helpers (used for the IFT ADReal pass)
// =============================================================================
void
ADOrcaBartonBandisContactTractionFastAD::computeNormalStressAndTangent(const ADReal & closure,
                                                                       ADReal & sigma_n,
                                                                       ADReal & kn_tangent) const
{
  // Single shared implementation of the Barton--Bandis power-law closure (see
  // OrcaNormalClosure.h). This class previously carried its own copy, which had already
  // drifted from the utility (a hard cl_lin = 1e-9 instead of min(1e-9, 0.01*V_m)).
  const auto response = OrcaNormalClosure::evaluateFromClosure<ADReal>(
      closure,
      _use_hyperbolic_normal_closure,
      _initial_normal_stiffness, // legacy linear penalty == K_ni for this family
      _initial_normal_stiffness,
      _maximum_closure,
      _maximum_closure_fraction,
      _normal_closure_stress_exponent);

  sigma_n = response.pressure;
  kn_tangent = response.tangent;
}

void
ADOrcaBartonBandisContactTractionFastAD::computeBartonBandisProperties(
    const ADReal & sigma_n,
    const ADReal & cumulative_slip,
    ADReal & jrc_mobilized,
    ADReal & roughness_angle_deg,
    ADReal & peak_friction_angle_deg,
    ADReal & friction_coefficient,
    ADReal & dilation_angle_deg,
    ADReal & dilation_coefficient,
    ADReal & shear_strength) const
{
  using std::pow;
  using std::tan;
  const ADReal sigma_eff = std::max(ADReal(_compressive_normal_stress_floor), sigma_n);
  jrc_mobilized = ADReal(_jrc_scaled_const);
  if (_use_mobilized_jrc)
  {
    ADReal sbar = std::max(ADReal(0.0), cumulative_slip / ADReal(_peak_shear_displacement));
    sbar = std::min(ADReal(1.0), sbar);
    jrc_mobilized *= pow(sbar, Real(_mobilized_jrc_exponent));
  }
  const ADReal ratio = std::max(ADReal(1.0e-30), ADReal(_jcs_scaled_const) / sigma_eff);
  roughness_angle_deg = jrc_mobilized * log10AD(ratio);
  if (!_allow_negative_roughness_angle)
    roughness_angle_deg = std::max(ADReal(0.0), roughness_angle_deg);
  peak_friction_angle_deg = clampAD(ADReal(_residual_friction_angle_deg) + roughness_angle_deg,
                                    _min_friction_angle_deg,
                                    _max_friction_angle_deg);
  if (_use_decoupled_dilation)
  {
    // Decoupled (Barton-1982-style) mobilized dilation angle, INDEPENDENT of JRC strength.
    // psi_mob = psi_res + (psi_peak - psi_res) * exp(-s^p / D_dil)
    using std::exp;
    const ADReal w = exp(-cumulative_slip / ADReal(_dilation_decay_distance));
    dilation_angle_deg =
        ADReal(_dilation_angle_residual_deg) +
        (ADReal(_dilation_angle_peak_deg) - ADReal(_dilation_angle_residual_deg)) * w;
    dilation_angle_deg =
        clampAD(dilation_angle_deg, _min_dilation_angle_deg, _max_dilation_angle_deg);
  }
  else
  {
    dilation_angle_deg = clampAD(ADReal(_dilation_factor) * roughness_angle_deg,
                                 _min_dilation_angle_deg,
                                 _max_dilation_angle_deg);
  }
  const ADReal deg_to_rad(M_PI / 180.0);
  friction_coefficient = tan(peak_friction_angle_deg * deg_to_rad);
  dilation_coefficient = _use_dilatancy ? tan(dilation_angle_deg * deg_to_rad) : ADReal(0.0);
  // Asperity cohesion (default 0 = Barton exactly). It is sigma'_n-independent, so it changes
  // d(tau_lim)/d(sigma'_n) -- the quantity an injection test actually sweeps -- and is NOT
  // interchangeable with a phi_r that reproduces the same strength at one calibration point.
  shear_strength = ADReal(_cohesion) + sigma_n * friction_coefficient;
  // Residual self-propping floor (default 0 = no-op). Keeps tau_limit > 0 when the joint
  // opens (sigma_n -> 0), removing the strength-collapse singularity at the slip instability.
  if (_min_tau_limit > 0.0)
    shear_strength = std::max(ADReal(_min_tau_limit), shear_strength);
}

ADReal
ADOrcaBartonBandisContactTractionFastAD::computeDilationIncrement(
    const ADReal & dilation_coefficient,
    const ADReal & plastic_slip_increment,
    const ADReal & available_closure) const
{
  ADReal dil = _use_dilatancy ? dilation_coefficient * plastic_slip_increment : ADReal(0.0);
  if (_max_dilation_increment > 0.0)
    dil = std::min(dil, ADReal(_max_dilation_increment));
  if (_cap_dilation_to_available_closure)
    dil = std::min(dil, std::max(ADReal(0.0), available_closure));
  return std::max(ADReal(0.0), dil);
}

// =============================================================================
// Real helpers (NR loop — zero AD overhead)
// =============================================================================
void
ADOrcaBartonBandisContactTractionFastAD::computeNormalStressAndTangentReal(Real closure,
                                                                           Real & sigma_n,
                                                                           Real & kn_tangent) const
{
  // Real instantiation of the SAME shared law used by the AD path above, so the NR loop and
  // the IFT pass can never disagree.
  const auto response = OrcaNormalClosure::evaluateFromClosure<Real>(
      closure,
      _use_hyperbolic_normal_closure,
      _initial_normal_stiffness,
      _initial_normal_stiffness,
      _maximum_closure,
      _maximum_closure_fraction,
      _normal_closure_stress_exponent);

  sigma_n = response.pressure;
  kn_tangent = response.tangent;
}

void
ADOrcaBartonBandisContactTractionFastAD::computeBartonBandisPropertiesReal(
    Real sigma_n,
    Real cumulative_slip,
    Real & jrc_mobilized,
    Real & roughness_angle_deg,
    Real & peak_friction_angle_deg,
    Real & friction_coefficient,
    Real & dilation_angle_deg,
    Real & dilation_coefficient,
    Real & shear_strength) const
{
  using std::log10;
  using std::pow;
  using std::tan;
  const Real sigma_eff = std::max(_compressive_normal_stress_floor, sigma_n);
  jrc_mobilized = _jrc_scaled_const;
  if (_use_mobilized_jrc)
  {
    const Real sbar =
        std::max(Real(0.0), std::min(Real(1.0), cumulative_slip / _peak_shear_displacement));
    jrc_mobilized *= pow(sbar, _mobilized_jrc_exponent);
  }
  const Real ratio = std::max(Real(1.0e-30), _jcs_scaled_const / sigma_eff);
  roughness_angle_deg = jrc_mobilized * log10(ratio);
  if (!_allow_negative_roughness_angle)
    roughness_angle_deg = std::max(Real(0.0), roughness_angle_deg);
  peak_friction_angle_deg = std::max(
      _min_friction_angle_deg,
      std::min(_max_friction_angle_deg, _residual_friction_angle_deg + roughness_angle_deg));
  if (_use_decoupled_dilation)
  {
    // Decoupled mobilized dilation angle (mirrors the AD version), independent of JRC.
    const Real w = std::exp(-cumulative_slip / _dilation_decay_distance);
    Real psi = _dilation_angle_residual_deg +
               (_dilation_angle_peak_deg - _dilation_angle_residual_deg) * w;
    dilation_angle_deg = std::max(_min_dilation_angle_deg, std::min(_max_dilation_angle_deg, psi));
  }
  else
  {
    dilation_angle_deg =
        std::max(_min_dilation_angle_deg,
                 std::min(_max_dilation_angle_deg, _dilation_factor * roughness_angle_deg));
  }
  const Real deg_to_rad = M_PI / 180.0;
  friction_coefficient = tan(peak_friction_angle_deg * deg_to_rad);
  dilation_coefficient = _use_dilatancy ? tan(dilation_angle_deg * deg_to_rad) : 0.0;
  shear_strength = _cohesion + sigma_n * friction_coefficient;  // mirrors the AD version
  // Residual self-propping floor (default 0 = no-op); mirrors the AD version.
  if (_min_tau_limit > 0.0)
    shear_strength = std::max(_min_tau_limit, shear_strength);
}

Real
ADOrcaBartonBandisContactTractionFastAD::computeDilationIncrementReal(Real dilation_coefficient,
                                                                      Real plastic_slip_increment,
                                                                      Real available_closure) const
{
  if (!_use_dilatancy)
    return 0.0;
  Real dil = dilation_coefficient * plastic_slip_increment;
  if (_max_dilation_increment > 0.0)
    dil = std::min(dil, _max_dilation_increment);
  if (_cap_dilation_to_available_closure)
    dil = std::min(dil, std::max(Real(0.0), available_closure));
  return std::max(Real(0.0), dil);
}

Real
ADOrcaBartonBandisContactTractionFastAD::computeDNormalStressDPlasticSlipReal(
    Real kn_tangent, Real dilation_coefficient, Real dilation_increment, Real closure_new) const
{
  Real d_dil_d_g = 0.0;
  if (_use_dilatancy)
  {
    const bool dilation_cap_active =
        (_max_dilation_increment > 0.0 && dilation_increment >= _max_dilation_increment - 1e-14);
    const bool closure_cap_active = (_cap_dilation_to_available_closure && closure_new <= 1e-14);
    if (!dilation_cap_active && !closure_cap_active)
      d_dil_d_g = dilation_coefficient;
  }

  return kn_tangent * (_dil_closure_sign * d_dil_d_g);
}

ADReal
ADOrcaBartonBandisContactTractionFastAD::computeAdditionalShearStrength(const ADReal &, Real) const
{
  return ADReal(0.0);
}

Real
ADOrcaBartonBandisContactTractionFastAD::computeAdditionalShearStrengthReal(
    Real, Real, Real, Real & dstrength_dslip) const
{
  dstrength_dslip = 0.0;
  return 0.0;
}

void
ADOrcaBartonBandisContactTractionFastAD::carryAdditionalState()
{
}

void
ADOrcaBartonBandisContactTractionFastAD::commitAdditionalState(Real)
{
}

// =============================================================================
// Analytical derivative dR/d(delta_gamma_p) — used for NR step and IFT
// =============================================================================
Real
ADOrcaBartonBandisContactTractionFastAD::computeReturnMappingDerivative(
    Real sigma_n,
    Real kn_tangent,
    Real jrc_mobilized,
    Real roughness_angle_deg,
    Real peak_friction_angle_deg,
    Real mu,
    Real dilation_coefficient,
    Real dilation_increment,
    Real closure_new,
    Real cumulative_slip_new) const
{
  // d(dilation)/d(delta_gamma_p): zero when a cap is active
  // NOTE on decoupled dilation: when use_decoupled_dilation=true, psi_mob also depends on
  // delta_gamma_p through cumulative_slip, which adds a term
  //   d(Ddil)/dg = tan(psi) + Dg * sec^2(psi) * dpsi/ds^p
  // The second term is intentionally OMITTED here. With typical values (Dg~1e-6 m,
  // D_dil~1e-4 m, peak-residual ~1 deg) it is ~1% of tan(psi), so neglecting it only
  // slows NR convergence slightly; it does not change the converged solution (which is
  // defined by the residual R=0, not by this Jacobian). The residual itself uses the full
  // mobilized psi via computeBartonBandisProperties, so the answer remains exact.
  const Real d_sn_d_g = computeDNormalStressDPlasticSlipReal(
      kn_tangent, dilation_coefficient, dilation_increment, closure_new);

  const Real phi_rad = peak_friction_angle_deg * M_PI / 180.0;
  const Real cos2_phi = std::max(Real(1e-14), std::cos(phi_rad) * std::cos(phi_rad));
  const Real d_mu_d_phi = 1.0 / cos2_phi;
  const Real deg_to_rad = M_PI / 180.0;

  const bool ra_at_lower = (!_allow_negative_roughness_angle && roughness_angle_deg <= 0.0);
  const bool phi_at_lower = (peak_friction_angle_deg <= _min_friction_angle_deg + 1e-10);
  const bool phi_at_upper = (peak_friction_angle_deg >= _max_friction_angle_deg - 1e-10);
  const bool phi_interior = !phi_at_lower && !phi_at_upper && !ra_at_lower;

  // d(mu)/d(sigma_n) via roughness angle
  Real d_mu_d_sn = 0.0;
  if (phi_interior && sigma_n > _compressive_normal_stress_floor)
    d_mu_d_sn = d_mu_d_phi * deg_to_rad * (-jrc_mobilized / (sigma_n * std::log(Real(10.0))));

  // d(mu)/d(cumulative_slip) via JRC mobilization ramp
  Real d_mu_d_cumslip = 0.0;
  if (_use_mobilized_jrc && phi_interior)
  {
    const Real sbar =
        std::max(Real(0.0), std::min(Real(1.0), cumulative_slip_new / _peak_shear_displacement));
    if (sbar > 0.0 && sbar < 1.0)
    {
      const Real sigma_eff = std::max(_compressive_normal_stress_floor, sigma_n);
      const Real log_ratio = std::log10(std::max(Real(1e-30), _jcs_scaled_const / sigma_eff));
      const Real d_jrc_d_cumslip = _jrc_scaled_const * _mobilized_jrc_exponent *
                                   std::pow(sbar, _mobilized_jrc_exponent - Real(1.0)) /
                                   _peak_shear_displacement;
      d_mu_d_cumslip = d_mu_d_phi * deg_to_rad * d_jrc_d_cumslip * log_ratio;
    }
  }

  const Real d_taulim_d_g = mu * d_sn_d_g + sigma_n * (d_mu_d_sn * d_sn_d_g + d_mu_d_cumslip);
  return -Real(_tangential_stiffness_qp) - d_taulim_d_g;
}

// =============================================================================
// Main constitutive update
// =============================================================================
void
ADOrcaBartonBandisContactTractionFastAD::computeInterfaceTractionIncrement()
{
  using std::sqrt;

  const auto & jump = _interface_displacement_jump[_qp];
  const auto & traction_old = _interface_traction_old[_qp];
  const auto & ptj_old = _plastic_tangential_jump_old[_qp];

  const Real cumslip_old = _cumulative_plastic_slip_old[_qp];
  const Real irrev_dil_old = _irreversible_dilation_old[_qp];

  // Default (stick) state — overwritten below for slip/open
  _fracture_state[_qp] = static_cast<Real>(FractureState::Stick);
  _plastic_slip_increment[_qp] = 0.0;
  _dilation_jump_increment[_qp] = 0.0;
  _cumulative_plastic_slip[_qp] = cumslip_old;
  _irreversible_dilation[_qp] = irrev_dil_old;
  _plastic_tangential_jump[_qp] = ptj_old;
  carryAdditionalState();

  // -----------------------------------------------------------------------
  // Effective gap (ADReal — carries sensitivity to jump(0))
  // Positive gap = open, negative gap = closure.
  // -----------------------------------------------------------------------
  const ADReal old_dil_offset =
      _accumulate_irreversible_dilation ? ADReal(irrev_dil_old) : ADReal(0.0);
  // _dil_gap_sign = +1 legacy (dilation softens closure); -1 kinematic (dilation is a
  // normal eigen-opening, so at fixed total jump it INCREASES elastic closure / engages
  // asperities, and the joint must physically open to relieve it -> routed to displacement).
  // _normal_closure_offset pre-seats the joint: at zero jump the closure is already c_0,
  // so an in-situ preloaded joint starts in equilibrium (jump measures relative opening).
  const ADReal raw_effective_gap =
      jump(0) + ADReal(_dil_gap_sign) * old_dil_offset - ADReal(_normal_closure_offset);
  const ADReal raw_closure_old_ad = -raw_effective_gap;
  const Real raw_closure_old_for_update =
      std::max(Real(0.0), MetaPhysicL::raw_value(raw_closure_old_ad));

  const bool normal_unload_correction_active =
      normalUnloadRetentionEnabled() && cumslip_old >= _normal_unload_activation_slip;
  const Real retained_opening_old =
      normal_unload_correction_active
          ? std::min(raw_closure_old_for_update,
                     std::max(Real(0.0), _bb_unload_retained_opening_old[_qp]))
          : Real(0.0);
  // Reclosure stiffening is anchored at the minimum raw closure reached after activation.
  // Its default multiplier is one, so this expression is algebraically identical to the
  // legacy retention-only path unless the new control is explicitly enabled.
  const Real minimum_closure_old = normal_unload_correction_active
                                       ? std::max(Real(0.0), _bb_unload_min_closure_old[_qp])
                                       : raw_closure_old_for_update;
  const ADReal recovered_raw_closure =
      std::max(ADReal(0.0), raw_closure_old_ad - ADReal(minimum_closure_old));
  const ADReal closure_old_candidate =
      raw_closure_old_ad +
      ADReal(normal_unload_correction_active ? _normal_reclosure_stiffness_multiplier - 1.0 : 0.0) *
          recovered_raw_closure -
      ADReal(retained_opening_old);

  // -----------------------------------------------------------------------
  // Open state
  // -----------------------------------------------------------------------
  if (_contact_gap_regularization <= 0.0 && MetaPhysicL::raw_value(closure_old_candidate) <= 0.0)
  {
    updateNormalUnloadState(raw_closure_old_for_update, cumslip_old);
    _fracture_state[_qp] = static_cast<Real>(FractureState::Open);
    _limit_tau[_qp] = 0.0;
    _friction_coefficient_effective[_qp] = std::tan(_residual_friction_angle_deg * M_PI / 180.0);
    _cohesion_effective[_qp] = 0.0;
    _roughness_state[_qp] = ADReal(computeRoughnessState());
    _roughness_damage[_qp] = 1.0 - computeRoughnessState();
    _bb_compressive_normal_stress[_qp] = 0.0;
    _bb_effective_normal_stress[_qp] = 0.0;
    _bb_normal_closure[_qp] = ADReal(0.0);
    _bb_normal_stiffness_tangent[_qp] = 0.0;
    _bb_jrc_scaled[_qp] = _jrc_scaled_const;
    _bb_jcs_scaled[_qp] = _jcs_scaled_const;
    _bb_jrc_mobilized[_qp] = _use_mobilized_jrc ? 0.0 : _jrc_scaled_const;
    _bb_roughness_angle_degrees[_qp] = 0.0;
    _bb_peak_friction_angle_degrees[_qp] = _residual_friction_angle_deg;
    _bb_peak_friction_coefficient[_qp] = std::tan(_residual_friction_angle_deg * M_PI / 180.0);
    _bb_dilation_angle_degrees[_qp] = 0.0;
    _bb_dilation_coefficient[_qp] = 0.0;
    _tangential_stiffness_qp = computeTangentialStiffness(0.0);
    _bb_tangential_stiffness[_qp] = _tangential_stiffness_qp;
    // Fully open joint: no solid contact area to shield the fluid, so the entire nominal area
    // is pressure-exposed (alpha=1), matching the MC material's identical open-state value.
    _fault_pressure_area_coefficient[_qp] = ADReal(1.0);
    _interface_traction_inc[_qp] = ADRealVectorValue(0.0, 0.0, 0.0) - traction_old;
    updateReportedNormalOpening(jump(0), irrev_dil_old, cumslip_old);
    return;
  }

  // -----------------------------------------------------------------------
  // Start-of-step closure — both Real (for NR) and ADReal (for IFT pass)
  // -----------------------------------------------------------------------
  const ADReal closure_old_ad = regularizedPositive(closure_old_candidate); // carries d/d(jump_0)
  const Real closure_old_raw = MetaPhysicL::raw_value(closure_old_ad);
  const Real closure_old_unregularized_raw = MetaPhysicL::raw_value(closure_old_candidate);

  // Start-of-step BB properties (Real, for NR and diagnostics)
  Real sn_old_r, kn_old_r, jrc_old_r, ra_old_r, phi_old_r, mu_old_r, da_old_r, dc_old_r, tl_old_r;
  computeNormalStressAndTangentReal(closure_old_raw, sn_old_r, kn_old_r);
  const Real sn_strength_old_r = computeEffectiveNormalStressForStrengthReal(sn_old_r);

  // Tangential stiffness for THIS step. Evaluated on the start-of-step effective normal
  // stress so it is a constant inside the step: every return-map expression below keeps
  // its existing algebra, and only the Jacobian's dependence of k_t on jump(0) is dropped
  // (the value itself is exact). Identically _penalty_tangent unless the opt-in law is on.
  _tangential_stiffness_qp = computeTangentialStiffness(sn_strength_old_r);
  _bb_tangential_stiffness[_qp] = _tangential_stiffness_qp;
  const Real kn_strength_old_r = computeEffectiveNormalStressTangentScale(sn_old_r) * kn_old_r;
  computeBartonBandisPropertiesReal(sn_strength_old_r,
                                    cumslip_old,
                                    jrc_old_r,
                                    ra_old_r,
                                    phi_old_r,
                                    mu_old_r,
                                    da_old_r,
                                    dc_old_r,
                                    tl_old_r);

  // -----------------------------------------------------------------------
  // Trial traction (ADReal — carries sensitivity to jump(1,2))
  // Normal component uses start-of-step sigma_n.
  // -----------------------------------------------------------------------
  // For the normal traction we need ADReal sigma_n_old (depends on closure_old_ad)
  ADReal sn_old_ad, kn_old_ad;
  computeNormalStressAndTangent(closure_old_ad, sn_old_ad, kn_old_ad);

  ADRealVectorValue traction_trial;
  traction_trial(0) = -sn_old_ad;
  traction_trial(1) = ADReal(_tangential_stiffness_qp) * (jump(1) - ADReal(ptj_old(1)));
  traction_trial(2) = ADReal(_tangential_stiffness_qp) * (jump(2) - ADReal(ptj_old(2)));

  const ADReal tau_norm_trial =
      sqrt(traction_trial(1) * traction_trial(1) + traction_trial(2) * traction_trial(2));
  const Real tau_norm_trial_raw = MetaPhysicL::raw_value(tau_norm_trial);

  // Set diagnostics from start-of-step state
  _limit_tau[_qp] = tl_old_r;
  _friction_coefficient_effective[_qp] = mu_old_r;
  _cohesion_effective[_qp] = computeCohesionEffective();
  _roughness_state[_qp] = ADReal(computeRoughnessState());
  _roughness_damage[_qp] = 1.0 - computeRoughnessState();
  _bb_compressive_normal_stress[_qp] = sn_old_r;
  _bb_effective_normal_stress[_qp] = sn_strength_old_r;
  _bb_normal_closure[_qp] = closure_old_ad;
  _bb_normal_stiffness_tangent[_qp] = kn_old_r;
  _bb_jrc_scaled[_qp] = _jrc_scaled_const;
  _bb_jcs_scaled[_qp] = _jcs_scaled_const;
  _bb_jrc_mobilized[_qp] = jrc_old_r;
  _bb_roughness_angle_degrees[_qp] = ra_old_r;
  _bb_peak_friction_angle_degrees[_qp] = phi_old_r;
  _bb_peak_friction_coefficient[_qp] = mu_old_r;
  _bb_dilation_angle_degrees[_qp] = da_old_r;
  _bb_dilation_coefficient[_qp] = dc_old_r;
  // Provisional (start-of-step) value; overwritten below with the converged sn_final once the
  // return map settles, same two-pass pattern as the other diagnostics on this code path.
  _fault_pressure_area_coefficient[_qp] =
      _use_state_dependent_fault_pressure_coefficient
          ? ADReal(_fault_pressure_area_reference_stress) /
                (ADReal(_fault_pressure_area_reference_stress) + sn_old_ad)
          : ADReal(1.0);

  // -----------------------------------------------------------------------
  // Stick check (using start-of-step tau_limit)
  // -----------------------------------------------------------------------
  if (tau_norm_trial_raw <= _tangential_traction_tolerance || tau_norm_trial_raw <= tl_old_r)
  {
    // STICK-HEALING FIX (2026-07-11): a closed, stuck interface must still evolve any
    // rate-and-state variable by the aging law at V=0 (dtheta/dt = 1 -> theta += dt).
    // The default carryAdditionalState() at the top of this function froze theta during
    // stick, silently dropping the hold-stage healing that the RSF re-stick mechanism
    // depends on (the exact-integral evolveRateStateTheta(0) gives theta_old + dt).
    // commitAdditionalState(0) is a no-op in this base class, so pure BB decks are
    // byte-identical; only RSF-enabled subclasses see the (correct) healing.
    commitAdditionalState(0.0);
    updateNormalUnloadState(raw_closure_old_for_update, cumslip_old);
    _fracture_state[_qp] = static_cast<Real>(FractureState::Stick);
    _interface_traction_inc[_qp] = traction_trial - traction_old;
    updateReportedNormalOpening(jump(0), irrev_dil_old, cumslip_old);
    return;
  }

  // -----------------------------------------------------------------------
  // Safeguarded Real return map — Newton inside a physical slip-increment bracket
  // -----------------------------------------------------------------------
  Real dgp = 0.0;

  // Working Real variables (updated by every residual evaluation)
  Real sn_new_r = sn_old_r, kn_new_r = kn_old_r;
  Real sn_strength_new_r = sn_strength_old_r, kn_strength_new_r = kn_strength_old_r;
  Real jrc_new_r = jrc_old_r, ra_new_r = ra_old_r, phi_new_r = phi_old_r;
  Real mu_new_r = mu_old_r, da_new_r = da_old_r, dc_new_r = dc_old_r;
  Real tl_new_r = tl_old_r;
  Real extra_new_r = 0.0;
  Real d_extra_d_g_new = 0.0;
  Real dil_new_r = 0.0;
  Real cl_new_r = closure_old_raw;

  const Real scale = std::max(tau_norm_trial_raw, Real(1.0));
  // Perzyna tangential viscous overstress rate factor (eta/dt). Added to the return-mapping
  // residual as -visc_rate*dgp and to the derivative as -visc_rate, consistently with the IFT
  // pass below. Guarded for dt<=0 (e.g. steady/initialization) so it is a no-op there.
  // Applied at the call sites (not inside computeReturnMappingDerivative) so the slip-weakening
  // Hardening subclass override inherits it automatically.
  const Real visc_rate = (_dt > 0.0) ? _tangential_viscosity / _dt : 0.0;

  auto evaluate_return_map = [&](const Real gamma, Real & derivative)
  {
    // Dilation and contact pressure are coupled. Resolve that inexpensive scalar fixed point for
    // each gamma so the bracketed residual is deterministic (the legacy loop evaluated R with the
    // dilation coefficient left over from the previous Newton iterate).
    //
    // Convergence criterion: the iterate is tan(psi), an O(0.01..1) quantity. The previous
    // test used an ABSOLUTE 1e-12 against dc_scale = max(1, |dc|) = 1, while the update was
    // damped by 0.5 -- a linear contraction of rate 1/2. Reaching 1e-12 from a typical
    // initial mismatch of ~0.1 therefore needs ~37 iterations, but the loop was capped at 25,
    // so the fixed point reported spurious non-convergence and threw whenever the dilation
    // coefficient moved appreciably between steps. That exception cuts dt, which is a
    // plausible contributor to the dt collapse seen in the SW-S4 Barton-Bandis decks.
    //
    // Fixed by (a) making the tolerance relative to |dc| with a sensible floor, (b) using
    // direct substitution -- which is exact in one iteration whenever the dilation angle does
    // not depend on sigma_n, i.e. the whole use_decoupled_dilation family -- falling back to
    // damping only if the residual fails to contract, and (c) raising the iteration cap.
    Real dc_iter = dc_old_r;
    Real dc_residual_old = std::numeric_limits<Real>::max();
    bool dilation_converged = !_use_dilatancy;
    for (unsigned int j = 0; j < 50; ++j)
    {
      dil_new_r = computeDilationIncrementReal(dc_iter, gamma, closure_old_raw);
      const Real cl_new_unregularized =
          closure_old_unregularized_raw + _dil_closure_sign * dil_new_r;
      cl_new_r = regularizedPositiveReal(cl_new_unregularized);
      computeNormalStressAndTangentReal(cl_new_r, sn_new_r, kn_new_r);
      sn_strength_new_r = computeEffectiveNormalStressForStrengthReal(sn_new_r);
      kn_strength_new_r = computeEffectiveNormalStressTangentScale(sn_new_r) * kn_new_r *
                          regularizedPositiveDerivativeReal(cl_new_unregularized);
      computeBartonBandisPropertiesReal(sn_strength_new_r,
                                        cumslip_old + gamma,
                                        jrc_new_r,
                                        ra_new_r,
                                        phi_new_r,
                                        mu_new_r,
                                        da_new_r,
                                        dc_new_r,
                                        tl_new_r);

      const Real dc_scale = std::max(Real(1.0e-6), std::abs(dc_new_r));
      const Real dc_residual = std::abs(dc_new_r - dc_iter);
      if (dc_residual <= Real(1e-11) * dc_scale)
      {
        dilation_converged = true;
        break;
      }

      // Direct substitution while it contracts; damped bisection if it stalls or oscillates.
      dc_iter = (dc_residual < Real(0.5) * dc_residual_old)
                    ? dc_new_r
                    : Real(0.5) * (dc_iter + dc_new_r);
      dc_residual_old = dc_residual;
    }

    if (!dilation_converged)
      throw MooseException("Barton-Bandis dilation/contact fixed point did not converge at qp ",
                           _qp,
                           " (t=",
                           _t,
                           ", dt=",
                           _dt,
                           "); requesting a smaller time step.");

    const Real d_sn_d_g_extra =
        computeDNormalStressDPlasticSlipReal(kn_strength_new_r, dc_new_r, dil_new_r, cl_new_r);
    extra_new_r = computeAdditionalShearStrengthReal(
        sn_strength_new_r, gamma, d_sn_d_g_extra, d_extra_d_g_new);

    derivative = computeReturnMappingDerivative(sn_strength_new_r,
                                                kn_strength_new_r,
                                                jrc_new_r,
                                                ra_new_r,
                                                phi_new_r,
                                                mu_new_r,
                                                dc_new_r,
                                                dil_new_r,
                                                cl_new_r,
                                                cumslip_old + gamma) -
                 d_extra_d_g_new - visc_rate;
    return tau_norm_trial_raw - (_tangential_stiffness_qp + visc_rate) * gamma - tl_new_r - extra_new_r;
  };

  Real derivative = 0.0;
  Real gamma_lo = 0.0;
  Real residual_lo = evaluate_return_map(gamma_lo, derivative);
  const Real natural_upper = tau_norm_trial_raw / (_tangential_stiffness_qp + visc_rate);
  Real gamma_hi = natural_upper;
  if (_max_plastic_slip_increment > 0.0)
    gamma_hi = std::min(gamma_hi, _max_plastic_slip_increment);
  Real residual_hi = evaluate_return_map(gamma_hi, derivative);

  if (residual_lo <= scale * _relative_tolerance)
  {
    // A subclass may contribute rate-dependent strength that is not part of the inexpensive
    // preliminary stick test. Gamma=0 is then the admissible endpoint, not a plastic-slip state.
    commitAdditionalState(0.0);
    updateNormalUnloadState(raw_closure_old_for_update, cumslip_old);
    _fracture_state[_qp] = static_cast<Real>(FractureState::Stick);
    _interface_traction_inc[_qp] = traction_trial - traction_old;
    updateReportedNormalOpening(jump(0), irrev_dil_old, cumslip_old);
    return;
  }

  if (residual_hi > 0.0)
    throw MooseException(
        "Barton-Bandis return-map root is outside the admissible per-step slip increment at qp ",
        _qp,
        " (t=",
        _t,
        ", dt=",
        _dt,
        ", R(gamma_max)/scale=",
        residual_hi / scale,
        "); requesting a smaller time step.");

  dgp = std::max(
      gamma_lo,
      std::min(gamma_hi, (tau_norm_trial_raw - tl_old_r) / (_tangential_stiffness_qp + visc_rate)));
  if (dgp <= gamma_lo || dgp >= gamma_hi)
    dgp = Real(0.5) * (gamma_lo + gamma_hi);

  bool converged = false;
  Real residual = residual_lo;
  for (unsigned int i = 0; !converged && i < _max_return_mapping_iterations; ++i)
  {
    residual = evaluate_return_map(dgp, derivative);
    if (std::abs(residual) / scale < _relative_tolerance)
    {
      converged = true;
      break;
    }

    if (residual > 0.0)
      gamma_lo = dgp;
    else
      gamma_hi = dgp;

    const Real newton = (std::isfinite(derivative) && std::abs(derivative) > Real(1e-30))
                            ? dgp - residual / derivative
                            : Real(-1.0);
    dgp = (std::isfinite(newton) && newton > gamma_lo && newton < gamma_hi)
              ? newton
              : Real(0.5) * (gamma_lo + gamma_hi);
  }

  if (!converged)
    throw MooseException("Safeguarded Barton-Bandis return map did not converge within ",
                         _max_return_mapping_iterations,
                         " iterations at qp ",
                         _qp,
                         " (t=",
                         _t,
                         ", dt=",
                         _dt,
                         ", |R|/scale=",
                         std::abs(residual) / scale,
                         "); requesting a smaller time step.");

  // Leave all working state and the IFT denominator synchronized with the accepted root. This is
  // also required for the rare gamma=0 endpoint root because the bracket check evaluated gamma_hi
  // after gamma_lo.
  residual = evaluate_return_map(dgp, derivative);
  if (std::abs(residual) / scale > _relative_tolerance)
    throw MooseException("Barton-Bandis return-map state lost consistency at qp ",
                         _qp,
                         " (t=",
                         _t,
                         ", dt=",
                         _dt,
                         ", |R|/scale=",
                         std::abs(residual) / scale,
                         "); requesting a smaller time step.");

  // -----------------------------------------------------------------------
  // Compute dR_dg at the converged state (needed for IFT)
  // -----------------------------------------------------------------------
  const Real cumslip_conv = cumslip_old + dgp;
  const Real extra_conv_r = extra_new_r;
  const Real dR_dg_conv = derivative;

  // -----------------------------------------------------------------------
  // IFT: construct delta_gamma_p_AD with consistent tangent
  //
  // By the implicit function theorem on R(dgp; jump) = 0 at convergence:
  //   d(dgp)/d(DOF_k) = -(dR/d(DOF_k))_dgp_fixed / (dR/d(dgp))
  //
  // We obtain dR/d(DOF_k) by evaluating the residual as an ADReal at the
  // converged dgp (treating dgp as a zero-derivative constant).  The result
  // carries the correct sensitivity through tau_norm_trial (jump_1, jump_2)
  // and through tau_limit (closure_old_ad, pore pressure -> strength normal stress -> tau_limit).
  //
  // delta_gamma_p_AD = dgp - residual_ad / dR_dg_conv
  // -----------------------------------------------------------------------
  ADReal sn_ift, kn_ift;
  const ADReal dil_ift = computeDilationIncrement(ADReal(dc_new_r), ADReal(dgp), closure_old_ad);
  const ADReal cl_ift =
      regularizedPositive(closure_old_candidate + ADReal(_dil_closure_sign) * dil_ift);
  computeNormalStressAndTangent(cl_ift, sn_ift, kn_ift);

  ADReal jrc_ift, ra_ift, phi_ift, mu_ift, da_ift, dc_ift, tl_ift;
  const ADReal sn_strength_ift = computeEffectiveNormalStressForStrength(sn_ift);
  computeBartonBandisProperties(sn_strength_ift,
                                ADReal(cumslip_conv),
                                jrc_ift,
                                ra_ift,
                                phi_ift,
                                mu_ift,
                                da_ift,
                                dc_ift,
                                tl_ift);
  const ADReal extra_ift = computeAdditionalShearStrength(sn_strength_ift, dgp);

  // The viscous overstress term -visc_rate*dgp is included for value-consistency with the NR
  // residual. dgp is treated as a constant in the IFT pass (as elsewhere here), so this term
  // carries no DOF derivative; the full d(dgp)/d(DOF) sensitivity is recovered through
  // dR_dg_conv, which already includes -visc_rate.
  const ADReal residual_ad = tau_norm_trial - ADReal(_tangential_stiffness_qp) * ADReal(dgp) - tl_ift -
                             extra_ift - ADReal(visc_rate) * ADReal(dgp);

  ADReal dgp_AD = ADReal(dgp);
  if (std::abs(dR_dg_conv) > Real(1e-30))
    dgp_AD = ADReal(dgp) - residual_ad / ADReal(dR_dg_conv);
  dgp_AD = std::max(ADReal(0.0), dgp_AD);
  if (_max_plastic_slip_increment > 0.0)
    dgp_AD = std::min(dgp_AD, ADReal(_max_plastic_slip_increment));

  // -----------------------------------------------------------------------
  // Final state with delta_gamma_p_AD
  // Use converged dilation_coeff (dc_new_r) as a constant so the circularity
  // in the dilation-closure relationship is broken consistently with the NR.
  // The sensitivity to dgp (and hence to jump components) flows through dgp_AD.
  // -----------------------------------------------------------------------
  const ADReal dil_final = computeDilationIncrement(ADReal(dc_new_r), dgp_AD, closure_old_ad);
  const ADReal cl_final =
      regularizedPositive(closure_old_candidate + ADReal(_dil_closure_sign) * dil_final);
  ADReal sn_final, kn_final;
  computeNormalStressAndTangent(cl_final, sn_final, kn_final);

  ADReal jrc_final, ra_final, phi_final, mu_final, da_final, dc_final, tl_final;
  const ADReal sn_strength_final = computeEffectiveNormalStressForStrength(sn_final);
  computeBartonBandisProperties(sn_strength_final,
                                ADReal(cumslip_conv),
                                jrc_final,
                                ra_final,
                                phi_final,
                                mu_final,
                                da_final,
                                dc_final,
                                tl_final);

  // Slip direction (Real unit vector from trial traction)
  const Real n1 = (tau_norm_trial_raw > 0.0)
                      ? MetaPhysicL::raw_value(traction_trial(1)) / tau_norm_trial_raw
                      : 0.0;
  const Real n2 = (tau_norm_trial_raw > 0.0)
                      ? MetaPhysicL::raw_value(traction_trial(2)) / tau_norm_trial_raw
                      : 0.0;

  // New traction (ADReal: dgp_AD carries the consistent tangent)
  ADRealVectorValue traction_new;
  traction_new(0) = -sn_final;
  traction_new(1) =
      ADReal(_tangential_stiffness_qp) * (jump(1) - ADReal(ptj_old(1)) - dgp_AD * ADReal(n1));
  traction_new(2) =
      ADReal(_tangential_stiffness_qp) * (jump(2) - ADReal(ptj_old(2)) - dgp_AD * ADReal(n2));

  // Committed Real values for stateful properties
  const Real ptj_new_1 = ptj_old(1) + dgp * n1;
  const Real ptj_new_2 = ptj_old(2) + dgp * n2;
  const Real irrev_dil_new =
      _accumulate_irreversible_dilation ? irrev_dil_old + MetaPhysicL::raw_value(dil_final) : 0.0;
  const Real raw_closure_final_for_update =
      std::max(Real(0.0),
               raw_closure_old_for_update + _dil_closure_sign * MetaPhysicL::raw_value(dil_final));

  // -----------------------------------------------------------------------
  // Open-due-to-dilation check: dilation drove the joint to full opening
  // -----------------------------------------------------------------------
  if (_contact_gap_regularization <= 0.0 &&
      (MetaPhysicL::raw_value(cl_final) <= 0.0 ||
       MetaPhysicL::raw_value(traction_new(0)) > _normal_traction_tolerance))
  {
    commitAdditionalState(dgp);
    updateNormalUnloadState(raw_closure_final_for_update, cumslip_conv);
    _fracture_state[_qp] = static_cast<Real>(FractureState::Open);
    _limit_tau[_qp] = 0.0;
    _plastic_slip_increment[_qp] = dgp;
    _dilation_jump_increment[_qp] = dil_final;
    _cumulative_plastic_slip[_qp] = cumslip_conv;
    _irreversible_dilation[_qp] = irrev_dil_new;
    _plastic_tangential_jump[_qp] = RealVectorValue(0.0, ptj_new_1, ptj_new_2);
    _friction_coefficient_effective[_qp] = mu_new_r;
    _cohesion_effective[_qp] = 0.0;
    _roughness_state[_qp] = ADReal(computeRoughnessState());
    _roughness_damage[_qp] = 1.0 - computeRoughnessState();
    _bb_compressive_normal_stress[_qp] = 0.0;
    _bb_effective_normal_stress[_qp] = 0.0;
    _bb_normal_closure[_qp] = ADReal(0.0);
    _bb_normal_stiffness_tangent[_qp] = 0.0;
    _bb_jrc_scaled[_qp] = _jrc_scaled_const;
    _bb_jcs_scaled[_qp] = _jcs_scaled_const;
    _bb_jrc_mobilized[_qp] = jrc_new_r;
    _bb_roughness_angle_degrees[_qp] = ra_new_r;
    _bb_peak_friction_angle_degrees[_qp] = phi_new_r;
    _bb_peak_friction_coefficient[_qp] = mu_new_r;
    _bb_dilation_angle_degrees[_qp] = 0.0;
    _bb_dilation_coefficient[_qp] = 0.0;
    _tangential_stiffness_qp = computeTangentialStiffness(0.0);
    _bb_tangential_stiffness[_qp] = _tangential_stiffness_qp;
    // Dilation drove the joint fully open: same alpha=1 open-state convention as above.
    _fault_pressure_area_coefficient[_qp] = ADReal(1.0);
    _interface_traction_inc[_qp] = ADRealVectorValue(0.0, 0.0, 0.0) - traction_old;
    updateReportedNormalOpening(jump(0), irrev_dil_new, cumslip_conv);
    return;
  }

  // -----------------------------------------------------------------------
  // Commit slip state
  // -----------------------------------------------------------------------
  commitAdditionalState(dgp);
  updateNormalUnloadState(raw_closure_final_for_update, cumslip_conv);
  _fracture_state[_qp] = static_cast<Real>(FractureState::Slip);
  _limit_tau[_qp] = tl_new_r + extra_conv_r;
  _plastic_slip_increment[_qp] = dgp;
  _dilation_jump_increment[_qp] = dil_final;
  _cumulative_plastic_slip[_qp] = cumslip_conv;
  _irreversible_dilation[_qp] = irrev_dil_new;
  _plastic_tangential_jump[_qp] = RealVectorValue(0.0, ptj_new_1, ptj_new_2);
  _friction_coefficient_effective[_qp] = mu_new_r;
  _cohesion_effective[_qp] = computeCohesionEffective();
  _roughness_state[_qp] = ADReal(computeRoughnessState());
  _roughness_damage[_qp] = 1.0 - computeRoughnessState();
  _bb_compressive_normal_stress[_qp] = MetaPhysicL::raw_value(sn_final);
  _bb_effective_normal_stress[_qp] = MetaPhysicL::raw_value(sn_strength_final);
  _bb_normal_closure[_qp] = cl_final;
  _bb_normal_stiffness_tangent[_qp] = MetaPhysicL::raw_value(kn_final);
  _bb_jrc_scaled[_qp] = _jrc_scaled_const;
  _bb_jcs_scaled[_qp] = _jcs_scaled_const;
  _bb_jrc_mobilized[_qp] = jrc_new_r;
  _bb_roughness_angle_degrees[_qp] = ra_new_r;
  _bb_peak_friction_angle_degrees[_qp] = phi_new_r;
  _bb_peak_friction_coefficient[_qp] = mu_new_r;
  _bb_dilation_angle_degrees[_qp] = da_new_r;
  _bb_dilation_coefficient[_qp] = dc_new_r;
  // Converged (end-of-step) value, using the same sn_final consumed by the traction update.
  _fault_pressure_area_coefficient[_qp] =
      _use_state_dependent_fault_pressure_coefficient
          ? ADReal(_fault_pressure_area_reference_stress) /
                (ADReal(_fault_pressure_area_reference_stress) + sn_final)
          : ADReal(1.0);

  _interface_traction_inc[_qp] = traction_new - traction_old;
  updateReportedNormalOpening(jump(0), irrev_dil_new, cumslip_conv);
}
