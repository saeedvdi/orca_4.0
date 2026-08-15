#include "OrcaTHMaterial.h"

#include "MooseError.h"
#include "metaphysicl/raw_type.h"

registerMooseObject("OrcaApp", OrcaTHMaterial);

InputParameters
OrcaTHMaterial::validParams()
{
    InputParameters params = ADMaterial::validParams();

    params.addClassDescription(
        "This material is used to compute the fluid properties for the fully saturated single-phase flow."
        "Hydraulic material properties are required."
        "Thermal properties are optional and only enforced when temperature is coupled.");

    // Coupled variables
    params.addRequiredCoupledVar("pore_pressure", "The pressure of the fluid inside the pore space (Pa).");
    params.addCoupledVar("temperature", "Temperature (K).");

    // Hydraulic Properties inputs (required):
    // permeability model
    params.addRequiredParam<RealTensorValue>(
        "initial_permeability", "Initial Permeability tensor k (m^2).");
    params.addParam<MooseEnum>(
        "permeability_model",
        MooseEnum("constant", "constant"),
        "the permeability model");
    
    // Porosity model
    params.addRequiredRangeCheckedParam<Real>(
        "initial_porosity",
        "initial_porosity > 0.0 & initial_porosity <= 1.0",
        "Initial porosity (-).");
    params.addParam<MooseEnum>(
        "porosity_model",
        MooseEnum("constant", "constant"),
        "the porosity model");

    // fluid reference fluid state for liquid water according to IAPWS 2008
    params.addRangeCheckedParam<Real>("fluid_bulk_modulus", 2e9, "fluid_bulk_modulus > 0.0", "Fluid bulk modulus Kf (Pa).");
    params.addRangeCheckedParam<Real>("fluid_density_ref", 1000.0, "fluid_density_ref > 0.0",
                                        "Reference density rho_ref (kg/m^3) at (p_ref,T_ref).");
    params.addRangeCheckedParam<Real>("fluid_viscosity_ref", 1.0e-3, "fluid_viscosity_ref > 0.0",
                                        "Reference viscosity mu_ref (Pa*s) at (p_ref,T_ref).");
    params.addParam<Real>("pore_pressure_ref", 0.0, "Reference pressure p_ref (Pa) for EOS.");
    params.addParam<Real>("fluid_temperature_ref", 293.15, "Reference temperature T_ref (K) for EOS.");
    params.addRangeCheckedParam<Real>("fluid_thermal_expansion_ref", 0.0, "fluid_thermal_expansion_ref >= 0.0",
        "Reference fluid volumetric thermal expansion coefficient beta_ref (1/K).");
  
    // Retain the former selectors temporarily so existing user-model input files still parse.
    // External fluid-properties UserObjects are intentionally unsupported: this material is self-contained.
    params.addDeprecatedParam<MooseEnum>(
        "fluid_properties_model",
        MooseEnum("fluid_properties user", "user"),
        "Legacy fluid-property model selector. Only 'user' is supported.",
        "OrcaTHMaterial now computes fluid properties directly from its local input parameters; "
        "remove fluid_properties_model from the input file.");
    params.addDeprecatedParam<UserObjectName>(
        "fp",
        UserObjectName(""),
        "Legacy external fluid-properties UserObject name.",
        "External fluid-properties UserObjects are no longer supported by OrcaTHMaterial; remove fp "
        "and provide the fluid-property parameters directly.");
    params.addParam<MooseEnum>(
        "fluid_density_model",
        MooseEnum("temperature_pressure_dependent constant", "temperature_pressure_dependent"),
        "temperature_pressure_dependent: compute density from pressure and temperature. "
        "constant: use fluid_density_ref.");
  
    // Thermal Properties inputs (optional):
    // NOTE: These are OPTIONAL and only enforced when temperature is coupled
    params.addParam<Real>("solid_specific_heat_capacity",
                            "Rock grain specific heat capacity cp_s (J/kg/K).");
    params.addParam<Real>("solid_density", "Rock grain density rho_s (kg/m^3).");
    
    // thermal expansion model
    params.addParam<Real>("volumetric_solid_thermal_expansion", "Volumetric thermal expansion coefficient of the drained skeleton (1/K).");
    params.addParam<Real>("volumetric_fluid_thermal_expansion", 2.1e-4,
        "Volumetric thermal expansion coefficient of the pore fluid (1/K).");
    // If user sets this, we use it (otherwise we compute from porosity/biot)
    // NOTE: Optional, but required when thermal_expansion_model=user_constant
    params.addParam<Real>(
        "effective_thermal_expansion_coeff",
        0.0,
        "User-provided effective thermal expansion coefficient (1/K). "
        "Used only when thermal_expansion_model=user_constant.");
    // thermal expansion model
    params.addParam<MooseEnum>(
        "effective_thermal_expansion_model",
        MooseEnum("user constant computed", "computed"),
        "computed: alpha_eff = (biot - phi)*beta_solid + phi*beta_fluid (recomputed each step). "
        "user: alpha_eff = effective_thermal_expansion_coeff (user-provided constant). "
        "constant: use old alpha_eff (stateful), helpful for stabilization/testing.");

    params.addDeprecatedParam<MooseEnum>(
        "fluid_thermal_expansion_model",
        MooseEnum("fluid_properties user", "user"),
        "Legacy fluid thermal-expansion selector. Only 'user' is supported.",
        "OrcaTHMaterial now uses volumetric_fluid_thermal_expansion directly; remove "
        "fluid_thermal_expansion_model from the input file.");

    // Thermal conductivity model
    params.addParam<RealTensorValue>(
        "dry_thermal_conductivity",
        "Dry rock thermal conductivity tensor (W/m/K).");
    params.addParam<RealTensorValue>(
        "wet_thermal_conductivity",
        RealTensorValue(0.0),
        "Wet/saturated thermal conductivity tensor (W/m/K). Used only if "
        "thermal_conductivity_model=effective_mixture.");

    params.addParam<MooseEnum>(
        "thermal_conductivity_model",
        MooseEnum("dry_only effective_mixture", "dry_only"),
        "dry_only: k = dry_thermal_conductivity. "
        "effective_mixture: k = phi*k_wet + (1-phi)*k_dry.");

    // fluid reference thermal state for liquid water according to IAPWS 2008
    params.addParam<bool>("compute_fluid_specific_heat", true, "Compute cp and cv.");
    params.addParam<bool>("compute_fluid_internal_energy", true, "Compute e.");
    params.addParam<bool>("compute_fluid_enthalpy", true, "Compute h.");
    params.addParam<bool>("compute_fluid_entropy", true, "Compute s.");
    params.addParam<bool>("compute_fluid_thermal_conductivity", true, "Compute kth (fluid-only scalar).");
    params.addParam<bool>("compute_fluid_thermal_expansion", true, "Compute beta (fluid volumetric expansion).");

    params.addRangeCheckedParam<Real>("fluid_thermal_expansion", 0.0, "fluid_thermal_expansion >= 0.0",
        "Fluid volumetric thermal expansion coefficient beta (1/K).");
    params.addRangeCheckedParam<Real>("fluid_specific_heat_pressure", 4180.0,
                                        "fluid_specific_heat_pressure > 0.0", "cp (J/kg/K).");
    params.addRangeCheckedParam<Real>("fluid_specific_heat_volume", 4180.0,
                                        "fluid_specific_heat_volume > 0.0", "cv (J/kg/K).");
    params.addParam<Real>("fluid_internal_energy", 0.0, "e (J/kg).");
    params.addParam<Real>("fluid_specific_entropy", 300.0, "s (J/kg/K).");
    params.addParam<Real>("fluid_thermal_conductivity", 0.0, "kth (W/m/K).");
    params.addParam<Real>("porepressure_coefficient",
                            1.0,
                            "The enthalpy is internal_energy + (p - p_ref) / rho * porepressure_coefficient. "
                            "Physically this should be 1.0, but analytic solutions are simplified when it is zero.");
    

    params.addRangeCheckedParam<Real>("solid_bulk_compliance",0.0,
                                        "solid_bulk_compliance>=0.0",
                                        "Reciprocal of the drained bulk modulus of the porous "
                                        "skeleton.  If strain = C * stress, then solid_bulk_compliance "
                                        "= de_ij de_kl C_ijkl.  If the grain bulk modulus is Kg then "
                                        "1/Kg = (1 - biot_coefficient) * solid_bulk_compliance.");
    params.addParam<MooseEnum>(
        "biot_modulus_model",
        MooseEnum("time_dependent constant", "constant"),
        "time_dependent: compute M every step; constant: freeze M after initialization.");

    return params;
}

