#include "ADOrcaDecoupledDilationRoughnessContactTraction.h"

#include "metaphysicl/raw_type.h"

#include <algorithm>
#include <cmath>
#include <limits>

registerMooseObject("OrcaApp", ADOrcaDecoupledDilationRoughnessContactTraction);
registerMooseObjectAliased("OrcaApp",
                           ADOrcaDecoupledDilationRoughnessContactTraction,
                           "OrcaDecoupledDilationRoughnessContactTraction");

InputParameters
ADOrcaDecoupledDilationRoughnessContactTraction::validParams()
{
  InputParameters params = OrcaCZMComputeLocalTractionIncrementalBase::validParams();
  params.addClassDescription(
      "Roughness-damage Coulomb contact law with stable roughness-controlled strength evolution "
      "and a separate cumulative-slip-based dilation decay law.");

  params.addParam<std::string>("base_name", "Material property base name");

  // FIX (Warning): penalty_normal now range-checked to > 0 to prevent silent division-by-zero.
  params.addRangeCheckedParam<Real>(
      "penalty_normal", "penalty_normal > 0.0", "Normal penalty stiffness.");
  params.addParam<Real>(
      "penalty_tangent", 0.0, "Tangential penalty stiffness (defaults to penalty_normal).");

  params.addParam<Real>(
      "normal_traction_tolerance", 0.0, "Open-state threshold on normal traction.");
  params.addParam<Real>("tangential_traction_tolerance",
                        1e-16,
                        "Tolerance for tangential traction norm.");

  params.addParam<bool>("use_dilatancy",
                        true,
                        "If true, use the separate dilation-decay law during slip.");

  params.addRangeCheckedParam<Real>(
      "tangential_viscosity",
      0.0,
      "tangential_viscosity >= 0.0",
      "Duvaut-Lions/Perzyna viscous (rate) regularization of the frictional slip (Pa.s/m). Adds "
      "tangential_viscosity/dt to the return-mapping denominator so the retained shear overstress "
      "equals tangential_viscosity * slip_rate. 0 disables (rate-independent, original behavior). "
      "A small positive value is negligible under slow loading but turns a pressure-driven slip "
      "burst into a smooth rate-limited slide, letting the quasi-static Newton solve traverse a "
      "stick-slip instability that the rate-independent law cannot resolve. Same pattern as "
      "OrcaCZMMohrCoulombFriction's 'viscosity' and ADOrcaBartonBandisContactTractionFastAD's "
      "'tangential_viscosity'.");

  params.addParam<bool>(
      "dilation_opens_joint",
      false,
      "If false (default, legacy) shear dilation is applied as a tensile increment to the normal "
      "traction (dilation softens normal compression, so the kinematic normal jump CLOSES). If "
      "true, dilation is applied as dilatant HARDENING (compressive increment), which routes the "
      "dilation into the joint OPENING: against the surrounding stiffness the kinematic normal "
      "jump physically opens by ~tan(psi)*plastic_slip, reproducing a standard non-associated "
      "dilatant joint and letting dn track the shear-dilation signal. The return-mapping "
      "denominator is flipped consistently (Kt + mu*Kn*tan(psi)), which is also unconditionally "
      "positive (more stable than the legacy Kt - mu*Kn*tan(psi)). Pair with "
      "use_kinematic_aperture=true in ADOrcaRoughnessDamageFracturePermeability to avoid "
      "double-counting the dilation in the hydraulic aperture.");

  params.addRangeCheckedParam<Real>("initial_roughness",
                                    1.0,
                                    "initial_roughness >= 0.0 & initial_roughness <= 1.0",
                                    "Initial normalized roughness state R0.");
  params.addRangeCheckedParam<Real>("residual_roughness",
                                    0.2,
                                    "residual_roughness >= 0.0 & residual_roughness <= 1.0",
                                    "Residual normalized roughness after asperity degradation.");
  params.addRangeCheckedParam<Real>("roughness_decay_distance",
                                    1e-5,
                                    "roughness_decay_distance > 0.0",
                                    "Characteristic plastic slip distance (m) for roughness degradation.");

  params.addParam<Real>("friction_coefficient_rough",
                        0.6,
                        "Friction coefficient for fully rough state R=1.");
  params.addParam<Real>("friction_coefficient_smooth",
                        0.4,
                        "Friction coefficient for smooth / degraded state.");
  params.addRangeCheckedParam<Real>("friction_roughness_exponent",
                                    1.0,
                                    "friction_roughness_exponent > 0.0",
                                    "Exponent in mu(R).");

  params.addParam<Real>("cohesion_rough", 0.0, "Cohesion for fully rough state R=1.");
  params.addParam<Real>("cohesion_smooth", 0.0, "Cohesion for smooth / degraded state.");
  params.addRangeCheckedParam<Real>("cohesion_roughness_exponent",
                                    1.0,
                                    "cohesion_roughness_exponent > 0.0",
                                    "Exponent in c(R).");

  params.addRangeCheckedParam<Real>("dilation_angle_peak_degrees",
                                    2.0,
                                    "dilation_angle_peak_degrees >= 0.0 & "
                                        "dilation_angle_peak_degrees < 89.9",
                                    "Peak dilation angle in degrees.");
  params.addRangeCheckedParam<Real>("dilation_angle_residual_degrees",
                                    0.0,
                                    "dilation_angle_residual_degrees >= 0.0 & "
                                        "dilation_angle_residual_degrees < 89.9",
                                    "Residual dilation angle in degrees after full dilation decay.");
  params.addRangeCheckedParam<Real>("dilation_decay_distance",
                                    1e-4,
                                    "dilation_decay_distance > 0.0",
                                    "Characteristic cumulative plastic slip distance (m) for "
                                    "dilation decay.");
  params.addRangeCheckedParam<Real>("dilation_decay_exponent",
                                    1.0,
                                    "dilation_decay_exponent > 0.0",
                                    "Exponent controlling the dilation-state decay shape.");
  params.addRangeCheckedParam<Real>(
      "dilation_support_reference",
      0.0,
      "dilation_support_reference >= 0.0",
      "Reference compressive normal traction magnitude (Pa) below which dilatancy starts to fade. "
      "Set to 0 to disable support-modulated dilatancy.");
  params.addRangeCheckedParam<Real>(
      "dilation_support_exponent",
      1.0,
      "dilation_support_exponent > 0.0",
      "Exponent controlling how sharply dilatancy fades with loss of compressive support.");
  params.addRangeCheckedParam<Real>(
      "dilation_high_normal_reference",
      0.0,
      "dilation_high_normal_reference >= 0.0",
      "Reference compressive normal traction magnitude (Pa) above which asperity crushing/wear "
      "suppresses dilatancy. Set to 0 to disable high-normal-stress suppression.");
  params.addRangeCheckedParam<Real>(
      "dilation_high_normal_exponent",
      1.0,
      "dilation_high_normal_exponent > 0.0",
      "Exponent controlling how strongly dilatancy is suppressed at high compressive normal stress.");
  params.addRangeCheckedParam<Real>(
      "max_plastic_slip_increment",
      0.0,
      "max_plastic_slip_increment >= 0.0",
      "Maximum allowed plastic slip increment per constitutive update (m). "
      "Set to 0 to disable capping.");
  params.addRangeCheckedParam<Real>(
      "max_dilation_increment",
      0.0,
      "max_dilation_increment >= 0.0",
      "Maximum allowed dilation opening increment per constitutive update (m). "
      "Set to 0 to disable capping.");
  params.addRangeCheckedParam<Real>(
      "normal_strength_retention_factor",
      0.0,
      "normal_strength_retention_factor >= 0.0 & normal_strength_retention_factor <= 1.0",
      "Fraction of previous compressive normal traction retained in the Coulomb strength "
      "calculation during unloading. 0 disables memory; larger values preserve post-failure "
      "shear strength during sudden opening/unloading.");
  params.addRangeCheckedParam<Real>(
      "retained_shear_support_factor",
      0.0,
      "retained_shear_support_factor >= 0.0 & retained_shear_support_factor <= 1.0",
      "Fraction of previously mobilized shear support retained as an effective post-peak "
      "support floor during slip. 0 disables the feature.");
  params.addRangeCheckedParam<Real>(
      "retained_shear_support_decay_distance",
      1e-4,
      "retained_shear_support_decay_distance > 0.0",
      "Characteristic cumulative plastic slip distance (m) over which retained post-peak "
      "shear support decays.");
  params.addParam<bool>("use_irreversible_dilation_target",
                        false,
                        "If true, compute dilation opening from a cumulative-slip-based target "
                        "instead of directly from tan(psi) * delta_gamma_p.");
  params.addRangeCheckedParam<Real>("max_irreversible_dilation",
                                    0.0,
                                    "max_irreversible_dilation >= 0.0",
                                    "Asymptotic irreversible dilation opening (m) for the "
                                    "cumulative-slip target law.");
  params.addRangeCheckedParam<Real>("irreversible_dilation_distance",
                                    1e-4,
                                    "irreversible_dilation_distance > 0.0",
                                    "Characteristic cumulative plastic slip distance (m) for the "
                                    "irreversible dilation target law.");
  params.addRangeCheckedParam<Real>("irreversible_dilation_exponent",
                                    1.0,
                                    "irreversible_dilation_exponent > 0.0",
                                    "Exponent controlling the irreversible dilation target shape.");
  params.addRangeCheckedParam<Real>(
      "reversible_closure_compliance",
      0.0,
      "reversible_closure_compliance >= 0.0",
      "Optional reversible fracture-normal closure compliance (m/Pa) activated during unloading. "
      "The material tracks the minimum compressive normal traction reached after loading/slip; "
      "when compression recovers, this compliance converts the recovery into a reversible closing "
      "offset that subtracts from shear-induced dilation. 0 disables.");
  params.addRangeCheckedParam<Real>(
      "reversible_closure_activation_slip",
      0.0,
      "reversible_closure_activation_slip >= 0.0",
      "Cumulative plastic slip (m) required before reversible unloading closure is allowed. "
      "The minimum-compression history is still tracked before activation.");
  params.addRangeCheckedParam<Real>(
      "max_reversible_closure",
      0.0,
      "max_reversible_closure >= 0.0",
      "Optional cap (m) on the reversible unloading closure. 0 disables the cap.");

  return params;
}

