#include "ADOrcaCohesionlessDamageMohrCoulombContactTraction.h"

#include "metaphysicl/raw_type.h"

#include <algorithm>
#include <cmath>

using std::atan;
using std::exp;
using std::log;
using std::pow;
using std::sqrt;

registerMooseObject("OrcaApp", ADOrcaCohesionlessDamageMohrCoulombContactTraction);
registerMooseObjectAliased("OrcaApp",
                           ADOrcaCohesionlessDamageMohrCoulombContactTraction,
                           "OrcaCohesionlessDamageMohrCoulombContactTraction");

namespace
{
constexpr Real damage_mc_pi = 3.141592653589793238462643383279502884;
constexpr Real damage_mc_asinh_one_half = 0.4812118250596034475;
}

InputParameters
ADOrcaCohesionlessDamageMohrCoulombContactTraction::validParams()
{
  InputParameters params = OrcaCZMComputeLocalTractionIncrementalBase::validParams();
  params.addClassDescription(
      "Simplified cohesionless Mohr-Coulomb contact law with one direct frictional damage "
      "state, energy-bounded dilation, optional referenced rate-and-state friction, and "
      "the same downstream CZM property names as the full decoupled MC law.");

  params.addParam<std::string>("base_name", "Material property base name");

  params.addRangeCheckedParam<Real>(
      "penalty_normal", "penalty_normal > 0.0", "Contact normal stiffness K_n [Pa/m].");
  params.addRangeCheckedParam<Real>(
      "penalty_tangent",
      0.0,
      "penalty_tangent >= 0.0",
      "Tangential stiffness K_t [Pa/m]. A value of zero uses penalty_normal.");
  params.addRangeCheckedParam<Real>(
      "opening_gap_tolerance",
      0.0,
      "opening_gap_tolerance >= 0.0",
      "Gap tolerance [m] for the contact/open active-set decision.");
  params.addRangeCheckedParam<Real>("tangential_traction_tolerance",
                                    1e-12,
                                    "tangential_traction_tolerance >= 0.0",
                                    "Tolerance [Pa] for defining a slip direction.");
  params.addRangeCheckedParam<Real>("contact_gap_regularization",
                                    1e-14,
                                    "contact_gap_regularization > 0.0",
                                    "Smooth-positive contact-gap regularization [m].");
  params.addRangeCheckedParam<Real>("stress_regularization",
                                    1e-8,
                                    "stress_regularization > 0.0",
                                    "Small stress floor used in diagnostic denominators [Pa].");
  params.addRangeCheckedParam<Real>(
      "local_newton_tolerance",
      1e-8,
      "local_newton_tolerance > 0.0",
      "Absolute residual tolerance [Pa] for the scalar slip return map.");
  params.addRangeCheckedParam<unsigned int>("max_local_newton_iterations",
                                            30,
                                            "max_local_newton_iterations > 0",
                                            "Maximum local scalar Newton iterations.");
  params.addRangeCheckedParam<Real>(
      "tangential_viscosity",
      0.0,
      "tangential_viscosity >= 0.0",
      "Perzyna tangential viscosity eta_t [Pa.s/m]. Zero gives rate-independent slip.");

  params.addRangeCheckedParam<Real>("peak_friction_coefficient",
                                    0.50,
                                    "peak_friction_coefficient >= 0.0",
                                    "Realized peak friction coefficient mu_p at first slip.");
  params.addRangeCheckedParam<Real>("residual_friction_coefficient",
                                    0.10,
                                    "residual_friction_coefficient >= 0.0",
                                    "Large-slip residual friction coefficient mu_r.");
  params.addRangeCheckedParam<Real>(
      "apparent_cohesion",
      0.0,
      "apparent_cohesion >= 0.0",
      "Optional constant apparent shear cohesion c [Pa] in tau_y = c + p*mu. "
      "Default zero preserves the cohesionless saw-cut law; this does not create "
      "tensile normal cohesion.");
  params.addRangeCheckedParam<Real>("damage_slip_distance",
                                    1.0e-4,
                                    "damage_slip_distance > 0.0",
                                    "Characteristic frictional damage slip distance D_w [m].");
  params.addRangeCheckedParam<Real>(
      "damage_exponent",
      1.0,
      "damage_exponent >= 1.0",
      "Shape exponent m in A(s)=exp[-(s/D_w)^m].");
  params.addParam<bool>(
      "use_two_stage_damage",
      false,
      "Use a compact two-stage friction damage law instead of the one-stage law.");
  params.addRangeCheckedParam<Real>("intermediate_friction_coefficient",
                                    0.30,
                                    "intermediate_friction_coefficient >= 0.0",
                                    "Intermediate friction coefficient mu_i for two-stage damage.");
  params.addRangeCheckedParam<Real>("fast_damage_slip_distance",
                                    2.0e-5,
                                    "fast_damage_slip_distance > 0.0",
                                    "Fast-branch slip distance D_fast [m].");
  params.addRangeCheckedParam<Real>("fast_damage_exponent",
                                    1.0,
                                    "fast_damage_exponent >= 1.0",
                                    "Fast-branch damage exponent.");
  params.addRangeCheckedParam<Real>("fast_damage_onset_slip",
                                    0.0,
                                    "fast_damage_onset_slip >= 0.0",
                                    "Fast-branch onset slip [m].");
  params.addRangeCheckedParam<Real>("slow_damage_slip_distance",
                                    1.0e-4,
                                    "slow_damage_slip_distance > 0.0",
                                    "Slow-branch slip distance D_slow [m].");
  params.addRangeCheckedParam<Real>("slow_damage_exponent",
                                    1.0,
                                    "slow_damage_exponent >= 1.0",
                                    "Slow-branch damage exponent.");
  params.addRangeCheckedParam<Real>("slow_damage_onset_slip",
                                    0.0,
                                    "slow_damage_onset_slip >= 0.0",
                                    "Slow-branch onset slip [m].");

  params.addParam<bool>("use_dilatancy", true, "Enable shear-induced irreversible dilation.");
  params.addRangeCheckedParam<Real>(
      "dilation_work_fraction",
      0.85,
      "dilation_work_fraction >= 0.0 & dilation_work_fraction < 1.0",
      "Fraction beta_d of Mohr-Coulomb frictional work allowed to become dilation work.");
  params.addRangeCheckedParam<Real>(
      "dilation_friction_coefficient_floor",
      0.0,
      "dilation_friction_coefficient_floor >= 0.0",
      "Optional lower bound on the friction coefficient used only for dilation. For this "
      "conservative Mohr-Coulomb law it must not exceed residual_friction_coefficient.");
  params.addRangeCheckedParam<Real>(
      "maximum_dilation_coefficient",
      0.0,
      "maximum_dilation_coefficient >= 0.0",
      "Optional geometric cap on dg_np/ds. Zero disables the cap.");

  params.addRangeCheckedParam<Real>(
      "roughness_state_initial",
      0.45,
      "roughness_state_initial >= 0.0 & roughness_state_initial <= 1.0",
      "Initial exported roughness_state for the permeability material.");
  params.addRangeCheckedParam<Real>(
      "roughness_state_residual",
      0.10,
      "roughness_state_residual >= 0.0 & roughness_state_residual <= 1.0",
      "Residual exported roughness_state for the permeability material.");

  params.addRangeCheckedParam<Real>(
      "reversible_normal_compliance",
      0.0,
      "reversible_normal_compliance >= 0.0",
      "Optional output-only elastic normal opening compliance C_n [m/Pa]. Zero disables.");
  params.addRangeCheckedParam<Real>(
      "reversible_normal_reference_stress",
      0.0,
      "reversible_normal_reference_stress >= 0.0",
      "Reference effective normal stress [Pa] for the optional output-only elastic opening.");

  params.addParam<bool>(
      "use_rate_and_state",
      false,
      "Enable a referenced Dieterich-Ruina rate-and-state perturbation about the damage-MC strength.");
  params.addRangeCheckedParam<Real>(
      "rate_and_state_a", 0.0, "rate_and_state_a >= 0.0", "RSF direct-effect coefficient a.");
  params.addRangeCheckedParam<Real>(
      "rate_and_state_b", 0.0, "rate_and_state_b >= 0.0", "RSF state coefficient b.");
  params.addRangeCheckedParam<Real>(
      "rate_and_state_Dc", 1.0e-5, "rate_and_state_Dc > 0.0", "RSF state distance Dc [m].");
  params.addRangeCheckedParam<Real>(
      "rate_and_state_V0", 1.0e-8, "rate_and_state_V0 > 0.0", "Reference velocity V0 [m/s].");
  params.addRangeCheckedParam<Real>(
      "rate_and_state_theta0",
      0.0,
      "rate_and_state_theta0 >= 0.0",
      "Initial RSF state theta [s]. Zero initializes to Dc/V0.");
  params.addParam<bool>(
      "rate_and_state_nonnegative",
      true,
      "Clamp the referenced RSF perturbation at zero so stick/slip transition is monotone.");

  return params;
}

