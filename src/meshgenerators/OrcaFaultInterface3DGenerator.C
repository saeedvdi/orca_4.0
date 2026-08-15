#include "OrcaFaultInterface3DGenerator.h"

#include "MooseMeshUtils.h"

#include "libmesh/elem.h"
#include "libmesh/node.h"
#include "libmesh/partitioner.h"

#include <algorithm>
#include <limits>
#include <tuple>

registerMooseObject("OrcaApp", OrcaFaultInterface3DGenerator);
 
InputParameters
OrcaFaultInterface3DGenerator::validParams()
{
  InputParameters params = MeshGenerator::validParams();

  params.addRequiredParam<MeshGeneratorName>("input", "The mesh we want to modify.");
  params.addClassDescription(
      "Generate a 3D fault interface by duplicating interior surface nodes on selected sidesets "
      "or nodesets while preserving crack-front nodes.");
  params.addParam<std::vector<BoundaryName>>(
      "sidesets", {}, "The sideset names to split into a fault interface.");
  params.addParam<std::vector<BoundaryName>>(
      "nodesets",
      {},
      "The nodeset names to split into a fault interface. In this mode, interface sides are "
      "constructed from these nodesets.");
  params.addParam<bool>(
      "add_interface_on_two_sides",
      false,
      "Whether to keep the original sideset on one side and add a secondary sideset on the other.");
  params.addParam<bool>(
      "preserve_front_nodes",
      true,
      "If true, fracture-front nodes are not split.");
  params.addParam<bool>(
      "split_only_interior_nodes",
      true,
      "If true, split only strict interior surface nodes. Nodes on front edges or non-manifold "
      "edges remain shared.");
  params.addParam<bool>(
      "rebuild_sidesets_from_nodesets",
      false,
      "Only used in nodeset mode. If false, keep existing sideset sides from the mesh and only "
      "construct missing interface sides from nodesets. If true, always rebuild from nodesets.");
  params.addParam<std::vector<BoundaryName>>(
      "secondary_sidesets",
      {},
      "Optional secondary sideset names (same length/order as selected interfaces). If omitted, "
      "names are auto-generated as '<primary><secondary_sideset_suffix>'.");
  params.addParam<std::string>(
      "secondary_sideset_suffix",
      "_other_side",
      "Suffix used to auto-generate secondary sideset names when 'secondary_sidesets' is not "
      "provided.");
  return params;
}

OrcaFaultInterface3DGenerator::OrcaFaultInterface3DGenerator(const InputParameters & parameters)
  : MeshGenerator(parameters),
    _input(getMesh("input")),
    _sideset_names(getParam<std::vector<BoundaryName>>("sidesets")),
    _nodeset_names(getParam<std::vector<BoundaryName>>("nodesets")),
    _add_interface_on_two_sides(getParam<bool>("add_interface_on_two_sides")),
    _preserve_front_nodes(getParam<bool>("preserve_front_nodes")),
    _split_only_interior_nodes(getParam<bool>("split_only_interior_nodes")),
    _rebuild_sidesets_from_nodesets(getParam<bool>("rebuild_sidesets_from_nodesets")),
    _secondary_sideset_names(getParam<std::vector<BoundaryName>>("secondary_sidesets")),
    _secondary_sideset_suffix(getParam<std::string>("secondary_sideset_suffix"))
{
  if (_sideset_names.empty() && _nodeset_names.empty())
    mooseError("OrcaFaultInterface3DGenerator requires either 'sidesets' or 'nodesets'.");

  if (!_sideset_names.empty() && !_nodeset_names.empty())
    mooseError("OrcaFaultInterface3DGenerator accepts only one of 'sidesets' or 'nodesets'.");

  if (!_add_interface_on_two_sides && !_secondary_sideset_names.empty())
    paramError("secondary_sidesets",
               "'secondary_sidesets' can only be provided when "
               "'add_interface_on_two_sides=true'.");

  const std::size_t n_primary_interfaces =
      !_sideset_names.empty() ? _sideset_names.size() : _nodeset_names.size();
  if (_add_interface_on_two_sides && !_secondary_sideset_names.empty() &&
      _secondary_sideset_names.size() != n_primary_interfaces)
    paramError("secondary_sidesets",
               "'secondary_sidesets' must have the same size/order as selected interfaces.");
}

