#include "ADOrcaPeakShelfTailFlowRSFContactTraction.h"
#include "OrcaNormalClosure.h"

#include "metaphysicl/raw_type.h"

#include <algorithm>
#include <cmath>
#include <limits>
#include <sstream>

registerMooseObject("OrcaApp", ADOrcaPeakShelfTailFlowRSFContactTraction);
registerMooseObjectAliased("OrcaApp",
                           ADOrcaPeakShelfTailFlowRSFContactTraction,
                           "OrcaPeakShelfTailFlowRSFContactTraction");

namespace
{
constexpr Real pst_pi = 3.141592653589793238462643383279502884;
constexpr Real pst_ln2 = 0.6931471805599453094;
// Above this value of L = ln(z) the exact asinh(z) = ln(z + sqrt(z^2+1)) equals
// L + ln 2 to double precision (relative error ~ e^{-2L} < 1e-17), and z^2 would
// eventually overflow; switch to the logarithmic branch.
constexpr Real pst_asinh_log_branch = 20.0;
// 10^{1/4}: the stick-velocity floor blends to the exact-stick branch over half a
// decade of slip velocity, [V_floor/r, V_floor*r], via a smoothstep in ln V.
constexpr Real pst_stick_blend_ratio = 1.7782794100389228;
constexpr Real pst_residual_roundoff_factor = 64.0;

inline Real
rawv(Real x)
{
  return x;
}
inline Real
rawv(const ADReal & x)
{
  return MetaPhysicL::raw_value(x);
}

template <typename T>
T
smoothPos(const T & x, const Real eps)
{
  using std::sqrt;
  return T(0.5) * (x + sqrt(x * x + T(eps * eps)));
}

template <typename T>
T
smoothPosDerivative(const T & x, const Real eps)
{
  using std::sqrt;
  return T(0.5) * (T(1.0) + x / sqrt(x * x + T(eps * eps)));
}
}

