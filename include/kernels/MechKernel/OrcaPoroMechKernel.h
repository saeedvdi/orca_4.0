#pragma once

#include "ADKernel.h"
#include "ADRankTwoTensorForward.h"

/**
 * OrcaPoroMechKernel is the kernel for the poro-mechanical problem.
**/
class OrcaPoroMechKernel : public ADKernel
{
public:
  static InputParameters validParams();

  OrcaPoroMechKernel(const InputParameters & parameters);

protected:
  void initialSetup() override;

  ADReal computeQpResidual() override;
  void precalculateResidual() override;

  /// Base name of the material system that this kernel applies to
  const std::string _base_name;

  /// The stress tensor that the divergence operator operates on
  const ADMaterialProperty<RankTwoTensor> & _stress;

  /// An integer corresponding to the direction this kernel acts in
  const unsigned int _component;

  /// Number of coupled displacement variables
  const unsigned int _ndisp;

  /// Coupled displacement variable IDs
  std::vector<unsigned int> _disp_var;

  /// Gradient of test function averaged over the element. Used in volumetric locking correction calculation.
  std::vector<ADReal> _avg_grad_test;

  /// Whether out-of-plane strain is coupeld
  const bool _out_of_plane_strain_coupled;

  /// Pointer to the out-of-plane strain variable
  const ADVariableValue * const _out_of_plane_strain;

  /// Flag for volumetric locking correction
  const bool _volumetric_locking_correction;

  // Optional pore pressure coupling
  const bool _has_pf;
  const ADVariableValue * _pf; // coupled pore pressure (AD)
  const ADMaterialProperty<Real> * _biot; // only valid if _has_pf


  /// Whether an RZ coordinate system is being used
  const bool _rz;
};