ADOrcaCohesionlessDamageMohrCoulombContactTraction::
    ADOrcaCohesionlessDamageMohrCoulombContactTraction(const InputParameters & parameters)
  : OrcaCZMComputeLocalTractionIncrementalBase(parameters),
    _penalty_normal(getParam<Real>("penalty_normal")),
    _penalty_tangent(getParam<Real>("penalty_tangent") > 0.0 ? getParam<Real>("penalty_tangent")
                                                             : getParam<Real>("penalty_normal")),
    _opening_gap_tolerance(getParam<Real>("opening_gap_tolerance")),
    _tangential_traction_tolerance(getParam<Real>("tangential_traction_tolerance")),
    _contact_gap_regularization(getParam<Real>("contact_gap_regularization")),
    _stress_regularization(getParam<Real>("stress_regularization")),
    _local_newton_tolerance(getParam<Real>("local_newton_tolerance")),
    _max_local_newton_iterations(getParam<unsigned int>("max_local_newton_iterations")),
    _tangential_viscosity(getParam<Real>("tangential_viscosity")),
    _peak_friction_coefficient(getParam<Real>("peak_friction_coefficient")),
    _residual_friction_coefficient(getParam<Real>("residual_friction_coefficient")),
    _apparent_cohesion(getParam<Real>("apparent_cohesion")),
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
    _use_dilatancy(getParam<bool>("use_dilatancy")),
    _dilation_work_fraction(getParam<Real>("dilation_work_fraction")),
    _dilation_friction_coefficient_floor(getParam<Real>("dilation_friction_coefficient_floor")),
    _maximum_dilation_coefficient(getParam<Real>("maximum_dilation_coefficient")),
    _roughness_state_initial(getParam<Real>("roughness_state_initial")),
    _roughness_state_residual(getParam<Real>("roughness_state_residual")),
    _reversible_normal_compliance(getParam<Real>("reversible_normal_compliance")),
    _reversible_normal_reference_stress(getParam<Real>("reversible_normal_reference_stress")),
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
    _roughness_damage(declareADProperty<Real>(_base_name + "roughness_damage")),
    _friction_coefficient_effective(
        declareADProperty<Real>(_base_name + "friction_coefficient_effective")),
    _cohesion_effective(declareADProperty<Real>(_base_name + "cohesion_effective")),
    _dilation_angle_effective(declareADProperty<Real>(_base_name + "dilation_angle_effective")),
    _dilation_state(declareADProperty<Real>(_base_name + "dilation_state")),
    _dilation_support_factor(declareADProperty<Real>(_base_name + "dilation_support_factor")),
    _strength_normal_memory_magnitude(
        declareADProperty<Real>(_base_name + "strength_normal_memory_magnitude")),
    _strength_normal_memory(declareADProperty<Real>(_base_name + "strength_normal_memory")),
    _retained_shear_support(declareADProperty<Real>(_base_name + "retained_shear_support")),
    _normal_plastic_jump(declareADProperty<Real>(_base_name + "normal_plastic_jump")),
    _normal_plastic_jump_old(getMaterialPropertyOld<Real>(_base_name + "normal_plastic_jump")),
    _irreversible_dilation(declareADProperty<Real>(_base_name + "irreversible_dilation")),
    _normal_contact_pressure(declareADProperty<Real>(_base_name + "normal_contact_pressure")),
    _reversible_normal_opening(declareADProperty<Real>(_base_name + "reversible_normal_opening")),
    _normal_opening_total(declareADProperty<Real>(_base_name + "normal_opening_total")),
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
        getMaterialPropertyOld<RealVectorValue>(_base_name + "plastic_tangential_jump"))
{
  if (_residual_friction_coefficient > _peak_friction_coefficient)
    paramError("residual_friction_coefficient",
               "Must be <= peak_friction_coefficient for monotone damage weakening.");
  if (_use_two_stage_damage &&
      (_intermediate_friction_coefficient < _residual_friction_coefficient ||
       _intermediate_friction_coefficient > _peak_friction_coefficient))
    paramError("intermediate_friction_coefficient",
               "For two-stage damage, mu_r <= mu_i <= mu_p is required.");
  if (_roughness_state_residual > _roughness_state_initial)
    paramError("roughness_state_residual", "Must be <= roughness_state_initial.");
  if (_dilation_friction_coefficient_floor > _residual_friction_coefficient)
    paramError("dilation_friction_coefficient_floor",
               "Must be <= residual_friction_coefficient so dilation work remains bounded by "
               "the Mohr-Coulomb sliding work at large slip.");
  if (_use_rate_and_state && _rate_and_state_a <= 0.0)
    paramError("rate_and_state_a", "use_rate_and_state=true requires rate_and_state_a > 0.");
}

