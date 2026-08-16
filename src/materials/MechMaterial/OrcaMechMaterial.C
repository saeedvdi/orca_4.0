#include "OrcaMechMaterial.h"

#include "Assembly.h"
#include "Function.h"
#include "MooseError.h"
#include "MooseMesh.h"

registerMooseObject("OrcaApp", OrcaMechMaterial);

InputParameters
OrcaMechMaterial::validParams()
{
  InputParameters params = OrcaElasticMechMaterialBase::validParams();
  params.addRequiredCoupledVar(
      "displacements",
      "The displacements appropriate for the simulation geometry and coordinate system.");

  MooseEnum strain_model("total=0 incremental=1", "incremental");
  params.addParam<MooseEnum>("strain_model", strain_model, "Strain model: incremental or total.");

  params.addParam<bool>(
      "volumetric_locking_correction", false, "Flag to correct volumetric locking.");
  params.addParam<std::vector<MaterialPropertyName>>(
      "eigenstrain_names", {}, "List of eigenstrains to be applied in this strain calculation.");
  params.addParam<std::vector<FunctionName>>(
      "initial_stress",
      {},
      "Initial Cauchy stress components as functions. Provide 3 (2D: xx, yy, xy) or "
      "6 (3D: xx, yy, zz, xy, xz, yz). Negative in compression.");
  params.addParam<MaterialPropertyName>(
      "global_strain",
      "",
      "Optional material property holding a global strain tensor applied to the mesh as a whole.");


  // Optional thermal expansion eigenstrain (isotropic)
  params.addCoupledVar("temperature", "Temperature (K). Optional.");
  params.addCoupledVar(
      "stress_free_temperature",
      "Reference temperature at which there is no thermal expansion (K). "
      "Required when temperature is coupled.");
  params.addParam<bool>(
      "use_old_temperature",
      false,
      "If true, use the old temperature value when forming thermal eigenstrain.");
  params.addParam<MaterialPropertyName>(
      "thermal_eigenstrain_name",
      "thermal_eigenstrain",
      "Base name for the thermal eigenstrain property.");
  params.addParam<bool>(
      "compute_thermal_eigenstrain",
      false,
      "If true and temperature is coupled, compute and apply thermal eigenstrain.");

  params.set<bool>("use_displaced_mesh") = false;
  params.suppressParameter<bool>("use_displaced_mesh");

  return params;
}