InputParameters
ADOrcaPeakShelfTailFlowRSFContactTraction::validParams()
{
  InputParameters params = OrcaCZMComputeLocalTractionIncrementalBase::validParams();
  params.addClassDescription(
      "Peak-shelf-tail slip-weakening friction with flow-form (always-creeping) regularized "
      "rate-and-state and energy-bounded dilation; the hardening law back-derived from the "
      "Ye & Ghassemi (2018) SW-S3/SW-S4 injection-shear tests. Exports the same CZM property "
      "names as the cohesionless damage MC law.");

  params.addParam<std::string>("base_name", "Material property base name");

  params.addRangeCheckedParam<Real>(
      "penalty_normal", "penalty_normal > 0.0", "Contact normal stiffness K_n [Pa/m].");
  params.addRangeCheckedParam<Real>(
      "penalty_tangent",
      0.0,
      "penalty_tangent >= 0.0",
      "Tangential stiffness K_t [Pa/m]. A value of zero uses penalty_normal.");
  params.addParam<bool>(
      "use_hyperbolic_normal_closure",
      false,
      "Use the pre-seated recoverable power-law Barton--Bandis mechanical normal response. "
      "False preserves the legacy linear penalty law exactly.");
  params.addRangeCheckedParam<Real>("initial_normal_stiffness",
                                    1e13,
                                    "initial_normal_stiffness > 0.0",
                                    "Initial stiffness K_ni [Pa/m] of the power-law closure.");
  params.addRangeCheckedParam<Real>("maximum_closure",
                                    1e-4,
                                    "maximum_closure > 0.0",
                                    "Maximum mechanical closure V_m [m].");
  params.addRangeCheckedParam<Real>("maximum_closure_fraction",
                                    0.999,
                                    "maximum_closure_fraction > 0.0 & maximum_closure_fraction < 1.0",
                                    "Numerical cap on mechanical closure/V_m.");
  params.addRangeCheckedParam<Real>("normal_closure_stress_exponent",
                                    1.0,
                                    "normal_closure_stress_exponent >= 1.0",
                                    "Power-law closure stress exponent p.");
  params.addRangeCheckedParam<Real>(
      "normal_closure_offset",
      0.0,
      "normal_closure_offset >= 0.0",
      "Pre-seating closure c0 [m], so a zero displacement jump may carry the in-situ preload.");
  params.addRangeCheckedParam<Real>(
      "opening_gap_tolerance",
      0.0,
      "opening_gap_tolerance >= 0.0",
      "Gap tolerance [m] for the contact/open active-set decision.");
  params.addRangeCheckedParam<Real>("tangential_traction_tolerance",
                                    1e-12,
                                    "tangential_traction_tolerance >= 0.0",
                                    "Trial shear [Pa] below which the flow solve is skipped.");
  params.addRangeCheckedParam<Real>("contact_gap_regularization",
                                    1e-14,
                                    "contact_gap_regularization > 0.0",
                                    "Smooth-positive contact-gap regularization [m].");
  params.addRangeCheckedParam<Real>("stress_regularization",
                                    1e-8,
                                    "stress_regularization > 0.0",
                                    "Small stress floor used in diagnostic denominators [Pa].");
  params.addRangeCheckedParam<Real>(
      "local_newton_tolerance",
      1e-8,
      "local_newton_tolerance > 0.0",
      "Absolute residual tolerance [Pa] for the scalar flow solve.");
  params.addRangeCheckedParam<unsigned int>("max_local_newton_iterations",
                                            80,
                                            "max_local_newton_iterations > 0",
                                            "Maximum safeguarded local iterations (Newton with "
                                            "log-space bisection fallback).");
  params.addRangeCheckedParam<Real>(
      "tangential_viscosity",
      0.0,
      "tangential_viscosity >= 0.0",
      "Optional extra Perzyna viscosity eta_t [Pa.s/m]. The flow-form rate term already "
      "regularizes the instability; keep this at 0 unless bridging legacy decks.");

  params.addRangeCheckedParam<Real>("peak_friction_coefficient",
                                    0.50,
                                    "peak_friction_coefficient >= 0.0",
                                    "Quasi-static peak friction mu_peak available at zero slip.");
  params.addRangeCheckedParam<Real>(
      "shelf_friction_coefficient",
      0.30,
      "shelf_friction_coefficient >= 0.0",
      "Arrest-shelf friction mu_shelf reached after the concentration branch. This is the "
      "level that arrests a burst (SW-S3 tau_res / sigma'_n).");
  params.addRangeCheckedParam<Real>(
      "tail_friction_coefficient",
      0.05,
      "tail_friction_coefficient >= 0.0",
      "Deep-tail friction mu_tail; the slow branch that produces unloading creep must sink "
      "below the unloading mobilized ratio (~0.09 for SW-S4).");
  params.addRangeCheckedParam<Real>("concentration_slip_distance",
                                    4.0e-5,
                                    "concentration_slip_distance > 0.0",
                                    "Concentration-branch slip distance D_c [m] (peak -> shelf).");
  params.addRangeCheckedParam<Real>(
      "concentration_exponent",
      1.0,
      "concentration_exponent >= 1.0",
      "Stretched exponent m_c of the concentration branch: the surface-finish knob. "
      "m_c > 1 delays then concentrates the strength drop (rough interlock breakdown).");
  params.addRangeCheckedParam<Real>("concentration_onset_slip",
                                    0.0,
                                    "concentration_onset_slip >= 0.0",
                                    "Onset slip [m] of the concentration branch.");
  params.addRangeCheckedParam<Real>("tail_slip_distance",
                                    1.5e-4,
                                    "tail_slip_distance > 0.0",
                                    "Tail-branch slip distance D_t [m] (shelf -> tail).");
  params.addRangeCheckedParam<Real>(
      "tail_exponent", 1.0, "tail_exponent >= 1.0", "Stretched exponent m_t of the tail branch.");
  params.addRangeCheckedParam<Real>(
      "tail_onset_slip", 0.0, "tail_onset_slip >= 0.0", "Onset slip [m] of the tail branch.");
  params.addRangeCheckedParam<Real>(
      "apparent_cohesion",
      0.0,
      "apparent_cohesion >= 0.0",
      "Optional constant apparent shear cohesion c [Pa]; no tensile normal cohesion.");

  params.addParam<std::vector<Real>>(
      "tread_friction_drops",
      std::vector<Real>(),
      "Optional multi-shelf treads: friction drop d_mu_i of each tread episode, subtracted "
      "as d_mu_i * (1 - exp(-((s - s_i)/D_i)^m_i)) from the peak/shelf/tail backbone. A "
      "single stretched-exponential branch couples episode supply to arrest, so it cannot "
      "produce a staircase of injection-paced slip treads separated by arrests; each tread "
      "here supplies its own backbone drop over its own slip window and leaves the backbone "
      "flat (arrested) until the next tread's onset. Empty disables (default backbone "
      "unchanged). Size the drops from the per-episode strength-drop demand and re-split "
      "the peak->shelf drop so the total residual level is preserved.");
  params.addParam<std::vector<Real>>(
      "tread_onset_slips",
      std::vector<Real>(),
      "Cumulative-slip onsets s_i [m] of the tread episodes (strictly increasing; same "
      "length as tread_friction_drops).");
  params.addParam<std::vector<Real>>(
      "tread_slip_distances",
      std::vector<Real>(),
      "Slip distances D_i [m] over which each tread delivers its drop (same length as "
      "tread_friction_drops). Keep D_i well below the spacing to the next onset so the "
      "backbone is flat (arrested) between treads.");
  params.addParam<std::vector<Real>>(
      "tread_exponents",
      std::vector<Real>(),
      "Optional stretched exponents m_i >= 1 of the tread branches (same length as "
      "tread_friction_drops); empty uses 1.0 for all.");

  params.addRangeCheckedParam<Real>(
      "rsf_a",
      0.015,
      "rsf_a > 0.0",
      "Rate-and-state direct effect a. The flow form requires a > 0; it is the only "
      "regularization of the slip instability besides optional viscosity.");
  params.addRangeCheckedParam<Real>("rsf_b", 0.010, "rsf_b >= 0.0", "Rate-and-state b (aging).");
  params.addRangeCheckedParam<Real>(
      "rsf_Dc", 5.0e-5, "rsf_Dc > 0.0", "Rate-and-state state distance D_rs [m].");
  params.addRangeCheckedParam<Real>(
      "rsf_V0", 5.0e-8, "rsf_V0 > 0.0", "Reference slip velocity V0 [m/s].");
  params.addRangeCheckedParam<Real>(
      "rsf_theta0",
      0.0,
      "rsf_theta0 >= 0.0",
      "Initial state theta [s]; zero initializes to steady state D_rs / V0.");
  params.addRangeCheckedParam<Real>(
      "stick_report_velocity",
      1.0e-11,
      "stick_report_velocity >= 0.0",
      "Slip velocity below which fracture_state reports Stick (reporting only; the flow "
      "form has no kinematic stick branch).");
  params.addRangeCheckedParam<Real>(
      "stick_velocity_floor",
      1.0e-11,
      "stick_velocity_floor >= 0.0",
      "Solved slip velocity [m/s] below which the step is taken as exact elastic stick "
      "(0 disables and recovers the pure always-flow form). Sub-floor creep (< ~1 nm/min "
      "at the default) is physically negligible, but its log-curvature length V*dt falls "
      "below the global Newton excursion scale and floors the nonlinear residual at "
      "~K_t*A*V*dt: a dt-independent stagnation observed at ramp->hold transitions. A "
      "half-decade smoothstep in ln V bridges the stick and flow branches value- and "
      "slope-continuously; theta keeps aging through stick. Keep <= stick_report_velocity.");

  params.addParam<bool>("use_dilatancy", true, "Enable shear-induced irreversible dilation.");
  params.addRangeCheckedParam<Real>(
      "dilation_work_fraction",
      0.88,
      "dilation_work_fraction >= 0.0 & dilation_work_fraction < 1.0",
      "Fraction beta_d of frictional work allowed to become dilation work: "
      "dg_np/ds = beta_d * max(mu_qs, floor).");
  params.addRangeCheckedParam<Real>(
      "dilation_friction_coefficient_floor",
      0.0,
      "dilation_friction_coefficient_floor >= 0.0",
      "Lower bound on the friction coefficient used only for dilation (wear bulking keeps "
      "lifting the surfaces after friction has weakened; affects dilation only).");
  params.addRangeCheckedParam<Real>(
      "maximum_dilation_coefficient",
      0.0,
      "maximum_dilation_coefficient >= 0.0",
      "Optional geometric cap on dg_np/ds. Zero disables the cap.");

  params.addRangeCheckedParam<Real>(
      "roughness_state_initial",
      0.45,
      "roughness_state_initial >= 0.0 & roughness_state_initial <= 1.0",
      "Initial exported roughness_state for the permeability material.");
  params.addRangeCheckedParam<Real>(
      "roughness_state_residual",
      0.10,
      "roughness_state_residual >= 0.0 & roughness_state_residual <= 1.0",
      "Residual exported roughness_state for the permeability material.");

  params.addRangeCheckedParam<Real>(
      "reversible_normal_compliance",
      0.0,
      "reversible_normal_compliance >= 0.0",
      "Optional output-only elastic normal opening compliance C_n [m/Pa]. Zero disables.");
  params.addRangeCheckedParam<Real>(
      "damage_scaled_reversible_compliance",
      0.0,
      "damage_scaled_reversible_compliance >= 0.0",
      "Optional output-only damage-scaled elastic normal compliance kappa [1/Pa]: "
      "d_rev = (C_n + kappa * g_np) * <sigma_ref - sigma'_n>_+, g_np the accumulated "
      "plastic dilation. Shear bulking leaves the joint elastically softer in the normal "
      "direction, so the compliance must grow with slip history: a slip-independent C_n "
      "matched to the post-slip unload branch necessarily over-opens the undamaged "
      "stick phase (where the measured stiffness is ~20x higher at the same sigma'_n). "
      "Zero disables.");
  params.addRangeCheckedParam<Real>(
      "reversible_normal_reference_stress",
      0.0,
      "reversible_normal_reference_stress >= 0.0",
      "Reference effective normal stress [Pa] for the output-only elastic opening.");
  params.addRangeCheckedParam<Real>(
      "reversible_normal_opening_retention_fraction",
      0.0,
      "reversible_normal_opening_retention_fraction >= 0.0 & "
      "reversible_normal_opening_retention_fraction <= 1.0",
      "Fraction of the largest reversible normal opening retained during subsequent "
      "recompression. This is an output-only hysteresis diagnostic: zero preserves the "
      "legacy response, while one prevents reversible reclosure after the maximum opening.");
  params.addRangeCheckedParam<Real>(
      "reversible_normal_opening_retention_activation_slip",
      0.0,
      "reversible_normal_opening_retention_activation_slip >= 0.0",
      "Cumulative plastic slip [m] at which reversible-opening peak memory is activated. "
      "Before activation the stored maximum follows the instantaneous opening, excluding "
      "preload and pressure-cycling history. Zero preserves the previous behavior.");

  params.addRangeCheckedParam<Real>(
      "stability_reference_normal_stress",
      0.0,
      "stability_reference_normal_stress >= 0.0",
      "If > 0, print the peak quasi-static weakening slope W_max = sigma'_n |d tau_y/ds|_max "
      "at this normal stress at startup (the burst/staircase design number).");
  params.addRangeCheckedParam<Real>(
      "system_shear_stiffness",
      0.0,
      "system_shear_stiffness >= 0.0",
      "If > 0 together with stability_reference_normal_stress, also print W_max / k_tau "
      "(< 1: arrested staircase, SW-S4-type; > 1: dynamic burst, SW-S3-type).");

  return params;
}