OrcaTHMaterial::OrcaTHMaterial(const InputParameters & parameters)
: ADMaterial(parameters),
    _p(adCoupledValue("pore_pressure")),
    _has_temperature(isCoupled("temperature")),
    // NOTE: temperature pointers optional
    _T(_has_temperature ? &adCoupledValue("temperature") : nullptr),

    // Model selection
    _porosity_model(getParam<MooseEnum>("porosity_model")),
    _permeability_model(getParam<MooseEnum>("permeability_model")),
    _fluid_density_model(getParam<MooseEnum>("fluid_density_model")),
    _thermal_conductivity_model(getParam<MooseEnum>("thermal_conductivity_model")),
    _effective_thermal_expansion_model(getParam<MooseEnum>("effective_thermal_expansion_model")),

    // inputs
    _Kf_in(getParam<Real>("fluid_bulk_modulus")),
    _kappa_in(getParam<RealTensorValue>("initial_permeability")),
    _phi_in(getParam<Real>("initial_porosity")),

    // EOS reference state
    _rho_ref(getParam<Real>("fluid_density_ref")),
    _mu_ref(getParam<Real>("fluid_viscosity_ref")),
    _p_ref(getParam<Real>("pore_pressure_ref")),
    _T_ref(getParam<Real>("fluid_temperature_ref")),
    _beta_ref(parameters.isParamSetByUser("fluid_thermal_expansion_ref")
                ? getParam<Real>("fluid_thermal_expansion_ref")
                : getParam<Real>("fluid_thermal_expansion")),

    // parameter computation
    _compute_cp_cv(getParam<bool>("compute_fluid_specific_heat")),
    _compute_e(getParam<bool>("compute_fluid_internal_energy")),
    _compute_h(getParam<bool>("compute_fluid_enthalpy")),
    _compute_s(getParam<bool>("compute_fluid_entropy")),
    _compute_k_fluid(getParam<bool>("compute_fluid_thermal_conductivity")),
    _compute_alpha_fluid_T(getParam<bool>("compute_fluid_thermal_expansion")),

    // fluid thermal inputs
    _cp_f_in(_has_temperature ? &getParam<Real>("fluid_specific_heat_pressure") : nullptr),
    _cv_f_in(_has_temperature ? &getParam<Real>("fluid_specific_heat_volume") : nullptr),
    _fluid_internal_energy_in(_has_temperature ? &getParam<Real>("fluid_internal_energy") : nullptr),
    _s_in(_has_temperature ? &getParam<Real>("fluid_specific_entropy") : nullptr),
    _k_fluid_in(_has_temperature ? &getParam<Real>("fluid_thermal_conductivity") : nullptr),
    _pp_coefficient_in(_has_temperature ? &getParam<Real>("porepressure_coefficient") : nullptr),

    _cp_s_in(_has_temperature ? &getParam<Real>("solid_specific_heat_capacity") : nullptr),
    _rho_s_in(_has_temperature ? &getParam<Real>("solid_density") : nullptr),
    _fluid_coeff_in(_has_temperature ? &getParam<Real>("volumetric_fluid_thermal_expansion") : nullptr),
    _drained_coeff_in(_has_temperature ? &getParam<Real>("volumetric_solid_thermal_expansion") : nullptr),
    _alpha_eff_user(_has_temperature ? &getParam<Real>("effective_thermal_expansion_coeff") : nullptr),
    _k_dry_in(_has_temperature ? &getParam<RealTensorValue>("dry_thermal_conductivity") : nullptr),
    _k_wet_in(_has_temperature ? &getParam<RealTensorValue>("wet_thermal_conductivity") : nullptr),

    // dependencies - get from biot material model
    _biot(getADMaterialProperty<Real>("biot_coefficient_qp")),                                           

    // outputs
    _Kf(declareADProperty<Real>("fluid_bulk_modulus_qp")),
    _porosity(declareADProperty<Real>("porosity_qp")),
    _permeability(declareADProperty<RealTensorValue>("permeability_qp")),

    _rho_f(declareADProperty<Real>("fluid_density_qp")),

    _mu(declareADProperty<Real>("fluid_viscosity_qp")),

    _cp_f(declareADProperty<Real>("fluid_cp_qp")),
    _cv_f(declareADProperty<Real>("fluid_cv_qp")),
    _fluid_internal_energy(declareADProperty<Real>("fluid_internal_energy_qp")),
    _fluid_enthalpy(declareADProperty<Real>("fluid_enthalpy_qp")),
    _s(declareADProperty<Real>("fluid_entropy_qp")),
    _k_fluid(declareADProperty<Real>("fluid_thermal_conductivity_qp")),
    _pp_coefficient(declareADProperty<Real>("porepressure_coefficient_qp")),
    
    _alpha_fluid_T(declareADProperty<Real>("fluid_thermal_expansion_qp")),
    _fluid_mobility_tensor(declareADProperty<RealTensorValue>("fluid_mobility_tensor_qp")),

    // thermal properties
    _cp_s(declareADProperty<Real>("solid_specific_heat_capacity_qp")),
    _rho_s(declareADProperty<Real>("solid_density_qp")),
    _fluid_coeff(declareADProperty<Real>("volumetric_fluid_thermal_expansion_qp")),
    _drained_coeff(declareADProperty<Real>("volumetric_solid_thermal_expansion_qp")),

    _rock_energy(declareADProperty<Real>("rock_energy_density_qp")),
    _alpha_eff_T(declareADProperty<Real>("effective_thermal_expansion_coeff_qp")),
    _alpha_eff_T_old(getMaterialPropertyOld<Real>("effective_thermal_expansion_coeff_qp")),

    _k_eff(declareADProperty<RealTensorValue>("effective_thermal_conductivity_qp")),

    // biot modulus addition
    _biot_modulus(declareADProperty<Real>("biot_modulus_qp")),
    _biot_modulus_old(getMaterialPropertyOld<Real>("biot_modulus_qp")),
    _biot_modulus_model(getParam<MooseEnum>("biot_modulus_model")),
    _has_MechMatTerm(hasADMaterialProperty<Real>("bulk_modulus")),
    _bulk_modulus(_has_MechMatTerm ? &getADMaterialProperty<Real>("bulk_modulus") : nullptr),
    _solid_bulk_compliance_set(parameters.isParamSetByUser("solid_bulk_compliance")),
    _solid_bulk_compliance_in(getParam<Real>("solid_bulk_compliance")),

    
    _solid_bulk_compliance(declareADProperty<Real>("solid_bulk_compliance_qp")),
    _biot_modulus_available(declareProperty<Real>("biot_modulus_available_qp"))
{
    if (getParam<MooseEnum>("fluid_properties_model") != "user")
        paramError("fluid_properties_model",
                   "The external fluid_properties model is no longer supported. Provide the fluid "
                   "property parameters directly to OrcaTHMaterial.");

    if (getParam<UserObjectName>("fp") != UserObjectName(""))
        paramError("fp",
                   "External fluid-properties UserObjects are no longer supported. Provide the fluid "
                   "property parameters directly to OrcaTHMaterial.");

    if (getParam<MooseEnum>("fluid_thermal_expansion_model") != "user")
        paramError("fluid_thermal_expansion_model",
                   "The external fluid_properties model is no longer supported. Set "
                   "volumetric_fluid_thermal_expansion directly.");

    // If alpha model is user_constant, ensure user actually set a meaningful value
    if (_effective_thermal_expansion_model == "user" && !parameters.isParamSetByUser("effective_thermal_expansion_coeff"))
        paramError("effective_thermal_expansion_coeff",
                "effective_thermal_expansion_model=user requires setting effective_thermal_expansion_coeff.");

    if (_has_temperature)
    {
        // require TH params only when temperature is coupled
        if (!parameters.isParamSetByUser("volumetric_solid_thermal_expansion"))
        paramError("volumetric_solid_thermal_expansion", "Required when temperature is coupled.");
        if (!parameters.isParamSetByUser("dry_thermal_conductivity"))
        paramError("dry_thermal_conductivity", "Required when temperature is coupled.");
        if (!parameters.isParamSetByUser("solid_density"))
        paramError("solid_density", "Required when temperature is coupled.");
        if (!parameters.isParamSetByUser("solid_specific_heat_capacity"))
        paramError("solid_specific_heat_capacity", "Required when temperature is coupled.");

        // range checks (since these are optional params in validParams)
        if (*_fluid_coeff_in < 0.0)
        paramError("volumetric_fluid_thermal_expansion", "Must be >= 0.0 when temperature is coupled.");
        if (_solid_bulk_compliance_in < 0.0)
        paramError("solid_bulk_compliance", "Must be >= 0.0.");
        if (*_drained_coeff_in < 0.0)
        paramError("volumetric_solid_thermal_expansion", "Must be >= 0.0 when temperature is coupled.");
        if (*_cp_s_in < 0.0)
        paramError("solid_specific_heat_capacity", "Must be >= 0.0 when temperature is coupled.");
        if (*_rho_s_in < 0.0)
        paramError("solid_density", "Must be >= 0.0 when temperature is coupled.");
    }
}