OrcaMechMaterial::OrcaMechMaterial(const InputParameters & parameters)
  : OrcaElasticMechMaterialBase(parameters),
    // main variable, displacement
    _ndisp(coupledComponents("displacements")),
    _grad_disp(3),
    _grad_disp_old(3),
    _num_ini_stress(0),
    _initial_stress(),
    _strain_model(getParam<MooseEnum>("strain_model")),
    // TM coupling (optional)
    _has_temperature(isCoupled("temperature")),
    _has_stress_free_temperature(isCoupled("stress_free_temperature")),
    _temperature(_has_temperature ? &adCoupledValue("temperature") : nullptr),
    _temperature_old((_has_temperature && _fe_problem.isTransient()) ? &coupledValueOld("temperature")
                                                                    : nullptr),
    _stress_free_temperature(_has_stress_free_temperature ? &adCoupledValue("stress_free_temperature")
                                                          : nullptr),
    _use_old_temperature(getParam<bool>("use_old_temperature")),
    _compute_thermal_eigenstrain(getParam<bool>("compute_thermal_eigenstrain")),
    _thermal_expansion_coeff(nullptr),
    _thermal_eigenstrain_prop_name(_base_name +
                                   getParam<MaterialPropertyName>("thermal_eigenstrain_name")),
    _ad_zero_grad(ADRealGradient(0.0, 0.0, 0.0)),
    _zero_grad(RealGradient(0.0, 0.0, 0.0)),
    _mechanical_strain(declareADProperty<RankTwoTensor>(_base_name + "mechanical_strain")),
    _mechanical_strain_old(getMaterialPropertyOld<RankTwoTensor>(_base_name + "mechanical_strain")),
    _total_strain(declareADProperty<RankTwoTensor>(_base_name + "total_strain")),
    _total_strain_old(getMaterialPropertyOld<RankTwoTensor>(_base_name + "total_strain")),
    _strain_rate(declareADProperty<RankTwoTensor>(_base_name + "strain_rate")),
    _strain_increment(declareADProperty<RankTwoTensor>(_base_name + "strain_increment")),
    _rotation_increment(declareADProperty<RankTwoTensor>(_base_name + "rotation_increment")),
    _vol_total_strain_qp(declareADProperty<Real>(_base_name + "vol_total_strain")),
    _vol_strain_rate_qp(declareADProperty<Real>(_base_name + "vol_strain_rate")),
    _thermal_eigenstrain(declareADProperty<RankTwoTensor>(_thermal_eigenstrain_prop_name)),
    _thermal_eigenstrain_old(getMaterialPropertyOld<RankTwoTensor>(_thermal_eigenstrain_prop_name)),
    _eigenstrain_names(getParam<std::vector<MaterialPropertyName>>("eigenstrain_names")),
    _eigenstrains(_eigenstrain_names.size()),
    _eigenstrains_old(_eigenstrain_names.size()),
    _global_strain(nullptr),
    _volumetric_locking_correction(getParam<bool>("volumetric_locking_correction") &&
                                   !this->isBoundaryMaterial()),
    _elem_vol_strain_accum(0.0),
    _elem_vol_JxW_accum(0.0),
    _elasticity_tensor(getADMaterialProperty<RankFourTensor>(_base_name + "Cijkl")),
    _stress_name(_base_name + "stress"),
    _stress(declareADProperty<RankTwoTensor>(_stress_name)),
    _initial_stress_tensor(declareADProperty<RankTwoTensor>(_base_name + "initial_stress")),
    _elastic_strain(declareADProperty<RankTwoTensor>(_base_name + "elastic_strain"))
{
  if (_ndisp == 1 && _volumetric_locking_correction)
    paramError("volumetric_locking_correction", "has to be set to false for 1-D problems.");

  const auto & global_strain_name = getParam<MaterialPropertyName>("global_strain");
  if (!global_strain_name.empty())
    _global_strain = &getADMaterialProperty<RankTwoTensor>(global_strain_name);

  for (unsigned int i = 0; i < _eigenstrains.size(); ++i)
  {
    const MaterialPropertyName full_name = _base_name + _eigenstrain_names[i];
    _eigenstrains[i] = &getADMaterialProperty<RankTwoTensor>(full_name);
    _eigenstrains_old[i] = &getMaterialPropertyOld<RankTwoTensor>(full_name);
  }


  if (_compute_thermal_eigenstrain && !_has_temperature)
    paramError("temperature", "compute_thermal_eigenstrain=true requires temperature coupling.");

  if (_use_old_temperature && !_fe_problem.isTransient())
    paramError(
        "use_old_temperature",
        "The old state of the temperature variable is only available in a transient simulation.");

  if (_has_temperature && !_has_stress_free_temperature)
    paramError("stress_free_temperature",
               "temperature is coupled, but stress_free_temperature is not.");

  if (_compute_thermal_eigenstrain)
  {
    const auto coeff_name = std::string("effective_thermal_expansion_coeff_qp");
    if (!hasADMaterialProperty<Real>(coeff_name))
      paramError("compute_thermal_eigenstrain",
                 "Thermal eigenstrain requires material property '",
                 coeff_name,
                 "'.");
    _thermal_expansion_coeff = &getADMaterialProperty<Real>(coeff_name);
  }
}

void
OrcaMechMaterial::initialSetup()
{
  OrcaElasticMechMaterialBase::initialSetup();
  displacementIntegrityCheck();

  for (unsigned int i = 0; i < _ndisp; ++i)
    _grad_disp[i] = &adCoupledGradient("displacements", i);

  for (unsigned int i = _ndisp; i < 3; ++i)
    _grad_disp[i] = nullptr;

  const auto names = getParam<std::vector<FunctionName>>("initial_stress");
  _num_ini_stress = names.size();
  if (_num_ini_stress != 0 && _num_ini_stress != 3 && _num_ini_stress != 6)
    paramError("initial_stress", "Provide either 3 or 6 initial stress components.");

  _initial_stress.resize(_num_ini_stress, nullptr);
  for (unsigned int i = 0; i < _num_ini_stress; ++i)
    _initial_stress[i] = &getFunctionByName(names[i]);

  if (_strain_model == "incremental")
  {
    for (unsigned int i = 0; i < 3; ++i)
    {
      if (_fe_problem.isTransient() && i < _ndisp)
        _grad_disp_old[i] = &coupledGradientOld("displacements", i);
      else
        _grad_disp_old[i] = nullptr;
    }
  }
  else
  {
    for (unsigned int i = 0; i < 3; ++i)
      _grad_disp_old[i] = nullptr;
  }
}

void
OrcaMechMaterial::displacementIntegrityCheck()
{
  if (_ndisp != _mesh.dimension())
    paramError(
        "displacements",
        "The number of variables supplied in 'displacements' must match the mesh dimension.");
}

