#include "OrcaGravityVectorMaterial.h"

registerMooseObject("OrcaApp", OrcaGravityVectorMaterial);

InputParameters
OrcaGravityVectorMaterial::validParams()
{
  InputParameters params = ADMaterial::validParams();

  params.addClassDescription(
      "Declares a constant gravitational acceleration vector (m/s^2).");

  params.addRequiredParam<RealVectorValue>(
      "gravity",
      "Gravity vector '0 0 -9.81' (m/s^2).");

  return params;
}

OrcaGravityVectorMaterial::OrcaGravityVectorMaterial(const InputParameters & parameters)
  : ADMaterial(parameters),
    _gravity_input(getParam<RealVectorValue>("gravity")),
    _gravity(declareADProperty<RealVectorValue>("gravity_vector_qp"))
{
}

void
OrcaGravityVectorMaterial::initQpStatefulProperties()
{
  computeQpProperties();
}

void
OrcaGravityVectorMaterial::computeQpProperties()
{
  _gravity[_qp] = _gravity_input;
}