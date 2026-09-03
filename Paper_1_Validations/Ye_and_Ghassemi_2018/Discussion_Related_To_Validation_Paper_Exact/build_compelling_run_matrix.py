#!/usr/bin/env python3
"""Build the targeted paper-strengthening simulation matrix.

The generated decks inherit the already selected and validated parent decks.
Only one declared axis is changed in each case.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path("/home/geomechanics/Documents/ChatGPT/Orca_4.0")
BASE = ROOT / "proposed_inputs"
OUT = BASE / "paper_compelling_20260902"


@dataclass(frozen=True)
class Case:
    stem: str
    specimen: str
    parent: str
    purpose: str
    replacements: tuple[tuple[str, str], ...] = ()
    regex_replacements: tuple[tuple[str, str], ...] = ()
    walltime: str = "12:00:00"


CASES = (
    Case(
        "112_01_swt1_dt0375_ppfix",
        "SWT1",
        "111_01_swt1_floor1nm_control_ppfix",
        "Time-step robustness: halve the SW-T1 maximum step from 0.75 to 0.375 s.",
        regex_replacements=(
            (r"(\[adaptive\][\s\S]*?\n\s*dt\s*=\s*)0\.75", r"\g<1>0.375"),
            (r"(?m)^(\s*dtmax\s*=\s*)0\.75(\s*)$", r"\g<1>0.375\g<2>"),
        ),
    ),
    Case(
        "112_02_swt1_eta200gpa_s_ppfix",
        "SWT1",
        "111_01_swt1_floor1nm_control_ppfix",
        "Regularization robustness: halve SW-T1 tangential viscosity from 4e11 to 2e11 Pa s/m.",
        replacements=(("tangential_viscosity = 400000000000", "tangential_viscosity = 200000000000"),),
    ),
    Case(
        "112_03_sw4_dt075_ppfix",
        "SWS4",
        "109_01_sw4_floor1nm_g028_ppfix",
        "Time-step robustness: halve the SW-S4 maximum step from 1.5 to 0.75 s.",
        regex_replacements=(
            (r"(\[TimeStepper\][\s\S]*?\n\s*dt\s*=\s*)1\.5", r"\g<1>0.75"),
            (r"(?m)^(\s*dtmax\s*=\s*)1\.5(\s*)$", r"\g<1>0.75\g<2>"),
        ),
    ),
    Case(
        "112_04_sw4_mesh3_ppfix",
        "SWS4",
        "109_01_sw4_floor1nm_g028_ppfix",
        "Mesh robustness: replace the selected nominal size-5 mesh with the existing theta-30 size-3 mesh.",
        replacements=(("mesh/ye2018_sw_s4_theta30_size5_mesh.e", "mesh/ye2018_sw_s4_theta30_size3_mesh.e"),),
        walltime="18:00:00",
    ),
    Case(
        "113_01_sw3_dscale0304_ppfix",
        "SWS3",
        "110_01_sw3_floor1nm_g040_ppfix",
        "Identifiability: decrease the retained-dilation scale by 20 percent.",
        regex_replacements=((r"(?m)^(dilation_scale\s*=\s*)0\.038(\s+.*)?$", r"\g<1>0.0304\g<2>"),),
    ),
    Case(
        "113_02_sw3_dscale0456_ppfix",
        "SWS3",
        "110_01_sw3_floor1nm_g040_ppfix",
        "Identifiability: increase the retained-dilation scale by 20 percent.",
        regex_replacements=((r"(?m)^(dilation_scale\s*=\s*)0\.038(\s+.*)?$", r"\g<1>0.0456\g<2>"),),
    ),
    Case(
        "113_03_sw3_gouge032_ppfix",
        "SWS3",
        "110_01_sw3_floor1nm_g040_ppfix",
        "Identifiability: decrease maximum gouge-related aperture loss by 20 percent.",
        regex_replacements=((r"(?m)^(slip_damage_scale\s*=\s*)0\.40e-6(\s+.*)?$", r"\g<1>0.32e-6\g<2>"),),
    ),
    Case(
        "113_04_sw3_gouge048_ppfix",
        "SWS3",
        "110_01_sw3_floor1nm_g040_ppfix",
        "Identifiability: increase maximum gouge-related aperture loss by 20 percent.",
        regex_replacements=((r"(?m)^(slip_damage_scale\s*=\s*)0\.40e-6(\s+.*)?$", r"\g<1>0.48e-6\g<2>"),),
    ),
    Case(
        "113_05_sw3_closure096_ppfix",
        "SWS3",
        "110_01_sw3_floor1nm_g040_ppfix",
        "Identifiability: decrease the hydraulic normal-closure amplitude by 20 percent.",
        regex_replacements=((r"(?m)^(bb_max_aperture_closure\s*=\s*)1\.2e-6(\s+.*)?$", r"\g<1>0.96e-6\g<2>"),),
    ),
    Case(
        "113_06_sw3_closure144_ppfix",
        "SWS3",
        "110_01_sw3_floor1nm_g040_ppfix",
        "Identifiability: increase the hydraulic normal-closure amplitude by 20 percent.",
        regex_replacements=((r"(?m)^(bb_max_aperture_closure\s*=\s*)1\.2e-6(\s+.*)?$", r"\g<1>1.44e-6\g<2>"),),
    ),
    Case(
        "114_01_swt2_ascale01416_ppfix",
        "SWT2",
        "111_03_swt2_floor1nm_control_ppfix",
        "Loading-only tensile selection: decrease the kinematic aperture scale by 20 percent.",
        regex_replacements=((r"(?m)^(aperture_scale\s*=\s*)0\.0177(\s+.*)?$", r"\g<1>0.01416\g<2>"),),
    ),
    Case(
        "114_02_swt2_ascale02124_ppfix",
        "SWT2",
        "111_03_swt2_floor1nm_control_ppfix",
        "Loading-only tensile selection: increase the kinematic aperture scale by 20 percent.",
        regex_replacements=((r"(?m)^(aperture_scale\s*=\s*)0\.0177(\s+.*)?$", r"\g<1>0.02124\g<2>"),),
    ),
    Case(
        "115_01_swt1_extended_depressurization_ppfix",
        "SWT1",
        "111_01_swt1_floor1nm_control_ppfix",
        "Elastic-closure diagnostic: hold the final post-slip state, then reduce the inlet-to-outlet pressure difference to 50 and 15 percent of its original final value.",
        regex_replacements=(
            (
                r"(?m)^(\s*x = '[^']*)'$",
                r"\g<1> 3700 3900 4100 4300 4500'",
            ),
            (
                r"(?m)^(\s*y = '[^']*)'$",
                r"\g<1> 8e6 6.5e6 6.5e6 5.45e6 5.45e6'",
            ),
            (
                r"(?m)^\s*end_time\s*=.*$",
                "  end_time = 4500  # original cycle plus normalized 50% and 15% pressure-difference holds",
            ),
        ),
        walltime="18:00:00",
    ),
    Case(
        "115_02_swt2_extended_depressurization_ppfix",
        "SWT2",
        "111_03_swt2_floor1nm_control_ppfix",
        "Elastic-closure diagnostic: hold the final post-slip state, then reduce the inlet-to-outlet pressure difference to 50 and 15 percent of its original final value.",
        regex_replacements=(
            (r"(?m)^(\s*x = '[^']*)'$", r"\g<1> 3052.5 3252.5 3452.5 3652.5 3852.5'"),
            (r"(?m)^(\s*y = '[^']*)'$", r"\g<1> 8e6 6.5e6 6.5e6 5.45e6 5.45e6'"),
            (
                r"(?m)^\s*end_time\s*=.*$",
                "  end_time = 3852.5  # original cycle plus normalized 50% and 15% pressure-difference holds",
            ),
        ),
        walltime="18:00:00",
    ),
    Case(
        "115_03_sws3_extended_depressurization_ppfix",
        "SWS3",
        "110_01_sw3_floor1nm_g040_ppfix",
        "Elastic-closure diagnostic: hold the final post-slip state, then reduce the inlet-to-outlet pressure difference to 50 and 15 percent of its original final value.",
        regex_replacements=(
            (r"(?m)^(\s*x = '[^']*)'$", r"\g<1> 5002.4 5202.4 5402.4 5602.4 5802.4'"),
            (
                r"(?m)^(\s*y = '[^']*)'$",
                r"\g<1> 7882927 6441463.5 6441463.5 5432439.05 5432439.05'",
            ),
            (
                r"(?m)^\s*end_time\s*=.*$",
                "  end_time = 5802.4  # original cycle plus normalized 50% and 15% pressure-difference holds",
            ),
        ),
        walltime="18:00:00",
    ),
    Case(
        "115_04_sws4_extended_depressurization_ppfix",
        "SWS4",
        "109_01_sw4_floor1nm_g028_ppfix",
        "Elastic-closure diagnostic: hold the final post-slip state, then reduce the inlet-to-outlet pressure difference to 50 and 15 percent of its original final value.",
        regex_replacements=(
            (r"(?m)^(\s*x = '[^']*)'$", r"\g<1> 3700 3900 4100 4300 4500'"),
            (
                r"(?m)^(\s*y = '[^']*)'$",
                r"\g<1> 7970497.57057629 6485248.785288145 6485248.785288145 5445574.6355864435 5445574.6355864435'",
            ),
            (
                r"(?m)^\s*end_time\s*=.*$",
                "  end_time = 4500  # original cycle plus normalized 50% and 15% pressure-difference holds",
            ),
        ),
        walltime="18:00:00",
    ),
)

BATCHES = (
    ("112_01_swt1_dt0375_ppfix", "112_02_swt1_eta200gpa_s_ppfix", "112_03_sw4_dt075_ppfix"),
    ("112_04_sw4_mesh3_ppfix", "113_01_sw3_dscale0304_ppfix", "113_02_sw3_dscale0456_ppfix"),
    ("113_03_sw3_gouge032_ppfix", "113_04_sw3_gouge048_ppfix", "113_05_sw3_closure096_ppfix"),
    ("113_06_sw3_closure144_ppfix", "114_01_swt2_ascale01416_ppfix", "114_02_swt2_ascale02124_ppfix"),
    (
        "115_01_swt1_extended_depressurization_ppfix",
        "115_02_swt2_extended_depressurization_ppfix",
        "115_03_sws3_extended_depressurization_ppfix",
    ),
    ("115_04_sws4_extended_depressurization_ppfix",),
)


def replace_once(text: str, old: str, new: str, *, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f"{label}: expected one literal match for {old!r}, found {count}")
    return text.replace(old, new, 1)


def regex_replace_once(text: str, pattern: str, replacement: str, *, label: str) -> str:
    updated, count = re.subn(pattern, replacement, text, count=1)
    if count != 1:
        raise RuntimeError(f"{label}: expected one regex match for {pattern!r}, found {count}")
    return updated


def output_paths(text: str, stem: str) -> str:
    exodus = f"proposed_inputs/paper_compelling_20260902/exodus/{stem}"
    csv = f"proposed_inputs/paper_compelling_20260902/csv/{stem}"
    text, ex_count = re.subn(
        r"(?m)^exodus_file_base\s*=.*$", f"exodus_file_base = {exodus}", text, count=1
    )
    text, csv_count = re.subn(
        r"(?m)^csv_file_base\s*=.*$", f"csv_file_base    = {csv}", text, count=1
    )
    if ex_count != 1 or csv_count != 1:
        raise RuntimeError(f"{stem}: could not set unique CSV/Exodus output bases")
    return text


def slurm_script(case: Case) -> str:
    return f"""#!/bin/bash

