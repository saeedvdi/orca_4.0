#include "OrcaPoroMechKernel.h"
#include "RankTwoTensor.h"
#include "SymmetricRankTwoTensor.h"
#include "libmesh/quadrature.h"

registerMooseObject("OrcaApp", OrcaPoroMechKernel);

InputParameters
OrcaPoroMechKernel::validParams()
{
  InputParameters params = ADKernel::validParams();
  params.addClassDescription("Stress divergence kernel with optional biot_coefficient * "
                             "grad(effective fluid pressure) and automatic differentiation for the "
                             "Cartesian coordinate system");

  params.addRequiredParam<unsigned int>("component",
                                        "An integer corresponding to the direction "
                                        "the variable this kernel acts in. (0 for x, "
                                        "1 for y, 2 for z)");
  params.addRequiredCoupledVar("displacements",
                               "The string of displacements suitable for the problem statement");
  
  params.addCoupledVar("pore_pressure",
                       "Pore pressure variable p (Pa). If coupled, adds -alpha*p*I term.");

  params.addParam<std::string>("base_name", "Material property base name");
  params.addCoupledVar("out_of_plane_strain",
                       "The name of the out_of_plane_strain variable used in the "
                       "WeakPlaneStress kernel.");
  params.set<bool>("use_displaced_mesh") = false;
  params.addParam<bool>("volumetric_locking_correction",
                        false,
                        "Set to false to turn off volumetric locking correction");
  return params;
}

OrcaPoroMechKernel::OrcaPoroMechKernel(
    const InputParameters & parameters)
  : ADKernel(parameters),
    _base_name(isParamValid("base_name") ? getParam<std::string>("base_name") + "_" : ""),
    _stress(getADMaterialProperty<RankTwoTensor>(_base_name + "stress")),
    _component(getParam<unsigned int>("component")),
    _ndisp(coupledComponents("displacements")),
    _disp_var(_ndisp),
    _avg_grad_test(),
    _out_of_plane_strain_coupled(isCoupled("out_of_plane_strain")),
    _out_of_plane_strain(_out_of_plane_strain_coupled ? &adCoupledValue("out_of_plane_strain")
                                                      : nullptr),
    _volumetric_locking_correction(getParam<bool>("volumetric_locking_correction")),
    _has_pf(isCoupled("pore_pressure")),
    _pf(isCoupled("pore_pressure") ? &adCoupledValue("pore_pressure"): nullptr),
    _biot(_has_pf ? &getADMaterialProperty<Real>(("biot_coefficient_qp")) : nullptr),

    _rz(getBlockCoordSystem() == Moose::COORD_RZ)
{

  for (unsigned int i = 0; i < _ndisp; ++i)
    _disp_var[i] = Coupleable::coupled("displacements", i);

  if (_ndisp == 1 && _volumetric_locking_correction)
    mooseError("Volumetric locking correction should be set to false for 1-D problems.");
}

void
OrcaPoroMechKernel::initialSetup()
{
  if (getBlockCoordSystem() != Moose::COORD_XYZ)
    mooseError(
        "The coordinate system in the Problem block must be set to XYZ for cartesian geometries.");
}

ADReal
OrcaPoroMechKernel::computeQpResidual()
{
  using std::exp;

  ADReal residual = _stress[_qp].row(_component) * _grad_test[_i][_qp];

  // volumetric locking correction
  if (_volumetric_locking_correction)
    residual += (_avg_grad_test[_i] - _grad_test[_i][_qp](_component)) / 3.0 * _stress[_qp].trace();

  if (_ndisp != 3 && _out_of_plane_strain_coupled && _use_displaced_mesh)
  {
    const ADReal out_of_plane_thickness = exp((*_out_of_plane_strain)[_qp]);
    residual *= out_of_plane_thickness;
  }

  if (_has_pf)
  {
    if (_rz && _component == 0)
      residual -= (*_biot)[_qp] * (*_pf)[_qp] *
                  (_grad_test[_i][_qp](0) + _test[_i][_qp] / _q_point[_qp](0));

    residual -= _grad_test[_i][_qp](_component) * (*_biot)[_qp] * (*_pf)[_qp];
  }

  return residual;
}

void
OrcaPoroMechKernel::precalculateResidual()
{
  if (!_volumetric_locking_correction)
    return;

  ADReal ad_current_elem_volume = 0.0;
  for (unsigned int qp = 0; qp < _qrule->n_points(); qp++)
    ad_current_elem_volume += _ad_JxW[qp] * _ad_coord[qp];

  // Calculate volume averaged value of shape function derivative
  _avg_grad_test.resize(_test.size());
  for (_i = 0; _i < _test.size(); ++_i)
  {
    _avg_grad_test[_i] = 0.0;
    for (_qp = 0; _qp < _qrule->n_points(); ++_qp)
      _avg_grad_test[_i] += _grad_test[_i][_qp](_component) * _ad_JxW[_qp] * _ad_coord[_qp];

    _avg_grad_test[_i] /= ad_current_elem_volume;
  }
}