void
ADOrcaCohesionlessDamageMohrCoulombContactTraction::initQpStatefulProperties()
{
  OrcaCZMComputeLocalTractionIncrementalBase::initQpStatefulProperties();

  _fracture_state[_qp] = static_cast<Real>(FractureState::Stick);
  _limit_tau[_qp] = 0.0;
  _plastic_slip_increment[_qp] = 0.0;
  _dilation_jump_increment[_qp] = 0.0;
  _cumulative_plastic_slip[_qp] = 0.0;
  _roughness_state[_qp] = _roughness_state_initial;
  _roughness_damage[_qp] = 1.0 - _roughness_state_initial;
  _friction_coefficient_effective[_qp] = _peak_friction_coefficient;
  _cohesion_effective[_qp] = _apparent_cohesion;
  _dilation_angle_effective[_qp] =
      atan(_dilation_work_fraction * _peak_friction_coefficient) * 180.0 / damage_mc_pi;
  _dilation_state[_qp] = _dilation_work_fraction * _peak_friction_coefficient;
  _dilation_support_factor[_qp] = 1.0;
  _strength_normal_memory_magnitude[_qp] = 0.0;
  _strength_normal_memory[_qp] = 0.0;
  _retained_shear_support[_qp] = 0.0;
  _normal_plastic_jump[_qp] = 0.0;
  _irreversible_dilation[_qp] = 0.0;
  _normal_contact_pressure[_qp] = 0.0;
  _reversible_normal_opening[_qp] = 0.0;
  _normal_opening_total[_qp] = 0.0;
  _rate_state_theta[_qp] =
      _rate_and_state_theta0 > 0.0 ? _rate_and_state_theta0 : _rate_and_state_Dc / _rate_and_state_V0;
  _frictional_sliding_work_increment[_qp] = 0.0;
  _dilation_work_increment[_qp] = 0.0;
  _frictional_dilatant_dissipation_increment[_qp] = 0.0;
  _cohesive_dissipation_increment[_qp] = 0.0;
  _plastic_tangential_jump[_qp] = RealVectorValue(0.0, 0.0, 0.0);
}

