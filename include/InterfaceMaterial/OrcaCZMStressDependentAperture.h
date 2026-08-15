#pragma once

#include "InterfaceMaterial.h"

/**
 * Hydraulic aperture model for hydroshearing examples.
 *
 * The aperture is computed from a reference aperture, an elastic normal-stress
 * opening/closure term, and the accumulated shear-induced dilation from
 * OrcaCZMMohrCoulombFriction:
 *
 *   a_h = a_ref + C_n * (N_ref - N_eff) + c_d * d_shear
 *
 * where N_eff is compression-positive effective normal stress inferred from the
 * interface effective normal traction (tension positive in the CZM convention).
 */
class OrcaCZMStressDependentAperture : public InterfaceMaterial
{
public:
  static InputParameters validParams();
  OrcaCZMStressDependentAperture(const InputParameters & parameters);

protected:
  void initQpStatefulProperties() override;
  void computeQpProperties() override;

  const std::string _base_name;

  /// Reference aperture at the reference effective normal stress (m)
  const Real _reference_aperture;

  /// Reference compression-positive effective normal stress (Pa)
  const Real _reference_effective_normal_stress;

  /// Aperture compliance with respect to effective normal stress (m/Pa)
  const Real _normal_compliance;

  /// Fraction of accumulated mechanical dilation contributing to hydraulic aperture (-)
  const Real _dilation_aperture_coefficient;

  /// Aperture lower/upper bounds (m)
  const Real _minimum_aperture;
  const Real _maximum_aperture;

  /// Effective/contact normal traction, tension positive (Pa)
  const ADMaterialProperty<Real> & _effective_normal_traction;

  /// Accumulated shear-induced normal dilation (m)
  const ADMaterialProperty<Real> & _dilation;

  /// Fluid viscosity (Pa.s)
  const ADMaterialProperty<Real> & _mu_f;

  ADMaterialProperty<Real> & _aperture;
  ADMaterialProperty<Real> & _permeability;
  ADMaterialProperty<Real> & _transmissivity;
};