void
OrcaMechMaterial::initQpStatefulProperties()
{
  _mechanical_strain[_qp].zero();
  _total_strain[_qp].zero();
  _strain_rate[_qp].zero();
  _strain_increment[_qp].zero();
  _rotation_increment[_qp].setToIdentity();
  _stress[_qp].zero();
  _initial_stress_tensor[_qp].zero();
  _elastic_strain[_qp].zero();
  _vol_total_strain_qp[_qp] = 0.0;
  _vol_strain_rate_qp[_qp] = 0.0;
  _thermal_eigenstrain[_qp].zero();
}

void
OrcaMechMaterial::computeQpProperties()
{
  OrcaElasticMechMaterialBase::computeQpProperties();
  _thermal_eigenstrain[_qp].zero();

  if (_compute_thermal_eigenstrain)
  {
    const ADReal T_cur =
        (_use_old_temperature && _temperature_old) ? ADReal((*_temperature_old)[_qp])
                                                   : (*_temperature)[_qp];
    const ADReal T_ref =
        _stress_free_temperature ? (*_stress_free_temperature)[_qp] : ADReal(0.0);

    const ADReal thermal_strain = (*_thermal_expansion_coeff)[_qp] * (T_cur - T_ref);
    _thermal_eigenstrain[_qp].addIa(thermal_strain);
  }

  if (_strain_model == "incremental")
    computeIncrementalStrain();
  else
    computeTotalSmallStrain();

  computeInitialStressTensor();
  computeLinearElasticStress();
}

void
OrcaMechMaterial::computeProperties()
{
  _elem_vol_strain_accum = 0.0;
  _elem_vol_JxW_accum = 0.0;

  Material::computeProperties();

  if (_volumetric_locking_correction && _elem_vol_JxW_accum > 0.0)
  {
    const unsigned int n_qp = _qrule->n_points();
    const ADReal avg_vol_strain = _elem_vol_strain_accum / _elem_vol_JxW_accum;

    for (unsigned int qp = 0; qp < n_qp; ++qp)
    {
      const ADReal correction = (avg_vol_strain - _total_strain[qp].trace()) / 3.0;
      _total_strain[qp].addIa(correction);

      _mechanical_strain[qp] = _total_strain[qp];
      for (const auto * es : _eigenstrains)
        _mechanical_strain[qp] -= (*es)[qp];
      if (_compute_thermal_eigenstrain)
        _mechanical_strain[qp] -= _thermal_eigenstrain[qp];

      _stress[qp] = (_elasticity_tensor[qp] * _mechanical_strain[qp]) + _initial_stress_tensor[qp];
      _elastic_strain[qp] = _mechanical_strain[qp];

      _vol_total_strain_qp[qp] = _total_strain[qp].trace();
      if (_dt > 0.0)
        _vol_strain_rate_qp[qp] =
            (_vol_total_strain_qp[qp] - _total_strain_old[qp].trace()) / _dt;
      else
        _vol_strain_rate_qp[qp] = 0.0;
    }
  }
}

void
OrcaMechMaterial::computeInitialStressTensor()
{
  _initial_stress_tensor[_qp].zero();

  if (_num_ini_stress == 0)
    return;

  std::vector<Real> init_values(_num_ini_stress, 0.0);
  for (unsigned int i = 0; i < _num_ini_stress; ++i)
    init_values[i] = _initial_stress[i]->value(_t, _q_point[_qp]);

  RankTwoTensor init_tensor;
  init_tensor.fillFromInputVector(init_values);
  _initial_stress_tensor[_qp] = init_tensor;
}

void
OrcaMechMaterial::computeTotalSmallStrain()
{
  const ADRealGradient & g0 = (_ndisp > 0 && _grad_disp[0]) ? (*_grad_disp[0])[_qp]
                                                           : _ad_zero_grad;
  const ADRealGradient & g1 = (_ndisp > 1 && _grad_disp[1]) ? (*_grad_disp[1])[_qp]
                                                           : _ad_zero_grad;
  const ADRealGradient & g2 = (_ndisp > 2 && _grad_disp[2]) ? (*_grad_disp[2])[_qp]
                                                           : _ad_zero_grad;

  const ADRankTwoTensor grad_tensor = ADRankTwoTensor::initializeFromRows(g0, g1, g2);
  _total_strain[_qp] = 0.5 * (grad_tensor + grad_tensor.transpose());

  if (_volumetric_locking_correction)
  {
    _elem_vol_strain_accum += _total_strain[_qp].trace() * _JxW[_qp] * _coord[_qp];
    _elem_vol_JxW_accum += _JxW[_qp] * _coord[_qp];
  }

  if (_global_strain)
    _total_strain[_qp] += (*_global_strain)[_qp];

  _mechanical_strain[_qp] = _total_strain[_qp];

  for (const auto * es : _eigenstrains)
    _mechanical_strain[_qp] -= (*es)[_qp];

  if (_compute_thermal_eigenstrain)
    _mechanical_strain[_qp] -= _thermal_eigenstrain[_qp];

  // Must be called on BOTH strain paths. computeIncrementalStrain() calls it;
  // this branch previously did not, so with strain_model = total the property
  // vol_strain_rate stayed at the 0.0 set in initQpStatefulProperties. Any
  // HydroMechanical mass kernel then silently lost its alpha * div(du/dt)
  // coupling -- the run completed and looked plausible, but the poroelastic
  // coupling was absent. Covered by test/tests/verification/terzaghi
  // (total_strain case).
  computeVolumetricStrain();
}

