#include "ADOrcaBartonBandisBakhtarFracturePermeability.h"

#include "metaphysicl/raw_type.h"

#include <algorithm>
#include <cmath>

registerMooseObject("OrcaApp", ADOrcaBartonBandisBakhtarFracturePermeability);
registerMooseObjectAliased("OrcaApp",
                           ADOrcaBartonBandisBakhtarFracturePermeability,
                           "OrcaBartonBandisBakhtarFracturePermeability");

InputParameters
ADOrcaBartonBandisBakhtarFracturePermeability::validParams()
{
  InputParameters params = InterfaceMaterial::validParams();
  params.addClassDescription(
      "Literal Barton-Bandis-Bakhtar (1985) hydraulic aperture reduction: "
      "e_h [um] = mechanical_aperture [um]^2 / JRC^2.5, with fracture_permeability = e_h^2/12 "
      "(cubic law). Distinct from ADOrcaRoughnessDamageFracturePermeability's additive "
      "roughness/dilation construction -- this class implements the published power law "
      "directly, for comparison against it.");

  params.addParam<std::string>("base_name", "", "Material property base name.");

  params.addParam<MaterialPropertyName>("mechanical_aperture_name",
                                        "mechanical_aperture",
                                        "Mechanical aperture property name (m).");

  params.addParam<bool>(
      "use_mobilized_jrc",
      false,
      "When true, couple JRC from jrc_name (a non-AD material property, e.g. the "
      "'bb_jrc_mobilized' diagnostic exported by the Barton-Bandis contact traction material) "
      "instead of using the constant jrc parameter. Lets the hydraulic reduction track the same "
      "stress-mobilized roughness degradation used in the mechanical response.");
  params.addParam<MaterialPropertyName>(
      "jrc_name",
      "bb_jrc_mobilized",
      "JRC material property name. Only coupled when use_mobilized_jrc = true.");
  params.addRangeCheckedParam<Real>(
      "jrc",
      10.0,
      "jrc > 0.0",
      "Constant joint roughness coefficient JRC, used when use_mobilized_jrc = false. Default "
      "matches the Barton-Bandis contact material's own JRC0 default.");
  params.addRangeCheckedParam<Real>(
      "jrc_min",
      0.1,
      "jrc_min > 0.0",
      "Floor applied to whichever JRC is in use, to avoid the JRC^2.5 denominator collapsing "
      "toward zero (relevant mainly for use_mobilized_jrc = true, where the mobilized JRC can "
      "approach 0 at low normal stress).");
  params.addRangeCheckedParam<Real>(
      "mechanical_aperture_offset",
      0.0,
      "mechanical_aperture_offset >= 0.0",
      "Residual/mismatch aperture (m) added to the mechanical aperture before applying the "
      "power law. NOT part of the literal 1985 formula -- exists only so a fully closed joint "
      "(mechanical_aperture = 0) does not force e_h identically to 0. Default 0 = pure literal "
      "formula.");

  params.addParam<MaterialPropertyName>("hydraulic_aperture_name",
                                        "hydraulic_aperture",
                                        "Output hydraulic aperture property name.");
  params.addParam<MaterialPropertyName>("fracture_permeability_name",
                                        "fracture_permeability",
                                        "Output fracture permeability property name.");
  params.addParam<MaterialPropertyName>(
      "transmissibility_name",
      "fracture_transmissivity",
      "Optional output property name for cubic-law fracture transmissivity e_h^3/(12*mu).");
  params.addParam<MaterialPropertyName>(
      "jrc_used_name", "bb_bakhtar_jrc_used", "Diagnostic output for the JRC value actually applied.");

  params.addParam<bool>(
      "compute_effective_normal_compression",
      false,
      "Optional pass-through diagnostic, unrelated to the aperture law itself: couple "
      "effective_normal_traction_name and export the compression-positive effective normal "
      "stress, matching the same diagnostic ADOrcaRoughnessDamageFracturePermeability exports, "
      "so decks swapping in this material keep their sigma'_n validation panel.");
  params.addParam<MaterialPropertyName>(
      "effective_normal_traction_name",
      "czm_sigma_n",
      "Scalar local normal traction property (tension positive) used only by the optional "
      "effective-normal-compression diagnostic.");
  params.addParam<MaterialPropertyName>(
      "effective_normal_compression_name",
      "effective_normal_compression",
      "Diagnostic output property for compression-positive effective normal stress (Pa).");

  params.addRangeCheckedParam<Real>("min_hydraulic_aperture",
                                    1e-12,
                                    "min_hydraulic_aperture >= 0.0",
                                    "Lower bound on hydraulic aperture (m).");
  params.addRangeCheckedParam<Real>("max_hydraulic_aperture",
                                    0.0,
                                    "max_hydraulic_aperture >= 0.0",
                                    "Upper bound on hydraulic aperture (m); 0 disables.");

  params.addParam<bool>(
      "compute_transmissibility",
      true,
      "If true, also compute cubic-law fracture transmissivity e_h^3/(12*mu), as expected by "
      "OrcaFractureFlowInterfaceKernel.");
  params.addRangeCheckedParam<Real>("fluid_viscosity",
                                    1.002e-3,
                                    "fluid_viscosity > 0.0",
                                    "Fluid dynamic viscosity (Pa.s).");

  return params;
}