ADOrcaDecoupledDilationRoughnessContactTraction::
    ADOrcaDecoupledDilationRoughnessContactTraction(const InputParameters & parameters)
  : OrcaCZMComputeLocalTractionIncrementalBase(parameters),
    _penalty_normal(getParam<Real>("penalty_normal")),
    _penalty_tangent(getParam<Real>("penalty_tangent") > 0.0 ? getParam<Real>("penalty_tangent")
                                                              : getParam<Real>("penalty_normal")),
    _normal_traction_tolerance(getParam<Real>("normal_traction_tolerance")),
    _tangential_traction_tolerance(getParam<Real>("tangential_traction_tolerance")),
    _use_dilatancy(getParam<bool>("use_dilatancy")),
    _tangential_viscosity(getParam<Real>("tangential_viscosity")),
    _dilation_opens_joint(getParam<bool>("dilation_opens_joint")),
    _dil_sign(_dilation_opens_joint ? -1.0 : 1.0),
    _initial_roughness(getParam<Real>("initial_roughness")),
    _residual_roughness(getParam<Real>("residual_roughness")),
    _roughness_decay_distance(getParam<Real>("roughness_decay_distance")),
    _friction_coefficient_rough(getParam<Real>("friction_coefficient_rough")),
    _friction_coefficient_smooth(getParam<Real>("friction_coefficient_smooth")),
    _friction_roughness_exponent(getParam<Real>("friction_roughness_exponent")),
    _cohesion_rough(getParam<Real>("cohesion_rough")),
    _cohesion_smooth(getParam<Real>("cohesion_smooth")),
    _cohesion_roughness_exponent(getParam<Real>("cohesion_roughness_exponent")),
    _dilation_angle_peak_degrees(getParam<Real>("dilation_angle_peak_degrees")),
    _dilation_angle_residual_degrees(getParam<Real>("dilation_angle_residual_degrees")),
    _dilation_decay_distance(getParam<Real>("dilation_decay_distance")),
    _dilation_decay_exponent(getParam<Real>("dilation_decay_exponent")),
    _dilation_support_reference(getParam<Real>("dilation_support_reference")),
    _dilation_support_exponent(getParam<Real>("dilation_support_exponent")),
    _max_plastic_slip_increment(getParam<Real>("max_plastic_slip_increment")),
    _max_dilation_increment(getParam<Real>("max_dilation_increment")),
    _normal_strength_retention_factor(getParam<Real>("normal_strength_retention_factor")),
    _retained_shear_support_factor(getParam<Real>("retained_shear_support_factor")),
    _retained_shear_support_decay_distance(getParam<Real>("retained_shear_support_decay_distance")),
    _use_irreversible_dilation_target(getParam<bool>("use_irreversible_dilation_target")),
    _max_irreversible_dilation(getParam<Real>("max_irreversible_dilation")),
    _irreversible_dilation_distance(getParam<Real>("irreversible_dilation_distance")),
    _irreversible_dilation_exponent(getParam<Real>("irreversible_dilation_exponent")),
    _reversible_closure_compliance(getParam<Real>("reversible_closure_compliance")),
    _reversible_closure_activation_slip(getParam<Real>("reversible_closure_activation_slip")),
    _max_reversible_closure(getParam<Real>("max_reversible_closure")),
    _fracture_state(declareADProperty<Real>(_base_name + "fracture_state")),
    _limit_tau(declareADProperty<Real>(_base_name + "limit_tau")),
    _plastic_slip_increment(declareADProperty<Real>(_base_name + "plastic_slip_increment")),
    _dilation_jump_increment(declareADProperty<Real>(_base_name + "dilation_jump_increment")),
    _cumulative_plastic_slip(declareADProperty<Real>(_base_name + "cumulative_plastic_slip")),
    _cumulative_plastic_slip_old(getMaterialPropertyOld<Real>(_base_name + "cumulative_plastic_slip")),
    _friction_coefficient_effective(
        declareADProperty<Real>(_base_name + "friction_coefficient_effective")),
    _cohesion_effective(declareADProperty<Real>(_base_name + "cohesion_effective")),
    _dilation_angle_effective(declareADProperty<Real>(_base_name + "dilation_angle_effective")),
    _dilation_state(declareADProperty<Real>(_base_name + "dilation_state")),
    _dilation_support_factor(declareADProperty<Real>(_base_name + "dilation_support_factor")),
    _roughness_state(declareADProperty<Real>(_base_name + "roughness_state")),
    _roughness_state_old(getMaterialPropertyOld<Real>(_base_name + "roughness_state")),
    _roughness_damage(declareADProperty<Real>(_base_name + "roughness_damage")),
    _strength_normal_memory(declareADProperty<Real>(_base_name + "strength_normal_memory")),
    _strength_normal_memory_old(getMaterialPropertyOld<Real>(_base_name + "strength_normal_memory")),
    _retained_shear_support(declareADProperty<Real>(_base_name + "retained_shear_support")),
    _retained_shear_support_old(getMaterialPropertyOld<Real>(_base_name + "retained_shear_support")),
    _irreversible_dilation(declareADProperty<Real>(_base_name + "irreversible_dilation")),
    _irreversible_dilation_old(getMaterialPropertyOld<Real>(_base_name + "irreversible_dilation")),
    _reversible_closure(declareADProperty<Real>(_base_name + "reversible_closure")),
    _reversible_closure_old(getMaterialPropertyOld<Real>(_base_name + "reversible_closure")),
    _reversible_closure_min_compression(
        declareADProperty<Real>(_base_name + "reversible_closure_min_compression")),
    _reversible_closure_min_compression_old(
        getMaterialPropertyOld<Real>(_base_name + "reversible_closure_min_compression")),
    _plastic_tangential_jump(
        declareADProperty<RealVectorValue>(_base_name + "plastic_tangential_jump")),
    _plastic_tangential_jump_old(
        getMaterialPropertyOld<RealVectorValue>(_base_name + "plastic_tangential_jump"))
{
  if (_residual_roughness > _initial_roughness)
    paramError("residual_roughness", "Must be <= initial_roughness.");
}

