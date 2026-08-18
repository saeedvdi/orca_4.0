#pragma once

#include "ADOrcaBartonBandisContactTractionFastADHardening.h"

/**
 * ADOrcaBartonBandisRateStateHardening
 *
 * Extends ADOrcaBartonBandisContactTractionFastADHardening with a Dieterich-Ruina
 * rate-and-state OVERSTRESS, replacing the linear Perzyna `tangential_viscosity`.
 *
 *   tau_lim = c(W) + sigma'_n * mu(s^p)          <-- unchanged parent envelope
 *           + sigma'_n * [ a*L(V/V0) - b*L(V_th/V0) ]      <-- this class
 *
 *   L(x)  = ln(1 + x)          regularized logarithm, L(0) = 0, L'(x) = 1/(1+x)
 *   V     = dgp/dt             slip velocity over the step
 *   V_th  = D_rs / theta       the "state velocity"
 *   dtheta/dt = 1 - V*theta/D_rs                 (Dieterich aging law)
 *
 * WHY AN OVERSTRESS AND NOT THE ARCSINH FLOW FORM.  The parent is a return-map law
 * with a genuine elastic stick branch: below yield no slip is solved for at all.
 * The regularized flow form tau = sigma'_n a asinh[(V/2V0) exp(Psi/a)] has no stick
 * branch (it creeps at every stress), so substituting it would destroy the parent's
 * active-set logic.  Added as an overstress, RSF occupies exactly the slot the
 * Perzyna viscosity occupies today -- the same residual term, the same tangent --
 * and reduces to it in form while replacing a fitted eta with two measurable
 * constants.  See ADOrcaBartonBandisFlowRSFContactTraction for the flow-form law,
 * which bundles RSF with Barton's JRC-mobilization table and is therefore NOT a
 * controlled comparison against this deck family.
 *
 * LIMITS.  At steady state theta = D_rs/V, so V_th = V and the overstress collapses
 * to the textbook sigma'_n (a-b) L(V/V0).  At V = 0 held long enough theta -> inf,
 * V_th -> 0 and the overstress -> 0: the parent Barton-Bandis envelope IS the
 * quasi-static, fully healed strength, which is the frame it was calibrated in.
 * Both branches are logarithmic and therefore bounded on any velocity this problem
 * can produce; no clamp is needed and none is applied.
 *
 * WHAT IT BUYS.  Slip-weakening alone has no time dependence: at constant stress
 * with no slip nothing evolves, so it cannot produce hold-stage creep or re-strengthening
 * between injection steps.  b > 0 supplies both.  theta ages through stick via the
 * parent's commitAdditionalState(0.0) call, which exists for exactly this purpose.
 *
 * CALIBRATION NOTE.  Equating the Perzyna and RSF direct effects at V = V0,
 *   eta * V0  ==  sigma'_n * a * ln 2,
 * the Ye2018 decks' fitted viscosities imply
 *   SW-T1 a = 5.1e-4,  SW-T2 5.0e-4,  SW-S3 1.2e-3,  SW-S4 9.5e-3
 * against a laboratory range of 0.008-0.015 for granite.  SW-S4 -- the only specimen
 * whose staircase timing never fitted -- is the only one whose fitted viscosity
 * already sits in the physical range.  The other three are 8-20x below it, so
 * enabling RSF at a physical `a` is expected to CHANGE those three fits, not merely
 * refine them.  That is the risk this class exists to measure.
 *
 * Set use_rate_and_state = false to recover the parent bit-for-bit (the control).
 *
 * Use in input files with:
 *   type = OrcaBartonBandisRateStateHardening
 */
class ADOrcaBartonBandisRateStateHardening
  : public ADOrcaBartonBandisContactTractionFastADHardening
{
public:
  static InputParameters validParams();
  ADOrcaBartonBandisRateStateHardening(const InputParameters & parameters);

protected:
  virtual void initQpStatefulProperties() override;

  ADReal computeAdditionalShearStrength(const ADReal & sigma_n,
                                        Real plastic_slip_increment) const override;

  Real computeAdditionalShearStrengthReal(Real sigma_n,
                                          Real plastic_slip_increment,
                                          Real d_sigma_n_d_plastic_slip,
                                          Real & dstrength_dslip) const override;

  void carryAdditionalState() override;
  void commitAdditionalState(Real plastic_slip_increment) override;

  /// theta after a step that slipped by `plastic_slip_increment`, exact integral of the
  /// aging law at constant V. Also returns dtheta/d(plastic_slip_increment).
  Real agedTheta(Real plastic_slip_increment, Real & dtheta_dslip) const;

  /// The rate-and-state friction perturbation and its derivative w.r.t. the slip increment.
  /// Returns delta_mu = a*L(V/V0) - b*L(V_th/V0); dmu_dslip is d(delta_mu)/d(dgp).
  Real frictionPerturbation(Real plastic_slip_increment, Real & dmu_dslip) const;

  const bool _use_rate_and_state;
  const Real _rsf_a;
  const Real _rsf_b;
  const Real _rsf_Dc;
  const Real _rsf_V0;
  const Real _rsf_theta0;

  /// State variable theta [s], aged every step including stick.
  MaterialProperty<Real> & _rate_state_theta;
  const MaterialProperty<Real> & _rate_state_theta_old;

  /// Diagnostics: solved slip velocity [m/s] and the shear overstress it produced [Pa].
  MaterialProperty<Real> & _rate_state_slip_velocity;
  MaterialProperty<Real> & _rate_state_overstress;
};
