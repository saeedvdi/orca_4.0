#include "OrcaFractureDarcyVelocityComponent.h"

#include "Assembly.h"
#include "metaphysicl/raw_type.h"

registerMooseObject("OrcaApp", OrcaFractureDarcyVelocityComponent);

InputParameters
OrcaFractureDarcyVelocityComponent::validParams()
{
  InputParameters params = AuxKernel::validParams();
  params.addClassDescription(
      "A Cartesian component of the physical in-plane fracture Darcy velocity "
      "v_f = -(T/a_h)(I-n*n)grad(p), in m/s.");
  params.addRequiredCoupledVar("fluid_pressure", "The fluid pressure variable.");
  params.addRequiredRangeCheckedParam<unsigned int>(
      "component", "component >= 0 & component <= 2", "Cartesian component (0=x, 1=y, 2=z).");
  params.addParam<MaterialPropertyName>(
      "transmissivity", "fracture_transmissivity", "Fracture transmissivity material property.");
  params.addParam<MaterialPropertyName>(
      "hydraulic_aperture", "hydraulic_aperture", "Hydraulic aperture material property.");
  return params;
}

OrcaFractureDarcyVelocityComponent::OrcaFractureDarcyVelocityComponent(
    const InputParameters & parameters)
  : AuxKernel(parameters),
    _component(getParam<unsigned int>("component")),
    _grad_p(adCoupledGradient("fluid_pressure")),
    _transmissivity(getADMaterialProperty<Real>("transmissivity")),
    _aperture(getADMaterialProperty<Real>("hydraulic_aperture")),
    _normals(_assembly.normals())
{
  if (isNodal())
    paramError("variable", "OrcaFractureDarcyVelocityComponent requires an elemental AuxVariable.");
  if (!isParamValid("boundary"))
    paramError("boundary", "The fracture velocity must be restricted to a fracture boundary.");
}

Real
OrcaFractureDarcyVelocityComponent::computeValue()
{
  const ADRealVectorValue normal(_normals[_qp]);
  const ADRealVectorValue grad_t = _grad_p[_qp] - (_grad_p[_qp] * normal) * normal;
  const ADReal aperture = _aperture[_qp];

  if (MetaPhysicL::raw_value(aperture) <= 0.0)
    mooseError("OrcaFractureDarcyVelocityComponent received non-positive hydraulic aperture: ",
               MetaPhysicL::raw_value(aperture),
               ".");

  const ADRealVectorValue velocity = -(_transmissivity[_qp] / aperture) * grad_t;
  return MetaPhysicL::raw_value(velocity(_component));
}
