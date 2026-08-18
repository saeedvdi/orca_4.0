#include "ADOrcaBartonBandisRateStateHardening.h"
#include "metaphysicl/raw_type.h"
#include <cmath>

registerMooseObject("OrcaApp", ADOrcaBartonBandisRateStateHardening);
registerMooseObjectAliased("OrcaApp",
                           ADOrcaBartonBandisRateStateHardening,
                           "OrcaBartonBandisRateStateHardening");

namespace
{
/// L(x) = ln(1+x). Regularized logarithm: L(0) = 0 exactly, L'(x) = 1/(1+x) bounded,
/// L(x) -> ln(x) for x >> 1. Using ln(1+x) rather than ln(x) is what makes the V = 0
/// branch finite without a velocity floor.
inline Real
regLog(Real x)
{
  return std::log1p(std::max(Real(0.0), x));
}

/// phi(z) = (1 - exp(-z))/z, with phi(0) = 1. The exact-integral aging factor.
inline Real
agingPhi(Real z)
{
  if (std::abs(z) < 1.0e-8)
    return 1.0 - 0.5 * z + z * z / 6.0;
  return -std::expm1(-z) / z;
}

/// phi'(z) = (z*exp(-z) - (1 - exp(-z)))/z^2, with phi'(0) = -1/2.
inline Real
agingPhiPrime(Real z)
{
  if (std::abs(z) < 1.0e-8)
    return -0.5 + z / 3.0;
  const Real e = std::exp(-z);
  return (z * e + std::expm1(-z)) / (z * z);
}
}

InputParameters
ADOrcaBartonBandisRateStateHardening::validParams()
{
  InputParameters params = ADOrcaBartonBandisContactTractionFastADHardening::validParams();
  params.addClassDescription(
      "Barton-Bandis contact/traction law with slip weakening (parent) plus a "
      "Dieterich-Ruina rate-and-state shear overstress "
      "sigma'_n*[a*ln(1+V/V0) - b*ln(1+V_theta/V0)], replacing the linear Perzyna "
      "tangential_viscosity with two laboratory-measurable constants. theta obeys the "
      "aging law and continues to heal through elastic stick.");

  params.addParam<bool>(
      "use_rate_and_state",
      true,
      "If false the class reduces to its parent bit-for-bit (the control deck).");
  params.addRangeCheckedParam<Real>(
      "rsf_a",
      0.010,
      "rsf_a >= 0.0",
      "Rate-and-state direct effect a [-]. Laboratory range for granite saw cuts is "
      "0.008-0.015 at room temperature.");
  params.addRangeCheckedParam<Real>(
      "rsf_b",
      0.006,
      "rsf_b >= 0.0",
      "Rate-and-state evolution effect b [-]. a-b > 0 is velocity strengthening "
      "(aseismic creep, which is what these specimens do); a-b < 0 is velocity "
      "weakening and permits stick-slip.");
  params.addRangeCheckedParam<Real>(
      "rsf_characteristic_slip",
      5.0e-5,
      "rsf_characteristic_slip > 0.0",
      "State evolution distance D_rs [m]. This is the RATE-AND-STATE distance and is "
      "independent of the parent's characteristic_slip_distance, which sets the "
      "slip-weakening of the envelope itself. Two length scales, two mechanisms.");
  params.addRangeCheckedParam<Real>(
      "rsf_reference_velocity",
      5.0e-8,
      "rsf_reference_velocity > 0.0",
      "Reference slip velocity V0 [m/s]. The parent Barton-Bandis envelope is the "
      "strength at V -> 0 (fully healed), so V0 sets only where the logarithm turns "
      "over, not the absolute strength level.");
  params.addRangeCheckedParam<Real>(
      "rsf_theta0",
      0.0,
      "rsf_theta0 >= 0.0",
      "Initial state [s]. Zero seeds the steady state D_rs/V0. NOTE: this MUST be "
      "seeded in initQpStatefulProperties -- carryAdditionalState() copies old -> new "
      "and there is no old value at t = 0.");

  return params;
}

