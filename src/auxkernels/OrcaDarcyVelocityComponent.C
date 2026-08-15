#include "OrcaDarcyVelocityComponent.h"

#include "metaphysicl/raw_type.h"

registerMooseObject("OrcaApp", OrcaDarcyVelocityComponent);

InputParameters
OrcaDarcyVelocityComponent::validParams()
{
  InputParameters params = AuxKernel::validParams();
  params.addClassDescription("A Cartesian component of the physical volumetric Darcy velocity "
                             "v = -(K/mu)(grad(p)-rho*g), in m/s.");
  params.addRequiredCoupledVar("fluid_pressure", "The fluid pressure variable.");
  params.addRequiredRangeCheckedParam<unsigned int>(
      "component", "component >= 0 & component <= 2", "Cartesian component (0=x, 1=y, 2=z).");
  return params;
}

OrcaDarcyVelocityComponent::OrcaDarcyVelocityComponent(const InputParameters & parameters)
  : AuxKernel(parameters),
    _component(getParam<unsigned int>("component")),
    _grad_p(adCoupledGradient("fluid_pressure")),
    _rho_f(getADMaterialProperty<Real>("fluid_density_qp")),
    _mobility(getADMaterialProperty<RealTensorValue>("fluid_mobility_tensor_qp")),
    _gravity(getADMaterialProperty<RealVectorValue>("gravity_vector_qp"))
{
  if (isNodal())
    paramError("variable", "OrcaDarcyVelocityComponent requires an elemental AuxVariable.");
}

Real
OrcaDarcyVelocityComponent::computeValue()
{
  const ADRealVectorValue driving_force = _grad_p[_qp] - _rho_f[_qp] * _gravity[_qp];
  const ADRealVectorValue velocity = -(_mobility[_qp] * driving_force);
  return MetaPhysicL::raw_value(velocity(_component));
}
