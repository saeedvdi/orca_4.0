#pragma once

#include "AuxKernel.h"

/**
 * Outputs one Cartesian component of the physical, volumetric Darcy velocity
 *
 *   v = -(K / mu) (grad(p) - rho g).
 *
 * This is the velocity corresponding to the ORCA saturated Darcy kernels.  It
 * deliberately does not include the optional density multiplier used when the
 * mass-balance residual is assembled in mass-flux form.
 */
class OrcaDarcyVelocityComponent : public AuxKernel
{
public:
  static InputParameters validParams();

  OrcaDarcyVelocityComponent(const InputParameters & parameters);

protected:
  Real computeValue() override;

private:
  const unsigned int _component;
  const ADVariableGradient & _grad_p;
  const ADMaterialProperty<Real> & _rho_f;
  const ADMaterialProperty<RealTensorValue> & _mobility;
  const ADMaterialProperty<RealVectorValue> & _gravity;
};