ADOrcaBartonBandisRateStateHardening::ADOrcaBartonBandisRateStateHardening(
    const InputParameters & parameters)
  : ADOrcaBartonBandisContactTractionFastADHardening(parameters),
    _use_rate_and_state(getParam<bool>("use_rate_and_state")),
    _rsf_a(getParam<Real>("rsf_a")),
    _rsf_b(getParam<Real>("rsf_b")),
    _rsf_Dc(getParam<Real>("rsf_characteristic_slip")),
    _rsf_V0(getParam<Real>("rsf_reference_velocity")),
    _rsf_theta0(getParam<Real>("rsf_theta0")),
    _rate_state_theta(declareProperty<Real>(_base_name + "rate_state_theta")),
    _rate_state_theta_old(getMaterialPropertyOld<Real>(_base_name + "rate_state_theta")),
    _rate_state_slip_velocity(declareProperty<Real>(_base_name + "rate_state_slip_velocity")),
    _rate_state_overstress(declareProperty<Real>(_base_name + "rate_state_overstress"))
{
  if (_use_rate_and_state && _tangential_viscosity > 0.0)
    paramWarning("tangential_viscosity",
                 "Both the Perzyna viscosity and rate-and-state are active. They occupy the "
                 "same slot in the return-mapping residual, so the rate dependence is "
                 "double-counted and neither constant means what it says. Set "
                 "tangential_viscosity = 0 unless you are deliberately bridging a legacy deck.");
}

void
ADOrcaBartonBandisRateStateHardening::initQpStatefulProperties()
{
  ADOrcaBartonBandisContactTractionFastADHardening::initQpStatefulProperties();

  // Seed theta HERE. carryAdditionalState() copies old -> new every step, which at t = 0
  // would pin theta at whatever the property was default-constructed to (0), and a zero
  // theta makes V_theta = D/theta infinite. This is the unseeded-stateful-property trap.
  _rate_state_theta[_qp] = _rsf_theta0 > 0.0 ? _rsf_theta0 : _rsf_Dc / _rsf_V0;
  _rate_state_slip_velocity[_qp] = 0.0;
  _rate_state_overstress[_qp] = 0.0;
}

// =============================================================================
// Aging law, exact integral over the step at constant V
//
//   dtheta/dt = 1 - V*theta/D,   V = dgp/dt,   z = V*dt/D = dgp/D
//   theta_new = theta_old*exp(-z) + dt*phi(z),   phi(z) = (1 - exp(-z))/z
//
// Note z depends on the slip INCREMENT alone, not on dt -- which is why the V -> 0
// limit theta_new = theta_old + dt falls out without a special case.
// =============================================================================
Real
ADOrcaBartonBandisRateStateHardening::agedTheta(Real plastic_slip_increment,
                                                Real & dtheta_dslip) const
{
  const Real theta_old = _rate_state_theta_old[_qp];
  const Real dt = _dt > 0.0 ? _dt : 0.0;
  const Real z = std::max(Real(0.0), plastic_slip_increment) / _rsf_Dc;
  const Real e = std::exp(-z);

  const Real theta = theta_old * e + dt * agingPhi(z);
  dtheta_dslip = (-theta_old * e + dt * agingPhiPrime(z)) / _rsf_Dc;
  return std::max(Real(0.0), theta);
}

