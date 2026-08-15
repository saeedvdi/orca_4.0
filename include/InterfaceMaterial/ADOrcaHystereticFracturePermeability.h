#pragma once

#include "ADOrcaRoughnessDamageFracturePermeability.h"

/**
 * Fracture permeability with a HYSTERETIC (path-dependent) reversible normal closure.
 *
 * The base class computes a single-path ("reversible") aperture opening O_b(sigma'_n) — linear,
 * Barton-Bandis, power-law Barton-Bandis, or exponential. Real rough joints instead follow a
 * closure LOOP: on unloading (opening) they follow a soft branch, but on re-closing they come back
 * along a STIFFER branch and retain part of the opening (Bandis & Barton, 1983).
 *
 * This class treats the base opening as the OPENING (unloading, sigma'_n decreasing) backbone and
 * makes the RE-CLOSING (sigma'_n increasing above the most-open state reached) branch
 * unload_reload_stiffness_ratio (R >= 1) times stiffer, anchored continuously at the reversal point:
 *
 *   opening(N) = O_b(N_min) - ( O_b(N_min) - O_b(N) ) / R ,   for N > N_min (re-closing)
 *   opening(N) = O_b(N)                                    ,   for N <= N_min (opening / virgin)
 *
 * where N_min is the smallest effective normal stress reached since the initial preload seating.
 * R = 1 recovers the reversible base law exactly (byte-identical). The branch selection uses the
 * OLD converged N_min (explicit state), so it is frozen within a Newton iteration — no Jacobian
 * discontinuity, and the value is continuous at the reversal.
 */
class ADOrcaHystereticFracturePermeability : public ADOrcaRoughnessDamageFracturePermeability
{
public:
  static InputParameters validParams();

  ADOrcaHystereticFracturePermeability(const InputParameters & parameters);

protected:
  virtual void initQpStatefulProperties() override;
  virtual ADReal computeStressAperture(const ADReal & effective_normal_compression) override;

  /// R >= 1: re-closing branch is R x stiffer than the opening backbone (R = 1 -> reversible base).
  const Real _unload_reload_stiffness_ratio;
  /// Hysteresis engages once sigma'_n has first reached this fraction of the reference stress, so the
  /// preload ramp (0 -> preload) is treated as virgin seating and does not latch N_min onto the ramp.
  const Real _preload_fraction;

  /// most-open effective normal stress reached since preload (running minimum) — the reversal anchor
  MaterialProperty<Real> & _sigma_n_min;
  const MaterialProperty<Real> & _sigma_n_min_old;
  /// flag (0/1): has sigma'_n first reached the preload seating threshold?
  MaterialProperty<Real> & _preloaded;
  const MaterialProperty<Real> & _preloaded_old;
};
