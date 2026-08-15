#include "OrcaFullySaturatedSinglePhaseHeatAdvectionKernel.h"

registerMooseObject("OrcaApp", OrcaFullySaturatedSinglePhaseHeatAdvectionKernel);

InputParameters
OrcaFullySaturatedSinglePhaseHeatAdvectionKernel::validParams()
{
    InputParameters params = OrcaFullySaturatedSinglePhaseDarcyKernel::validParams();

    params.addClassDescription(
        "Heat/energy advection for fully saturated single-phase Darcy flow. "
        "Adds ∫ grad(test) · (q*e) dΩ to the temperature/energy equation, "
        "where q = -gamma*K*(grad(p) - rho*g). No upwinding.");

    params.addRequiredCoupledVar(
        "pore_pressure",
        "Pressure variable used to compute Darcy flux direction/magnitude.");

    // IMPORTANT: do NOT re-add multiply_by_fluid_density here; it already exists in the base.

    return params;
}

OrcaFullySaturatedSinglePhaseHeatAdvectionKernel::OrcaFullySaturatedSinglePhaseHeatAdvectionKernel(const InputParameters & parameters)
    : OrcaFullySaturatedSinglePhaseDarcyKernel(parameters),
        _grad_p(adCoupledGradient("pore_pressure")),
        _enthalpy(getADMaterialProperty<Real>("fluid_enthalpy_qp"))
{
}

ADReal
OrcaFullySaturatedSinglePhaseHeatAdvectionKernel::computeQpResidual()
{
    // Darcy flux from coupled pressure gradient (NOT from _grad_u, which is grad(T) here)
    const ADRealVectorValue q = computeDarcyFluxFromGradP(_grad_p[_qp]);

    // advected energy flux
    const ADRealVectorValue energy_flux = q * _enthalpy[_qp];

    // divergence form weak contribution
    return _grad_test[_i][_qp] * energy_flux;
}