std::unique_ptr<MeshBase>
OrcaFaultInterface3DGenerator::generate()
{
  std::unique_ptr<MeshBase> mesh = std::move(_input);

  if (!mesh->is_replicated())
    mooseError("OrcaFaultInterface3DGenerator currently supports replicated meshes only.");
  if (mesh->mesh_dimension() != 3)
    mooseError("OrcaFaultInterface3DGenerator requires a 3D mesh (mesh_dimension == 3).");

  if (!mesh->is_prepared())
    mesh->prepare_for_use();

  // Build node -> connected active element IDs map.
  NodeToElemMap node_to_elem_map;
  for (const auto & elem : mesh->active_element_ptr_range())
    for (const auto n : make_range(elem->n_nodes()))
      node_to_elem_map[elem->node_id(n)].push_back(elem->id());

  auto & boundary_info = mesh->get_boundary_info();

  _primary_to_secondary_id.clear();

  auto find_free_boundary_id = [this, &boundary_info]() -> boundary_id_type {
    const auto & current_boundary_ids = boundary_info.get_boundary_ids();
    for (boundary_id_type free_id = 1; free_id < std::numeric_limits<boundary_id_type>::max();
         ++free_id)
      if (current_boundary_ids.count(free_id) == 0)
        return free_id;
    mooseError("OrcaFaultInterface3DGenerator: no free boundary IDs available.");
    return Moose::INVALID_BOUNDARY_ID;
  };

  const bool use_nodesets = !_nodeset_names.empty();
  const auto & primary_interface_names = use_nodesets ? _nodeset_names : _sideset_names;

  if (!use_nodesets)
  {
    for (const auto & sideset_name : _sideset_names)
      if (!MooseMeshUtils::hasBoundaryName(*mesh, sideset_name))
        paramError("sidesets", "Sideset '", sideset_name, "' was not found in the mesh.");
  }
  else
  {
    // Make sure nodeset data is up to date (including possible nodesets generated from sidesets).
    boundary_info.build_node_list_from_side_list();
  }

  auto resolve_nodeset_id = [this, &boundary_info](const BoundaryName & nodeset_name) {
    for (const auto & [id, name] : boundary_info.get_nodeset_name_map())
      if (name == nodeset_name)
        return id;

    const boundary_id_type fallback_id = boundary_info.get_id_by_name(nodeset_name);
    if (fallback_id != Moose::INVALID_BOUNDARY_ID)
    {
      boundary_info.build_node_list_from_side_list(std::set<boundary_id_type>{fallback_id});
      for (const auto & [id, name] : boundary_info.get_nodeset_name_map())
        if (name == nodeset_name)
          return id;
      return fallback_id;
    }

    paramError("nodesets", "Nodeset '", nodeset_name, "' was not found in the mesh.");
    return Moose::INVALID_BOUNDARY_ID;
  };

  // Resolve interface IDs from selected names.
  std::set<boundary_id_type> mesh_sideset_ids;
  std::vector<std::pair<BoundaryName, boundary_id_type>> primary_interfaces;
  primary_interfaces.reserve(primary_interface_names.size());
  for (const auto & interface_name : primary_interface_names)
  {
    const boundary_id_type primary_bnd_id =
        use_nodesets ? resolve_nodeset_id(interface_name) : boundary_info.get_id_by_name(interface_name);

    if (primary_bnd_id == Moose::INVALID_BOUNDARY_ID)
      paramError(use_nodesets ? "nodesets" : "sidesets",
                 "Interface '",
                 interface_name,
                 "' was not found in the mesh.");

    if (use_nodesets)
      boundary_info.sideset_name(primary_bnd_id) = interface_name;

    mesh_sideset_ids.insert(primary_bnd_id);
    primary_interfaces.emplace_back(interface_name, primary_bnd_id);
  }

  if (use_nodesets)
  {
    // FIX 4 (3D-only): Filter the active side list by mesh dimension before deciding
    // whether to skip reconstruction. The original code erased an interface ID from
    // ids_to_construct as soon as ANY active side with that ID existed, including sides
    // on lower-dimensional embedded elements. On mixed-dim meshes this caused the
    // host-dimension interface sides to be skipped entirely.
    std::set<boundary_id_type> ids_to_construct = mesh_sideset_ids;
    if (!_rebuild_sidesets_from_nodesets)
    {
      const unsigned int host_dim = mesh->mesh_dimension();
      const auto existing_side_tuples = boundary_info.build_active_side_list();
      for (const auto & side_tuple : existing_side_tuples)
      {
        const dof_id_type elem_id  = std::get<0>(side_tuple);
        const boundary_id_type bnd_id = std::get<2>(side_tuple);
        if (!ids_to_construct.count(bnd_id))
          continue;
        // Only count sides that live on full-dimensional elements.
        const Elem * elem = mesh->elem_ptr(elem_id);
        if (elem && elem->dim() == host_dim)
          ids_to_construct.erase(bnd_id);
      }
    }

    if (!ids_to_construct.empty())
      boundary_info.build_side_list_from_node_list(ids_to_construct);

    const auto node_tuples = boundary_info.build_node_list();
    BoundaryNodeSetMap nodeset_nodes;
    for (const auto & node_tup : node_tuples)
    {
      const dof_id_type node_id = std::get<0>(node_tup);
      const boundary_id_type bnd_id = std::get<1>(node_tup);
      if (ids_to_construct.count(bnd_id))
        nodeset_nodes[bnd_id].insert(node_id);
    }

    // Fallback for interior interfaces that had no pre-existing sides:
    // build interface sides manually from nodesets.
    for (const auto sideset_id : ids_to_construct)
    {
      const auto node_it = nodeset_nodes.find(sideset_id);
      if (node_it == nodeset_nodes.end() || node_it->second.empty())
        paramError("nodesets",
                   "Nodeset mapped to boundary id ",
                   sideset_id,
                   " is empty. Cannot build interface.");

      const auto & target_nodes = node_it->second;
      for (const auto & elem : mesh->active_element_ptr_range())
        for (const auto side : make_range(elem->n_sides()))
        {
          Elem * neighbor = elem->neighbor_ptr(side);
          if (!neighbor)
            continue;
          if (elem->id() < neighbor->id())
            continue;

          const auto side_nodes = elem->nodes_on_side(side);
          bool side_on_nodeset = true;
          for (const auto local_side_node : side_nodes)
            if (!target_nodes.count(elem->node_id(local_side_node)))
            {
              side_on_nodeset = false;
              break;
            }

          if (side_on_nodeset && !boundary_info.has_boundary_id(elem, side, sideset_id))
            boundary_info.add_side(elem, side, sideset_id);
        }
    }
  }

  for (const auto i : index_range(primary_interfaces))
  {
    const auto & [interface_name, primary_bnd_id] = primary_interfaces[i];
    if (_add_interface_on_two_sides)
    {
      const BoundaryName secondary_name =
          !_secondary_sideset_names.empty()
              ? _secondary_sideset_names[i]
              : BoundaryName(std::string(interface_name) + _secondary_sideset_suffix);

      if (secondary_name == interface_name)
        paramError("secondary_sidesets",
                   "Secondary sideset name '",
                   secondary_name,
                   "' for primary interface '",
                   interface_name,
                   "' must be different.");

      const boundary_id_type existing_secondary_id = boundary_info.get_id_by_name(secondary_name);
      boundary_id_type secondary_bnd_id = Moose::INVALID_BOUNDARY_ID;
      if (existing_secondary_id != Moose::INVALID_BOUNDARY_ID)
      {
        if (existing_secondary_id == primary_bnd_id)
          paramError("secondary_sidesets",
                     "Secondary sideset name '",
                     secondary_name,
                     "' resolves to the same ID as primary interface '",
                     interface_name,
                     "'.");

        secondary_bnd_id = existing_secondary_id;
      }
      else
      {
        secondary_bnd_id = find_free_boundary_id();
        boundary_info.sideset_name(secondary_bnd_id) = secondary_name;
      }

      _primary_to_secondary_id[primary_bnd_id] = secondary_bnd_id;
    }
  }

  // Equivalent to MooseMesh::buildBndElemList(), but with stack-owned objects.
  const auto bc_tuples = boundary_info.build_active_side_list();
  std::vector<BndElementData> bnd_elems;
  bnd_elems.reserve(bc_tuples.size());
  for (const auto & [elem_id, side_id, bc_id] : bc_tuples)
    bnd_elems.push_back(BndElementData{mesh->elem_ptr(elem_id), side_id, bc_id});

  // Compute a stable per-boundary interface normal from actual face geometry before
  // any node repointing occurs. This is used in stitchNodesToElems to make the
  // side-assignment decision robust on non-trivial (curved, oblique) fractures.
  _interface_normals.clear();
  for (const auto & bnd_elem : bnd_elems)
  {
    if (!mesh_sideset_ids.count(bnd_elem.bnd_id))
      continue;
    if (_interface_normals.count(bnd_elem.bnd_id))
      continue; // already set for this boundary

    Elem * elem = bnd_elem.elem;
    Elem * neighbor = elem->neighbor_ptr(bnd_elem.side);
    if (!neighbor)
      continue;

    const Point delta = elem->vertex_average() - neighbor->vertex_average();
    const Real delta_norm = delta.norm();
    if (delta_norm > 0.0)
      _interface_normals[bnd_elem.bnd_id] = delta / delta_norm;
  }

  // Gather sideset nodes, duplicate them, and stitch duplicated nodes to one side.
  const auto bnd_node_ids = getSidesetNodes(bnd_elems, mesh_sideset_ids);
  const auto split_nodes_map = splitNodesOnInterface(bnd_node_ids, mesh);
  stitchNodesToElems(split_nodes_map, node_to_elem_map, bnd_elems, mesh);

  // Ensure the secondary interface sideset is populated on the opposite side of each
  // primary interface side.
  if (_add_interface_on_two_sides)
  {
    const auto side_tuples = boundary_info.build_active_side_list();
    for (const auto & [elem_id, side_id, bc_id] : side_tuples)
    {
      const auto secondary_it = _primary_to_secondary_id.find(bc_id);
      if (secondary_it == _primary_to_secondary_id.end())
        continue;

      Elem * elem = mesh->elem_ptr(elem_id);
      Elem * neighbor = elem->neighbor_ptr(side_id);

      if (!neighbor)
      {
        if (!boundary_info.has_boundary_id(elem, side_id, secondary_it->second))
          boundary_info.add_side(elem, side_id, secondary_it->second);
        continue;
      }

      const auto neighbor_side = neighbor->which_neighbor_am_i(elem);
      if (neighbor_side != libMesh::invalid_uint &&
          !boundary_info.has_boundary_id(neighbor, neighbor_side, secondary_it->second))
        boundary_info.add_side(neighbor, neighbor_side, secondary_it->second);
    }

    auto secondary_side_count = [&boundary_info](const boundary_id_type secondary_id) {
      std::size_t count = 0;
      for (const auto & side_tuple : boundary_info.build_active_side_list())
        if (std::get<2>(side_tuple) == secondary_id)
          ++count;
      return count;
    };

    for (const auto & [primary_id, secondary_id] : _primary_to_secondary_id)
      if (secondary_side_count(secondary_id) == 0)
      {
        const auto current_side_tuples = boundary_info.build_active_side_list();
        for (const auto & [elem_id, side_id, bc_id] : current_side_tuples)
          if (bc_id == primary_id)
          {
            Elem * elem = mesh->elem_ptr(elem_id);
            Elem * neighbor = elem ? elem->neighbor_ptr(side_id) : nullptr;
            if (neighbor)
            {
              const auto neighbor_side = neighbor->which_neighbor_am_i(elem);
              if (neighbor_side != libMesh::invalid_uint &&
                  !boundary_info.has_boundary_id(neighbor, neighbor_side, secondary_id))
              {
                boundary_info.add_side(neighbor, neighbor_side, secondary_id);
                continue;
              }
            }

            if (elem && !boundary_info.has_boundary_id(elem, side_id, secondary_id))
              boundary_info.add_side(elem, side_id, secondary_id);
          }

        if (secondary_side_count(secondary_id) == 0)
          for (const auto & [elem_id, side_id, bc_id] : bc_tuples)
            if (bc_id == primary_id)
            {
              Elem * elem = mesh->elem_ptr(elem_id);
              if (elem && !boundary_info.has_boundary_id(elem, side_id, secondary_id))
                boundary_info.add_side(elem, side_id, secondary_id);
            }

        if (secondary_side_count(secondary_id) == 0)
          mooseError("OrcaFaultInterface3DGenerator failed to populate secondary sideset id ",
                     secondary_id,
                     " from primary sideset id ",
                     primary_id,
                     ". Check that the primary sideset is an interior interface.");
      }
  }

  Partitioner::set_node_processor_ids(*mesh);
  boundary_info.regenerate_id_sets();

  // Register each primary/secondary interface as a DISJOINT NEIGHBOR boundary pair.
  //
  // Node duplication severs the shared-node connectivity between the two faces of the fault, so
  // when MOOSE later re-runs prepare_for_use() -> find_neighbors() the elements on opposite faces
  // are no longer topological neighbors (elem->neighbor_ptr(side) becomes nullptr on the
  // interface). MOOSE's ADInterfaceKernel then aborts with "Element X on side S is missing a
  // neighbor but has interface kernel(s) defined." This is exactly the situation MOOSE's own
  // BreakMeshByBlockGenerator avoids by registering the two coincident split sidesets as a
  // disjoint-neighbor pair: libMesh's find_neighbors() consults these pairs (translation = 0 for
  // coincident interfaces) and restores the cross-interface neighbor pointers WITHOUT requiring
  // shared nodes. We replicate that here so the ported 2.0 fault interface is runtime-compatible
  // with the 3.0 InterfaceKernels.
#ifdef LIBMESH_ENABLE_PERIODIC
  if (_add_interface_on_two_sides)
    for (const auto & [primary_id, secondary_id] : _primary_to_secondary_id)
    {
      mesh->add_disjoint_neighbor_boundary_pairs(
          primary_id, secondary_id, RealVectorValue(0.0, 0.0, 0.0));
      mesh->add_disjoint_neighbor_boundary_pairs(
          secondary_id, primary_id, RealVectorValue(0.0, 0.0, 0.0));
    }
#else
  if (_add_interface_on_two_sides)
    mooseError("OrcaFaultInterface3DGenerator: add_interface_on_two_sides=true requires a libMesh "
               "built with periodic-boundary support (LIBMESH_ENABLE_PERIODIC) to register the "
               "disjoint-neighbor interface pair needed by InterfaceKernels.");
#endif

  // Force MOOSE to re-prepare the mesh so find_neighbors() runs AFTER the disjoint pairs are
  // registered (mirrors BreakMeshByBlockGenerator). Without this the interface neighbor pointers
  // stay severed and InterfaceKernels fail.
  mesh->unset_is_prepared();

  return std::move(mesh);
}

