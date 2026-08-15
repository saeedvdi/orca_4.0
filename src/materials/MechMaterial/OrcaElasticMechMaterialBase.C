#include "OrcaElasticMechMaterialBase.h"

#include "MooseError.h"

#include <algorithm>
#include <cmath>

InputParameters
OrcaElasticMechMaterialBase::validParams()
{
  InputParameters params = ADMaterial::validParams();

  params.addClassDescription("Base class for isotropic elasticity tensor construction (AD).");

  // Elastic constants (any two independent constants)
  params.addParam<Real>("bulk_modulus", "Bulk modulus K (Pa).");
  params.addParam<Real>("lambda", "Lamé's first parameter λ (Pa).");
  params.addParam<Real>("poissons_ratio", "Poisson's ratio ν [-].");
  params.addParam<Real>("shear_modulus", "Shear modulus μ (Pa).");
  params.addParam<Real>("youngs_modulus", "Young's modulus E (Pa).");

  params.addParam<std::string>(
      "base_name",
      "",
      "Optional prefix for material property names (e.g., for multiple material systems).");

  return params;
}

OrcaElasticMechMaterialBase::OrcaElasticMechMaterialBase(const InputParameters & parameters)
  : ADMaterial(parameters),

    _base_name(isParamValid("base_name") && !getParam<std::string>("base_name").empty()
                 ? getParam<std::string>("base_name") + "_"
                 : ""),

    _bulk_modulus_set(parameters.isParamSetByUser("bulk_modulus")),
    _lambda_set(parameters.isParamSetByUser("lambda")),
    _poissons_ratio_set(parameters.isParamSetByUser("poissons_ratio")),
    _shear_modulus_set(parameters.isParamSetByUser("shear_modulus")),
    _youngs_modulus_set(parameters.isParamSetByUser("youngs_modulus")),

    _bulk_modulus_in(_bulk_modulus_set ? getParam<Real>("bulk_modulus") : 0.0),
    _lambda_in(_lambda_set ? getParam<Real>("lambda") : 0.0),
    _poissons_ratio_in(_poissons_ratio_set ? getParam<Real>("poissons_ratio") : 0.0),
    _shear_modulus_in(_shear_modulus_set ? getParam<Real>("shear_modulus") : 0.0),
    _youngs_modulus_in(_youngs_modulus_set ? getParam<Real>("youngs_modulus") : 0.0),

    _Cijkl_name(_base_name + "Cijkl"),
    _K_name(_base_name + "bulk_modulus"),

    _Cijkl(declareADProperty<RankFourTensor>(_Cijkl_name)),
    _K(declareADProperty<Real>(_K_name))
{
  // Basic param checks (only when user provided them)
  if (_youngs_modulus_set && _youngs_modulus_in <= 0.0)
    paramError("youngs_modulus", "Young's modulus must be > 0.");
  if (_shear_modulus_set && _shear_modulus_in <= 0.0)
    paramError("shear_modulus", "Shear modulus must be > 0.");
  if (_bulk_modulus_set && _bulk_modulus_in <= 0.0)
    paramError("bulk_modulus", "Bulk modulus must be > 0.");

  if (_poissons_ratio_set)
  {
    const Real nu = _poissons_ratio_in;
    if (nu <= -1.0 || nu >= 0.5)
      paramError("poissons_ratio", "Poisson's ratio must satisfy -1 < nu < 0.5.");
  }
}

void
OrcaElasticMechMaterialBase::initialSetup()
{
  ADMaterial::initialSetup();
  elasticConstantsInputCheck();
  buildIsotropicTensor();
}

void
OrcaElasticMechMaterialBase::computeQpProperties()
{
  // Expose tensor + K as QP properties
  _Cijkl[_qp] = _Cijkl_cache;

  // K is computed consistently even if user did not provide it explicitly
  // For isotropic: K = lambda + 2/3 mu
  const auto lame = computeLameParameters();
  const Real lambda = lame.first;
  const Real mu = lame.second;
  const Real K = lambda + (2.0 / 3.0) * mu;

  _K[_qp] = K;
}

