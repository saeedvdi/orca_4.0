#!/usr/bin/env python3.14
"""Generate the Ye-Ghassemi input-deck property comparison report.

Run with the Python interpreter from the MOOSE environment because ``pyhit``
must match the Python version used to build MOOSE's HIT extension:

    PYTHONPATH=../moose/python \
      /home/geomechanics/miniforge/envs/moose/bin/python3.14 \
      scripts/generate_input_deck_property_comparison.py
"""

from __future__ import annotations

import html
import re
import sys
from collections import defaultdict
from pathlib import Path


SAMPLES = ("SWT1", "SWT2", "SWS3", "SWS4")
ID_PREFIX = {"SWT1": "T1", "SWT2": "T2", "SWS3": "S3", "SWS4": "S4"}
REPORT_NAME = "INPUT_DECK_MATERIAL_PROPERTY_COMPARISON_2026-08-18.md"
MATRIX_REPORT_NAME = "INPUT_DECK_MATERIAL_PROPERTY_MATRIX_2026-08-18.md"
GENERATED_DATE = "2026-08-19"
SUBSTITUTION = re.compile(r"\$\{([^{}]+)\}")


def load_pyhit(project_root: Path):
    """Load MOOSE's HIT parser, failing safely before importing a mismatched extension."""
    if sys.version_info[:2] != (3, 14):
        raise SystemExit(
            "This generator currently requires Python 3.14 from the MOOSE environment; "
            f"the active interpreter is {sys.version.split()[0]}."
        )
    moose_python = project_root.parent / "moose" / "python"
    if not moose_python.is_dir():
        raise SystemExit(f"MOOSE Python utilities not found at {moose_python}")
    sys.path.insert(0, str(moose_python))
    import pyhit  # pylint: disable=import-outside-toplevel

    return pyhit


def walk(node):
    yield node
    for child in node.children:
        yield from walk(child)


def value_text(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, float):
        return f"{value:.12g}"
    return str(value).replace("\n", " ").strip()


def resolve_value(value, globals_by_name: dict[str, object]) -> str:
    """Expand ordinary root-parameter substitutions without evaluating HIT expressions."""
    if not isinstance(value, str):
        return value_text(value)

    exact = SUBSTITUTION.fullmatch(value.strip())
    if exact and exact.group(1) in globals_by_name:
        return value_text(globals_by_name[exact.group(1)])

    def replace(match: re.Match[str]) -> str:
        body = match.group(1)
        if body in globals_by_name:
            return value_text(globals_by_name[body])
        if body.startswith("fparse "):
            expression = body[7:]
            for name in sorted(globals_by_name, key=len, reverse=True):
                expression = re.sub(
                    rf"\b{re.escape(name)}\b",
                    value_text(globals_by_name[name]),
                    expression,
                )
            return f"${{fparse {expression}}}"
        return match.group(0)

    return SUBSTITUTION.sub(replace, value).strip()


def code(value: str) -> str:
    escaped = html.escape(str(value), quote=False).replace("|", "&#124;")
    return f"<code>{escaped}</code>"


def compress_ids(ids: set[str], id_order: dict[str, tuple[str, int]]) -> str:
    by_prefix: dict[str, list[int]] = defaultdict(list)
    for file_id in sorted(ids, key=lambda item: id_order[item]):
        prefix, number = id_order[file_id]
        by_prefix[prefix].append(number)

    groups = []
    for sample in SAMPLES:
        prefix = ID_PREFIX[sample]
        numbers = sorted(by_prefix.get(prefix, []))
        if not numbers:
            continue
        ranges = []
        start = previous = numbers[0]
        for number in numbers[1:]:
            if number == previous + 1:
                previous = number
                continue
            ranges.append((start, previous))
            start = previous = number
        ranges.append((start, previous))
        groups.extend(
            f"{prefix}-{start:02d}" if start == end
            else f"{prefix}-{start:02d}–{prefix}-{end:02d}"
            for start, end in ranges
        )
    return ", ".join(groups)


