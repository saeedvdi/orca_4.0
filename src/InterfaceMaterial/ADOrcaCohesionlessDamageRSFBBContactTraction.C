#include "ADOrcaCohesionlessDamageRSFBBContactTraction.h"
#include "metaphysicl/raw_type.h"
#include <algorithm>
#include <cmath>

registerMooseObject("OrcaApp", ADOrcaCohesionlessDamageRSFBBContactTraction);
registerMooseObjectAliased("OrcaApp",
                           ADOrcaCohesionlessDamageRSFBBContactTraction,
                           "OrcaCohesionlessDamageRSFBBContactTraction");

InputParameters
ADOrcaCohesionlessDamageRSFBBContactTraction::validParams()
{
  InputParameters params = ADOrcaBartonBandisContactTractionFastAD::validParams();
  params.addClassDescription(
      "Cohesionless damage-RSF joint with Barton-Bandis mechanical normal closure. "
      "The inherited BB normal closure remains in the residual; shear strength is "
      "tau_y = sigma_n * [mu_r + (mu_p - mu_r) exp(-(s/D_w)^m)] + c_app, where c_app "
      "is an optional closed-contact apparent shear intercept. Dilation is bounded by a "
      "user-specified fraction of the damaged friction coefficient, and optional two-stage "
      "damage, rate-and-state friction, and roughness-scaled smooth/rough endpoint parameters "
      "add the combined SW3/SW4 perturbations.");

  params.addRangeCheckedParam<Real>("peak_friction_coefficient", 0.50,
      "peak_friction_coefficient >= 0.0",
      "Peak cohesionless friction coefficient mu_p at zero plastic slip.");
  params.addRangeCheckedParam<Real>("residual_friction_coefficient", 0.12,
      "residual_friction_coefficient >= 0.0",
      "Large-slip residual friction coefficient mu_r.");
  params.addRangeCheckedParam<Real>("damage_slip_distance", 1.0e-4,
      "damage_slip_distance > 0.0",
      "Characteristic plastic slip distance D_w for frictional damage/weakening [m].");
  params.addRangeCheckedParam<Real>("damage_exponent", 1.0,
      "damage_exponent >= 1.0",
      "Shape exponent m in A(s)=exp[-(s/D_w)^m].  Values below 1 are disallowed because "
      "they give a singular initial weakening slope.");
  params.addParam<bool>("use_two_stage_damage", false,
      "If true, replace the single exponential weakening law with "
      "mu = mu_r + (mu_i - mu_r) A_slow(s) + (mu_p - mu_i) A_fast(s).  "
      "The fast branch captures small-slip asperity polishing; the slow branch captures "
      "continued gouge/roughness evolution.  Defaults leave the one-stage law unchanged.");
  params.addRangeCheckedParam<Real>("intermediate_friction_coefficient", 0.30,
      "intermediate_friction_coefficient >= 0.0",
      "Intermediate friction coefficient mu_i used only when use_two_stage_damage=true.");
  params.addRangeCheckedParam<Real>("fast_damage_slip_distance", 1.0e-5,
      "fast_damage_slip_distance > 0.0",
      "Fast-branch slip distance D_fast [m] for the optional two-stage damage law.");
  params.addRangeCheckedParam<Real>("fast_damage_exponent", 1.0,
      "fast_damage_exponent >= 1.0",
      "Fast-branch exponent m_fast in exp[-(s/D_fast)^m_fast].");
  params.addRangeCheckedParam<Real>("fast_damage_onset_slip", 0.0,
      "fast_damage_onset_slip >= 0.0",
      "Plastic slip threshold s_fast0 [m] before the optional two-stage fast damage branch "
      "starts evolving.  The fast branch uses exp[-(<s-s_fast0>+/D_fast)^m_fast].  "
      "Default 0 preserves the original immediate fast weakening.");
  params.addRangeCheckedParam<Real>("slow_damage_slip_distance", 1.0e-4,
      "slow_damage_slip_distance > 0.0",
      "Slow-branch slip distance D_slow [m] for the optional two-stage damage law.");
  params.addRangeCheckedParam<Real>("slow_damage_exponent", 1.0,
      "slow_damage_exponent >= 1.0",
      "Slow-branch exponent m_slow in exp[-(s/D_slow)^m_slow].");
  params.addRangeCheckedParam<Real>("slow_damage_onset_slip", 0.0,
      "slow_damage_onset_slip >= 0.0",
      "Plastic slip threshold s_slow0 [m] before the optional two-stage slow damage branch "
      "starts evolving.  Default 0 preserves the original immediate slow weakening and roughness "
      "export.");

  params.addRangeCheckedParam<Real>("dilation_work_fraction", 0.85,
      "dilation_work_fraction >= 0.0 & dilation_work_fraction < 1.0",
      "Fraction of the instantaneous frictional work that may be converted to normal "
      "dilation work when dilation_friction_coefficient_floor=0.  More generally, "
      "the model enforces dg_n^p/ds <= dilation_work_fraction*max(mu(s), "
      "dilation_friction_coefficient_floor).");
  params.addRangeCheckedParam<Real>("dilation_friction_coefficient_floor", 0.0,
      "dilation_friction_coefficient_floor >= 0.0",
      "Optional lower bound on the friction coefficient used for dilation only.  "
      "Shear strength and friction weakening still use the actual damaged mu(s), but "
      "dg_n^p/ds is computed from max(mu(s), dilation_friction_coefficient_floor).  "
      "Default 0 preserves the original fully coupled dilation/friction behavior.  "
      "Positive values deliberately decouple late-time dilation from the weakened shear strength.");
  params.addRangeCheckedParam<Real>("maximum_dilation_coefficient", 0.0,
      "maximum_dilation_coefficient >= 0.0",
      "Optional cap on dg_n^p/ds.  Zero disables this extra geometric cap.");
  params.addRangeCheckedParam<Real>("apparent_cohesion", 0.0,
      "apparent_cohesion >= 0.0",
      "Optional apparent shear intercept c_app [Pa] added to the closed-contact shear limit: "
      "tau_y = sigma'_n*mu(s) + c_app.  This is not tensile cohesion and does not carry shear "
      "traction across an open interface.  Default 0 keeps the physical cohesionless law.");

  params.addRangeCheckedParam<Real>("roughness_state_initial", 0.45,
      "roughness_state_initial >= 0.0 & roughness_state_initial <= 1.0",
      "Initial exported roughness_state at zero slip for the downstream permeability law.");
  params.addRangeCheckedParam<Real>("roughness_state_residual", 0.10,
      "roughness_state_residual >= 0.0 & roughness_state_residual <= 1.0",
      "Residual exported roughness_state after large slip for the downstream permeability law.");
  params.addParam<bool>("use_roughness_scaled_parameters", false,
      "If true, interpolate the damage/friction/dilation parameters between smooth- and "
      "rough-joint endpoint values using roughness_state_initial.  This implements the "
      "combined SW3/SW4 paper-level idea that roughness changes the peak branch, weakening "
      "distances, and dilation capacity while preserving a single cohesionless law.  False "
      "uses the direct parameters above exactly.");
  params.addRangeCheckedParam<Real>("roughness_parameter_smooth_state", 0.45,
      "roughness_parameter_smooth_state >= 0.0 & roughness_parameter_smooth_state <= 1.0",
      "Roughness-state value mapped to the smooth endpoint when "
      "use_roughness_scaled_parameters=true.  Default matches the SW4 hybrid decks.");
  params.addRangeCheckedParam<Real>("roughness_parameter_rough_state", 0.64,
      "roughness_parameter_rough_state >= 0.0 & roughness_parameter_rough_state <= 1.0",
      "Roughness-state value mapped to the rough endpoint when "
      "use_roughness_scaled_parameters=true.  Default matches the SW3 hybrid decks.");
  params.addRangeCheckedParam<Real>("roughness_parameter_exponent", 1.0,
      "roughness_parameter_exponent >= 1.0",
      "Exponent applied to the smooth-to-rough interpolation coordinate.  Values >1 keep "
      "near-smooth joints closer to the smooth endpoint; values <1 would be nonphysical here "
      "and are disallowed.");
  params.addRangeCheckedParam<Real>("smooth_peak_friction_coefficient", 0.50,
      "smooth_peak_friction_coefficient >= 0.0",
      "Smooth-endpoint peak friction used only when use_roughness_scaled_parameters=true.");
  params.addRangeCheckedParam<Real>("rough_peak_friction_coefficient", 0.50,
      "rough_peak_friction_coefficient >= 0.0",
      "Rough-endpoint peak friction used only when use_roughness_scaled_parameters=true.");
  params.addRangeCheckedParam<Real>("smooth_residual_friction_coefficient", 0.12,
      "smooth_residual_friction_coefficient >= 0.0",
      "Smooth-endpoint residual friction used only when use_roughness_scaled_parameters=true.");
  params.addRangeCheckedParam<Real>("rough_residual_friction_coefficient", 0.12,
      "rough_residual_friction_coefficient >= 0.0",
      "Rough-endpoint residual friction used only when use_roughness_scaled_parameters=true.");
  params.addRangeCheckedParam<Real>("smooth_intermediate_friction_coefficient", 0.30,
      "smooth_intermediate_friction_coefficient >= 0.0",
      "Smooth-endpoint intermediate friction used only when two-stage damage and "
      "use_roughness_scaled_parameters are both true.");
  params.addRangeCheckedParam<Real>("rough_intermediate_friction_coefficient", 0.30,
      "rough_intermediate_friction_coefficient >= 0.0",
      "Rough-endpoint intermediate friction used only when two-stage damage and "
      "use_roughness_scaled_parameters are both true.");
  params.addRangeCheckedParam<Real>("smooth_damage_slip_distance", 1.0e-4,
      "smooth_damage_slip_distance > 0.0",
      "Smooth-endpoint one-stage damage distance used only when "
      "use_roughness_scaled_parameters=true.");
  params.addRangeCheckedParam<Real>("rough_damage_slip_distance", 1.0e-4,
      "rough_damage_slip_distance > 0.0",
      "Rough-endpoint one-stage damage distance used only when "
      "use_roughness_scaled_parameters=true.");
  params.addRangeCheckedParam<Real>("smooth_fast_damage_slip_distance", 1.0e-5,
      "smooth_fast_damage_slip_distance > 0.0",
      "Smooth-endpoint fast damage distance used only when two-stage damage and "
      "use_roughness_scaled_parameters are both true.");
  params.addRangeCheckedParam<Real>("rough_fast_damage_slip_distance", 1.0e-5,
      "rough_fast_damage_slip_distance > 0.0",
      "Rough-endpoint fast damage distance used only when two-stage damage and "
      "use_roughness_scaled_parameters are both true.");
  params.addRangeCheckedParam<Real>("smooth_slow_damage_slip_distance", 1.0e-4,
      "smooth_slow_damage_slip_distance > 0.0",
      "Smooth-endpoint slow damage distance used only when two-stage damage and "
      "use_roughness_scaled_parameters are both true.");
  params.addRangeCheckedParam<Real>("rough_slow_damage_slip_distance", 1.0e-4,
      "rough_slow_damage_slip_distance > 0.0",
      "Rough-endpoint slow damage distance used only when two-stage damage and "
      "use_roughness_scaled_parameters are both true.");
  params.addRangeCheckedParam<Real>("smooth_dilation_work_fraction", 0.85,
      "smooth_dilation_work_fraction >= 0.0 & smooth_dilation_work_fraction < 1.0",
      "Smooth-endpoint dilation work fraction used only when "
      "use_roughness_scaled_parameters=true.");
  params.addRangeCheckedParam<Real>("rough_dilation_work_fraction", 0.85,
      "rough_dilation_work_fraction >= 0.0 & rough_dilation_work_fraction < 1.0",
      "Rough-endpoint dilation work fraction used only when "
      "use_roughness_scaled_parameters=true.");
  params.addRangeCheckedParam<Real>("smooth_dilation_friction_coefficient_floor", 0.0,
      "smooth_dilation_friction_coefficient_floor >= 0.0",
      "Smooth-endpoint dilation friction floor used only when "
      "use_roughness_scaled_parameters=true.");
  params.addRangeCheckedParam<Real>("rough_dilation_friction_coefficient_floor", 0.0,
      "rough_dilation_friction_coefficient_floor >= 0.0",
      "Rough-endpoint dilation friction floor used only when "
      "use_roughness_scaled_parameters=true.");
  params.addRangeCheckedParam<Real>("smooth_maximum_dilation_coefficient", 0.0,
      "smooth_maximum_dilation_coefficient >= 0.0",
      "Smooth-endpoint geometric cap on dg_n^p/ds.  Zero disables the cap at the endpoint.");
  params.addRangeCheckedParam<Real>("rough_maximum_dilation_coefficient", 0.0,
      "rough_maximum_dilation_coefficient >= 0.0",
      "Rough-endpoint geometric cap on dg_n^p/ds.  Zero disables the cap at the endpoint.");

  params.addParam<bool>("use_rate_and_state", false,
      "If true, add a regularized Dieterich-Ruina rate-and-state perturbation to the "
      "cohesionless damage strength.");
  params.addRangeCheckedParam<Real>("rate_and_state_a", 0.0,
      "rate_and_state_a >= 0.0",
      "Direct-effect coefficient a.  Set to zero to disable the RSF perturbation.");
  params.addRangeCheckedParam<Real>("rate_and_state_b", 0.0,
      "rate_and_state_b >= 0.0",
      "State-effect coefficient b.");
  params.addRangeCheckedParam<Real>("rate_and_state_Dc", 1.0e-5,
      "rate_and_state_Dc > 0.0",
      "RSF state evolution distance Dc [m].");
  params.addRangeCheckedParam<Real>("rate_and_state_V0", 1.0e-8,
      "rate_and_state_V0 > 0.0",
      "Reference slip rate V0 [m/s].");
  params.addRangeCheckedParam<Real>("rate_and_state_theta0", 0.0,
      "rate_and_state_theta0 >= 0.0",
      "Initial RSF state theta [s].  Zero uses Dc/V0.");
  params.addParam<bool>("rate_and_state_nonnegative", false,
      "Clamp the referenced RSF term at zero (strengthening only). The raw referenced form "
      "a*(asinh(z)-asinh(1/2)) is NEGATIVE as V->0 (-0.481*a*sigma_n), so the slip-branch strength "
      "at vanishing slip rate sits 0.481*a*sigma_n BELOW the stick limit tl used by the stick check: "
      "an infinitesimal criterion exceedance produces a finite slip/traction jump and the global "
      "Newton limit-cycles across the branch flip (observed: 54_18 died at t=809 s / slip 3.3 um and "
      "54_19 at t=952 s / slip 1.3 um -- both exactly at first yield, residuals rising from ~1e-5). "
      "With the clamp the slip strength at V->0+ equals tl (continuous, monotone transition); only "
      "the mild V<V0 weakening is given up. Default false = legacy (fatal at onset with RSF on).");

  return params;
}

