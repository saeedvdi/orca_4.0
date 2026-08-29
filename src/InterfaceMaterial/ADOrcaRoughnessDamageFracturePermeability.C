#include "ADOrcaRoughnessDamageFracturePermeability.h"

#include "metaphysicl/raw_type.h"

#include <algorithm>
#include <cmath>

registerMooseObject("OrcaApp", ADOrcaRoughnessDamageFracturePermeability);
registerMooseObjectAliased("OrcaApp",
                           ADOrcaRoughnessDamageFracturePermeability,
                           "OrcaRoughnessDamageFracturePermeability");

InputParameters
ADOrcaRoughnessDamageFracturePermeability::validParams()
{
  InputParameters params = InterfaceMaterial::validParams();
  params.addClassDescription(
      "Compute hydraulic aperture and fracture permeability using mechanical opening, "
      "cumulative irreversible dilation, and roughness-dependent self-propping retention.");

  params.addParam<std::string>("base_name", "", "Material property base name.");

  params.addParam<MaterialPropertyName>("mechanical_aperture_name",
                                        "mechanical_aperture",
                                        "Mechanical aperture property name.");
  params.addParam<MaterialPropertyName>("dilation_jump_increment_name",
                                        "dilation_jump_increment",
                                        "Plastic dilation increment property name.");
  params.addParam<MaterialPropertyName>("roughness_name",
                                        "roughness_state",
                                        "Roughness state property name.");

  params.addParam<MaterialPropertyName>("hydraulic_aperture_name",
                                        "hydraulic_aperture",
                                        "Output hydraulic aperture property name.");
  params.addParam<MaterialPropertyName>("fracture_permeability_name",
                                        "fracture_permeability",
                                        "Output fracture permeability property name.");
  params.addParam<MaterialPropertyName>("cumulative_dilation_name",
                                        "cumulative_dilation",
                                        "Output cumulative dilation property name.");
  params.addParam<MaterialPropertyName>(
      "transmissibility_name",
      "fracture_transmissivity",
      "Optional output property name for cubic-law fracture transmissivity a_h^3/(12*mu). "
      "The parameter name is kept for compatibility with older inputs.");
  params.addParam<MaterialPropertyName>("roughness_retention_factor_name",
                                        "roughness_retention_factor",
                                        "Diagnostic output property for retention factor.");
  params.addParam<MaterialPropertyName>("self_propping_aperture_name",
                                        "self_propping_aperture",
                                        "Diagnostic output property for self-propping aperture.");

  params.addRangeCheckedParam<Real>("initial_hydraulic_aperture",
                                    0.0,
                                    "initial_hydraulic_aperture >= 0.0",
                                    "Reference hydraulic aperture a_h0 (m).");
  params.addParam<Real>("aperture_scale",
                        1.0,
                        "Scale factor on reversible mechanical aperture contribution.");
  params.addRangeCheckedParam<Real>(
      "normal_stress_aperture_compliance",
      0.0,
      "normal_stress_aperture_compliance >= 0.0",
      "Optional reversible hydraulic aperture compliance with effective normal stress (m/Pa). "
      "When positive, adds normal_stress_aperture_compliance * "
      "(reference_effective_normal_stress - N_eff) to the hydraulic aperture, where N_eff is "
      "compression-positive and is inferred from effective_normal_traction_name. The default 0 "
      "preserves the legacy roughness/dilation-only aperture law.");
  params.addRangeCheckedParam<Real>(
      "reference_effective_normal_stress",
      0.0,
      "reference_effective_normal_stress >= 0.0",
      "Compression-positive effective normal stress (Pa) at which initial_hydraulic_aperture is "
      "defined for the optional normal-stress aperture term.");
  params.addParam<bool>(
      "use_nonlinear_normal_closure",
      false,
      "When true, replace the LINEAR normal-stress aperture term "
      "(normal_stress_aperture_compliance * (reference_effective_normal_stress - N_eff)) with a "
      "Barton-Bandis HYPERBOLIC reversible closure: opening(N) = V_m * (g(ref) - g(N)), clamped >= 0, "
      "with g(s) = s / (V_m*K_ni + s). This is soft at low N (opens more at peak injection) and stiff "
      "at high N (closes fast on re-compression toward the reference), matching the convex joint-closure "
      "the linear term cannot capture at peak and mid-unload simultaneously. Requires "
      "bb_max_aperture_closure and bb_initial_normal_stiffness. Default false = legacy linear term "
      "(byte-identical).");
  params.addRangeCheckedParam<Real>(
      "bb_max_aperture_closure",
      0.0,
      "bb_max_aperture_closure >= 0.0",
      "Barton-Bandis V_m (m): the asymptotic reversible aperture range as N_eff -> 0. Only used when "
      "use_nonlinear_normal_closure = true.");
  params.addRangeCheckedParam<Real>(
      "bb_initial_normal_stiffness",
      0.0,
      "bb_initial_normal_stiffness >= 0.0",
      "Barton-Bandis K_ni (Pa/m): initial (low-stress) normal stiffness. The half-closure stress is "
      "sigma_0 = V_m*K_ni (where the closure fraction g = 1/2). Only used when "
      "use_nonlinear_normal_closure = true and nonlinear_closure_type = barton_bandis.");
  params.addRangeCheckedParam<Real>(
      "bb_stress_exponent",
      1.0,
      "bb_stress_exponent >= 1.0",
      "Power-law exponent p on the Barton-Bandis closure fraction g(s) = s^p / (sigma_0^p + s^p), "
      "sigma_0 = V_m*K_ni. p = 1 is the standard hyperbola (compliance decays as 1/s^2, max stiffening "
      "over [s_lo,s_hi] = (s_hi/s_lo)^2). p > 1 stiffens faster (1/s^(p+1), ceiling (s_hi/s_lo)^(p+1)) "
      "while remaining BOUNDED by V_m -- needed because the SW-S4 unloading closure stiffens ~3.2x, "
      "above the p=1 ceiling of 2.1x; p=2 gives (s_hi/s_lo)^3 ~ 3.2x. Default 1.0 = standard hyperbola.");
  params.addParam<MooseEnum>(
      "nonlinear_closure_type",
      MooseEnum("barton_bandis exponential", "barton_bandis"),
      "Which nonlinear reversible closure to use when use_nonlinear_normal_closure = true. "
      "'barton_bandis' = hyperbolic (see bb_* params). 'exponential' = stress_aperture(N) = "
      "exp_closure_amplitude * exp(-(N - exp_closure_reference_stress)/exp_closure_stress_scale), "
      "an exponentially-stiffening closure that reproduces closure stiffening steeper than a single "
      "Barton-Bandis hyperbola can (the SW-S4 unloading branch stiffens ~3.2x, above the hyperbola's "
      "structural ceiling of ~2.1x; the exponential fits it to <0.7% RMSE).");
  params.addRangeCheckedParam<Real>(
      "exp_closure_amplitude",
      0.0,
      "exp_closure_amplitude >= 0.0",
      "Exponential closure amplitude A (m): the reversible aperture opening at N_eff = "
      "exp_closure_reference_stress. Only used when nonlinear_closure_type = exponential.");
  params.addRangeCheckedParam<Real>(
      "exp_closure_stress_scale",
      1.0,
      "exp_closure_stress_scale > 0.0",
      "Exponential closure stress scale sigma_c (Pa): the e-folding effective normal stress over which "
      "the reversible aperture changes. Smaller sigma_c = sharper stiffening. Only used when "
      "nonlinear_closure_type = exponential.");
  params.addRangeCheckedParam<Real>(
      "exp_closure_reference_stress",
      0.0,
      "exp_closure_reference_stress >= 0.0",
      "Compression-positive effective normal stress N_ref (Pa) at which the exponential closure opening "
      "equals exp_closure_amplitude. Only used when nonlinear_closure_type = exponential.");
  params.addParam<MaterialPropertyName>(
      "effective_normal_traction_name",
      "czm_sigma_n",
      "Scalar local normal traction property used by the optional normal-stress aperture term. "
      "The sign convention is tension positive, compression negative.");
  params.addParam<MaterialPropertyName>(
      "normal_stress_aperture_name",
      "normal_stress_aperture",
      "Diagnostic output property for the reversible normal-stress aperture term (m).");
  params.addParam<MaterialPropertyName>(
      "effective_normal_compression_name",
      "effective_normal_compression",
      "Diagnostic output property for compression-positive effective normal stress (Pa).");
  params.addParam<bool>(
      "compute_effective_normal_compression",
      false,
      "Couple effective_normal_traction_name and export the compression-positive effective "
      "normal stress as a DIAGNOSTIC even when no aperture term consumes it. Without this the "
      "diagnostic is identically zero whenever normal_stress_aperture_compliance = 0 and "
      "use_nonlinear_normal_closure = false -- which silently zeroed the sigma'_n validation "
      "panel once the redundant second closure model was removed from the aperture law. "
      "Requires the named traction property to exist.");
  params.addParam<Real>("dilation_scale",
                        1.0,
                        "Scale factor on cumulative irreversible dilation contribution. "
                        "Ignored when use_kinematic_aperture=true.");
  params.addParam<bool>("use_kinematic_aperture",
                        false,
                        "OPT-IN (default false). Set true when the contact material has "
                        "dilation_opens_joint=true. In that mode the dilation already appears in "
                        "the mechanical gap (routed into the displacement field), so the separate "
                        "dilation_scale*cumulative_dilation term here is dropped to avoid double "
                        "counting: a_h = a_h0 + aperture_scale*mechanical_aperture (+ self-prop). "
                        "cumulative_dilation is still accumulated and output for diagnostics.");
  params.addRangeCheckedParam<Real>("min_hydraulic_aperture",
                                    1e-12,
                                    "min_hydraulic_aperture >= 0.0",
                                    "Lower bound on hydraulic aperture.");
  params.addRangeCheckedParam<Real>("max_hydraulic_aperture",
                                    0.0,
                                    "max_hydraulic_aperture >= 0.0",
                                    "Upper bound on hydraulic aperture (m); 0 disables. Bounds the "
                                    "cubic transmissivity so a transient mechanical-gap excursion "
                                    "cannot blow up the permeability and wreck the HM Newton solve.");

  params.addRangeCheckedParam<Real>("retention_residual",
                                    0.2,
                                    "retention_residual >= 0.0 & retention_residual <= 1.0",
                                    "Residual retention factor when roughness is fully degraded.");
  params.addRangeCheckedParam<Real>("self_propping_scale",
                                    0.0,
                                    "self_propping_scale >= 0.0",
                                    "Additional aperture contribution from remaining roughness.");
  params.addRangeCheckedParam<Real>("self_propping_exponent",
                                    1.0,
                                    "self_propping_exponent > 0.0",
                                    "Exponent on roughness in self-propping term.");

  // --- slip-damage (gouge-fill) aperture reduction ---
  params.addParam<bool>(
      "use_slip_damage",
      false,
      "OPT-IN (default false). When true, subtract a shear-driven gouge-fill aperture that "
      "saturates with cumulative plastic slip: a_h -= slip_damage_scale * "
      "(1 - exp(-cumulative_plastic_slip / slip_damage_characteristic_slip)). Models wear/gouge "
      "progressively filling the void as the joint shears, so the hydraulic aperture stops "
      "tracking the sigma'_n-driven mechanical re-opening 1:1. Zero at zero slip, so it leaves "
      "the baseline unchanged.");
  params.addRangeCheckedParam<Real>(
      "slip_damage_scale",
      0.0,
      "slip_damage_scale >= 0.0",
      "Maximum gouge-fill aperture reduction (m) at full slip damage. Used only when "
      "use_slip_damage=true.");
  params.addRangeCheckedParam<Real>(
      "slip_damage_characteristic_slip",
      1e-3,
      "slip_damage_characteristic_slip > 0.0",
      "Characteristic cumulative plastic slip (m) over which the gouge-fill saturates. "
      "Used only when use_slip_damage=true.");
  params.addRangeCheckedParam<Real>(
      "slip_damage_onset_slip",
      0.0,
      "slip_damage_onset_slip >= 0.0",
      "Cumulative-plastic-slip threshold s* (m) below which NO gouge-fill accrues; the saturation is "
      "measured from s* instead of 0: a_h -= slip_damage_scale * (1 - exp(-<s - s*>_+ / "
      "slip_damage_characteristic_slip)). Default 0 = legacy (fills from first slip). A positive s* keeps "
      "the LOADING branch open (early slip produces no flow-blocking gouge) while still filling by the "
      "large-slip unloading branch -- the physical loading/unloading aperture asymmetry (gouge is produced "
      "and mobilized late, not on first slip). Used only when use_slip_damage=true.");
  params.addParam<MaterialPropertyName>(
      "cumulative_plastic_slip_name",
      "cumulative_plastic_slip",
      "Cumulative plastic (shear) slip property name from the coupled contact material.");
  params.addParam<bool>(
      "cumulative_plastic_slip_is_ad",
      true,
      "Whether the contact material declares the cumulative-plastic-slip property as AD "
      "(default true, e.g. the decoupled-dilation-roughness laws). Set false for contact "
      "laws that export it as a plain (non-AD) property, e.g. the FastAD Barton-Bandis "
      "family. The gouge-fill only reads the raw value, so no Jacobian information is lost.");
  params.addParam<MaterialPropertyName>(
      "slip_damage_aperture_name",
      "slip_damage_aperture",
      "Diagnostic output property for the gouge-fill aperture reduction (m).");

  // --- time-dependent closure creep (pressure solution / asperity indentation) ---
  params.addParam<bool>(
      "use_closure_creep",
      false,
      "OPT-IN (default false). When true, subtract a TIME-dependent closure from the hydraulic "
      "aperture: da_c/dt = (1/closure_creep_time) * (<N_eff>_+/closure_creep_reference_stress)^q * "
      "(closure_creep_max_aperture - a_c), integrated implicitly. This is the only term in the "
      "aperture budget that advances with time alone -- every other term is a function of the "
      "current stress or of a history variable monotone in slip, so without it a joint held at "
      "constant pressure is stationary to machine precision. Models pressure solution / asperity "
      "indentation progressively closing a loaded joint over 1e5-1e7 s. Zero at t=0 and frozen "
      "(not reversed) whenever the joint is open, so it leaves the baseline unchanged.");
  params.addRangeCheckedParam<Real>(
      "closure_creep_max_aperture",
      0.0,
      "closure_creep_max_aperture >= 0.0",
      "Asymptotic creep closure a_c_max (m) the aperture loses at long time. Used only when "
      "use_closure_creep=true; zero makes the term a no-op even when the flag is set.");
  params.addRangeCheckedParam<Real>(
      "closure_creep_time",
      1.0e5,
      "closure_creep_time > 0.0",
      "Creep time constant tau_c (s) AT THE REFERENCE STRESS. The effective time constant is "
      "tau_c * (closure_creep_reference_stress/N_eff)^q, so a joint held above the reference "
      "stress creeps faster. Used only when use_closure_creep=true.");
  params.addRangeCheckedParam<Real>(
      "closure_creep_reference_stress",
      1.0e6,
      "closure_creep_reference_stress > 0.0",
      "Effective normal stress (Pa) at which the creep time constant equals closure_creep_time. "
      "Used only when use_closure_creep=true.");
  params.addRangeCheckedParam<Real>(
      "closure_creep_stress_exponent",
      1.0,
      "closure_creep_stress_exponent >= 0.0",
      "Exponent q in rate ~ (N_eff/sigma_ref)^q. 1.0 is the linear pressure-solution scaling "
      "(rate proportional to the stress at the contacts); 0.0 removes the stress dependence and "
      "leaves a pure first-order relaxation. Used only when use_closure_creep=true.");
  params.addParam<MaterialPropertyName>(
      "closure_creep_aperture_name",
      "closure_creep_aperture",
      "Diagnostic (and stateful) output property for the accumulated creep closure (m).");

  params.addParam<bool>(
      "compute_transmissibility",
      true,
      "If true, also compute cubic-law fracture transmissivity a_h^3/(12*mu), as expected "
      "by OrcaFractureFlowInterfaceKernel. The parameter name is kept for compatibility "
      "with older inputs.");
  params.addRangeCheckedParam<Real>("fluid_viscosity",
                                    1.002e-3,
                                    "fluid_viscosity > 0.0",
                                    "Fluid dynamic viscosity (Pa.s).");
  params.addRangeCheckedParam<Real>("fault_thickness",
                                    1e-3,
                                    "fault_thickness > 0.0",
                                    "Kept for compatibility with older inputs; the current "
                                    "fracture-flow kernel uses a_h^3/(12*mu) and does not "
                                    "need a separate fault-thickness factor.");

  return params;
}