#SBATCH --job-name={case.stem}
#SBATCH --chdir=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/Examples/YeGhasemmi2018/{case.specimen}
#SBATCH --account=def-biaoli66
#SBATCH --time={case.walltime}
#SBATCH --nodes=1
#SBATCH --ntasks=8
#SBATCH --cpus-per-task=1
#SBATCH --mem=24G
#SBATCH --output=proposed_inputs/paper_compelling_20260902/logs/{case.stem}_%j.out
#SBATCH --error=proposed_inputs/paper_compelling_20260902/logs/{case.stem}_%j.err

set -euo pipefail

PROJECT_ROOT=/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0
CASE_STEM={case.stem}
CASE_DIR=${{PROJECT_ROOT}}/Examples/YeGhasemmi2018/{case.specimen}

cd "${{CASE_DIR}}"
unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p proposed_inputs/paper_compelling_20260902/{{csv,exodus,checkpoint,logs}}

srun --mpi=pmi2 -n 8 "${{PROJECT_ROOT}}/orca-opt" -i "proposed_inputs/${{CASE_STEM}}.i" \
  Outputs/chk/enable=false
"""


def local_batch_script(batch: tuple[str, ...]) -> str:
    by_stem = {case.stem: case for case in CASES}
    entries = "\n".join(f'  "{by_stem[stem].specimen}:{stem}"' for stem in batch)
    return f"""#!/bin/bash