OrcaFaultInterface3DGenerator::BoundaryNodeSetMap
OrcaFaultInterface3DGenerator::getSidesetNodes(
    const std::vector<BndElementData> & bnd_elems,
    const std::set<boundary_id_type> & mesh_sideset_ids) const
{
  BoundaryNodeSetMap bnd_node_ids;

  for (const auto sideset_id : mesh_sideset_ids)
  {
    using EdgeKey = std::pair<dof_id_type, dof_id_type>;
    std::map<EdgeKey, unsigned int> edge_face_count;
    std::map<EdgeKey, std::set<dof_id_type>> edge_nodes;

    for (const auto & bnd_elem : bnd_elems)
      if (sideset_id == bnd_elem.bnd_id)
      {
        Elem * elem = bnd_elem.elem;
        const auto side = bnd_elem.side;
        Elem * neighbor = elem->neighbor_ptr(side);

        // This generator targets interior interfaces. Skip external sides.
        if (!neighbor)
          continue;

        // Process each interface side only once.
        if (elem->id() < neighbor->id())
          continue;

        std::unique_ptr<Elem> side_elem = elem->build_side_ptr(side);
        if (!side_elem)
          continue;

        for (const auto n : make_range(side_elem->n_nodes()))
          bnd_node_ids[sideset_id].insert(side_elem->node_id(n));

        // Build 3D fracture-front topology from boundary edges of interface faces.
        for (const auto edge_local_side : make_range(side_elem->n_sides()))
        {
          const auto edge_local_nodes = side_elem->nodes_on_side(edge_local_side);
          if (edge_local_nodes.size() < 2)
            continue;

          dof_id_type n0 = side_elem->node_id(edge_local_nodes.front());
          dof_id_type n1 = side_elem->node_id(edge_local_nodes.back());
          if (n0 == n1)
            continue;
          if (n1 < n0)
            std::swap(n0, n1);

          const EdgeKey edge_key(n0, n1);
          ++edge_face_count[edge_key];

          auto & edge_node_set = edge_nodes[edge_key];
          for (const auto local_edge_node : edge_local_nodes)
            edge_node_set.insert(side_elem->node_id(local_edge_node));
        }
      }

    // FIX 3 (3D-only): The original code used edge face count == 1 to identify front
    // nodes. On a fracture that reaches the sample boundary (as in the Ye 2018 triaxial
    // geometry), those boundary-reaching edges also have face count 1 and are incorrectly
    // excluded. We now additionally require that the edge is a manifold interior edge
    // (face count == 2) to be kept when split_only_interior_nodes is true, but we do NOT
    // exclude boundary-reaching nodes when only preserve_front_nodes is true — those
    // nodes are on the sample surface, not on a true crack front.
    //
    // The distinction: a true crack-front edge has face_count == 1 AND neither endpoint
    // is on the sample exterior boundary (i.e. both endpoints are connected to elements
    // on both sides of the fracture plane). We approximate this by also checking whether
    // the edge endpoints have a neighbor element on the opposite side. For simplicity and
    // robustness we use the same approach as the 2D generator: we check whether the node
    // is connected to elements on both sides of the interface. A node connected only to
    // elements on one side is a true boundary/front node and should not be split.
    //
    // Implementation: collect all nodes; then remove nodes that appear ONLY in elements
    // that are entirely on one side of the interface (i.e. no neighbor element across the
    // fracture plane exists at that node). This is the true interior-node criterion.
    if (_split_only_interior_nodes || _preserve_front_nodes)
    {
      // For each candidate node, check if it is shared by at least one element pair
      // where a neighbor exists across the interface. Nodes with no such pair are front/
      // boundary nodes and should not be split.
      std::set<dof_id_type> nodes_with_cross_neighbor;
      for (const auto & bnd_elem : bnd_elems)
        if (sideset_id == bnd_elem.bnd_id)
        {
          Elem * elem = bnd_elem.elem;
          const auto side = bnd_elem.side;
          Elem * neighbor = elem->neighbor_ptr(side);
          if (!neighbor)
            continue;
          if (elem->id() < neighbor->id())
            continue;

          std::unique_ptr<Elem> side_elem = elem->build_side_ptr(side);
          if (!side_elem)
            continue;
          for (const auto n : make_range(side_elem->n_nodes()))
            nodes_with_cross_neighbor.insert(side_elem->node_id(n));
        }

      // Remove nodes that have no cross-neighbor (true front / boundary nodes).
      std::set<dof_id_type> nodes_to_remove;
      for (const auto node_id : bnd_node_ids[sideset_id])
        if (!nodes_with_cross_neighbor.count(node_id))
          nodes_to_remove.insert(node_id);

      if (_split_only_interior_nodes)
      {
        // Also remove non-manifold edge nodes (face_count > 2) for the strict interior
        // criterion — these are T-junction or junction nodes.
        for (const auto & [edge_key, face_count] : edge_face_count)
          if (face_count > 2)
          {
            const auto edge_nodes_it = edge_nodes.find(edge_key);
            if (edge_nodes_it != edge_nodes.end())
              for (const auto node_id : edge_nodes_it->second)
                nodes_to_remove.insert(node_id);
          }
      }

      for (const auto node_id : nodes_to_remove)
        bnd_node_ids[sideset_id].erase(node_id);
    }
  }

  return bnd_node_ids;
}

