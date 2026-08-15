#include "OrcaADRankTwoAux.h"

#include "MooseError.h"

#include "metaphysicl/raw_type.h"

registerMooseObject("OrcaApp", OrcaADRankTwoAux);

InputParameters
OrcaADRankTwoAux::validParams()
{
  InputParameters params = NodalPatchRecovery::validParams();
  params.addClassDescription("Access a component of an AD RankTwoTensor material property.");
  params.addRequiredParam<MaterialPropertyName>("rank_two_tensor",
                                                "The rank two material tensor name.");
  params.addRequiredRangeCheckedParam<unsigned int>(
      "index_i", "index_i >= 0 & index_i <= 2", "The first tensor component index.");
  params.addRequiredRangeCheckedParam<unsigned int>(
      "index_j", "index_j >= 0 & index_j <= 2", "The second tensor component index.");
  params.addParam<unsigned int>("selected_qp", "Evaluate the tensor at this specific quadpoint.");
  params.addParamNamesToGroup("selected_qp", "Advanced");
  return params;
}

OrcaADRankTwoAux::OrcaADRankTwoAux(const InputParameters & parameters)
  : NodalPatchRecovery(parameters),
    _tensor(getADMaterialProperty<RankTwoTensor>("rank_two_tensor")),
    _i(getParam<unsigned int>("index_i")),
    _j(getParam<unsigned int>("index_j")),
    _has_selected_qp(isParamValid("selected_qp")),
    _selected_qp(_has_selected_qp ? getParam<unsigned int>("selected_qp") : 0)
{
}

Real
OrcaADRankTwoAux::computeValue()
{
  unsigned int qp = _qp;
  if (_has_selected_qp)
  {
    if (_selected_qp >= _q_point.size())
      mooseError("selected_qp specified as ",
                 _selected_qp,
                 " but there are only ",
                 _q_point.size(),
                 " quadpoints in the element.");

    qp = _selected_qp;
  }

  return MetaPhysicL::raw_value(_tensor[qp])(_i, _j);
}
