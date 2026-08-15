#pragma once

#include "ADTimeKernelValue.h"

/**
 * Fully-saturated single-phase storage term:
 *
 *   storage_rate = (1/M) * dp/dt  -  alpha_T * dT/dt  +  alpha * eps_v_dot
 *
 * Optionally multiplies by fluid density to get a mass form:
 *
 *   rho * storage_rate
 *
 * This is an element/time kernel assembled at quadrature points.
 */
class OrcaFullySaturatedSinglePhaseMassTimeDerivativeKernel : public ADTimeKernelValue
{
public:
  static InputParameters validParams();

  OrcaFullySaturatedSinglePhaseMassTimeDerivativeKernel(const InputParameters & parameters);

protected:
  enum class CouplingTypeEnum
  {
    Hydro,
    ThermoHydro,
    HydroMechanical,
    ThermoHydroMechanical
  };

  virtual ADReal precomputeQpResidual() override;

  const CouplingTypeEnum _coupling_type;
  const bool _includes_thermal;
  const bool _includes_mechanical;
  const bool _multiply_by_fluid_density;

  // Quadrature-point material properties
  const ADMaterialProperty<Real> & _biot_modulus;
  const MaterialProperty<Real> * _biot_modulus_available;
  const ADMaterialProperty<Real> & _biot;

  const ADMaterialProperty<Real> * _alpha_eff_T;   // thermal expansion coefficient (optional)
  const ADMaterialProperty<Real> * _epsv_dot;  // volumetric strain rate (optional)
  const ADMaterialProperty<Real> * _rho;       // fluid density (optional)

  // Coupled variable time derivative (optional)
  const ADVariableValue * _T_dot;

  // diagnostics (optional to output later)
  ADReal _storage_rate_p;
  ADReal _storage_rate_thermal;
  ADReal _storage_rate_mech;
};