void
OrcaElasticMechMaterialBase::elasticConstantsInputCheck() const
{
  const unsigned int n =
      _bulk_modulus_set + _lambda_set + _poissons_ratio_set + _shear_modulus_set + _youngs_modulus_set;

  if (n < 2)
    mooseError("Provide at least two independent elastic constants (e.g., E and nu).");

  // If user provides >2 constants, enforce mutual consistency with isotropic elasticity
  if (n > 2)
  {
    const auto lame_ref = computeLameParameters();
    const Real lambda_ref = lame_ref.first;
    const Real mu_ref = lame_ref.second;

    auto close = [](Real a, Real b) -> bool
    {
      const Real denom = std::max(std::max(std::abs(a), std::abs(b)), Real(1.0));
      return std::abs(a - b) / denom < 1e-10;
    };

    auto check_pair = [&](Real lambda_c, Real mu_c, const std::string & label)
    {
      if (!close(lambda_c, lambda_ref) || !close(mu_c, mu_ref))
        mooseError("Elastic constants are over-specified and inconsistent. The combination implied by ",
                   label,
                   " does not match the combination used internally. "
                   "Provide only two constants, or provide a mutually consistent set.");
    };

    if (_youngs_modulus_set && _poissons_ratio_set)
    {
      const Real nu = _poissons_ratio_in;
      const Real mu = _youngs_modulus_in / (2.0 * (1.0 + nu));
      const Real lambda = 2.0 * mu * nu / (1.0 - 2.0 * nu);
      check_pair(lambda, mu, "E+nu");
    }

    if (_lambda_set && _shear_modulus_set)
      check_pair(_lambda_in, _shear_modulus_in, "lambda+mu");

    if (_bulk_modulus_set && _shear_modulus_set)
      check_pair(_bulk_modulus_in - 2.0 / 3.0 * _shear_modulus_in, _shear_modulus_in, "K+mu");

    if (_bulk_modulus_set && _poissons_ratio_set)
    {
      const Real nu = _poissons_ratio_in;
      const Real mu = 3.0 * _bulk_modulus_in * (1.0 - 2.0 * nu) / (2.0 * (1.0 + nu));
      const Real lambda = 3.0 * _bulk_modulus_in * nu / (1.0 + nu);
      check_pair(lambda, mu, "K+nu");
    }

    if (_shear_modulus_set && _poissons_ratio_set)
    {
      const Real mu = _shear_modulus_in;
      const Real lambda = 2.0 * mu * _poissons_ratio_in / (1.0 - 2.0 * _poissons_ratio_in);
      check_pair(lambda, mu, "mu+nu");
    }

    mooseWarning("More than two elastic constants were provided. They appear consistent. "
                 "To avoid ambiguity, consider providing only two constants.");
  }
}

std::pair<Real, Real>
OrcaElasticMechMaterialBase::computeLameParameters() const
{
  if (_youngs_modulus_set && _poissons_ratio_set)
  {
    const Real nu = _poissons_ratio_in;
    const Real mu = _youngs_modulus_in / (2.0 * (1.0 + nu));
    const Real lambda = 2.0 * mu * nu / (1.0 - 2.0 * nu);
    return {lambda, mu};
  }

  if (_lambda_set && _shear_modulus_set)
    return {_lambda_in, _shear_modulus_in};

  if (_bulk_modulus_set && _shear_modulus_set)
    return {_bulk_modulus_in - 2.0 / 3.0 * _shear_modulus_in, _shear_modulus_in};

  if (_bulk_modulus_set && _poissons_ratio_set)
  {
    const Real nu = _poissons_ratio_in;
    const Real mu = 3.0 * _bulk_modulus_in * (1.0 - 2.0 * nu) / (2.0 * (1.0 + nu));
    const Real lambda = 3.0 * _bulk_modulus_in * nu / (1.0 + nu);
    return {lambda, mu};
  }

  if (_shear_modulus_set && _poissons_ratio_set)
  {
    const Real mu = _shear_modulus_in;
    const Real lambda = 2.0 * mu * _poissons_ratio_in / (1.0 - 2.0 * _poissons_ratio_in);
    return {lambda, mu};
  }

  mooseError("Unsupported elastic constants combination.");
  return {0.0, 0.0}; // not reached, but keeps compilers happy
}

void
OrcaElasticMechMaterialBase::buildIsotropicTensor()
{
  const auto lame = computeLameParameters();
  const Real lambda = lame.first;
  const Real mu = lame.second;

  _Cijkl_cache.fillGeneralIsotropic(lambda, mu, 0.0);
}