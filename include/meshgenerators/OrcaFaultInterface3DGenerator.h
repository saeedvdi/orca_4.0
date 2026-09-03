#pragma once

#include "MeshGenerator.h"

#include "libmesh/boundary_info.h"

/**
 * OrcaFaultInterface3DGenerator
 *
 * Splits an interior 3D fault surface into a CZM interface by duplicating nodes
 * on the selected sideset or nodeset and stitching the duplicated nodes to one
 * side of each element pair that straddles the interface.
 *
 * Verified against Sneddon's closed form and, on a T-junction, against MOOSE's
 * BreakMeshByBlockGenerator; see
 * Examples/Validaitons/benchmarks/mesh_generator_check/.
 *
 * Fixed issues (compared to the original). Every one of FIX 5-10 was silent: the mesh
 * built, the interface kernels assembled and the solve converged on a wrong answer.
 *  FIX 1: interface normal pre-computed once per boundary from unmodified geometry and
 *         stored in _interface_normals. The original computed it lazily from the first
 *         element pair encountered and reused it for all nodes, which is wrong on
 *         oblique or non-planar fractures.
 *  FIX 2: neighbor_side captured before set_node, so node-ID-based neighbour lookup
 *         cannot go stale. Subsumed by FIX 10, which does all sideset bookkeeping
 *         before any node is repointed.
 *  FIX 3: superseded by FIX 5. It replaced the original face-count front detection with
 *         a cross-neighbour check that was a tautology, leaving the front options inert.
 *  FIX 4: ids_to_construct filters the active side list by mesh_dimension before
 *         deciding whether to skip reconstruction, preventing premature skips on
 *         mixed-dimensional meshes.
 *  FIX 5: real crack-front detection -- an edge bounding the interface that does not
 *         reach the specimen surface. Before this the front options did nothing and an
 *         embedded crack opened at its tips, reading 15 % too long.
 *  FIX 6: secondary sideset ids are reserved when handed out. Allocating registered only
 *         a NAME, so a second fracture was given the same id and every secondary sideset
 *         collapsed into one boundary -- surfacing much later as libMesh's
 *         "Periodic boundary neighbor not found".
 *  FIX 7: interface faces are de-duplicated against what the sideset actually holds, so
 *         a ONE-SIDED sideset works. Before this every face of such a sideset was
 *         dropped and the fracture came out welded with zero opening.
 *  FIX 8: an interface edge terminating on ANOTHER interface is a junction, not a crack
 *         front, and must be split.
 *  FIX 9: front and junction detection made edge-based rather than node-based. In a
 *         plane-strain model one element thick every node is on an exterior face, so a
 *         node test split every crack tip.
 *  FIX 10: interface nodes are partitioned by CONNECTIVITY rather than by a geometric
 *         half-space test per interface. The old scheme inverted the partition at a
 *         junction -- welding the quadrants a fracture separates and splitting the block
 *         nothing runs through -- while still producing the right number of node copies.
 */
class OrcaFaultInterface3DGenerator : public MeshGenerator
{
public:
  static InputParameters validParams();

  OrcaFaultInterface3DGenerator(const InputParameters & parameters);

  std::unique_ptr<MeshBase> generate() override;

protected:
  using NodeToElemMap = std::map<dof_id_type, std::vector<dof_id_type>>;
  using BoundaryNodeSetMap = std::map<boundary_id_type, std::set<dof_id_type>>;

  struct BndElementData
  {
    Elem * elem;
    unsigned short side;
    boundary_id_type bnd_id;
  };

  BoundaryNodeSetMap getSidesetNodes(const std::vector<BndElementData> & bnd_elems,
                                     const std::set<boundary_id_type> & mesh_sideset_ids,
                                     const libMesh::MeshBase & mesh) const;

  /// Edges lying IN the exterior surface of the mesh, i.e. edges of element sides with no
  /// neighbor. Used to tell a true crack front (terminating inside the material) from the
  /// line where a through-going fracture daylights on the sample surface.
  ///
  /// Edge-based, not node-based, and that distinction is essential. In a plane-strain
  /// model one element thick, EVERY node lies on the z-min or z-max face, so a node test
  /// calls every crack tip "exterior" and splits it. The tip EDGE runs through the
  /// thickness at an interior (x, y) and is not an edge of any exterior face, so the edge
  /// test separates the two correctly at any thickness.
  static std::set<std::pair<dof_id_type, dof_id_type>>
  exteriorEdges(const libMesh::MeshBase & mesh);

  /// Split every interface node into as many copies as there are pieces of material
  /// meeting at it, and move each sideset onto one side of its interface.
  ///
  /// FIX 10 replaces a pair of routines that duplicated ONE node per (sideset, node) and
  /// then assigned elements to sides with a geometric half-space test against the
  /// interface normal. That is correct for a single fracture and wrong wherever two meet:
  /// at a T-junction the second interface's pass also repointed elements that do not touch
  /// it at all -- splitting the block ABOVE the junction, which no fracture separates,
  /// while leaving the two flanks that a fracture does separate welded together. The node
  /// COUNT came out right (three copies) and the connectivity was inverted, so nothing
  /// downstream complained.
  ///
  /// The partition is now by connectivity: two elements at a node belong to the same piece
  /// when they share a face that contains the node and is not an interface face. For a
  /// single fracture this reduces exactly to the old two-sided split.
  void splitInterfaceNodes(const BoundaryNodeSetMap & bnd_node_ids,
                           NodeToElemMap & node_to_elem_map,
                           const std::vector<BndElementData> & bnd_elems,
                           std::unique_ptr<MeshBase> & mesh) const;

  std::unique_ptr<MeshBase> & _input;

  const std::vector<BoundaryName> _sideset_names;
  const std::vector<BoundaryName> _nodeset_names;
  const bool _add_interface_on_two_sides;
  const bool _preserve_front_nodes;
  const bool _split_only_interior_nodes;
  const bool _rebuild_sidesets_from_nodesets;
  const std::vector<BoundaryName> _secondary_sideset_names;
  const std::string _secondary_sideset_suffix;

  // Maps primary boundary ID -> secondary boundary ID (populated in generate()).
  mutable std::map<boundary_id_type, boundary_id_type> _primary_to_secondary_id;

  // FIX 1: Per-boundary interface normals computed from unmodified geometry in
  // generate() and consumed in splitInterfaceNodes. Declared mutable so that
  // generate() (which is logically const from MOOSE's perspective) can populate it.
  mutable std::map<boundary_id_type, RealVectorValue> _interface_normals;
};