ADReal
ADOrcaCohesionlessDamageMohrCoulombContactTraction::smoothPositive(const ADReal & x,
                                                                   const Real eps) const
{
  return ADReal(0.5) * (x + sqrt(x * x + ADReal(eps * eps)));
}

ADReal
ADOrcaCohesionlessDamageMohrCoulombContactTraction::smoothPositiveDerivative(
    const ADReal & x, const Real eps) const
{
  return ADReal(0.5) * (ADReal(1.0) + x / sqrt(x * x + ADReal(eps * eps)));
}

ADReal
ADOrcaCohesionlessDamageMohrCoulombContactTraction::weakeningWeight(
    const ADReal & cumulative_slip,
    const Real slip_distance,
    const Real exponent,
    const Real onset_slip) const
{
  const ADReal active_slip =
      std::max(ADReal(0.0), cumulative_slip - ADReal(onset_slip));
  const ADReal x = active_slip / ADReal(slip_distance);
  return exp(-pow(x, ADReal(exponent)));
}

ADReal
ADOrcaCohesionlessDamageMohrCoulombContactTraction::weakeningWeightDerivative(
    const ADReal & cumulative_slip,
    const Real slip_distance,
    const Real exponent,
    const Real onset_slip) const
{
  if (MetaPhysicL::raw_value(cumulative_slip) <= onset_slip)
    return ADReal(0.0);

  const ADReal x = (cumulative_slip - ADReal(onset_slip)) / ADReal(slip_distance);
  const ADReal A = exp(-pow(x, ADReal(exponent)));
  return -A * ADReal(exponent) * pow(x, ADReal(exponent - 1.0)) /
         ADReal(slip_distance);
}

void
ADOrcaCohesionlessDamageMohrCoulombContactTraction::frictionCoefficient(
    const ADReal & cumulative_slip, ADReal & friction, ADReal & dfriction_dgamma) const
{
  if (_use_two_stage_damage)
  {
    const ADReal A_fast =
        weakeningWeight(cumulative_slip,
                        _fast_damage_slip_distance,
                        _fast_damage_exponent,
                        _fast_damage_onset_slip);
    const ADReal A_slow =
        weakeningWeight(cumulative_slip,
                        _slow_damage_slip_distance,
                        _slow_damage_exponent,
                        _slow_damage_onset_slip);
    const ADReal dA_fast =
        weakeningWeightDerivative(cumulative_slip,
                                  _fast_damage_slip_distance,
                                  _fast_damage_exponent,
                                  _fast_damage_onset_slip);
    const ADReal dA_slow =
        weakeningWeightDerivative(cumulative_slip,
                                  _slow_damage_slip_distance,
                                  _slow_damage_exponent,
                                  _slow_damage_onset_slip);
    friction = ADReal(_residual_friction_coefficient) +
               ADReal(_intermediate_friction_coefficient - _residual_friction_coefficient) *
                   A_slow +
               ADReal(_peak_friction_coefficient - _intermediate_friction_coefficient) * A_fast;
    dfriction_dgamma =
        ADReal(_intermediate_friction_coefficient - _residual_friction_coefficient) * dA_slow +
        ADReal(_peak_friction_coefficient - _intermediate_friction_coefficient) * dA_fast;
    return;
  }

  const ADReal A = weakeningWeight(cumulative_slip, _damage_slip_distance, _damage_exponent);
  const ADReal dA = weakeningWeightDerivative(cumulative_slip, _damage_slip_distance, _damage_exponent);
  friction = ADReal(_residual_friction_coefficient) +
             ADReal(_peak_friction_coefficient - _residual_friction_coefficient) * A;
  dfriction_dgamma =
      ADReal(_peak_friction_coefficient - _residual_friction_coefficient) * dA;
}

