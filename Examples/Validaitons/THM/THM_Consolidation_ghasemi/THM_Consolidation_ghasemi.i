# this is the validation for THM consolidation case done by Qian Gao & Ahmad Ghassemi
# Three-Dimensional Thermo-Poroelastic Modeling and Analysis of Flow, 
# Heat Transport and Deformation in Fractured Rock with Applications to a Lab-Scale Geothermal System
# https://link.springer.com/article/10.1007/s00603-019-01989-0
##########################################################
[GlobalParams]
  displacements = 'disp_x disp_y disp_z'
[]
##########################################################
# notes about the mesh
# x: left (negative side X), right (opposite side x)
# y: bottom (negative side X), top (opposite side x)
# z: front (opossite side z), back (negative size Z)

[Mesh]
    type = GeneratedMesh
    dim = 3
    nx = 1
    ny = 1
    nz = 50
    xmin = -1
    xmax = 1
    ymin = -1
    ymax = 1
    zmin = 0
    zmax = 7
  []
##########################################################
[Variables]
  [temperature]
    order = FIRST
    family = LAGRANGE
  []
  [disp_x]
    order = FIRST
    family = LAGRANGE
  []
  [disp_y]
    order = FIRST
    family = LAGRANGE
  []
  [disp_z]
    order = FIRST
    family = LAGRANGE
  []
  [pore_pressure]
    order = FIRST
    family = LAGRANGE
  []
[]

[ICs]
  [init_pp]
    type = ConstantIC
    value = 1
    variable = pore_pressure
  []
  [init_temp]
    type = ConstantIC
    value = 273.15
    variable = temperature
  []
[]
##########################################################
[Kernels]
  [poro_mech_x]
    type = OrcaPoroMechKernel
    variable = disp_x
    pore_pressure = pore_pressure
    component = 0
    displacements = 'disp_x disp_y disp_z'
  []
  [poro_mech_y]
    type = OrcaPoroMechKernel
    variable = disp_y
    pore_pressure = pore_pressure
    component = 1
    displacements = 'disp_x disp_y disp_z'
  []
  [poro_mech_z]
    type = OrcaPoroMechKernel
    variable = disp_z
    pore_pressure = pore_pressure
    component = 2
    displacements = 'disp_x disp_y disp_z'
  []

  [mass_storage]
    type = OrcaSinglePhaseMassTimeDerivativeKernel
    variable = pore_pressure
    multiply_by_fluid_density = true
  []

  [mass_vol_expansion]
    type = OrcaSinglePhaseMassVolumetricExpansionKernel
    variable = pore_pressure
    multiply_by_fluid_density = true
  []

  [fluid_advection_SUPG]
    type = OrcaFullySaturatedSinglePhaseDarcySUPGKernel
    use_supg = true
    variable = pore_pressure
    multiply_by_fluid_density = true
  []

  # Thermal Flow
  [heat_conduction]
    type = OrcaHeatConductionKernel
    variable = temperature
  []
  [Heat_convection]
    type = OrcaFullySaturatedSinglePhaseHeatAdvectionSUPGKernel
    variable = temperature
    pore_pressure = pore_pressure
  []

  # Energy Time derivative
  [energy_storage]
    type = OrcaFullySaturatedSinglePhaseEnergyTimeDerivativeKernel
    variable = temperature
    use_total_strain_old = true
  []
  [heat_vol_exp]
    type = OrcaFullySaturatedSinglePhaseHeatVolumetricExpansionKernel
    variable = temperature
  []
