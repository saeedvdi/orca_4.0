#include "OrcaCZMComputeLocalTractionIncrementalBase.h"

InputParameters
OrcaCZMComputeLocalTractionIncrementalBase::validParams()
{
  InputParameters params = InterfaceMaterial::validParams();
  return params;
}

OrcaCZMComputeLocalTractionIncrementalBase::OrcaCZMComputeLocalTractionIncrementalBase(
    const InputParameters & parameters)
  : InterfaceMaterial(parameters),
  _base_name(isParamValid("base_name") && !getParam<std::string>("base_name").empty()
                   ? getParam<std::string>("base_name") + "_"
                   : ""),
    _interface_traction(
        declareADPropertyByName<RealVectorValue>(_base_name + "interface_traction")),
    _interface_displacement_jump(
        getADMaterialPropertyByName<RealVectorValue>(_base_name + "interface_displacement_jump")),

    _interface_traction_inc(
        declareADPropertyByName<RealVectorValue>(_base_name + "interface_traction_inc")),
    _interface_traction_old(
        getMaterialPropertyOldByName<RealVectorValue>(_base_name + "interface_traction")),
    _interface_displacement_jump_inc(
        declareADPropertyByName<RealVectorValue>(_base_name + "interface_displacement_jump_inc")),
    _interface_displacement_jump_old(
        getMaterialPropertyOldByName<RealVectorValue>(_base_name + "interface_displacement_jump"))
{
}

void
OrcaCZMComputeLocalTractionIncrementalBase::initQpStatefulProperties()
{
  _interface_traction[_qp] = 0;
}

void
OrcaCZMComputeLocalTractionIncrementalBase::computeQpProperties()
{
  computeInterfaceTraction();
}

void
OrcaCZMComputeLocalTractionIncrementalBase::computeInterfaceTraction()
{
  // ADCZMComputeLocalTractionIncrementalBase
  _interface_displacement_jump_inc[_qp] =
      _interface_displacement_jump[_qp] - _interface_displacement_jump_old[_qp];
  computeInterfaceTractionIncrement();
  _interface_traction[_qp] = _interface_traction_inc[_qp] + _interface_traction_old[_qp];
}