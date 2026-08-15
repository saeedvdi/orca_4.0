#pragma once

#include "InterfaceMaterial.h"

class OrcaCZMRealVectorScalar : public InterfaceMaterial
{
public:
  static InputParameters validParams();
  OrcaCZMRealVectorScalar(const InputParameters & parameters);

protected:
  void computeQpProperties() override;

  /// Base name of the material system
  const std::string _base_name;

  /// Scalar options
  enum class DirectionType
  {
    Normal,
    Tangent
  } _direction;

  /// The AD property created by this material
  ADMaterialProperty<Real> & _property;

  /// The AD vector material property
  const ADMaterialProperty<RealVectorValue> & _vector;

  /// The AD material property defining the CZM normal
  const ADMaterialProperty<RankTwoTensor> & _czm_rotation;
};