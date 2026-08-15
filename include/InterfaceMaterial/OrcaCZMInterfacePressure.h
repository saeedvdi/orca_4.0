#pragma once

#include "InterfaceMaterial.h"

/**
 * Computes the fracture (interface) pore pressure as the average of the bulk
 * pore_pressure variable evaluated on the element and neighbor sides of a CZM
 * sideset. Used to feed effective-stress-dependent interface constitutive
 * laws (e.g. Mohr-Coulomb friction).
 */
class OrcaCZMInterfacePressure : public InterfaceMaterial
{
public:
  static InputParameters validParams();
  OrcaCZMInterfacePressure(const InputParameters & parameters);

protected:
  void initQpStatefulProperties() override;
  void computeQpProperties() override;

  /// Base name of the material system
  const std::string _base_name;

  /// pore_pressure evaluated on the element side
  const ADVariableValue & _pressure;

  /// pore_pressure evaluated on the neighbor side
  const ADVariableValue & _pressure_neighbor;

  /// Output: average pore pressure at the interface
  ADMaterialProperty<Real> & _interface_pressure;
};