def render_value_groups(
    groups: dict[str, set[str]], id_order: dict[str, tuple[str, int]]
) -> str:
    ordered = sorted(
        groups.items(),
        key=lambda item: (
            min((id_order[file_id] for file_id in item[1]), default=("", 0)),
            item[0],
        ),
    )
    return "<br>".join(
        f"{code(value)} — {compress_ids(file_ids, id_order)}"
        for value, file_ids in ordered
    )


def root_category(name: str) -> str:
    geometry = {
        "mesh_file", "sample_area", "sample_radius", "bulk_sin_theta", "bulk_cos_theta",
        "paper_flow_width_over_length", "mesh_flow_width_over_length",
        "paper_flow_width_over_length_sw_s3", "mesh_flow_width_over_length_sw_s3",
        "paper_flow_width_over_length_sw_s4", "mesh_flow_width_over_length_sw_s4",
    }
    bulk = {
        "youngs_modulus", "poissons_ratio", "strain_model", "initial_porosity",
        "matrix_permeability", "biot_coefficient",
    }
    fluid = {"fluid_bulk_modulus", "fluid_density_ref", "fluid_viscosity_ref"}
    loading_tokens = (
        "axial_", "confining_", "production_", "fault_pressure_", "initial_stress",
        "poro_", "relax_", "side_unload_",
    )
    numerical_tokens = (
        "penalty_", "tolerance", "max_plastic", "dissipation", "file_base",
        "compute_", "ml_per_",
    )
    fracture_tokens = (
        "bb_", "roughness", "cohesion", "friction", "dilation", "closure",
        "hydraulic_aperture", "aperture_scale", "retention", "self_propping",
        "slip_damage", "weakening", "normal_stiffness", "tangential_viscosity",
        "min_tau", "compressive_normal", "rate_and_state", "reversible_normal",
        "fault_thickness",
    )
    if name in geometry:
        return "Geometry, mesh, and flow geometry"
    if name in bulk:
        return "Bulk rock and poroelastic properties"
    if name in fluid:
        return "Fluid properties"
    if any(token in name for token in loading_tokens):
        return "Experimental loading and apparatus controls"
    if any(token in name for token in numerical_tokens):
        return "Numerical, conversion, and output controls"
    if any(token in name for token in fracture_tokens):
        return "Fracture/contact/hydraulic constitutive properties"
    return "Other root declarations"


def material_category(material_type: str) -> str:
    if material_type in {
        "OrcaMechMaterial", "OrcaTHMaterial", "OrcaBiotCoefficientMaterial",
        "OrcaGravityVectorMaterial",
    }:
        return "Bulk, poroelastic, fluid, and gravity materials"
    if "Permeability" in material_type or "Aperture" in material_type:
        return "Fracture aperture and permeability materials"
    if "BartonBandis" in material_type or "DilationRoughnessContact" in material_type:
        return "Fracture contact, strength, weakening, and rate materials"
    if material_type in {"OrcaCZMComputeDisplacementJump", "OrcaCZMInterfacePressure"}:
        return "Interface kinematics and pressure materials"
    return "Derived and output material properties"


def append_assignment_table(
    lines: list[str],
    rows: list[tuple[str, str, str, dict[str, set[str]], dict[str, set[str]], set[str]]],
    id_order: dict[str, tuple[str, int]],
    total_files: int,
) -> None:
    lines.extend([
        "| Property | Object path | Object type | Declared form(s) → input IDs | Effective value(s) → input IDs | Coverage |",
        "|---|---|---|---|---|---:|",
    ])
    for parameter, path, object_type, raw_groups, effective_groups, file_ids in rows:
        lines.append(
            f"| {code(parameter)} | {code(path)} | {code(object_type)} | "
            f"{render_value_groups(raw_groups, id_order)} | "
            f"{render_value_groups(effective_groups, id_order)} | "
            f"{len(file_ids)}/{total_files} |"
        )
    lines.append("")