void
OrcaTHMaterial::initQpStatefulProperties()
{
    // Initialize everything consistently at t=0 so old values exist.
    computeQpProperties();
}

void
OrcaTHMaterial::computeQpProperties()
{
    // assign simple state-independent solids
    if (_has_temperature)
    {
        _cp_f[_qp] = *_cp_f_in;
        _cv_f[_qp] = *_cv_f_in;
        _fluid_internal_energy[_qp] = *_fluid_internal_energy_in;
        _s[_qp] = *_s_in;
        _k_fluid[_qp] = *_k_fluid_in;
        _pp_coefficient[_qp] = _pp_coefficient_in ? *_pp_coefficient_in : 1.0;
        _cp_s[_qp] = *_cp_s_in;
        _rho_s[_qp] = *_rho_s_in;
        _fluid_coeff[_qp] = *_fluid_coeff_in;
        _drained_coeff[_qp] = *_drained_coeff_in;
    }
    else
    {
        // HM-only (or Hydro-only): define safe values so declared properties exist and are not garbage
        _cp_f[_qp] = 0.0;
        _cv_f[_qp] = 0.0;
        _fluid_internal_energy[_qp] = 0.0;
        _s[_qp] = 0.0;
        _k_fluid[_qp] = 0.0;
        _pp_coefficient[_qp] = 1.0;

        _cp_s[_qp] = 0.0;
        _rho_s[_qp] = 0.0;
        _fluid_coeff[_qp] = 0.0;
        _drained_coeff[_qp] = 0.0;
    }

    // basic always-on hydraulic props
    _Kf[_qp] = _Kf_in; // fluid bulk modulus

    computePorosityModel();
    computePermeabilityTensorModel();
    computeDensityViscosity();
    computeMobility();

    computeSpecificHeats();
    computeInternalEnergy();
    computeEnthalpy();
    computeEntropy();
    computeRockEnergy();

    computeEffectiveThermalConductivity();
    computeFluidThermalConductivity();

    computeFluidThermalExpansionCoefficient();
    computeSolidEffectiveThermalExpansionCoefficient();

    computeBiotModulus();
}

