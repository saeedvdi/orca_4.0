#pragma once

#include "AuxKernel.h"

/**
 * Outputs one Cartesian component of the in-plane fracture Darcy velocity
 * corresponding to OrcaFractureFlowInterfaceKernel:
 *
 *   v_f = -(T / a_h) (I - n (x) n) grad(p).
 *
 * T is the cubic-law fracture transmissivity [m^3/(Pa.s)] and a_h is the
 * hydraulic aperture [m], so v_f has units m/s.  The AuxKernel is intended to
 * be boundary-restricted and to write to a coincident lower-dimensional block
 * created by LowerDBlockFromSidesetGenerator.
 */
class OrcaFractureDarcyVelocityComponent : public AuxKernel
{
public:
  static InputParameters validParams();

  OrcaFractureDarcyVelocityComponent(const InputParameters & parameters);

protected:
  Real computeValue() override;

private:
  const unsigned int _component;
  const ADVariableGradient & _grad_p;
  const ADMaterialProperty<Real> & _transmissivity;
  const ADMaterialProperty<Real> & _aperture;
  const MooseArray<Point> & _normals;
};
