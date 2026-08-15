#include "OrcaFaultPressureInterfaceKernel.h"

registerMooseObject("OrcaApp", OrcaFaultPressureInterfaceKernel);

InputParameters
OrcaFaultPressureInterfaceKernel::validParams()
{
  InputParameters params = ADInterfaceKernel::validParams();
  params.addClassDescription(
      "Applies fracture fluid pressure traction to split-interface mechanics: "
      "t = traction_sign * alpha_eff * p_f * n.");
  params.addRequiredParam<unsigned int>("component",
                                        "Displacement component: 0->x, 1->y, 2->z.");
  params.addRequiredCoupledVar("fluid_pressure",
                               "Fluid pressure variable on the fracture interface.");
  params.addRangeCheckedParam<Real>(
      "effective_stress_coefficient",
      1.0,
      "effective_stress_coefficient >= 0.0 & effective_stress_coefficient <= 1.0",
      "Effective stress coefficient for pressure traction.");
  params.addRangeCheckedParam<Real>(
      "traction_sign",
      1.0,
      "traction_sign >= -1.0 & traction_sign <= 1.0",
      "Sign on pressure traction. Use -1 to make positive pressure reduce compression "
      "(effective-stress convention). Use +1 for legacy behavior.");
  params.addParam<bool>("use_average_pressure",
                        true,
                        "Use 0.5*(p_primary + p_secondary) if true; use primary p otherwise.");
  params.suppressParameter<bool>("use_displaced_mesh");
  return params;
}

OrcaFaultPressureInterfaceKernel::OrcaFaultPressureInterfaceKernel(
    const InputParameters & parameters)
  : ADInterfaceKernel(parameters),
    _component(getParam<unsigned int>("component")),
    _fluid_pressure(adCoupledValue("fluid_pressure")),
    _fluid_pressure_neighbor(adCoupledNeighborValue("fluid_pressure")),
    _effective_stress_coefficient(getParam<Real>("effective_stress_coefficient")),
    _traction_sign(getParam<Real>("traction_sign")),
    _use_average_pressure(getParam<bool>("use_average_pressure"))
{
  if (_component > 2)
    paramError("component", "Invalid component. Allowed values are 0, 1, 2.");
  if (_traction_sign != -1.0 && _traction_sign != 1.0)
    paramError("traction_sign", "Allowed values are exactly -1.0 or 1.0.");
}

ADReal
OrcaFaultPressureInterfaceKernel::computeQpResidual(Moose::DGResidualType type)
{
  const ADReal pressure =
      _use_average_pressure ? 0.5 * (_fluid_pressure[_qp] + _fluid_pressure_neighbor[_qp])
                            : _fluid_pressure[_qp];

  ADReal traction_component =
      _traction_sign * _effective_stress_coefficient * pressure * _normals[_qp](_component);

  switch (type)
  {
    case Moose::Element:
      traction_component *= -_test[_i][_qp];
      break;
    case Moose::Neighbor:
      traction_component *= _test_neighbor[_i][_qp];
      break;
  }

  return traction_component;
}