ADOrcaCohesionlessDamageRSFBBContactTraction::
    ADOrcaCohesionlessDamageRSFBBContactTraction(const InputParameters & parameters)
  : ADOrcaBartonBandisContactTractionFastAD(parameters),
    _peak_friction_coefficient(getParam<Real>("peak_friction_coefficient")),
    _residual_friction_coefficient(getParam<Real>("residual_friction_coefficient")),
    _damage_slip_distance(getParam<Real>("damage_slip_distance")),
    _damage_exponent(getParam<Real>("damage_exponent")),
    _use_two_stage_damage(getParam<bool>("use_two_stage_damage")),
    _intermediate_friction_coefficient(getParam<Real>("intermediate_friction_coefficient")),
    _fast_damage_slip_distance(getParam<Real>("fast_damage_slip_distance")),
    _fast_damage_exponent(getParam<Real>("fast_damage_exponent")),
    _fast_damage_onset_slip(getParam<Real>("fast_damage_onset_slip")),
    _slow_damage_slip_distance(getParam<Real>("slow_damage_slip_distance")),
    _slow_damage_exponent(getParam<Real>("slow_damage_exponent")),
    _slow_damage_onset_slip(getParam<Real>("slow_damage_onset_slip")),
    _dilation_work_fraction(getParam<Real>("dilation_work_fraction")),
    _dilation_friction_coefficient_floor(getParam<Real>("dilation_friction_coefficient_floor")),
    _maximum_dilation_coefficient(getParam<Real>("maximum_dilation_coefficient")),
    _apparent_cohesion(getParam<Real>("apparent_cohesion")),
    _roughness_state_initial(getParam<Real>("roughness_state_initial")),
    _roughness_state_residual(getParam<Real>("roughness_state_residual")),
    _use_roughness_scaled_parameters(getParam<bool>("use_roughness_scaled_parameters")),
    _roughness_parameter_smooth_state(getParam<Real>("roughness_parameter_smooth_state")),
    _roughness_parameter_rough_state(getParam<Real>("roughness_parameter_rough_state")),
    _roughness_parameter_exponent(getParam<Real>("roughness_parameter_exponent")),
    _smooth_peak_friction_coefficient(getParam<Real>("smooth_peak_friction_coefficient")),
    _rough_peak_friction_coefficient(getParam<Real>("rough_peak_friction_coefficient")),
    _smooth_residual_friction_coefficient(getParam<Real>("smooth_residual_friction_coefficient")),
    _rough_residual_friction_coefficient(getParam<Real>("rough_residual_friction_coefficient")),
    _smooth_intermediate_friction_coefficient(
        getParam<Real>("smooth_intermediate_friction_coefficient")),
    _rough_intermediate_friction_coefficient(
        getParam<Real>("rough_intermediate_friction_coefficient")),
    _smooth_damage_slip_distance(getParam<Real>("smooth_damage_slip_distance")),
    _rough_damage_slip_distance(getParam<Real>("rough_damage_slip_distance")),
    _smooth_fast_damage_slip_distance(getParam<Real>("smooth_fast_damage_slip_distance")),
    _rough_fast_damage_slip_distance(getParam<Real>("rough_fast_damage_slip_distance")),
    _smooth_slow_damage_slip_distance(getParam<Real>("smooth_slow_damage_slip_distance")),
    _rough_slow_damage_slip_distance(getParam<Real>("rough_slow_damage_slip_distance")),
    _smooth_dilation_work_fraction(getParam<Real>("smooth_dilation_work_fraction")),
    _rough_dilation_work_fraction(getParam<Real>("rough_dilation_work_fraction")),
    _smooth_dilation_friction_coefficient_floor(
        getParam<Real>("smooth_dilation_friction_coefficient_floor")),
    _rough_dilation_friction_coefficient_floor(
        getParam<Real>("rough_dilation_friction_coefficient_floor")),
    _smooth_maximum_dilation_coefficient(getParam<Real>("smooth_maximum_dilation_coefficient")),
    _rough_maximum_dilation_coefficient(getParam<Real>("rough_maximum_dilation_coefficient")),
    _use_rate_and_state(getParam<bool>("use_rate_and_state")),
    _rate_and_state_a(getParam<Real>("rate_and_state_a")),
    _rate_and_state_b(getParam<Real>("rate_and_state_b")),
    _rate_and_state_Dc(getParam<Real>("rate_and_state_Dc")),
    _rate_and_state_V0(getParam<Real>("rate_and_state_V0")),
    _rate_and_state_theta0(getParam<Real>("rate_and_state_theta0")),
    _rate_and_state_nonnegative(getParam<bool>("rate_and_state_nonnegative")),
    _rate_state_theta(declareProperty<Real>(_base_name + "rate_state_theta")),
    _rate_state_theta_old(getMaterialPropertyOld<Real>(_base_name + "rate_state_theta"))
{
  if (!_use_roughness_scaled_parameters &&
      _residual_friction_coefficient > _peak_friction_coefficient)
    paramError("residual_friction_coefficient",
               "Must be <= peak_friction_coefficient for monotone damage weakening.");
  if (_use_roughness_scaled_parameters)
  {
    if (_roughness_parameter_rough_state <= _roughness_parameter_smooth_state)
      paramError("roughness_parameter_rough_state",
                 "Must be > roughness_parameter_smooth_state.");
    if (_smooth_residual_friction_coefficient > _smooth_peak_friction_coefficient)
      paramError("smooth_residual_friction_coefficient",
                 "Must be <= smooth_peak_friction_coefficient.");
    if (_rough_residual_friction_coefficient > _rough_peak_friction_coefficient)
      paramError("rough_residual_friction_coefficient",
                 "Must be <= rough_peak_friction_coefficient.");
    if (_use_two_stage_damage &&
        (_smooth_intermediate_friction_coefficient < _smooth_residual_friction_coefficient ||
         _smooth_intermediate_friction_coefficient > _smooth_peak_friction_coefficient))
      paramError("smooth_intermediate_friction_coefficient",
                 "For use_two_stage_damage=true, smooth mu_i must satisfy mu_r <= mu_i <= mu_p.");
    if (_use_two_stage_damage &&
        (_rough_intermediate_friction_coefficient < _rough_residual_friction_coefficient ||
         _rough_intermediate_friction_coefficient > _rough_peak_friction_coefficient))
      paramError("rough_intermediate_friction_coefficient",
                 "For use_two_stage_damage=true, rough mu_i must satisfy mu_r <= mu_i <= mu_p.");
    if (_smooth_dilation_friction_coefficient_floor > _smooth_peak_friction_coefficient)
      paramError("smooth_dilation_friction_coefficient_floor",
                 "Must be <= smooth_peak_friction_coefficient.");
    if (_rough_dilation_friction_coefficient_floor > _rough_peak_friction_coefficient)
      paramError("rough_dilation_friction_coefficient_floor",
                 "Must be <= rough_peak_friction_coefficient.");
  }
  if (!_use_roughness_scaled_parameters && _use_two_stage_damage &&
      (_intermediate_friction_coefficient < _residual_friction_coefficient ||
       _intermediate_friction_coefficient > _peak_friction_coefficient))
    paramError("intermediate_friction_coefficient",
               "For use_two_stage_damage=true, mu_i must satisfy mu_r <= mu_i <= mu_p.");
  if (_roughness_state_residual > _roughness_state_initial)
    paramError("roughness_state_residual", "Must be <= roughness_state_initial.");
  if (!_use_roughness_scaled_parameters &&
      _dilation_friction_coefficient_floor > _peak_friction_coefficient)
    paramError("dilation_friction_coefficient_floor",
               "Must be <= peak_friction_coefficient for this cohesionless damage law.");
  if (dilationFrictionCoefficientFloor() > peakFrictionCoefficient())
    paramError(_use_roughness_scaled_parameters ? "roughness_state_initial"
                                                : "dilation_friction_coefficient_floor",
               "The effective dilation friction floor must be <= the effective peak friction.");
  if (_use_rate_and_state && _rate_and_state_a <= 0.0)
    paramError("rate_and_state_a", "use_rate_and_state=true requires rate_and_state_a > 0.");
}

