#include "ADOrcaHystereticFracturePermeability.h"

#include "metaphysicl/raw_type.h"

#include <algorithm>
#include <limits>

registerMooseObject("OrcaApp", ADOrcaHystereticFracturePermeability);
registerMooseObjectAliased("OrcaApp",
                           ADOrcaHystereticFracturePermeability,
                           "OrcaHystereticFracturePermeability");

InputParameters
ADOrcaHystereticFracturePermeability::validParams()
{
  InputParameters params = ADOrcaRoughnessDamageFracturePermeability::validParams();
  params.addClassDescription(
      "Fracture permeability with a HYSTERETIC (path-dependent) normal closure. The reversible "
      "closure of the base class is the opening (unloading, sigma'_n decreasing) backbone; the "
      "re-closing (reloading, sigma'_n increasing above the most-open state) branch is "
      "unload_reload_stiffness_ratio x stiffer, so the joint retains opening on re-compression "
      "(a Bandis-Barton closure loop). Reduces to the reversible base law when "
      "unload_reload_stiffness_ratio = 1.");
  params.addRangeCheckedParam<Real>(
      "unload_reload_stiffness_ratio",
      1.0,
      "unload_reload_stiffness_ratio >= 1.0",
      "R >= 1: on re-closing (sigma'_n rising above the most-open state reached), the aperture closes "
      "only 1/R as fast as the opening backbone, so the joint stays more open than the single-path law. "
      "R = 1 recovers the reversible backbone (byte-identical to the base material).");
  params.addRangeCheckedParam<Real>(
      "hysteresis_preload_fraction",
      0.9,
      "hysteresis_preload_fraction > 0.0 & hysteresis_preload_fraction <= 1.0",
      "Fraction of reference_effective_normal_stress that sigma'_n must first reach before the "
      "hysteresis engages. This treats the initial preload ramp (0 -> preload) as virgin seating so the "
      "most-open state N_min is not latched onto the low transient sigma'_n during ramp-up.");
  return params;
}

ADOrcaHystereticFracturePermeability::ADOrcaHystereticFracturePermeability(
    const InputParameters & parameters)
  : ADOrcaRoughnessDamageFracturePermeability(parameters),
    _unload_reload_stiffness_ratio(getParam<Real>("unload_reload_stiffness_ratio")),
    _preload_fraction(getParam<Real>("hysteresis_preload_fraction")),
    _sigma_n_min(declareProperty<Real>(_base_name + "closure_sigma_n_min")),
    _sigma_n_min_old(getMaterialPropertyOld<Real>(_base_name + "closure_sigma_n_min")),
    _preloaded(declareProperty<Real>(_base_name + "closure_preloaded")),
    _preloaded_old(getMaterialPropertyOld<Real>(_base_name + "closure_preloaded"))
{
}

void
ADOrcaHystereticFracturePermeability::initQpStatefulProperties()
{
  ADOrcaRoughnessDamageFracturePermeability::initQpStatefulProperties();
  _sigma_n_min[_qp] = std::numeric_limits<Real>::max();
  _preloaded[_qp] = 0.0;
}

ADReal
ADOrcaHystereticFracturePermeability::computeStressAperture(const ADReal & N)
{
  const Real n_raw = MetaPhysicL::raw_value(N);

  // Engage the loop only after the joint has been seated by the preload ramp; before that the initial
  // 0 -> preload ramp is virgin loading and must not latch the most-open state onto the ramp transient.
  const bool preloaded =
      _preloaded_old[_qp] > 0.5 || n_raw >= _preload_fraction * _reference_effective_normal_stress;
  _preloaded[_qp] = preloaded ? 1.0 : 0.0;

  // Not yet seated, or plain reversible (R = 1): use the backbone and (re)seed the most-open state.
  if (!preloaded || _unload_reload_stiffness_ratio == 1.0)
  {
    _sigma_n_min[_qp] =
        preloaded ? std::min(_sigma_n_min_old[_qp], n_raw) : std::numeric_limits<Real>::max();
    return ADOrcaRoughnessDamageFracturePermeability::computeStressAperture(N);
  }

  // Running minimum of sigma'_n since preload (the most-open state = the reversal anchor). Uses the OLD
  // converged value -> the opening/re-closing branch is frozen within a Newton iteration.
  const Real n_min_old = _sigma_n_min_old[_qp];

  if (n_raw <= n_min_old)
  {
    // OPENING (sigma'_n at/below the most-open state) -> follow the soft backbone; extend N_min.
    _sigma_n_min[_qp] = n_raw;
    return ADOrcaRoughnessDamageFracturePermeability::computeStressAperture(N);
  }

  // RE-CLOSING (sigma'_n above the most-open state) -> stiffer branch anchored at the reversal:
  //   O(N) = O_b(N_min) - ( O_b(N_min) - O_b(N) ) / R
  // Continuous at N = N_min (both give O_b(N_min)); closes only 1/R as fast as the backbone.
  _sigma_n_min[_qp] = n_min_old;
  const ADReal o_b_min =
      ADOrcaRoughnessDamageFracturePermeability::computeStressAperture(ADReal(n_min_old));
  const ADReal o_b_n = ADOrcaRoughnessDamageFracturePermeability::computeStressAperture(N);
  return o_b_min - (o_b_min - o_b_n) / _unload_reload_stiffness_ratio;
}