void
ADOrcaCohesionlessDamageMohrCoulombContactTraction::dilationCoefficient(
    const ADReal & friction,
    const ADReal & dfriction_dgamma,
    ADReal & coefficient,
    ADReal & dcoefficient_dgamma) const
{
  if (!_use_dilatancy)
  {
    coefficient = 0.0;
    dcoefficient_dgamma = 0.0;
    return;
  }

  const bool floor_active =
      MetaPhysicL::raw_value(friction) < _dilation_friction_coefficient_floor;
  coefficient =
      ADReal(_dilation_work_fraction) *
      (floor_active ? ADReal(_dilation_friction_coefficient_floor) : friction);
  dcoefficient_dgamma = floor_active ? ADReal(0.0) : ADReal(_dilation_work_fraction) * dfriction_dgamma;

  if (_maximum_dilation_coefficient > 0.0 &&
      MetaPhysicL::raw_value(coefficient) > _maximum_dilation_coefficient)
  {
    coefficient = ADReal(_maximum_dilation_coefficient);
    dcoefficient_dgamma = ADReal(0.0);
  }
}

ADReal
ADOrcaCohesionlessDamageMohrCoulombContactTraction::roughnessState(
    const ADReal & cumulative_slip) const
{
  const ADReal A = _use_two_stage_damage
                       ? weakeningWeight(cumulative_slip,
                                         _slow_damage_slip_distance,
                                         _slow_damage_exponent,
                                         _slow_damage_onset_slip)
                       : weakeningWeight(cumulative_slip, _damage_slip_distance, _damage_exponent);
  return ADReal(_roughness_state_residual) +
         ADReal(_roughness_state_initial - _roughness_state_residual) * A;
}

ADReal
ADOrcaCohesionlessDamageMohrCoulombContactTraction::evolveRateStateTheta(
    const ADReal & gamma) const
{
  const ADReal theta_old = ADReal(_rate_state_theta_old[_qp]);
  if (!_use_rate_and_state || _rate_and_state_a <= 0.0 || _dt <= 0.0)
    return theta_old;

  const ADReal x = gamma / ADReal(_rate_and_state_Dc);
  const ADReal ex = exp(-x);
  const ADReal one_minus_ex_over_x =
      (MetaPhysicL::raw_value(x) > 1.0e-8) ? (ADReal(1.0) - ex) / x
                                           : (ADReal(1.0) - ADReal(0.5) * x);
  return theta_old * ex + ADReal(_dt) * one_minus_ex_over_x;
}

