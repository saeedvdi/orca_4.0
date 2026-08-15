#pragma once

#include "ADKernelValue.h"

class OrcaFullySaturatedSinglePhaseHeatVolumetricExpansionKernel : public ADKernelValue
{
public:
  static InputParameters validParams();

  OrcaFullySaturatedSinglePhaseHeatVolumetricExpansionKernel(const InputParameters & parameters);

protected:
  virtual ADReal precomputeQpResidual() override;

  const ADMaterialProperty<Real> & _porosity;
  const ADMaterialProperty<Real> & _rock_energy_density;
  const std::string _base_name;
  const ADMaterialProperty<Real> & _vol_strain_rate;

  const bool _has_fluid_terms;
  const ADMaterialProperty<Real> * _rho_f_qp;
  const ADMaterialProperty<Real> * _e_f_qp;
};
