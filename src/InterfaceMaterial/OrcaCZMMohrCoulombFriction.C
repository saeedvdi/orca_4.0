#include "OrcaCZMMohrCoulombFriction.h"
#include "metaphysicl/raw_type.h"

registerMooseObject("OrcaApp", OrcaCZMMohrCoulombFriction);

InputParameters
OrcaCZMMohrCoulombFriction::validParams()
{
  InputParameters params = OrcaCZMComputeLocalTractionIncrementalBase::validParams();
  params.addClassDescription(
      "Elastic-predictor / Coulomb-corrector traction-separation law for a rock fracture CZM "
      "sideset: penalty contact in the normal direction, Mohr-Coulomb friction with effective "
      "stress (using the fracture pore pressure) in shear, and shear-induced normal dilation "
      "with optional exponential degradation of the dilation angle with accumulated slip.");

  params.addParam<std::string>("base_name", "Material property base name");

  params.addRequiredRangeCheckedParam<Real>(
      "normal_stiffness", "normal_stiffness > 0", "Elastic contact stiffness in the normal direction (Pa/m).");
  params.addRequiredRangeCheckedParam<Real>(
      "tangent_stiffness", "tangent_stiffness > 0", "Elastic stiffness in the shear plane (Pa/m).");
  params.addRequiredRangeCheckedParam<Real>(
      "friction_coefficient", "friction_coefficient >= 0", "Coulomb sliding friction coefficient (-).");
  params.addRangeCheckedParam<Real>("cohesion", 0.0, "cohesion >= 0", "Fracture cohesion (Pa).");

  params.addRequiredRangeCheckedParam<Real>(
      "dilation_angle", "dilation_angle >= 0 & dilation_angle < 90",
      "Peak dilation angle (degrees).");
  params.addRangeCheckedParam<Real>(
      "dilation_angle_residual", "dilation_angle_residual >= 0 & dilation_angle_residual < 90",
      "Residual (fully asperity-degraded) dilation angle (degrees). Defaults to dilation_angle "
      "(i.e. no degradation) if not set.");
  params.addRangeCheckedParam<Real>(
      "critical_slip_distance", 1.0e3, "critical_slip_distance > 0",
      "Slip distance controlling the exponential decay of the dilation angle from its peak to "
      "its residual value (m). Large default effectively disables degradation.");
  params.addRangeCheckedParam<Real>(
      "tensile_stiffness_ratio", 1.0e-4, "tensile_stiffness_ratio > 0 & tensile_stiffness_ratio <= 1",
      "Ratio of the normal stiffness used once the fracture separates (elastic normal gap > 0) "
      "to the contact normal stiffness. Kept small but nonzero for numerical conditioning.");

  params.addParam<std::string>(
      "pore_pressure_property_name", "interface_pore_pressure",
      "Name of the fracture pore pressure material property (e.g. from OrcaCZMInterfacePressure).");
  params.addParam<Real>(
      "pore_pressure_strength_coefficient",
      1.0,
      "Coefficient multiplying pore pressure in the effective-normal-stress value used by the "
      "Coulomb strength. Keep 1.0 for the original total-traction interpretation. Set 0.0 when "
      "initial_effective_normal_traction is used and a separate pressure InterfaceKernel applies "
      "the fluid pressure load.");
  params.addParam<Real>(
      "initial_effective_normal_traction",
      0.0,
      "Initial effective/contact normal traction in local coordinates (Pa, tension positive; "
      "compression is negative). This represents the pre-injection triaxial stress state.");
  params.addParam<RealVectorValue>(
      "initial_shear_traction",
      RealVectorValue(0.0, 0.0, 0.0),
      "Initial effective/contact shear traction vector in local coordinates (Pa). Component 0 is "
      "ignored; components 1 and 2 are the shear-plane components.");
  params.addParam<Real>(
      "normal_gap_reference",
      0.0,
      "Reference local normal displacement jump for the normal penalty law (m).");
  params.addRangeCheckedParam<Real>(
      "slip_start_time",
      0.0,
      "slip_start_time >= 0",
      "Suppress inelastic slip/dilation before this time. This is useful for reproducing "
      "laboratory protocols where mechanical preload is established before the injection-induced "
      "slip stage is measured.");
  params.addRangeCheckedParam<Real>(
      "viscosity",
      0.0,
      "viscosity >= 0",
      "Duvaut-Lions viscous (rate) regularization of the frictional slip (Pa.s/m). Adds "
      "viscosity/dt to the radial-return denominator so the retained shear overstress equals "
      "viscosity * slip_rate. 0 disables (rate-independent). A small positive value (negligible "
      "under slow loading) regularizes a pressure-driven slip burst into a smooth rate-limited "
      "slide so the quasi-static solve can traverse the instability; essential on fine meshes "
      "where the slip front sharpens into a true snap.");
  params.addRangeCheckedParam<Real>(
      "max_plastic_slip_increment",
      0.0,
      "max_plastic_slip_increment >= 0",
      "Maximum plastic slip increment per constitutive update (m). Set to 0 to disable the cap "
      "(full radial return). A small positive value spreads a pressure-driven slip burst over "
      "several steps instead of a single snap, stabilizing the quasi-static solve through the "
      "frictional instability. The shear traction is then left above the Coulomb envelope and the "
      "excess is relieved over subsequent steps.");

  return params;
}

