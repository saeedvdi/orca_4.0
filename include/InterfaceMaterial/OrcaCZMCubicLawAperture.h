#pragma once

#include "InterfaceMaterial.h"

/**
 * Computes the hydraulic aperture, fracture permeability (cubic law) and
 * fracture transmissivity of a CZM sideset from the mechanical normal
 * displacement jump produced by OrcaCZMComputeDisplacementJump.
 *
 * a_h = a_r * exp(jump_n / a_r)
 * k_f = a_h^2 / 12
 * T_f = a_h^3 / (12 * mu_f)
 *
 * See the accompanying documentation for the rationale behind the smooth
 * exponential closure law.
 */
class OrcaCZMCubicLawAperture : public InterfaceMaterial
{
public:
  static InputParameters validParams();
  OrcaCZMCubicLawAperture(const InputParameters & parameters);

protected:
  void initQpStatefulProperties() override;
  void computeQpProperties() override;

  /// Base name of the material system
  const std::string _base_name;

  /// Residual / reference hydraulic aperture at zero mechanical opening (m)
  const Real _a_r;

  /// Mechanical normal displacement jump (tension positive), from OrcaCZMComputeDisplacementJump
  const ADMaterialProperty<RealVectorValue> & _jump;

  /// Fluid viscosity, read from the bulk THMaterial (Pa.s)
  const ADMaterialProperty<Real> & _mu_f;

  /// Output: hydraulic aperture (m)
  ADMaterialProperty<Real> & _aperture;

  /// Output: fracture permeability, a_h^2/12 (m^2)
  ADMaterialProperty<Real> & _permeability;

  /// Output: fracture transmissivity, a_h^3/(12*mu_f) (m^3/(Pa.s))
  ADMaterialProperty<Real> & _transmissivity;
};
