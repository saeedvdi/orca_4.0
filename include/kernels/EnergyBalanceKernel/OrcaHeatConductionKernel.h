#pragma once

#include "ADKernelGrad.h"

class OrcaHeatConductionKernel : public ADKernelGrad
{
public:
  static InputParameters validParams();

  OrcaHeatConductionKernel(const InputParameters & parameters);

protected:
  virtual ADRealVectorValue precomputeQpResidual() override;

  const ADMaterialProperty<RealTensorValue> & _thermal_conductivity;
};