void
ADOrcaCohesionlessDamageRSFBBContactTraction::initQpStatefulProperties()
{
  ADOrcaBartonBandisContactTractionFastAD::initQpStatefulProperties();
  _rate_state_theta[_qp] =
      _rate_and_state_theta0 > 0.0 ? _rate_and_state_theta0 : _rate_and_state_Dc / _rate_and_state_V0;
  const Real mu_p = peakFrictionCoefficient();
  _friction_coefficient_effective[_qp] = mu_p;
  _cohesion_effective[_qp] = _apparent_cohesion;
  _bb_peak_friction_coefficient[_qp] = mu_p;
  _bb_peak_friction_angle_degrees[_qp] =
      std::atan(mu_p) * 180.0 / M_PI;
  _roughness_state[_qp] = ADReal(_roughness_state_initial);
  _roughness_damage[_qp] = 1.0 - _roughness_state_initial;
}

ADReal
ADOrcaCohesionlessDamageRSFBBContactTraction::damageWeight(
    const ADReal & cumulative_slip) const
{
  return weakeningWeight(cumulative_slip, damageSlipDistance(), _damage_exponent);
}

Real
ADOrcaCohesionlessDamageRSFBBContactTraction::damageWeightReal(Real cumulative_slip) const
{
  return weakeningWeightReal(cumulative_slip, damageSlipDistance(), _damage_exponent);
}

