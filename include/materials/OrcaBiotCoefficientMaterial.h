#pragma once

#include "ADMaterial.h"
#include "MooseEnum.h"
#include "MooseTypes.h"
#include "RankFourTensor.h"

class OrcaBiotCoefficientMaterial : public ADMaterial
{
public:
  static InputParameters validParams();
  OrcaBiotCoefficientMaterial(const InputParameters & parameters);

protected:
  void initQpStatefulProperties() override;
  void computeQpProperties() override;

private:
  const MooseEnum _model;
  const Real _alpha_user;
  const bool _clamp;

  // Only used for model=from_elasticity (QP only)
  const ADMaterialProperty<RankFourTensor> * _Cijkl;
  const ADMaterialProperty<Real> * _Ks;

  // Output alpha (hard-wired qp vs nodal)
  ADMaterialProperty<Real> & _biot;
};