void
ADOrcaDecoupledDilationRoughnessContactTraction::initQpStatefulProperties()
{
  OrcaCZMComputeLocalTractionIncrementalBase::initQpStatefulProperties();
  _cumulative_plastic_slip[_qp] = 0.0;
  _roughness_state[_qp] = _initial_roughness;
  _roughness_damage[_qp] = 1.0 - _initial_roughness;
  _plastic_slip_increment[_qp] = 0.0;
  _dilation_jump_increment[_qp] = 0.0;
  _fracture_state[_qp] = static_cast<Real>(FractureState::Stick);
  _limit_tau[_qp] = 0.0;
  _friction_coefficient_effective[_qp] = _friction_coefficient_rough;
  _cohesion_effective[_qp] = _cohesion_rough;
  _dilation_angle_effective[_qp] = _dilation_angle_peak_degrees;
  _dilation_state[_qp] = 1.0;
  _dilation_support_factor[_qp] = 1.0;
  _strength_normal_memory[_qp] = 0.0;
  _retained_shear_support[_qp] = 0.0;
  _irreversible_dilation[_qp] = 0.0;
  _reversible_closure[_qp] = 0.0;
  _reversible_closure_min_compression[_qp] = std::numeric_limits<Real>::max();
  _plastic_tangential_jump[_qp] = RealVectorValue(0.0, 0.0, 0.0);
}