Real
ADOrcaCohesionlessDamageRSFBBContactTraction::damageWeightDerivativeReal(
    Real cumulative_slip) const
{
  return weakeningWeightDerivativeReal(cumulative_slip, damageSlipDistance(), _damage_exponent);
}

ADReal
ADOrcaCohesionlessDamageRSFBBContactTraction::weakeningWeight(
    const ADReal & cumulative_slip, Real slip_distance, Real exponent, Real onset_slip) const
{
  using std::exp;
  using std::pow;
  const ADReal active_slip =
      std::max(ADReal(0.0), cumulative_slip - ADReal(onset_slip));
  const ADReal x = active_slip / ADReal(slip_distance);
  return exp(-pow(x, ADReal(exponent)));
}

Real
ADOrcaCohesionlessDamageRSFBBContactTraction::weakeningWeightReal(
    Real cumulative_slip, Real slip_distance, Real exponent, Real onset_slip) const
{
  const Real active_slip = std::max(Real(0.0), cumulative_slip - onset_slip);
  const Real x = active_slip / slip_distance;
  return std::exp(-std::pow(x, exponent));
}

Real
ADOrcaCohesionlessDamageRSFBBContactTraction::weakeningWeightDerivativeReal(
    Real cumulative_slip, Real slip_distance, Real exponent, Real onset_slip) const
{
  if (cumulative_slip <= onset_slip)
    return 0.0;

  const Real x = (cumulative_slip - onset_slip) / slip_distance;
  const Real A = std::exp(-std::pow(x, exponent));
  return -A * exponent * std::pow(x, exponent - 1.0) / slip_distance;
}

