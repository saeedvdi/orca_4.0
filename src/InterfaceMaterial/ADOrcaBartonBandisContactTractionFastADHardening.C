#include "ADOrcaBartonBandisContactTractionFastADHardening.h"
#include "metaphysicl/raw_type.h"
#include <cmath>

registerMooseObject("OrcaApp", ADOrcaBartonBandisContactTractionFastADHardening);
registerMooseObjectAliased("OrcaApp",
                           ADOrcaBartonBandisContactTractionFastADHardening,
                           "OrcaBartonBandisContactTractionFastADHardening");

InputParameters
ADOrcaBartonBandisContactTractionFastADHardening::validParams()
{
  InputParameters params = ADOrcaBartonBandisContactTractionFastAD::validParams();
  params.addClassDescription(
      "Barton-Bandis contact/traction-separation law (FastAD) with an additional post-peak "
      "slip-weakening law: mu(s^p) = mu_r + (mu_p - mu_r)*exp(-(s^p / D_c)^m), "
      "applied independently of JRC mobilization.");

  params.addParam<bool>("use_slip_weakening", true,
      "If true, apply exponential slip-weakening of friction from phi_p to phi_r.");
  params.addRangeCheckedParam<Real>("characteristic_slip_distance", 1e-3,
      "characteristic_slip_distance > 0.0",
      "Characteristic slip-weakening distance D_c [m]. "
      "Friction decays from peak to residual over this length scale.");
  params.addRangeCheckedParam<Real>("slip_weakening_exponent", 1.0,
      "slip_weakening_exponent >= 1.0",
      "Exponent m in W = exp(-(s^p / D_c)^m). The default m=1 reproduces the "
      "legacy exponential slip-weakening law.");
  params.addParam<Real>("slip_weakening_residual_friction_angle_degrees", -1.0,
      "Residual friction angle used only by the slip-weakening tail. A negative value "
      "uses residual_friction_angle_degrees, preserving legacy behavior. Setting this "
      "separately lets the Barton-Bandis peak envelope and the post-slip tail be tuned "
      "independently.");

  params.addParam<bool>("use_roughness_degradation", false,
      "If true, roughness_state decays exponentially with cumulative plastic slip: "
      "R = exp(-s^p / D_r).  When false, roughness_state = 1 (no degradation).");
  params.addRangeCheckedParam<Real>("roughness_characteristic_slip", 1e-3,
      "roughness_characteristic_slip > 0.0",
      "Characteristic slip distance for roughness degradation D_r [m]. "
      "roughness_state decays from 1 to 0 over this length scale.");
  params.addRangeCheckedParam<Real>("roughness_state_initial", 1.0,
      "roughness_state_initial >= 0.0 & roughness_state_initial <= 1.0",
      "Initial roughness_state R_ini at zero slip (default 1.0 = legacy). With "
      "roughness_state_residual this generalizes the degradation law to "
      "R = R_res + (R_ini - R_res)*exp(-s^p / D_r), letting the exported roughness_state "
      "match a calibrated retention curve in the downstream permeability material "
      "(e.g. the decoupled-roughness law's R: 0.45 -> 0.10).");
  params.addRangeCheckedParam<Real>("roughness_state_residual", 0.0,
      "roughness_state_residual >= 0.0 & roughness_state_residual <= 1.0",
      "Residual roughness_state R_res after large slip (default 0.0 = legacy).");

  return params;
}

ADOrcaBartonBandisContactTractionFastADHardening::ADOrcaBartonBandisContactTractionFastADHardening(
    const InputParameters & parameters)
  : ADOrcaBartonBandisContactTractionFastAD(parameters),
    _use_slip_weakening(getParam<bool>("use_slip_weakening")),
    _characteristic_slip_distance(getParam<Real>("characteristic_slip_distance")),
    _slip_weakening_exponent(getParam<Real>("slip_weakening_exponent")),
    _slip_weakening_residual_friction_angle_deg(
        getParam<Real>("slip_weakening_residual_friction_angle_degrees")),
    _use_roughness_degradation(getParam<bool>("use_roughness_degradation")),
    _roughness_characteristic_slip(getParam<Real>("roughness_characteristic_slip")),
    _roughness_state_initial(getParam<Real>("roughness_state_initial")),
    _roughness_state_residual(getParam<Real>("roughness_state_residual"))
{
  if (_slip_weakening_residual_friction_angle_deg >= 89.9)
    paramError("slip_weakening_residual_friction_angle_degrees", "Must be < 89.9 degrees.");
  if (_roughness_state_residual > _roughness_state_initial)
    paramError("roughness_state_residual", "Must be <= roughness_state_initial.");
}

