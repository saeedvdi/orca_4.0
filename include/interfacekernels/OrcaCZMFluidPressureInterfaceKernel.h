#pragma once

#include "ADInterfaceKernel.h"

/**
 * Applies fracture fluid pressure as a normal traction on a CZM sideset.
 *
 * The pressure value is usually supplied by OrcaCZMInterfacePressure. The local
 * pressure traction is converted to global coordinates with the CZM rotation
 * matrix, then assembled with the same element/neighbor signs as
 * OrcaMechInterfaceKernel.
 */
class OrcaCZMFluidPressureInterfaceKernel : public ADInterfaceKernel
{
public:
  static InputParameters validParams();
  OrcaCZMFluidPressureInterfaceKernel(const InputParameters & parameters);

protected:
  ADReal computeQpResidual(Moose::DGResidualType type) override;

  const std::string _base_name;
  const unsigned int _component;
  const unsigned int _ndisp;

  /// Multiplier on p*n_local. Use -1 for the same tension-positive convention as total stress.
  const Real _pressure_traction_coefficient;

  const ADMaterialProperty<Real> & _interface_pressure;
  const ADMaterialProperty<RankTwoTensor> & _czm_total_rotation;
};
