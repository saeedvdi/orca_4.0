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
 * Fixed issues (compared to the original):
 *  FIX 1 (shared): interface normal pre-computed once per boundary from unmodified
 *         geometry and stored in _interface_normals, then used consistently in
 *         stitchNodesToElems. The original code computed the normal lazily from the
 *         first element pair encountered and reused it for all nodes, which gave
 *         wrong results on oblique / non-planar fractures.
 *  FIX 2 (shared): neighbor_side captured via which_neighbor_am_i BEFORE set_node
 *         is called on elem, preventing stale node-ID mismatches in libMesh versions
 *         that use node-ID matching for neighbor lookup.
 *  FIX 3 (3D-only): front-node detection in getSidesetNodes replaced by a
 *         cross-neighbor check. The original edge-face-count approach incorrectly
 *         excluded boundary-reaching nodes (face_count == 1 at the sample surface)
 *         as if they were crack-front nodes.
 *  FIX 4 (3D-only): ids_to_construct now filters the active side list by
 *         mesh_dimension before deciding whether to skip reconstruction, preventing
 *         premature skips on mixed-dimensional meshes.
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
  using SplitNodeMap = std::map<boundary_id_type, std::map<dof_id_type, dof_id_type>>;

  struct BndElementData
  {
    Elem * elem;
    unsigned short side;
    boundary_id_type bnd_id;
  };

  BoundaryNodeSetMap getSidesetNodes(const std::vector<BndElementData> & bnd_elems,
                                     const std::set<boundary_id_type> & mesh_sideset_ids) const;

  SplitNodeMap splitNodesOnInterface(const BoundaryNodeSetMap & bnd_node_ids,
                                     std::unique_ptr<MeshBase> & mesh) const;

  void stitchNodesToElems(const SplitNodeMap & split_nodes_map,
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
  // generate() and consumed in stitchNodesToElems. Declared mutable so that
  // generate() (which is logically const from MOOSE's perspective) can populate it.
  mutable std::map<boundary_id_type, RealVectorValue> _interface_normals;
};
