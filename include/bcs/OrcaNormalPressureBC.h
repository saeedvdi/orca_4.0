#pragma once

#include "IntegratedBC.h"

class Function;

/**
 * OrcaNormalPressureBC applies a pressure on a given boundary in a given direction.
 */
class OrcaNormalPressureBC : public IntegratedBC
{
public:
  static InputParameters validParams();

  OrcaNormalPressureBC(const InputParameters & parameters);

protected:
  Real computeQpResidual() override;

  /// The component of the pressure to apply (0, 1, or 2)
  const unsigned int _component;

  /// Constant value of the pressure applied
  const Real _value;

  /// Optional function describing the pressure
  const Function * const _function;
};
