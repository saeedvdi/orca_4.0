#include "OrcaFullySaturatedSinglePhaseHeatVolumetricExpansionKernel.h"

#include "MooseError.h"
 
registerADMooseObject("OrcaApp", OrcaFullySaturatedSinglePhaseHeatVolumetricExpansionKernel);

InputParameters
OrcaFullySaturatedSinglePhaseHeatVolumetricExpansionKernel::validParams()
{
  InputParameters params = ADKernelValue::validParams();

  params.set<bool>("use_displaced_mesh") = false;
  params.suppressParameter<bool>("use_displaced_mesh");

  params.addClassDescription("Adds solid-energy * volumetric strain-rate term: "
                             "(1-phi)*rock_energy*eps_v_dot.");
  params.addParam<std::string>(
      "base_name",
      "Material property base name for mechanics properties such as vol_strain_rate.");
  return params;
}

OrcaFullySaturatedSinglePhaseHeatVolumetricExpansionKernel::OrcaFullySaturatedSinglePhaseHeatVolumetricExpansionKernel(
    const InputParameters & parameters)
  : ADKernelValue(parameters),
    _porosity(getADMaterialProperty<Real>("porosity_qp")),
    _rock_energy_density(getADMaterialProperty<Real>("rock_energy_density_qp")),
    _base_name(isParamValid("base_name") && !getParam<std::string>("base_name").empty()
                   ? getParam<std::string>("base_name") + "_"
                   : ""),
    _vol_strain_rate(getADMaterialProperty<Real>(_base_name + "vol_strain_rate")),

    // optional fluid terms
    _has_fluid_terms(hasADMaterialProperty<Real>("fluid_density_qp") &&
                     hasADMaterialProperty<Real>("fluid_internal_energy_qp")),
    _rho_f_qp(_has_fluid_terms ? &getADMaterialProperty<Real>("fluid_density_qp") : nullptr),
    _e_f_qp(_has_fluid_terms ? &getADMaterialProperty<Real>("fluid_internal_energy_qp") : nullptr)
{
   // Enforce pairing: rho and e must come together
  const bool has_rho = hasADMaterialProperty<Real>("fluid_density_qp");
  const bool has_e = hasADMaterialProperty<Real>("fluid_internal_energy_qp");
  if (has_rho != has_e)
    mooseError("OrcaFullySaturatedSinglePhaseHeatVolumetricExpansionKernel requires "
               "'fluid_density_qp' and 'fluid_internal_energy_qp' to be provided together.");
}

ADReal
OrcaFullySaturatedSinglePhaseHeatVolumetricExpansionKernel::precomputeQpResidual()
{
  ADReal energy = (1.0 - _porosity[_qp]) * _rock_energy_density[_qp];

  if (_has_fluid_terms)
  {
    const ADReal rho = (*_rho_f_qp)[_qp];
    const ADReal e = (*_e_f_qp)[_qp];

    energy += _porosity[_qp] * rho * e;
  }

  return energy * _vol_strain_rate[_qp];
}