// =============================================================================
// AD version (used in IFT pass — carries full derivative information)
// =============================================================================
void
ADOrcaBartonBandisContactTractionFastADHardening::computeBartonBandisProperties(
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
  ADOrcaBartonBandisContactTractionFastAD::computeBartonBandisProperties(
      sigma_n, cumulative_slip, jrc_mobilized, roughness_angle_deg, peak_friction_angle_deg,
      friction_coefficient, dilation_angle_deg, dilation_coefficient, shear_strength);

  if (!_use_slip_weakening)
    return;

  using std::exp; using std::pow; using std::tan;
  const Real phi_r_deg = _slip_weakening_residual_friction_angle_deg >= 0.0
                             ? _slip_weakening_residual_friction_angle_deg
                             : _residual_friction_angle_deg;
  const ADReal mu_r(std::tan(phi_r_deg * M_PI / 180.0));
  const ADReal mu_p = friction_coefficient;  // BB peak from base
  const ADReal x = std::max(ADReal(0.0),
                            cumulative_slip / ADReal(_characteristic_slip_distance));
  const ADReal W = exp(-pow(x, Real(_slip_weakening_exponent)));
  friction_coefficient = mu_r + (mu_p - mu_r) * W;
  shear_strength       = sigma_n * friction_coefficient;
  // Re-apply the base-class residual self-propping floor: slip-weakening above overwrote
  // shear_strength, so without this the floor would be bypassed in the Hardening model.
  if (_min_tau_limit > 0.0)
    shear_strength = std::max(ADReal(_min_tau_limit), shear_strength);
}

// =============================================================================
// Real version (used in the NR loop — no AD overhead)
// =============================================================================
void
ADOrcaBartonBandisContactTractionFastADHardening::computeBartonBandisPropertiesReal(
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
  ADOrcaBartonBandisContactTractionFastAD::computeBartonBandisPropertiesReal(
      sigma_n, cumulative_slip, jrc_mobilized, roughness_angle_deg, peak_friction_angle_deg,
      friction_coefficient, dilation_angle_deg, dilation_coefficient, shear_strength);

  if (!_use_slip_weakening)
    return;

  const Real phi_r_deg = _slip_weakening_residual_friction_angle_deg >= 0.0
                             ? _slip_weakening_residual_friction_angle_deg
                             : _residual_friction_angle_deg;
  const Real mu_r = std::tan(phi_r_deg * M_PI / 180.0);
  const Real mu_p = friction_coefficient;  // BB peak from base
  const Real x = std::max(Real(0.0), cumulative_slip / _characteristic_slip_distance);
  const Real W = std::exp(-std::pow(x, _slip_weakening_exponent));
  friction_coefficient = mu_r + (mu_p - mu_r) * W;
  shear_strength       = sigma_n * friction_coefficient;
  // Re-apply the base-class residual self-propping floor (slip-weakening overwrote it).
  if (_min_tau_limit > 0.0)
    shear_strength = std::max(_min_tau_limit, shear_strength);
}

