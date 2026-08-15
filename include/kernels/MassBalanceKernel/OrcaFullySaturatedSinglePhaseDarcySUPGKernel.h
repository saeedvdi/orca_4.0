#pragma once

#include "ADKernel.h"
#include "metaphysicl/raw_type.h"

class OrcaFullySaturatedSinglePhaseDarcySUPGKernel : public ADKernel
{
public:
  static InputParameters validParams();

  OrcaFullySaturatedSinglePhaseDarcySUPGKernel(const InputParameters & parameters);

protected:
  virtual ADReal computeQpResidual() override;

  ADRealVectorValue computeDarcyFlux() const;
  ADRealVectorValue computeDarcyFluxFromGradP(const ADRealVectorValue & grad_p) const;

  // ---- SUPG helpers (optional, used by derived advection kernels) ----
  Real computeSUPGTau(const ADRealVectorValue & advective_flux) const;

  /// Returns tau * (a · grad(test)) * (a · grad(u)) * scale
  ADReal supgStabilization(const ADRealVectorValue & advective_flux,
                           const ADReal & scale = ADReal(1.0)) const;

  // Darcy flux options/materials
  const bool _multiply_by_fluid_density;

  const ADMaterialProperty<Real> & _rho_f;
  const ADMaterialProperty<RealTensorValue> & _mobility_tensor;
  const ADMaterialProperty<RealVectorValue> & _g;

  // SUPG options
  const bool _use_supg;
  const Real _supg_tau_user; // >=0 => constant tau, <0 => auto
  const Real _supg_alpha;    // scaling for auto tau
};