OrcaCZMMohrCoulombFriction::OrcaCZMMohrCoulombFriction(const InputParameters & parameters)
  : OrcaCZMComputeLocalTractionIncrementalBase(parameters),
    _K_n(getParam<Real>("normal_stiffness")),
    _K_s(getParam<Real>("tangent_stiffness")),
    _mu(getParam<Real>("friction_coefficient")),
    _cohesion(getParam<Real>("cohesion")),
    _psi0(getParam<Real>("dilation_angle") * libMesh::pi / 180.0),
    _psi_r((parameters.isParamSetByUser("dilation_angle_residual")
                ? getParam<Real>("dilation_angle_residual")
                : getParam<Real>("dilation_angle")) *
           libMesh::pi / 180.0),
    _delta_c(getParam<Real>("critical_slip_distance")),
    _tensile_ratio(getParam<Real>("tensile_stiffness_ratio")),
    _pore_pressure(getADMaterialPropertyByName<Real>(
        _base_name + getParam<std::string>("pore_pressure_property_name"))),
    _pore_pressure_strength_coefficient(getParam<Real>("pore_pressure_strength_coefficient")),
    _initial_effective_normal_traction(getParam<Real>("initial_effective_normal_traction")),
    _initial_shear_traction(getParam<RealVectorValue>("initial_shear_traction")),
    _normal_gap_reference(getParam<Real>("normal_gap_reference")),
    _slip_start_time(getParam<Real>("slip_start_time")),
    _viscosity(getParam<Real>("viscosity")),
    _max_plastic_slip_increment(getParam<Real>("max_plastic_slip_increment")),
    _interface_effective_traction(
        declareADPropertyByName<RealVectorValue>(_base_name + "interface_effective_traction")),
    _interface_effective_traction_old(
        getMaterialPropertyOldByName<RealVectorValue>(_base_name + "interface_effective_traction")),
    _interface_effective_normal_traction(
        declareADPropertyByName<Real>(_base_name + "interface_effective_normal_traction")),
    _accum_slip(declareADPropertyByName<Real>(_base_name + "interface_accumulated_slip")),
    _accum_slip_old(getMaterialPropertyOldByName<Real>(_base_name + "interface_accumulated_slip")),
    _dilation(declareADPropertyByName<Real>(_base_name + "interface_dilation")),
    _dilation_old(getMaterialPropertyOldByName<Real>(_base_name + "interface_dilation")),
    _cumulative_plastic_slip(declareProperty<Real>(_base_name + "cumulative_plastic_slip"))
{
}

void
OrcaCZMMohrCoulombFriction::initQpStatefulProperties()
{
  OrcaCZMComputeLocalTractionIncrementalBase::initQpStatefulProperties();
  const RealVectorValue effective_traction_initial(_initial_effective_normal_traction,
                                                   _initial_shear_traction(1),
                                                   _initial_shear_traction(2));
  _interface_traction[_qp] = effective_traction_initial;
  _interface_effective_traction[_qp] = effective_traction_initial;
  _interface_effective_normal_traction[_qp] = _initial_effective_normal_traction;
  _accum_slip[_qp] = 0.0;
  _dilation[_qp] = 0.0;
  _cumulative_plastic_slip[_qp] = 0.0;
}