ADOrcaPeakShelfTailFlowRSFContactTraction::ADOrcaPeakShelfTailFlowRSFContactTraction(
    const InputParameters & parameters)
  : OrcaCZMComputeLocalTractionIncrementalBase(parameters),
    _penalty_normal(getParam<Real>("penalty_normal")),
    _penalty_tangent(getParam<Real>("penalty_tangent") > 0.0 ? getParam<Real>("penalty_tangent")
                                                             : getParam<Real>("penalty_normal")),
    _use_hyperbolic_normal_closure(getParam<bool>("use_hyperbolic_normal_closure")),
    _initial_normal_stiffness(getParam<Real>("initial_normal_stiffness")),
    _maximum_closure(getParam<Real>("maximum_closure")),
    _maximum_closure_fraction(getParam<Real>("maximum_closure_fraction")),
    _normal_closure_stress_exponent(getParam<Real>("normal_closure_stress_exponent")),
    _normal_closure_offset(getParam<Real>("normal_closure_offset")),
    _opening_gap_tolerance(getParam<Real>("opening_gap_tolerance")),
    _tangential_traction_tolerance(getParam<Real>("tangential_traction_tolerance")),
    _contact_gap_regularization(getParam<Real>("contact_gap_regularization")),
    _stress_regularization(getParam<Real>("stress_regularization")),
    _local_newton_tolerance(getParam<Real>("local_newton_tolerance")),
    _max_local_newton_iterations(getParam<unsigned int>("max_local_newton_iterations")),
    _tangential_viscosity(getParam<Real>("tangential_viscosity")),
    _peak_friction_coefficient(getParam<Real>("peak_friction_coefficient")),
    _shelf_friction_coefficient(getParam<Real>("shelf_friction_coefficient")),
    _tail_friction_coefficient(getParam<Real>("tail_friction_coefficient")),
    _concentration_slip_distance(getParam<Real>("concentration_slip_distance")),
    _concentration_exponent(getParam<Real>("concentration_exponent")),
    _concentration_onset_slip(getParam<Real>("concentration_onset_slip")),
    _tail_slip_distance(getParam<Real>("tail_slip_distance")),
    _tail_exponent(getParam<Real>("tail_exponent")),
    _tail_onset_slip(getParam<Real>("tail_onset_slip")),
    _apparent_cohesion(getParam<Real>("apparent_cohesion")),
    _tread_friction_drops(getParam<std::vector<Real>>("tread_friction_drops")),
    _tread_onset_slips(getParam<std::vector<Real>>("tread_onset_slips")),
    _tread_slip_distances(getParam<std::vector<Real>>("tread_slip_distances")),
    _tread_exponents(getParam<std::vector<Real>>("tread_exponents")),
    _rsf_a(getParam<Real>("rsf_a")),
    _rsf_b(getParam<Real>("rsf_b")),
    _rsf_Dc(getParam<Real>("rsf_Dc")),
    _rsf_V0(getParam<Real>("rsf_V0")),
    _rsf_theta0(getParam<Real>("rsf_theta0")),
    _stick_report_velocity(getParam<Real>("stick_report_velocity")),
    _stick_velocity_floor(getParam<Real>("stick_velocity_floor")),
    _use_dilatancy(getParam<bool>("use_dilatancy")),
    _dilation_work_fraction(getParam<Real>("dilation_work_fraction")),
    _dilation_friction_coefficient_floor(getParam<Real>("dilation_friction_coefficient_floor")),
    _maximum_dilation_coefficient(getParam<Real>("maximum_dilation_coefficient")),
    _roughness_state_initial(getParam<Real>("roughness_state_initial")),
    _roughness_state_residual(getParam<Real>("roughness_state_residual")),
    _reversible_normal_compliance(getParam<Real>("reversible_normal_compliance")),
    _damage_scaled_reversible_compliance(getParam<Real>("damage_scaled_reversible_compliance")),
    _reversible_normal_reference_stress(getParam<Real>("reversible_normal_reference_stress")),
    _reversible_normal_opening_retention_fraction(
        getParam<Real>("reversible_normal_opening_retention_fraction")),
    _reversible_normal_opening_retention_activation_slip(
        getParam<Real>("reversible_normal_opening_retention_activation_slip")),
    _stability_reference_normal_stress(getParam<Real>("stability_reference_normal_stress")),
    _system_shear_stiffness(getParam<Real>("system_shear_stiffness")),
    _fracture_state(declareADProperty<Real>(_base_name + "fracture_state")),
    _limit_tau(declareADProperty<Real>(_base_name + "limit_tau")),
    _plastic_slip_increment(declareADProperty<Real>(_base_name + "plastic_slip_increment")),
    _dilation_jump_increment(declareADProperty<Real>(_base_name + "dilation_jump_increment")),
    _cumulative_plastic_slip(declareADProperty<Real>(_base_name + "cumulative_plastic_slip")),
    _cumulative_plastic_slip_old(
        getMaterialPropertyOld<Real>(_base_name + "cumulative_plastic_slip")),
    _roughness_state(declareADProperty<Real>(_base_name + "roughness_state")),
    _roughness_damage(declareADProperty<Real>(_base_name + "roughness_damage")),
    _friction_coefficient_effective(
        declareADProperty<Real>(_base_name + "friction_coefficient_effective")),
    _cohesion_effective(declareADProperty<Real>(_base_name + "cohesion_effective")),
    _dilation_angle_effective(declareADProperty<Real>(_base_name + "dilation_angle_effective")),
    _dilation_state(declareADProperty<Real>(_base_name + "dilation_state")),
    _dilation_support_factor(declareADProperty<Real>(_base_name + "dilation_support_factor")),
    _strength_normal_memory_magnitude(
        declareADProperty<Real>(_base_name + "strength_normal_memory_magnitude")),
    _strength_normal_memory(declareADProperty<Real>(_base_name + "strength_normal_memory")),
    _retained_shear_support(declareADProperty<Real>(_base_name + "retained_shear_support")),
    _normal_plastic_jump(declareADProperty<Real>(_base_name + "normal_plastic_jump")),
    _normal_plastic_jump_old(getMaterialPropertyOld<Real>(_base_name + "normal_plastic_jump")),
    _irreversible_dilation(declareADProperty<Real>(_base_name + "irreversible_dilation")),
    _normal_contact_pressure(declareADProperty<Real>(_base_name + "normal_contact_pressure")),
    _reversible_normal_opening(declareADProperty<Real>(_base_name + "reversible_normal_opening")),
    _normal_opening_total(declareADProperty<Real>(_base_name + "normal_opening_total")),
    _maximum_reversible_normal_opening(
        declareADProperty<Real>(_base_name + "maximum_reversible_normal_opening")),
    _maximum_reversible_normal_opening_old(
        getMaterialPropertyOld<Real>(_base_name + "maximum_reversible_normal_opening")),
    _rate_state_theta(declareADProperty<Real>(_base_name + "rate_state_theta")),
    _rate_state_theta_old(getMaterialPropertyOld<Real>(_base_name + "rate_state_theta")),
    _frictional_sliding_work_increment(
        declareADProperty<Real>(_base_name + "frictional_sliding_work_increment")),
    _dilation_work_increment(declareADProperty<Real>(_base_name + "dilation_work_increment")),
    _frictional_dilatant_dissipation_increment(
        declareADProperty<Real>(_base_name + "frictional_dilatant_dissipation_increment")),
    _cohesive_dissipation_increment(
        declareADProperty<Real>(_base_name + "cohesive_dissipation_increment")),
    _plastic_tangential_jump(
        declareADProperty<RealVectorValue>(_base_name + "plastic_tangential_jump")),
    _plastic_tangential_jump_old(
        getMaterialPropertyOld<RealVectorValue>(_base_name + "plastic_tangential_jump"))
{
  if (!_use_hyperbolic_normal_closure && _normal_closure_stress_exponent != 1.0)
    paramError("normal_closure_stress_exponent",
               "A non-unit exponent requires use_hyperbolic_normal_closure=true.");

  if (_shelf_friction_coefficient > _peak_friction_coefficient)
    paramError("shelf_friction_coefficient", "Must be <= peak_friction_coefficient.");
  if (_tail_friction_coefficient > _shelf_friction_coefficient)
    paramError("tail_friction_coefficient", "Must be <= shelf_friction_coefficient.");
  if (_roughness_state_residual > _roughness_state_initial)
    paramError("roughness_state_residual", "Must be <= roughness_state_initial.");

  const std::size_t n_treads = _tread_friction_drops.size();
  if (_tread_onset_slips.size() != n_treads)
    paramError("tread_onset_slips", "Must have the same length as tread_friction_drops.");
  if (_tread_slip_distances.size() != n_treads)
    paramError("tread_slip_distances", "Must have the same length as tread_friction_drops.");
  if (_tread_exponents.empty())
    _tread_exponents.assign(n_treads, 1.0);
  else if (_tread_exponents.size() != n_treads)
    paramError("tread_exponents",
               "Must be empty (all 1.0) or have the same length as tread_friction_drops.");
  for (std::size_t i = 0; i < n_treads; ++i)
  {
    if (_tread_friction_drops[i] <= 0.0)
      paramError("tread_friction_drops", "Drops must be > 0.");
    if (_tread_slip_distances[i] <= 0.0)
      paramError("tread_slip_distances", "Distances must be > 0.");
    if (_tread_exponents[i] < 1.0)
      paramError("tread_exponents", "Exponents must be >= 1.");
    if (i > 0 && _tread_onset_slips[i] <= _tread_onset_slips[i - 1])
      paramError("tread_onset_slips", "Onsets must be strictly increasing.");
  }

  if (_stability_reference_normal_stress > 0.0 && _communicator.rank() == 0)
  {
    const Real w_max = maxWeakeningSlope(_stability_reference_normal_stress);
    std::ostringstream oss;
    oss << name() << ": peak quasi-static weakening slope W_max = " << w_max
        << " Pa/m at sigma'_n = " << _stability_reference_normal_stress << " Pa";
    if (_system_shear_stiffness > 0.0)
    {
      const Real ratio = w_max / _system_shear_stiffness;
      oss << "; W_max / k_tau = " << ratio
          << (ratio < 1.0 ? "  (< 1: arrested staircase / SW-S4-type response)"
                          : "  (> 1: dynamic burst / SW-S3-type response)");
    }
    mooseInfo(oss.str());
  }
}

