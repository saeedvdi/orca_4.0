#include "OrcaFaultFlowInterfaceKernel.h"

#include "MathUtils.h"
#include "metaphysicl/raw_type.h"

registerMooseObject("OrcaApp", OrcaFaultFlowInterfaceKernel);

InputParameters
OrcaFaultFlowInterfaceKernel::validParams()
{
  InputParameters params = ADInterfaceKernel::validParams();

  params.addClassDescription(
      "Mass-conservative pressure-transfer interface kernel for split faults. "
      "Residual uses flux q = T * (p_primary - p_secondary), applied with opposite signs on the "
      "two sides of the interface. "
      "Supports three transmissibility models: 'constant', 'aperture_cubic' (computes T from "
      "the mechanical aperture on-the-fly), and 'permeability_property' (reads pre-computed "
      "fracture permeability from the CZM permeability material — the recommended model "
      "for the Ye & Ghassemi (2018) validation because it includes the irreversible dilatant "
      "contribution to the hydraulic aperture).");

  // --- model selection ---
  params.addParam<MooseEnum>("model",
                             MooseEnum("constant aperture_cubic permeability_property", "constant"),
                             "Transmissibility model. "
                             "'constant': use user-provided transmissibility. "
                             "'aperture_cubic': compute from mechanical aperture only (no dilation). "
                             "'permeability_property': read k from AD material property and compute "
                             "T = k / (mu * fault_thickness). Use this with "
                             "the roughness-damage permeability material for full HM coupling.");

  // --- use_transmissibility_property (legacy override) ---
  params.addParam<bool>("use_transmissibility_property",
                        false,
                        "If true, read transmissibility directly from AD material property "
                        "'transmissibility_property_name' and ignore 'model' entirely.");
  params.addParam<MaterialPropertyName>(
      "transmissibility_property_name",
      "fault_flow_transmissibility",
      "Name of AD material property for transmissibility (legacy override path).");

  // --- constant model ---
  params.addParam<Real>("transmissibility",
                        0.0,
                        "Constant hydraulic transmissibility T (m^3 s / kg) for model='constant'.");
  params.addRangeCheckedParam<Real>(
      "min_transmissibility",
      0.0,
      "min_transmissibility >= 0.0",
      "Lower bound applied to computed transmissibility.");

  // --- aperture_cubic model ---
  params.addParam<MaterialPropertyName>("aperture_property_name",
                                        "mechanical_aperture",
                                        "AD aperture property for model='aperture_cubic'.");
  params.addParam<Real>("initial_aperture",
                        0.0,
                        "Reference hydraulic aperture b0 (m) for model='aperture_cubic'.");
  params.addRangeCheckedParam<Real>(
      "min_aperture",
      1e-12,
      "min_aperture >= 0.0",
      "Lower bound for effective aperture in aperture_cubic mode.");
  params.addParam<Real>("aperture_scale",
                        1.0,
                        "Scale factor on aperture property in aperture_cubic mode.");
  params.addRangeCheckedParam<Real>("fault_thickness",
                                    1e-3,
                                    "fault_thickness > 0.0",
                                    "Fault core thickness (m) for aperture_cubic and "
                                    "permeability_property modes.");
  params.addParam<bool>("clamp_aperture_to_opening",
                        true,
                        "Clamp aperture to positive part in aperture_cubic mode.");

  // --- permeability_property model ---
  params.addParam<MaterialPropertyName>(
      "permeability_property_name",
      "fracture_permeability",
      "Name of AD permeability property for model='permeability_property'. "
      "Produced by the roughness-damage fracture-permeability material.");

  // --- fluid viscosity ---
  params.addParam<bool>(
      "use_material_viscosity",
      true,
      "If true, read fluid viscosity from AD material property 'fluid_viscosity_name'. "
      "Otherwise use constant 'fluid_viscosity'.");
  params.addParam<MaterialPropertyName>("fluid_viscosity_name",
                                        "fluid_viscosity_qp",
                                        "Name of AD fluid viscosity material property.");
  params.addRangeCheckedParam<Real>(
      "fluid_viscosity", 1e-3, "fluid_viscosity > 0.0", "Constant fluid viscosity (Pa.s).");

  // --- fluid density ---
  params.addParam<bool>("multiply_by_fluid_density",
                        true,
                        "If true, multiply interface flux by fluid density (mass flux form).");
  params.addParam<bool>(
      "use_material_density",
      true,
      "If true and multiply_by_fluid_density=true, read density from AD material property.");
  params.addParam<MaterialPropertyName>("fluid_density_name",
                                        "fluid_density_qp",
                                        "Name of AD fluid density material property.");
  params.addRangeCheckedParam<Real>(
      "fluid_density", 1000.0, "fluid_density > 0.0", "Constant fluid density (kg/m^3).");

  return params;
}

