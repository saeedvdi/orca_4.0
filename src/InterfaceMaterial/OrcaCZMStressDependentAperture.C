#include "OrcaCZMStressDependentAperture.h"
#include "metaphysicl/raw_type.h"

registerMooseObject("OrcaApp", OrcaCZMStressDependentAperture);

InputParameters
OrcaCZMStressDependentAperture::validParams()
{
  InputParameters params = InterfaceMaterial::validParams();
  params.addClassDescription(
      "Stress- and dilation-dependent hydraulic aperture for CZM hydroshearing. Aperture is "
      "a_ref + C_n*(N_ref - N_eff) + c_d*dilation, bounded by min/max apertures, then cubic-law "
      "permeability/transmissivity are computed.");

  params.addParam<std::string>("base_name", "Material property base name");
  params.addRequiredRangeCheckedParam<Real>(
      "reference_aperture", "reference_aperture > 0", "Reference hydraulic aperture (m).");
  params.addRequiredRangeCheckedParam<Real>(
      "reference_effective_normal_stress",
      "reference_effective_normal_stress >= 0",
      "Reference compression-positive effective normal stress (Pa).");
  params.addRangeCheckedParam<Real>(
      "normal_compliance",
      0.0,
      "normal_compliance >= 0",
      "Hydraulic aperture compliance with effective normal stress (m/Pa).");
  params.addRangeCheckedParam<Real>(
      "dilation_aperture_coefficient",
      0.0,
      "dilation_aperture_coefficient >= 0",
      "Fraction of accumulated mechanical dilation that contributes to hydraulic aperture.");
  params.addRangeCheckedParam<Real>(
      "minimum_aperture", 1.0e-9, "minimum_aperture > 0", "Minimum hydraulic aperture (m).");
  params.addRangeCheckedParam<Real>(
      "maximum_aperture", 1.0e-3, "maximum_aperture > 0", "Maximum hydraulic aperture (m).");
  params.addParam<std::string>(
      "effective_normal_traction_property_name",
      "interface_effective_normal_traction",
      "Name of the tension-positive effective/contact normal traction property.");
  params.addParam<std::string>(
      "dilation_property_name",
      "interface_dilation",
      "Name of the accumulated shear-induced dilation property.");

  return params;
}

OrcaCZMStressDependentAperture::OrcaCZMStressDependentAperture(
    const InputParameters & parameters)
  : InterfaceMaterial(parameters),
    _base_name(isParamValid("base_name") && !getParam<std::string>("base_name").empty()
                   ? getParam<std::string>("base_name") + "_"
                   : ""),
    _reference_aperture(getParam<Real>("reference_aperture")),
    _reference_effective_normal_stress(getParam<Real>("reference_effective_normal_stress")),
    _normal_compliance(getParam<Real>("normal_compliance")),
    _dilation_aperture_coefficient(getParam<Real>("dilation_aperture_coefficient")),
    _minimum_aperture(getParam<Real>("minimum_aperture")),
    _maximum_aperture(getParam<Real>("maximum_aperture")),
    _effective_normal_traction(getADMaterialPropertyByName<Real>(
        _base_name + getParam<std::string>("effective_normal_traction_property_name"))),
    _dilation(
        getADMaterialPropertyByName<Real>(_base_name + getParam<std::string>("dilation_property_name"))),
    _mu_f(getADMaterialPropertyByName<Real>("fluid_viscosity_qp")),
    _aperture(declareADPropertyByName<Real>(_base_name + "hydraulic_aperture")),
    _permeability(declareADPropertyByName<Real>(_base_name + "fracture_permeability")),
    _transmissivity(declareADPropertyByName<Real>(_base_name + "fracture_transmissivity"))
{
  if (_maximum_aperture <= _minimum_aperture)
    paramError("maximum_aperture", "maximum_aperture must be greater than minimum_aperture.");
}

void
OrcaCZMStressDependentAperture::initQpStatefulProperties()
{
  _aperture[_qp] = _reference_aperture;
  _permeability[_qp] = _reference_aperture * _reference_aperture / 12.0;
  _transmissivity[_qp] = 0.0;
}

void
OrcaCZMStressDependentAperture::computeQpProperties()
{
  const ADReal effective_normal_compression =
      MetaPhysicL::raw_value(_effective_normal_traction[_qp]) < 0.0
          ? -_effective_normal_traction[_qp]
          : ADReal(0.0);

  ADReal aperture = _reference_aperture +
                    _normal_compliance *
                        (_reference_effective_normal_stress - effective_normal_compression) +
                    _dilation_aperture_coefficient * _dilation[_qp];

  if (MetaPhysicL::raw_value(aperture) < _minimum_aperture)
    aperture = _minimum_aperture;
  else if (MetaPhysicL::raw_value(aperture) > _maximum_aperture)
    aperture = _maximum_aperture;

  _aperture[_qp] = aperture;
  _permeability[_qp] = aperture * aperture / 12.0;
  _transmissivity[_qp] = aperture * aperture * aperture / (12.0 * _mu_f[_qp]);
}