void
ADOrcaPeakShelfTailFlowRSFContactTraction::initQpStatefulProperties()
{
  OrcaCZMComputeLocalTractionIncrementalBase::initQpStatefulProperties();

  _fracture_state[_qp] = static_cast<Real>(FractureState::Stick);
  _limit_tau[_qp] = 0.0;
  _plastic_slip_increment[_qp] = 0.0;
  _dilation_jump_increment[_qp] = 0.0;
  _cumulative_plastic_slip[_qp] = 0.0;
  _roughness_state[_qp] = _roughness_state_initial;
  _roughness_damage[_qp] = 1.0 - _roughness_state_initial;
  _friction_coefficient_effective[_qp] = _peak_friction_coefficient;
  _cohesion_effective[_qp] = _apparent_cohesion;
  _dilation_angle_effective[_qp] =
      std::atan(_dilation_work_fraction * _peak_friction_coefficient) * 180.0 / pst_pi;
  _dilation_state[_qp] = _dilation_work_fraction * _peak_friction_coefficient;
  _dilation_support_factor[_qp] = 1.0;
  _strength_normal_memory_magnitude[_qp] = 0.0;
  _strength_normal_memory[_qp] = 0.0;
  _retained_shear_support[_qp] = 0.0;
  _normal_plastic_jump[_qp] = 0.0;
  _irreversible_dilation[_qp] = 0.0;
  _normal_contact_pressure[_qp] = 0.0;
  _reversible_normal_opening[_qp] = 0.0;
  _normal_opening_total[_qp] = 0.0;
  _maximum_reversible_normal_opening[_qp] = 0.0;
  _rate_state_theta[_qp] = _rsf_theta0 > 0.0 ? _rsf_theta0 : _rsf_Dc / _rsf_V0;
  _frictional_sliding_work_increment[_qp] = 0.0;
  _dilation_work_increment[_qp] = 0.0;
  _frictional_dilatant_dissipation_increment[_qp] = 0.0;
  _cohesive_dissipation_increment[_qp] = 0.0;
  _plastic_tangential_jump[_qp] = RealVectorValue(0.0, 0.0, 0.0);
}

ADReal
ADOrcaPeakShelfTailFlowRSFContactTraction::smoothPositive(const ADReal & x, const Real eps) const
{
  return smoothPos(x, eps);
}

Real
ADOrcaPeakShelfTailFlowRSFContactTraction::smoothPositiveReal(const Real x, const Real eps) const
{
  return smoothPos(x, eps);
}

