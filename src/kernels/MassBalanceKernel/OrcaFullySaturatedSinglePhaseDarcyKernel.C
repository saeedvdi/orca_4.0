#include "OrcaFullySaturatedSinglePhaseDarcyKernel.h"

registerMooseObject("OrcaApp", OrcaFullySaturatedSinglePhaseDarcyKernel);

InputParameters
OrcaFullySaturatedSinglePhaseDarcyKernel::validParams()
{
  InputParameters params = ADKernel::validParams();

  params.addClassDescription(
      "Tensor-permeability Darcy flux kernel (fully saturated, single-phase): "
      "q = gamma * K * (grad(p) - rho*g), where gamma = 1/mu (volumetric) or rho/mu (mass). "
      "Adds ∫ grad(test)·q dΩ.");

  params.addParam<bool>(
      "multiply_by_fluid_density",
      true,
      "If true, compute mass flux (rho*K/mu). If false, compute volumetric flux (K/mu).");

  return params;
}

OrcaFullySaturatedSinglePhaseDarcyKernel::OrcaFullySaturatedSinglePhaseDarcyKernel(
    const InputParameters & parameters)
  : ADKernel(parameters),
    _multiply_by_fluid_density(getParam<bool>("multiply_by_fluid_density")),
    _rho_f(getADMaterialProperty<Real>("fluid_density_qp")),
    _mobility_tensor(getADMaterialProperty<RealTensorValue>("fluid_mobility_tensor_qp")),
    _g(getADMaterialProperty<RealVectorValue>("gravity_vector_qp"))
{
}

ADReal
OrcaFullySaturatedSinglePhaseDarcyKernel::computeQpResidual()
{
  // divergence form: ∫ grad(test) · q dΩ
  return _grad_test[_i][_qp] * computeDarcyFlux();
}

ADRealVectorValue
OrcaFullySaturatedSinglePhaseDarcyKernel::computeDarcyFlux() const
{
  // This base kernel assumes its primary variable is pressure p
  return computeDarcyFluxFromGradP(_grad_u[_qp]);
}

ADRealVectorValue
OrcaFullySaturatedSinglePhaseDarcyKernel::computeDarcyFluxFromGradP(const ADRealVectorValue & grad_p) const
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