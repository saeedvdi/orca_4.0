#pragma once

#include "InterfaceMaterial.h"

#include <vector>

class OrcaCZMComputeDisplacementJump : public InterfaceMaterial
{
public:
  static InputParameters validParams();
  OrcaCZMComputeDisplacementJump(const InputParameters & parameters);

protected:
  void initQpStatefulProperties() override;
  void computeQpProperties() override;

  /// Compute the displacement jump in interface-local coordinates
  void computeLocalDisplacementJump();

  /// Compute the interface rotation matrix
  void computeRotationMatrices();

  /// Base name of the material system
  const std::string _base_name;

  /// Number of displacement components
  const unsigned int _ndisp;

  /// Coupled displacement values on current and neighbor sides
  std::vector<const ADVariableValue *> _disp;
  std::vector<const ADVariableValue *> _disp_neighbor;

  /// Displacement jump in global and interface coordinates
  ADMaterialProperty<RealVectorValue> & _displacement_jump_global;
  ADMaterialProperty<RealVectorValue> & _interface_displacement_jump;

  /// Rotation matrix transforming interface/global coordinate systems
  ADMaterialProperty<RankTwoTensor> & _czm_total_rotation;
};