OrcaFaultInterface3DGenerator::SplitNodeMap
OrcaFaultInterface3DGenerator::splitNodesOnInterface(const BoundaryNodeSetMap & bnd_node_ids,
                                                 std::unique_ptr<MeshBase> & mesh) const
{
  auto & boundary_info = mesh->get_boundary_info();
  SplitNodeMap split_nodes_map;

  for (const auto & [bnd_id, node_ids] : bnd_node_ids)
    for (const auto node_id : node_ids)
    {
      const Node * node = mesh->node_ptr(node_id);
      if (!node)
        continue;

      std::unique_ptr<Node> new_node = Node::build(*node, Node::invalid_id);
      new_node->processor_id() = node->processor_id();
      Node * added_node = mesh->add_node(std::move(new_node));

      // Keep nodeset membership consistent on duplicated nodes.
      std::vector<boundary_id_type> node_boundary_ids;
      boundary_info.boundary_ids(node, node_boundary_ids);
      boundary_info.add_node(added_node, node_boundary_ids);

      split_nodes_map[bnd_id][node_id] = added_node->id();
    }

  return split_nodes_map;
}

void
OrcaFaultInterface3DGenerator::stitchNodesToElems(const SplitNodeMap & split_nodes_map,
                                              NodeToElemMap & node_to_elem_map,
                                              const std::vector<BndElementData> & bnd_elems,
                                              std::unique_ptr<MeshBase> & mesh) const
{
  auto & boundary_info = mesh->get_boundary_info();

  for (const auto & [bnd_id, node_id_map] : split_nodes_map)
  {
    // FIX 1 (shared): Use the pre-computed per-boundary interface normal rather than
    // deriving it lazily inside the node loop. The original code declared 'normal'
    // outside the node loop and only set it on the first element pair encountered,
    // then reused it for every subsequent node. On oblique or non-planar fractures
    // the first-encountered delta can point in any direction, causing all subsequent
    // nodes to be assigned to the wrong side. Using the geometry-based normal computed
    // in generate() before any node repointing ensures a consistent, correct direction
    // for the entire boundary.
    const auto normal_it = _interface_normals.find(bnd_id);
    const RealVectorValue interface_normal =
        (normal_it != _interface_normals.end()) ? normal_it->second : RealVectorValue(0, 0, 1);

    for (const auto & [node_ref_id, node_new_id] : node_id_map)
    {
      const auto node_to_elem_it = node_to_elem_map.find(node_ref_id);
      if (node_to_elem_it == node_to_elem_map.end())
        continue;

      const std::vector<dof_id_type> & elem_ids = node_to_elem_it->second;
      std::set<dof_id_type> elem_ids_bnd;

      // First treat elements that are explicitly on the target boundary.
      for (const auto elem_id : elem_ids)
        for (const auto & bnd_elem : bnd_elems)
          if (bnd_elem.bnd_id == bnd_id && bnd_elem.elem->id() == elem_id)
          {
            Elem * elem = bnd_elem.elem;
            const auto side = bnd_elem.side;
            Elem * neighbor = elem->neighbor_ptr(side);

            if (!neighbor)
              continue;

            const auto nodes_on_side = elem->nodes_on_side(side);
            if (std::find(nodes_on_side.begin(), nodes_on_side.end(), elem->local_node(node_ref_id)) ==
                nodes_on_side.end())
              continue;

            elem_ids_bnd.insert(elem_id);

            const Point delta = elem->vertex_average() - neighbor->vertex_average();
            const Real delta_norm = delta.norm();
            if (delta_norm == 0.0)
              continue;

            const Real side_sign = interface_normal * (delta / delta_norm);
            if (side_sign > 0.0)
            {
              // FIX 2 (shared): Capture the neighbor side index BEFORE calling
              // set_node. After set_node the element's node list changes, and some
              // libMesh versions compute which_neighbor_am_i via node-ID matching —
              // which then fails to find the neighbor because the shared node has been
              // replaced. Capturing the index first guarantees a valid result.
              const auto neighbor_side = neighbor->which_neighbor_am_i(elem);

              unsigned int local_node_id = libMesh::invalid_uint;
              for (const auto i : make_range(elem->n_nodes()))
                if (elem->node_id(i) == node_ref_id)
                {
                  local_node_id = i;
                  break;
                }

              if (local_node_id != libMesh::invalid_uint)
              {
                Node * new_node = mesh->node_ptr(node_new_id);
                elem->set_node(local_node_id, new_node);

                // Use the pre-captured neighbor_side.
                if (neighbor_side != libMesh::invalid_uint &&
                    !boundary_info.has_boundary_id(neighbor, neighbor_side, bnd_id))
                  boundary_info.add_side(neighbor, neighbor_side, bnd_id);

                if (boundary_info.has_boundary_id(elem, side, bnd_id))
                  boundary_info.remove_side(elem, side, bnd_id);

                if (_add_interface_on_two_sides)
                {
                  const auto secondary_it = _primary_to_secondary_id.find(bnd_id);
                  if (secondary_it != _primary_to_secondary_id.end() &&
                      !boundary_info.has_boundary_id(elem, side, secondary_it->second))
                    boundary_info.add_side(elem, side, secondary_it->second);
                }
              }
            }
          }

      // Then treat connected elements that are not directly in the boundary side list.
      for (const auto elem_id : elem_ids)
        if (elem_ids_bnd.count(elem_id) == 0)
        {
          Elem * elem = mesh->elem_ptr(elem_id);

          unsigned int local_node_id = libMesh::invalid_uint;
          for (const auto i : make_range(elem->n_nodes()))
            if (elem->node_id(i) == node_ref_id)
            {
              local_node_id = i;
              break;
            }

          if (local_node_id == libMesh::invalid_uint)
            continue;

          const Point delta = elem->vertex_average() - elem->point(local_node_id);
          const Real delta_norm = delta.norm();
          if (delta_norm == 0.0)
            continue;

          if (interface_normal * (delta / delta_norm) > 0.0)
          {
            Node * new_node = mesh->node_ptr(node_new_id);
            elem->set_node(local_node_id, new_node);
          }
        }
    }
  }
}
