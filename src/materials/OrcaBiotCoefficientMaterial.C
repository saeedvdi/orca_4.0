#include "OrcaBiotCoefficientMaterial.h"

#include "MooseError.h"
#include "metaphysicl/raw_type.h"

registerMooseObject("OrcaApp", OrcaBiotCoefficientMaterial);

InputParameters
OrcaBiotCoefficientMaterial::validParams()
{
    InputParameters params = ADMaterial::validParams();
    params.addClassDescription("Biot coefficient alpha: user-provided or computed as 1 - Kd/Ks.");

    params.addParam<MooseEnum>(
        "model",
        MooseEnum("user from_elasticity", "user"),
        "user: alpha from input; from_elasticity: alpha = 1 - Kd/Ks using isotropic Cijkl.");

    params.addRangeCheckedParam<Real>(
        "biot_coefficient",
        1.0,
        "biot_coefficient > 0 & biot_coefficient <= 1.0",
        "User-provided Biot coefficient (used when model=user).");

    // Only used when model=from_elasticity (QP only)
    params.addParam<MaterialPropertyName>(
        "elasticity_tensor",
        "elasticity_tensor",
        "AD RankFourTensor drained stiffness property name Cijkl (used when model=from_elasticity).");

    params.addParam<MaterialPropertyName>(
        "grain_bulk_modulus_property",
        "grain_bulk_modulus",
        "AD Real grain bulk modulus property name Ks (used when model=from_elasticity).");

    params.addParam<bool>(
        "clamp_to_unit_interval",
        true,
        "Clamp alpha into [0,1] (recommended).");

    return params;
}

OrcaBiotCoefficientMaterial::OrcaBiotCoefficientMaterial(const InputParameters & parameters)
    : ADMaterial(parameters),
    _model(getParam<MooseEnum>("model")),
    _alpha_user(getParam<Real>("biot_coefficient")),
    _clamp(getParam<bool>("clamp_to_unit_interval")),

    // Only set if model=from_elasticity
    _Cijkl(nullptr),
    _Ks(nullptr),

    // Hard-wired OUTPUT property name (qp vs nodal)
    _biot(declareADProperty<Real>("biot_coefficient_qp"))
{
    if (_model == "from_elasticity")
    {
        _Cijkl = &getADMaterialProperty<RankFourTensor>(getParam<MaterialPropertyName>("elasticity_tensor"));
        _Ks    = &getADMaterialProperty<Real>(getParam<MaterialPropertyName>("grain_bulk_modulus_property"));
    }
}

void
OrcaBiotCoefficientMaterial::initQpStatefulProperties()
{
    computeQpProperties();
}

void
OrcaBiotCoefficientMaterial::computeQpProperties()
{
    ADReal alpha = ADReal(_alpha_user);

    if (_model == "from_elasticity")
    {
        // isotropic extraction: lambda = C0011, mu = C0101
        const ADReal lambda = (*_Cijkl)[_qp](0, 0, 1, 1);
        const ADReal mu     = (*_Cijkl)[_qp](0, 1, 0, 1);

        const ADReal Kd = lambda + (2.0 / 3.0) * mu; // drained bulk modulus
        alpha = ADReal(1.0) - Kd / (*_Ks)[_qp];
    }

    // Note: clamping is a non-smooth operation; for AD this is inherently piecewise.
    if (_clamp)
    {
        const Real a = MetaPhysicL::raw_value(alpha);
        if (a < 0.0)
        alpha = ADReal(0.0);
        else if (a > 1.0)
        alpha = ADReal(1.0);
    }
    else
    {
        const Real a = MetaPhysicL::raw_value(alpha);
        if (a <= 0.0 || a > 1.0)
        mooseError("Biot coefficient alpha=", a, " is outside (0,1].");
    }

    _biot[_qp] = alpha;
}