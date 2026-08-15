#include "ADOrcaBartonBandisFlowRSFContactTraction.h"
#include "OrcaNormalClosure.h"

#include "metaphysicl/raw_type.h"

#include <algorithm>
#include <cmath>
#include <limits>
#include <sstream>

registerMooseObject("OrcaApp", ADOrcaBartonBandisFlowRSFContactTraction);
registerMooseObjectAliased("OrcaApp",
                           ADOrcaBartonBandisFlowRSFContactTraction,
                           "OrcaBartonBandisFlowRSFContactTraction");

namespace
{
constexpr Real bbf_pi = 3.141592653589793238462643383279502884;
constexpr Real bbf_deg_to_rad = bbf_pi / 180.0;
constexpr Real bbf_ln10 = 2.302585092994045684;
constexpr Real bbf_ln2 = 0.6931471805599453094;
// Above this value of L = ln(z) the exact asinh(z) = ln(z + sqrt(z^2+1)) equals
// L + ln 2 to double precision (relative error ~ e^{-2L} < 1e-17), and z^2 would
// eventually overflow; switch to the logarithmic branch.
constexpr Real bbf_asinh_log_branch = 20.0;
// 10^{1/4}: the stick-velocity floor blends to the exact-stick branch over half a
// decade of slip velocity, [V_floor/r, V_floor*r], via a smoothstep in ln V.
constexpr Real bbf_stick_blend_ratio = 1.7782794100389228;
// Smoothing widths of the non-negative roughness-angle floor and of the friction/
// dilation angle caps [degrees]; the floor/cap corners are outside the calibrated
// operating range, the smoothing only keeps the local solve C1 if they are reached.
constexpr Real bbf_angle_floor_eps_deg = 0.01;
constexpr Real bbf_angle_cap_width_deg = 1.0;
// The flow residual subtracts several traction-scale terms. Once their cancellation
// reaches this multiple of machine epsilon, further local iterations cannot improve
// gamma. This is a numerical acceptance floor, not a constitutive tolerance.
constexpr Real bbf_residual_roundoff_factor = 64.0;

inline Real
bbfRaw(Real x)
{
  return x;
}
inline Real
bbfRaw(const ADReal & x)
{
  return MetaPhysicL::raw_value(x);
}

template <typename T>
T
bbfSmoothPos(const T & x, const Real eps)
{
  using std::sqrt;
  return T(0.5) * (x + sqrt(x * x + T(eps * eps)));
}

template <typename T>
T
bbfSmoothPosDeriv(const T & x, const Real eps)
{
  using std::sqrt;
  return T(0.5) * (T(1.0) + x / sqrt(x * x + T(eps * eps)));
}

template <typename T>
T
softplusT(const T & t)
{
  using std::exp;
  using std::log;
  if (bbfRaw(t) > 30.0)
    return t;
  if (bbfRaw(t) < -30.0)
    return exp(t);
  return log(T(1.0) + exp(t));
}

template <typename T>
T
sigmoidT(const T & t)
{
  using std::exp;
  if (bbfRaw(t) > 30.0)
    return T(1.0);
  if (bbfRaw(t) < -30.0)
    return exp(t);
  return T(1.0) / (T(1.0) + exp(-t));
}

/// Smooth min(a, cap) with transition width w: exact for a << cap, asymptotes to cap.
template <typename T>
T
smoothCapMin(const T & a, const Real cap, const Real w)
{
  return a - T(w) * softplusT((a - T(cap)) / T(w));
}

template <typename T>
T
smoothCapMinDerivative(const T & a, const Real cap, const Real w)
{
  return T(1.0) - sigmoidT((a - T(cap)) / T(w));
}

/// delta_p: user value if > 0, else Barton's (1982) estimate (L/500)(JRC_n/L)^0.33.
Real
resolvePeakShearDisplacement(Real user_value, Real joint_length, Real jrc_scaled)
{
  if (user_value > 0.0)
    return user_value;
  if (jrc_scaled <= 0.0)
    return 0.0;
  return (joint_length / 500.0) * std::pow(jrc_scaled / joint_length, 0.33);
}
}

