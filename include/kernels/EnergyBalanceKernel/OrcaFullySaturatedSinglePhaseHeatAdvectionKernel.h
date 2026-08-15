#pragma once

#include "OrcaFullySaturatedSinglePhaseDarcyKernel.h"

class OrcaFullySaturatedSinglePhaseHeatAdvectionKernel
  : public OrcaFullySaturatedSinglePhaseDarcyKernel
{
public:
  static InputParameters validParams();

  OrcaFullySaturatedSinglePhaseHeatAdvectionKernel(const InputParameters & parameters);

protected:
  virtual ADReal computeQpResidual() override;

  const ADVariableGradient & _grad_p;
  const ADMaterialProperty<Real> & _enthalpy;
};