/*----------------------------------------------------------------
Hydraulic properties computations
----------------------------------------------------------------*/
void
OrcaTHMaterial::computeDensityViscosity()
{
    const ADReal p = _p[_qp];
    const ADReal T = (_has_temperature ? (*_T)[_qp] : ADReal(0.0));

    if (_fluid_density_model == "temperature_pressure_dependent")
    {
        if (!_has_temperature)
            paramError("temperature", "Temperature must be coupled for temperature-dependent user density.");

        _rho_f[_qp] = rho_from_p_T(p, T);
        _mu[_qp] = _mu_ref;
    }
    else
    {
        _rho_f[_qp] = _rho_ref;
        _mu[_qp] = _mu_ref;
    }
}

ADReal
OrcaTHMaterial::rho_from_p_T(const ADReal & p, const ADReal & T) const
{
    // Slightly compressible thermo-fluid EOS:
    // rho = rho_ref * exp((p - p_ref)/Kf - beta*(T - T_ref))
    // this formulation comes from simple fluid properties (J/(kg K)) 
    return ADReal(_rho_ref) * exp((p - ADReal(_p_ref)) / _Kf[_qp] - ADReal(_beta_ref) * (T - ADReal(_T_ref)));
}

void
OrcaTHMaterial::computePorosityModel()
{
    if (_porosity_model == "constant")
    {
        _porosity[_qp] = _phi_in;
    }
}

