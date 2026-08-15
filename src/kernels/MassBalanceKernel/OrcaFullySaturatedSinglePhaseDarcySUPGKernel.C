#include "OrcaFullySaturatedSinglePhaseDarcySUPGKernel.h"

#include "libmesh/elem.h"
#include <cmath>

registerMooseObject("OrcaApp", OrcaFullySaturatedSinglePhaseDarcySUPGKernel);

InputParameters
OrcaFullySaturatedSinglePhaseDarcySUPGKernel::validParams()
{
  InputParameters params = ADKernel::validParams();

  params.addClassDescription(
      "Tensor-permeability Darcy flux kernel (fully saturated, single-phase): "
      "q = gamma * K * (grad(p) - rho*g), where gamma = 1/mu (volumetric) or rho/mu (mass). "
      "Adds ∫ grad(test)·q dΩ. "
      "Also provides optional SUPG stabilization helpers for derived advection kernels.");

  params.addParam<bool>(
      "multiply_by_fluid_density",
      true,
      "If true, compute mass flux (rho*K/mu). If false, compute volumetric flux (K/mu).");

  // ---- SUPG controls (default off) ----
  params.addParam<bool>(
      "use_supg",
      false,
      "If true, derived advection kernels may add SUPG stabilization using base-class helpers.");

  params.addParam<Real>(
      "supg_tau",
      -1.0,
      "SUPG tau. If >= 0, uses this constant value. If < 0, tau is computed automatically.");

  params.addParam<Real>(
      "supg_alpha",
      1.0,
      "Scaling factor for automatically computed tau (only used if supg_tau < 0).");

  return params;
}

OrcaFullySaturatedSinglePhaseDarcySUPGKernel::OrcaFullySaturatedSinglePhaseDarcySUPGKernel(
    const InputParameters & parameters)
  : ADKernel(parameters),
    _multiply_by_fluid_density(getParam<bool>("multiply_by_fluid_density")),
    _rho_f(getADMaterialProperty<Real>("fluid_density_qp")),
    _mobility_tensor(getADMaterialProperty<RealTensorValue>("fluid_mobility_tensor_qp")),
    _g(getADMaterialProperty<RealVectorValue>("gravity_vector_qp")),
    _use_supg(getParam<bool>("use_supg")),
    _supg_tau_user(getParam<Real>("supg_tau")),
    _supg_alpha(getParam<Real>("supg_alpha"))
{
}

ADReal
OrcaFullySaturatedSinglePhaseDarcySUPGKernel::computeQpResidual()
{
  // divergence form: ∫ grad(test) · q dΩ
  // NOTE: we do NOT add SUPG here because this base kernel is used for pressure too.
  return _grad_test[_i][_qp] * computeDarcyFlux();
}

ADRealVectorValue
OrcaFullySaturatedSinglePhaseDarcySUPGKernel::computeDarcyFlux() const
{
  // This base kernel assumes its primary variable is pressure p
  return computeDarcyFluxFromGradP(_grad_u[_qp]);
}

ADRealVectorValue
OrcaFullySaturatedSinglePhaseDarcySUPGKernel::computeDarcyFluxFromGradP(const ADRealVectorValue & grad_p) const
{
  // mobility tensor: K/mu
  ADRealTensorValue mob = _mobility_tensor[_qp];

  // gamma factor:
  //   volumetric:  K/mu
  //   mass:        rho*K/mu
  if (_multiply_by_fluid_density)
    mob *= _rho_f[_qp];

  // driving force: grad(p) - rho*g
  const ADRealVectorValue grad_p_minus_rhog = grad_p - _rho_f[_qp] * _g[_qp];

  // Darcy flux: q = mob * (grad(p) - rho*g)
  return (mob * grad_p_minus_rhog);
}

// ----------------- SUPG helpers -----------------

Real
OrcaFullySaturatedSinglePhaseDarcySUPGKernel::computeSUPGTau(const ADRealVectorValue & a) const
{
  // If user provides constant tau, use it
  if (_supg_tau_user >= 0.0)
    return _supg_tau_user;

  // Auto tau ~ alpha * h / (2 |a|)
  // Use element hmin and raw values to avoid injecting extra nonlinear couplings via tau
  const Real h = _current_elem ? _current_elem->hmin() : 0.0;

  Real anorm_sq = 0.0;
  for (unsigned d = 0; d < LIBMESH_DIM; ++d)
  {
    const Real ad = MetaPhysicL::raw_value(a(d));
    anorm_sq += ad * ad;
  }

  const Real anorm = std::sqrt(anorm_sq);
  const Real eps = 1e-14;

  if (anorm < eps || h <= 0.0)
    return 0.0;

  return _supg_alpha * h / (2.0 * anorm + eps);
}

ADReal
OrcaFullySaturatedSinglePhaseDarcySUPGKernel::supgStabilization(const ADRealVectorValue & a,
                                                     const ADReal & scale) const
{
  if (!_use_supg)
    return 0.0;

  const Real tau = computeSUPGTau(a);
  if (tau <= 0.0)
    return 0.0;

  // SUPG: tau (a · grad(test)) (a · grad(u)) * scale
  const ADReal a_dot_grad_test = a * _grad_test[_i][_qp];
  const ADReal a_dot_grad_u    = a * _grad_u[_qp];

  return tau * a_dot_grad_test * a_dot_grad_u * scale;
}