ADOrcaCohesionlessDamageMohrCoulombContactTraction::FrictionState
ADOrcaCohesionlessDamageMohrCoulombContactTraction::evaluateFriction(
    const ADReal & gamma,
    const ADReal & tau_trial,
    const ADReal & current_normal_jump,
    const ADReal & old_normal_plastic_jump,
    const ADReal & old_cumulative_slip,
    const ADReal & old_theta) const
{
  FrictionState s;
  s.gamma = gamma;
  s.cumulative_slip = old_cumulative_slip + gamma;
  frictionCoefficient(s.cumulative_slip, s.friction, s.dfriction_dgamma);
  dilationCoefficient(
      s.friction, s.dfriction_dgamma, s.dilation_coefficient, s.ddilation_dgamma);

  s.dilation_increment = s.dilation_coefficient * gamma;
  const ADReal ddilation_increment_dgamma =
      s.dilation_coefficient + gamma * s.ddilation_dgamma;
  s.normal_plastic_jump = old_normal_plastic_jump + s.dilation_increment;

  const ADReal overlap = s.normal_plastic_jump - current_normal_jump;
  s.normal_pressure = ADReal(_penalty_normal) * smoothPositive(overlap, _contact_gap_regularization);
  s.normal_pressure_tangent_gamma =
      ADReal(_penalty_normal) * smoothPositiveDerivative(overlap, _contact_gap_regularization) *
      ddilation_increment_dgamma;

  s.cohesion = ADReal(_apparent_cohesion);
  s.strength = s.cohesion + s.normal_pressure * s.friction;
  const ADReal dstrength_dgamma =
      s.normal_pressure_tangent_gamma * s.friction +
      s.normal_pressure * s.dfriction_dgamma;

  s.rsf_strength = 0.0;
  s.drsf_dgamma = 0.0;
  s.rate_state_theta = old_theta;
  if (_use_rate_and_state && _rate_and_state_a > 0.0 && _dt > 0.0)
  {
    const ADReal V = gamma / ADReal(_dt);
    const ADReal theta_safe = std::max(ADReal(1.0e-30), old_theta);
    const ADReal state_factor =
        pow(ADReal(_rate_and_state_V0) * theta_safe / ADReal(_rate_and_state_Dc),
            ADReal(_rate_and_state_b / _rate_and_state_a));
    const ADReal z = V / (ADReal(2.0) * ADReal(_rate_and_state_V0)) * state_factor;
    const ADReal root = sqrt(z * z + ADReal(1.0));
    ADReal mu_rs =
        ADReal(_rate_and_state_a) * (log(z + root) - ADReal(damage_mc_asinh_one_half));
    if (_rate_and_state_nonnegative && MetaPhysicL::raw_value(mu_rs) <= 0.0)
    {
      mu_rs = 0.0;
    }
    else
    {
      const ADReal dz_dgamma =
          state_factor / (ADReal(2.0) * ADReal(_rate_and_state_V0) * ADReal(_dt));
      s.drsf_dgamma =
          s.normal_pressure_tangent_gamma * mu_rs +
          s.normal_pressure * ADReal(_rate_and_state_a) / root * dz_dgamma;
    }
    s.rsf_strength = s.normal_pressure * mu_rs;
    s.rate_state_theta = evolveRateStateTheta(gamma);
  }

  const ADReal viscous_strength =
      (_tangential_viscosity > 0.0 && _dt > 0.0)
          ? ADReal(_tangential_viscosity / _dt) * gamma
          : ADReal(0.0);
  const ADReal dviscous_dgamma =
      (_tangential_viscosity > 0.0 && _dt > 0.0)
          ? ADReal(_tangential_viscosity / _dt)
          : ADReal(0.0);

  s.residual = tau_trial - ADReal(_penalty_tangent) * gamma - s.strength -
               s.rsf_strength - viscous_strength;
  s.dres_dgamma = -(ADReal(_penalty_tangent) + dstrength_dgamma + s.drsf_dgamma +
                    dviscous_dgamma);
  return s;
}

