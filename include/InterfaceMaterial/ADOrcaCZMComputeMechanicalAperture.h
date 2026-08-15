#pragma once

#include "InterfaceMaterial.h"

class ADOrcaCZMComputeMechanicalAperture : public InterfaceMaterial
{
public:
  static InputParameters validParams();
  ADOrcaCZMComputeMechanicalAperture(const InputParameters & parameters);

protected:
  void computeQpProperties() override;

  /// Base name of the material system
  const std::string _base_name;

  /// Local interface displacement jump (normal component is index 0)
  const ADMaterialProperty<RealVectorValue> & _interface_displacement_jump;

  /// Mechanical aperture (optionally clamped to opening only)
  /// This is the reversible elastic opening contribution.
  ADMaterialProperty<Real> & _mechanical_aperture;

  /// Raw normal jump before clamping
  ADMaterialProperty<Real> & _mechanical_aperture_raw;

  /// If true, store max(jump_n, 0) in _mechanical_aperture
  /// (compression does not drive the reported aperture below zero).
  const bool _clamp_to_zero;
};