ADOrcaRoughnessDamageFracturePermeability::ADOrcaRoughnessDamageFracturePermeability(
    const InputParameters & parameters)
  : InterfaceMaterial(parameters),
    _base_name(isParamValid("base_name") && !getParam<std::string>("base_name").empty()
                   ? getParam<std::string>("base_name") + "_"
                   : ""),
    _mechanical_aperture(
        getADMaterialPropertyByName<Real>(getParam<MaterialPropertyName>("mechanical_aperture_name"))),
    _dilation_jump_increment(getParam<bool>("use_kinematic_aperture")
                                 ? nullptr
                                 : &getADMaterialPropertyByName<Real>(
                                       _base_name +
                                       getParam<MaterialPropertyName>("dilation_jump_increment_name"))),
    _roughness_state(getParam<bool>("use_kinematic_aperture")
                         ? nullptr
                         : &getADMaterialPropertyByName<Real>(
                               _base_name + getParam<MaterialPropertyName>("roughness_name"))),
    _cumulative_plastic_slip(
        (getParam<bool>("use_slip_damage") && getParam<bool>("cumulative_plastic_slip_is_ad"))
            ? &getADMaterialPropertyByName<Real>(
                  _base_name + getParam<MaterialPropertyName>("cumulative_plastic_slip_name"))
            : nullptr),
    _cumulative_plastic_slip_nonad(
        (getParam<bool>("use_slip_damage") && !getParam<bool>("cumulative_plastic_slip_is_ad"))
            ? &getMaterialPropertyByName<Real>(
                  _base_name + getParam<MaterialPropertyName>("cumulative_plastic_slip_name"))
            : nullptr),
    _effective_normal_traction(
        (getParam<Real>("normal_stress_aperture_compliance") > 0.0 ||
         getParam<bool>("use_nonlinear_normal_closure") ||
         getParam<bool>("compute_effective_normal_compression") ||
         getParam<bool>("use_closure_creep"))
            ? &getADMaterialPropertyByName<Real>(
                  _base_name + getParam<MaterialPropertyName>("effective_normal_traction_name"))
            : nullptr),
    _cumulative_dilation(
        declareADPropertyByName<Real>(getParam<MaterialPropertyName>("cumulative_dilation_name"))),
    _cumulative_dilation_old(
        getMaterialPropertyOldByName<Real>(getParam<MaterialPropertyName>("cumulative_dilation_name"))),
    _closure_creep_aperture(declareADPropertyByName<Real>(
        getParam<MaterialPropertyName>("closure_creep_aperture_name"))),
    _closure_creep_aperture_old(getMaterialPropertyOldByName<Real>(
        getParam<MaterialPropertyName>("closure_creep_aperture_name"))),
    _hydraulic_aperture(
        declareADPropertyByName<Real>(getParam<MaterialPropertyName>("hydraulic_aperture_name"))),
    _fracture_permeability(
        declareADPropertyByName<Real>(getParam<MaterialPropertyName>("fracture_permeability_name"))),
    _transmissivity(getParam<bool>("compute_transmissibility")
                        ? &declareADPropertyByName<Real>(
                              getParam<MaterialPropertyName>("transmissibility_name"))
                        : nullptr),
    _roughness_retention_factor(declareADPropertyByName<Real>(
        getParam<MaterialPropertyName>("roughness_retention_factor_name"))),
    _self_propping_aperture(
        declareADPropertyByName<Real>(getParam<MaterialPropertyName>("self_propping_aperture_name"))),
    _slip_damage_aperture(
        declareADPropertyByName<Real>(getParam<MaterialPropertyName>("slip_damage_aperture_name"))),
    _normal_stress_aperture(
        declareADPropertyByName<Real>(getParam<MaterialPropertyName>("normal_stress_aperture_name"))),
    _effective_normal_compression(declareADPropertyByName<Real>(
        getParam<MaterialPropertyName>("effective_normal_compression_name"))),
    _a_h0(getParam<Real>("initial_hydraulic_aperture")),
    _aperture_scale(getParam<Real>("aperture_scale")),
    _normal_stress_aperture_compliance(getParam<Real>("normal_stress_aperture_compliance")),
    _reference_effective_normal_stress(getParam<Real>("reference_effective_normal_stress")),
    _use_nonlinear_normal_closure(getParam<bool>("use_nonlinear_normal_closure")),
    _compute_effective_normal_compression(getParam<bool>("compute_effective_normal_compression")),
    _nonlinear_closure_type(getParam<MooseEnum>("nonlinear_closure_type")),
    _bb_max_aperture_closure(getParam<Real>("bb_max_aperture_closure")),
    _bb_initial_normal_stiffness(getParam<Real>("bb_initial_normal_stiffness")),
    _bb_stress_exponent(getParam<Real>("bb_stress_exponent")),
    _exp_closure_amplitude(getParam<Real>("exp_closure_amplitude")),
    _exp_closure_stress_scale(getParam<Real>("exp_closure_stress_scale")),
    _exp_closure_reference_stress(getParam<Real>("exp_closure_reference_stress")),
    _dilation_scale(getParam<Real>("dilation_scale")),
    _use_kinematic_aperture(getParam<bool>("use_kinematic_aperture")),
    _min_aperture(getParam<Real>("min_hydraulic_aperture")),
    _max_aperture(getParam<Real>("max_hydraulic_aperture")),
    _retention_residual(getParam<Real>("retention_residual")),
    _self_propping_scale(getParam<Real>("self_propping_scale")),
    _self_propping_exponent(getParam<Real>("self_propping_exponent")),
    _compute_transmissivity(getParam<bool>("compute_transmissibility")),
    _fluid_viscosity(getParam<Real>("fluid_viscosity")),
    _fault_thickness(getParam<Real>("fault_thickness")),
    _use_slip_damage(getParam<bool>("use_slip_damage")),
    _slip_damage_scale(getParam<Real>("slip_damage_scale")),
    _slip_damage_char_slip(getParam<Real>("slip_damage_characteristic_slip")),
    _slip_damage_onset_slip(getParam<Real>("slip_damage_onset_slip")),
    _use_closure_creep(getParam<bool>("use_closure_creep")),
    _closure_creep_max_aperture(getParam<Real>("closure_creep_max_aperture")),
    _closure_creep_time(getParam<Real>("closure_creep_time")),
    _closure_creep_reference_stress(getParam<Real>("closure_creep_reference_stress")),
    _closure_creep_stress_exponent(getParam<Real>("closure_creep_stress_exponent"))
{
  if (_use_nonlinear_normal_closure)
  {
    if (_nonlinear_closure_type == 0 &&
        (_bb_max_aperture_closure <= 0.0 || _bb_initial_normal_stiffness <= 0.0))
      paramError("use_nonlinear_normal_closure",
                 "nonlinear_closure_type = barton_bandis requires bb_max_aperture_closure and "
                 "bb_initial_normal_stiffness to both be positive.");
    if (_nonlinear_closure_type == 1 && _exp_closure_amplitude <= 0.0)
      paramError("use_nonlinear_normal_closure",
                 "nonlinear_closure_type = exponential requires exp_closure_amplitude > 0.");
  }
}

