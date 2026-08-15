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

/**
 * Normal response as a function of the (already positive-parted) closure.
 *
 * This is the single implementation of the Barton--Bandis power-law closure
 *
 *   sigma_n = (K_ni V_m) [c / (V_m - c)]^(1/p)
 *
 * shared by every contact material. Callers that hold an *overlap* and need the
 * smooth-positive part applied should use evaluate() below; callers that already track a
 * closure (e.g. the FastAD Barton--Bandis family, which folds the pre-seating offset and any
 * unload/reclosure transform into the closure before calling) use this directly.
 *
 * `tangent` here is d(sigma_n)/d(closure); evaluate() chains it with d(closure)/d(overlap).
 */
template <typename T>
Response<T>
evaluateFromClosure(const T & raw_closure,
                    const bool use_power_law,
                    const Real legacy_penalty,
                    const Real initial_stiffness,
                    const Real maximum_closure,
                    const Real maximum_closure_fraction,
                    const Real stress_exponent)
{
  using std::pow;

  if (!use_power_law)
  {
    const T closure = std::max(T(0.0), raw_closure);
    return {T(legacy_penalty) * closure,
            rawValue(raw_closure) > 0.0 ? T(legacy_penalty) : T(0.0),
            closure};
  }

  const Real closure_cap = maximum_closure_fraction * maximum_closure;
  const T closure = std::min(T(closure_cap), std::max(T(0.0), raw_closure));
  const bool capped = rawValue(raw_closure) >= closure_cap;
  // Below this closure the law is linearized so the tangent stays bounded: for p > 1 the
  // exact tangent ~ c^(1/p - 1) is singular as c -> 0.
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

  return {pressure, capped ? T(0.0) : tangent_wrt_closure, closure};
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

  const auto response = evaluateFromClosure<T>(positive_closure,
                                               use_power_law,
                                               legacy_penalty,
                                               initial_stiffness,
                                               maximum_closure,
                                               maximum_closure_fraction,
                                               stress_exponent);

  return {response.pressure, response.tangent * dclosure_doverlap, response.closure};
}
} // namespace OrcaNormalClosure
