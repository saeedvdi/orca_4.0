#include "OrcaCZMComputeDisplacementJump.h"
#include "OrcaCZMTools.h"
#include "RotationMatrix.h"

registerMooseObject("OrcaApp", OrcaCZMComputeDisplacementJump);

InputParameters
OrcaCZMComputeDisplacementJump::validParams()
{
  InputParameters params = InterfaceMaterial::validParams();
  params.addClassDescription("Class used to compute the displacement jump across a czm "
                             "interface in local coordinates for small strain kinematic formulation");

  params.addRequiredCoupledVar("displacements",
                               "The string of displacements suitable for the problem statement");
  params.suppressParameter<bool>("use_displaced_mesh");
  params.addParam<std::string>("base_name", "Material property base name");

  return params;
}

OrcaCZMComputeDisplacementJump::OrcaCZMComputeDisplacementJump(
    const InputParameters & parameters)
  : InterfaceMaterial(parameters),
    _base_name(isParamValid("base_name") && !getParam<std::string>("base_name").empty()
                   ? getParam<std::string>("base_name") + "_"
                   : ""),
    _ndisp(coupledComponents("displacements")),
    _disp(3),
    _disp_neighbor(3),
    _displacement_jump_global(declareADProperty<RealVectorValue>(_base_name + "displacement_jump_global")),
    _interface_displacement_jump(declareADProperty<RealVectorValue>(_base_name +"interface_displacement_jump")),
    _czm_total_rotation(declareADProperty<RankTwoTensor>(_base_name + "czm_total_rotation"))
{
  // Enforce consistency
  if (_ndisp != _mesh.dimension())
    paramError("displacements", "Number of displacements must match problem dimension.");

  if (_ndisp > 3 || _ndisp < 1)
    mooseError("the CZM material requires 1, 2 or 3 displacement variables");

  // initializing the displacement vectors
  for (unsigned int i = 0; i < _ndisp; ++i)
  {
    _disp[i] = &coupledGenericValue<true>("displacements", i);
    _disp_neighbor[i] = &coupledGenericNeighborValue<true>("displacements", i);
  }

  // All others zero (so this will work naturally for 2D and 1D problems)
  for (unsigned int i = _ndisp; i < 3; i++)
  {
    _disp[i] = &_ad_zero;
    _disp_neighbor[i] = &_ad_zero;
  }
}


void
OrcaCZMComputeDisplacementJump::initQpStatefulProperties()
{
  // requried to promote _interface_displacement_jump to stateful in case someone needs it
  _interface_displacement_jump[_qp] = 0;
}


void
OrcaCZMComputeDisplacementJump::computeQpProperties()
{
  // computing the displacement jump
  for (unsigned int i = 0; i < _ndisp; i++)
    _displacement_jump_global[_qp](i) = (*_disp_neighbor[i])[_qp] - (*_disp[i])[_qp];
  for (unsigned int i = _ndisp; i < 3; i++)
    _displacement_jump_global[_qp](i) = 0;

  computeRotationMatrices();
  computeLocalDisplacementJump();
}


void
OrcaCZMComputeDisplacementJump::computeRotationMatrices()
{
  _czm_total_rotation[_qp] =
      OrcaCZMTools::computeReferenceRotation(_normals[_qp], _mesh.dimension());
}

void
OrcaCZMComputeDisplacementJump::computeLocalDisplacementJump()
{
  // Small-strain CZM kinematics: rotate global displacement jump into interface coordinates.
  _interface_displacement_jump[_qp] =
      _czm_total_rotation[_qp].transpose() * _displacement_jump_global[_qp];
}