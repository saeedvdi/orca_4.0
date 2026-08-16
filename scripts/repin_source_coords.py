#!/usr/bin/env python3
"""Pin each mesh-3 deck's injection/production coordinate to a real fracture node.

Adapted from meshes/snap_source_coords.py for the orca_4.0 sample-directory layout,
with two changes:

  * it acts ONLY on decks matching a name filter (default '*_mesh3.i'), so the
    mesh-5 parents -- including decks currently running -- are never rewritten;
  * it also syncs the postprocessor `point = '...'` entries that duplicate the
    source coordinate, which the original script left behind.

Why this must run after any mesh change: `ExtraNodesetGenerator` with
`use_closest_node = true` searches the WHOLE mesh and runs BEFORE the fault split,
so a coordinate merely NEAR the fracture can snap to a BULK node. No error is
raised; injection just happens inside the matrix and fluid reaches the fracture
only through the 5e-19 m2 matrix permeability. On one measured mesh the nearest
bulk node was 1.734 mm from the ideal point and the nearest fracture node
1.775 mm -- 41 um decided it, and two production decks lost their injection point.

Method: keep the deck's x and y (the borehole inset is deliberate and sample
specific), recompute z from the mesh's own least-squares fracture plane, then pin
to the nearest node that is actually a member of `fracture_interface`.

    python repin_source_coords.py [--apply] [--glob '*_mesh3.i']
"""
import re
import sys
from pathlib import Path

import numpy as np
from netCDF4 import Dataset

ROOT = Path("/media/geomechanics/Data4TB/projects/orca_4.0/Examples/YeGhasemmi2018")
SAMPLES = ["SWS3", "SWS4", "SWT1", "SWT2"]


def mesh_nodes(path):
    ds = Dataset(str(path), "r")
    names = [b"".join([c for c in row if c]).decode() for row in ds.variables["ns_names"][:]]
    if "fracture_interface" not in names:
        ds.close()
        raise KeyError("%s has no fracture_interface nodeset; found %s" % (path.name, names))
    frac = np.asarray(ds.variables["node_ns%d" % (names.index("fracture_interface") + 1)][:]) - 1
    xyz = np.column_stack([np.asarray(ds.variables[k][:]) for k in ("coordx", "coordy", "coordz")])
    ds.close()
    X, Z = xyz[frac][:, 0], xyz[frac][:, 2]
    slope, icept = np.linalg.lstsq(np.column_stack([X, np.ones_like(X)]), Z, rcond=None)[0]
    return xyz, frac, float(slope), float(icept)


def fmt(v):
    return "%.10g" % v


def main():
    apply_ = "--apply" in sys.argv[1:]
    pattern = "*_mesh3.i"
    if "--glob" in sys.argv:
        pattern = sys.argv[sys.argv.index("--glob") + 1]

    cache, edits, regate, bad = {}, [], [], []

    for sample in SAMPLES:
        d = ROOT / sample
        for deck in sorted(d.glob(pattern)):
            text = deck.read_text()
            m = re.search(r"^mesh_file\s*=\s*(\S+)", text, re.M)
            if not m:
                continue
            mesh = d / m.group(1)
            if not mesh.is_file():
                bad.append("%s: mesh %s not found" % (deck.name, m.group(1)))
                continue
            if mesh not in cache:
                cache[mesh] = mesh_nodes(mesh)
            xyz, frac, slope, icept = cache[mesh]
            frac_set = set(frac.tolist())

            new_text, rows = text, []
            for name in ("source_in", "source_out"):
                blk = re.search(r"(\[%s\].*?\[\])" % name, text, re.S)
                if not blk:
                    continue
                cm = re.search(r"coord\s*=\s*'([^']+)'", blk.group(1))
                if not cm:
                    continue
                old = cm.group(1)
                c = np.asarray([float(v) for v in old.split()])

                # what this coordinate would select on THIS mesh, as written
                winner = int(np.argmin(np.linalg.norm(xyz - c, axis=1)))
                was_ok = winner in frac_set

                ideal = np.array([c[0], c[1], slope * c[0] + icept])
                dist = np.linalg.norm(xyz - ideal, axis=1)
                d_frac = np.full(len(dist), np.inf)
                d_frac[frac] = dist[frac]
                target = int(np.argmin(d_frac))

                new = " ".join(fmt(v) for v in xyz[target])
                move_mm = float(np.linalg.norm(xyz[target] - c)) * 1000.0
                rows.append((name, old, new, move_mm, was_ok, winner == target))

                if new != old:
                    patched = blk.group(1).replace("'%s'" % old, "'%s'" % new, 1)
                    new_text = new_text.replace(blk.group(1), patched, 1)
                    # keep duplicated postprocessor sample points on the same node
                    new_text = new_text.replace("point = '%s'" % old, "point = '%s'" % new)

            if not rows:
                continue
            print("%-58s %s" % (deck.name[:58], mesh.name))
            for name, old, new, move_mm, was_ok, same in rows:
                if old == new:
                    note = "already pinned"
                elif was_ok and same:
                    note = "pin only (same node, no physics change)"
                elif not was_ok:
                    note = "*** WAS MISSING THE FRACTURE -- RE-GATE ***"
                else:
                    note = "*** DIFFERENT NODE -- RE-GATE ***"
                print("    %-11s %-30s -> %-30s %7.3f mm  %s"
                      % (name, old, new, move_mm, note))
                if not (was_ok and same):
                    regate.append("%s / %s (%.3f mm)" % (deck.name, name, move_mm))
            if apply_ and new_text != text:
                deck.write_text(new_text)
                edits.append(deck.name)

    print()
    if bad:
        print("MESH MISSING:")
        for x in bad:
            print("   ", x)
        return 1
    if not apply_:
        print("Dry run. Re-run with --apply to write the decks.")
        return 0
    print("Updated %d decks." % len(edits))
    if regate:
        print("\n%d source points changed NODE. Calibration tuned on the mesh-5 node does"
              "\nnot carry over to these; treat them as a fresh gate:" % len(regate))
        for x in regate:
            print("   ", x)
    return 0


if __name__ == "__main__":
    sys.exit(main())