void
ADOrcaPeakShelfTailFlowRSFContactTraction::storeReversibleOpening(
    const ADReal & raw_opening, const ADReal & irreversible_opening, const ADReal & cumulative_slip)
{
  const bool retain_opening_history = MetaPhysicL::raw_value(cumulative_slip) >=
                                      _reversible_normal_opening_retention_activation_slip;
  const ADReal maximum_opening =
      retain_opening_history
          ? std::max(ADReal(_maximum_reversible_normal_opening_old[_qp]), raw_opening)
          : raw_opening;
  const ADReal retained_opening =
      raw_opening +
      ADReal(retain_opening_history ? _reversible_normal_opening_retention_fraction : 0.0) *
          (maximum_opening - raw_opening);
  _maximum_reversible_normal_opening[_qp] = maximum_opening;
  _reversible_normal_opening[_qp] = retained_opening;
  _normal_opening_total[_qp] = irreversible_opening + retained_opening;
}

template <typename T>
T
ADOrcaPeakShelfTailFlowRSFContactTraction::weakeningWeight(const T & cumulative_slip,
                                                           const Real slip_distance,
                                                           const Real exponent,
                                                           const Real onset_slip) const
{
  using std::exp;
  using std::pow;
  const T active_slip = std::max(T(0.0), cumulative_slip - T(onset_slip));
  const T x = active_slip / T(slip_distance);
  return exp(-pow(x, T(exponent)));
}

template <typename T>
T
ADOrcaPeakShelfTailFlowRSFContactTraction::weakeningWeightDerivative(const T & cumulative_slip,
                                                                     const Real slip_distance,
                                                                     const Real exponent,
                                                                     const Real onset_slip) const
{
  using std::exp;
  using std::pow;
  if (rawv(cumulative_slip) <= onset_slip)
    return T(0.0);
  const T x = (cumulative_slip - T(onset_slip)) / T(slip_distance);
  const T A = exp(-pow(x, T(exponent)));
  return -A * T(exponent) * pow(x, T(exponent - 1.0)) / T(slip_distance);
}

template <typename T>
void
ADOrcaPeakShelfTailFlowRSFContactTraction::frictionCoefficient(const T & cumulative_slip,
                                                               T & friction,
                                                               T & dfriction_dgamma) const
{
  const T A_c = weakeningWeight(cumulative_slip,
                                _concentration_slip_distance,
                                _concentration_exponent,
                                _concentration_onset_slip);
  const T A_t =
      weakeningWeight(cumulative_slip, _tail_slip_distance, _tail_exponent, _tail_onset_slip);
  const T dA_c = weakeningWeightDerivative(cumulative_slip,
                                           _concentration_slip_distance,
                                           _concentration_exponent,
                                           _concentration_onset_slip);
  const T dA_t = weakeningWeightDerivative(
      cumulative_slip, _tail_slip_distance, _tail_exponent, _tail_onset_slip);

  friction = T(_tail_friction_coefficient) +
             T(_shelf_friction_coefficient - _tail_friction_coefficient) * A_t +
             T(_peak_friction_coefficient - _shelf_friction_coefficient) * A_c;
  dfriction_dgamma = T(_shelf_friction_coefficient - _tail_friction_coefficient) * dA_t +
                     T(_peak_friction_coefficient - _shelf_friction_coefficient) * dA_c;

  if (!_tread_friction_drops.empty())
  {
    for (std::size_t i = 0; i < _tread_friction_drops.size(); ++i)
    {
      const T A_i = weakeningWeight(
          cumulative_slip, _tread_slip_distances[i], _tread_exponents[i], _tread_onset_slips[i]);
      const T dA_i = weakeningWeightDerivative(
          cumulative_slip, _tread_slip_distances[i], _tread_exponents[i], _tread_onset_slips[i]);
      friction -= T(_tread_friction_drops[i]) * (T(1.0) - A_i);
      dfriction_dgamma += T(_tread_friction_drops[i]) * dA_i;
    }
    if (rawv(friction) < 0.0)
    {
      friction = T(0.0);
      dfriction_dgamma = T(0.0);
    }
  }
}

template <typename T>
void
ADOrcaPeakShelfTailFlowRSFContactTraction::dilationCoefficient(const T & friction,
                                                               const T & dfriction_dgamma,
                                                               T & coefficient,
                                                               T & dcoefficient_dgamma) const
{
  if (!_use_dilatancy)
  {
    coefficient = T(0.0);
    dcoefficient_dgamma = T(0.0);
    return;
  }

  const bool floor_active = rawv(friction) < _dilation_friction_coefficient_floor;
  coefficient = T(_dilation_work_fraction) *
                (floor_active ? T(_dilation_friction_coefficient_floor) : friction);
  dcoefficient_dgamma =
      floor_active ? T(0.0) : T(_dilation_work_fraction) * dfriction_dgamma;

  if (_maximum_dilation_coefficient > 0.0 && rawv(coefficient) > _maximum_dilation_coefficient)
  {
    coefficient = T(_maximum_dilation_coefficient);
    dcoefficient_dgamma = T(0.0);
  }
}

template <typename T>
T
ADOrcaPeakShelfTailFlowRSFContactTraction::roughnessState(const T & cumulative_slip) const
{
  // Tie the exported roughness state to the tail (slow, gouge/wear) branch, mirroring
  // the two-stage damage-law convention consumed by the permeability material.
  const T A =
      weakeningWeight(cumulative_slip, _tail_slip_distance, _tail_exponent, _tail_onset_slip);
  return T(_roughness_state_residual) +
         T(_roughness_state_initial - _roughness_state_residual) * A;
}

template <typename T>
T
ADOrcaPeakShelfTailFlowRSFContactTraction::evolveRateStateTheta(const T & gamma,
                                                                const Real theta_old) const
{
  using std::exp;
  if (_dt <= 0.0)
    return T(theta_old);
  const T x = std::max(T(0.0), gamma) / T(_rsf_Dc);
  const T ex = exp(-x);
  const T one_minus_ex_over_x =
      (rawv(x) > 1.0e-8) ? (T(1.0) - ex) / x : (T(1.0) - T(0.5) * x);
  return T(theta_old) * ex + T(_dt) * one_minus_ex_over_x;
}

