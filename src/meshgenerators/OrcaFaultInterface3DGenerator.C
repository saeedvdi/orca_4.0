#include "OrcaFaultInterface3DGenerator.h"

#include "MooseMeshUtils.h"

#include "libmesh/elem.h"
#include "libmesh/node.h"
#include "libmesh/partitioner.h"

#include <algorithm>
#include <functional>
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

  // FIX 6 (2026-09-03): ids handed out here must be remembered.
  //
  // Allocating a secondary sideset only calls boundary_info.sideset_name(id), which
  // registers a NAME. The id itself does not enter boundary_info.get_boundary_ids() until
  // a side is actually assigned to it, which happens much later. So on the SECOND sideset
  // this lambda saw the first secondary id as still free and handed out the same id again:
  // every secondary sideset collapsed into one boundary.
  //
  // The symptom was remote from the cause. The generator itself succeeded; the mesh then
  // failed in libMesh's find_neighbors with "Periodic boundary neighbor not found"
  // (periodic_boundaries.C:107), because add_disjoint_neighbor_boundary_pairs could not
  // pair a primary face against a secondary boundary that now held both sides of both
  // fractures. It only ever appeared with TWO OR MORE sidesets AND
  // add_interface_on_two_sides = true -- a single fracture, which is all the Kalantar2025
  // decks use, allocates once and is unaffected.
  std::set<boundary_id_type> reserved_boundary_ids;
  auto find_free_boundary_id = [this, &boundary_info, &reserved_boundary_ids]()
      -> boundary_id_type {
    const auto & current_boundary_ids = boundary_info.get_boundary_ids();
    for (boundary_id_type free_id = 1; free_id < std::numeric_limits<boundary_id_type>::max();
         ++free_id)
      if (current_boundary_ids.count(free_id) == 0 && reserved_boundary_ids.count(free_id) == 0)
      {
        reserved_boundary_ids.insert(free_id);
        return free_id;
      }
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
  // any node repointing occurs. This is used in splitInterfaceNodes to make the
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
  const auto bnd_node_ids = getSidesetNodes(bnd_elems, mesh_sideset_ids, *mesh);
  splitInterfaceNodes(bnd_node_ids, node_to_elem_map, bnd_elems, mesh);

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

std::set<std::pair<dof_id_type, dof_id_type>>
OrcaFaultInterface3DGenerator::exteriorEdges(const libMesh::MeshBase & mesh)
{
  std::set<std::pair<dof_id_type, dof_id_type>> exterior;
  for (const auto & elem : mesh.active_element_ptr_range())
    for (const auto s : make_range(elem->n_sides()))
      if (!elem->neighbor_ptr(s))
      {
        const auto side_elem = elem->build_side_ptr(s);
        for (const auto e : make_range(side_elem->n_sides()))
        {
          const auto edge_local_nodes = side_elem->nodes_on_side(e);
          if (edge_local_nodes.size() < 2)
            continue;
          dof_id_type n0 = side_elem->node_id(edge_local_nodes.front());
          dof_id_type n1 = side_elem->node_id(edge_local_nodes.back());
          if (n0 == n1)
            continue;
          if (n1 < n0)
            std::swap(n0, n1);
          exterior.insert(std::make_pair(n0, n1));
        }
      }
  return exterior;
}

OrcaFaultInterface3DGenerator::BoundaryNodeSetMap
OrcaFaultInterface3DGenerator::getSidesetNodes(
    const std::vector<BndElementData> & bnd_elems,
    const std::set<boundary_id_type> & mesh_sideset_ids,
    const libMesh::MeshBase & mesh) const
{
  using EdgeKey = std::pair<dof_id_type, dof_id_type>;

  BoundaryNodeSetMap bnd_node_ids;
  std::map<boundary_id_type, std::map<EdgeKey, unsigned int>> edge_face_count;
  std::map<boundary_id_type, std::map<EdgeKey, std::set<dof_id_type>>> edge_nodes;

  // FIX 7: which (element, side) pairs each sideset actually carries.
  //
  // The interface faces below are de-duplicated so each is processed once. The old test,
  // `if (elem->id() < neighbor->id()) continue;`, assumed the sideset holds BOTH sides of
  // every face and keeps the higher-id copy. That is true of a sideset built from a
  // nodeset, but NOT of one from SideSetsBetweenSubdomainsGenerator, which is ONE-SIDED:
  // every face whose owner had the lower id was dropped, and with the usual element
  // numbering that is all of them. The failure was silent -- the sidesets were still
  // created with the right side counts, the interface kernels still assembled, the solve
  // still converged, and the fracture came out welded with w_max exactly 0.
  std::map<boundary_id_type, std::set<std::pair<dof_id_type, unsigned int>>> sideset_sides;
  for (const auto & bnd_elem : bnd_elems)
    sideset_sides[bnd_elem.bnd_id].insert(
        std::make_pair(bnd_elem.elem->id(), static_cast<unsigned int>(bnd_elem.side)));

  // ---------------------------------------------------------------------------------
  // PASS 1: collect the candidate nodes and the edge topology of every interface.
  // ---------------------------------------------------------------------------------
  for (const auto sideset_id : mesh_sideset_ids)
  {
    auto & face_count = edge_face_count[sideset_id];
    auto & nodes_on_edge = edge_nodes[sideset_id];

    for (const auto & bnd_elem : bnd_elems)
      if (sideset_id == bnd_elem.bnd_id)
      {
        Elem * elem = bnd_elem.elem;
        const auto side = bnd_elem.side;
        Elem * neighbor = elem->neighbor_ptr(side);

        // This generator targets interior interfaces. Skip external sides.
        if (!neighbor)
          continue;

        // Process each interface face once. Skip this copy only when the partner copy is
        // also in the sideset and will be processed instead; on a one-sided sideset this
        // copy is the only one there is.
        const auto neighbor_side = neighbor->which_neighbor_am_i(elem);
        const bool partner_in_sideset =
            neighbor_side != libMesh::invalid_uint &&
            sideset_sides[sideset_id].count(std::make_pair(neighbor->id(), neighbor_side));
        if (partner_in_sideset && elem->id() < neighbor->id())
          continue;

        std::unique_ptr<Elem> side_elem = elem->build_side_ptr(side);
        if (!side_elem)
          continue;

        for (const auto n : make_range(side_elem->n_nodes()))
          bnd_node_ids[sideset_id].insert(side_elem->node_id(n));

        // Edge topology of the interface surface: an edge shared by two interface faces is
        // interior to it, an edge touched once bounds it.
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
          ++face_count[edge_key];

          auto & edge_node_set = nodes_on_edge[edge_key];
          for (const auto local_edge_node : edge_local_nodes)
            edge_node_set.insert(side_elem->node_id(local_edge_node));
        }
      }
  }

  if (!(_split_only_interior_nodes || _preserve_front_nodes))
    return bnd_node_ids;

  // ---------------------------------------------------------------------------------
  // PASS 2: classify the bounding edges and weld the ones that are true crack fronts.
  //
  // FIX 5: this is the criterion the old FIX 3 comment described but did not implement.
  //
  // History. The ORIGINAL code treated every edge with face_count == 1 as crack front.
  // That is wrong for a through-going fracture: where it daylights on the sample surface
  // those edges also have face_count == 1, and welding them clamps the fracture at the
  // specimen boundary. FIX 3 replaced it with a "does this node have a neighbour across
  // the interface" test -- but that set was built by scanning the same faces, with the
  // same filters, that built the candidate set, so the two were equal by construction and
  // the removal was a no-op. Both options were therefore INERT: setting them false gave a
  // mesh with exactly the same node count as setting them true.
  //
  // FIX 8 adds the third case. An edge that bounds one fracture may lie ON another one --
  // a T-junction, where a branch terminates against a second fracture. That is not a crack
  // front either: the material there IS already separated, and the two flanks have to be
  // free to slide apart along the fracture they meet. Welding it pins the aperture and the
  // slip to zero exactly at the junction, which is where they peak.
  //
  //     face_count == 1, edge lies IN an exterior face       -> daylighting -> split
  //     face_count == 1, edge is an edge of another interface -> junction    -> split
  //     face_count == 1, otherwise                            -> crack front -> weld
  //     face_count >  2                                       -> junction    -> weld
  //
  // FIX 9 makes both tests EDGE-based rather than node-based. In a plane-strain model one
  // element thick, EVERY node lies on the z-min or z-max face, so a node test calls every
  // crack tip "exterior" and splits it -- which is exactly what it did, giving 2 node
  // copies at each tip where there must be 1. The tip EDGE runs through the thickness at
  // an interior (x, y) and is not an edge of any exterior face, so the edge test is
  // correct at any thickness.
  //
  // For a fracture that cuts the whole specimen -- every Kalantar2025 OG-SH/OG-SC/OG-T
  // geometry -- every bounding edge lies on the cylindrical surface, so nothing is removed
  // and the generated mesh is IDENTICAL to the one the old code produced. Verified by node
  // count and by MD5 of the coordinate and connectivity arrays; see
  // Examples/Validaitons/benchmarks/mesh_generator_check/README.md.
  const std::set<EdgeKey> exterior_edges = exteriorEdges(mesh);

  for (const auto sideset_id : mesh_sideset_ids)
  {
    // Edges belonging to any OTHER interface in this request.
    std::set<EdgeKey> other_interface_edges;
    for (const auto & [other_id, other_edges] : edge_face_count)
      if (other_id != sideset_id)
        for (const auto & [edge_key, unused_count] : other_edges)
        {
          libmesh_ignore(unused_count);
          other_interface_edges.insert(edge_key);
        }

    const auto & face_count = edge_face_count[sideset_id];
    const auto & nodes_on_edge = edge_nodes[sideset_id];
    std::set<dof_id_type> nodes_to_remove;

    for (const auto & [edge_key, count] : face_count)
    {
      const auto edge_nodes_it = nodes_on_edge.find(edge_key);
      if (edge_nodes_it == nodes_on_edge.end())
        continue;

      if (count == 1)
      {
        // Daylighting on the specimen surface, or terminating against another fracture:
        // either way the faces must be free to separate.
        if (exterior_edges.count(edge_key) || other_interface_edges.count(edge_key))
          continue;

        for (const auto node_id : edge_nodes_it->second)
          nodes_to_remove.insert(node_id);
      }
      else if (count > 2 && _split_only_interior_nodes)
      {
        // A non-manifold edge WITHIN this one interface: branches of the same fracture
        // meeting. Junctions between two SEPARATE sidesets are handled by the
        // on_other_interface test above, since edge_face_count is per sideset.
        for (const auto node_id : edge_nodes_it->second)
          nodes_to_remove.insert(node_id);
      }
    }

    for (const auto node_id : nodes_to_remove)
      bnd_node_ids[sideset_id].erase(node_id);
  }

  return bnd_node_ids;
}

