#include "OrcaFullySaturatedSinglePhaseHeatAdvectionSUPGKernel.h"

#include "metaphysicl/raw_type.h"

#include "libmesh/elem.h"

#include <cmath>

registerMooseObject("OrcaApp", OrcaFullySaturatedSinglePhaseHeatAdvectionSUPGKernel);

InputParameters
OrcaFullySaturatedSinglePhaseHeatAdvectionSUPGKernel::validParams()
{
  InputParameters params = OrcaFullySaturatedSinglePhaseDarcyKernel::validParams();

  params.addClassDescription(
      "Heat/energy advection for fully saturated single-phase Darcy flow. "
      "Adds ∫ grad(test) · (q*h) dΩ to the temperature/energy equation, "
      "where q = -gamma*K*(grad(p) - rho*g). Optional SUPG stabilization.");

  params.addRequiredCoupledVar(
      "pore_pressure",
      "Pressure variable p used to compute Darcy flux direction/magnitude.");

  // SUPG controls
  params.addParam<bool>(
      "use_supg",
      true,
      "If true, add a streamline-upwind/Petrov-Galerkin (SUPG) stabilization term.");

  params.addParam<Real>(
      "supg_tau",
      -1.0,
      "SUPG tau. If >= 0, uses this constant value. If < 0, tau is computed automatically.");

  params.addParam<Real>(
      "supg_alpha",
      1.0,
      "Scaling factor for automatically computed tau (only used if supg_tau < 0).");

  params.addParam<bool>(
      "supg_use_dh_dT",
      false,
      "If true, multiply the SUPG strong advection term by dh/dT (requires a material property).");

  params.addParam<MaterialPropertyName>(
      "dh_dT_property",
      "fluid_enthalpy_dT_qp",
      "Material property name for dh/dT at QPs (only used if supg_use_dh_dT=true).");

  return params;
}

OrcaFullySaturatedSinglePhaseHeatAdvectionSUPGKernel::OrcaFullySaturatedSinglePhaseHeatAdvectionSUPGKernel(
    const InputParameters & parameters)
  : OrcaFullySaturatedSinglePhaseDarcyKernel(parameters),
    _grad_p(adCoupledGradient("pore_pressure")),
    _enthalpy(getADMaterialProperty<Real>("fluid_enthalpy_qp")),
    _use_supg(getParam<bool>("use_supg")),
    _supg_tau_user(getParam<Real>("supg_tau")),
    _supg_alpha(getParam<Real>("supg_alpha")),
    _supg_use_dh_dT(getParam<bool>("supg_use_dh_dT")),
    _dh_dT(nullptr)
{
  // Only fetch dh/dT if user explicitly wants it
  if (_supg_use_dh_dT)
    _dh_dT = &getADMaterialProperty<Real>(getParam<MaterialPropertyName>("dh_dT_property"));
}

Real
OrcaFullySaturatedSinglePhaseHeatAdvectionSUPGKernel::computeSUPGTau(const ADRealVectorValue & q) const
{
  // User-specified constant tau
  if (_supg_tau_user >= 0.0)
    return _supg_tau_user;

  // Auto tau ~ alpha * h / (2 |q|)
  // Use raw values so tau doesn't add extra nonlinear couplings
  const Real h = _current_elem ? _current_elem->hmin() : 0.0;

  Real qnorm_sq = 0.0;
  for (unsigned d = 0; d < LIBMESH_DIM; ++d)
  {
    const Real qd = MetaPhysicL::raw_value(q(d));
    qnorm_sq += qd * qd;
  }

  const Real qnorm = std::sqrt(qnorm_sq);
  const Real eps = 1e-14;

  if (qnorm < eps || h <= 0.0)
    return 0.0;

  return _supg_alpha * h / (2.0 * qnorm + eps);
}

ADReal
OrcaFullySaturatedSinglePhaseHeatAdvectionSUPGKernel::computeQpResidual()
{
  // Darcy flux from coupled pressure gradient (NOT from _grad_u, which is grad(T) here)
  const ADRealVectorValue q = computeDarcyFluxFromGradP(_grad_p[_qp]);

  // Galerkin advection contribution (conservative/divergence form weak term)
  const ADRealVectorValue energy_flux = q * _enthalpy[_qp];
  ADReal R = _grad_test[_i][_qp] * energy_flux;

  // Optional SUPG stabilization:
  // Add tau (q · grad(test)) (q · grad(T)) [* dh/dT if requested]
  if (_use_supg)
  {
    const Real tau = computeSUPGTau(q);

    if (tau > 0.0)
    {
      ADReal scale = 1.0;
      if (_supg_use_dh_dT && _dh_dT)
        scale = (*_dh_dT)[_qp];

      const ADReal q_dot_grad_test = q * _grad_test[_i][_qp];
      const ADReal q_dot_grad_T    = q * _grad_u[_qp]; // _u is the variable of this kernel (T)

      R += tau * q_dot_grad_test * q_dot_grad_T * scale;
    }
  }

  return R;
}