def main() -> None:
    project_root = Path(__file__).resolve().parents[1]
    pyhit = load_pyhit(project_root)
    study_root = project_root / "Examples" / "YeGhasemmi2018"
    report_path = project_root / "doc" / "independent_analysis" / REPORT_NAME
    matrix_report_path = (
        project_root / "doc" / "independent_analysis" / MATRIX_REPORT_NAME
    )

    input_paths: list[Path] = []
    file_id_by_path: dict[Path, str] = {}
    id_order: dict[str, tuple[str, int]] = {}
    catalog: dict[str, list[tuple[str, Path]]] = defaultdict(list)
    for sample in SAMPLES:
        sample_paths = sorted((study_root / sample).glob("*.i"))
        for number, path in enumerate(sample_paths, start=1):
            file_id = f"{ID_PREFIX[sample]}-{number:02d}"
            input_paths.append(path)
            file_id_by_path[path] = file_id
            id_order[file_id] = (ID_PREFIX[sample], number)
            catalog[sample].append((file_id, path))

    root_groups: dict[str, dict[str, set[str]]] = defaultdict(lambda: defaultdict(set))
    block_records: dict[tuple[str, str, str, str], dict[str, object]] = {}
    root_assignment_count = 0
    block_assignment_count = 0
    material_assignment_count = 0

    for path in input_paths:
        file_id = file_id_by_path[path]
        root = pyhit.load(str(path))
        globals_by_name = dict(root.params())
        for name, value in globals_by_name.items():
            parsed_value = value_text(value)
            root_groups[name][parsed_value].add(file_id)
            root_assignment_count += 1

        for node in walk(root):
            if node is root:
                continue
            node_path = node.fullpath.lstrip("/")
            top_block = node_path.split("/", 1)[0]
            object_type = value_text(node.get("type", "(no type)"))
            for parameter, value in node.params():
                key = (top_block, node_path, object_type, parameter)
                record = block_records.setdefault(
                    key,
                    {
                        "raw": defaultdict(set),
                        "effective": defaultdict(set),
                        "files": set(),
                    },
                )
                raw = value_text(value)
                effective = resolve_value(value, globals_by_name)
                record["raw"][raw].add(file_id)
                record["effective"][effective].add(file_id)
                record["files"].add(file_id)
                block_assignment_count += 1
                if top_block == "Materials":
                    material_assignment_count += 1

    total_files = len(input_paths)
    all_ids = set(file_id_by_path.values())
    material_keys = [key for key in block_records if key[0] == "Materials"]
    other_keys = [key for key in block_records if key[0] != "Materials"]
    represented_root_assignments = sum(
        len(file_ids)
        for value_groups in root_groups.values()
        for file_ids in value_groups.values()
    )
    represented_block_assignments = sum(
        len(record["files"]) for record in block_records.values()
    )
    if represented_root_assignments != root_assignment_count:
        raise RuntimeError(
            "Root grouping lost or conflated assignments: "
            f"parsed={root_assignment_count}, represented={represented_root_assignments}"
        )
    if represented_block_assignments != block_assignment_count:
        raise RuntimeError(
            "Block grouping lost or conflated assignments: "
            f"parsed={block_assignment_count}, represented={represented_block_assignments}"
        )

    lines = [
        "# Ye–Ghassemi input-deck material-property and value comparison",
        "",
        "**Repository:** `orca_4.0`  ",
        f"**Generated:** {GENERATED_DATE}<br>",
        "**Scope:** every top-level `.i` file in `SWT1`, `SWT2`, `SWS3`, and `SWS4`  ",
        f"**Coverage:** {total_files} input decks; all parsed successfully; no `!include` directives are present<br>",
        "**Companion analysis:** `CONSOLIDATED_ANALYSIS_2026-08-18.md` and `TABLE2_ERROR_ACCURACY_RANKING.csv`",
        f"**Cross-file matrix summary:** `{MATRIX_REPORT_NAME}`",
        "",
        "## 1. How to read this report",
        "",
        "This is a complete assignment inventory, not only a hand-selected parameter table. It contains:",
        "",
        f"- {root_assignment_count:,} root/global declarations grouped into {len(root_groups)} property names;",
        f"- {material_assignment_count:,} assignments under `[Materials]`, grouped into {len(material_keys)} exact object-path/type/property rows;",
        f"- {block_assignment_count - material_assignment_count:,} assignments in every other block, grouped into {len(other_keys)} exact object-path/type/property rows.",
        "",
        "Comments and commented-out lines are not definitions and are excluded. Syntactically defined inactive objects are retained; their `active`/`inactive` controls also appear in the inventory. Root substitutions such as `${youngs_modulus}` are shown both as declared and after expansion. HIT/fparse expressions are expanded where possible but are not numerically evaluated.",
        "",
        "Values are reported in the form parsed by HIT. Dimensional values follow the units expected by their MOOSE/ORCA object (normally SI); configuration strings, names, flags, indices, and expressions are shown literally. Consult the relevant object definition before assigning a unit to an unfamiliar field.",
        "",
        f"The file-ID lists are exhaustive. If a row has coverage below {total_files}, files not listed for a value do not define that exact property/object path. Consecutive IDs are compressed as ranges.",
        "",
        "## 2. Input-file ID catalog",
        "",
    ]

    for sample in SAMPLES:
        lines.extend([
            f"### {sample}",
            "",
            "| ID | Input file |",
            "|---|---|",
        ])
        for file_id, path in catalog[sample]:
            lines.append(f"| {code(file_id)} | {code(path.relative_to(project_root))} |")
        lines.append("")

    lines.extend([
        "## 3. Root/global property declarations",
        "",
        "These are the named values at the top of each deck. They are the clearest cross-deck comparison because most material blocks consume them through substitutions. Categories are conservative semantic labels; they do not imply that every value was independently measured.",
        "",
    ])

    root_categories: dict[str, list[str]] = defaultdict(list)
    for name in root_groups:
        root_categories[root_category(name)].append(name)
    category_order = (
        "Bulk rock and poroelastic properties",
        "Fracture/contact/hydraulic constitutive properties",
        "Fluid properties",
        "Geometry, mesh, and flow geometry",
        "Experimental loading and apparatus controls",
        "Numerical, conversion, and output controls",
        "Other root declarations",
    )
    for category in category_order:
        names = sorted(root_categories.get(category, []))
        if not names:
            continue
        lines.extend([
            f"### {category}",
            "",
            "| Property | Declared value(s) → input IDs | Distinct values | Coverage |",
            "|---|---|---:|---:|",
        ])
        for name in names:
            file_ids = set().union(*root_groups[name].values())
            lines.append(
                f"| {code(name)} | {render_value_groups(root_groups[name], id_order)} | "
                f"{len(root_groups[name])} | {len(file_ids)}/{total_files} |"
            )
        lines.append("")

    lines.extend([
        "## 4. Every `[Materials]` assignment",
        "",
        "Rows are categorized by material role and sorted first by property name, as requested. The exact object path prevents similarly named properties in different material objects from being conflated.",
        "",
    ])

    material_rows_by_category: dict[str, list] = defaultdict(list)
    for key in material_keys:
        _, path, object_type, parameter = key
        record = block_records[key]
        material_rows_by_category[material_category(object_type)].append(
            (parameter, path, object_type, record["raw"], record["effective"], record["files"])
        )
    for category in (
        "Bulk, poroelastic, fluid, and gravity materials",
        "Fracture contact, strength, weakening, and rate materials",
        "Fracture aperture and permeability materials",
        "Interface kinematics and pressure materials",
        "Derived and output material properties",
    ):
        rows = sorted(material_rows_by_category.get(category, []), key=lambda row: (row[0], row[1], row[2]))
        if not rows:
            continue
        lines.extend([f"### {category}", ""])
        append_assignment_table(lines, rows, id_order, total_files)

    lines.extend([
        "## 5. Every non-material block assignment",
        "",
        "This section supplies the requested ‘any other value’ comparison. It includes mesh construction, variables, initial conditions, functions, kernels, interface kernels, boundary conditions, auxiliary output, postprocessors, executioner, preconditioning, and outputs. Values are grouped only when the exact object path and property name match.",
        "",
    ])
    other_rows_by_block: dict[str, list] = defaultdict(list)
    for key in other_keys:
        top_block, path, object_type, parameter = key
        record = block_records[key]
        other_rows_by_block[top_block].append(
            (parameter, path, object_type, record["raw"], record["effective"], record["files"])
        )
    preferred_blocks = (
        "GlobalParams", "Problem", "Mesh", "Variables", "ICs", "Functions", "Kernels",
        "InterfaceKernels", "BCs", "AuxVariables", "AuxKernels", "Postprocessors",
        "Preconditioning", "Executioner", "Outputs",
    )
    for top_block in (*preferred_blocks, *sorted(set(other_rows_by_block) - set(preferred_blocks))):
        rows = sorted(other_rows_by_block.get(top_block, []), key=lambda row: (row[0], row[1], row[2]))
        if not rows:
            continue
        lines.extend([f"### `{top_block}`", ""])
        append_assignment_table(lines, rows, id_order, total_files)

    lines.extend([
        "## 6. Properties to hold fixed for a non-rock-property improvement campaign",
        "",
        "A conservative interpretation of ‘rock-characteristic material properties’ should lock more than only `E` and `nu`. It should hold the following groups at the selected authoritative baseline unless an independently measured correction is available:",
        "",
        "| Locked group | Examples in these decks | Reason |",
        "|---|---|---|",
        "| Bulk elastic and porous matrix | `youngs_modulus`, `poissons_ratio`, `initial_porosity`, `matrix_permeability`, `biot_coefficient` | These define the specimen matrix and poroelastic response. The 96-series shows that Biot sensitivity is specimen-dependent. |",
        "| Fracture strength and surface character | `bb_jrc`, `bb_jcs`, cohesion, friction angles/coefficients, residual strengths, roughness states | These are the calibrated or measured fracture/rock characteristics. The existing path does not identify all of them independently. |",
        "| Contact and weakening response | normal stiffness/closure, weakening distances, viscosity, dilation, damage and self-propping terms | Although several are calibrated rather than directly measured, changing them would be a constitutive recalibration rather than a non-material correction. |",
        "| Hydraulic fracture state | initial/minimum/maximum aperture, aperture scale, compliance and retention terms | These control the physical flow/opening relation and should not be tuned indirectly to improve a score. |",
        "| Measured specimen geometry | radius, area, fracture plane/angle and dimensions | Correct documented geometry errors, but do not tune geometry against the response. |",
        "",
        "The production sets are calibrated sets, not collections of independently identified properties. In particular, cohesion and JRC have nearly collinear influence over this loading path. Locking both is the safest way to avoid exchanging one compensating error for another.",
        "",
        "### Result-informed material selections through the 100-series",
        "",
        "The 99/100-series cases are controlled material-property recalibrations, not non-material corrections. Their status is therefore recorded separately from the locked 93-series validation controls:",
        "",
        "| Sample | Selected result | Material-property implication | Status |",
        "|---|---|---|---|",
        "| SWT1 | `99_01` | `maximum_closure = 50.00e-6 m`, with its seating offset recomputed | strongest candidate; all five scored observables improve |",
        "| SWT2 | `100_04` nominally | `aperture_scale = 0.0177`; `0.0175–0.0177` is unresolved | nominal minimum is 2.131869%; `100_03` differs by only 0.003869 points, below reproducibility |",
        "| SWS3 | `99_06` | `residual_cohesion = 1.30e6 Pa` | provisional tradeoff; re-gate preload before promotion |",
        "| SWS4 | `93_07` | no 99-series material change accepted | both tested scalar changes worsen the mean |",
        "",
        "For SWT2, the refinement changes only the hydraulic aperture scale. Relative to `99_04` (`0.0170`), `100_04` lowers flow nRMSE from 4.892625% to 4.335516% while the four mechanical nRMSE values each move by at most 0.015 points. Its mean falls from 2.236611% to 2.131869%. The gain is resolved relative to the 93-series control but the two 100-series bracket values are not distinguishable from each other.",
        "",
        "## 7. Can accuracy improve without changing those properties?",
        "",
        "**Yes, but the likely gain is targeted rather than a large uniform reduction.** The authoritative 93-series mean nRMSE values are 4.44% (SWT1), 2.43% (SWT2), 4.57% (SWS3), and 6.14% (SWS4). Cross-machine repeats establish an approximately 0.08 percentage-point floor, so differences below about 0.1 point should not be treated as a real ranking improvement.",
        "",
        "| Priority | Sample(s) | Non-rock-property action | Evidence and expected effect |",
        "|---:|---|---|---|",
        "| 1 | SWS3 | Re-gate the axial preload on the corrected 123.40 mm mesh while leaving strength, roughness, closure, aperture and permeability parameters unchanged. Treat `axial_pres_initial`/the preload boundary state as apparatus/loading setup, not a strength knob. | The remaining shear-stress residual contains an approximately constant stage-1 offset introduced when the mesh length changed but the preload was retained. This is the clearest justified route to a genuine score improvement. |",
        "| 2 | All | Re-audit exact injection-pressure transition times, ramp shapes, production pressure, confining pressure and Table-2 sampling times against the measured driver. Only correct provenance errors; do not tune the imposed history to the response. | Earlier schedule errors shifted transitions by 48–155 s and propagated into flow, slip and unloading. Correct driver timing can improve history agreement without changing material physics. Current production schedules already include major corrections, so remaining gains may be small. |",
        "| 3 | All, especially incomplete 96/97 runs | Capture stdout/stderr, reduce event-window timestep caps, preserve checkpoints, and diagnose nonlinear/active-set termination before changing physics. Use two-step smoke runs after material-block changes. | Four `alpha_f = 1` probes and three cyclic runs are incomplete. Numerical robustness can make their conclusions complete, but must not be misreported as a lower constitutive error until full Table-2 coverage exists. |",
        "| 4 | All | Re-run mesh/source-node audits and require exact interface-node placement rather than relying only on `use_closest_node`. Complete the missing post-slip mesh comparisons. | Historical apparent failures were caused by stale coordinates and geometry. SWS4's completed mesh pair changes the score by only 0.22 point, suggesting limited but nonzero discretisation sensitivity. |",
        "| 5 | All | Score the independent mesh-geometry flow channel and retain the five-column Table-2 metric; keep derived aperture/permeability out of the headline average. | This removes dependence on the fitted paper `W/L` route and improves the defensibility and diagnostic accuracy of `Q`. It may change the reported score, but it does not change physical predictions. |",
        "| 6 | SWS4 | Localise the stage-4 ramp residual using measured ramp/apparatus response. If a new hypothesis is allowed, test a separately verified pressure/path-dependent coupling or larger-scale mechanism; do not use another scalar cohesion/JRC/`D_c` adjustment. | SWS4 has roughly the correct final slip but distributes it over the wrong pressure windows. Rate/state healing and one-dimensional `D_c` brackets already failed. A static material shift cannot generate the missing shape without damaging adjacent stages. |",
        "| 7 | SWT1/SWT2 | Preserve the 93-series baseline as the validation control and keep accepted material refinements explicitly labelled as recalibrations. | The SWT2 100-series lowers the nominal score to 2.13% by changing `aperture_scale`; it is useful calibration evidence but does not qualify as a non-material improvement. |",
        "",
        "### Expected outcome by sample",
        "",
        "- **SWT1:** modest improvement may be possible in flow and normal displacement through driver/geometry/reporting checks, but no existing non-material probe demonstrates a large gain.",
        "- **SWT2:** the hydraulic-only 100-series reaches 2.13%, but the `0.0175` and `0.0177` cases are indistinguishable at campaign precision. Further fine spacing on this scalar is not justified.",
        "- **SWS3:** the corrected-mesh preload re-gate is the best concrete non-material opportunity. It should be tested as a minimal-diff deck with a preregistered prediction for the shear-stress offset.",
        "- **SWS4:** numerical and driver audits remain worthwhile, but a large physical improvement is unlikely without a new path-dependent mechanism. The existing rate/state and static-strength directions should not be repeated without new evidence.",
        "",
        "### Changes that can improve reported accuracy but not model physics",
        "",
        "Stress-frame corrections, exact point samplers, displacement zeroing, corrected digitisation, and avoiding algebraically duplicated validation columns can materially change the reported error without changing the solution. They are necessary, but should be described as measurement/reporting corrections rather than constitutive improvements.",
        "",
        "## 8. Recommendation",
        "",
        "Use each specimen's authoritative 93-series deck as the locked-property control. Treat `99_01` and nominal `100_04` as separately labelled material-calibration candidates, with the SWT2 bracket uncertainty stated explicitly. Build only minimal-diff non-material variants, beginning with the SWS3 preload re-gate. For each variant, record the expected affected observable and load window before running, require complete stage coverage, and reject changes that improve one channel by degrading already-correct neighbouring stages. Do not rank partial runs with complete runs.",
        "",
        "For SWS4, treat the remaining stage-4 residual as a model-form/path-dependence question, not as permission to alter the rock/fracture constants. For SWT2, the 2.13% refined score should now be followed by mesh, machine, driver, and scoring robustness rather than a finer aperture-scale sweep.",
        "",
        "## 9. Reproduction",
        "",
        "```bash",
        "PYTHONPATH=../moose/python \\",
        "  /home/geomechanics/miniforge/envs/moose/bin/python3.14 \\",
        "  scripts/generate_input_deck_property_comparison.py",
        "```",
        "",
        "The generator parses the HIT syntax directly with MOOSE `pyhit`, checks every deck, expands ordinary root substitutions, and rewrites this report deterministically.",
    ])

    matrix_lines = [
        "# Ye–Ghassemi material-property cross-file matrix",
        "",
        f"**Generated:** {GENERATED_DATE}<br>",
        f"**Scope:** all {total_files} `.i` files in SWT1, SWT2, SWS3, and SWS4<br>",
        f"**Detailed audit:** `{REPORT_NAME}`",
        "",
        "## How to read the matrix",
        "",
        "Each sample has one table in the requested orientation: input files are columns and `[Materials]` model/property names are rows. Values supplied through root `${...}` substitutions are resolved in the cells. `—` means that the exact material-object/property combination is not defined in that input file.",
        "",
        "The `Material model / property` label uses `material type :: object path :: property`. This keeps identically named properties from different material objects separate. Full filenames are retained as column headings.",
        "",
    ]

    for sample in SAMPLES:
        sample_catalog = catalog[sample]
        sample_ids = [file_id for file_id, _ in sample_catalog]
        sample_material_keys = sorted(
            (
                key for key in material_keys
                if block_records[key]["files"].intersection(sample_ids)
            ),
            key=lambda key: (key[2], key[1], key[3]),
        )

        matrix_lines.extend([
            f"## {sample}",
            "",
            f"{len(sample_catalog)} input files. Values are shown in parsed MOOSE/ORCA units, normally SI.",
            "",
        ])
        header = ["Sample name", "Material Model Name / Property Name"] + [
            path.name for _, path in sample_catalog
        ]
        matrix_lines.append("| " + " | ".join(code(item) for item in header) + " |")
        matrix_lines.append("|" + "---|" * len(header))

        for key in sample_material_keys:
            _, object_path, object_type, parameter = key
            record = block_records[key]
            value_by_file = {
                file_id: value
                for value, file_ids in record["effective"].items()
                for file_id in file_ids
            }
            label = f"{object_type} :: {object_path} :: {parameter}"
            cells = [sample, label]
            cells.extend(value_by_file.get(file_id, "—") for file_id in sample_ids)
            matrix_lines.append(
                "| " + " | ".join(
                    code(cell) if cell != "—" else "—" for cell in cells
                ) + " |"
            )
        matrix_lines.append("")

    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    matrix_report_path.write_text(
        "\n".join(matrix_lines) + "\n", encoding="utf-8"
    )
    if set(file_id_by_path.values()) != all_ids:
        raise RuntimeError("Internal file-ID coverage mismatch")
    print(f"Wrote {report_path}")
    print(f"Wrote {matrix_report_path}")
    print(
        f"Parsed {total_files} decks: {root_assignment_count} root assignments, "
        f"{material_assignment_count} material assignments, "
        f"{block_assignment_count - material_assignment_count} other assignments."
    )


if __name__ == "__main__":
    main()