ADOrcaBartonBandisBakhtarFracturePermeability::ADOrcaBartonBandisBakhtarFracturePermeability(
    const InputParameters & parameters)
  : InterfaceMaterial(parameters),
    _base_name(isParamValid("base_name") && !getParam<std::string>("base_name").empty()
                   ? getParam<std::string>("base_name") + "_"
                   : ""),
    _mechanical_aperture(
        getADMaterialPropertyByName<Real>(getParam<MaterialPropertyName>("mechanical_aperture_name"))),
    _use_mobilized_jrc(getParam<bool>("use_mobilized_jrc")),
    _jrc_mobilized(_use_mobilized_jrc ? &getMaterialPropertyByName<Real>(
                                             _base_name + getParam<MaterialPropertyName>("jrc_name"))
                                       : nullptr),
    _effective_normal_traction(
        getParam<bool>("compute_effective_normal_compression")
            ? &getADMaterialPropertyByName<Real>(
                  _base_name + getParam<MaterialPropertyName>("effective_normal_traction_name"))
            : nullptr),
    _hydraulic_aperture(
        declareADPropertyByName<Real>(getParam<MaterialPropertyName>("hydraulic_aperture_name"))),
    _fracture_permeability(
        declareADPropertyByName<Real>(getParam<MaterialPropertyName>("fracture_permeability_name"))),
    _transmissivity(getParam<bool>("compute_transmissibility")
                        ? &declareADPropertyByName<Real>(
                              getParam<MaterialPropertyName>("transmissibility_name"))
                        : nullptr),
    _jrc_used(declareADPropertyByName<Real>(getParam<MaterialPropertyName>("jrc_used_name"))),
    _effective_normal_compression(
        getParam<bool>("compute_effective_normal_compression")
            ? &declareADPropertyByName<Real>(
                  getParam<MaterialPropertyName>("effective_normal_compression_name"))
            : nullptr),
    _jrc_const(getParam<Real>("jrc")),
    _jrc_min(getParam<Real>("jrc_min")),
    _mechanical_aperture_offset(getParam<Real>("mechanical_aperture_offset")),
    _min_aperture(getParam<Real>("min_hydraulic_aperture")),
    _max_aperture(getParam<Real>("max_hydraulic_aperture")),
    _compute_transmissivity(getParam<bool>("compute_transmissibility")),
    _fluid_viscosity(getParam<Real>("fluid_viscosity"))
{
}

void
ADOrcaBartonBandisBakhtarFracturePermeability::initQpStatefulProperties()
{
  // Mirrors the same fix ADOrcaRoughnessDamageFracturePermeability needed: OrcaFractureFlowInterfaceKernel's
  // storage term is (a_h - a_h_old)/dt, so a_h must be seeded here or a_h_old = 0 injects a
  // spurious first-step fluid source. At t=0 the mechanical aperture is 0 (undeformed joint), and
  // the coupled mobilized-JRC material is not yet available during stateful init, so use the
  // constant jrc regardless of use_mobilized_jrc (matching the existing material's R=1 convention).
  const Real E0_um = _mechanical_aperture_offset * 1.0e6;
  const Real jrc0 = std::max(_jrc_const, _jrc_min);
  Real e_h0 = (E0_um * E0_um / std::pow(jrc0, 2.5)) * 1.0e-6;

  if (e_h0 < _min_aperture)
    e_h0 = _min_aperture;
  if (_max_aperture > 0.0 && e_h0 > _max_aperture)
    e_h0 = _max_aperture;

  _hydraulic_aperture[_qp] = ADReal(e_h0);
  _fracture_permeability[_qp] = ADReal(e_h0 * e_h0 / 12.0);
  _jrc_used[_qp] = ADReal(jrc0);
  if (_compute_transmissivity && _transmissivity)
    (*_transmissivity)[_qp] = ADReal(e_h0 * e_h0 * e_h0 / (12.0 * _fluid_viscosity));
  if (_effective_normal_compression)
    (*_effective_normal_compression)[_qp] = ADReal(0.0);
}

void
ADOrcaBartonBandisBakhtarFracturePermeability::computeQpProperties()
{
  using std::pow;

  ADReal E = _mechanical_aperture[_qp] + ADReal(_mechanical_aperture_offset);
  if (MetaPhysicL::raw_value(E) < 0.0)
    E = ADReal(0.0);
  const ADReal E_um = E * 1.0e6;

  Real jrc = _use_mobilized_jrc ? (*_jrc_mobilized)[_qp] : _jrc_const;
  if (jrc < _jrc_min)
    jrc = _jrc_min;
  _jrc_used[_qp] = ADReal(jrc);

  // Literal Barton-Bandis-Bakhtar (1985): e_h [um] = E_m [um]^2 / JRC^2.5.
  const ADReal e_h_um = pow(E_um, 2) / std::pow(jrc, 2.5);
  ADReal e_h = e_h_um * 1.0e-6;

  if (MetaPhysicL::raw_value(e_h) < _min_aperture)
    e_h = ADReal(_min_aperture);
  if (_max_aperture > 0.0 && MetaPhysicL::raw_value(e_h) > _max_aperture)
    e_h = ADReal(_max_aperture);

  _hydraulic_aperture[_qp] = e_h;
  _fracture_permeability[_qp] = (e_h * e_h) / 12.0;

  if (_compute_transmissivity && _transmissivity)
    (*_transmissivity)[_qp] = (e_h * e_h * e_h) / (12.0 * _fluid_viscosity);

  if (_effective_normal_traction && _effective_normal_compression)
  {
    const ADReal traction_n = (*_effective_normal_traction)[_qp];
    (*_effective_normal_compression)[_qp] =
        MetaPhysicL::raw_value(traction_n) < 0.0 ? -traction_n : ADReal(0.0);
  }
}
