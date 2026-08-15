#include "OrcaCZMRealVectorCartesianComponent.h"

registerMooseObject("OrcaApp", OrcaCZMRealVectorCartesianComponent);

InputParameters
OrcaCZMRealVectorCartesianComponent::validParams()
{
  InputParameters params = InterfaceMaterial::validParams();
  params.addClassDescription("Access a component of an AD RealVectorValue defined on a cohesive zone");
  params.addRequiredParam<std::string>("real_vector_value", "The vector material name");
  params.addRequiredParam<MaterialPropertyName>(
      "property_name", "Name of the material property computed by this model");
  params.addRequiredRangeCheckedParam<unsigned int>(
      "index", "index >= 0 & index <= 2", "The vector component output (0, 1, 2)");
  params.addParam<std::string>("base_name", "Material property base name");
  return params;
}

OrcaCZMRealVectorCartesianComponent::OrcaCZMRealVectorCartesianComponent(
    const InputParameters & parameters)
  : InterfaceMaterial(parameters),
    _base_name(isParamValid("base_name") && !getParam<std::string>("base_name").empty()
                   ? getParam<std::string>("base_name") + "_"
                   : ""),
    _property(declareADPropertyByName<Real>(getParam<MaterialPropertyName>("property_name"))),
    _vector(getADMaterialPropertyByName<RealVectorValue>(_base_name +
                                                         getParam<std::string>("real_vector_value"))),
    _index(getParam<unsigned int>("index"))
{
}

void
OrcaCZMRealVectorCartesianComponent::computeQpProperties()
{
  _property[_qp] = _vector[_qp](_index);
}