void
OrcaMechMaterial::computeIncrementalStrain()
{
  ADRankTwoTensor total_strain_increment;
  computeTotalStrainIncrement(total_strain_increment);

  _strain_increment[_qp] = total_strain_increment;

  if (_volumetric_locking_correction)
  {
    _elem_vol_strain_accum += total_strain_increment.trace() * _JxW[_qp] * _coord[_qp];
    _elem_vol_JxW_accum += _JxW[_qp] * _coord[_qp];
  }

  const ADRankTwoTensor total_old(_total_strain_old[_qp]);
  _total_strain[_qp] = total_old + _strain_increment[_qp];

  subtractEigenstrainIncrementFromStrain(_strain_increment[_qp]);

  if (_dt > 0.0)
    _strain_rate[_qp] = _strain_increment[_qp] / _dt;
  else
    _strain_rate[_qp].zero();

  const ADRankTwoTensor mech_old(_mechanical_strain_old[_qp]);
  _mechanical_strain[_qp] = mech_old + _strain_increment[_qp];

  _rotation_increment[_qp].setToIdentity();

  computeVolumetricStrain();
}

void
OrcaMechMaterial::computeTotalStrainIncrement(ADRankTwoTensor & total_strain_increment) const
{
  const ADRealGradient & g0 = (_ndisp > 0 && _grad_disp[0]) ? (*_grad_disp[0])[_qp]
                                                           : _ad_zero_grad;
  const ADRealGradient & g1 = (_ndisp > 1 && _grad_disp[1]) ? (*_grad_disp[1])[_qp]
                                                           : _ad_zero_grad;
  const ADRealGradient & g2 = (_ndisp > 2 && _grad_disp[2]) ? (*_grad_disp[2])[_qp]
                                                           : _ad_zero_grad;

  const RealGradient & g0_old = (_grad_disp_old[0]) ? (*_grad_disp_old[0])[_qp] : _zero_grad;
  const RealGradient & g1_old =
      (_ndisp > 1 && _grad_disp_old[1]) ? (*_grad_disp_old[1])[_qp] : _zero_grad;
  const RealGradient & g2_old =
      (_ndisp > 2 && _grad_disp_old[2]) ? (*_grad_disp_old[2])[_qp] : _zero_grad;

  const ADRankTwoTensor grad_tensor = ADRankTwoTensor::initializeFromRows(g0, g1, g2);
  const RankTwoTensor grad_tensor_old = RankTwoTensor::initializeFromRows(g0_old, g1_old, g2_old);

  const ADRankTwoTensor A = grad_tensor - ADRankTwoTensor(grad_tensor_old);
  total_strain_increment = 0.5 * (A + A.transpose());
}

void
OrcaMechMaterial::subtractEigenstrainIncrementFromStrain(ADRankTwoTensor & strain) const
{
  for (unsigned int i = 0; i < _eigenstrains.size(); ++i)
  {
    strain -= (*_eigenstrains[i])[_qp];
    strain += (*_eigenstrains_old[i])[_qp];
  }

  if (_compute_thermal_eigenstrain)
  {
    strain -= _thermal_eigenstrain[_qp];
    strain += _thermal_eigenstrain_old[_qp];
  }
}

void
OrcaMechMaterial::computeLinearElasticStress()
{
  _stress[_qp] = (_elasticity_tensor[_qp] * _mechanical_strain[_qp]) + _initial_stress_tensor[_qp];
  _elastic_strain[_qp] = _mechanical_strain[_qp];
}

void
OrcaMechMaterial::computeVolumetricStrain()
{
  _vol_total_strain_qp[_qp] = _total_strain[_qp].trace();
  if (_dt > 0.0)
    _vol_strain_rate_qp[_qp] =
        (_vol_total_strain_qp[_qp] - _total_strain_old[_qp].trace()) / _dt;
  else
    _vol_strain_rate_qp[_qp] = 0.0;
}