void
OrcaTHMaterial::computePermeabilityTensorModel()
{
    if (_permeability_model == "constant")
    {
        _permeability[_qp] = _kappa_in;
    }
}

void
OrcaTHMaterial::computeMobility()
{
    // mobility tensor = permeability / mu
    _fluid_mobility_tensor[_qp] = _permeability[_qp] / _mu[_qp];
}

/*----------------------------------------------------------------
Thermal properties computations
----------------------------------------------------------------*/
void
OrcaTHMaterial::computeSpecificHeats()
{
    if (!_compute_cp_cv)
    {
        _cp_f[_qp] = 0;
        _cv_f[_qp] = 0;
        return;
    }

    if (!_has_temperature)
    {
        _cp_f[_qp] = 0;
        _cv_f[_qp] = 0;
        return;
    }

    _cp_f[_qp] = *_cp_f_in;
    _cv_f[_qp] = *_cv_f_in;
}

void
OrcaTHMaterial::computeInternalEnergy()
{
    if (!_compute_e)
    {
        _fluid_internal_energy[_qp] = 0;
        return;
    }

    if (!_has_temperature)
    {
        _fluid_internal_energy[_qp] = 0;
        return;
    }

    const ADReal T = (*_T)[_qp];
    _cv_f[_qp] = *_cv_f_in;
    _fluid_internal_energy[_qp] = _cv_f[_qp] * (T - ADReal(_T_ref));
}

