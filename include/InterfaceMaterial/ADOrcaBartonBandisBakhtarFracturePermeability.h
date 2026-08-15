#pragma once

#include "InterfaceMaterial.h"

/**
 * ADOrcaBartonBandisBakhtarFracturePermeability
 *
 * Literal Barton-Bandis-Bakhtar (1985) mechanical-to-hydraulic aperture reduction:
 *
 *     e_h [um] = E_m [um]^2 / JRC^2.5
 *
 * (Barton, Bandis & Bakhtar, "Strength, deformation and conductivity coupling of rock
 * joints", Int. J. Rock Mech. Min. Sci. & Geomech. Abstr., 22(3), 121-140, 1985; also Barton
 * 1982). E_m is the mechanical aperture and e_h the hydraulic aperture, both in micrometers;
 * JRC is the (dimensionless) joint roughness coefficient. The correlation is empirical and
 * dimensionally inhomogeneous, so it is only valid with both apertures expressed in
 * micrometers -- this class converts to/from the project's SI (meter) convention internally.
 *
 * This is a deliberately different, narrower model from ADOrcaRoughnessDamageFracturePermeability:
 * that class builds a_h from an additive combination of mechanical aperture, cumulative
 * dilation, and roughness-retention terms (a legitimate but distinct construction, NOT this
 * formula). This class exists to let a deck opt into the literal published power law instead,
 * for direct comparison / for stating in the manuscript that the literal form was tested.
 *
 * JRC can be a fixed constant or, when use_mobilized_jrc = true, coupled to the mobilized JRC
 * already exported by the Barton-Bandis contact traction material (e.g. "bb_jrc_mobilized" on
 * ADOrcaBartonBandisContactTractionFastAD/Hardening), so the hydraulic reduction tracks the
 * same stress-mobilized roughness degradation used in the mechanical response.
 *
 * The mechanical aperture is floored by an optional mechanical_aperture_offset (default 0)
 * before the power law is applied. This is NOT part of the literal 1985 formula -- it exists
 * purely so a fully closed joint (E_m = 0) does not force e_h identically to 0, which would be
 * numerically singular for the flow coupling. Set it to 0 to use the pure literal formula.
 */
class ADOrcaBartonBandisBakhtarFracturePermeability : public InterfaceMaterial
{
public:
  static InputParameters validParams();

  ADOrcaBartonBandisBakhtarFracturePermeability(const InputParameters & parameters);

protected:
  virtual void initQpStatefulProperties() override;
  virtual void computeQpProperties() override;

  const std::string _base_name;

  // --- inputs ---
  const ADMaterialProperty<Real> & _mechanical_aperture;
  const bool _use_mobilized_jrc;
  const MaterialProperty<Real> * const _jrc_mobilized; // non-AD: matches how the BB contact
                                                         // material exports it
  // Optional pass-through diagnostic, independent of the aperture law itself -- kept here purely
  // so decks swapping in this material don't lose the sigma'_n validation panel the additive
  // model also exported this way.
  const ADMaterialProperty<Real> * const _effective_normal_traction;

  // --- outputs ---
  ADMaterialProperty<Real> & _hydraulic_aperture;
  ADMaterialProperty<Real> & _fracture_permeability;
  ADMaterialProperty<Real> * _transmissivity;
  ADMaterialProperty<Real> & _jrc_used; // diagnostic: the JRC value actually applied this step
  ADMaterialProperty<Real> * _effective_normal_compression; // diagnostic: compression-positive (Pa)

  // --- parameters ---
  const Real _jrc_const;              // constant JRC when use_mobilized_jrc = false
  const Real _jrc_min;                // floor to avoid JRC^2.5 -> 0 blow-up
  const Real _mechanical_aperture_offset; // residual/mismatch aperture added before the power
                                           // law (m); NOT part of the literal formula, see class doc
  const Real _min_aperture;
  const Real _max_aperture; // upper bound on hydraulic aperture (m); 0 disables
  const bool _compute_transmissivity;
  const Real _fluid_viscosity;
};
