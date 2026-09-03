######################################################################################
# MESH-GENERATOR CHECK: two fractures at once, with two-sided interfaces
#
# Guards FIX 6. Until it, OrcaFaultInterface3DGenerator could not build more than ONE
# fracture whenever `add_interface_on_two_sides = true` -- which is always, because that
# is what InterfaceKernels need. Allocating a secondary sideset only registered a NAME,
# not the boundary id, so the second allocation handed out the SAME id and every secondary
# sideset collapsed into one boundary.
#
# The symptom appeared far from the cause: the generator succeeded and the mesh then died
# in libMesh's find_neighbors with "Periodic boundary neighbor not found"
# (periodic_boundaries.C:107), because add_disjoint_neighbor_boundary_pairs could not pair
# a primary face against a secondary boundary holding both sides of both fractures.
#
# It was NOT about the fractures intersecting, which is what it first looked like. Two
# PARALLEL fractures failed the same way, and two intersecting ones were fine with
# `add_interface_on_two_sides = false`. The trigger is two or more sidesets plus two-sided
# interfaces. A single fracture -- all the Kalantar2025 decks use one `fracture_interface`
# nodeset -- allocates once and was never affected.
#
# The geometry is a T, matching ../fracutre_interseciton_problem: a vertical interface at
# x = 0 spanning y in [-2, 0] meeting the middle of a horizontal one at y = 0 spanning
# x in [-2, 2]. Mesh-only; the physics of this configuration is covered by that benchmark.
#
# PASSES when the mesh builds and the four sidesets come out with DISTINCT ids and their
# expected side counts: frac_h 8, frac_v 4, frac_h_o 8, frac_v_o 4. Before the fix,
# frac_h_o and frac_v_o shared an id.
######################################################################################
[Mesh]
  [base]
    type = GeneratedMeshGenerator
    dim = 3
    nx = 8
    ny = 8
    nz = 2
    xmin = -4
    xmax = 4
    ymin = -4
    ymax = 4
    zmin = 0
    zmax = 1
  []
  [lower_left]
    type = SubdomainBoundingBoxGenerator
    input = base
    bottom_left = '-2 -2 -1'
    top_right = '0 0 2'
    block_id = 2
    block_name = lower_left
  []
  [lower_right]
    type = SubdomainBoundingBoxGenerator
    input = lower_left
    bottom_left = '0 -2 -1'
    top_right = '2 0 2'
    block_id = 3
    block_name = lower_right
  []
  [cap]
    type = SubdomainBoundingBoxGenerator
    input = lower_right
    bottom_left = '-2 0 -1'
    top_right = '2 4 2'
    block_id = 4
    block_name = cap
  []
  # One-sided sidesets, as SideSetsBetweenSubdomainsGenerator produces them. This also
  # exercises FIX 7 on a second geometry.
  [frac_h]
    type = SideSetsBetweenSubdomainsGenerator
    input = cap
    primary_block = 'lower_left lower_right'
    paired_block = 'cap'
    new_boundary = 'frac_h'
  []
  [frac_v]
    type = SideSetsBetweenSubdomainsGenerator
    input = frac_h
    primary_block = 'lower_left'
    paired_block = 'lower_right'
    new_boundary = 'frac_v'
  []
  [split]
    type = OrcaFaultInterface3DGenerator
    input = frac_v
    sidesets = 'frac_h frac_v'
    preserve_front_nodes = true
    split_only_interior_nodes = true
    add_interface_on_two_sides = true
    secondary_sidesets = 'frac_h_other frac_v_other'
  []
[]

[Outputs]
  exodus = true
[]
