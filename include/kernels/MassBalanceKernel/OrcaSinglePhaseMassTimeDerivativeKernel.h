#pragma once

#pragma once

#include "ADTimeKernel.h"
#include "RankTwoTensor.h"

/**
 * Time derivative of pore fluid volume or mass (single phase).
 *
 * Residual (per qp):
 *   R = test * (1 + tr(eps_old)) * (phi * rho - phi_old * rho_old) / dt
 *
 * If multiply_by_fluid_density = false, rho terms are set to 1.0 to give volumetric form.
 * Optionally includes volumetric strain from a mechanics material (base_name + "total_strain").
 */
class OrcaSinglePhaseMassTimeDerivativeKernel : public ADTimeKernel
{
public:
  static InputParameters validParams();

  OrcaSinglePhaseMassTimeDerivativeKernel(const InputParameters & parameters);

protected:
  virtual ADReal computeQpResidual() override;

  const bool _multiply_by_fluid_density;
  const std::string _base_name;

  const bool _has_total_strain;
  const MaterialProperty<RankTwoTensor> * _total_strain_old;

  const ADMaterialProperty<Real> & _porosity;
  const MaterialProperty<Real> & _porosity_old;

  const ADMaterialProperty<Real> * _fluid_density;
  const MaterialProperty<Real> * _fluid_density_old;
};