OrcaFaultFlowInterfaceKernel::OrcaFaultFlowInterfaceKernel(const InputParameters & parameters)
  : ADInterfaceKernel(parameters),
    _model(getParam<MooseEnum>("model")),
    _use_transmissibility_property(getParam<bool>("use_transmissibility_property")),
    _transmissibility_property_name(getParam<MaterialPropertyName>("transmissibility_property_name")),
    _transmissibility(getParam<Real>("transmissibility")),
    _min_transmissibility(getParam<Real>("min_transmissibility")),
    _transmissibility_prop(_use_transmissibility_property
                               ? &getADMaterialProperty<Real>(_transmissibility_property_name)
                               : nullptr),
    _aperture_property_name(getParam<MaterialPropertyName>("aperture_property_name")),
    _initial_aperture(getParam<Real>("initial_aperture")),
    _min_aperture(getParam<Real>("min_aperture")),
    _aperture_scale(getParam<Real>("aperture_scale")),
    _fault_thickness(getParam<Real>("fault_thickness")),
    _clamp_aperture_to_opening(getParam<bool>("clamp_aperture_to_opening")),
    _mechanical_aperture(_model == "aperture_cubic"
                             ? &getADMaterialProperty<Real>(_aperture_property_name)
                             : nullptr),
    // permeability_property model
    _permeability_property_name(getParam<MaterialPropertyName>("permeability_property_name")),
    _fracture_permeability_prop(_model == "permeability_property"
                                    ? &getADMaterialProperty<Real>(_permeability_property_name)
                                    : nullptr),
    _use_material_viscosity(getParam<bool>("use_material_viscosity")),
    _fluid_viscosity_name(getParam<MaterialPropertyName>("fluid_viscosity_name")),
    _fluid_viscosity(getParam<Real>("fluid_viscosity")),
    _fluid_viscosity_prop(_use_material_viscosity
                              ? &getADMaterialProperty<Real>(_fluid_viscosity_name)
                              : nullptr),
    _multiply_by_fluid_density(getParam<bool>("multiply_by_fluid_density")),
    _use_material_density(getParam<bool>("use_material_density")),
    _fluid_density_name(getParam<MaterialPropertyName>("fluid_density_name")),
    _fluid_density(getParam<Real>("fluid_density")),
    _fluid_density_prop(_multiply_by_fluid_density && _use_material_density
                            ? &getADMaterialProperty<Real>(_fluid_density_name)
                            : nullptr)
{
  if (_use_transmissibility_property &&
      !hasADMaterialProperty<Real>(_transmissibility_property_name))
    mooseError("OrcaFaultFlowInterfaceKernel: use_transmissibility_property=true requires AD "
               "material property '",
               _transmissibility_property_name, "'.");

  if (_model == "aperture_cubic" && !hasADMaterialProperty<Real>(_aperture_property_name))
    mooseError("OrcaFaultFlowInterfaceKernel: model='aperture_cubic' requires AD aperture "
               "property '", _aperture_property_name, "'.");

  if (_model == "permeability_property" &&
      !hasADMaterialProperty<Real>(_permeability_property_name))
    mooseError("OrcaFaultFlowInterfaceKernel: model='permeability_property' requires AD "
               "permeability property '", _permeability_property_name,
               "'. Make sure the roughness-damage fracture-permeability material is active.");

  if (_use_material_viscosity && !hasADMaterialProperty<Real>(_fluid_viscosity_name))
    mooseError("OrcaFaultFlowInterfaceKernel: use_material_viscosity=true requires AD material "
               "property '", _fluid_viscosity_name, "'.");

  if (_multiply_by_fluid_density && _use_material_density &&
      !hasADMaterialProperty<Real>(_fluid_density_name))
    mooseError("OrcaFaultFlowInterfaceKernel: use_material_density=true requires AD material "
               "property '", _fluid_density_name, "'.");
}

ADReal
OrcaFaultFlowInterfaceKernel::computeFluidViscosity() const
{
  return _use_material_viscosity ? (*_fluid_viscosity_prop)[_qp] : ADReal(_fluid_viscosity);
}

ADReal
OrcaFaultFlowInterfaceKernel::computeFluidDensity() const
{
  return (_multiply_by_fluid_density && _use_material_density) ? (*_fluid_density_prop)[_qp]
                                                                : ADReal(_fluid_density);
}

ADReal
OrcaFaultFlowInterfaceKernel::computeTransmissibility() const
{
  ADReal transmissibility = _transmissibility;

  if (_use_transmissibility_property)
  {
    transmissibility = (*_transmissibility_prop)[_qp];
  }
  else if (_model == "aperture_cubic")
  {
    // Mechanical-aperture-only path (no dilatant contribution).
    ADReal aperture = _initial_aperture + _aperture_scale * (*_mechanical_aperture)[_qp];

    if (_clamp_aperture_to_opening)
      aperture = MathUtils::positivePart(aperture);

    if (MetaPhysicL::raw_value(aperture) < _min_aperture)
      aperture = _min_aperture;

    const ADReal mu = computeFluidViscosity();
    const ADReal k  = (aperture * aperture) / 12.0;
    transmissibility = k / (mu * _fault_thickness);
  }
  else if (_model == "permeability_property")
  {
    // Recommended path for Ye & Ghassemi (2018) validation.
    // Reads k from the roughness-damage permeability material, which includes both the
    // reversible elastic opening and the irreversible dilatant contribution.
    //   T = k / (mu * L_fault)
    const ADReal mu = computeFluidViscosity();
    transmissibility = (*_fracture_permeability_prop)[_qp] / (mu * _fault_thickness);
  }

  if (MetaPhysicL::raw_value(transmissibility) < _min_transmissibility)
    transmissibility = _min_transmissibility;

  return transmissibility;
}

ADReal
OrcaFaultFlowInterfaceKernel::computeQpResidual(Moose::DGResidualType type)
{
  ADReal flux = computeTransmissibility() * (_u[_qp] - _neighbor_value[_qp]);

  if (_multiply_by_fluid_density)
    flux *= computeFluidDensity();

  switch (type)
  {
    case Moose::Element:
      return  _test[_i][_qp] * flux;

    case Moose::Neighbor:
      return -_test_neighbor[_i][_qp] * flux;
  }

  mooseError("OrcaFaultFlowInterfaceKernel: unsupported DGResidualType.");
  return 0.0;
}
