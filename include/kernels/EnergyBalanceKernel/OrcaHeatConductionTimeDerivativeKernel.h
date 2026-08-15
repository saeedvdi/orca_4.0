#pragma once

#include "ADTimeKernelValue.h"

class OrcaHeatConductionTimeDerivativeKernel : public ADTimeKernelValue
{
public:
  static InputParameters validParams();

  OrcaHeatConductionTimeDerivativeKernel(const InputParameters & parameters);

protected:
  virtual ADReal precomputeQpResidual() override;

  const ADMaterialProperty<Real> & _cp_s;
  const ADMaterialProperty<Real> & _rho_s;
};