void
ADOrcaRoughnessDamageFracturePermeability::initQpStatefulProperties()
{
  _cumulative_dilation[_qp] = 0.0;
  _closure_creep_aperture[_qp] = 0.0;
  _normal_stress_aperture[_qp] = 0.0;
  _effective_normal_compression[_qp] = 0.0;

  // The hydraulic aperture is stateful whenever a consumer requests its old value -- in
  // particular OrcaFractureFlowInterfaceKernel, whose storage term is (a_h - a_h_old)/dt.
  // Leaving it unset here made a_h_old = 0 on the first step, so that term injected the ENTIRE
  // reference aperture as a spurious fluid source in one time step (observed as a 14x spike in
  // the first-step injection flux of the SW-S4 decks).
  //
  // At the reference state the stress-aperture term vanishes by construction
  // (stress_aperture(reference_effective_normal_stress) = 0) and no dilation or gouge has
  // accumulated, so a_h(t=0) = a_h0 + self_propping(R=1), subject to the same bounds as
  // computeQpProperties. (R = 1 is the undamaged joint; the contact material's roughness
  // property is not yet available during stateful initialization.)
  Real a_h0 = _a_h0 + _self_propping_scale;
  if (a_h0 < _min_aperture)
    a_h0 = _min_aperture;
  if (_max_aperture > 0.0 && a_h0 > _max_aperture)
    a_h0 = _max_aperture;

  _hydraulic_aperture[_qp] = ADReal(a_h0);
  _fracture_permeability[_qp] = ADReal(a_h0 * a_h0 / 12.0);
  if (_compute_transmissivity && _transmissivity)
    (*_transmissivity)[_qp] = ADReal(a_h0 * a_h0 * a_h0 / (12.0 * _fluid_viscosity));
}

