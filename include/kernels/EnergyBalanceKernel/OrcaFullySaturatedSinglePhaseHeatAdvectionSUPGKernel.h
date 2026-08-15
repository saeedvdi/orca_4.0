#pragma once

#include "OrcaFullySaturatedSinglePhaseDarcyKernel.h"

class OrcaFullySaturatedSinglePhaseHeatAdvectionSUPGKernel
  : public OrcaFullySaturatedSinglePhaseDarcyKernel
{
public:
  static InputParameters validParams();

  OrcaFullySaturatedSinglePhaseHeatAdvectionSUPGKernel(const InputParameters & parameters);

protected:
  virtual ADReal computeQpResidual() override;

  Real computeSUPGTau(const ADRealVectorValue & q) const;

  const ADVariableGradient & _grad_p;
  const ADMaterialProperty<Real> & _enthalpy;

  const bool _use_supg;
  const Real _supg_tau_user;
  const Real _supg_alpha;
  const bool _supg_use_dh_dT;
  const ADMaterialProperty<Real> * _dh_dT;
};