void
OrcaTHMaterial::computeEnthalpy()
{
    if (!_compute_h)
    {
        _fluid_enthalpy[_qp] = 0.0;
        return;
    }

    if (!_has_temperature)
    {
        _fluid_enthalpy[_qp] = 0.0;
        return;
    }

    const ADReal p = _p[_qp];
    _fluid_enthalpy[_qp] =
        _fluid_internal_energy[_qp] + _pp_coefficient[_qp] * ((p - ADReal(_p_ref)) / _rho_f[_qp]);
}

void
OrcaTHMaterial::computeEntropy()
{
    if (!_compute_s)
    {
        _s[_qp] = 0;
        return;
    }

    if (!_has_temperature)
    {
        _s[_qp] = 0;
        return;
    }

    _s[_qp] = *_s_in;
}

void
OrcaTHMaterial::computeRockEnergy()
{
    if (!_has_temperature)
    {
        _rock_energy[_qp] = 0.0;
        return;
    }

    // Rock-grain volumetric heat capacity: rho_s * cp_s
    const ADReal C_s = _rho_s[_qp] * _cp_s[_qp];

    // Rock-grain energy: rho_s * cp_s * T
    _rock_energy[_qp] = C_s * (*_T)[_qp];
}

void
OrcaTHMaterial::computeEffectiveThermalConductivity()
{
    if (!_has_temperature)
    {
        _k_eff[_qp] = RealTensorValue(0.0);
        return;
    }

    const RealTensorValue k_dry = *_k_dry_in;
    const RealTensorValue k_wet = *_k_wet_in;

    if (_thermal_conductivity_model == "dry_only")
    {
        _k_eff[_qp] = k_dry;
        return;
    }

    // effective_mixture
    _k_eff[_qp] = _porosity[_qp] * k_wet + (1.0 - _porosity[_qp]) * k_dry;
}

