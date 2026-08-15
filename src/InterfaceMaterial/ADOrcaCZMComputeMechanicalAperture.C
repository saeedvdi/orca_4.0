#include "ADOrcaCZMComputeMechanicalAperture.h"

#include <algorithm>

registerMooseObject("OrcaApp", ADOrcaCZMComputeMechanicalAperture);
registerMooseObjectAliased(
    "OrcaApp", ADOrcaCZMComputeMechanicalAperture, "OrcaCZMComputeMechanicalAperture");

InputParameters
ADOrcaCZMComputeMechanicalAperture::validParams()
{
  InputParameters params = InterfaceMaterial::validParams();
  params.addClassDescription(
      "Compute mechanical aperture from the local interface displacement jump. "
      "By convention, the local normal jump is component 0 (positive = opening). "
      "The output 'mechanical_aperture' represents only the reversible elastic normal "
      "separation. Irreversible dilation from shear slip is accumulated separately by "
      "ADOrcaRoughnessDamageFracturePermeability, which reads 'dilation_jump_increment' "
      "from the Barton-Bandis contact material.");
  params.addParam<std::string>("base_name", "Material property base name");
  params.addParam<std::string>(
      "jump_property_name",
      "interface_displacement_jump",
      "Name of the local displacement-jump vector property.");
  params.addParam<MaterialPropertyName>(
      "aperture_property_name",
      "mechanical_aperture",
      "Name of the output mechanical aperture property.");
  params.addParam<MaterialPropertyName>(
      "raw_aperture_property_name",
      "mechanical_aperture_raw",
      "Name of the output raw normal-jump property (not clamped).");
  params.addParam<bool>(
      "clamp_to_zero",
      true,
      "If true, output aperture = max(normal_jump, 0). "
      "This represents opening only; compression does not reduce the aperture below zero. "
      "The raw unclamped value is always available via raw_aperture_property_name.");
  return params;
}

ADOrcaCZMComputeMechanicalAperture::ADOrcaCZMComputeMechanicalAperture(
    const InputParameters & parameters)
  : InterfaceMaterial(parameters),
    _base_name(isParamValid("base_name") && !getParam<std::string>("base_name").empty()
                   ? getParam<std::string>("base_name") + "_"
                   : ""),
    _interface_displacement_jump(
        getADMaterialPropertyByName<RealVectorValue>(_base_name +
                                                     getParam<std::string>("jump_property_name"))),
    _mechanical_aperture(
        declareADPropertyByName<Real>(getParam<MaterialPropertyName>("aperture_property_name"))),
    _mechanical_aperture_raw(
        declareADPropertyByName<Real>(getParam<MaterialPropertyName>("raw_aperture_property_name"))),
    _clamp_to_zero(getParam<bool>("clamp_to_zero"))
{
}

void
ADOrcaCZMComputeMechanicalAperture::computeQpProperties()
{
  // Normal jump component 0: positive = opening, negative = compression.
  // The raw value is stored without modification for diagnostics.
  // The clamped value can be used by the fracture-flow/aperture materials as the elastic
  // contribution to hydraulic aperture.
  const ADReal raw_aperture = _interface_displacement_jump[_qp](0);
  _mechanical_aperture_raw[_qp] = raw_aperture;
  _mechanical_aperture[_qp] = _clamp_to_zero ? std::max(ADReal(0.0), raw_aperture) : raw_aperture;
}