set -euo pipefail

PROJECT_ROOT=/media/geomechanics/Data4TB/projects/orca_4.0
MOOSE_ENV=/home/geomechanics/miniforge/envs/moose
MPIEXEC=/home/geomechanics/miniforge/envs/moose/bin/mpiexec.hydra
ORCA=${{PROJECT_ROOT}}/orca-opt
RUN_REL=proposed_inputs/paper_compelling_20260902

# Parsed-function JIT compilation invokes the linker during a run.  Preserve the
# MOOSE environment even when this launcher is started non-interactively.
export PATH="${{MOOSE_ENV}}/bin:${{PATH}}"
export LD_LIBRARY_PATH="${{MOOSE_ENV}}/lib:${{LD_LIBRARY_PATH:-}}"
export LIBRARY_PATH="${{MOOSE_ENV}}/lib:${{LIBRARY_PATH:-}}"

cases=(
{entries}
)

pids=()
labels=()
for entry in "${{cases[@]}}"; do
  specimen=${{entry%%:*}}
  case_stem=${{entry#*:}}
  case_dir=${{PROJECT_ROOT}}/Examples/YeGhasemmi2018/${{specimen}}
  mkdir -p "${{case_dir}}/${{RUN_REL}}/csv" "${{case_dir}}/${{RUN_REL}}/exodus" "${{case_dir}}/${{RUN_REL}}/logs"
  (
    cd "${{case_dir}}"
    "${{MPIEXEC}}" -n 8 "${{ORCA}}" -i "proposed_inputs/${{case_stem}}.i" \\
      Outputs/chk/enable=false \\
      >"${{RUN_REL}}/logs/${{case_stem}}.out" \\
      2>"${{RUN_REL}}/logs/${{case_stem}}.err"
  ) &
  pids+=("$!")
  labels+=("${{specimen}}/${{case_stem}}")
done

status=0
for index in "${{!pids[@]}}"; do
  if ! wait "${{pids[$index]}}"; then
    status=1
    echo "${{labels[$index]}} failed; inspect its log." >&2
  fi
done

exit "${{status}}"
"""


def submit_batch_script(batch: tuple[str, ...]) -> str:
    by_stem = {case.stem: case for case in CASES}
    lines = ["#!/bin/bash", "", "set -euo pipefail", ""]
    for stem in batch:
        case = by_stem[stem]
        case_dir = (
            "/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0/"
            f"Examples/YeGhasemmi2018/{case.specimen}/proposed_inputs"
        )
        lines.append(f'sbatch "{case_dir}/{stem}.sh"')
    return "\n".join(lines) + "\n"


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for case in CASES:
        parent_path = BASE / f"{case.parent}.i"
        text = parent_path.read_text()
        text = text.replace(case.parent, case.stem)
        for old, new in case.replacements:
            text = replace_once(text, old, new, label=case.stem)
        for pattern, replacement in case.regex_replacements:
            text = regex_replace_once(text, pattern, replacement, label=case.stem)
        text = output_paths(text, case.stem)
        text = (
            f"# PAPER-COMPELLING MATRIX 2026-09-02\n"
            f"# Purpose: {case.purpose}\n"
            f"# Parent deck: {case.parent}.i; every unlisted parameter is unchanged.\n\n"
            + text
        )

        specimen_dir = OUT / case.specimen
        specimen_dir.mkdir(parents=True, exist_ok=True)
        (specimen_dir / f"{case.stem}.i").write_text(text)
        sh_path = specimen_dir / f"{case.stem}.sh"
        sh_path.write_text(slurm_script(case))
        sh_path.chmod(0o755)

    manifest = OUT / "case_manifest.tsv"
    manifest.write_text(
        "stem\tspecimen\tparent\tpurpose\n"
        + "\n".join(
            f"{case.stem}\t{case.specimen}\t{case.parent}\t{case.purpose}" for case in CASES
        )
        + "\n"
    )

    for index, batch in enumerate(BATCHES, start=1):
        local_path = OUT / f"run_compelling_batch_{index:02d}_local.sh"
        local_path.write_text(local_batch_script(batch))
        local_path.chmod(0o755)
        submit_path = OUT / f"submit_compelling_batch_{index:02d}_hpc.sh"
        submit_path.write_text(submit_batch_script(batch))
        submit_path.chmod(0o755)


if __name__ == "__main__":
    main()