[]
##########################################################
[Materials]
  [rockTHMat]
    type = OrcaTHMaterial
    pore_pressure = pore_pressure
    temperature = temperature

    initial_porosity = 0.2  #(-)
    initial_permeability = '4e-9 0 0   0 4e-9 0   0 0 4e-9' # m^2

    fluid_properties_model = user
    fluid_density_model = temperature_pressure_dependent

    fluid_bulk_modulus = 4200 
    fluid_density_ref = 1000
    fluid_viscosity_ref = 1e-03
    pore_pressure_ref = 0.0
    fluid_temperature_ref = 293.15
    fluid_thermal_expansion = 0.0
    fluid_specific_heat_pressure = 1.672e2  # kJ/m3/K
    fluid_specific_heat_volume = 1.672e2    # kJ/m3/K

  #  thermal material properties
    solid_specific_heat_capacity = 69.67    # kJ/m3/K
    solid_density = 2400                    # kg/m^3
    solid_bulk_compliance = 1e-04           # 1/Ks 1/10,000
    
    effective_thermal_expansion_model = computed # alpha_eff = (biot-phi)*beta_solid + phi*beta_fluid
    
    fluid_thermal_expansion_model = user
    volumetric_solid_thermal_expansion = 4e-07         # volumetric thermal expansion coeff (1/K)
    volumetric_fluid_thermal_expansion = 0             # volumetric thermal expansion coeff of fluid

    thermal_conductivity_model = dry_only # can have dry_only and effective_mixture
    dry_thermal_conductivity = '836 0 0  0 836 0  0 0 836' # kj/m/s/k
    biot_modulus_model = constant
  []
      
  [mech]
    type = OrcaMechMaterial
    displacements = 'disp_x disp_y disp_z'
    # youngs_modulus = 6000 # pa
    bulk_modulus = 1e4 # pa
    shear_modulus = 2143 # pa
    # poissons_ratio = 0.4 # (-)

    temperature = temperature
    stress_free_temperature = T_ref
    compute_thermal_eigenstrain = true
    thermal_eigenstrain_name = thermal_eigenstrain
  []
  [grav_qp]
    type = OrcaGravityVectorMaterial
    gravity = '0 0 0'
  []
      
  [biot_qp]
    type = OrcaBiotCoefficientMaterial
    model = user
    biot_coefficient = 1
  []
[]
##########################################################
[AuxVariables]
  [stress_xx]
    order = CONSTANT
    family = MONOMIAL
  []
  [stress_xy]
    order = CONSTANT
    family = MONOMIAL
  []
  [stress_xz]
    order = CONSTANT
    family = MONOMIAL
  []
  [stress_yy]
    order = CONSTANT
    family = MONOMIAL
  []
  [stress_yz]
    order = CONSTANT
    family = MONOMIAL
  []
  [stress_zz]
    order = CONSTANT
    family = MONOMIAL
  []
  # darcy veloctiy
  # [darcy_vel_x]
  #   # type = MooseVariableConstMonomial
  #   family = MONOMIAL
  #   order = CONSTANT
    
  # []
  # [darcy_vel_y]
  #   # type = MooseVariableConstMonomial
  #   family = MONOMIAL
  #   order = CONSTANT
  # []
  # [darcy_vel_z]
  #   # type = MooseVariableConstMonomial
  #   family = MONOMIAL
  #   order = CONSTANT
  # []

  # T_ref is needed. Becuase density is pressure and temperature dependent.
  [T_ref]
    order = CONSTANT
    family = MONOMIAL
  []
  # Material Property outputs
  [solid_bulk_compliance]
    order = CONSTANT
    family = MONOMIAL
  []
  [biot_modulus]
      family = MONOMIAL
      order  = CONSTANT
  []
  [fluid_density]
    order = CONSTANT
    family = MONOMIAL
  []
  [fluid_internal_energy]
    order = CONSTANT
    family = MONOMIAL
  []
  [rock_energy_density]
    order = CONSTANT
    family = MONOMIAL
  []
  [vol_strain]
    order = CONSTANT
    family = MONOMIAL
  []
[]
##########################################################
[AuxKernels]
  [stress_xx]
    type = OrcaADRankTwoAux
    rank_two_tensor = stress
    variable = stress_xx
    index_i = 0
    index_j = 0
  []
  [stress_xy]
    type = OrcaADRankTwoAux
    rank_two_tensor = stress
    variable = stress_xy
    index_i = 0
    index_j = 1
  []
  [stress_xz]
    type = OrcaADRankTwoAux
    rank_two_tensor = stress
    variable = stress_xz
    index_i = 0
    index_j = 2
  []
  [stress_yy]
    type = OrcaADRankTwoAux
    rank_two_tensor = stress
    variable = stress_yy
    index_i = 1
    index_j = 1
  []
  [stress_yz]
    type = OrcaADRankTwoAux
    rank_two_tensor = stress
    variable = stress_yz
    index_i = 1
    index_j = 2
  []
  [stress_zz]
    type = OrcaADRankTwoAux
    rank_two_tensor = stress
    variable = stress_zz
    index_i = 2
    index_j = 2
  []
  # darcy velocity