void
ADOrcaRoughnessDamageFracturePermeability::computeQpProperties()
{
  using std::pow;

  ADReal d_inc = _dilation_jump_increment ? (*_dilation_jump_increment)[_qp] : ADReal(0.0);
  if (MetaPhysicL::raw_value(d_inc) < 0.0)
    d_inc = ADReal(0.0);

  _cumulative_dilation[_qp] = _cumulative_dilation_old[_qp] + d_inc;

  // No roughness coupling in kinematic mode -> treat the joint as fully rough (R=1).
  const ADReal R = _roughness_state
                       ? std::max(ADReal(0.0), std::min(ADReal(1.0), (*_roughness_state)[_qp]))
                       : ADReal(1.0);
  const ADReal retention_factor =
      ADReal(_retention_residual) + (ADReal(1.0) - ADReal(_retention_residual)) * R;
  const ADReal self_prop = ADReal(_self_propping_scale) * pow(R, _self_propping_exponent);

  _roughness_retention_factor[_qp] = retention_factor;
  _self_propping_aperture[_qp] = self_prop;

  // Legacy: dilation fed separately via dilation_scale (the over-feed that inflates k).
  // Kinematic mode: dilation already lives in mechanical_aperture (displacement field),
  // so drop the separate term to avoid double counting. cumulative_dilation is still
  // tracked above for diagnostics/output.
  const ADReal dilation_term = _use_kinematic_aperture
                                   ? ADReal(0.0)
                                   : ADReal(_dilation_scale) * _cumulative_dilation[_qp] * retention_factor;

  // Slip-damage (gouge-fill): a shear-driven aperture reduction that saturates with cumulative
  // plastic slip. Models wear/gouge progressively filling the void as the joint shears, so the
  // hydraulic aperture stops tracking the sigma'_n-driven mechanical re-opening 1:1 -> decouples
  // the reported permeability from the closure (effective-stress) response. Zero at zero slip,
  // so the baseline is unchanged. Read explicitly (no Jacobian term) as a slow history variable.
  Real slip_damage_fill = 0.0;
  if (_use_slip_damage && (_cumulative_plastic_slip || _cumulative_plastic_slip_nonad) &&
      _slip_damage_scale > 0.0)
  {
    const Real s = std::max(
        0.0,
        _cumulative_plastic_slip ? MetaPhysicL::raw_value((*_cumulative_plastic_slip)[_qp])
                                 : (*_cumulative_plastic_slip_nonad)[_qp]);
    // Gouge accrues only past the onset threshold s* (measured from s*, not 0). s* = 0 -> legacy.
    const Real s_eff = std::max(0.0, s - _slip_damage_onset_slip);
    slip_damage_fill = _slip_damage_scale * (1.0 - std::exp(-s_eff / _slip_damage_char_slip));
  }
  _slip_damage_aperture[_qp] = ADReal(slip_damage_fill);

  ADReal effective_normal_compression = 0.0;
  ADReal stress_aperture = 0.0;
  if (_effective_normal_traction)
  {
    const ADReal traction_n = (*_effective_normal_traction)[_qp];
    effective_normal_compression =
        MetaPhysicL::raw_value(traction_n) < 0.0 ? -traction_n : ADReal(0.0);
    // The aperture CONTRIBUTION is still gated on the aperture terms being enabled; only the
    // diagnostic above is unconditional.
    if (_normal_stress_aperture_compliance > 0.0 || _use_nonlinear_normal_closure)
      stress_aperture = computeStressAperture(effective_normal_compression);
  }
  _effective_normal_compression[_qp] = effective_normal_compression;
  _normal_stress_aperture[_qp] = stress_aperture;

  // Time-dependent closure creep (pressure solution / asperity indentation), OPT-IN.
  //   da_c/dt = r * (a_c_max - a_c),   r = (1/tau_c) * (<N_eff>_+ / sigma_ref)^q
  // Integrated IMPLICITLY over the step -- a_c = (a_c_old + r dt a_c_max)/(1 + r dt) -- because a
  // long-hold deck spans dt from 0.05 s inside the slip event to hundreds of seconds during the
  // hold, and the explicit update is unstable once r*dt > 2. The implicit form is unconditionally
  // stable and monotone, and reproduces the exact exponential to O(r dt).
  //
  // Read explicitly from the RAW effective normal stress (no Jacobian term), the same treatment
  // the gouge-fill above gets and for the same reason: it is a slow history variable, so the
  // dropped coupling costs Newton nothing on the time scale over which it moves.
  //
  // The rate vanishes for an open joint (N_eff = 0), so creep FREEZES rather than reverses when
  // the fracture is pressurised back open. Pressure solution does not undo.
  Real closure_creep = 0.0;
  if (_use_closure_creep && _closure_creep_max_aperture > 0.0)
  {
    const Real n_eff = std::max(0.0, MetaPhysicL::raw_value(effective_normal_compression));
    const Real rate =
        (_closure_creep_stress_exponent == 0.0
             ? 1.0
             : std::pow(n_eff / _closure_creep_reference_stress, _closure_creep_stress_exponent)) /
        _closure_creep_time;
    const Real r_dt = std::max(0.0, rate * _dt);
    const Real a_c_old = std::max(0.0, _closure_creep_aperture_old[_qp]);
    closure_creep = (a_c_old + r_dt * _closure_creep_max_aperture) / (1.0 + r_dt);
    closure_creep = std::min(closure_creep, _closure_creep_max_aperture);
  }
  _closure_creep_aperture[_qp] = ADReal(closure_creep);

  ADReal a_h = ADReal(_a_h0) + stress_aperture +
               ADReal(_aperture_scale) * _mechanical_aperture[_qp] + dilation_term + self_prop -
               ADReal(slip_damage_fill) - ADReal(closure_creep);

  if (MetaPhysicL::raw_value(a_h) < _min_aperture)
    a_h = ADReal(_min_aperture);
  // Cap the hydraulic aperture. The cubic transmissivity (a_h^3) makes a transient mechanical-gap
  // excursion (e.g. before contact is established under a ramping confinement) blow the
  // permeability up by orders of magnitude, which wrecks the HM Newton solve (residual chatter).
  // The cap bounds the aperture to a physical maximum and keeps the coupling well-conditioned.
  if (_max_aperture > 0.0 && MetaPhysicL::raw_value(a_h) > _max_aperture)
    a_h = ADReal(_max_aperture);

  _hydraulic_aperture[_qp] = a_h;
  _fracture_permeability[_qp] = (a_h * a_h) / 12.0;

  if (_compute_transmissivity && _transmissivity)
    (*_transmissivity)[_qp] = (a_h * a_h * a_h) / (12.0 * _fluid_viscosity);
}