InputParameters
ADOrcaBartonBandisFlowRSFContactTraction::validParams()
{
  InputParameters params = OrcaCZMComputeLocalTractionIncrementalBase::validParams();
  params.addClassDescription(
      "Barton--Bandis joint friction (phi_r + JRC_mob log10(JCS/sigma_n), Barton 1982 "
      "post-peak JRC mobilization table, laboratory->field scale corrections, mobilized "
      "Barton dilation) driving the flow-form (always-creeping) regularized rate-and-state "
      "solve of the peak-shelf-tail law. Exports the same CZM property names as the PST / "
      "cohesionless damage MC laws.");

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
      "Requested absolute residual tolerance [Pa] for the scalar flow solve. The effective "
      "tolerance is the larger of this value and a scale-aware floating-point roundoff floor.");
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

  params.addRangeCheckedParam<Real>(
      "jrc", 10.0, "jrc >= 0.0", "Laboratory joint roughness coefficient JRC0.");
  params.addRangeCheckedParam<Real>(
      "jcs", 1e8, "jcs > 0.0", "Laboratory joint wall compressive strength JCS0 [Pa].");
  params.addRangeCheckedParam<Real>(
      "residual_friction_angle_degrees",
      30.0,
      "residual_friction_angle_degrees >= 0.0 & residual_friction_angle_degrees < 89.0",
      "Residual friction angle phi_r [degrees]; the strength floor reached when JRC_mob "
      "has fully decayed (x = delta/delta_p >= 100 in Barton's 1982 table).");
  params.addParam<bool>("use_scale_correction",
                        true,
                        "Apply the Barton--Bandis (1982) laboratory->field scale corrections "
                        "JRC_n = JRC0 (Ln/L0)^(-0.02 JRC0), JCS_n = JCS0 (Ln/L0)^(-0.03 JRC0).");
  params.addRangeCheckedParam<Real>(
      "laboratory_length", 0.1, "laboratory_length > 0.0", "Laboratory sample length L0 [m].");
  params.addRangeCheckedParam<Real>(
      "joint_length", 0.1, "joint_length > 0.0", "In-situ joint/block length Ln [m].");
  params.addRangeCheckedParam<Real>(
      "peak_shear_displacement",
      0.0,
      "peak_shear_displacement >= 0.0",
      "Barton mobilization peak displacement delta_p [m]; the slip scale of the JRC "
      "mobilization table (residual is reached at 100 delta_p). Zero computes Barton's "
      "(1982) estimate (L/500)(JRC_n/L)^0.33 with L = joint_length. NOTE: for the "
      "Ye2018 saw-cut calibrations delta_p is a fitted parameter (~1e-5 m), far below "
      "Barton's mm-scale estimate for natural joints.");
  params.addRangeCheckedParam<Real>(
      "mobilization_onset_slip",
      0.0,
      "mobilization_onset_slip >= 0.0",
      "Plastic slip [m] below which JRC_mob stays at JRC_n (post-peak decay starts only "
      "beyond it): x = 1 + <s - s0>/delta_p. Physically: near-peak plastic slip that does "
      "not yet damage the interlocked asperities (Barton's pre-peak plasticity). Without "
      "it the table's steepest decay sits at s = 0+, so the first micron of flow-form "
      "creep self-accelerates and onset fires far too early on an initially stressed "
      "fault (measured on deck 57_01: onset t = 411 s vs data 1024 s).");
  params.addParam<std::vector<Real>>(
      "mobilization_shelf_onsets",
      std::vector<Real>(),
      "Optional multi-shelf staircase: cumulative-slip values [m] at which JRC mobilization "
      "FREEZES (the table's effective slip stops accruing) for the width of the matching "
      "mobilization_shelf_widths entry, then resumes. A single (delta_p, onset) pair cannot "
      "both pace the injection staircase and reach full residual inside the test (the "
      "one-delta_p dilemma, deck 57_03): shelves cut the table into tread cliffs, each "
      "supplying its own strength drop and arresting at frozen JRC_mob until the next "
      "pressure step re-mobilizes it. Because each tread then slips at a HIGHER mobilized "
      "JRC than a terminal cliff would, the mobilized dilation integral also rises toward "
      "the data (the deck-57_03 plastic-dilation deficit). Onsets must be strictly "
      "increasing, each past the previous shelf's end, and lie at or beyond "
      "mobilization_onset_slip. Empty disables (default table unchanged).");
  params.addParam<std::vector<Real>>(
      "mobilization_shelf_widths",
      std::vector<Real>(),
      "Slip width [m] of each mobilization freeze shelf (same length as "
      "mobilization_shelf_onsets, each > 0).");
  params.addRangeCheckedParam<Real>(
      "compressive_normal_stress_floor",
      1e3,
      "compressive_normal_stress_floor > 0.0",
      "Floor [Pa] on the sigma'_n argument of log10(JCS/sigma'_n) (angle arguments only; "
      "the multiplicative sigma'_n in the strength is never floored).");
  params.addRangeCheckedParam<Real>(
      "max_friction_angle_degrees",
      85.0,
      "max_friction_angle_degrees > 0.0 & max_friction_angle_degrees < 89.9",
      "Smooth cap on the total friction angle phi_r + JRC_mob log10(JCS/sigma'_n).");
  params.addRangeCheckedParam<Real>(
      "apparent_cohesion",
      0.0,
      "apparent_cohesion >= 0.0",
      "Optional constant apparent shear cohesion c [Pa]; the Barton--Bandis envelope is "
      "cohesionless, keep 0 unless bridging decks.");
  params.addRangeCheckedParam<Real>(
      "late_friction_angle_increment_degrees",
      0.0,
      "late_friction_angle_increment_degrees >= 0.0",
      "Optional asymptotic friction-angle increment [degrees] activated only after "
      "late_friction_onset_slip. It separates late-event arrest from the residual "
      "friction angle that controls the onset envelope; zero preserves the legacy law.");
  params.addRangeCheckedParam<Real>(
      "late_friction_onset_slip",
      0.0,
      "late_friction_onset_slip >= 0.0",
      "Cumulative plastic slip [m] at which the optional late friction increment starts.");
  params.addRangeCheckedParam<Real>(
      "late_friction_distance",
      1.0e-5,
      "late_friction_distance > 0.0",
      "Characteristic cumulative-slip distance [m] for the late friction increment.");
  params.addRangeCheckedParam<Real>(
      "late_friction_exponent",
      2.0,
      "late_friction_exponent >= 1.0",
      "Exponent in H=1-exp(-((s-s_late)/D_late)^m) for the late friction increment.");
  params.addRangeCheckedParam<Real>(
      "late_tangential_viscosity",
      0.0,
      "late_tangential_viscosity >= 0.0",
      "Optional asymptotic late-slip viscosity [Pa.s/m]. It multiplies slip rate rather than "
      "permanently raising the friction envelope, so it can suppress excessive unloading creep "
      "without biasing the terminal quasi-static shear strength. Zero preserves legacy behavior.");
  params.addRangeCheckedParam<Real>(
      "late_tangential_viscosity_onset_slip",
      0.0,
      "late_tangential_viscosity_onset_slip >= 0.0",
      "Cumulative plastic slip [m] at which late tangential viscosity starts.");
  params.addRangeCheckedParam<Real>(
      "late_tangential_viscosity_distance",
      1.0e-5,
      "late_tangential_viscosity_distance > 0.0",
      "Characteristic cumulative-slip distance [m] for activation of late viscosity.");
  params.addRangeCheckedParam<Real>(
      "late_tangential_viscosity_exponent",
      2.0,
      "late_tangential_viscosity_exponent >= 1.0",
      "Exponent in H=1-exp(-((s-s_eta)/D_eta)^m) for late viscosity.");
  params.addRangeCheckedParam<Real>(
      "late_tangential_viscosity_release_slip",
      0.0,
      "late_tangential_viscosity_release_slip >= 0.0",
      "Optional cumulative plastic slip [m] at which the late viscosity starts to release. "
      "Zero disables release and preserves the monotone Level-81 branch exactly. When enabled, "
      "the activation weight is multiplied by exp(-((s-s_release)/D_release)^m_release)) after "
      "s_release, producing a finite damping window without a terminal viscous-strength bias.");
  params.addRangeCheckedParam<Real>(
      "late_tangential_viscosity_release_distance",
      1.0e-5,
      "late_tangential_viscosity_release_distance > 0.0",
      "Characteristic cumulative-slip distance [m] for releasing late viscosity.");
  params.addRangeCheckedParam<Real>(
      "late_tangential_viscosity_release_exponent",
      2.0,
      "late_tangential_viscosity_release_exponent >= 1.0",
      "Exponent in exp(-((s-s_release)/D_release)^m_release) for late-viscosity release.");

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
      "dilation_factor",
      0.5,
      "dilation_factor >= 0.0",
      "Multiplier on the mobilized roughness angle for dilation: psi_mob = dilation_factor "
      "* JRC_mob * log10(JCS/sigma'_n) [deg]. Barton's damage coefficient M enters as "
      "1/M (0.5 standard laboratory value).");
  params.addRangeCheckedParam<Real>(
      "min_dilation_angle_degrees",
      0.0,
      "min_dilation_angle_degrees >= 0.0 & min_dilation_angle_degrees < 89.9",
      "Optional smooth floor on the mobilized dilation angle (0 = pure Barton decay: "
      "dilation dies with JRC_mob). A positive floor sustains wear/bulking dilation after "
      "mobilization decay (the SW-S3 constant-slope calibration uses floor = cap).");
  params.addRangeCheckedParam<Real>(
      "max_dilation_angle_degrees",
      30.0,
      "max_dilation_angle_degrees >= 0.0 & max_dilation_angle_degrees < 89.9",
      "Smooth cap on the mobilized dilation angle.");

  params.addRangeCheckedParam<Real>(
      "roughness_state_initial",
      0.45,
      "roughness_state_initial >= 0.0 & roughness_state_initial <= 1.0",
      "Exported roughness_state at full JRC mobilization (JRC_mob = JRC_n).");
  params.addRangeCheckedParam<Real>(
      "roughness_state_residual",
      0.10,
      "roughness_state_residual >= 0.0 & roughness_state_residual <= 1.0",
      "Exported roughness_state after full JRC decay (JRC_mob = 0).");

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
      "recompression. This is output-only; zero preserves the legacy response.");
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