# [darcy_x_aux]
#     type = OrcaDarcyVelocityComponent
#     component = 0
#     variable = darcy_vel_x
#     pore_pressure = pore_pressure
# []
# [darcy_y_aux]
#     type = OrcaDarcyVelocityComponent
#     component = 1
#     variable = darcy_vel_y
#     pore_pressure = pore_pressure
# []
# [darcy_z_aux]
#     type = OrcaDarcyVelocityComponent
#     component =2
#     variable = darcy_vel_z
#     pore_pressure = pore_pressure
# []
  [Tref_const]
    type = ConstantAux
    variable = T_ref
    value = 273.15
  []
  [solid_bulk_compliance]
    type     = ADMaterialRealAux
    variable = solid_bulk_compliance
    property = solid_bulk_compliance_qp  
    execute_on = 'initial timestep_end'
  []
  [biot_modulus]
    type     = ADMaterialRealAux
    variable = biot_modulus
    property = biot_modulus_qp   
    execute_on = 'initial timestep_end'
  []
  [fluid_density]
    type     = ADMaterialRealAux
    variable = fluid_density
    property = fluid_density_qp   
    execute_on = 'initial timestep_end'
  []
  [fluid_internal_energy]
    type     = ADMaterialRealAux
    variable = fluid_internal_energy
    property = fluid_internal_energy_qp   
    execute_on = 'initial timestep_end'
  []
  [rock_energy_density]
    type     = ADMaterialRealAux
    variable = rock_energy_density
    property = rock_energy_density_qp   
    execute_on = 'initial timestep_end'
  []
  [vol_strain]
    type     = ADMaterialRealAux
    variable = vol_strain
    property = vol_strain_rate  
    execute_on = 'initial timestep_end'
  []
[]
##########################################################
[BCs]
  [confinex]
    type = DirichletBC
    variable = disp_x
    value = 0
    boundary = 'left right'
  []
  [confiney]
    type = DirichletBC
    variable = disp_y
    value = 0
    boundary = 'bottom top'
  []
  [basefixed]
    type = DirichletBC
    variable = disp_z
    value = 0
    boundary = 'back'
  []
  [topdrained]
    type = DirichletBC
    variable = pore_pressure
    value = 0
    boundary = 'front'
  []
  [topload]
    type = NeumannBC
    variable = disp_z
    value = -1
    boundary = 'front'
  []
  [toptemp]
    type = DirichletBC
    variable = temperature
    value = 323.15
    boundary = 'front'
  []
[]
##########################################################
[Preconditioning]
  [preferred]
    #per Andy
    type = SMP
    full = true
    petsc_options_iname = '-pc_type -pc_factor_mat_solver_package'
    petsc_options_value = ' lu       mumps'
  []
[]
#########################################################
[Postprocessors]
  [p0]
    type = PointValue
    outputs = csv
    point = '0 0 0'
    variable = pore_pressure
    use_displaced_mesh = false
  []
  [p2_4_2]
    type = PointValue
    outputs = csv
    point = '0 0 4.2'
    variable = pore_pressure
    use_displaced_mesh = false
  []
  [p_5_6]
    type = PointValue
    outputs = csv
    point = '0 0 5.6'
    variable = pore_pressure
    use_displaced_mesh = false
  []

  [t0]
    type = PointValue
    outputs = csv
    point = '0 0 0'
    variable = temperature
    use_displaced_mesh = false
  []
  [t2_4_2]
    type = PointValue
    outputs = csv
    point = '0 0 4.2'
    variable = temperature
    use_displaced_mesh = false
  []
  [t_5_6]
    type = PointValue
    outputs = csv
    point = '0 0 5.6'
    variable = temperature
    use_displaced_mesh = false
  []
  
  [zdis_1_4]
    type = PointValue
    outputs = csv
    point = '0 0 1.4'
    variable = disp_z
    use_displaced_mesh = false
  []
  [zdisp_4_2]
    type = PointValue
    outputs = csv
    point = '0 0 4.2'
    variable = disp_z
    use_displaced_mesh = false
  []
  [zdisp_7]
    type = PointValue
    outputs = csv
    point = '0 0 7'
    variable = disp_z
    use_displaced_mesh = false
  []
  [dt]
    type = FunctionValuePostprocessor
    outputs = console
    function = if(0.5*t<0.1,0.5*t,0.1)
  []
[]
#########################################################
[Executioner]
  type = Transient
  solve_type = Newton
  start_time = 0
  end_time = 1e+04 # 1e+05
  
  [TimeStepper]
    type = FunctionDT
    function = 'time_step_fct'
  []

# controls for linear iterations
  l_max_its = 50
  l_tol = 1e-4
# controls for nonlinear iterations
  nl_max_its = 50
  nl_abs_tol = 1e-6
[]

[Functions]
    [time_step_fct]
    type = PiecewiseConstant
    x = '0 0.1 1 5 10 50 100 500 1000 5000 10000'
    y = '0.01 0.01 0.1 0.5 1 5 10 50 100 500 1000'
    []
[]
##########################################################
[Outputs]
  file_base = THM_Consolidation_ghasemi
  exodus = true
  [csv]
    type = CSV
  []
[]
##########################################################