void
ADOrcaDecoupledDilationRoughnessContactTraction::computeStrengthDependentProperties(
    const ADReal & roughness, ADReal & friction_eff, ADReal & cohesion_eff) const
{
  using std::pow;

  const ADReal R = std::max(ADReal(_residual_roughness), std::min(ADReal(1.0), roughness));

  const ADReal friction_weight = pow(R, _friction_roughness_exponent);
  friction_eff = _friction_coefficient_smooth +
                 (_friction_coefficient_rough - _friction_coefficient_smooth) * friction_weight;

  const ADReal cohesion_weight = pow(R, _cohesion_roughness_exponent);
  cohesion_eff = _cohesion_smooth + (_cohesion_rough - _cohesion_smooth) * cohesion_weight;
}

void
ADOrcaDecoupledDilationRoughnessContactTraction::computeDilationDependentProperties(
    const ADReal & cumulative_plastic_slip,
    ADReal & dilation_state,
    ADReal & dilation_angle_deg_eff,
    ADReal & tan_dilation_eff) const
{
  using std::exp;
  using std::pow;
  using std::tan;

  if (!_use_dilatancy)
  {
    dilation_state = 0.0;
    dilation_angle_deg_eff = 0.0;
    tan_dilation_eff = 0.0;
    return;
  }

  const ADReal normalized_slip = cumulative_plastic_slip / ADReal(_dilation_decay_distance);
  dilation_state = exp(-pow(std::max(ADReal(0.0), normalized_slip), _dilation_decay_exponent));
  dilation_state = std::max(ADReal(0.0), std::min(ADReal(1.0), dilation_state));

  dilation_angle_deg_eff =
      ADReal(_dilation_angle_residual_degrees) +
      (ADReal(_dilation_angle_peak_degrees) - ADReal(_dilation_angle_residual_degrees)) *
          dilation_state;
  tan_dilation_eff = tan(dilation_angle_deg_eff * ADReal(M_PI / 180.0));
}

ADReal
ADOrcaDecoupledDilationRoughnessContactTraction::updateRoughness(
    const ADReal & roughness_old, const ADReal & plastic_slip_increment) const
{
  using std::exp;

  if (MetaPhysicL::raw_value(plastic_slip_increment) <= 0.0)
    return roughness_old;

  const ADReal R_old = std::max(ADReal(_residual_roughness), std::min(ADReal(1.0), roughness_old));
  ADReal R_new = ADReal(_residual_roughness) +
                 (R_old - ADReal(_residual_roughness)) *
                     exp(-plastic_slip_increment / ADReal(_roughness_decay_distance));
  R_new = std::max(ADReal(_residual_roughness), std::min(ADReal(1.0), R_new));
  return R_new;
}

ADReal
ADOrcaDecoupledDilationRoughnessContactTraction::computeIrreversibleDilationTarget(
    const ADReal & cumulative_plastic_slip, const ADReal & dilation_support_factor) const
{
  using std::exp;
  using std::pow;

  if (!_use_irreversible_dilation_target || !_use_dilatancy || _max_irreversible_dilation <= 0.0)
    return ADReal(0.0);

  const ADReal normalized_slip =
      std::max(ADReal(0.0), cumulative_plastic_slip / ADReal(_irreversible_dilation_distance));
  ADReal growth =
      ADReal(1.0) - exp(-pow(normalized_slip, ADReal(_irreversible_dilation_exponent)));
  growth = std::max(ADReal(0.0), std::min(ADReal(1.0), growth));
  return ADReal(_max_irreversible_dilation) * growth * dilation_support_factor;
}

ADReal
ADOrcaDecoupledDilationRoughnessContactTraction::updateStrengthNormalMemory(
    const ADReal & memory_old, const ADReal & traction_normal_current) const
{
  const ADReal current_compressive = std::min(traction_normal_current, ADReal(0.0));

  if (_normal_strength_retention_factor <= 0.0)
    return current_compressive;

  // Compression is negative. If the current traction is more compressive than the stored value,
  // update immediately. If it unloads toward zero/tension, retain a fraction of the previous
  // compressive support to avoid an unrealistically abrupt post-failure strength collapse.
  if (MetaPhysicL::raw_value(current_compressive) <= MetaPhysicL::raw_value(memory_old))
    return current_compressive;

  return ADReal(_normal_strength_retention_factor) * memory_old +
         (ADReal(1.0) - ADReal(_normal_strength_retention_factor)) * current_compressive;
}

ADReal
ADOrcaDecoupledDilationRoughnessContactTraction::computeDilationSupportFactor(
    const ADReal & strength_normal_memory) const
{
  using std::pow;

  const ADReal compression_mag = std::max(ADReal(0.0), -strength_normal_memory);

  // Low-normal-stress suppression: when contact support is too small, asperities cannot
  // generate meaningful shear-induced dilation. Set dilation_support_reference = 0 to disable.
  ADReal low_stress_factor = ADReal(1.0);
  if (_dilation_support_reference > 0.0)
  {
    ADReal normalized = compression_mag / ADReal(_dilation_support_reference);
    normalized = std::max(ADReal(0.0), std::min(ADReal(1.0), normalized));
    low_stress_factor = pow(normalized, ADReal(_dilation_support_exponent));
  }

  // High-normal-stress suppression: very large compression crushes/wears asperities and reduces
  // dilation. This makes the support factor bell-shaped: small compression gives little dilation,
  // moderate compression gives full dilation, and very high compression suppresses dilation again.
  const Real high_normal_reference = getParam<Real>("dilation_high_normal_reference");
  const Real high_normal_exponent = getParam<Real>("dilation_high_normal_exponent");
  ADReal high_stress_factor = ADReal(1.0);
  if (high_normal_reference > 0.0)
  {
    const ADReal ratio = ADReal(high_normal_reference) / (compression_mag + ADReal(1e-30));
    high_stress_factor = std::min(ADReal(1.0), pow(ratio, ADReal(high_normal_exponent)));
  }

  return std::max(ADReal(0.0), std::min(ADReal(1.0), low_stress_factor * high_stress_factor));
}

