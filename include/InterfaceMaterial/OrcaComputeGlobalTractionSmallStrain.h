#pragma once

#include "InterfaceMaterial.h"

class OrcaComputeGlobalTractionSmallStrain : public InterfaceMaterial
{
public:
  static InputParameters validParams();
  OrcaComputeGlobalTractionSmallStrain(const InputParameters & parameters);

protected:
  void computeQpProperties() override;
  void computeEquilibriumTracion();

  const std::string _base_name;

  ADMaterialProperty<RealVectorValue> & _traction_global;
  const ADMaterialProperty<RealVectorValue> & _interface_traction;
  const ADMaterialProperty<RankTwoTensor> & _czm_total_rotation;
};