// =============================================================================
// Analytical derivative dR/d(delta_gamma_p) with slip-weakening contributions
//
// With  mu_eff = mu_r + (mu_p - mu_r) * W,  W = exp(-(s^p / D_c)^m):
//
//   d(mu_eff)/d(sigma_n)   = W * d(mu_p)/d(sigma_n)
//   d(mu_eff)/d(cumslip)   = W * d(mu_p)/d(cumslip) + (mu_p - mu_r) * dW/ds
//
// The dilation and sigma_n terms are identical to the base class.
// =============================================================================
Real
ADOrcaBartonBandisContactTractionFastADHardening::computeReturnMappingDerivative(
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
  if (!_use_slip_weakening)
    return ADOrcaBartonBandisContactTractionFastAD::computeReturnMappingDerivative(
        sigma_n, kn_tangent, jrc_mobilized, roughness_angle_deg, peak_friction_angle_deg,
        mu, dilation_coefficient, dilation_increment, closure_new, cumulative_slip_new);

  // d(dilation)/d(delta_gamma_p): zero when a cap is active
  Real d_dil_d_g = 0.0;
  if (_use_dilatancy)
  {
    const bool dilation_cap_active = (_max_dilation_increment > 0.0 &&
                                      dilation_increment >= _max_dilation_increment - 1e-14);
    const bool closure_cap_active  = (_cap_dilation_to_available_closure && closure_new <= 1e-14);
    if (!dilation_cap_active && !closure_cap_active)
      d_dil_d_g = dilation_coefficient;
  }

  // Mirror the base-class kinematic-dilation sign threading: closure_new =
  // closure_old + _dil_closure_sign * dilation. Legacy (_dil_closure_sign=-1)
  // reproduces the original -d_dil_d_g exactly.
  const Real d_sn_d_g = kn_tangent * (_dil_closure_sign * d_dil_d_g);

  const Real phi_rad  = peak_friction_angle_deg * M_PI / 180.0;
  const Real cos2_phi = std::max(Real(1e-14), std::cos(phi_rad) * std::cos(phi_rad));
  const Real d_mu_bb_d_phi = 1.0 / cos2_phi;
  const Real deg_to_rad    = M_PI / 180.0;

  const bool ra_at_lower  = (!_allow_negative_roughness_angle && roughness_angle_deg <= 0.0);
  const bool phi_at_lower = (peak_friction_angle_deg <= _min_friction_angle_deg + 1e-10);
  const bool phi_at_upper = (peak_friction_angle_deg >= _max_friction_angle_deg - 1e-10);
  const bool phi_interior = !phi_at_lower && !phi_at_upper && !ra_at_lower;

  const Real x = std::max(Real(0.0), cumulative_slip_new / _characteristic_slip_distance);
  const Real W = std::exp(-std::pow(x, _slip_weakening_exponent));
  const Real phi_r_deg = _slip_weakening_residual_friction_angle_deg >= 0.0
                             ? _slip_weakening_residual_friction_angle_deg
                             : _residual_friction_angle_deg;
  const Real mu_r = std::tan(phi_r_deg * M_PI / 180.0);
  const Real mu_p = std::tan(peak_friction_angle_deg * M_PI / 180.0);

  // d(mu_eff)/d(sigma_n) = W * d(mu_bb)/d(sigma_n)
  Real d_mu_eff_d_sn = 0.0;
  if (phi_interior && sigma_n > _compressive_normal_stress_floor)
  {
    const Real d_mu_bb_d_sn = d_mu_bb_d_phi * deg_to_rad *
        (-jrc_mobilized / (sigma_n * std::log(Real(10.0))));
    d_mu_eff_d_sn = W * d_mu_bb_d_sn;
  }

  // d(mu_eff)/d(cumslip) = W * d(mu_bb)/d(cumslip) + (mu_p - mu_r) * dW/ds
  Real dW_d_cumslip = 0.0;
  if (x > 0.0)
    dW_d_cumslip = -W * _slip_weakening_exponent *
                   std::pow(x, _slip_weakening_exponent - Real(1.0)) /
                   _characteristic_slip_distance;
  else if (_slip_weakening_exponent == 1.0)
    dW_d_cumslip = -W / _characteristic_slip_distance;

  Real d_mu_eff_d_cumslip = (mu_p - mu_r) * dW_d_cumslip;
  if (_use_mobilized_jrc && phi_interior)
  {
    const Real sbar = std::max(Real(0.0),
        std::min(Real(1.0), cumulative_slip_new / _peak_shear_displacement));
    if (sbar > 0.0 && sbar < 1.0)
    {
      const Real sigma_eff  = std::max(_compressive_normal_stress_floor, sigma_n);
      const Real log_ratio  = std::log10(std::max(Real(1e-30), _jcs_scaled_const / sigma_eff));
      const Real d_jrc_d_cumslip = _jrc_scaled_const * _mobilized_jrc_exponent *
          std::pow(sbar, _mobilized_jrc_exponent - Real(1.0)) / _peak_shear_displacement;
      const Real d_mu_bb_d_cumslip = d_mu_bb_d_phi * deg_to_rad * d_jrc_d_cumslip * log_ratio;
      d_mu_eff_d_cumslip += W * d_mu_bb_d_cumslip;
    }
  }

  const Real d_taulim_d_g = mu * d_sn_d_g +
      sigma_n * (d_mu_eff_d_sn * d_sn_d_g + d_mu_eff_d_cumslip);
  return -Real(_penalty_tangent) - d_taulim_d_g;
}

// =============================================================================
// Roughness degradation: R = R_res + (R_ini - R_res) * exp(-s^p / D_r)
// roughness_state decays from R_ini (default 1, intact) toward R_res (default 0)
// as cumulative plastic slip accumulates. The permeability model reads this via
// roughness_retention_factor to reduce dilation retention as the joint surface
// wears; the R_ini/R_res bounds let the exported curve match a retention
// calibration done with the decoupled-roughness law (R: 0.45 -> 0.10).
// =============================================================================
Real
ADOrcaBartonBandisContactTractionFastADHardening::computeRoughnessState() const
{
  if (!_use_roughness_degradation)
    return ADOrcaBartonBandisContactTractionFastAD::computeRoughnessState();
  const Real s = _cumulative_plastic_slip[_qp];
  return _roughness_state_residual + (_roughness_state_initial - _roughness_state_residual) *
                                         std::exp(-s / _roughness_characteristic_slip);
}