ADReal
ADOrcaDecoupledDilationRoughnessContactTraction::updateRetainedShearSupport(
    const ADReal & support_old,
    const ADReal & reference_support,
    const ADReal & plastic_slip_increment) const
{
  using std::exp;

  if (_retained_shear_support_factor <= 0.0)
    return ADReal(0.0);

  ADReal decayed = support_old;
  if (MetaPhysicL::raw_value(plastic_slip_increment) > 0.0)
    decayed = support_old *
              exp(-plastic_slip_increment / ADReal(_retained_shear_support_decay_distance));

  return std::max(decayed, std::max(ADReal(0.0), reference_support));
}

void
ADOrcaDecoupledDilationRoughnessContactTraction::computeReversibleClosureState(
    const ADReal & normal_traction,
    const ADReal & cumulative_plastic_slip,
    const ADReal & dilation_opening_bound,
    ADReal & reversible_closure,
    ADReal & min_compression) const
{
  // NOTE (stability): the caller passes the PREVIOUS converged normal traction here (an old
  // material property with no derivatives), NOT the within-iteration trial traction. The closure
  // is therefore an explicit, lagged offset with zero self-feedback in the tangent. Driving it
  // from the live trial traction instead would inject a normal-stiffness feedback of gain
  // penalty_normal * reversible_closure_compliance; with the calibrated values that gain is ~12,
  // which flips the effective normal tangent stiffness NEGATIVE during unloading (penalty*(1 -
  // penalty*C_n)) and destroys Newton convergence exactly in the recovery phase. Lagging removes
  // that feedback while leaving the (slowly varying) closure history physically unchanged.
  const ADReal compression = std::max(ADReal(0.0), -normal_traction);
  const Real min_old_raw = _reversible_closure_min_compression_old[_qp];
  const bool min_initialized = min_old_raw < 0.5 * std::numeric_limits<Real>::max();

  min_compression = min_initialized ? ADReal(min_old_raw) : compression;
  if (MetaPhysicL::raw_value(compression) > _normal_traction_tolerance)
    min_compression = std::min(min_compression, compression);

  reversible_closure = ADReal(0.0);
  if (_reversible_closure_compliance <= 0.0 ||
      MetaPhysicL::raw_value(cumulative_plastic_slip) < _reversible_closure_activation_slip)
    return;

  const ADReal compression_recovery = std::max(ADReal(0.0), compression - min_compression);
  reversible_closure = ADReal(_reversible_closure_compliance) * compression_recovery;
  if (_max_reversible_closure > 0.0)
    reversible_closure = std::min(reversible_closure, ADReal(_max_reversible_closure));

  // PHYSICAL BOUND: reversible closure can at most undo the dilation-induced opening; it can never
  // close the joint tighter than its undilated baseline. Clamping to the accumulated dilation
  // opening keeps the net normal offset (dilation - closure) non-tensile, so the closure term by
  // itself can never push the trial normal traction into tension and spuriously open the interface.
  reversible_closure =
      std::min(reversible_closure, std::max(ADReal(0.0), dilation_opening_bound));
}