// =============================================================================
// delta_mu = a*L(V/V0) - b*L(V_theta/V0),  V = dgp/dt,  V_theta = D/theta
// =============================================================================
Real
ADOrcaBartonBandisRateStateHardening::frictionPerturbation(Real plastic_slip_increment,
                                                           Real & dmu_dslip) const
{
  dmu_dslip = 0.0;
  if (!_use_rate_and_state || _dt <= 0.0)
    return 0.0;

  const Real V = std::max(Real(0.0), plastic_slip_increment) / _dt;
  const Real dV_dslip = 1.0 / _dt;

  Real dtheta_dslip = 0.0;
  const Real theta = agedTheta(plastic_slip_increment, dtheta_dslip);

  // V_theta = D/theta. theta is bounded below by dt*phi(z) > 0 whenever dt > 0, so the
  // division is safe; the guard covers a pathological dt = 0 reaching here.
  const Real theta_safe = std::max(theta, 1.0e-30);
  const Real V_theta = _rsf_Dc / theta_safe;
  const Real dVtheta_dslip = -_rsf_Dc / (theta_safe * theta_safe) * dtheta_dslip;

  const Real direct = _rsf_a * regLog(V / _rsf_V0);
  const Real state = _rsf_b * regLog(V_theta / _rsf_V0);

  dmu_dslip = _rsf_a / (_rsf_V0 + V) * dV_dslip - _rsf_b / (_rsf_V0 + V_theta) * dVtheta_dslip;

  return direct - state;
}

// =============================================================================
// Real hook -- called inside the safeguarded Newton loop, must not mutate state.
//
// The parent adds `extra` to the residual as  R = tau_trial - K_t*g - tau_lim - extra
// and `d_extra_d_g` to the derivative, so returning sigma'_n*delta_mu here puts the
// rate term in exactly the slot the Perzyna viscosity occupies.
// =============================================================================
Real
ADOrcaBartonBandisRateStateHardening::computeAdditionalShearStrengthReal(
    Real sigma_n,
    Real plastic_slip_increment,
    Real d_sigma_n_d_plastic_slip,
    Real & dstrength_dslip) const
{
  dstrength_dslip = 0.0;
  if (!_use_rate_and_state || _dt <= 0.0)
    return 0.0;

  Real dmu_dslip = 0.0;
  const Real delta_mu = frictionPerturbation(plastic_slip_increment, dmu_dslip);

  // Product rule: sigma'_n depends on the slip increment through dilation.
  dstrength_dslip = d_sigma_n_d_plastic_slip * delta_mu + sigma_n * dmu_dslip;
  return sigma_n * delta_mu;
}

// =============================================================================
// AD hook -- the IFT pass, called once with the CONVERGED slip increment. Only
// sigma_n carries derivative information here, matching the parent's convention.
// =============================================================================
ADReal
ADOrcaBartonBandisRateStateHardening::computeAdditionalShearStrength(
    const ADReal & sigma_n, Real plastic_slip_increment) const
{
  if (!_use_rate_and_state || _dt <= 0.0)
    return ADReal(0.0);

  Real dmu_dslip = 0.0;
  const Real delta_mu = frictionPerturbation(plastic_slip_increment, dmu_dslip);
  return sigma_n * ADReal(delta_mu);
}

// =============================================================================
// State carry / commit
// =============================================================================
void
ADOrcaBartonBandisRateStateHardening::carryAdditionalState()
{
  _rate_state_theta[_qp] = _rate_state_theta_old[_qp];
  _rate_state_slip_velocity[_qp] = 0.0;
  _rate_state_overstress[_qp] = 0.0;
}

void
ADOrcaBartonBandisRateStateHardening::commitAdditionalState(Real plastic_slip_increment)
{
  if (_dt <= 0.0)
    return;

  // The parent calls this with 0.0 on the elastic-stick path precisely so that a stuck
  // interface still heals: z = 0 gives theta_new = theta_old + dt.
  Real dtheta_dslip = 0.0;
  _rate_state_theta[_qp] = agedTheta(plastic_slip_increment, dtheta_dslip);
  _rate_state_slip_velocity[_qp] = std::max(Real(0.0), plastic_slip_increment) / _dt;

  Real dmu_dslip = 0.0;
  _rate_state_overstress[_qp] =
      _bb_effective_normal_stress[_qp] * frictionPerturbation(plastic_slip_increment, dmu_dslip);
}
