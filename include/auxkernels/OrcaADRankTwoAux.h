#pragma once

#include "NodalPatchRecovery.h"
#include "RankTwoTensor.h"

/**
 * Outputs one component of a RankTwoTensor material property.
 */
class OrcaADRankTwoAux : public NodalPatchRecovery
{
public:
  static InputParameters validParams();

  OrcaADRankTwoAux(const InputParameters & parameters);

protected:
  Real computeValue() override;

private:
  const ADMaterialProperty<RankTwoTensor> & _tensor;
  const unsigned int _i;
  const unsigned int _j;
  const bool _has_selected_qp;
  const unsigned int _selected_qp;
};