Real
ADOrcaCohesionlessDamageRSFBBContactTraction::roughnessParameterWeight() const
{
  if (!_use_roughness_scaled_parameters)
    return 0.0;

  const Real denom = _roughness_parameter_rough_state - _roughness_parameter_smooth_state;
  const Real eta =
      denom > 0.0 ? (_roughness_state_initial - _roughness_parameter_smooth_state) / denom : 0.0;
  return std::pow(std::max(Real(0.0), std::min(Real(1.0), eta)),
                  _roughness_parameter_exponent);
}

Real
ADOrcaCohesionlessDamageRSFBBContactTraction::roughnessScaledParameter(
    Real direct_value, Real smooth_value, Real rough_value) const
{
  if (!_use_roughness_scaled_parameters)
    return direct_value;

  const Real w = roughnessParameterWeight();
  return smooth_value + (rough_value - smooth_value) * w;
}

Real
ADOrcaCohesionlessDamageRSFBBContactTraction::peakFrictionCoefficient() const
{
  return roughnessScaledParameter(_peak_friction_coefficient,
                                  _smooth_peak_friction_coefficient,
                                  _rough_peak_friction_coefficient);
}

Real
ADOrcaCohesionlessDamageRSFBBContactTraction::residualFrictionCoefficient() const
{
  return roughnessScaledParameter(_residual_friction_coefficient,
                                  _smooth_residual_friction_coefficient,
                                  _rough_residual_friction_coefficient);
}