ADOrcaBartonBandisFlowRSFContactTraction::ADOrcaBartonBandisFlowRSFContactTraction(
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
    _jrc0(getParam<Real>("jrc")),
    _jcs0(getParam<Real>("jcs")),
    _residual_friction_angle_deg(getParam<Real>("residual_friction_angle_degrees")),
    _use_scale_correction(getParam<bool>("use_scale_correction")),
    _laboratory_length(getParam<Real>("laboratory_length")),
    _joint_length(getParam<Real>("joint_length")),
    _jrc_scaled(_use_scale_correction
                    ? _jrc0 * std::pow(_joint_length / _laboratory_length, -0.02 * _jrc0)
                    : _jrc0),
    _jcs_scaled(_use_scale_correction
                    ? _jcs0 * std::pow(_joint_length / _laboratory_length, -0.03 * _jrc0)
                    : _jcs0),
    _peak_shear_displacement(resolvePeakShearDisplacement(
        getParam<Real>("peak_shear_displacement"), _joint_length, _jrc_scaled)),
    _mobilization_onset_slip(getParam<Real>("mobilization_onset_slip")),
    _mobilization_shelf_onsets(getParam<std::vector<Real>>("mobilization_shelf_onsets")),
    _mobilization_shelf_widths(getParam<std::vector<Real>>("mobilization_shelf_widths")),
    _compressive_normal_stress_floor(getParam<Real>("compressive_normal_stress_floor")),
    _max_friction_angle_deg(getParam<Real>("max_friction_angle_degrees")),
    _apparent_cohesion(getParam<Real>("apparent_cohesion")),
    _late_friction_angle_increment_deg(getParam<Real>("late_friction_angle_increment_degrees")),
    _late_friction_onset_slip(getParam<Real>("late_friction_onset_slip")),
    _late_friction_distance(getParam<Real>("late_friction_distance")),
    _late_friction_exponent(getParam<Real>("late_friction_exponent")),
    _late_tangential_viscosity(getParam<Real>("late_tangential_viscosity")),
    _late_tangential_viscosity_onset_slip(getParam<Real>("late_tangential_viscosity_onset_slip")),
    _late_tangential_viscosity_distance(getParam<Real>("late_tangential_viscosity_distance")),
    _late_tangential_viscosity_exponent(getParam<Real>("late_tangential_viscosity_exponent")),
    _late_tangential_viscosity_release_slip(
        getParam<Real>("late_tangential_viscosity_release_slip")),
    _late_tangential_viscosity_release_distance(
        getParam<Real>("late_tangential_viscosity_release_distance")),
    _late_tangential_viscosity_release_exponent(
        getParam<Real>("late_tangential_viscosity_release_exponent")),
    _rsf_a(getParam<Real>("rsf_a")),
    _rsf_b(getParam<Real>("rsf_b")),
    _rsf_Dc(getParam<Real>("rsf_Dc")),
    _rsf_V0(getParam<Real>("rsf_V0")),
    _rsf_theta0(getParam<Real>("rsf_theta0")),
    _stick_report_velocity(getParam<Real>("stick_report_velocity")),
    _stick_velocity_floor(getParam<Real>("stick_velocity_floor")),
    _use_dilatancy(getParam<bool>("use_dilatancy")),
    _dilation_factor(getParam<Real>("dilation_factor")),
    _min_dilation_angle_deg(getParam<Real>("min_dilation_angle_degrees")),
    _max_dilation_angle_deg(getParam<Real>("max_dilation_angle_degrees")),
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
    _bb_jrc_mobilized(declareADProperty<Real>(_base_name + "bb_jrc_mobilized")),
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

  if (_peak_shear_displacement <= 0.0)
    paramError("peak_shear_displacement",
               "Resolved delta_p is zero; set peak_shear_displacement > 0 or jrc > 0.");
  if (_min_dilation_angle_deg > _max_dilation_angle_deg)
    paramError("min_dilation_angle_degrees", "Must be <= max_dilation_angle_degrees.");
  if (_roughness_state_residual > _roughness_state_initial)
    paramError("roughness_state_residual", "Must be <= roughness_state_initial.");
  if (_stick_velocity_floor > _stick_report_velocity)
    paramError("stick_velocity_floor",
               "Must be <= stick_report_velocity so the numerical stick branch cannot be "
               "classified as physical creep in the reported fracture state.");
  if (_late_tangential_viscosity > 0.0 &&
      _late_tangential_viscosity_release_slip > 0.0 &&
      _late_tangential_viscosity_release_slip <= _late_tangential_viscosity_onset_slip)
    paramError("late_tangential_viscosity_release_slip",
               "Must be greater than late_tangential_viscosity_onset_slip when the optional "
               "finite viscosity window is enabled.");

  // Barton (1982) post-peak mobilization table, monotone (Fritsch--Carlson) cubic in
  // u = log10(x); the end slope is forced to 0 for a C1 landing on the residual plateau.
  const Real xk[6] = {1.0, 2.0, 4.0, 10.0, 25.0, 100.0};
  const Real yk[6] = {1.00, 0.85, 0.70, 0.50, 0.40, 0.00};
  Real h[5], d[5];
  for (unsigned int i = 0; i < 6; ++i)
  {
    _mob_u[i] = std::log10(xk[i]);
    _mob_y[i] = yk[i];
  }
  for (unsigned int i = 0; i < 5; ++i)
  {
    h[i] = _mob_u[i + 1] - _mob_u[i];
    d[i] = (_mob_y[i + 1] - _mob_y[i]) / h[i];
  }
  _mob_m[0] = ((2.0 * h[0] + h[1]) * d[0] - h[0] * d[1]) / (h[0] + h[1]);
  if (_mob_m[0] * d[0] <= 0.0)
    _mob_m[0] = 0.0;
  else if (std::abs(_mob_m[0]) > 3.0 * std::abs(d[0]))
    _mob_m[0] = 3.0 * d[0];
  for (unsigned int i = 1; i < 5; ++i)
  {
    if (d[i - 1] * d[i] > 0.0)
    {
      const Real w1 = 2.0 * h[i] + h[i - 1];
      const Real w2 = h[i] + 2.0 * h[i - 1];
      _mob_m[i] = (w1 + w2) / (w1 / d[i - 1] + w2 / d[i]);
    }
    else
      _mob_m[i] = 0.0;
  }
  _mob_m[5] = 0.0;

  if (_mobilization_shelf_widths.size() != _mobilization_shelf_onsets.size())
    paramError("mobilization_shelf_widths",
               "Must have the same length as mobilization_shelf_onsets.");
  for (std::size_t i = 0; i < _mobilization_shelf_onsets.size(); ++i)
  {
    if (_mobilization_shelf_widths[i] <= 0.0)
      paramError("mobilization_shelf_widths", "Widths must be > 0.");
    if (_mobilization_shelf_onsets[i] < _mobilization_onset_slip)
      paramError("mobilization_shelf_onsets",
                 "Onsets must lie at or beyond mobilization_onset_slip.");
    if (i > 0 && _mobilization_shelf_onsets[i] <=
                     _mobilization_shelf_onsets[i - 1] + _mobilization_shelf_widths[i - 1])
      paramError("mobilization_shelf_onsets",
                 "Onsets must be strictly increasing and shelves must not overlap.");
  }

  if (_stability_reference_normal_stress > 0.0 && _communicator.rank() == 0)
  {
    const Real sref = _stability_reference_normal_stress;
    Real mu_peak, dmu;
    frictionCoefficient(Real(0.0), sref, mu_peak, dmu);
    const Real w_max = maxWeakeningSlope(sref);
    std::ostringstream oss;
    oss << name() << ": JRC_n = " << _jrc_scaled << ", JCS_n = " << _jcs_scaled
        << " Pa, delta_p = " << _peak_shear_displacement
        << (getParam<Real>("peak_shear_displacement") > 0.0 ? " m (user)"
                                                            : " m (Barton 1982 estimate)")
        << "; mu_peak(sigma'_n = " << sref << " Pa) = " << mu_peak
        << ", mu_r = " << std::tan(_residual_friction_angle_deg * bbf_deg_to_rad)
        << "; peak quasi-static weakening slope W_max = " << w_max
        << " Pa/m; local_solver=guarded-central-half-v1";
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
ADOrcaBartonBandisFlowRSFContactTraction::initQpStatefulProperties()
{
  OrcaCZMComputeLocalTractionIncrementalBase::initQpStatefulProperties();

  // Cosmetic initial exports use the stability reference stress when given, else the
  // one-decade point JCS_n/10 (phi = phi_r + JRC_n degrees).
  const Real sref = _stability_reference_normal_stress > 0.0 ? _stability_reference_normal_stress
                                                             : _jcs_scaled / 10.0;
  Real mu0, dmu0;
  frictionCoefficient(Real(0.0), sref, mu0, dmu0);
  Real y0, dy0, dil0, ddil0;
  mobilizationFraction(Real(0.0), y0, dy0);
  dilationCoefficient(y0, dy0, sref, dil0, ddil0);

  _fracture_state[_qp] = static_cast<Real>(FractureState::Stick);
  _limit_tau[_qp] = 0.0;
  _plastic_slip_increment[_qp] = 0.0;
  _dilation_jump_increment[_qp] = 0.0;
  _cumulative_plastic_slip[_qp] = 0.0;
  _roughness_state[_qp] = _roughness_state_initial;
  _roughness_damage[_qp] = 1.0 - _roughness_state_initial;
  _friction_coefficient_effective[_qp] = mu0;
  _cohesion_effective[_qp] = _apparent_cohesion;
  _dilation_angle_effective[_qp] = std::atan(dil0) * 180.0 / bbf_pi;
  _dilation_state[_qp] = dil0;
  _dilation_support_factor[_qp] = 1.0;
  _bb_jrc_mobilized[_qp] = _jrc_scaled;
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
ADOrcaBartonBandisFlowRSFContactTraction::smoothPositive(const ADReal & x, const Real eps) const
{
  return bbfSmoothPos(x, eps);
}

void
ADOrcaBartonBandisFlowRSFContactTraction::storeReversibleOpening(
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
void
ADOrcaBartonBandisFlowRSFContactTraction::mobilizationFraction(const T & cumulative_slip,
                                                               T & fraction,
                                                               T & dfraction_ds) const
{
  using std::log;
  T s = std::max(T(0.0), cumulative_slip - T(_mobilization_onset_slip));
  // Multi-shelf: subtract the slip spent frozen on shelves from the table's effective
  // slip; inside a shelf the table is exactly flat (gate zeroes the returned slope).
  Real shelf_gate = 1.0;
  if (!_mobilization_shelf_onsets.empty())
  {
    const Real s_raw = bbfRaw(cumulative_slip);
    if (s_raw <= _mobilization_onset_slip)
      shelf_gate = 0.0;
    T frozen(0.0);
    for (std::size_t i = 0; i < _mobilization_shelf_onsets.size(); ++i)
    {
      const Real onset = _mobilization_shelf_onsets[i];
      const Real width = _mobilization_shelf_widths[i];
      frozen += std::min(std::max(cumulative_slip - T(onset), T(0.0)), T(width));
      if (s_raw > onset && s_raw < onset + width)
        shelf_gate = 0.0;
    }
    s = std::max(T(0.0), s - frozen);
  }
  const T x = T(1.0) + s / T(_peak_shear_displacement);
  const T u = log(x) / T(bbf_ln10);

  if (bbfRaw(u) >= _mob_u[5])
  {
    fraction = T(0.0);
    dfraction_ds = T(0.0);
    return;
  }

  unsigned int i = 0;
  while (i < 4 && bbfRaw(u) > _mob_u[i + 1])
    ++i;

  const Real h = _mob_u[i + 1] - _mob_u[i];
  const T t = (u - T(_mob_u[i])) / T(h);
  const T t2 = t * t;
  const T t3 = t2 * t;

  const T h00 = T(2.0) * t3 - T(3.0) * t2 + T(1.0);
  const T h10 = t3 - T(2.0) * t2 + t;
  const T h01 = T(-2.0) * t3 + T(3.0) * t2;
  const T h11 = t3 - t2;
  fraction = T(_mob_y[i]) * h00 + T(h * _mob_m[i]) * h10 + T(_mob_y[i + 1]) * h01 +
             T(h * _mob_m[i + 1]) * h11;

  const T dy_du = (T(_mob_y[i]) * (T(6.0) * t2 - T(6.0) * t) +
                   T(h * _mob_m[i]) * (T(3.0) * t2 - T(4.0) * t + T(1.0)) +
                   T(_mob_y[i + 1]) * (T(-6.0) * t2 + T(6.0) * t) +
                   T(h * _mob_m[i + 1]) * (T(3.0) * t2 - T(2.0) * t)) /
                  T(h);
  dfraction_ds = dy_du / (x * T(bbf_ln10) * T(_peak_shear_displacement));
  if (!_mobilization_shelf_onsets.empty())
    dfraction_ds *= T(shelf_gate);
}

template <typename T>
void
ADOrcaBartonBandisFlowRSFContactTraction::frictionCoefficient(const T & cumulative_slip,
                                                              const T & sigma_arg,
                                                              T & friction,
                                                              T & dfriction_ds) const
{
  using std::cos;
  using std::exp;
  using std::log;
  using std::pow;
  using std::tan;

  T y, dy_ds;
  mobilizationFraction(cumulative_slip, y, dy_ds);

  const T sigma_safe = std::max(T(_compressive_normal_stress_floor), sigma_arg);
  const T log_ratio = log(T(_jcs_scaled) / sigma_safe) / T(bbf_ln10);

  const T i_raw = T(_jrc_scaled) * y * log_ratio;
  const T i_pos = bbfSmoothPos(i_raw, bbf_angle_floor_eps_deg);
  const T di_pos = bbfSmoothPosDeriv(i_raw, bbf_angle_floor_eps_deg);

  T late_weight = T(0.0);
  T dlate_weight_ds = T(0.0);
  if (_late_friction_angle_increment_deg > 0.0 &&
      bbfRaw(cumulative_slip) > _late_friction_onset_slip)
  {
    const T x =
        (cumulative_slip - T(_late_friction_onset_slip)) / T(_late_friction_distance);
    const T decay = exp(-pow(x, T(_late_friction_exponent)));
    late_weight = T(1.0) - decay;
    dlate_weight_ds = decay * T(_late_friction_exponent) *
                      pow(x, T(_late_friction_exponent - 1.0)) /
                      T(_late_friction_distance);
  }

  const T phi_raw = T(_residual_friction_angle_deg) + i_pos +
                    T(_late_friction_angle_increment_deg) * late_weight;
  const T phi = smoothCapMin(phi_raw, _max_friction_angle_deg, bbf_angle_cap_width_deg);
  const T dphi = smoothCapMinDerivative(phi_raw, _max_friction_angle_deg, bbf_angle_cap_width_deg);

  const T phi_rad = phi * T(bbf_deg_to_rad);
  friction = tan(phi_rad);
  const T sec = T(1.0) / cos(phi_rad);
  const T dphi_raw_ds = di_pos * T(_jrc_scaled) * log_ratio * dy_ds +
                        T(_late_friction_angle_increment_deg) * dlate_weight_ds;
  dfriction_ds = sec * sec * T(bbf_deg_to_rad) * dphi * dphi_raw_ds;
}

template <typename T>
void
ADOrcaBartonBandisFlowRSFContactTraction::dilationCoefficient(const T & mobilization,
                                                              const T & dmobilization_ds,
                                                              const T & sigma_arg,
                                                              T & coefficient,
                                                              T & dcoefficient_ds) const
{
  using std::cos;
  using std::log;
  using std::tan;

  if (!_use_dilatancy)
  {
    coefficient = T(0.0);
    dcoefficient_ds = T(0.0);
    return;
  }

  const T sigma_safe = std::max(T(_compressive_normal_stress_floor), sigma_arg);
  const T log_ratio = log(T(_jcs_scaled) / sigma_safe) / T(bbf_ln10);

  const T psi_raw = T(_dilation_factor) * T(_jrc_scaled) * mobilization * log_ratio;
  T psi_pos = bbfSmoothPos(psi_raw, bbf_angle_floor_eps_deg);
  T dpsi_pos = bbfSmoothPosDeriv(psi_raw, bbf_angle_floor_eps_deg);

  // Optional smooth floor (skipped at 0: the softplus would inject a spurious
  // ~0.7 deg * width offset right at psi = floor, i.e. everywhere for floor = 0).
  if (_min_dilation_angle_deg > 0.0)
  {
    const T t = (T(_min_dilation_angle_deg) - psi_pos) / T(bbf_angle_cap_width_deg);
    psi_pos = psi_pos + T(bbf_angle_cap_width_deg) * softplusT(t);
    dpsi_pos = dpsi_pos * (T(1.0) - sigmoidT(t));
  }

  const T psi = smoothCapMin(psi_pos, _max_dilation_angle_deg, bbf_angle_cap_width_deg);
  const T dpsi = smoothCapMinDerivative(psi_pos, _max_dilation_angle_deg, bbf_angle_cap_width_deg);

  const T psi_rad = psi * T(bbf_deg_to_rad);
  coefficient = tan(psi_rad);
  const T sec = T(1.0) / cos(psi_rad);
  dcoefficient_ds = sec * sec * T(bbf_deg_to_rad) * dpsi * dpsi_pos * T(_dilation_factor) *
                    T(_jrc_scaled) * log_ratio * dmobilization_ds;
}

template <typename T>
T
ADOrcaBartonBandisFlowRSFContactTraction::evolveRateStateTheta(const T & gamma,
                                                               const Real theta_old) const
{
  using std::exp;
  if (_dt <= 0.0)
    return T(theta_old);
  const T x = std::max(T(0.0), gamma) / T(_rsf_Dc);
  const T ex = exp(-x);
  const T one_minus_ex_over_x =
      (bbfRaw(x) > 1.0e-8) ? (T(1.0) - ex) / x : (T(1.0) - T(0.5) * x);
  return T(theta_old) * ex + T(_dt) * one_minus_ex_over_x;
}

template <typename T>
ADOrcaBartonBandisFlowRSFContactTraction::FlowEval<T>
ADOrcaBartonBandisFlowRSFContactTraction::evaluateFlow(const T & gamma,
                                                       const T & tau_trial,
                                                       const T & current_normal_jump,
                                                       const Real old_normal_plastic_jump,
                                                       const Real old_cumulative_slip,
                                                       const Real old_theta) const
{
  using std::exp;
  using std::log;
  using std::pow;
  using std::sqrt;

  FlowEval<T> f;
  f.cumulative_slip = T(old_cumulative_slip) + gamma;

  // Pre-dilation contact pressure: the sigma'_n argument of the Barton angle terms.
  // gamma-independent inside the local solve (breaks the angle->dilation->pressure
  // cycle; second order, the angles see sigma'_n only through log10), but AD-live
  // through the displacement jump for the global Jacobian.
  const T sigma_arg =
      OrcaNormalClosure::evaluate(T(old_normal_plastic_jump) - current_normal_jump,
                                  _contact_gap_regularization,
                                  _use_hyperbolic_normal_closure,
                                  _penalty_normal,
                                  _initial_normal_stiffness,
                                  _maximum_closure,
                                  _maximum_closure_fraction,
                                  _normal_closure_stress_exponent,
                                  _normal_closure_offset)
          .pressure;

  frictionCoefficient(f.cumulative_slip, sigma_arg, f.friction, f.dfriction_dgamma);

  T y, dy_ds;
  mobilizationFraction(f.cumulative_slip, y, dy_ds);
  f.mobilization = y;

  T dil_coeff, ddil_coeff;
  dilationCoefficient(y, dy_ds, sigma_arg, dil_coeff, ddil_coeff);
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
  if (bbfRaw(L) > bbf_asinh_log_branch)
  {
    asinh_z = L + T(bbf_ln2);
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

  T late_viscosity_weight = T(0.0);
  T dlate_viscosity_weight_ds = T(0.0);
  if (_late_tangential_viscosity > 0.0 &&
      bbfRaw(f.cumulative_slip) > _late_tangential_viscosity_onset_slip)
  {
    const T x = (f.cumulative_slip - T(_late_tangential_viscosity_onset_slip)) /
                T(_late_tangential_viscosity_distance);
    const T decay = exp(-pow(x, T(_late_tangential_viscosity_exponent)));
    late_viscosity_weight = T(1.0) - decay;
    dlate_viscosity_weight_ds = decay * T(_late_tangential_viscosity_exponent) *
                                pow(x, T(_late_tangential_viscosity_exponent - 1.0)) /
                                T(_late_tangential_viscosity_distance);

    if (_late_tangential_viscosity_release_slip > 0.0 &&
        bbfRaw(f.cumulative_slip) > _late_tangential_viscosity_release_slip)
    {
      const T release_x =
          (f.cumulative_slip - T(_late_tangential_viscosity_release_slip)) /
          T(_late_tangential_viscosity_release_distance);
      const T release_weight =
          exp(-pow(release_x, T(_late_tangential_viscosity_release_exponent)));
      const T drelease_weight_ds =
          -release_weight * T(_late_tangential_viscosity_release_exponent) *
          pow(release_x, T(_late_tangential_viscosity_release_exponent - 1.0)) /
          T(_late_tangential_viscosity_release_distance);
      dlate_viscosity_weight_ds =
          dlate_viscosity_weight_ds * release_weight +
          late_viscosity_weight * drelease_weight_ds;
      late_viscosity_weight *= release_weight;
    }
  }
  const T effective_viscosity =
      T(_tangential_viscosity) + T(_late_tangential_viscosity) * late_viscosity_weight;
  const bool viscous =
      (_tangential_viscosity > 0.0 || _late_tangential_viscosity > 0.0) && _dt > 0.0;
  const T viscous_strength = viscous ? effective_viscosity / T(_dt) * gamma : T(0.0);
  // cumulative_slip = old_cumulative_slip + gamma, so the consistent local tangent includes
  // gamma*d(eta_eff)/ds in addition to eta_eff.
  const T dviscous_dgamma = viscous ? (effective_viscosity + gamma * T(_late_tangential_viscosity) *
                                                                 dlate_viscosity_weight_ds) /
                                          T(_dt)
                                    : T(0.0);

  f.residual = tau_trial - T(_penalty_tangent) * gamma - f.strength - viscous_strength;
  f.dres_dgamma = -(T(_penalty_tangent) + dstrength_dgamma + dviscous_dgamma);
  f.rate_state_theta = evolveRateStateTheta(gamma, old_theta);
  return f;
}

Real
ADOrcaBartonBandisFlowRSFContactTraction::solveFlowRaw(const Real tau_trial,
                                                       const Real current_normal_jump,
                                                       const Real old_normal_plastic_jump,
                                                       const Real old_cumulative_slip,
                                                       const Real old_theta) const
{
  Real lo = 1.0e-30;
  Real hi = tau_trial / _penalty_tangent;
  if (hi <= lo)
    return 0.0;

  // A purely absolute 1e-8 Pa test is not representable when a global Newton trial
  // temporarily drives the traction terms to O(1e12) Pa. For example, subtracting
  // such terms can leave a 4.88e-4 Pa residual (relative error O(1e-16)) even at the
  // converged root. Accept only the larger of the user tolerance and that unavoidable
  // cancellation floor. The corresponding slip uncertainty is roundoff-scale because
  // dR/dgamma contains K_t.
  const auto effective_residual_tolerance =
      [&](const FlowEval<Real> & f, const Real candidate_gamma)
  {
    const Real viscous_strength =
        ((_tangential_viscosity > 0.0 || _late_tangential_viscosity > 0.0) && _dt > 0.0)
            ? std::abs((_tangential_viscosity + _late_tangential_viscosity) / _dt * candidate_gamma)
            : 0.0;
    const Real residual_scale =
        std::max(1.0,
                 std::abs(tau_trial) + std::abs(_penalty_tangent * candidate_gamma) +
                     std::abs(f.strength) + viscous_strength);
    return std::max(_local_newton_tolerance,
                    bbf_residual_roundoff_factor * std::numeric_limits<Real>::epsilon() *
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
  Real mu0, dmu0;
  frictionCoefficient(Real(old_cumulative_slip), p_trial, mu0, dmu0);
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

    // Do not accept an in-bracket Newton point arbitrarily close to an endpoint. In the
    // strongly weakening, low-viscosity SW3 regime such points can remain technically
    // admissible while reducing the bracket by only roundoff for hundreds of iterations.
    // Requiring the Newton point to lie in the central half retains its fast local
    // convergence but guarantees at least 25% bracket contraction per iteration. An
    // arithmetic midpoint is the correct bisection fallback for this signed residual;
    // the former geometric midpoint excessively favored the near-zero endpoint.
    const Real width = hi - lo;
    const Real newton = gamma - f.residual / f.dres_dgamma;
    const Real guarded_lo = lo + 0.25 * width;
    const Real guarded_hi = hi - 0.25 * width;
    if (std::isfinite(newton) && newton > guarded_lo && newton < guarded_hi)
      gamma = newton;
    else
      gamma = 0.5 * (lo + hi);

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
ADOrcaBartonBandisFlowRSFContactTraction::maxWeakeningSlope(const Real sigma_n_ref) const
{
  // Barton's table reaches residual at x = 100, i.e. s = 99 delta_p; scan slightly past.
  Real s_end = _mobilization_onset_slip + 100.0 * _peak_shear_displacement;
  for (const Real w : _mobilization_shelf_widths)
    s_end += w;
  const unsigned int n = 4000;
  Real w_max = 0.0;
  for (unsigned int i = 0; i <= n; ++i)
  {
    const Real s = s_end * static_cast<Real>(i) / static_cast<Real>(n);
    Real mu, dmu;
    frictionCoefficient(s, sigma_n_ref, mu, dmu);
    w_max = std::max(w_max, -dmu * sigma_n_ref);
  }
  return w_max;
}

void
ADOrcaBartonBandisFlowRSFContactTraction::computeInterfaceTractionIncrement()
{
  const ADRealVectorValue & jump = _interface_displacement_jump[_qp];
  const RealVectorValue traction_old(_interface_traction_old[_qp]);
  const Real old_cumulative_slip = _cumulative_plastic_slip_old[_qp];
  const Real old_normal_plastic_jump = _normal_plastic_jump_old[_qp];
  const Real old_theta = _rate_state_theta_old[_qp];

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

  ADReal old_mu, old_dmu;
  frictionCoefficient(ADReal(old_cumulative_slip), pressure_trial, old_mu, old_dmu);
  ADReal old_y, old_dy;
  mobilizationFraction(ADReal(old_cumulative_slip), old_y, old_dy);

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
  _bb_jrc_mobilized[_qp] = ADReal(_jrc_scaled) * old_y;
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

  const ADReal R_old = ADReal(_roughness_state_residual) +
                       ADReal(_roughness_state_initial - _roughness_state_residual) * old_y;
  _roughness_state[_qp] = R_old;
  _roughness_damage[_qp] = ADReal(1.0) - R_old;
  ADReal old_dil_coeff, old_ddil_coeff;
  dilationCoefficient(old_y, old_dy, pressure_trial, old_dil_coeff, old_ddil_coeff);
  _dilation_state[_qp] = old_dil_coeff;
  _dilation_angle_effective[_qp] = atan(old_dil_coeff) * ADReal(180.0 / bbf_pi);

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
      gamma_raw <= _dt * _stick_velocity_floor / bbf_stick_blend_ratio)
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
      MetaPhysicL::raw_value(gamma) < _dt * _stick_velocity_floor * bbf_stick_blend_ratio)
  {
    const Real gamma_lo = _dt * _stick_velocity_floor / bbf_stick_blend_ratio;
    const ADReal x =
        log(gamma / ADReal(gamma_lo)) / ADReal(2.0 * std::log(bbf_stick_blend_ratio));
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
      atan(final_state.dilation_coefficient) * ADReal(180.0 / bbf_pi);
  _dilation_support_factor[_qp] = 1.0;
  _bb_jrc_mobilized[_qp] = ADReal(_jrc_scaled) * final_state.mobilization;
  const ADReal R_new =
      ADReal(_roughness_state_residual) +
      ADReal(_roughness_state_initial - _roughness_state_residual) * final_state.mobilization;
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
