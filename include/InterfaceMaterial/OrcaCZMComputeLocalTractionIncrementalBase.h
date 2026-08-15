#pragma once

#include "InterfaceMaterial.h"

class OrcaCZMComputeLocalTractionIncrementalBase : public InterfaceMaterial
{
public:
  static InputParameters validParams();
  OrcaCZMComputeLocalTractionIncrementalBase(const InputParameters & parameters);

protected:
  void initQpStatefulProperties() override;
  void computeQpProperties() override;
  void computeInterfaceTraction();

  /// Method used to compute the traction increment
  virtual void computeInterfaceTractionIncrement() = 0;

  /// Base name of the material system
  const std::string _base_name;

  /// Total interface traction and displacement jump in local coordinates
  ADMaterialProperty<RealVectorValue> & _interface_traction;
  const ADMaterialProperty<RealVectorValue> & _interface_displacement_jump;

  /// Incremental formulation properties
  ADMaterialProperty<RealVectorValue> & _interface_traction_inc;
  const MaterialProperty<RealVectorValue> & _interface_traction_old;
  ADMaterialProperty<RealVectorValue> & _interface_displacement_jump_inc;
  const MaterialProperty<RealVectorValue> & _interface_displacement_jump_old;
};