Real
ADOrcaCohesionlessDamageRSFBBContactTraction::intermediateFrictionCoefficient() const
{
  return roughnessScaledParameter(_intermediate_friction_coefficient,
                                  _smooth_intermediate_friction_coefficient,
                                  _rough_intermediate_friction_coefficient);
}

Real
ADOrcaCohesionlessDamageRSFBBContactTraction::damageSlipDistance() const
{
  return roughnessScaledParameter(
      _damage_slip_distance, _smooth_damage_slip_distance, _rough_damage_slip_distance);
}

Real
ADOrcaCohesionlessDamageRSFBBContactTraction::fastDamageSlipDistance() const
{
  return roughnessScaledParameter(_fast_damage_slip_distance,
                                  _smooth_fast_damage_slip_distance,
                                  _rough_fast_damage_slip_distance);
}

Real
ADOrcaCohesionlessDamageRSFBBContactTraction::slowDamageSlipDistance() const
{
  return roughnessScaledParameter(_slow_damage_slip_distance,
                                  _smooth_slow_damage_slip_distance,
                                  _rough_slow_damage_slip_distance);
}

Real
ADOrcaCohesionlessDamageRSFBBContactTraction::dilationWorkFraction() const
{
  return roughnessScaledParameter(_dilation_work_fraction,
                                  _smooth_dilation_work_fraction,
                                  _rough_dilation_work_fraction);
}

Real
ADOrcaCohesionlessDamageRSFBBContactTraction::dilationFrictionCoefficientFloor() const
{
  return roughnessScaledParameter(_dilation_friction_coefficient_floor,
                                  _smooth_dilation_friction_coefficient_floor,
                                  _rough_dilation_friction_coefficient_floor);
}

Real
ADOrcaCohesionlessDamageRSFBBContactTraction::maximumDilationCoefficient() const
{
  return roughnessScaledParameter(_maximum_dilation_coefficient,
                                  _smooth_maximum_dilation_coefficient,
                                  _rough_maximum_dilation_coefficient);
}

ADReal
ADOrcaCohesionlessDamageRSFBBContactTraction::frictionCoefficient(
    const ADReal & cumulative_slip) const
{
  const Real mu_p = peakFrictionCoefficient();
  const Real mu_r = residualFrictionCoefficient();
  if (_use_two_stage_damage)
  {
    const Real mu_i = intermediateFrictionCoefficient();
    const ADReal A_fast =
        weakeningWeight(cumulative_slip,
                        fastDamageSlipDistance(),
                        _fast_damage_exponent,
                        _fast_damage_onset_slip);
    const ADReal A_slow =
        weakeningWeight(cumulative_slip,
                        slowDamageSlipDistance(),
                        _slow_damage_exponent,
                        _slow_damage_onset_slip);
    return ADReal(mu_r) + ADReal(mu_i - mu_r) * A_slow +
           ADReal(mu_p - mu_i) * A_fast;
  }

  const ADReal A = damageWeight(cumulative_slip);
  return ADReal(mu_r) + ADReal(mu_p - mu_r) * A;
}

