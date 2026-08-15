#include "OrcaFractureFlowInterfaceKernel.h"

registerMooseObject("OrcaApp", OrcaFractureFlowInterfaceKernel);

InputParameters
OrcaFractureFlowInterfaceKernel::validParams()
{
  InputParameters params = ADInterfaceKernel::validParams();

  params.addClassDescription(
      "In-plane Reynolds/cubic-law fracture flow equation applied at a CZM sideset, using the "
      "transmissivity and hydraulic aperture from OrcaCZMCubicLawAperture. The Element side "
      "carries the fracture's flow equation (transport + aperture-rate storage); the Neighbor "
      "side is tied to it by a pressure-continuity penalty.");

  params.addParam<std::string>("base_name", "Material property base name");
  params.addRangeCheckedParam<Real>(
      "pressure_penalty_length", 1.0e-4, "pressure_penalty_length > 0",
      "Length scale converting the fracture mobility into a pressure-continuity penalty "
      "conductance (m). Smaller enforces tighter continuity at the cost of conditioning.");
  params.addParam<bool>(
      "multiply_by_fluid_density", false,
      "If true, compute mass flux/storage (rho*...). If false (default), volumetric form, "
      "matching the convention used in the bulk Orca Darcy/storage kernels.");

  return params;
}

OrcaFractureFlowInterfaceKernel::OrcaFractureFlowInterfaceKernel(const InputParameters & parameters)
  : ADInterfaceKernel(parameters),
    _base_name(isParamValid("base_name") && !getParam<std::string>("base_name").empty()
                   ? getParam<std::string>("base_name") + "_"
                   : ""),
    _penalty_length(getParam<Real>("pressure_penalty_length")),
    _multiply_by_fluid_density(getParam<bool>("multiply_by_fluid_density")),
    _transmissivity(getADMaterialPropertyByName<Real>(_base_name + "fracture_transmissivity")),
    _aperture(getADMaterialPropertyByName<Real>(_base_name + "hydraulic_aperture")),
    _aperture_old(getMaterialPropertyOldByName<Real>(_base_name + "hydraulic_aperture")),
    _rho_f(_multiply_by_fluid_density ? &getADMaterialPropertyByName<Real>("fluid_density_qp")
                                       : nullptr)
{
}

ADReal
OrcaFractureFlowInterfaceKernel::computeQpResidual(Moose::DGResidualType type)
{
  const ADReal gamma = _rho_f ? (*_rho_f)[_qp] : ADReal(1.0);

  // Stiff penalty enforcing pressure continuity across the hydraulically-thin gap
  // (both faces bound the same fluid body).
  const ADReal kappa_p = gamma * _transmissivity[_qp] / (_aperture[_qp] * _penalty_length);
  const ADReal flux = kappa_p * (_u[_qp] - _neighbor_value[_qp]);

  ADReal r = 0.0;

  switch (type)
  {
    case Moose::Element:
    {
      // Storage from the time rate of the mechanical (dilation/closure-driven) aperture.
      const ADReal storage = gamma * (_aperture[_qp] - _aperture_old[_qp]) / _dt;

      // In-plane (tangential) Reynolds/cubic-law transport along the fracture.
      const ADRealVectorValue grad_p_t = tangentialGradient(_grad_u[_qp]);
      const ADRealVectorValue grad_test_t = tangentialGradient(_grad_test[_i][_qp]);
      const ADReal transport = gamma * _transmissivity[_qp] * (grad_p_t * grad_test_t);

      r = _test[_i][_qp] * (storage + flux) + transport;
      break;
    }
    case Moose::Neighbor:
      r = -_test_neighbor[_i][_qp] * flux;
      break;
  }

  return r;
}

ADRealVectorValue
OrcaFractureFlowInterfaceKernel::tangentialGradient(const ADRealVectorValue & grad) const
{
  const ADRealVectorValue normal = _normals[_qp];
  return grad - (grad * normal) * normal;
}
