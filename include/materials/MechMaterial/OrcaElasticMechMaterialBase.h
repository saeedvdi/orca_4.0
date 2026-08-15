#pragma once

#include "ADMaterial.h"
#include "RankFourTensor.h"
#include "RankTwoTensor.h"

/**
 * Base class that builds isotropic elasticity tensor Cijkl from any two independent
 * elastic constants and exposes it as an AD material property.
 *
 * Declared properties (with optional base_name prefix):
 *   - <base_name>Cijkl        (RankFourTensor)
 *   - <base_name>bulk_modulus (Real)
 */
class OrcaElasticMechMaterialBase : public ADMaterial
{
public:
  static InputParameters validParams();

  OrcaElasticMechMaterialBase(const InputParameters & parameters) ;

protected:
  virtual void initialSetup() override;
  virtual void computeQpProperties() override;

  void elasticConstantsInputCheck() const;
  std::pair<Real, Real> computeLameParameters() const; // returns {lambda, mu}
  void buildIsotropicTensor();

  // Base-name prefix for property naming
  const std::string _base_name;

  // User-specified flags
  const bool _bulk_modulus_set;
  const bool _lambda_set;
  const bool _poissons_ratio_set;
  const bool _shear_modulus_set;
  const bool _youngs_modulus_set;

  // Raw input values (if provided)
  const Real _bulk_modulus_in;
  const Real _lambda_in;
  const Real _poissons_ratio_in;
  const Real _shear_modulus_in;
  const Real _youngs_modulus_in;

  // Material properties we expose
  const MaterialPropertyName _Cijkl_name;
  const MaterialPropertyName _K_name;

  ADMaterialProperty<RankFourTensor> & _Cijkl;
  ADMaterialProperty<Real> & _K;

  // Cached (non-property) tensor built in buildIsotropicTensor()
  RankFourTensor _Cijkl_cache;
};