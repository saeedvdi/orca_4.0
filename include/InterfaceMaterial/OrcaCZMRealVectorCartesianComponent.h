#pragma once

#include "InterfaceMaterial.h"

class OrcaCZMRealVectorCartesianComponent : public InterfaceMaterial
{
public:
  static InputParameters validParams();
  OrcaCZMRealVectorCartesianComponent(const InputParameters & parameters);

protected:
  void computeQpProperties() override;

  /// Base name of the material system
  const std::string _base_name;

  /// The AD property created by this material
  ADMaterialProperty<Real> & _property;

  /// The AD vector material property
  const ADMaterialProperty<RealVectorValue> & _vector;

  /// The component of vector to extract
  const unsigned int _index;
};