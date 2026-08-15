#pragma once

#include "ADMaterial.h"
#include "ADReal.h"
#include "MooseEnum.h"
#include "MooseTypes.h"

class SinglePhaseFluidProperties;

class OrcaTHMaterial : public ADMaterial
{
public:
  static InputParameters validParams();

  OrcaTHMaterial(const InputParameters & parameters);

protected:
  virtual void initQpStatefulProperties() override;
  virtual void computeQpProperties() override;

private:
  void computePorosityModel();
  void computePermeabilityTensorModel();
  void computeDensityViscosity();
  ADReal rho_from_p_T(const ADReal & p, const ADReal & T) const;
  void computeSpecificHeats();
  void computeInternalEnergy();
  void computeEnthalpy();
  void computeEntropy();
  void computeMobility();
  void computeRockEnergy();
  void computeEffectiveThermalConductivity();
  void computeSolidEffectiveThermalExpansionCoefficient();
  void computeFluidThermalExpansionCoefficient();
  void computeFluidThermalConductivity();
  void computeBiotModulus();

  const ADVariableValue & _p;
  const bool _has_temperature;
  const ADVariableValue * const _T;

  const MooseEnum _fluid_properties_model;
  const bool _use_fp;
  const SinglePhaseFluidProperties * const _fp;
  const MooseEnum _porosity_model;
  const MooseEnum _permeability_model;
  const MooseEnum _fluid_density_model;
  const MooseEnum _thermal_conductivity_model;
  const MooseEnum _effective_thermal_expansion_model;
  const MooseEnum _fluid_thermal_expansion_model;

  const Real _Kf_in;
  const RealTensorValue _kappa_in;
  const Real _phi_in;

  const Real _rho_ref;
  const Real _mu_ref;
  const Real _p_ref;
  const Real _T_ref;
  const Real _beta_ref;

  const bool _compute_cp_cv;
  const bool _compute_e;
  const bool _compute_h;
  const bool _compute_s;
  const bool _compute_k_fluid;
  const bool _compute_alpha_fluid_T;

  const Real * const _cp_f_in;
  const Real * const _cv_f_in;
  const Real * const _fluid_internal_energy_in;
  const Real * const _s_in;
  const Real * const _k_fluid_in;
  const Real * const _pp_coefficient_in;
  const Real * const _cp_s_in;
  const Real * const _rho_s_in;
  const Real * const _fluid_coeff_in;
  const Real * const _drained_coeff_in;
  const Real * const _alpha_eff_user;
  const RealTensorValue * const _k_dry_in;
  const RealTensorValue * const _k_wet_in;

  const ADMaterialProperty<Real> & _biot;

  ADMaterialProperty<Real> & _Kf;
  ADMaterialProperty<Real> & _porosity;
  ADMaterialProperty<RealTensorValue> & _permeability;
  ADMaterialProperty<Real> & _rho_f;
  ADMaterialProperty<Real> & _mu;
  ADMaterialProperty<Real> & _cp_f;
  ADMaterialProperty<Real> & _cv_f;
  ADMaterialProperty<Real> & _fluid_internal_energy;
  ADMaterialProperty<Real> & _fluid_enthalpy;
  ADMaterialProperty<Real> & _s;
  ADMaterialProperty<Real> & _k_fluid;
  ADMaterialProperty<Real> & _pp_coefficient;
  ADMaterialProperty<Real> & _alpha_fluid_T;
  ADMaterialProperty<RealTensorValue> & _fluid_mobility_tensor;
  ADMaterialProperty<Real> & _cp_s;
  ADMaterialProperty<Real> & _rho_s;
  ADMaterialProperty<Real> & _fluid_coeff;
  ADMaterialProperty<Real> & _drained_coeff;
  ADMaterialProperty<Real> & _rock_energy;
  ADMaterialProperty<Real> & _alpha_eff_T;
  const MaterialProperty<Real> & _alpha_eff_T_old;
  ADMaterialProperty<RealTensorValue> & _k_eff;
  ADMaterialProperty<Real> & _biot_modulus;
  const MaterialProperty<Real> & _biot_modulus_old;
  const MooseEnum _biot_modulus_model;
  const bool _has_MechMatTerm;
  const ADMaterialProperty<Real> * const _bulk_modulus;
  const bool _solid_bulk_compliance_set;
  const Real _solid_bulk_compliance_in;
  ADMaterialProperty<Real> & _solid_bulk_compliance;
  MaterialProperty<Real> & _biot_modulus_available;
};
