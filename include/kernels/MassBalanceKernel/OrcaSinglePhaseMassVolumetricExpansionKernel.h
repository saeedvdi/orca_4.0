#pragma once
#include "ADTimeKernel.h"

/**
 * Adds fluid mass (or volume) change due to solid volumetric strain rate.
 *
 * Residual per qp:
 *   R = test * (dens) * porosity * strain_rate
 * where dens = rho if multiply_by_fluid_density, else 1.0.
 */
 
class OrcaSinglePhaseMassVolumetricExpansionKernel : public ADTimeKernel
{
public:
  static InputParameters validParams();
  OrcaSinglePhaseMassVolumetricExpansionKernel(const InputParameters & parameters);

protected:
  virtual ADReal computeQpResidual() override;

  const bool _multiply_by_fluid_density;

  const ADMaterialProperty<Real> & _vol_strain_rate;
  const ADMaterialProperty<Real> & _porosity;
  const ADMaterialProperty<Real> * _fluid_density;
};