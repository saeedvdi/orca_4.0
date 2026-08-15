#include "OrcaNormalPressureBC.h"
#include "Function.h"

registerMooseObject("OrcaApp", OrcaNormalPressureBC);

InputParameters
OrcaNormalPressureBC::validParams()
{
  InputParameters params = IntegratedBC::validParams();
  params.addClassDescription("Applies a pressure on a given boundary in a given direction.");
  params.addRequiredParam<unsigned int>("component", "The component for the pressure.");
  params.addParam<Real>("value", 0.0, "Value of the pressure applied.");
  params.addParam<FunctionName>("function", "The function that describes the pressure.");
  params.set<bool>("use_displaced_mesh") = false;
  return params;
}

OrcaNormalPressureBC::OrcaNormalPressureBC(const InputParameters & parameters)
  : IntegratedBC(parameters),
    _component(getParam<unsigned int>("component")),
    _value(getParam<Real>("value")),
    _function(isParamValid("function") ? &getFunction("function") : nullptr)
{
  if (_component > 2)
    paramError("component", "Invalid component given.\n");
}

Real
OrcaNormalPressureBC::computeQpResidual()
{
  Real value = _value;

  if (_function)
    value = _function->value(_t, _q_point[_qp]);

  return value * (_normals[_qp](_component) * _test[_i][_qp]);
}
