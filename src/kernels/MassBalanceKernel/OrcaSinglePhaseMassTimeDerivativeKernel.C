#include "OrcaSinglePhaseMassTimeDerivativeKernel.h"
#include "MooseVariable.h"
#include "libmesh/quadrature.h"
#include <limits>
registerMooseObject("OrcaApp", OrcaSinglePhaseMassTimeDerivativeKernel);

InputParameters
OrcaSinglePhaseMassTimeDerivativeKernel::validParams()
{
  InputParameters params = ADTimeKernel::validParams();

  params.addParam<std::string>(
      "base_name",
      "For mechanically-coupled systems, this Kernel will depend on the volumetric strain.  "
      "base_name should almost always be the same base_name as given to the TensorMechanics object "
      "that computes strain.  Supplying a base_name to this Kernel but not defining an associated "
      "TensorMechanics strain calculator means that this Kernel will not depend on volumetric "
      "strain.  That could be useful when models contain solid mechanics that is not coupled to "
      "porous flow, for example");
  params.addParam<bool>(
      "multiply_by_fluid_density",
      true,
      "If true, then this Kernel represents the time derivative of the fluid mass.  If false, then "
      "this Kernel represents the time derivative of the fluid volume (care must then be taken "
      "when using other PorousFlow objects, such as the PorousFlowFluidMass postprocessor).");

  params.addClassDescription("Derivative of fluid-component mass with respect to time.");
  return params;
}

OrcaSinglePhaseMassTimeDerivativeKernel::OrcaSinglePhaseMassTimeDerivativeKernel(const InputParameters & parameters)
  : ADTimeKernel(parameters),
    _multiply_by_fluid_density(getParam<bool>("multiply_by_fluid_density")),
    _base_name(isParamValid("base_name") ? getParam<std::string>("base_name") + "_" : ""),
    _has_total_strain(hasMaterialProperty<RankTwoTensor>(_base_name + "total_strain")),
    _total_strain_old(_has_total_strain
                          ? &getMaterialPropertyOld<RankTwoTensor>(_base_name + "total_strain")
                          : nullptr),
    _porosity(getADMaterialProperty<Real>("porosity_qp")),
    _porosity_old(getMaterialPropertyOld<Real>("porosity_qp")),
    _fluid_density(_multiply_by_fluid_density ? &getADMaterialProperty<Real>(
                                              "fluid_density_qp")
                                        : nullptr),
    _fluid_density_old(_multiply_by_fluid_density ? &getMaterialPropertyOld<Real>(
                                                  "fluid_density_qp")
                                            : nullptr)
{
}

ADReal
OrcaSinglePhaseMassTimeDerivativeKernel::computeQpResidual()
{
  const ADReal dens = (_multiply_by_fluid_density ? (*_fluid_density)[_qp] : 1.0);
  const ADReal dens_old = (_multiply_by_fluid_density ? (*_fluid_density_old)[_qp] : 1.0);
  const ADReal strain = (_has_total_strain ? (*_total_strain_old)[_qp].trace() : 0.0);

  return _test[_i][_qp] * (1.0 + strain) * (_porosity[_qp] * dens - _porosity_old[_qp] * dens_old) /
         _dt;
}