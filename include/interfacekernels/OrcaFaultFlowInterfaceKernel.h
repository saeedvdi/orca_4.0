#pragma once

#include "ADInterfaceKernel.h"

/**
 * Mass-conservative cross-gap pressure-transfer interface kernel for split faults.
 * Residual uses flux q = T * (p_primary - p_secondary), applied with opposite signs on the two
 * faces. Transmissibility T may be constant, computed from a mechanical aperture (cubic law), or
 * read from a fracture-permeability material property (the Ye & Ghassemi 2018 path:
 * T = k / (mu * fault_thickness)).
 *
 * Ported verbatim (registration renamed orcaApp -> OrcaApp) from Orca_2.0.
 */
class OrcaFaultFlowInterfaceKernel : public ADInterfaceKernel
{
public:
  static InputParameters validParams();
  OrcaFaultFlowInterfaceKernel(const InputParameters & parameters);

protected:
  ADReal computeQpResidual(Moose::DGResidualType type) override;

  ADReal computeTransmissibility() const;
  ADReal computeFluidViscosity() const;
  ADReal computeFluidDensity() const;

  const MooseEnum _model;

  const bool _use_transmissibility_property;
  const std::string _transmissibility_property_name;
  const Real _transmissibility;
  const Real _min_transmissibility;
  const ADMaterialProperty<Real> * _transmissibility_prop;

  const std::string _aperture_property_name;
  const Real _initial_aperture;
  const Real _min_aperture;
  const Real _aperture_scale;
  const Real _fault_thickness;
  const bool _clamp_aperture_to_opening;
  const ADMaterialProperty<Real> * _mechanical_aperture;

  // permeability_property model
  const std::string _permeability_property_name;
  const ADMaterialProperty<Real> * _fracture_permeability_prop;

  const bool _use_material_viscosity;
  const std::string _fluid_viscosity_name;
  const Real _fluid_viscosity;
  const ADMaterialProperty<Real> * _fluid_viscosity_prop;

  const bool _multiply_by_fluid_density;
  const bool _use_material_density;
  const std::string _fluid_density_name;
  const Real _fluid_density;
  const ADMaterialProperty<Real> * _fluid_density_prop;
};
