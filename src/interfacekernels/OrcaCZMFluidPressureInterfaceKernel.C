#include "OrcaCZMFluidPressureInterfaceKernel.h"

registerMooseObject("OrcaApp", OrcaCZMFluidPressureInterfaceKernel);

InputParameters
OrcaCZMFluidPressureInterfaceKernel::validParams()
{
  InputParameters params = ADInterfaceKernel::validParams();

  params.addClassDescription(
      "Applies CZM fracture fluid pressure as a normal traction on the displacement residual.");
  params.addRequiredParam<unsigned int>(
      "component",
      "Displacement component this kernel acts on: 0=x, 1=y, 2=z.");
  params.addRequiredCoupledVar("displacements", "Displacement variables for dimension checking.");
  params.addParam<std::string>("base_name", "Material property base name");
  params.addParam<std::string>(
      "pore_pressure_property_name",
      "interface_pore_pressure",
      "Name of the interface pore pressure material property.");
  params.addParam<Real>(
      "pressure_traction_coefficient",
      -1.0,
      "Multiplier on p*n_local before rotation to global coordinates. The default -1 follows "
      "the app's tension-positive stress convention.");
  params.suppressParameter<bool>("use_displaced_mesh");

  return params;
}

OrcaCZMFluidPressureInterfaceKernel::OrcaCZMFluidPressureInterfaceKernel(
    const InputParameters & parameters)
  : ADInterfaceKernel(parameters),
    _base_name(isParamValid("base_name") && !getParam<std::string>("base_name").empty()
                   ? getParam<std::string>("base_name") + "_"
                   : ""),
    _component(getParam<unsigned int>("component")),
    _ndisp(coupledComponents("displacements")),
    _pressure_traction_coefficient(getParam<Real>("pressure_traction_coefficient")),
    _interface_pressure(getADMaterialPropertyByName<Real>(
        _base_name + getParam<std::string>("pore_pressure_property_name"))),
    _czm_total_rotation(getADMaterialPropertyByName<RankTwoTensor>(_base_name + "czm_total_rotation"))
{
  if (_ndisp != _mesh.dimension())
    paramError("displacements", "Number of displacements must match problem dimension.");

  if (_ndisp > 3 || _ndisp < 1)
    mooseError("the CZM pressure interface kernel requires 1, 2 or 3 displacement variables");
}

ADReal
OrcaCZMFluidPressureInterfaceKernel::computeQpResidual(Moose::DGResidualType type)
{
  const ADRealVectorValue local_pressure_traction(_pressure_traction_coefficient *
                                                      _interface_pressure[_qp],
                                                  0.0,
                                                  0.0);
  const ADRealVectorValue global_pressure_traction =
      _czm_total_rotation[_qp] * local_pressure_traction;

  ADReal r = global_pressure_traction(_component);

  switch (type)
  {
    case Moose::Element:
      r *= -_test[_i][_qp];
      break;
    case Moose::Neighbor:
      r *= _test_neighbor[_i][_qp];
      break;
  }

  return r;
}