void
OrcaFaultInterface3DGenerator::splitInterfaceNodes(const BoundaryNodeSetMap & bnd_node_ids,
                                                   NodeToElemMap & node_to_elem_map,
                                                   const std::vector<BndElementData> & bnd_elems,
                                                   std::unique_ptr<MeshBase> & mesh) const
{
  auto & boundary_info = mesh->get_boundary_info();
  using FaceKey = std::pair<dof_id_type, unsigned int>;

  // -----------------------------------------------------------------------------------
  // Every interface face, from BOTH sides, across all requested sidesets. Two elements
  // that touch across one of these are on opposite sides of a fracture.
  // -----------------------------------------------------------------------------------
  std::set<FaceKey> interface_faces;
  for (const auto & bnd_elem : bnd_elems)
  {
    Elem * elem = bnd_elem.elem;
    interface_faces.insert(std::make_pair(elem->id(), static_cast<unsigned int>(bnd_elem.side)));
    Elem * neighbor = elem->neighbor_ptr(bnd_elem.side);
    if (!neighbor)
      continue;
    const auto neighbor_side = neighbor->which_neighbor_am_i(elem);
    if (neighbor_side != libMesh::invalid_uint)
      interface_faces.insert(std::make_pair(neighbor->id(), neighbor_side));
  }

  // -----------------------------------------------------------------------------------
  // PASS 1: move each sideset onto one side of its interface, and populate the secondary.
  //
  // Done BEFORE any node is repointed, so which_neighbor_am_i is asked only of intact
  // connectivity. The old code did this inside the node loop and had to capture the
  // neighbour index before calling set_node to dodge exactly that hazard (FIX 2).
  //
  // The convention is unchanged: the primary sideset ends up on the side the interface
  // normal points AWAY from, the secondary on the side it points towards.
  // -----------------------------------------------------------------------------------
  for (const auto & bnd_elem : bnd_elems)
  {
    const auto bnd_id = bnd_elem.bnd_id;
    Elem * elem = bnd_elem.elem;
    const auto side = bnd_elem.side;
    Elem * neighbor = elem->neighbor_ptr(side);
    if (!neighbor)
      continue;

    const auto normal_it = _interface_normals.find(bnd_id);
    const RealVectorValue interface_normal =
        (normal_it != _interface_normals.end()) ? normal_it->second : RealVectorValue(0, 0, 1);

    const Point delta = elem->vertex_average() - neighbor->vertex_average();
    const Real delta_norm = delta.norm();
    if (delta_norm == 0.0)
      continue;
    if (interface_normal * (delta / delta_norm) <= 0.0)
      continue;

    const auto neighbor_side = neighbor->which_neighbor_am_i(elem);
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

  // -----------------------------------------------------------------------------------
  // PASS 2: split each interface node into one copy per connected piece of material.
  // -----------------------------------------------------------------------------------
  std::set<dof_id_type> nodes_to_split;
  for (const auto & [bnd_id, node_ids] : bnd_node_ids)
  {
    libmesh_ignore(bnd_id);
    nodes_to_split.insert(node_ids.begin(), node_ids.end());
  }

  for (const auto node_ref_id : nodes_to_split)
  {
    const Node * node = mesh->node_ptr(node_ref_id);
    if (!node)
      continue;

    const auto node_to_elem_it = node_to_elem_map.find(node_ref_id);
    if (node_to_elem_it == node_to_elem_map.end())
      continue;
    const std::vector<dof_id_type> & elem_ids = node_to_elem_it->second;
    if (elem_ids.size() < 2)
      continue;

    // Union-find over the elements meeting at this node.
    std::map<dof_id_type, dof_id_type> parent;
    for (const auto id : elem_ids)
      parent[id] = id;
    std::function<dof_id_type(dof_id_type)> find = [&](dof_id_type a) {
      while (parent[a] != a)
        a = parent[a] = parent[parent[a]];
      return a;
    };
    auto unite = [&](dof_id_type a, dof_id_type b) {
      const auto ra = find(a), rb = find(b);
      if (ra != rb)
        parent[std::max(ra, rb)] = std::min(ra, rb);
    };

    const std::set<dof_id_type> elem_id_set(elem_ids.begin(), elem_ids.end());
    for (const auto id : elem_ids)
    {
      Elem * elem = mesh->elem_ptr(id);
      if (!elem)
        continue;
      for (const auto s : make_range(elem->n_sides()))
      {
        Elem * neighbor = elem->neighbor_ptr(s);
        if (!neighbor || !elem_id_set.count(neighbor->id()))
          continue;
        // A fracture face separates the two pieces.
        if (interface_faces.count(std::make_pair(id, static_cast<unsigned int>(s))))
          continue;
        // Only faces touching THIS node say anything about connectivity at it.
        bool side_has_node = false;
        for (const auto local_side_node : elem->nodes_on_side(s))
          if (elem->node_id(local_side_node) == node_ref_id)
          {
            side_has_node = true;
            break;
          }
        if (!side_has_node)
          continue;
        unite(id, neighbor->id());
      }
    }

    // Group by component, ordered so the result does not depend on map iteration order.
    std::map<dof_id_type, std::vector<dof_id_type>> components;
    for (const auto id : elem_ids)
      components[find(id)].push_back(id);
    if (components.size() < 2)
      continue;

    // The lowest-rooted component keeps the original node; every other gets a copy.
    bool first = true;
    for (const auto & [root, ids] : components)
    {
      libmesh_ignore(root);
      if (first)
      {
        first = false;
        continue;
      }

      std::unique_ptr<Node> new_node = Node::build(*node, Node::invalid_id);
      new_node->processor_id() = node->processor_id();
      Node * added_node = mesh->add_node(std::move(new_node));

      // Keep nodeset membership consistent on duplicated nodes.
      std::vector<boundary_id_type> node_boundary_ids;
      boundary_info.boundary_ids(node, node_boundary_ids);
      boundary_info.add_node(added_node, node_boundary_ids);

      for (const auto id : ids)
      {
        Elem * elem = mesh->elem_ptr(id);
        if (!elem)
          continue;
        for (const auto i : make_range(elem->n_nodes()))
          if (elem->node_id(i) == node_ref_id)
          {
            elem->set_node(i, added_node);
            break;
          }
      }
    }
  }
}
