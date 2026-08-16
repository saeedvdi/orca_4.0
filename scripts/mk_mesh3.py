#!/usr/bin/env python3
"""Generate the mesh-size-3 variant of every kernel_SV deck in orca_4.0.

For each <base>_kernel_SV*.i produce <base>_kernel_SV*_mesh3.i carrying:
  * mesh_file repointed to the sample's size-3 mesh (~10x the elements),
  * *_file_base repointed to the new deck name,
  * a dated provenance header.

Source coordinates are NOT touched here -- they are pinned to mesh-5 nodes and
must be re-pinned against the size-3 mesh by repin_source_coords.py, which is a
separate, checkable step (see the standing source-node rule: ExtraNodesetGenerator
can snap injection to a bulk node with no error).

The mesh-5 parents are never modified.
"""
import os
import re

ROOT = "/media/geomechanics/Data4TB/projects/orca_4.0/Examples/YeGhasemmi2018"
DATE = "2026-08-15"

MESH3 = {
    "SWS4": ("ye2018_sw_s4_size5_mesh.e", "ye2018_sw_s4_size3_mesh.e"),
    "SWS3": ("sw3_mesh_size5.e", "sw3_mesh_size3.e"),
    "SWT1": ("ye2018_sw_T1_mesh_size_5.e", "ye2018_sw_T1_mesh_size_3.e"),
    "SWT2": ("ye2018_sw_T2_mesh_size_5.e", "ye2018_sw_T2_mesh_size_3.e"),
}

HEADER = """# ==============================================================================
# {name}
# GENERATED {date} from {parent}.i -- do not hand-edit; regenerate instead.
#
# Change applied on {date}:
#   mesh_file: {old} -> {new}
#     size 3 is the FINER mesh: {e5:,} -> {e3:,} elements ({ratio:.1f}x).
#
#   The solver is a DIRECT one (-pc_type lu, MUMPS). Factorisation cost and
#   memory grow much faster than the element count, so this deck is an HPC
#   deck, not a local one -- see doc/TODO.md section H.
#
#   Source coordinates are re-pinned against this mesh by
#   scratchpad/repin_source_coords.py; they are NOT inherited blindly from the
#   mesh-5 parent, because ExtraNodesetGenerator searches the whole mesh and
#   runs before the fault split, so a coordinate that is merely near the
#   fracture can snap to a BULK node with no error at all.
#
# The parent deck {parent}.i is left untouched.
# ==============================================================================
"""

SH = """#!/bin/bash

#SBATCH --job-name={name}
#SBATCH --account=def-biaoli66
#SBATCH --time=48:00:00
#SBATCH --nodes=1
#SBATCH --ntasks=32
#SBATCH --cpus-per-task=1
#SBATCH --mem=180G
#SBATCH --output=logs/{name}_%j.out
#SBATCH --error=logs/{name}_%j.err

cd {hpc}/Examples/YeGhasemmi2018/{sample}

# Alliance injects SLURM_MEM_PER_CPU; --mem sets SLURM_MEM_PER_NODE. Clear both.
unset SLURM_MEM_PER_NODE SLURM_MEM_PER_CPU SLURM_MEM_PER_GPU
mkdir -p logs results_csv results_exodus results_checkpoint

srun --mpi=pmi2 -n 32 {hpc}/orca-opt -i {name}.i
"""
HPC = "/home/saeedvdi/links/projects/def-biaoli66/saeedvdi/projects/orca_4.0"

# element counts, measured from the Exodus files
ELEMS = {"SWS4": (8640, 88504), "SWS3": (10368, 100048),
         "SWT1": (10752, 117232), "SWT2": (10752, 117232)}


def strip_generated_header(lines):
    if lines and lines[0].startswith("# ====") and "GENERATED" in "".join(lines[:6]):
        for i in range(1, len(lines)):
            if lines[i].startswith("# ===="):
                return lines[i + 1:]
    return lines


def main():
    made = []
    for sample, (m5, m3) in MESH3.items():
        d = os.path.join(ROOT, sample)
        if not os.path.isfile(os.path.join(d, "mesh", m3)):
            print("  SKIP %s: mesh/%s not present" % (sample, m3))
            continue
        bases = sorted(f[:-2] for f in os.listdir(d)
                       if f.endswith(".i") and "_kernel_SV" in f and not f.endswith("_mesh3.i"))
        for b in bases:
            name = b + "_mesh3"
            src, dst = os.path.join(d, b + ".i"), os.path.join(d, name + ".i")
            lines = strip_generated_header(open(src).readlines())

            hit = False
            for i, l in enumerate(lines):
                mm = re.match(r"^(mesh_file\s*=\s*)(\S+)(.*)$", l)
                if mm:
                    lines[i] = "%smesh/%s%s\n" % (mm.group(1), m3, mm.group(3))
                    hit = True
                    break
            if not hit:
                print("  WARN %s: no mesh_file line" % b)
                continue

            pat = re.compile(r"^(\s*(?:exodus|csv|checkpoint)_file_base\s*=\s*)(\S+)(.*)$")
            for i, l in enumerate(lines):
                mm = pat.match(l)
                if mm:
                    kind = mm.group(2).split("/")[0]
                    lines[i] = "%s%s/%s%s\n" % (mm.group(1), kind, name, mm.group(3))

            e5, e3 = ELEMS[sample]
            hdr = HEADER.format(name=name, date=DATE, parent=b, old=m5, new=m3,
                                e5=e5, e3=e3, ratio=e3 / e5)
            open(dst, "w").writelines([hdr] + lines)
            open(os.path.join(d, name + ".sh"), "w").write(
                SH.format(name=name, sample=sample, hpc=HPC))
            made.append("%s/%s.i" % (sample, name))

    print("created %d mesh3 decks" % len(made))
    for p in made:
        print("  " + p)


if __name__ == "__main__":
    main()
