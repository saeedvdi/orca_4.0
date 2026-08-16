#include "OrcaFullySaturatedSinglePhaseMassTimeDerivativeKernel.h"
#include "metaphysicl/raw_type.h"

registerADMooseObject("OrcaApp", OrcaFullySaturatedSinglePhaseMassTimeDerivativeKernel);

InputParameters
OrcaFullySaturatedSinglePhaseMassTimeDerivativeKernel::validParams()
{
  InputParameters params = ADTimeKernelValue::validParams();

  MooseEnum coupling_type("Hydro ThermoHydro HydroMechanical ThermoHydroMechanical", "Hydro");
  params.addParam<MooseEnum>("coupling_type",
                            coupling_type,
                            "Type of simulation coupling (Hydro/TH/HM/THM).");

  params.addParam<bool>("multiply_by_fluid_density",
                        true,
                        "If true, this Kernel returns the time derivative of fluid mass "
                        "(rho * storage). If false, it returns the derivative of fluid volume "
                        "(storage only).");

  params.addCoupledVar("temperature",
                       "Temperature variable (required for ThermoHydro / THM if using thermal term).");

  params.addClassDescription(
      "AD storage term for fully-saturated single-phase: "
      "(1/M) dp/dt - alpha_T dT/dt + alpha*eps_v_dot, optionally multiplied by density.");

  return params;
}

OrcaFullySaturatedSinglePhaseMassTimeDerivativeKernel::OrcaFullySaturatedSinglePhaseMassTimeDerivativeKernel(const InputParameters & parameters)
  : ADTimeKernelValue(parameters),
    _coupling_type(getParam<MooseEnum>("coupling_type").getEnum<CouplingTypeEnum>()),
    _includes_thermal(_coupling_type == CouplingTypeEnum::ThermoHydro ||
                      _coupling_type == CouplingTypeEnum::ThermoHydroMechanical),
    _includes_mechanical(_coupling_type == CouplingTypeEnum::HydroMechanical ||
                         _coupling_type == CouplingTypeEnum::ThermoHydroMechanical),
    _multiply_by_fluid_density(getParam<bool>("multiply_by_fluid_density")),

    // biot_modulus_qp holds M itself, NOT 1/M. OrcaTHMaterial::computeBiotModulus
    // builds the compliance 1/M = (1-a)(a-phi)/Kd + phi/Kf and then stores its
    // reciprocal, so the storage term below must DIVIDE by this property.
    // Verified by test/tests/materials/biot_modulus.
    _biot_modulus(getADMaterialProperty<Real>("biot_modulus_qp")),
    _biot_modulus_available(hasMaterialProperty<Real>("biot_modulus_available_qp")
                                ? &getMaterialProperty<Real>("biot_modulus_available_qp")
                                : nullptr),
    _biot(getADMaterialProperty<Real>("biot_coefficient_qp")),

    _alpha_eff_T(_includes_thermal
                   ? &getADMaterialProperty<Real>("effective_thermal_expansion_coeff_qp")
                   : nullptr),
    _epsv_dot(_includes_mechanical
                ? &getADMaterialProperty<Real>("vol_strain_rate")
                : nullptr),
    _rho(_multiply_by_fluid_density
           ? &getADMaterialProperty<Real>("fluid_density_qp")
           : nullptr),

    _T_dot(_includes_thermal ? &adCoupledDot("temperature") : nullptr),

    // diagnostic breakdown (member variables)
    _storage_rate_p(0.0),
    _storage_rate_thermal(0.0),
    _storage_rate_mech(0.0)
{
  if (_includes_thermal && !isCoupled("temperature"))
    paramError("temperature",
               "temperature must be coupled for ThermoHydro or ThermoHydroMechanical.");
}

ADReal
OrcaFullySaturatedSinglePhaseMassTimeDerivativeKernel::precomputeQpResidual()
{
  if (_biot_modulus_available && (*_biot_modulus_available)[_qp] < 0.5)
    mooseError("OrcaFullySaturatedSinglePhaseMassTimeDerivativeKernel requires a valid storage source in "
               "OrcaTHMaterial: set solid_bulk_compliance or provide a positive mechanics "
               "bulk_modulus property.");

  if (MetaPhysicL::raw_value(_biot_modulus[_qp]) <= 0.0)
    mooseError("biot_modulus_qp must be > 0 when OrcaFullySaturatedSinglePhaseMassTimeDerivativeKernel is used. "
               "Check solid_bulk_compliance and bulk_modulus setup.");

  // reset diagnostic pieces
  _storage_rate_p = 0.0;
  _storage_rate_thermal = 0.0;
  _storage_rate_mech = 0.0;

  // dp/dt (pressure is the kernel variable)
  const ADReal dpdt = _u_dot[_qp];

  // Pressure storage contribution (1/M) dp/dt. Written as an explicit division:
  // the previous form `dpdt * 1/_biot_modulus[_qp]` evaluates identically (it is
  // (dpdt*1)/M by left-associativity) but reads like a multiplication, which is
  // the wrong operation for a property holding M. Locked by
  // test/tests/kernels/mass_storage, which checks p(t) = M q t against a
  // closed-form solution -- a flipped operator lands a factor M^2 ~ 1e22 out.
  _storage_rate_p = dpdt / _biot_modulus[_qp];

  // thermal storage coupling: - alpha_T dT/dt
  if (_includes_thermal)
    _storage_rate_thermal = -(*_alpha_eff_T)[_qp] * (*_T_dot)[_qp];

  // mechanical coupling: + alpha * eps_v_dot
  if (_includes_mechanical)
    _storage_rate_mech = _biot[_qp] * (*_epsv_dot)[_qp];

  // total (volumetric form)
  ADReal storage_rate_total = _storage_rate_p + _storage_rate_thermal + _storage_rate_mech;

  // optional rho multiplier (mass form)
  if (_multiply_by_fluid_density)
    storage_rate_total *= (*_rho)[_qp];

  return storage_rate_total;
}
