#pragma once

#include "ADInterfaceKernel.h"

class OrcaMechInterfaceKernel : public ADInterfaceKernel
{
public:
  static InputParameters validParams();
  OrcaMechInterfaceKernel(const InputParameters & parameters);

protected:
  ADReal computeQpResidual(Moose::DGResidualType type) override;

  const std::string _base_name;
  const unsigned int _component;
  const unsigned int _ndisp;
  const ADMaterialProperty<RealVectorValue> & _traction_global;
};