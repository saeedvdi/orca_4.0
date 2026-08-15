#pragma once

#include "ADTimeKernelValue.h"
#include "RankTwoTensor.h"

class OrcaFullySaturatedSinglePhaseEnergyTimeDerivativeKernel : public ADTimeKernelValue
{
public:
  static InputParameters validParams();

  OrcaFullySaturatedSinglePhaseEnergyTimeDerivativeKernel(const InputParameters & parameters);

protected:
  virtual ADReal precomputeQpResidual() override;

  const ADMaterialProperty<Real> & _porosity;
  const MaterialProperty<Real> & _porosity_old;

  const ADMaterialProperty<Real> & _rock_energy_density;
  const MaterialProperty<Real> & _rock_energy_density_old;

  const bool _has_fluid_terms;
  const ADMaterialProperty<Real> * _rho_f;
  const MaterialProperty<Real> * _rho_f_old;
  const ADMaterialProperty<Real> * _e_f;
  const MaterialProperty<Real> * _e_f_old;

  const bool _use_total_strain_old;
  const bool _debug_require_displacements;
  const std::string _base_name;
  const MaterialProperty<RankTwoTensor> * _total_strain_old;
};
