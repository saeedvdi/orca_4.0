
#include "OrcaHeatConductionTimeDerivativeKernel.h"

registerMooseObject("OrcaApp", OrcaHeatConductionTimeDerivativeKernel);

InputParameters
OrcaHeatConductionTimeDerivativeKernel::validParams()
{
  InputParameters params = ADTimeKernelValue::validParams();
  params.addClassDescription("Time derivative term $\\rho c_p \\frac{\\partial T}{\\partial t}$ of "
                             "the thermal energy conservation equation.");

//   // Density may be changing with deformation, so we must integrate
//   // over current volume by setting the use_displaced_mesh flag.
//   params.set<bool>("use_displaced_mesh") = true;

  return params;
}

OrcaHeatConductionTimeDerivativeKernel::OrcaHeatConductionTimeDerivativeKernel(const InputParameters & parameters)
    : ADTimeKernelValue(parameters),
    _cp_s(getADMaterialProperty<Real>("solid_specific_heat_capacity_qp")),
    _rho_s(getADMaterialProperty<Real>("solid_density_qp"))
{
}

// the ADTimeKernelValue the whole residual would be multiplied by the _test[_i][_qp].
ADReal
OrcaHeatConductionTimeDerivativeKernel::precomputeQpResidual()
{
    return _cp_s[_qp] * _rho_s[_qp] * _u_dot[_qp];
}