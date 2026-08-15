#pragma once

#include "ADOrcaBartonBandisContactTractionFastAD.h"

/**
 * ADOrcaBartonBandisContactTractionFastADHardening
 *
 * Extends ADOrcaBartonBandisContactTractionFastAD with a post-peak slip-weakening
 * law that is independent of JRC mobilization:
 *
 *   mu(s^p) = mu_r + (mu_p - mu_r) * exp(-(s^p / D_c)^m)
 *   tau_lim  = sigma_c * mu(s^p)
 *
 * where mu_p is the Barton-Bandis peak friction coefficient, mu_r is the residual
 * friction coefficient, s^p is cumulative plastic slip, and D_c is the characteristic
 * slip-weakening distance.  As s^p -> inf the friction decays to mu_r; at s^p = 0 it
 * equals mu_p.
 *
 * When use_slip_weakening = false the model is identical to the base class.
 *
 * Use in input files with:
 *   type = OrcaBartonBandisContactTractionFastADHardening
 */
class ADOrcaBartonBandisContactTractionFastADHardening
    : public ADOrcaBartonBandisContactTractionFastAD
{
public:
  static InputParameters validParams();
  ADOrcaBartonBandisContactTractionFastADHardening(const InputParameters & parameters);

protected:
  void computeBartonBandisProperties(const ADReal & sigma_n,
                                     const ADReal & cumulative_slip,
                                     ADReal & jrc_mobilized,
                                     ADReal & roughness_angle_deg,
                                     ADReal & peak_friction_angle_deg,
                                     ADReal & friction_coefficient,
                                     ADReal & dilation_angle_deg,
                                     ADReal & dilation_coefficient,
                                     ADReal & shear_strength) const override;

  void computeBartonBandisPropertiesReal(Real sigma_n,
                                         Real cumulative_slip,
                                         Real & jrc_mobilized,
                                         Real & roughness_angle_deg,
                                         Real & peak_friction_angle_deg,
                                         Real & friction_coefficient,
                                         Real & dilation_angle_deg,
                                         Real & dilation_coefficient,
                                         Real & shear_strength) const override;

  Real computeReturnMappingDerivative(Real sigma_n,
                                      Real kn_tangent,
                                      Real jrc_mobilized,
                                      Real roughness_angle_deg,
                                      Real peak_friction_angle_deg,
                                      Real mu,
                                      Real dilation_coefficient,
                                      Real dilation_increment,
                                      Real closure_new,
                                      Real cumulative_slip_new) const override;

  Real computeRoughnessState() const override;

  const bool _use_slip_weakening;
  const Real _characteristic_slip_distance;
  const Real _slip_weakening_exponent;
  const Real _slip_weakening_residual_friction_angle_deg;

  const bool _use_roughness_degradation;
  const Real _roughness_characteristic_slip;
  const Real _roughness_state_initial;
  const Real _roughness_state_residual;
};
