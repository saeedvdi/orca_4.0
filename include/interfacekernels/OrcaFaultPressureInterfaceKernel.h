#pragma once

#include "ADInterfaceKernel.h"

/**
 * Applies fracture fluid pressure as a traction term on a split interface:
 *   t = traction_sign * alpha_eff * p_f * n
 * where n is the interface normal on the current side.
 *
 * The same traction magnitude is applied with opposite signs to element and
 * neighbor residuals through ADInterfaceKernel DG residual handling.
 *
 * Ported verbatim (registration renamed orcaApp -> OrcaApp) from Orca_2.0. This is the
 * MECHANICAL effective-stress fault-pressure route used by the Ye & Ghassemi (2018) DD02
 * reference deck: it couples the pore_pressure VARIABLE directly (optionally averaged across
 * the two faces) and applies it as a normal opening traction, distinct from the orca_3.0
 * OrcaCZMFluidPressureInterfaceKernel which uses a rotated material property instead.
 */
class OrcaFaultPressureInterfaceKernel : public ADInterfaceKernel
{
public:
  static InputParameters validParams();
  OrcaFaultPressureInterfaceKernel(const InputParameters & parameters);

protected:
  virtual ADReal computeQpResidual(Moose::DGResidualType type) override;

  const unsigned int _component;
  const ADVariableValue & _fluid_pressure;
  const ADVariableValue & _fluid_pressure_neighbor;
  const Real _effective_stress_coefficient;
  const Real _traction_sign;
  const bool _use_average_pressure;
};
