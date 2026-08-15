#include "OrcaSinglePhaseMassVolumetricExpansionKernel.h"
#include "MooseVariable.h"
#include "libmesh/quadrature.h"
#include <limits>

registerMooseObject("OrcaApp", OrcaSinglePhaseMassVolumetricExpansionKernel);

InputParameters
OrcaSinglePhaseMassVolumetricExpansionKernel::validParams()
{
  InputParameters params = ADTimeKernel::validParams();

  params.addParam<bool>(
      "multiply_by_fluid_density",
      true,
      "If true, then this Kernel represents the time derivative of the fluid mass.  If false, then "
      "this Kernel represents the time derivative of the fluid volume (care must then be taken "
      "when using other PorousFlow objects, such as the PorousFlowFluidMass postprocessor).");

  params.addClassDescription("Component_mass*rate_of_solid_volumetric_expansion.  This Kernel "
                             "lumps the component mass to the nodes.");
  return params;
}

OrcaSinglePhaseMassVolumetricExpansionKernel::OrcaSinglePhaseMassVolumetricExpansionKernel(const InputParameters & parameters)
  : ADTimeKernel(parameters),
    _multiply_by_fluid_density(getParam<bool>("multiply_by_fluid_density")),
    _vol_strain_rate(getADMaterialProperty<Real>("vol_strain_rate")),
    _porosity(getADMaterialProperty<Real>("porosity_qp")),
    _fluid_density(_multiply_by_fluid_density ? &getADMaterialProperty<Real>("fluid_density_qp"): nullptr)
{
}

ADReal
OrcaSinglePhaseMassVolumetricExpansionKernel::computeQpResidual()
{
  const ADReal dens = (_multiply_by_fluid_density ? (*_fluid_density)[_qp] : 1.0);

  return _test[_i][_qp] * dens * _porosity[_qp] * _vol_strain_rate[_qp];
}