void
OrcaCZMMohrCoulombFriction::computeInterfaceTractionIncrement()
{
  // Local axes (set up by OrcaCZMComputeDisplacementJump): component 0 = normal
  // (tension positive), components 1,2 = shear plane. See doc for sign conventions.
  const ADReal jump_n = _interface_displacement_jump[_qp](0);

  const Real s_acc_old = _accum_slip_old[_qp];
  const Real d_dil_old = _dilation_old[_qp];

  // Dilation angle, degraded with accumulated slip from the *previous* time step
  // (semi-implicit lag avoids a fully-coupled nonlinear root-find within the radial return).
  const Real psi = _psi_r + (_psi0 - _psi_r) * std::exp(-s_acc_old / _delta_c);

  // --- Normal direction: penalty contact using the OLD dilation state ---
  const ADReal jump_n_elastic_trial = jump_n - _normal_gap_reference - d_dil_old;
  const bool trial_in_contact = MetaPhysicL::raw_value(jump_n_elastic_trial) <= 0.0;
  const ADReal sigma_n_trial = _initial_effective_normal_traction +
                               (trial_in_contact ? _K_n * jump_n_elastic_trial
                                                 : _tensile_ratio * _K_n * jump_n_elastic_trial);

  // Effective normal stress for the friction criterion (tension positive). The pressure
  // coefficient preserves the original behavior but lets hydroshearing inputs use an
  // explicitly initialized effective/contact traction plus a separate pressure-load kernel.
  const ADReal sigma_n_eff_trial =
      sigma_n_trial + _pore_pressure_strength_coefficient * _pore_pressure[_qp];
  const ADReal N_eff_trial =
      MetaPhysicL::raw_value(sigma_n_eff_trial) < 0.0 ? -sigma_n_eff_trial : ADReal(0.0);

  // --- Shear direction: elastic predictor ---
  const ADRealVectorValue tau_trial(0.0,
                                    _interface_effective_traction_old[_qp](1) +
                                        _K_s * _interface_displacement_jump_inc[_qp](1),
                                    _interface_effective_traction_old[_qp](2) +
                                        _K_s * _interface_displacement_jump_inc[_qp](2));
  const ADReal tau_trial_norm = tau_trial.norm();

  const ADReal tau_strength = _cohesion + _mu * N_eff_trial;
  const ADReal F_trial = tau_trial_norm - tau_strength;

  ADReal sigma_n_new;
  ADRealVectorValue tau_new;
  ADReal d_dil_new;
  ADReal s_acc_new;

  if (_t < _slip_start_time || MetaPhysicL::raw_value(F_trial) <= 0.0 ||
      MetaPhysicL::raw_value(tau_trial_norm) < 1.0e-10)
  {
    // Stick: no new inelastic slip, no new dilation.
    tau_new = tau_trial;
    d_dil_new = d_dil_old;
    s_acc_new = s_acc_old;
    sigma_n_new = sigma_n_trial;
  }
  else
  {
    // Slip: radial return of the shear traction onto the Mohr-Coulomb envelope, with optional
    // Duvaut-Lions viscous (rate) regularization and a cap on the plastic slip increment.
    //
    // Viscous regularization adds viscosity/dt to the return denominator:
    //   delta_s = (tau_trial - tau_strength) / (K_s + viscosity/dt)
    // i.e. the retained overstress (tau_new - tau_strength) = viscosity * (delta_s/dt) = viscosity *
    // slip_rate. Under slow loading the slip rate is tiny so the overstress is negligible (the
    // quasi-static answer is unchanged); during a pressure-driven slip burst the rate term limits
    // the slip rate, turning the snap into a smooth rate-limited slide that the quasi-static Newton
    // solve can actually traverse. This is the standard regularization for frictional instabilities
    // and is what lets the burst converge on a fine mesh (where it sharpens into a true snap).
    ADReal denom = _K_s;
    if (_viscosity > 0.0 && _dt > 0.0)
      denom += _viscosity / _dt;
    ADReal delta_s = (tau_trial_norm - tau_strength) / denom;
    if (_max_plastic_slip_increment > 0.0)
      delta_s = std::min(delta_s, ADReal(_max_plastic_slip_increment));

    // Reduce the shear traction by K_s * delta_s along the trial direction. When delta_s is the
    // full return value this is exactly the radial projection onto the envelope (tau_strength);
    // when capped, the traction is left above the envelope and the excess slip is relieved over
    // subsequent steps, turning a one-step burst into a controlled multi-step slide.
    tau_new = tau_trial * (1.0 - _K_s * delta_s / tau_trial_norm);

    s_acc_new = s_acc_old + delta_s;
    d_dil_new = d_dil_old + std::tan(psi) * delta_s;

    // Re-evaluate the normal traction with the corrected (dilated) elastic gap.
    const ADReal jump_n_elastic_new = jump_n - _normal_gap_reference - d_dil_new;
    const bool new_in_contact = MetaPhysicL::raw_value(jump_n_elastic_new) <= 0.0;
    sigma_n_new = _initial_effective_normal_traction +
                  (new_in_contact ? _K_n * jump_n_elastic_new
                                  : _tensile_ratio * _K_n * jump_n_elastic_new);
  }

  _accum_slip[_qp] = s_acc_new;
  _cumulative_plastic_slip[_qp] = MetaPhysicL::raw_value(s_acc_new);
  _dilation[_qp] = d_dil_new;

  const ADRealVectorValue traction_new(sigma_n_new, tau_new(1), tau_new(2));
  _interface_effective_traction[_qp] = traction_new;
  _interface_effective_normal_traction[_qp] = sigma_n_new;
  _interface_traction_inc[_qp] = traction_new - _interface_traction_old[_qp];
}