void
OrcaTHMaterial::computeFluidThermalConductivity()
{
    _k_fluid[_qp] = 0.0;

    if (!_compute_k_fluid)
        return;

    if (!_has_temperature)
    {
        _k_fluid[_qp] = 0.0;
        return;
    }

    _k_fluid[_qp] = *_k_fluid_in;
}

void
OrcaTHMaterial::computeSolidEffectiveThermalExpansionCoefficient()
{
    if (!_has_temperature)
    {
        _alpha_eff_T[_qp] = 0.0;
        return;
    }

    // lagged option: keep the previous value (stateful)
    if (_effective_thermal_expansion_model == "constant")
    {
        _alpha_eff_T[_qp] = _alpha_eff_T_old[_qp];
        return;
    }

    // user constant option
    if (_effective_thermal_expansion_model == "user")
    {
        _alpha_eff_T[_qp] = *_alpha_eff_user;
        return;
    }

    // computed: formulation from PorousFlowConstantThermalExpansionCoefficient
    // alpha_eff = (biot - phi)*beta_solid + phi*beta_fluid
    _alpha_eff_T[_qp] =
        (_biot[_qp] - _porosity[_qp]) * _drained_coeff[_qp] + _porosity[_qp] * _fluid_coeff[_qp];
}

void
OrcaTHMaterial::computeFluidThermalExpansionCoefficient()
{
    _alpha_fluid_T[_qp] = 0.0;

    if (!_compute_alpha_fluid_T)
        return;

    if (_has_temperature)
        _alpha_fluid_T[_qp] = _fluid_coeff[_qp];
}

// compute biot modulus
void
OrcaTHMaterial::computeBiotModulus()
{
    _biot_modulus_available[_qp] = 1.0;

    if (_solid_bulk_compliance_set)
        _solid_bulk_compliance[_qp] = _solid_bulk_compliance_in;

    else if (_bulk_modulus)
    {
        const ADReal Kd = (*_bulk_modulus)[_qp];
        if (MetaPhysicL::raw_value(Kd) <= 0.0)
        {
            _solid_bulk_compliance[_qp] = 0.0;
            _biot_modulus[_qp] = 0.0;
            _biot_modulus_available[_qp] = 0.0;
            return;
        }

        _solid_bulk_compliance[_qp] = ADReal(1.0) / Kd;
    }
    else
    {
        // Storage terms are unavailable unless either solid_bulk_compliance is provided
        // or a mechanics bulk_modulus material property exists.
        _solid_bulk_compliance[_qp] = 0.0;
        _biot_modulus[_qp] = 0.0;
        _biot_modulus_available[_qp] = 0.0;
        return;
    }

    const ADReal denom =
        (ADReal(1.0) - _biot[_qp]) * (_biot[_qp] - _porosity[_qp]) * _solid_bulk_compliance[_qp] +
        _porosity[_qp] / _Kf[_qp];

    const ADReal M_new = ADReal(1.0) / denom;

    if (_biot_modulus_model == "constant")
    {
        const Real Mold = _biot_modulus_old[_qp];
        _biot_modulus[_qp] = (Mold > 0.0) ? ADReal(Mold) : M_new;
    }
    else
        _biot_modulus[_qp] = M_new;
}
