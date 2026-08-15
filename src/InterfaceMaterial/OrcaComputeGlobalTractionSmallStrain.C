#include "OrcaComputeGlobalTractionSmallStrain.h"

registerMooseObject("OrcaApp", OrcaComputeGlobalTractionSmallStrain);

InputParameters
OrcaComputeGlobalTractionSmallStrain::validParams()
{
  InputParameters params = InterfaceMaterial::validParams();
  params.suppressParameter<bool>("use_displaced_mesh");
  params.addParam<std::string>("base_name", "Material property base name");
  return params;
}

OrcaComputeGlobalTractionSmallStrain::OrcaComputeGlobalTractionSmallStrain(const InputParameters & parameters)
  : InterfaceMaterial(parameters),
    _base_name(isParamValid("base_name") && !getParam<std::string>("base_name").empty()
                   ? getParam<std::string>("base_name") + "_"
                   : ""),
    _traction_global(declareADPropertyByName<RealVectorValue>(_base_name + "traction_global")),
    _interface_traction(getADMaterialPropertyByName<RealVectorValue>(_base_name + "interface_traction")),
    _czm_total_rotation(getADMaterialPropertyByName<RankTwoTensor>(_base_name + "czm_total_rotation"))
{
}

void
OrcaComputeGlobalTractionSmallStrain::computeQpProperties()
{
  computeEquilibriumTracion();
}

void
OrcaComputeGlobalTractionSmallStrain::computeEquilibriumTracion()
{
    _traction_global[_qp] = _czm_total_rotation[_qp] * _interface_traction[_qp];
}