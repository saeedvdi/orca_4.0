#include "OrcaCZMCubicLawAperture.h"

registerMooseObject("OrcaApp", OrcaCZMCubicLawAperture);

InputParameters
OrcaCZMCubicLawAperture::validParams()
{
  InputParameters params = InterfaceMaterial::validParams();
  params.addClassDescription(
      "Computes the hydraulic aperture (smooth exponential closure law), cubic-law fracture "
      "permeability and fracture transmissivity from the CZM mechanical normal displacement "
      "jump.");

  params.addParam<std::string>("base_name", "Material property base name");
  params.addRequiredRangeCheckedParam<Real>(
      "residual_aperture", "residual_aperture > 0",
      "Hydraulic aperture at zero mechanical opening / reference closed state (m). Calibrate "
      "against the pre-shear flow-rate-derived aperture of the real fracture.");

  return params;
}

OrcaCZMCubicLawAperture::OrcaCZMCubicLawAperture(const InputParameters & parameters)
  : InterfaceMaterial(parameters),
    _base_name(isParamValid("base_name") && !getParam<std::string>("base_name").empty()
                   ? getParam<std::string>("base_name") + "_"
                   : ""),
    _a_r(getParam<Real>("residual_aperture")),
    _jump(getADMaterialPropertyByName<RealVectorValue>(_base_name + "interface_displacement_jump")),
    _mu_f(getADMaterialPropertyByName<Real>("fluid_viscosity_qp")),
    _aperture(declareADPropertyByName<Real>(_base_name + "hydraulic_aperture")),
    _permeability(declareADPropertyByName<Real>(_base_name + "fracture_permeability")),
    _transmissivity(declareADPropertyByName<Real>(_base_name + "fracture_transmissivity"))
{
}

void
OrcaCZMCubicLawAperture::initQpStatefulProperties()
{
  _aperture[_qp] = _a_r;
  _permeability[_qp] = _a_r * _a_r / 12.0;
  _transmissivity[_qp] = 0.0;
}

void
OrcaCZMCubicLawAperture::computeQpProperties()
{
  const ADReal jump_n = _jump[_qp](0);

  // Smooth, always-positive closure law: a_h = a_r at jump_n = 0, grows for opening
  // (jump_n > 0, e.g. dilation), decays smoothly toward (but never reaches) zero under
  // continued compaction (jump_n << 0).
  _aperture[_qp] = _a_r * exp(jump_n / _a_r);

  _permeability[_qp] = _aperture[_qp] * _aperture[_qp] / 12.0;
  _transmissivity[_qp] = _aperture[_qp] * _aperture[_qp] * _aperture[_qp] / (12.0 * _mu_f[_qp]);
}
