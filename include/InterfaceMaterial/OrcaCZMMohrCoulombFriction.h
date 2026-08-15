#pragma once

#include "OrcaCZMComputeLocalTractionIncrementalBase.h"

/**
 * Elastic-predictor / Coulomb-corrector traction-separation law for a CZM
 * sideset representing a frictional rock fracture.
 *
 * Normal direction: penalty contact law (compressive once the "elastic" part
 * of the normal gap closes), softened by a residual tensile stiffness once
 * separated.
 *
 * Shear direction: linear elastic up to a Mohr-Coulomb slip criterion based
 * on the *effective* normal traction (total normal traction plus the
 * fracture pore pressure, in a tension-positive sign convention). Slip beyond
 * the criterion is corrected by radial return and produces shear-induced
 * normal dilation, with an optional exponential decay of the dilation angle
 * with accumulated slip to mimic asperity degradation.
 *
 * See the accompanying documentation for the full equations and sign
 * conventions used here.
 */
class OrcaCZMMohrCoulombFriction : public OrcaCZMComputeLocalTractionIncrementalBase
{
public:
  static InputParameters validParams();
  OrcaCZMMohrCoulombFriction(const InputParameters & parameters);

protected:
  void initQpStatefulProperties() override;
  void computeInterfaceTractionIncrement() override;

  /// Elastic penalty stiffness in the normal direction (Pa/m)
  const Real _K_n;

  /// Elastic penalty stiffness in the shear (tangential) plane (Pa/m)
  const Real _K_s;

  /// Coulomb friction coefficient (-)
  const Real _mu;

  /// Cohesion (Pa)
  const Real _cohesion;

  /// Peak dilation angle (radians)
  const Real _psi0;

  /// Residual (fully degraded) dilation angle (radians)
  const Real _psi_r;

  /// Critical slip distance controlling the exponential decay of the dilation angle (m)
  const Real _delta_c;

  /// Ratio of tensile to compressive normal stiffness, K_n_tension = ratio * K_n (-)
  const Real _tensile_ratio;

  /// Fracture pore pressure at the interface (from OrcaCZMInterfacePressure)
  const ADMaterialProperty<Real> & _pore_pressure;

  /// Coefficient used when converting pore pressure to effective stress for the slip criterion.
  /// Use 1.0 when the normal traction stored in this material is total traction, and 0.0 when it
  /// is already the effective contact traction and a pressure InterfaceKernel applies the fluid
  /// load separately.
  const Real _pore_pressure_strength_coefficient;

  /// Initial effective/contact normal traction, tension positive (Pa)
  const Real _initial_effective_normal_traction;

  /// Initial shear traction in the local interface coordinate system (Pa)
  const RealVectorValue _initial_shear_traction;

  /// Reference normal gap for the penalty law (m)
  const Real _normal_gap_reference;

  /// Do not accumulate inelastic slip/dilation before this simulation time (s)
  const Real _slip_start_time;

  /// Duvaut-Lions viscous (rate) regularization of slip (Pa.s/m); 0 disables. Adds viscosity/dt to
  /// the return denominator so a pressure-driven slip burst becomes a smooth rate-limited slide the
  /// quasi-static solver can traverse (essential on fine meshes where the front snaps).
  const Real _viscosity;

  /// Maximum plastic slip increment per constitutive update (m); 0 disables the cap. Spreads a
  /// pressure-driven slip burst (sigma'_n collapse) over several steps instead of one snap, which
  /// stabilizes the quasi-static solve through the instability (DD02-style stabilizer).
  const Real _max_plastic_slip_increment;

  /// Effective/contact traction, before any separate fluid-pressure InterfaceKernel contribution
  ADMaterialProperty<RealVectorValue> & _interface_effective_traction;
  const MaterialProperty<RealVectorValue> & _interface_effective_traction_old;

  /// Effective/contact normal traction scalar, tension positive (Pa)
  ADMaterialProperty<Real> & _interface_effective_normal_traction;

  /// Accumulated inelastic shear slip magnitude (state variable)
  ADMaterialProperty<Real> & _accum_slip;
  const MaterialProperty<Real> & _accum_slip_old;

  /// Accumulated shear-induced normal dilation (state variable)
  ADMaterialProperty<Real> & _dilation;
  const MaterialProperty<Real> & _dilation_old;

  /// Non-AD mirror of interface_accumulated_slip, so non-AD readers (e.g. the slip-damage
  /// term in ADOrcaRoughnessDamageFracturePermeability) can couple to the accumulated slip.
  MaterialProperty<Real> & _cumulative_plastic_slip;
};
