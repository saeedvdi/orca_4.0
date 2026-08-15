#include "OrcaHeatConductionKernel.h"

registerMooseObject("OrcaApp", OrcaHeatConductionKernel);

InputParameters
OrcaHeatConductionKernel::validParams()
{
  InputParameters params = ADKernelGrad::validParams();
  params.addClassDescription("Heat conduction: q = -K grad(T), contributes div(q) in the energy equation."
                             "Adds ∫ grad(test) · (q) dΩ. this is simply the diffusiion term multiplied by the test function.");

  return params;
}

OrcaHeatConductionKernel::OrcaHeatConductionKernel(const InputParameters & parameters)
  : ADKernelGrad(parameters),
    _thermal_conductivity(getADMaterialProperty<RealTensorValue>("effective_thermal_conductivity_qp"))
{
}

ADRealVectorValue
OrcaHeatConductionKernel::precomputeQpResidual()
{
  // In ADKernelGrad, this returned vector F is used in: R = grad_test · F
  // Here: F = K * grad(T)
  return _thermal_conductivity[_qp] * _grad_u[_qp];
}
