#pragma once

#include "OrcaElasticMechMaterialBase.h"

#include "MooseEnum.h"
#include "RankTwoTensor.h"
#include "RankFourTensor.h"
#include "ADReal.h"

#include <vector>

class Function;

class OrcaMechMaterial : public OrcaElasticMechMaterialBase
{
public:
  static InputParameters validParams();

  OrcaMechMaterial(const InputParameters & parameters);

protected:
  virtual void initialSetup() override;
  virtual void initQpStatefulProperties() override;
  virtual void computeQpProperties() override;
  virtual void computeProperties() override;

private:
  void displacementIntegrityCheck();
  void computeInitialStressTensor();
  void computeTotalSmallStrain();
  void computeIncrementalStrain();
  void computeTotalStrainIncrement(ADRankTwoTensor & total_strain_increment) const;
  void subtractEigenstrainIncrementFromStrain(ADRankTwoTensor & strain) const;
  void computeVolumetricStrain();
  void computeLinearElasticStress();

  const unsigned int _ndisp;
  std::vector<const ADVariableGradient *> _grad_disp;
  std::vector<const VariableGradient *> _grad_disp_old;

  unsigned int _num_ini_stress;
  std::vector<const Function *> _initial_stress;

  const MooseEnum _strain_model;

  // --- optional thermal coupling ---
  const bool _has_temperature;
  const bool _has_stress_free_temperature;
  const ADVariableValue * _temperature;
  const VariableValue * _temperature_old;
  const ADVariableValue * _stress_free_temperature;
  const bool _use_old_temperature;
  const bool _compute_thermal_eigenstrain;
  const ADMaterialProperty<Real> * _thermal_expansion_coeff;
  const MaterialPropertyName _thermal_eigenstrain_prop_name;

  const ADRealGradient _ad_zero_grad;
  const RealGradient _zero_grad;

  ADMaterialProperty<RankTwoTensor> & _mechanical_strain;
  const MaterialProperty<RankTwoTensor> & _mechanical_strain_old;
  ADMaterialProperty<RankTwoTensor> & _total_strain;
  const MaterialProperty<RankTwoTensor> & _total_strain_old;
  ADMaterialProperty<RankTwoTensor> & _strain_rate;
  ADMaterialProperty<RankTwoTensor> & _strain_increment;
  ADMaterialProperty<RankTwoTensor> & _rotation_increment;
  ADMaterialProperty<Real> & _vol_total_strain_qp;
  ADMaterialProperty<Real> & _vol_strain_rate_qp;
  ADMaterialProperty<RankTwoTensor> & _thermal_eigenstrain;
  const MaterialProperty<RankTwoTensor> & _thermal_eigenstrain_old;

  const std::vector<MaterialPropertyName> _eigenstrain_names;
  std::vector<const ADMaterialProperty<RankTwoTensor> *> _eigenstrains;
  std::vector<const MaterialProperty<RankTwoTensor> *> _eigenstrains_old;
  const ADMaterialProperty<RankTwoTensor> * _global_strain;

  const bool _volumetric_locking_correction;
  ADReal _elem_vol_strain_accum;
  ADReal _elem_vol_JxW_accum;

  const ADMaterialProperty<RankFourTensor> & _elasticity_tensor;

  const MaterialPropertyName _stress_name;
  ADMaterialProperty<RankTwoTensor> & _stress;
  ADMaterialProperty<RankTwoTensor> & _initial_stress_tensor;
  ADMaterialProperty<RankTwoTensor> & _elastic_strain;
};