template <typename T>
ADOrcaPeakShelfTailFlowRSFContactTraction::FlowEval<T>
ADOrcaPeakShelfTailFlowRSFContactTraction::evaluateFlow(const T & gamma,
                                                        const T & tau_trial,
                                                        const T & current_normal_jump,
                                                        const Real old_normal_plastic_jump,
                                                        const Real old_cumulative_slip,
                                                        const Real old_theta) const
{
  using std::exp;
  using std::log;
  using std::sqrt;

  FlowEval<T> f;
  f.cumulative_slip = T(old_cumulative_slip) + gamma;
  frictionCoefficient(f.cumulative_slip, f.friction, f.dfriction_dgamma);

  T dil_coeff, ddil_coeff;
  dilationCoefficient(f.friction, f.dfriction_dgamma, dil_coeff, ddil_coeff);
  f.dilation_coefficient = dil_coeff;
  f.dilation_increment = dil_coeff * gamma;
  const T ddilinc_dgamma = dil_coeff + gamma * ddil_coeff;
  f.normal_plastic_jump = T(old_normal_plastic_jump) + f.dilation_increment;

  const T overlap = f.normal_plastic_jump - current_normal_jump;
  const auto normal_response = OrcaNormalClosure::evaluate(overlap,
                                                           _contact_gap_regularization,
                                                           _use_hyperbolic_normal_closure,
                                                           _penalty_normal,
                                                           _initial_normal_stiffness,
                                                           _maximum_closure,
                                                           _maximum_closure_fraction,
                                                           _normal_closure_stress_exponent,
                                                           _normal_closure_offset);
  f.normal_pressure = normal_response.pressure;
  const T dpressure_dgamma = normal_response.tangent * ddilinc_dgamma;

  // Flow-form regularized rate-and-state shear strength (log-space stable):
  //   tau_rsf = a p asinh(z),  ln z = ln(V/2V0) + [mu_qs + b ln(V0 theta / D_rs)] / a
  const Real theta_safe = std::max(old_theta, 1.0e-30);
  const Real state_term = _rsf_b * std::log(_rsf_V0 * theta_safe / _rsf_Dc);
  const T E = (f.friction + T(state_term)) / T(_rsf_a);
  const T V = gamma / T(_dt);
  const T L = log(V / T(2.0 * _rsf_V0)) + E;

  T asinh_z, w;
  if (rawv(L) > pst_asinh_log_branch)
  {
    asinh_z = L + T(pst_ln2);
    w = T(1.0);
  }
  else
  {
    const T z = exp(L);
    const T root = sqrt(z * z + T(1.0));
    asinh_z = log(z + root);
    w = z / root;
  }

  const T tau_rsf = T(_rsf_a) * f.normal_pressure * asinh_z;
  f.strength = T(_apparent_cohesion) + tau_rsf;
  const T dL_dgamma = T(1.0) / gamma + f.dfriction_dgamma / T(_rsf_a);
  const T dstrength_dgamma = T(_rsf_a) * dpressure_dgamma * asinh_z +
                             T(_rsf_a) * f.normal_pressure * w * dL_dgamma;

  const bool viscous = _tangential_viscosity > 0.0 && _dt > 0.0;
  const T viscous_strength = viscous ? T(_tangential_viscosity / _dt) * gamma : T(0.0);
  const T dviscous_dgamma = viscous ? T(_tangential_viscosity / _dt) : T(0.0);

  f.residual = tau_trial - T(_penalty_tangent) * gamma - f.strength - viscous_strength;
  f.dres_dgamma = -(T(_penalty_tangent) + dstrength_dgamma + dviscous_dgamma);
  f.rate_state_theta = evolveRateStateTheta(gamma, old_theta);
  return f;
}

Real
ADOrcaPeakShelfTailFlowRSFContactTraction::solveFlowRaw(const Real tau_trial,
                                                        const Real current_normal_jump,
                                                        const Real old_normal_plastic_jump,
                                                        const Real old_cumulative_slip,
                                                        const Real old_theta) const
{
  Real lo = 1.0e-30;
  Real hi = tau_trial / _penalty_tangent;
  if (hi <= lo)
    return 0.0;

  const auto effective_residual_tolerance = [&](const FlowEval<Real> & f,
                                                 const Real candidate_gamma)
  {
    const Real viscous_strength =
        (_tangential_viscosity > 0.0 && _dt > 0.0)
            ? std::abs(_tangential_viscosity / _dt * candidate_gamma)
            : 0.0;
    const Real residual_scale =
        std::max(1.0,
                 std::abs(tau_trial) + std::abs(_penalty_tangent * candidate_gamma) +
                     std::abs(f.strength) + viscous_strength);
    return std::max(_local_newton_tolerance,
                    pst_residual_roundoff_factor * std::numeric_limits<Real>::epsilon() *
                        residual_scale);
  };

  // F(lo) <= 0 means even a vanishing creep rate over-carries the trial shear
  // (tau_trial below the apparent cohesion): no slip.
  {
    const FlowEval<Real> f_lo = evaluateFlow<Real>(
        lo, tau_trial, current_normal_jump, old_normal_plastic_jump, old_cumulative_slip, old_theta);
    if (f_lo.residual <= 0.0)
      return 0.0;
  }

  // Quasi-static initial guess, clamped into the bracket.
  Real mu0, dmu0;
  frictionCoefficient(Real(old_cumulative_slip), mu0, dmu0);
  const Real p_trial = OrcaNormalClosure::evaluate(old_normal_plastic_jump - current_normal_jump,
                                                   _contact_gap_regularization,
                                                   _use_hyperbolic_normal_closure,
                                                   _penalty_normal,
                                                   _initial_normal_stiffness,
                                                   _maximum_closure,
                                                   _maximum_closure_fraction,
                                                   _normal_closure_stress_exponent,
                                                   _normal_closure_offset)
                           .pressure;
  Real gamma = (tau_trial - _apparent_cohesion - p_trial * mu0) / _penalty_tangent;
  if (!(gamma > lo && gamma < hi))
    gamma = std::sqrt(lo * hi);

  for (unsigned int i = 0; i < _max_local_newton_iterations; ++i)
  {
    const FlowEval<Real> f = evaluateFlow<Real>(gamma,
                                                tau_trial,
                                                current_normal_jump,
                                                old_normal_plastic_jump,
                                                old_cumulative_slip,
                                                old_theta);
    if (std::abs(f.residual) <= effective_residual_tolerance(f, gamma))
      return gamma;

    if (f.residual > 0.0)
      lo = gamma;
    else
      hi = gamma;

    const Real newton = gamma - f.residual / f.dres_dgamma;
    if (std::isfinite(newton) && newton > lo && newton < hi)
      gamma = newton;
    else
      gamma = std::sqrt(lo * hi); // bisection in log space

    if (hi - lo <= 1.0e-16 * hi)
    {
      const FlowEval<Real> f_collapsed = evaluateFlow<Real>(gamma,
                                                            tau_trial,
                                                            current_normal_jump,
                                                            old_normal_plastic_jump,
                                                            old_cumulative_slip,
                                                            old_theta);
      const Real effective_tolerance = effective_residual_tolerance(f_collapsed, gamma);
      if (std::abs(f_collapsed.residual) <= effective_tolerance)
        return gamma;

      mooseError(name(),
                 ": local FlowRSF bracket collapsed without satisfying the residual tolerance; "
                 "|R|=",
                 std::abs(f_collapsed.residual),
                 ", effective tolerance=",
                 effective_tolerance,
                 ", requested absolute tolerance=",
                 _local_newton_tolerance,
                 ", gamma=",
                 gamma,
                 ". Increase max_local_newton_iterations or revise the regularization.");
    }
  }

  const FlowEval<Real> f_final = evaluateFlow<Real>(gamma,
                                                    tau_trial,
                                                    current_normal_jump,
                                                    old_normal_plastic_jump,
                                                    old_cumulative_slip,
                                                    old_theta);
  const Real effective_tolerance = effective_residual_tolerance(f_final, gamma);
  mooseError(name(),
             ": local FlowRSF solve exhausted max_local_newton_iterations without convergence; "
             "|R|=",
             std::abs(f_final.residual),
             ", effective tolerance=",
             effective_tolerance,
             ", requested absolute tolerance=",
             _local_newton_tolerance,
             ", gamma=",
             gamma,
             ". The constitutive update is not admissible for validation output.");
}

