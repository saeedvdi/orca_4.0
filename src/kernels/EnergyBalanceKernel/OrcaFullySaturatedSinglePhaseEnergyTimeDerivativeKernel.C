#include "OrcaFullySaturatedSinglePhaseEnergyTimeDerivativeKernel.h"

#include "MooseError.h"

registerMooseObject("OrcaApp", OrcaFullySaturatedSinglePhaseEnergyTimeDerivativeKernel);

InputParameters
OrcaFullySaturatedSinglePhaseEnergyTimeDerivativeKernel::validParams()
{
  InputParameters params = ADTimeKernelValue::validParams();

  params.addClassDescription(
    " this kernel computes the "
      "time derivative of heat energy density for fully-saturated single-phase."
      "Energy density is computed from material properties:"
      "E = (1-phi)*rock_energy + phi*rho*e (fluid part optional)."
      "Optionally multiplies by (1 + tr(total_strain_old)) using QP total_strain (old).");

  params.addParam<bool>(
      "use_total_strain_old",
      false,
      "If true, multiply by (1 + tr(total_strain_old)) using the old QP total_strain property.");

  params.addParam<bool>(
      "debug_require_displacements",
      false,
      "If true and use_total_strain_old=true, error out unless displacement variables are coupled.");

  params.addParam<std::string>(
      "base_name",
      "Material property base name for mechanics properties such as total_strain.");

  // Optional guard-only coupling (not used directly in residual)
  params.addCoupledVar("displacements",
                       "Displacement variables (required only when debug_require_displacements=true "
                       "and use_total_strain_old=true).");

  return params;
}

OrcaFullySaturatedSinglePhaseEnergyTimeDerivativeKernel::OrcaFullySaturatedSinglePhaseEnergyTimeDerivativeKernel(
    const InputParameters & parameters)
  : ADTimeKernelValue(parameters),
    _porosity(getADMaterialProperty<Real>("porosity_qp")),
    _porosity_old(getMaterialPropertyOld<Real>("porosity_qp")),

    _rock_energy_density(getADMaterialProperty<Real>("rock_energy_density_qp")),
    _rock_energy_density_old(getMaterialPropertyOld<Real>("rock_energy_density_qp")),

    // optional fluid terms: only if BOTH exist
    _has_fluid_terms(hasADMaterialProperty<Real>("fluid_density_qp") &&
                     hasADMaterialProperty<Real>("fluid_internal_energy_qp")),
    _rho_f(_has_fluid_terms ? &getADMaterialProperty<Real>("fluid_density_qp") : nullptr),
    _rho_f_old(_has_fluid_terms ? &getMaterialPropertyOld<Real>("fluid_density_qp")
                                      : nullptr),
    _e_f(_has_fluid_terms ? &getADMaterialProperty<Real>("fluid_internal_energy_qp")
                                : nullptr),
    _e_f_old(_has_fluid_terms ? &getMaterialPropertyOld<Real>("fluid_internal_energy_qp")
                                    : nullptr),

    // optional mechanics scaling
    _use_total_strain_old(getParam<bool>("use_total_strain_old")),
    _debug_require_displacements(getParam<bool>("debug_require_displacements")),
    _base_name(isParamValid("base_name") && !getParam<std::string>("base_name").empty()
                   ? getParam<std::string>("base_name") + "_"
                   : ""),
    _total_strain_old(nullptr)
{
  // Enforce pairing: rho and e must come together
  const bool has_rho = hasADMaterialProperty<Real>("fluid_density_qp");
  const bool has_e = hasADMaterialProperty<Real>("fluid_internal_energy_qp");
  if (has_rho != has_e)
    mooseError("OrcaFullySaturatedSinglePhaseEnergyTimeDerivativeKernel requires "
               "'fluid_density_qp' and 'fluid_internal_energy_qp' to be provided together.");

  if (_use_total_strain_old)
  {
    // This will throw a clear error if mechanics/strain property isn't provided
    if (!hasADMaterialProperty<RankTwoTensor>(_base_name + "total_strain"))
      paramError("use_total_strain_old",
                 "use_total_strain_old=true but no AD material property '" + _base_name +
                     "total_strain' exists.");

    _total_strain_old = &getMaterialPropertyOld<RankTwoTensor>(_base_name + "total_strain");

    // Optional extra guard for user-friendliness
    if (_debug_require_displacements)
    {
      if (!isCoupled("displacements"))
        paramError("displacements",
                   "use_total_strain_old=true requires displacement variables. "
                   "Enable mechanics (add displacements / TensorMechanics action) or set "
                   "debug_require_displacements=false.");

      if (coupledComponents("displacements") == 0)
        paramError("displacements", "No displacement components were provided.");
    }
  }
}

ADReal
OrcaFullySaturatedSinglePhaseEnergyTimeDerivativeKernel::precomputeQpResidual()
{
  // Solid energy density:
  //   E_s = (1 - phi) * rock_energy   where rock_energy = rho_s * cp_s * T (provided by material)
  ADReal energy = (1.0 - _porosity[_qp]) * _rock_energy_density[_qp];
  ADReal energy_old = (1.0 - _porosity_old[_qp]) * _rock_energy_density_old[_qp];

  // Optional fluid energy density:
  //   E_f = phi * rho * e
  if (_has_fluid_terms)
  {
    const ADReal rho = (*_rho_f)[_qp];
    const ADReal e = (*_e_f)[_qp];

    const Real rho_old = (*_rho_f_old)[_qp];
    const Real e_old = (*_e_f_old)[_qp];

    energy += _porosity[_qp] * rho * e;
    energy_old += _porosity_old[_qp] * rho_old * e_old;
  }

  // Optional strain scaling factor: (1 + tr(total_strain_old))
  ADReal factor = 1.0;
  if (_use_total_strain_old)
    factor += ADReal((*_total_strain_old)[_qp].trace());

  return factor * (energy - energy_old) / _dt;
}
