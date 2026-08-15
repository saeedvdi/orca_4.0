#include "OrcaCZMInterfacePressure.h"

registerMooseObject("OrcaApp", OrcaCZMInterfacePressure);

InputParameters
OrcaCZMInterfacePressure::validParams()
{
  InputParameters params = InterfaceMaterial::validParams();
  params.addClassDescription(
      "Averages the pore_pressure variable across a CZM sideset to produce a single "
      "fracture pore pressure usable by effective-stress-dependent interface materials.");
  params.addRequiredCoupledVar("pore_pressure", "The fluid pore pressure variable.");
  params.addParam<std::string>("base_name", "Material property base name");
  return params;
}

OrcaCZMInterfacePressure::OrcaCZMInterfacePressure(const InputParameters & parameters)
  : InterfaceMaterial(parameters),
    _base_name(isParamValid("base_name") && !getParam<std::string>("base_name").empty()
                   ? getParam<std::string>("base_name") + "_"
                   : ""),
    _pressure(adCoupledValue("pore_pressure")),
    _pressure_neighbor(adCoupledNeighborValue("pore_pressure")),
    _interface_pressure(declareADProperty<Real>(_base_name + "interface_pore_pressure"))
{
}

void
OrcaCZMInterfacePressure::initQpStatefulProperties()
{
  _interface_pressure[_qp] = 0;
}

void
OrcaCZMInterfacePressure::computeQpProperties()
{
  _interface_pressure[_qp] = 0.5 * (_pressure[_qp] + _pressure_neighbor[_qp]);
}
