#pragma once

#include "MooseTypes.h"

#include "metaphysicl/raw_type.h"

#include <algorithm>
#include <cmath>

/**
 * Shared recoverable joint-normal response for CZM contact materials.
 *
 * The legacy branch is exactly the smoothed linear penalty law used by the MC, PST, and
 * Barton--Bandis FlowRSF materials.  The opt-in branch is the same pre-seated power-law
 * Barton--Bandis closure used by ADOrcaBartonBandisContactTractionFastAD:
 *
 *   sigma_n = (K_ni V_m) [c / (V_m - c)]^(1/p).
 *
 * `tangent` is d(sigma_n)/d(overlap), including the smooth-positive derivative.  Keeping
 * this response in one utility prevents the three constitutive laws from drifting apart.
 */
namespace OrcaNormalClosure
{
template <typename T>
struct Response
{
  T pressure;
  T tangent;
  T closure;
};

template <typename T>
Real
rawValue(const T & value)
{
  return MetaPhysicL::raw_value(value);
}

template <typename T>
Response<T>
evaluate(const T & overlap,
         const Real gap_regularization,
         const bool use_power_law,
         const Real legacy_penalty,
         const Real initial_stiffness,
         const Real maximum_closure,
         const Real maximum_closure_fraction,
         const Real stress_exponent,
         const Real closure_offset)
{
  using std::pow;
  using std::sqrt;

  const T shifted_overlap = overlap + T(use_power_law ? closure_offset : 0.0);
  const T root =
      sqrt(shifted_overlap * shifted_overlap + T(gap_regularization * gap_regularization));
  const T positive_closure = T(0.5) * (shifted_overlap + root);
  const T dclosure_doverlap = T(0.5) * (T(1.0) + shifted_overlap / root);

  if (!use_power_law)
    return {T(legacy_penalty) * positive_closure,
            T(legacy_penalty) * dclosure_doverlap,
            positive_closure};

  const Real closure_cap = maximum_closure_fraction * maximum_closure;
  const T closure = std::min(T(closure_cap), std::max(T(0.0), positive_closure));
  const bool capped = rawValue(positive_closure) >= closure_cap;
  const Real linearization_closure = std::min(1.0e-9, 0.01 * maximum_closure);
  const Real sigma0 = initial_stiffness * maximum_closure;

  T pressure;
  T tangent_wrt_closure;
  if (rawValue(closure) < linearization_closure)
  {
    const Real x_linear = linearization_closure / (maximum_closure - linearization_closure);
    const Real pressure_linear = sigma0 * std::pow(x_linear, 1.0 / stress_exponent);
    const Real stiffness_linear = pressure_linear / linearization_closure;
    pressure = T(stiffness_linear) * closure;
    tangent_wrt_closure = T(stiffness_linear);
  }
  else
  {
    const T denominator = T(maximum_closure) - closure;
    const T ratio = closure / denominator;
    pressure = T(sigma0) * pow(ratio, T(1.0 / stress_exponent));
    tangent_wrt_closure =
        T(sigma0 / stress_exponent) * pow(ratio, T(1.0 / stress_exponent - 1.0)) *
        T(maximum_closure) / (denominator * denominator);
  }

  return {pressure,
          capped ? T(0.0) : tangent_wrt_closure * dclosure_doverlap,
          closure};
}
} // namespace OrcaNormalClosure
