#include "OrcaCZMRealVectorScalar.h"

registerMooseObject("OrcaApp", OrcaCZMRealVectorScalar);

InputParameters
OrcaCZMRealVectorScalar::validParams()
{
  InputParameters params = InterfaceMaterial::validParams();
  params.addClassDescription("Compute the normal or tangent component of an AD vector quantity defined "
                             "on a cohesive interface.");
  params.addRequiredParam<std::string>("real_vector_value", "The vector material name");
  params.addRequiredParam<MaterialPropertyName>(
      "property_name", "Name of the material property computed by this model");
  MooseEnum directionType("Normal Tangent");
  params.addRequiredParam<MooseEnum>("direction", directionType, "the direction: Normal, Tangent");
  params.addParam<std::string>("base_name", "Material property base name");
  return params;
}

OrcaCZMRealVectorScalar::OrcaCZMRealVectorScalar(const InputParameters & parameters)
  : InterfaceMaterial(parameters),
    _base_name(isParamValid("base_name") && !getParam<std::string>("base_name").empty()
                   ? getParam<std::string>("base_name") + "_"
                   : ""),
    _direction(getParam<MooseEnum>("direction").getEnum<DirectionType>()),
    _property(declareADPropertyByName<Real>(getParam<MaterialPropertyName>("property_name"))),
    _vector(getADMaterialPropertyByName<RealVectorValue>(_base_name +
                                                         getParam<std::string>("real_vector_value"))),
    _czm_rotation(getADMaterialPropertyByName<RankTwoTensor>(_base_name + "czm_total_rotation"))
{
}

void
OrcaCZMRealVectorScalar::computeQpProperties()
{
  const auto normal = _czm_rotation[_qp] * RealVectorValue(1.0, 0.0, 0.0);
  const auto normal_component = (normal * _vector[_qp]) * normal;
  const auto tangent_component = _vector[_qp] - normal_component;
  switch (_direction)
  {
    case DirectionType::Normal:
      _property[_qp] = normal_component * normal;
      break;
    case DirectionType::Tangent:
      _property[_qp] = tangent_component.norm();
      break;
    default:
      mooseError("ScalarType type not recognized");
      break;
  }
}