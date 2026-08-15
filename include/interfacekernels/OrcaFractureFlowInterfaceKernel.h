#pragma once

#include "ADInterfaceKernel.h"

/**
 * Adds the fracture's own (in-plane) Reynolds/cubic-law flow equation to the
 * pore_pressure system at a CZM sideset, using the transmissivity and
 * hydraulic aperture computed by OrcaCZMCubicLawAperture.
 *
 * By convention, the "Element" side of the sideset carries the fracture flow
 * equation (in-plane transport + storage from the time rate of the hydraulic
 * aperture); the "Neighbor" side is tied to it through a stiff penalty that
 * enforces pressure continuity across the (hydraulically thin) gap. Orient
 * the CZM sideset / mesh generation consistently so the same block is always
 * the "Element" side.
 *
 * See the accompanying documentation for the governing equation, sign
 * conventions and the dimensional analysis behind the penalty term.
 */
class OrcaFractureFlowInterfaceKernel : public ADInterfaceKernel
{
public:
  static InputParameters validParams();
  OrcaFractureFlowInterfaceKernel(const InputParameters & parameters);

protected:
  ADReal computeQpResidual(Moose::DGResidualType type) override;

  /// Base name of the material system
  const std::string _base_name;

  /// Length scale used to convert the fracture's own mobility into a pressure-continuity
  /// penalty conductance (m). Smaller values enforce tighter continuity.
  const Real _penalty_length;

  /// If true, work in mass form (multiply by fluid density); otherwise volumetric form.
  const bool _multiply_by_fluid_density;

  /// Fracture transmissivity, a_h^3/(12*mu_f) (m^3/(Pa.s))
  const ADMaterialProperty<Real> & _transmissivity;

  /// Hydraulic aperture, current and old (m)
  const ADMaterialProperty<Real> & _aperture;
  const MaterialProperty<Real> & _aperture_old;

  /// Optional fluid density (mass form only)
  const ADMaterialProperty<Real> * const _rho_f;

  /// Project a bulk gradient onto the tangent plane of the interface
  ADRealVectorValue tangentialGradient(const ADRealVectorValue & grad) const;
};