Real
ADOrcaCohesionlessDamageRSFBBContactTraction::frictionCoefficientReal(
    Real cumulative_slip) const
{
  const Real mu_p = peakFrictionCoefficient();
  const Real mu_r = residualFrictionCoefficient();
  if (_use_two_stage_damage)
  {
    const Real mu_i = intermediateFrictionCoefficient();
    const Real A_fast = weakeningWeightReal(
        cumulative_slip,
        fastDamageSlipDistance(),
        _fast_damage_exponent,
        _fast_damage_onset_slip);
    const Real A_slow = weakeningWeightReal(
        cumulative_slip,
        slowDamageSlipDistance(),
        _slow_damage_exponent,
        _slow_damage_onset_slip);
    return mu_r + (mu_i - mu_r) * A_slow + (mu_p - mu_i) * A_fast;
  }

  return mu_r + (mu_p - mu_r) * damageWeightReal(cumulative_slip);
}

Real
ADOrcaCohesionlessDamageRSFBBContactTraction::frictionCoefficientDerivativeReal(
    Real cumulative_slip) const
{
  const Real mu_p = peakFrictionCoefficient();
  const Real mu_r = residualFrictionCoefficient();
  if (_use_two_stage_damage)
  {
    const Real mu_i = intermediateFrictionCoefficient();
    return (mu_i - mu_r) *
               weakeningWeightDerivativeReal(
                   cumulative_slip,
                   slowDamageSlipDistance(),
                   _slow_damage_exponent,
                   _slow_damage_onset_slip) +
           (mu_p - mu_i) *
               weakeningWeightDerivativeReal(
                   cumulative_slip,
                   fastDamageSlipDistance(),
                   _fast_damage_exponent,
                   _fast_damage_onset_slip);
  }

  return (mu_p - mu_r) * damageWeightDerivativeReal(cumulative_slip);
}

Real
ADOrcaCohesionlessDamageRSFBBContactTraction::roughnessWeightReal(Real cumulative_slip) const
{
  if (_use_two_stage_damage)
    return weakeningWeightReal(cumulative_slip,
                               slowDamageSlipDistance(),
                               _slow_damage_exponent,
                               _slow_damage_onset_slip);

  return damageWeightReal(cumulative_slip);
}

ADReal
ADOrcaCohesionlessDamageRSFBBContactTraction::dilationCoefficient(
    const ADReal & friction_coefficient) const
{
  const ADReal dilation_friction =
      std::max(std::max(ADReal(0.0), friction_coefficient),
               ADReal(dilationFrictionCoefficientFloor()));
  ADReal coeff = ADReal(dilationWorkFraction()) * dilation_friction;
  const Real max_coeff = maximumDilationCoefficient();
  if (max_coeff > 0.0)
    coeff = std::min(coeff, ADReal(max_coeff));
  return coeff;
}

Real
ADOrcaCohesionlessDamageRSFBBContactTraction::dilationCoefficientReal(
    Real friction_coefficient) const
{
  const Real dilation_friction =
      std::max(std::max(Real(0.0), friction_coefficient),
               dilationFrictionCoefficientFloor());
  Real coeff = dilationWorkFraction() * dilation_friction;
  const Real max_coeff = maximumDilationCoefficient();
  if (max_coeff > 0.0)
    coeff = std::min(coeff, max_coeff);
  return coeff;
}

void
ADOrcaCohesionlessDamageRSFBBContactTraction::computeBartonBandisProperties(
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
  using std::atan;

  friction_coefficient = this->frictionCoefficient(cumulative_slip);
  dilation_coefficient = _use_dilatancy ? this->dilationCoefficient(friction_coefficient)
                                        : ADReal(0.0);

  jrc_mobilized = ADReal(0.0);
  const ADReal phi_r = atan(ADReal(residualFrictionCoefficient())) * ADReal(180.0 / M_PI);
  peak_friction_angle_deg = atan(friction_coefficient) * ADReal(180.0 / M_PI);
  roughness_angle_deg = std::max(ADReal(0.0), peak_friction_angle_deg - phi_r);
  dilation_angle_deg = atan(dilation_coefficient) * ADReal(180.0 / M_PI);
  shear_strength = sigma_n * friction_coefficient + ADReal(_apparent_cohesion);
  if (_min_tau_limit > 0.0)
    shear_strength = std::max(ADReal(_min_tau_limit), shear_strength);
}

void
ADOrcaCohesionlessDamageRSFBBContactTraction::computeBartonBandisPropertiesReal(
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
  friction_coefficient = frictionCoefficientReal(cumulative_slip);
  dilation_coefficient =
      _use_dilatancy ? dilationCoefficientReal(friction_coefficient) : 0.0;

  jrc_mobilized = 0.0;
  const Real phi_r = std::atan(residualFrictionCoefficient()) * 180.0 / M_PI;
  peak_friction_angle_deg = std::atan(friction_coefficient) * 180.0 / M_PI;
  roughness_angle_deg = std::max(Real(0.0), peak_friction_angle_deg - phi_r);
  dilation_angle_deg = std::atan(dilation_coefficient) * 180.0 / M_PI;
  shear_strength = sigma_n * friction_coefficient + _apparent_cohesion;
  if (_min_tau_limit > 0.0)
    shear_strength = std::max(_min_tau_limit, shear_strength);
}