void
ADOrcaCohesionlessDamageMohrCoulombContactTraction::computeInterfaceTractionIncrement()
{
  const ADRealVectorValue & jump = _interface_displacement_jump[_qp];
  const RealVectorValue jump_old(_interface_displacement_jump_old[_qp]);
  const RealVectorValue traction_old(_interface_traction_old[_qp]);
  const ADReal old_cumulative_slip = ADReal(_cumulative_plastic_slip_old[_qp]);
  const ADReal old_normal_plastic_jump = ADReal(_normal_plastic_jump_old[_qp]);

  ADReal old_mu;
  ADReal old_dmu;
  frictionCoefficient(old_cumulative_slip, old_mu, old_dmu);

  const ADReal contact_overlap_trial = old_normal_plastic_jump - jump(0);
  const bool contact_active =
      MetaPhysicL::raw_value(contact_overlap_trial) > _opening_gap_tolerance;
  const ADReal pressure_trial =
      contact_active
          ? ADReal(_penalty_normal) * smoothPositive(contact_overlap_trial, _contact_gap_regularization)
          : ADReal(0.0);

  ADRealVectorValue traction_new(0.0, 0.0, 0.0);

  _plastic_slip_increment[_qp] = 0.0;
  _dilation_jump_increment[_qp] = 0.0;
  _cumulative_plastic_slip[_qp] = old_cumulative_slip;
  _normal_plastic_jump[_qp] = old_normal_plastic_jump;
  _irreversible_dilation[_qp] = old_normal_plastic_jump;
  _normal_contact_pressure[_qp] = pressure_trial;
  _strength_normal_memory_magnitude[_qp] = pressure_trial;
  _strength_normal_memory[_qp] = -pressure_trial;
  _retained_shear_support[_qp] = 0.0;
  _friction_coefficient_effective[_qp] = old_mu;
  _cohesion_effective[_qp] = _apparent_cohesion;
  _dilation_support_factor[_qp] = 1.0;
  _rate_state_theta[_qp] = ADReal(_rate_state_theta_old[_qp]);
  _frictional_sliding_work_increment[_qp] = 0.0;
  _dilation_work_increment[_qp] = 0.0;
  _frictional_dilatant_dissipation_increment[_qp] = 0.0;
  _cohesive_dissipation_increment[_qp] = 0.0;
  _plastic_tangential_jump[_qp] = ADRealVectorValue(ADReal(0.0),
                                                   ADReal(_plastic_tangential_jump_old[_qp](1)),
                                                   ADReal(_plastic_tangential_jump_old[_qp](2)));

  const ADReal R_old = roughnessState(old_cumulative_slip);
  _roughness_state[_qp] = R_old;
  _roughness_damage[_qp] = ADReal(1.0) - R_old;
  ADReal old_dil_coeff;
  ADReal old_ddil_coeff;
  dilationCoefficient(old_mu, old_dmu, old_dil_coeff, old_ddil_coeff);
  _dilation_state[_qp] = old_dil_coeff;
  _dilation_angle_effective[_qp] = atan(old_dil_coeff) * ADReal(180.0 / damage_mc_pi);

  if (!contact_active)
  {
    _fracture_state[_qp] = static_cast<Real>(FractureState::Open);
    _limit_tau[_qp] = 0.0;
    _reversible_normal_opening[_qp] = 0.0;
    _normal_opening_total[_qp] = old_normal_plastic_jump;
    _interface_traction_inc[_qp] = traction_new - ADRealVectorValue(ADReal(traction_old(0)),
                                                                    ADReal(traction_old(1)),
                                                                    ADReal(traction_old(2)));
    return;
  }

  traction_new(0) = -pressure_trial;

  const ADReal tangential_trial_1 =
      ADReal(_penalty_tangent) *
      (jump(1) - ADReal(_plastic_tangential_jump_old[_qp](1)));
  const ADReal tangential_trial_2 =
      ADReal(_penalty_tangent) *
      (jump(2) - ADReal(_plastic_tangential_jump_old[_qp](2)));
  const ADReal tau_trial =
      sqrt(tangential_trial_1 * tangential_trial_1 + tangential_trial_2 * tangential_trial_2);

  const ADReal stick_strength = ADReal(_apparent_cohesion) + pressure_trial * old_mu;
  _limit_tau[_qp] = stick_strength;

  if (MetaPhysicL::raw_value(tau_trial) <= _tangential_traction_tolerance ||
      MetaPhysicL::raw_value(tau_trial - stick_strength) <= _local_newton_tolerance)
  {
    traction_new(1) = tangential_trial_1;
    traction_new(2) = tangential_trial_2;
    _fracture_state[_qp] = static_cast<Real>(FractureState::Stick);
    const ADReal reversible_opening =
        ADReal(_reversible_normal_compliance) *
        smoothPositive(ADReal(_reversible_normal_reference_stress) - pressure_trial,
                       _stress_regularization);
    _reversible_normal_opening[_qp] = reversible_opening;
    _normal_opening_total[_qp] = old_normal_plastic_jump + reversible_opening;
    _interface_traction_inc[_qp] = traction_new - ADRealVectorValue(ADReal(traction_old(0)),
                                                                    ADReal(traction_old(1)),
                                                                    ADReal(traction_old(2)));
    return;
  }

  ADReal gamma = std::max(ADReal(0.0), (tau_trial - stick_strength) / ADReal(_penalty_tangent));
  const ADReal gamma_upper = tau_trial / ADReal(_penalty_tangent);
  if (MetaPhysicL::raw_value(gamma) > MetaPhysicL::raw_value(gamma_upper))
    gamma = gamma_upper;

  for (unsigned int i = 0; i < _max_local_newton_iterations; ++i)
  {
    const FrictionState s = evaluateFriction(gamma,
                                             tau_trial,
                                             jump(0),
                                             old_normal_plastic_jump,
                                             old_cumulative_slip,
                                             ADReal(_rate_state_theta_old[_qp]));
    if (std::abs(MetaPhysicL::raw_value(s.residual)) <= _local_newton_tolerance)
      break;

    ADReal step = -s.residual / s.dres_dgamma;
    Real alpha = 1.0;
    const Real current_norm = std::abs(MetaPhysicL::raw_value(s.residual));
    bool accepted = false;
    for (unsigned int ls = 0; ls < 12; ++ls)
    {
      ADReal trial_gamma = gamma + ADReal(alpha) * step;
      if (MetaPhysicL::raw_value(trial_gamma) < 0.0)
        trial_gamma = 0.0;
      if (MetaPhysicL::raw_value(trial_gamma) > MetaPhysicL::raw_value(gamma_upper))
        trial_gamma = gamma_upper;

      const FrictionState trial = evaluateFriction(trial_gamma,
                                                   tau_trial,
                                                   jump(0),
                                                   old_normal_plastic_jump,
                                                   old_cumulative_slip,
                                                   ADReal(_rate_state_theta_old[_qp]));
      const Real trial_norm = std::abs(MetaPhysicL::raw_value(trial.residual));
      if (trial_norm < current_norm)
      {
        gamma = trial_gamma;
        accepted = true;
        break;
      }
      alpha *= 0.5;
    }
    if (!accepted)
      break;
  }

  // One AD implicit-function corrector at the converged scalar return point.
  {
    const FrictionState s = evaluateFriction(gamma,
                                             tau_trial,
                                             jump(0),
                                             old_normal_plastic_jump,
                                             old_cumulative_slip,
                                             ADReal(_rate_state_theta_old[_qp]));
    const ADReal corr = -s.residual / s.dres_dgamma;
    const Real corr_limit = 1.0e3 * _local_newton_tolerance / _penalty_tangent;
    if (std::abs(MetaPhysicL::raw_value(corr)) <= corr_limit)
    {
      gamma += corr;
      if (MetaPhysicL::raw_value(gamma) < 0.0)
        gamma = 0.0;
      if (MetaPhysicL::raw_value(gamma) > MetaPhysicL::raw_value(gamma_upper))
        gamma = gamma_upper;
    }
  }

  const FrictionState final_state = evaluateFriction(gamma,
                                                     tau_trial,
                                                     jump(0),
                                                     old_normal_plastic_jump,
                                                     old_cumulative_slip,
                                                     ADReal(_rate_state_theta_old[_qp]));

  ADRealVectorValue slip_direction(0.0, 0.0, 0.0);
  slip_direction(1) = tangential_trial_1 / tau_trial;
  slip_direction(2) = tangential_trial_2 / tau_trial;

  const ADRealVectorValue plastic_tangential_jump_new(
      ADReal(0.0),
      ADReal(_plastic_tangential_jump_old[_qp](1)) + gamma * slip_direction(1),
      ADReal(_plastic_tangential_jump_old[_qp](2)) + gamma * slip_direction(2));

  const ADReal branch_traction_1 =
      ADReal(_penalty_tangent) * (jump(1) - plastic_tangential_jump_new(1));
  const ADReal branch_traction_2 =
      ADReal(_penalty_tangent) * (jump(2) - plastic_tangential_jump_new(2));

  traction_new(0) = -final_state.normal_pressure;
  traction_new(1) = branch_traction_1;
  traction_new(2) = branch_traction_2;

  _fracture_state[_qp] = static_cast<Real>(FractureState::Slip);
  _plastic_slip_increment[_qp] = gamma;
  _dilation_jump_increment[_qp] = final_state.dilation_increment;
  _cumulative_plastic_slip[_qp] = final_state.cumulative_slip;
  _normal_plastic_jump[_qp] = final_state.normal_plastic_jump;
  _irreversible_dilation[_qp] = final_state.normal_plastic_jump;
  _normal_contact_pressure[_qp] = final_state.normal_pressure;
  _strength_normal_memory_magnitude[_qp] = final_state.normal_pressure;
  _strength_normal_memory[_qp] = -final_state.normal_pressure;
  _limit_tau[_qp] = final_state.strength + final_state.rsf_strength;
  _friction_coefficient_effective[_qp] = final_state.friction;
  _cohesion_effective[_qp] = final_state.cohesion;
  _dilation_state[_qp] = final_state.dilation_coefficient;
  _dilation_angle_effective[_qp] =
      atan(final_state.dilation_coefficient) * ADReal(180.0 / damage_mc_pi);
  _dilation_support_factor[_qp] = 1.0;
  const ADReal R_new = roughnessState(final_state.cumulative_slip);
  _roughness_state[_qp] = R_new;
  _roughness_damage[_qp] = ADReal(1.0) - R_new;
  _rate_state_theta[_qp] = final_state.rate_state_theta;
  _plastic_tangential_jump[_qp] = plastic_tangential_jump_new;

  const ADReal tau_final =
      sqrt(branch_traction_1 * branch_traction_1 + branch_traction_2 * branch_traction_2);
  _frictional_sliding_work_increment[_qp] = tau_final * gamma;
  _dilation_work_increment[_qp] = final_state.normal_pressure * final_state.dilation_increment;
  _frictional_dilatant_dissipation_increment[_qp] =
      _frictional_sliding_work_increment[_qp] - _dilation_work_increment[_qp];
  _cohesive_dissipation_increment[_qp] = final_state.cohesion * gamma;

  const ADReal reversible_opening =
      ADReal(_reversible_normal_compliance) *
      smoothPositive(ADReal(_reversible_normal_reference_stress) - final_state.normal_pressure,
                     _stress_regularization);
  _reversible_normal_opening[_qp] = reversible_opening;
  _normal_opening_total[_qp] = final_state.normal_plastic_jump + reversible_opening;

  _interface_traction_inc[_qp] = traction_new - ADRealVectorValue(ADReal(traction_old(0)),
                                                                  ADReal(traction_old(1)),
                                                                  ADReal(traction_old(2)));
}