ADReal
ADOrcaRoughnessDamageFracturePermeability::computeStressAperture(
    const ADReal & effective_normal_compression)
{
  // Reversible normal-stress aperture (the "backbone" closure). Selected by nonlinear_closure_type:
  //  - barton_bandis (power-law): opening(N) = V_m*(g(ref) - g(N)), g(s)=s^p/(sigma_0^p+s^p),
  //    sigma_0 = V_m*K_ni. p=1 is the standard hyperbola; p>1 stiffens faster, bounded by V_m.
  //  - exponential: opening(N) = A*exp(-(N - N_ref)/sigma_c) (stiffens exponentially with compression).
  //  - linear (default): opening(N) = C_n*(ref - N).
  // Subclasses (e.g. hysteretic) override this and call it as the single-path backbone.
  if (_use_nonlinear_normal_closure && _nonlinear_closure_type == 0)
  {
    const Real sigma0 = _bb_max_aperture_closure * _bb_initial_normal_stiffness;
    const Real p = _bb_stress_exponent;
    const Real sigma0_p = std::pow(sigma0, p);
    const Real ref_p = std::pow(_reference_effective_normal_stress, p);
    const Real g_ref = ref_p / (sigma0_p + ref_p);
    const ADReal n_p = pow(effective_normal_compression, p);
    const ADReal g_n = n_p / (ADReal(sigma0_p) + n_p);
    ADReal stress_aperture = ADReal(_bb_max_aperture_closure) * (ADReal(g_ref) - g_n);
    if (MetaPhysicL::raw_value(stress_aperture) < 0.0)
      stress_aperture = ADReal(0.0);
    return stress_aperture;
  }
  else if (_use_nonlinear_normal_closure && _nonlinear_closure_type == 1)
  {
    const ADReal exp_arg =
        -(effective_normal_compression - ADReal(_exp_closure_reference_stress)) /
        ADReal(_exp_closure_stress_scale);
    return ADReal(_exp_closure_amplitude) * exp(exp_arg);
  }
  return ADReal(_normal_stress_aperture_compliance) *
         (ADReal(_reference_effective_normal_stress) - effective_normal_compression);
}