Real
ADOrcaCohesionlessDamageRSFBBContactTraction::computeReturnMappingDerivative(
    Real sigma_n,
    Real kn_tangent,
    Real,
    Real,
    Real,
    Real mu,
    Real dilation_coefficient,
    Real dilation_increment,
    Real closure_new,
    Real cumulative_slip_new) const
{
  const Real d_sn_d_g = computeDNormalStressDPlasticSlipReal(
      kn_tangent, dilation_coefficient, dilation_increment, closure_new);
  const Real d_mu_d_s = frictionCoefficientDerivativeReal(cumulative_slip_new);

  Real d_taulim_d_g = mu * d_sn_d_g + sigma_n * d_mu_d_s;
  if (_min_tau_limit > 0.0 && sigma_n * mu + _apparent_cohesion <= _min_tau_limit)
    d_taulim_d_g = 0.0;
  return -Real(_penalty_tangent) - d_taulim_d_g;
}

ADReal
ADOrcaCohesionlessDamageRSFBBContactTraction::computeAdditionalShearStrength(
    const ADReal & sigma_n, Real plastic_slip_increment) const
{
  if (!_use_rate_and_state || _rate_and_state_a <= 0.0 || _dt <= 0.0)
    return ADReal(0.0);

  using std::pow;
  const Real theta_old =
      std::max(Real(1.0e-30), _rate_state_theta_old[_qp]);
  const Real state_factor =
      std::pow(_rate_and_state_V0 * theta_old / _rate_and_state_Dc,
               _rate_and_state_b / _rate_and_state_a);
  const Real V = std::max(Real(0.0), plastic_slip_increment / _dt);
  const Real z = V / (2.0 * _rate_and_state_V0) * state_factor;
  const Real root = std::sqrt(z * z + 1.0);
  const Real rsf_ref = 0.4812118250596035; // asinh(1/2)
  Real mu_rs = _rate_and_state_a * (std::log(z + root) - rsf_ref);
  // Non-negative clamp (see param doc): keeps the slip-branch strength at V->0+ equal to the
  // stick limit so the branch transition is continuous. Must stay value-consistent with the
  // Real variant below (the IFT residual is evaluated with this function at the converged dgp).
  if (_rate_and_state_nonnegative && mu_rs < 0.0)
    mu_rs = 0.0;
  return sigma_n * ADReal(mu_rs);
}

Real
ADOrcaCohesionlessDamageRSFBBContactTraction::computeAdditionalShearStrengthReal(
    Real sigma_n,
    Real plastic_slip_increment,
    Real d_sigma_n_d_plastic_slip,
    Real & dstrength_dslip) const
{
  dstrength_dslip = 0.0;
  if (!_use_rate_and_state || _rate_and_state_a <= 0.0 || _dt <= 0.0)
    return 0.0;

  const Real theta_old =
      std::max(Real(1.0e-30), _rate_state_theta_old[_qp]);
  const Real state_factor =
      std::pow(_rate_and_state_V0 * theta_old / _rate_and_state_Dc,
               _rate_and_state_b / _rate_and_state_a);
  const Real V = std::max(Real(0.0), plastic_slip_increment / _dt);
  const Real z = V / (2.0 * _rate_and_state_V0) * state_factor;
  const Real root = std::sqrt(z * z + 1.0);
  const Real rsf_ref = 0.4812118250596035; // asinh(1/2)
  const Real mu_rs = _rate_and_state_a * (std::log(z + root) - rsf_ref);
  // Non-negative clamp (see param doc): zero strength AND zero tangents in the clamped region so
  // the local NR and the IFT tangent stay consistent with the clamped value above.
  if (_rate_and_state_nonnegative && mu_rs < 0.0)
    return 0.0;
  const Real dz_dg = state_factor / (2.0 * _rate_and_state_V0 * _dt);
  const Real dmu_dg = _rate_and_state_a / root * dz_dg;

  dstrength_dslip = mu_rs * d_sigma_n_d_plastic_slip + sigma_n * dmu_dg;
  return sigma_n * mu_rs;
}

void
ADOrcaCohesionlessDamageRSFBBContactTraction::carryAdditionalState()
{
  _rate_state_theta[_qp] = _rate_state_theta_old[_qp];
}

Real
ADOrcaCohesionlessDamageRSFBBContactTraction::evolveRateStateTheta(
    Real plastic_slip_increment) const
{
  const Real theta_old = _rate_state_theta_old[_qp];
  if (!_use_rate_and_state || _rate_and_state_a <= 0.0 || _dt <= 0.0)
    return theta_old;

  const Real x = std::max(Real(0.0), plastic_slip_increment / _rate_and_state_Dc);
  const Real ex = std::exp(-x);
  const Real one_minus_ex_over_x =
      (x > 1.0e-8) ? (1.0 - ex) / x : (1.0 - 0.5 * x);
  return theta_old * ex + _dt * one_minus_ex_over_x;
}

void
ADOrcaCohesionlessDamageRSFBBContactTraction::commitAdditionalState(
    Real plastic_slip_increment)
{
  _rate_state_theta[_qp] = evolveRateStateTheta(plastic_slip_increment);
}

Real
ADOrcaCohesionlessDamageRSFBBContactTraction::computeRoughnessState() const
{
  const Real A = roughnessWeightReal(_cumulative_plastic_slip[_qp]);
  return _roughness_state_residual + (_roughness_state_initial - _roughness_state_residual) * A;
}

Real
ADOrcaCohesionlessDamageRSFBBContactTraction::computeCohesionEffective() const
{
  return _apparent_cohesion;
}