Real
ADOrcaPeakShelfTailFlowRSFContactTraction::maxWeakeningSlope(const Real sigma_n_ref) const
{
  Real s_end =
      3.0 * (_concentration_slip_distance + _tail_slip_distance) + _concentration_onset_slip +
      _tail_onset_slip;
  for (std::size_t i = 0; i < _tread_friction_drops.size(); ++i)
    s_end = std::max(s_end, _tread_onset_slips[i] + 3.0 * _tread_slip_distances[i]);
  const unsigned int n = 3000;
  Real w_max = 0.0;
  for (unsigned int i = 0; i <= n; ++i)
  {
    const Real s = s_end * static_cast<Real>(i) / static_cast<Real>(n);
    Real mu, dmu;
    frictionCoefficient(s, mu, dmu);
    w_max = std::max(w_max, -dmu * sigma_n_ref);
  }
  return w_max;
}

void
ADOrcaPeakShelfTailFlowRSFContactTraction::computeInterfaceTractionIncrement()
{
  const ADRealVectorValue & jump = _interface_displacement_jump[_qp];
  const RealVectorValue traction_old(_interface_traction_old[_qp]);
  const Real old_cumulative_slip = _cumulative_plastic_slip_old[_qp];
  const Real old_normal_plastic_jump = _normal_plastic_jump_old[_qp];
  const Real old_theta = _rate_state_theta_old[_qp];

  ADReal old_mu, old_dmu;
  frictionCoefficient(ADReal(old_cumulative_slip), old_mu, old_dmu);

  const ADReal contact_overlap_trial = ADReal(old_normal_plastic_jump) - jump(0);
  const ADReal active_overlap =
      contact_overlap_trial +
      ADReal(_use_hyperbolic_normal_closure ? _normal_closure_offset : 0.0);
  const bool contact_active =
      MetaPhysicL::raw_value(active_overlap) > _opening_gap_tolerance;
  const ADReal pressure_trial =
      contact_active
          ? OrcaNormalClosure::evaluate(contact_overlap_trial,
                                        _contact_gap_regularization,
                                        _use_hyperbolic_normal_closure,
                                        _penalty_normal,
                                        _initial_normal_stiffness,
                                        _maximum_closure,
                                        _maximum_closure_fraction,
                                        _normal_closure_stress_exponent,
                                        _normal_closure_offset)
                .pressure
          : ADReal(0.0);

  ADRealVectorValue traction_new(0.0, 0.0, 0.0);

  _plastic_slip_increment[_qp] = 0.0;
  _dilation_jump_increment[_qp] = 0.0;
  _cumulative_plastic_slip[_qp] = ADReal(old_cumulative_slip);
  _normal_plastic_jump[_qp] = ADReal(old_normal_plastic_jump);
  _irreversible_dilation[_qp] = ADReal(old_normal_plastic_jump);
  _normal_contact_pressure[_qp] = pressure_trial;
  _strength_normal_memory_magnitude[_qp] = pressure_trial;
  _strength_normal_memory[_qp] = -pressure_trial;
  _retained_shear_support[_qp] = 0.0;
  _friction_coefficient_effective[_qp] = old_mu;
  _cohesion_effective[_qp] = _apparent_cohesion;
  _dilation_support_factor[_qp] = 1.0;
  // Aging-law healing at (numerically) zero slip rate: theta grows by dt during
  // holds and while open. (The referenced-RSF damage laws freeze theta on stick.)
  _rate_state_theta[_qp] = evolveRateStateTheta(ADReal(0.0), old_theta);
  _frictional_sliding_work_increment[_qp] = 0.0;
  _dilation_work_increment[_qp] = 0.0;
  _frictional_dilatant_dissipation_increment[_qp] = 0.0;
  _cohesive_dissipation_increment[_qp] = 0.0;
  _plastic_tangential_jump[_qp] =
      ADRealVectorValue(ADReal(0.0),
                        ADReal(_plastic_tangential_jump_old[_qp](1)),
                        ADReal(_plastic_tangential_jump_old[_qp](2)));

  const ADReal R_old = roughnessState(ADReal(old_cumulative_slip));
  _roughness_state[_qp] = R_old;
  _roughness_damage[_qp] = ADReal(1.0) - R_old;
  ADReal old_dil_coeff, old_ddil_coeff;
  dilationCoefficient(old_mu, old_dmu, old_dil_coeff, old_ddil_coeff);
  _dilation_state[_qp] = old_dil_coeff;
  _dilation_angle_effective[_qp] = atan(old_dil_coeff) * ADReal(180.0 / pst_pi);

  if (!contact_active)
  {
    _fracture_state[_qp] = static_cast<Real>(FractureState::Open);
    _limit_tau[_qp] = 0.0;
    storeReversibleOpening(
        ADReal(0.0), ADReal(old_normal_plastic_jump), ADReal(old_cumulative_slip));
    _interface_traction_inc[_qp] =
        traction_new - ADRealVectorValue(ADReal(traction_old(0)),
                                         ADReal(traction_old(1)),
                                         ADReal(traction_old(2)));
    return;
  }

  traction_new(0) = -pressure_trial;

  const ADReal tangential_trial_1 =
      ADReal(_penalty_tangent) * (jump(1) - ADReal(_plastic_tangential_jump_old[_qp](1)));
  const ADReal tangential_trial_2 =
      ADReal(_penalty_tangent) * (jump(2) - ADReal(_plastic_tangential_jump_old[_qp](2)));
  const ADReal tau_trial =
      sqrt(tangential_trial_1 * tangential_trial_1 + tangential_trial_2 * tangential_trial_2);

  _limit_tau[_qp] = ADReal(_apparent_cohesion) + pressure_trial * old_mu;

  if (MetaPhysicL::raw_value(tau_trial) <= _tangential_traction_tolerance || _dt <= 0.0)
  {
    traction_new(1) = tangential_trial_1;
    traction_new(2) = tangential_trial_2;
    _fracture_state[_qp] = static_cast<Real>(FractureState::Stick);
    const ADReal reversible_opening =
        (ADReal(_reversible_normal_compliance) +
         ADReal(_damage_scaled_reversible_compliance) * ADReal(old_normal_plastic_jump)) *
        smoothPositive(ADReal(_reversible_normal_reference_stress) - pressure_trial,
                       _stress_regularization);
    storeReversibleOpening(
        reversible_opening, ADReal(old_normal_plastic_jump), ADReal(old_cumulative_slip));
    _interface_traction_inc[_qp] =
        traction_new - ADRealVectorValue(ADReal(traction_old(0)),
                                         ADReal(traction_old(1)),
                                         ADReal(traction_old(2)));
    return;
  }

  // ---- flow solve: raw safeguarded Newton, then AD implicit-function correctors ----
  const Real gamma_raw = solveFlowRaw(MetaPhysicL::raw_value(tau_trial),
                                      MetaPhysicL::raw_value(jump(0)),
                                      old_normal_plastic_jump,
                                      old_cumulative_slip,
                                      old_theta);

  // Stick-velocity floor: sub-floor creep carries no physics (< ~1 nm/min) but its
  // log-curvature length gamma* = V*dt drops below the global Newton excursion scale,
  // flooring |R| at ~K_t*A*gamma* (dt-independent stagnation once the load ramp ends
  // and |R|_0 collapses). Below the blend window take an exact elastic step; the
  // V=0 aging update for theta set above stays in effect.
  if (_stick_velocity_floor > 0.0 &&
      gamma_raw <= _dt * _stick_velocity_floor / pst_stick_blend_ratio)
  {
    traction_new(1) = tangential_trial_1;
    traction_new(2) = tangential_trial_2;
    _fracture_state[_qp] = static_cast<Real>(FractureState::Stick);
    const ADReal reversible_opening =
        (ADReal(_reversible_normal_compliance) +
         ADReal(_damage_scaled_reversible_compliance) * ADReal(old_normal_plastic_jump)) *
        smoothPositive(ADReal(_reversible_normal_reference_stress) - pressure_trial,
                       _stress_regularization);
    storeReversibleOpening(
        reversible_opening, ADReal(old_normal_plastic_jump), ADReal(old_cumulative_slip));
    _interface_traction_inc[_qp] =
        traction_new - ADRealVectorValue(ADReal(traction_old(0)),
                                         ADReal(traction_old(1)),
                                         ADReal(traction_old(2)));
    return;
  }

  const ADReal gamma_upper = tau_trial / ADReal(_penalty_tangent);
  ADReal gamma = ADReal(std::max(gamma_raw, 1.0e-30));
  for (unsigned int c = 0; c < 2; ++c)
  {
    const FlowEval<ADReal> f = evaluateFlow<ADReal>(gamma,
                                                    tau_trial,
                                                    jump(0),
                                                    old_normal_plastic_jump,
                                                    old_cumulative_slip,
                                                    old_theta);
    const ADReal corr = -f.residual / f.dres_dgamma;
    if (!std::isfinite(MetaPhysicL::raw_value(corr)))
      break;
    gamma += corr;
    if (MetaPhysicL::raw_value(gamma) < 1.0e-30)
      gamma = 1.0e-30;
    if (MetaPhysicL::raw_value(gamma) > MetaPhysicL::raw_value(gamma_upper))
      gamma = gamma_upper;
  }

  // Half-decade smoothstep in ln V bridging to the exact-stick branch: s = 0 at
  // V_floor/r and s = 1 at V_floor*r (r = 10^{1/4}), so the branch switch above is
  // value- and slope-continuous. Everything downstream (dilation, theta, work,
  // exports) sees the blended increment.
  if (_stick_velocity_floor > 0.0 &&
      MetaPhysicL::raw_value(gamma) < _dt * _stick_velocity_floor * pst_stick_blend_ratio)
  {
    const Real gamma_lo = _dt * _stick_velocity_floor / pst_stick_blend_ratio;
    const ADReal x =
        log(gamma / ADReal(gamma_lo)) / ADReal(2.0 * std::log(pst_stick_blend_ratio));
    if (MetaPhysicL::raw_value(x) <= 0.0)
      gamma = ADReal(1.0e-30); // correctors dipped below the raw-branch cut: ~stick
    else
      gamma *= x * x * (ADReal(3.0) - ADReal(2.0) * x);
    if (MetaPhysicL::raw_value(gamma) < 1.0e-30)
      gamma = ADReal(1.0e-30);
  }

  const FlowEval<ADReal> final_state = evaluateFlow<ADReal>(gamma,
                                                            tau_trial,
                                                            jump(0),
                                                            old_normal_plastic_jump,
                                                            old_cumulative_slip,
                                                            old_theta);

  ADRealVectorValue slip_direction(0.0, 0.0, 0.0);
  slip_direction(1) = tangential_trial_1 / tau_trial;
  slip_direction(2) = tangential_trial_2 / tau_trial;

  const ADRealVectorValue plastic_tangential_jump_new(
      ADReal(0.0),
      ADReal(_plastic_tangential_jump_old[_qp](1)) + gamma * slip_direction(1),
      ADReal(_plastic_tangential_jump_old[_qp](2)) + gamma * slip_direction(2));

  const ADReal branch_traction_1 =
      ADReal(_penalty_tangent) * (jump(1) - plastic_tangential_jump_new(1));
  const ADReal branch_traction_2 =
      ADReal(_penalty_tangent) * (jump(2) - plastic_tangential_jump_new(2));

  traction_new(0) = -final_state.normal_pressure;
  traction_new(1) = branch_traction_1;
  traction_new(2) = branch_traction_2;

  const Real V_report = MetaPhysicL::raw_value(gamma) / _dt;
  _fracture_state[_qp] = static_cast<Real>(V_report > _stick_report_velocity
                                               ? FractureState::Slip
                                               : FractureState::Stick);
  _plastic_slip_increment[_qp] = gamma;
  _dilation_jump_increment[_qp] = final_state.dilation_increment;
  _cumulative_plastic_slip[_qp] = final_state.cumulative_slip;
  _normal_plastic_jump[_qp] = final_state.normal_plastic_jump;
  _irreversible_dilation[_qp] = final_state.normal_plastic_jump;
  _normal_contact_pressure[_qp] = final_state.normal_pressure;
  _strength_normal_memory_magnitude[_qp] = final_state.normal_pressure;
  _strength_normal_memory[_qp] = -final_state.normal_pressure;
  _limit_tau[_qp] = final_state.strength;
  _friction_coefficient_effective[_qp] = final_state.friction;
  _cohesion_effective[_qp] = ADReal(_apparent_cohesion);
  _dilation_state[_qp] = final_state.dilation_coefficient;
  _dilation_angle_effective[_qp] =
      atan(final_state.dilation_coefficient) * ADReal(180.0 / pst_pi);
  _dilation_support_factor[_qp] = 1.0;
  const ADReal R_new = roughnessState(final_state.cumulative_slip);
  _roughness_state[_qp] = R_new;
  _roughness_damage[_qp] = ADReal(1.0) - R_new;
  _rate_state_theta[_qp] = final_state.rate_state_theta;
  _plastic_tangential_jump[_qp] = plastic_tangential_jump_new;

  const ADReal tau_final =
      sqrt(branch_traction_1 * branch_traction_1 + branch_traction_2 * branch_traction_2);
  _frictional_sliding_work_increment[_qp] = tau_final * gamma;
  _dilation_work_increment[_qp] =
      final_state.normal_pressure * final_state.dilation_increment;
  _frictional_dilatant_dissipation_increment[_qp] =
      _frictional_sliding_work_increment[_qp] - _dilation_work_increment[_qp];
  _cohesive_dissipation_increment[_qp] = ADReal(_apparent_cohesion) * gamma;

  const ADReal reversible_opening =
      (ADReal(_reversible_normal_compliance) +
       ADReal(_damage_scaled_reversible_compliance) * final_state.normal_plastic_jump) *
      smoothPositive(ADReal(_reversible_normal_reference_stress) - final_state.normal_pressure,
                     _stress_regularization);
  storeReversibleOpening(
      reversible_opening, final_state.normal_plastic_jump, final_state.cumulative_slip);

  _interface_traction_inc[_qp] =
      traction_new - ADRealVectorValue(ADReal(traction_old(0)),
                                       ADReal(traction_old(1)),
                                       ADReal(traction_old(2)));
}
