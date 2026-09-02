# Mandel 2D consolidation — HM benchmark
#
# Plane-strain sample: half-width a=1 m (x), half-height b=0.25 m (y).
# Symmetry at x=0 (disp_x=0) and y=0 (disp_y=0).
# Drained right face (x=a): p=0.
# Smooth rigid plate load at top (y=b): total Neumann load with top
# disp_y constrained to remain uniform.
# Out-of-plane (z): plane strain enforced by disp_z=0 on front+back.
# No-flow at top and bottom faces (impermeable plate — natural Neumann BC).
#
# The Mandel-Cryer effect: pore pressure at the centre (x=0) first
# rises above the initial undrained value before dissipating.
#
# Reference: Mandel (1953); Abousleiman et al. (1996).
# Setup follows the MOOSE PorousFlow Mandel validation: quarter-domain
# symmetry, drained side at x=a, impermeable smooth loading plate, constant
# Biot modulus, and a constant compressive total force. MOOSE enforces the
# constant force through a prescribed plate displacement history; this ORCA
# input applies the equivalent constant Neumann traction directly and uses an
# equal-value constraint to keep the plate displacement uniform.
# Compare with: mandel_analytical.ipynb
#
# Material (must match the notebook):
#   E = 1e5 Pa, nu = 0.2,  nu_u = 0.5 (incompressible)
#   K = 55556 Pa, G = 41667 Pa
#   phi = 0.3, alpha_biot = 1, k = 1e-10 m^2, mu = 1e-3 Pa.s
#   B = 1, cv_mandel = 2*(k/mu)*B^2*G*(1-nu)*(1+nu_u)^2
#                       / (9*(1-nu_u)*(nu_u-nu)) = 1.111e-2 m^2/s
#   tc = a^2/cv = 90 s
#   Initial undrained pore pressure: p_u = q/2 = 500 Pa
##########################################################

[GlobalParams]
  displacements = 'disp_x disp_y disp_z'
[]

##########################################################
[Mesh]
  type = GeneratedMesh
  dim  = 3
  nx   = 20   # x: drainage direction
  ny   = 5    # y: loading direction
  nz   = 1    # z: out-of-plane (plane strain)
  xmin = 0
  xmax = 1.0   # half-width a
  ymin = 0
  ymax = 0.25  # half-height b
  zmin = 0
  zmax = 0.05
[]

##########################################################
[Variables]
  [pore_pressure]
    order  = FIRST
    family = LAGRANGE
  []
  [disp_x]
    order  = FIRST
    family = LAGRANGE
  []
  [disp_y]
    order  = FIRST
    family = LAGRANGE
  []
  [disp_z]
    order  = FIRST
    family = LAGRANGE
  []
[]

##########################################################
# Zero IC: the first small timestep establishes the undrained state.
# The undrained pore pressure converges to p_u = q/2 = 500 Pa.
[ICs]
  [init_pp]
    type     = ConstantIC
    variable = pore_pressure
    value    = 0
  []
[]

##########################################################
[Kernels]
  # ---- Mechanics ---------------------------------------------------
  [mech_x]
    type          = OrcaPoroMechKernel
    variable      = disp_x
    pore_pressure = pore_pressure
    component     = 0
    displacements = 'disp_x disp_y disp_z'
  []
  [mech_y]
    type          = OrcaPoroMechKernel
    variable      = disp_y
    pore_pressure = pore_pressure
    component     = 1
    displacements = 'disp_x disp_y disp_z'
  []
  [mech_z]
    type          = OrcaPoroMechKernel
    variable      = disp_z
    pore_pressure = pore_pressure
    component     = 2
    displacements = 'disp_x disp_y disp_z'
  []

  # ---- Fluid mass balance ------------------------------------------
  # (1/M)*dp/dt + alpha*d(eps_v)/dt + div(q) = 0   [volume form]
  [fluid_storage]
    type                      = OrcaSinglePhaseMassTimeDerivativeKernel
    variable                  = pore_pressure
    multiply_by_fluid_density = false
  []
  [vol_expansion]
    type                      = OrcaSinglePhaseMassVolumetricExpansionKernel
    variable                  = pore_pressure
    multiply_by_fluid_density = false
  []

  [darcy]
    type                      = OrcaFullySaturatedSinglePhaseDarcySUPGKernel
    variable                  = pore_pressure
    multiply_by_fluid_density = false
    use_supg                  = false
  []
[]

