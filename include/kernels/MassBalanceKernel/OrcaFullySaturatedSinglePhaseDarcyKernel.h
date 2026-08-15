#pragma once

#include "ADKernel.h"

/**
 * Tensor-permeability Darcy flux kernel (fully saturated, single-phase):
 *
 *   q = -gamma * K * (grad(p) - rho*g)
 *
 * where gamma is either:
 *   - 1/mu   (volumetric flux)   if multiply_by_fluid_density = false
 *   - rho/mu (mass flux)         if multiply_by_fluid_density = true
 *
 * Weak form contribution for a divergence term:
 *   ∫ grad(test) · q dΩ
 */
class OrcaFullySaturatedSinglePhaseDarcyKernel : public ADKernel
{
public:
  static InputParameters validParams();
  OrcaFullySaturatedSinglePhaseDarcyKernel(const InputParameters & parameters);

protected:
  virtual ADReal computeQpResidual() override;

  /// Darcy flux built from a supplied grad(p) (useful for derived kernels)
  ADRealVectorValue computeDarcyFluxFromGradP(const ADRealVectorValue & grad_p) const;

  /// Darcy flux for *this kernel's primary variable* (uses _grad_u)
  virtual ADRealVectorValue computeDarcyFlux() const;

  const bool _multiply_by_fluid_density;

  const ADMaterialProperty<Real> & _rho_f;
  const ADMaterialProperty<RealTensorValue> & _mobility_tensor; // K/mu (tensor mobility)
  const ADMaterialProperty<RealVectorValue> & _g;               // gravity vector
};