void
ADOrcaDecoupledDilationRoughnessContactTraction::computeInterfaceTractionIncrement()
{
  using std::sqrt;

  const auto & jump = _interface_displacement_jump[_qp];
  const auto & jump_old = _interface_displacement_jump_old[_qp];
  const auto & traction_old = _interface_traction_old[_qp];
  const auto & plastic_tangential_jump_old = _plastic_tangential_jump_old[_qp];

  const ADReal cumulative_slip_old = _cumulative_plastic_slip_old[_qp];
  const ADReal roughness_old = _roughness_state_old[_qp];

  ADReal mu_old;
  ADReal cohesion_old;
  computeStrengthDependentProperties(roughness_old, mu_old, cohesion_old);

  ADReal dilation_state_old;
  ADReal dilation_angle_old_deg;
  ADReal tan_dilation_old;
  computeDilationDependentProperties(
      cumulative_slip_old, dilation_state_old, dilation_angle_old_deg, tan_dilation_old);

  // Local tangent d(g_n^p)/d(gamma_p) used in the return-mapping denominator. This keeps the
  // denominator consistent with the selected dilation law. For the target law, the tangent is the
  // derivative of the cumulative irreversible dilation target with respect to cumulative plastic
  // slip. For the direct law, it is simply tan(psi) times the normal-stress support factor.
  const auto effectiveDilationTangent = [&](const ADReal & cumulative_slip,
                                            const ADReal & tan_dilation,
                                            const ADReal & support_factor) -> ADReal
  {
    using std::exp;
    using std::pow;

    if (!_use_dilatancy)
      return ADReal(0.0);

    if (!_use_irreversible_dilation_target || _max_irreversible_dilation <= 0.0)
      return tan_dilation * support_factor;

    const ADReal x = std::max(
        ADReal(1e-30), cumulative_slip / ADReal(_irreversible_dilation_distance));
    const ADReal m = ADReal(_irreversible_dilation_exponent);
    const ADReal target_tangent =
        ADReal(_max_irreversible_dilation) * exp(-pow(x, m)) * m *
        pow(x, m - ADReal(1.0)) / ADReal(_irreversible_dilation_distance) * support_factor;

    return std::max(ADReal(0.0), target_tangent);
  };

  const auto dilationIncrementFromSlip = [&](const ADReal & cumulative_slip_old_local,
                                             const ADReal & cumulative_slip_new_local,
                                             const ADReal & delta_gamma_local,
                                             const ADReal & tan_dilation,
                                             const ADReal & support_factor) -> ADReal
  {
    if (!_use_dilatancy || MetaPhysicL::raw_value(delta_gamma_local) <= 0.0)
      return ADReal(0.0);

    if (_use_irreversible_dilation_target)
    {
      const ADReal dilation_target_new =
          computeIrreversibleDilationTarget(cumulative_slip_new_local, support_factor);
      const ADReal dilation_target_old =
          computeIrreversibleDilationTarget(cumulative_slip_old_local, support_factor);
      return std::max(ADReal(0.0), dilation_target_new - dilation_target_old);
    }

    return tan_dilation * support_factor * delta_gamma_local;
  };

  // Incremental return-mapping form.
  // The normal trial traction is advanced from the previous converged traction because this
  // class does not store an independent plastic/irreversible normal jump offset. The tangential
  // trial traction is written in total elastic-offset form using the stored plastic tangential
  // jump. The plastic slip increment below remains incremental; accumulated slip only controls
  // history-dependent strength, roughness, and dilation degradation.
  ADRealVectorValue traction_trial;
  traction_trial(0) = ADReal(_penalty_normal) * (jump(0) - jump_old(0)) + traction_old(0);
  traction_trial(1) =
      ADReal(_penalty_tangent) * (jump(1) - ADReal(plastic_tangential_jump_old(1)));
  traction_trial(2) =
      ADReal(_penalty_tangent) * (jump(2) - ADReal(plastic_tangential_jump_old(2)));
  ADRealVectorValue plastic_tangential_jump_new(0.0,
                                                plastic_tangential_jump_old(1),
                                                plastic_tangential_jump_old(2));

  ADRealVectorValue traction_new = traction_trial;
  const ADReal tau_norm = sqrt(traction_trial(1) * traction_trial(1) +
                               traction_trial(2) * traction_trial(2));

  _friction_coefficient_effective[_qp] = mu_old;
  _cohesion_effective[_qp] = cohesion_old;
  _dilation_angle_effective[_qp] = dilation_angle_old_deg;
  _dilation_state[_qp] = dilation_state_old;
  _dilation_support_factor[_qp] = 1.0;
  _cumulative_plastic_slip[_qp] = cumulative_slip_old;
  _roughness_state[_qp] = roughness_old;
  _roughness_damage[_qp] = 1.0 - roughness_old;
  _strength_normal_memory[_qp] = _strength_normal_memory_old[_qp];
  _retained_shear_support[_qp] = _retained_shear_support_old[_qp];
  _plastic_slip_increment[_qp] = 0.0;
  _dilation_jump_increment[_qp] = 0.0;
  _irreversible_dilation[_qp] = _irreversible_dilation_old[_qp];
  _reversible_closure[_qp] = _reversible_closure_old[_qp];
  _reversible_closure_min_compression[_qp] = _reversible_closure_min_compression_old[_qp];
  _plastic_tangential_jump[_qp] = plastic_tangential_jump_new;

  ADReal reversible_closure_new;
  ADReal reversible_closure_min_compression_new;
  // Driver is the PREVIOUS converged normal traction (traction_old(0)), not the live trial, to
  // avoid the penalty*compliance normal-stiffness feedback (see computeReversibleClosureState).
  // The closure is bounded by the accumulated dilation opening so it can only recover dilation,
  // never over-close past the undilated baseline.
  computeReversibleClosureState(traction_old(0),
                                cumulative_slip_old,
                                ADReal(_irreversible_dilation_old[_qp]),
                                reversible_closure_new,
                                reversible_closure_min_compression_new);
  const ADReal delta_reversible_closure =
      reversible_closure_new - ADReal(_reversible_closure_old[_qp]);
  traction_trial(0) -=
      ADReal(_dil_sign) * ADReal(_penalty_normal) * delta_reversible_closure;
  traction_new(0) = traction_trial(0);
  _reversible_closure[_qp] = reversible_closure_new;
  _reversible_closure_min_compression[_qp] = reversible_closure_min_compression_new;

  if (traction_trial(0) > _normal_traction_tolerance)
  {
    traction_new = ADRealVectorValue(0.0, 0.0, 0.0);
    _fracture_state[_qp] = static_cast<Real>(FractureState::Open);
    _limit_tau[_qp] = 0.0;
    _retained_shear_support[_qp] = _retained_shear_support_old[_qp];
    _reversible_closure[_qp] = _reversible_closure_old[_qp];
    _reversible_closure_min_compression[_qp] = _reversible_closure_min_compression_old[_qp];
    _interface_traction_inc[_qp] = traction_new - traction_old;
    return;
  }

  traction_new(0) = traction_trial(0);
  _strength_normal_memory[_qp] =
      updateStrengthNormalMemory(_strength_normal_memory_old[_qp], traction_new(0));

  // FIX (Warning): clamp limit_tau to >= 0 to prevent negative strength when cohesion is zero.
  const ADReal raw_limit_tau_stick = cohesion_old - mu_old * _strength_normal_memory[_qp];
  _limit_tau[_qp] = std::max(raw_limit_tau_stick, ADReal(0.0));

  if (tau_norm <= _tangential_traction_tolerance)
  {
    _fracture_state[_qp] = static_cast<Real>(FractureState::Stick);
    _interface_traction_inc[_qp] = traction_new - traction_old;
    return;
  }

  const bool slipping = (MetaPhysicL::raw_value(tau_norm) >
                         MetaPhysicL::raw_value(_limit_tau[_qp]));

  if (!slipping)
  {
    _fracture_state[_qp] = static_cast<Real>(FractureState::Stick);
    _interface_traction_inc[_qp] = traction_new - traction_old;
    return;
  }

  // --- First predictor pass ---
  ADReal denom = ADReal(_penalty_tangent);
  const ADReal dilation_support_old =
      computeDilationSupportFactor(_strength_normal_memory_old[_qp]);
  if (_use_dilatancy)
  {
    // Keep the return-mapping denominator consistent with the active dilation law. If the
    // dilation coupling would make the denominator non-positive, bound it from below to avoid
    // an unstable slip correction.
    const ADReal dilation_tangent_old =
        effectiveDilationTangent(cumulative_slip_old, tan_dilation_old, dilation_support_old);
    const ADReal denom_raw = ADReal(_penalty_tangent) -
                             ADReal(_dil_sign) * mu_old * ADReal(_penalty_normal) * dilation_tangent_old;
    if (MetaPhysicL::raw_value(denom_raw) < _tangential_traction_tolerance)
      denom = ADReal(_tangential_traction_tolerance);
    else
      denom = denom_raw;
  }

  // Duvaut-Lions/Perzyna viscous (rate) regularization: negligible under slow loading (the
  // quasi-static answer is unchanged), but bounds the slip RATE during a fast slip burst so the
  // Newton solve has a continuous path through what would otherwise be an instantaneous
  // stick->slip snap. See OrcaCZMMohrCoulombFriction and ADOrcaBartonBandisContactTractionFastAD
  // for the identical pattern already validated elsewhere in this codebase.
  if (_tangential_viscosity > 0.0 && _dt > 0.0)
    denom += ADReal(_tangential_viscosity) / ADReal(_dt);

  ADReal delta_gamma_p = (tau_norm - _limit_tau[_qp]) / denom;
  if (MetaPhysicL::raw_value(delta_gamma_p) < 0.0)
    delta_gamma_p = ADReal(0.0);
  if (_max_plastic_slip_increment > 0.0)
    delta_gamma_p = std::min(delta_gamma_p, ADReal(_max_plastic_slip_increment));

  ADReal roughness_new = updateRoughness(roughness_old, delta_gamma_p);

  ADReal mu_new;
  ADReal cohesion_new;
  computeStrengthDependentProperties(roughness_new, mu_new, cohesion_new);

  ADReal cumulative_slip_new = cumulative_slip_old + delta_gamma_p;
  ADReal dilation_state_new;
  ADReal dilation_angle_new_deg;
  ADReal tan_dilation_new;
  computeDilationDependentProperties(
      cumulative_slip_new, dilation_state_new, dilation_angle_new_deg, tan_dilation_new);

  ADReal delta_gn_p = dilationIncrementFromSlip(
      cumulative_slip_old, cumulative_slip_new, delta_gamma_p, tan_dilation_new, ADReal(1.0));
  if (_max_dilation_increment > 0.0 && MetaPhysicL::raw_value(delta_gn_p) > _max_dilation_increment)
    delta_gn_p = ADReal(_max_dilation_increment);

  ADReal traction_n_predictor = traction_trial(0) + ADReal(_dil_sign) * ADReal(_penalty_normal) * delta_gn_p;
  ADReal strength_normal_predictor =
      updateStrengthNormalMemory(_strength_normal_memory_old[_qp], traction_n_predictor);
  const ADReal dilation_support_predictor = computeDilationSupportFactor(strength_normal_predictor);
  delta_gn_p = dilationIncrementFromSlip(cumulative_slip_old,
                                         cumulative_slip_new,
                                         delta_gamma_p,
                                         tan_dilation_new,
                                         dilation_support_predictor);
  if (_max_dilation_increment > 0.0 && MetaPhysicL::raw_value(delta_gn_p) > _max_dilation_increment)
    delta_gn_p = ADReal(_max_dilation_increment);
  traction_n_predictor = traction_trial(0) + ADReal(_dil_sign) * ADReal(_penalty_normal) * delta_gn_p;
  strength_normal_predictor =
      updateStrengthNormalMemory(_strength_normal_memory_old[_qp], traction_n_predictor);
  // FIX (Warning): clamp predictor limit_tau to >= 0.
  const ADReal limit_tau_predictor =
      std::max(cohesion_new - mu_new * strength_normal_predictor, ADReal(0.0));

  // --- Corrected pass ---
  ADReal denom_corrected = ADReal(_penalty_tangent);
  if (_use_dilatancy)
  {
    // Same denominator treatment in the corrected pass for consistency.
    const ADReal dilation_tangent_new =
        effectiveDilationTangent(cumulative_slip_new, tan_dilation_new, dilation_support_predictor);
    const ADReal denom_corrected_raw =
        ADReal(_penalty_tangent) -
        ADReal(_dil_sign) * mu_new * ADReal(_penalty_normal) * dilation_tangent_new;
    if (MetaPhysicL::raw_value(denom_corrected_raw) < _tangential_traction_tolerance)
      denom_corrected = ADReal(_tangential_traction_tolerance);
    else
      denom_corrected = denom_corrected_raw;
  }

  // Same viscous regularization as the first predictor pass above, kept consistent here.
  if (_tangential_viscosity > 0.0 && _dt > 0.0)
    denom_corrected += ADReal(_tangential_viscosity) / ADReal(_dt);

  ADReal delta_gamma_p_corrected = (tau_norm - limit_tau_predictor) / denom_corrected;
  if (MetaPhysicL::raw_value(delta_gamma_p_corrected) < 0.0)
    delta_gamma_p_corrected = ADReal(0.0);
  if (_max_plastic_slip_increment > 0.0)
    delta_gamma_p_corrected =
        std::min(delta_gamma_p_corrected, ADReal(_max_plastic_slip_increment));
  delta_gamma_p = delta_gamma_p_corrected;

  // --- Final state update with accepted delta_gamma_p ---
  roughness_new = updateRoughness(roughness_old, delta_gamma_p);
  computeStrengthDependentProperties(roughness_new, mu_new, cohesion_new);
  cumulative_slip_new = cumulative_slip_old + delta_gamma_p;
  computeDilationDependentProperties(
      cumulative_slip_new, dilation_state_new, dilation_angle_new_deg, tan_dilation_new);

  // FIX (Bug 3): Recompute dilation_support_new consistently from the final accepted
  // delta_gamma_p, not from the stale first-predictor traction_n_predictor.
  // We re-evaluate the dilation opening with the corrected plastic slip and then derive the
  // support factor from the resulting normal traction.
  ADReal delta_gn_p_final = dilationIncrementFromSlip(
      cumulative_slip_old, cumulative_slip_new, delta_gamma_p, tan_dilation_new, ADReal(1.0));
  if (_max_dilation_increment > 0.0 &&
      MetaPhysicL::raw_value(delta_gn_p_final) > _max_dilation_increment)
    delta_gn_p_final = ADReal(_max_dilation_increment);
  const ADReal traction_n_final = traction_trial(0) + ADReal(_dil_sign) * ADReal(_penalty_normal) * delta_gn_p_final;
  const ADReal strength_normal_final =
      updateStrengthNormalMemory(_strength_normal_memory_old[_qp], traction_n_final);
  const ADReal dilation_support_new = computeDilationSupportFactor(strength_normal_final);

  // Now apply support modulation to get the definitive dilation opening, using the same
  // dilation law that was used in the return-mapping denominator.
  delta_gn_p = dilationIncrementFromSlip(cumulative_slip_old,
                                         cumulative_slip_new,
                                         delta_gamma_p,
                                         tan_dilation_new,
                                         dilation_support_new);
  if (_max_dilation_increment > 0.0 && MetaPhysicL::raw_value(delta_gn_p) > _max_dilation_increment)
    delta_gn_p = ADReal(_max_dilation_increment);

  _plastic_slip_increment[_qp] = delta_gamma_p;
  _dilation_jump_increment[_qp] = delta_gn_p;
  _cumulative_plastic_slip[_qp] = cumulative_slip_new;
  _roughness_state[_qp] = roughness_new;
  _roughness_damage[_qp] = 1.0 - roughness_new;
  _friction_coefficient_effective[_qp] = mu_new;
  _cohesion_effective[_qp] = cohesion_new;
  _dilation_angle_effective[_qp] = dilation_angle_new_deg;
  _dilation_state[_qp] = dilation_state_new;
  _dilation_support_factor[_qp] = dilation_support_new;
  _irreversible_dilation[_qp] = _irreversible_dilation_old[_qp] + delta_gn_p;

  traction_new(0) = traction_trial(0) + ADReal(_dil_sign) * ADReal(_penalty_normal) * delta_gn_p;
  _strength_normal_memory[_qp] =
      updateStrengthNormalMemory(_strength_normal_memory_old[_qp], traction_new(0));
  // FIX (Warning): clamp raw_limit_tau to >= 0 before storing and using as floor.
  const ADReal raw_limit_tau = std::max(cohesion_new - mu_new * _strength_normal_memory[_qp],
                                        ADReal(0.0));
  _retained_shear_support[_qp] = updateRetainedShearSupport(
      _retained_shear_support_old[_qp], raw_limit_tau, delta_gamma_p);

  // FIX (Bug 2): Check for post-dilation opening BEFORE committing irreversible state.
  // In the original code all state variables were already stored above when this branch fired,
  // leaving roughness, cumulative slip, and dilation permanently advanced for an open-interface
  // step. We now detect opening here and roll back the plastic state to the old values.
  if (traction_new(0) > _normal_traction_tolerance)
  {
    // Roll back all plastic state — this step should be treated as pure opening.
    _plastic_slip_increment[_qp] = 0.0;
    _dilation_jump_increment[_qp] = 0.0;
    _cumulative_plastic_slip[_qp] = cumulative_slip_old;
    _roughness_state[_qp] = roughness_old;
    _roughness_damage[_qp] = 1.0 - roughness_old;
    _friction_coefficient_effective[_qp] = mu_old;
    _cohesion_effective[_qp] = cohesion_old;
    _dilation_angle_effective[_qp] = dilation_angle_old_deg;
    _dilation_state[_qp] = dilation_state_old;
    _dilation_support_factor[_qp] = dilation_support_old;
    _irreversible_dilation[_qp] = _irreversible_dilation_old[_qp];
    _plastic_tangential_jump[_qp] = ADRealVectorValue(0.0,
                                                       plastic_tangential_jump_old(1),
                                                       plastic_tangential_jump_old(2));
    _retained_shear_support[_qp] = _retained_shear_support_old[_qp];
    _strength_normal_memory[_qp] =
        updateStrengthNormalMemory(_strength_normal_memory_old[_qp], ADReal(0.0));
    _reversible_closure[_qp] = _reversible_closure_old[_qp];
    _reversible_closure_min_compression[_qp] = _reversible_closure_min_compression_old[_qp];

    traction_new = ADRealVectorValue(0.0, 0.0, 0.0);
    _fracture_state[_qp] = static_cast<Real>(FractureState::Open);
    _limit_tau[_qp] = 0.0;
    _interface_traction_inc[_qp] = traction_new - traction_old;
    return;
  }

  const ADReal retained_floor =
      ADReal(_retained_shear_support_factor) * _retained_shear_support[_qp];
  _limit_tau[_qp] = std::max(raw_limit_tau, retained_floor);

  ADRealVectorValue slip_direction(0.0, 0.0, 0.0);
  // FIX (Minor): removed the dead 1e-30 softener; this branch is only reachable when
  // tau_norm > _tangential_traction_tolerance, so the softener was never active.
  slip_direction(1) = traction_trial(1) / tau_norm;
  slip_direction(2) = traction_trial(2) / tau_norm;

  plastic_tangential_jump_new(1) =
      ADReal(plastic_tangential_jump_old(1)) + delta_gamma_p * slip_direction(1);
  plastic_tangential_jump_new(2) =
      ADReal(plastic_tangential_jump_old(2)) + delta_gamma_p * slip_direction(2);
  _plastic_tangential_jump[_qp] = plastic_tangential_jump_new;

  // Use the actual capped plastic increment to compute shear traction. Projecting directly to
  // the Coulomb limit here would bypass max_plastic_slip_increment and over-unload the interface.
  traction_new(1) = ADReal(_penalty_tangent) * (jump(1) - plastic_tangential_jump_new(1));
  traction_new(2) = ADReal(_penalty_tangent) * (jump(2) - plastic_tangential_jump_new(2));

  _fracture_state[_qp] = static_cast<Real>(FractureState::Slip);
  _interface_traction_inc[_qp] = traction_new - traction_old;
}