##########################################################
[BCs]
  # Symmetry at x=0 (left face)
  [symm_x]
    type     = DirichletBC
    variable = disp_x
    boundary = 'left'
    value    = 0
  []

  # Symmetry at y=0 (bottom face)
  [symm_y]
    type     = DirichletBC
    variable = disp_y
    boundary = 'bottom'
    value    = 0
  []

  # Plane strain: out-of-plane deformation zero on both z-faces
  [plane_strain_back]
    type     = DirichletBC
    variable = disp_z
    boundary = 'back'
    value    = 0
  []
  [plane_strain_front]
    type     = DirichletBC
    variable = disp_z
    boundary = 'front'
    value    = 0
  []

  # Drainage at x=a (right face)
  [drainage]
    type     = DirichletBC
    variable = pore_pressure
    boundary = 'right'
    value    = 0
  []

  # Compressive load at y=b (top face).  No shear traction is applied.
  # The constraint below keeps disp_y uniform, representing the rigid plate.
  [top_load]
    type     = NeumannBC
    variable = disp_y
    boundary = 'top'
    value    = -1000  # Pa, compressive
  []
[]

##########################################################
[Constraints]
  # Rigid frictionless plate: all top nodes share the same vertical displacement
  # while the NeumannBC above supplies the constant total compressive load.
  [rigid_top_y]
    type               = EqualValueBoundaryConstraint
    variable           = disp_y
    secondary          = top
    primary_node_coord = '0 0.25 0'
    penalty            = 1e9
  []
[]

##########################################################
[Materials]
  [mech]
    type           = OrcaMechMaterial
    displacements  = 'disp_x disp_y disp_z'
    youngs_modulus = 1e5
    poissons_ratio = 0.2
    strain_model   = incremental
  []

  [rockHM]
    type = OrcaTHMaterial
    pore_pressure = pore_pressure

    initial_porosity     = 0.3
    initial_permeability = '1e-10 0 0   0 1e-10 0   0 0 1e-10'

    fluid_properties_model = user
    fluid_density_model    = constant
    fluid_density_ref      = 1000
    # Large Kf approximates the incompressible fluid assumption used by the
    # analytical Mandel solution (B=1, nu_u=0.5).
    fluid_bulk_modulus     = 1e12
    fluid_viscosity_ref    = 1e-3

    biot_modulus_model = constant

    fluid_thermal_expansion_model = user
  []

  [biot]
    type             = OrcaBiotCoefficientMaterial
    model            = user
    biot_coefficient = 1.0
  []

  [gravity]
    type    = OrcaGravityVectorMaterial
    gravity = '0 0 0'
  []
[]

##########################################################
[Postprocessors]
  # Pore pressure at several x-locations along the mid-plane (y=b/2, z=Lz/2)
  # to capture the Mandel-Cryer pressure build-up at the centre.
  [p_x0]
    type             = PointValue
    variable         = pore_pressure
    point            = '0.0   0.125 0.025'
    use_displaced_mesh = false
  []
  [p_x025]
    type             = PointValue
    variable         = pore_pressure
    point            = '0.25  0.125 0.025'
    use_displaced_mesh = false
  []
  [p_x050]
    type             = PointValue
    variable         = pore_pressure
    point            = '0.5   0.125 0.025'
    use_displaced_mesh = false
  []
  [p_x075]
    type             = PointValue
    variable         = pore_pressure
    point            = '0.75  0.125 0.025'
    use_displaced_mesh = false
  []

  # Settlement at top (average vertical displacement at y=b)
  [uy_top_corner]
    type             = PointValue
    variable         = disp_y
    point            = '0.5   0.25  0.025'
    use_displaced_mesh = false
  []
[]

##########################################################
[Preconditioning]
  [smp]
    type                = SMP
    full                = true
    petsc_options_iname = '-pc_type -pc_factor_mat_solver_package'
    petsc_options_value = ' lu       mumps'
  []
[]

##########################################################
[Executioner]
  type       = Transient
  solve_type = Newton
  start_time = 0
  end_time   = 180   # 2 * tc  (tc = 90 s)

  [TimeStepper]
    # Very fine steps initially to resolve the Mandel-Cryer transient,
    # coarsen as consolidation slows.
    type     = FunctionDT
    function = 'if(t<2, 0.1, if(t<18, 1, if(t<90, 5, 10)))'
  []

  l_max_its  = 50
  l_tol      = 1e-6
  nl_max_its = 30
  nl_abs_tol = 2e-9
  nl_rel_tol = 1e-10
[]

##########################################################
[Outputs]
  file_base = mandel
  exodus    = false
  [csv]
    type = CSV
  []
[]
