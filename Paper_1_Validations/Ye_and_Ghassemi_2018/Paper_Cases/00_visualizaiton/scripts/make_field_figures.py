#!/usr/bin/env pvpython
"""Regenerate the Exodus field figures for the Ye & Ghassemi validation paper.

Run with pvpython (ParaView's python), which supplies the Exodus reader:

    pvpython scripts/make_field_figures.py                 # all specimens, default stages
    pvpython scripts/make_field_figures.py --stage peak    # single-stage figure
    pvpython scripts/make_field_figures.py --specimens SWT2 SWS3 SWS4
    pvpython scripts/make_field_figures.py --allow-inplane # opt in to u_x/u_y (see WARNING)

Design notes
------------
Data are EXTRACTED with ParaView and PLOTTED with matplotlib. Driving a 3-D
ParaView camera reproducibly is fragile; extracting a slice to numpy and drawing
it in matplotlib gives a true vector PDF, exact control over scales, and a
figure that regenerates identically on any machine.

Three rows are produced per figure:

  1. axial displacement u_z on the longitudinal plane through both boreholes;
  2. hydraulic aperture on the fracture plane;
  3. fracture Darcy speed on the fracture plane (the fluid-flow panel).

Rows 2 and 3 live on the ``fracture_surface`` block; row 1 uses the bulk blocks
only, because the displacement variables are block-restricted to the bulk.

WARNING -- in-plane displacement
--------------------------------
u_x and u_y in the current Exodus output are not physical. Measured at the last
step of the archived BB runs, max |u_xy| reaches 4.4% of the specimen radius for
SW-T1, 2.7% for SW-T2, 8.1% for SW-S4 and 2723% (688 mm on a 25 mm radius) for
SW-S3, and the field varies in proportion to radius, which is the signature of a
uniform radial scaling rather than a solution. u_z is sound: it matches the
axial shortening implied by inverting the paper's own d_n/d_s reduction. This
script therefore plots u_z only. --allow-inplane exists so the check can be
repeated after the output is fixed; it prints the same diagnostic either way.
"""

import argparse, os, sys
import numpy as np

try:
    from paraview.simple import ExodusIIReader, MergeBlocks, Slice
    from paraview import servermanager as sm
    from paraview.numpy_support import vtk_to_numpy
except ImportError:                                            # pragma: no cover
    sys.exit("run this with pvpython, not python3")

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.font_manager import findfont, FontProperties


def apply_agu_style():
    """The single controlled style shared by every manuscript figure.

    Mirrors apply_agu_style() in the standalone_figure_exports plotters so that
    figures produced here match the rest of the paper in font, text sizes,
    line weights and embedded-font type. Times is preferred, with fallbacks,
    because the AGU template sets Times for body text.
    """
    fam = "DejaVu Serif"
    for cand in ("Times New Roman", "Nimbus Roman", "Liberation Serif",
                 "TeX Gyre Termes", "FreeSerif", "DejaVu Serif"):
        try:
            if cand.lower().replace(" ", "") in findfont(
                    FontProperties(family=cand)).lower().replace("-", ""):
                fam = cand
                break
        except Exception:
            continue
    plt.rcParams.update({
        "font.family": fam,
        "font.size": 7.0,
        "axes.titlesize": 7.4,
        "axes.labelsize": 6.9,
        "xtick.labelsize": 6.0,
        "ytick.labelsize": 6.0,
        "legend.fontsize": 6.5,
        "mathtext.fontset": "stix",
        "figure.dpi": 600,
        "savefig.dpi": 600,
        "axes.linewidth": 0.65,
        "lines.linewidth": 1.15,
        "pdf.fonttype": 42,
        "ps.fonttype": 42,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
    })
from matplotlib.tri import Triangulation
from matplotlib.colors import Normalize
import matplotlib.cm as cm

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.environ.get(
    "ORCA_ROOT", "/media/geomechanics/Data4TB/projects/orca_4.0")
MAIN = os.path.join(
    ROOT, "Paper_1_Validations/Ye_and_Ghassemi_2018/Paper_Cases/01_Main_Validation")

SPECIMENS = ["SWT1", "SWT2", "SWS3", "SWS4"]
LABEL = {"SWT1": "SW-T1", "SWT2": "SW-T2", "SWS3": "SW-S3", "SWS4": "SW-S4"}
STEM = "{s}_OrcaBartonBandisContactTractionFastADHardening"

# Specimens known to need a rerun before their panel is trustworthy. Their
# column is drawn as a labelled placeholder so the figure keeps its layout.
PLACEHOLDER = {"SWT1": "rerun pending"}

# Borehole coordinates (m) from the mesh journals; both lie on y = 0, which is
# also perpendicular to the fracture strike, so the slice shows true dip.
SLICE_ORIGIN, SLICE_NORMAL = (0.0, 0.0, 0.0), (0.0, 1.0, 0.0)

# The tensile and saw-cut families differ by up to an order of magnitude in
# every field, so a single colour scale flattens the saw cuts. Scales are shared
# WITHIN each family and stated per family, matching the convention used by the
# paper's stage-comparison figure.
SCALE_GROUPS = (("SWT1", "SWT2"), ("SWS3", "SWS4"))


def exodus_path(spec):
    stem = STEM.format(s=spec)
    return os.path.join(MAIN, spec, "results", stem, stem + ".e")


def open_reader(path, point_vars, elem_vars, blocks):
    r = ExodusIIReader(FileName=[path])
    if point_vars:
        r.PointVariables = point_vars
    if elem_vars:
        r.ElementVariables = elem_vars
    r.ApplyDisplacements = 0
    r.UpdatePipeline()
    avail = list(r.ElementBlocks.Available)
    keep = [b for b in blocks if b in avail]
    if not keep:
        raise RuntimeError("none of %s in %s" % (blocks, avail))
    r.ElementBlocks = keep
    r.UpdatePipeline()
    return r, list(r.TimestepValues or [])


def pick_stages(path):
    """Return (t_initial, t_peak, t_final) using mean pore pressure to find peak."""
    r, ts = open_reader(path, ["pore_pressure"], [], ["top_block", "bottom_block"])
    mg = MergeBlocks(Input=r)
    best, best_t = -1.0, ts[-1]
    for t in ts:
        mg.UpdatePipeline(t)
        arr = sm.Fetch(mg).GetPointData().GetArray("pore_pressure")
        if arr is None:
            continue
        m = float(np.mean(vtk_to_numpy(arr)))
        if m > best:
            best, best_t = m, t
    return ts[0], best_t, ts[-1]


def bulk_slice(path, t):
    """u_z on the y = 0 plane, one triangulation per bulk block (keeps the jump)."""
    r, ts = open_reader(path, ["disp_"], [], ["top_block", "bottom_block"])
    t = min(ts, key=lambda v: abs(v - t))
    out = []
    for blk in ("top_block", "bottom_block"):
        rr, _ = open_reader(path, ["disp_"], [], [blk])
        sl = Slice(Input=MergeBlocks(Input=rr))
        sl.SliceType = "Plane"
        sl.SliceType.Origin, sl.SliceType.Normal = list(SLICE_ORIGIN), list(SLICE_NORMAL)
        sl.UpdatePipeline(t)
        d = sm.Fetch(sl)
        if d.GetNumberOfPoints() == 0:
            continue
        xyz = vtk_to_numpy(d.GetPoints().GetData())
        u = vtk_to_numpy(d.GetPointData().GetArray("disp_"))
        out.append((xyz, u, triangles(d)))
    return out, t


def fracture_field(path, name, t):
    """Cell field on the fracture plane, returned in in-plane coordinates."""
    r, ts = open_reader(path, [], [name], ["fracture_surface"])
    t = min(ts, key=lambda v: abs(v - t))
    from paraview.simple import CellDatatoPointData
    c2p = CellDatatoPointData(Input=MergeBlocks(Input=r))
    c2p.UpdatePipeline(t)
    d = sm.Fetch(c2p)
    if d.GetNumberOfPoints() == 0:
        raise RuntimeError("empty fracture_surface in %s" % path)
    xyz = vtk_to_numpy(d.GetPoints().GetData())
    arr = d.GetPointData().GetArray(name)
    if arr is None:
        raise RuntimeError("%s not found on fracture_surface" % name)
    v = vtk_to_numpy(arr)
    if v.ndim > 1:                       # vector field -> magnitude
        v = np.linalg.norm(v, axis=1)
    # in-plane basis from the point cloud itself, so any dip angle works
    c = xyz.mean(0)
    _, _, vt = np.linalg.svd(xyz - c, full_matrices=False)
    e1, e2 = vt[0], vt[1]
    uv = np.column_stack([(xyz - c) @ e1, (xyz - c) @ e2])
    return uv, v, triangles(d), t


def triangles(d):
    tri = []
    for i in range(d.GetNumberOfCells()):
        c = d.GetCell(i)
        ids = [c.GetPointId(j) for j in range(c.GetNumberOfPoints())]
        if len(ids) == 3:
            tri.append(ids)
        elif len(ids) == 4:
            tri += [[ids[0], ids[1], ids[2]], [ids[0], ids[2], ids[3]]]
    return np.asarray(tri, dtype=np.int64)


def inplane_report(path, t):
    """Print the u_x/u_y plausibility check; returns max |u_xy| in mm."""
    r, ts = open_reader(path, ["disp_"], [], ["top_block", "bottom_block"])
    mg = MergeBlocks(Input=r)
    mg.UpdatePipeline(min(ts, key=lambda v: abs(v - t)))
    d = sm.Fetch(mg)
    u = vtk_to_numpy(d.GetPointData().GetArray("disp_")) * 1e3
    xyz = vtk_to_numpy(d.GetPoints().GetData()) * 1e3
    rad = float(np.hypot(xyz[:, 0], xyz[:, 1]).max())
    mx = float(np.hypot(u[:, 0], u[:, 1]).max())
    flag = "IMPLAUSIBLE" if mx > 0.02 * rad else "ok"
    print("      in-plane check: max|u_xy| = %.4f mm = %.1f%% of radius  [%s]"
          % (mx, 100 * mx / rad, flag))
    return mx


def panel(ax, coords, vals, tri, norm, cmap, blocks=None):
    if blocks:
        for xy, v, tr in blocks:
            ax.tricontourf(Triangulation(xy[:, 0], xy[:, 1], tr), v,
                           levels=np.linspace(norm.vmin, norm.vmax, 24),
                           norm=norm, cmap=cmap, extend="both")
    else:
        ax.tricontourf(Triangulation(coords[:, 0], coords[:, 1], tri), vals,
                       levels=np.linspace(norm.vmin, norm.vmax, 24),
                       norm=norm, cmap=cmap, extend="both")
    ax.set_aspect("equal")
    ax.tick_params(length=2, pad=1.5)
    for s in ax.spines.values():
        s.set_linewidth(0.5)


def placeholder(ax, text, xlim=(0, 120), ylim=(-25, 25)):
    ax.set_xlim(*xlim); ax.set_ylim(*ylim)
    ax.set_aspect("equal")
    ax.text(0.5, 0.5, text, transform=ax.transAxes, ha="center", va="center",
            fontsize=7, color="0.35",
            bbox=dict(fc="0.94", ec="0.7", lw=0.6, pad=4))
    ax.set_xticks([]); ax.set_yticks([])
    for s in ax.spines.values():
        s.set_linewidth(0.5); s.set_color("0.7")


ROWS = [("axial displacement ($\\mu$m)", "cividis"),
        ("hydraulic aperture ($\\mu$m)", "viridis"),
        ("fracture Darcy speed (mm s$^{-1}$)", "magma")]


def build(specimens, stage, out, allow_inplane):
    apply_agu_style()
    data, missing = {}, []
    for s in specimens:
        p = exodus_path(s)
        if s in PLACEHOLDER or not os.path.isfile(p):
            missing.append(s)
            print("  %-6s placeholder (%s)" % (s, PLACEHOLDER.get(s, "file not found")))
            continue
        print("  %-6s %s" % (s, p))
        t0, tp, tf = pick_stages(p)
        t = {"initial": t0, "peak": tp, "final": tf}[stage]
        blocks, t_used = bulk_slice(p, t)
        uz = [(xy[:, [2, 0]] * 1e3, u[:, 2] * 1e6, tr) for xy, u, tr in blocks]
        ah_xy, ah, ah_tri, _ = fracture_field(p, "aperture_hydraulic", t)
        fv_xy, fv, fv_tri, _ = fracture_field(p, "fracture_darcy_vel_", t)
        inplane_report(p, t)
        if allow_inplane:
            print("      --allow-inplane set, but u_x/u_y remain unplotted by design")
        data[s] = dict(uz=uz, ah=(ah_xy * 1e3, ah * 1e6, ah_tri),
                       fv=(fv_xy * 1e3, fv * 1e3, fv_tri), t=t_used)

    if not data:
        sys.exit("no usable Exodus files found")

    def rng(key, members, idx=1):
        vals = []
        for s in members:
            if s not in data:
                continue
            v = data[s][key]
            vals += [b[idx] for b in v] if key == "uz" else [v[idx]]
        if not vals:
            return None
        allv = np.concatenate([np.asarray(x).ravel() for x in vals])
        lo, hi = float(np.nanmin(allv)), float(np.nanmax(allv))
        if lo == hi:
            hi = lo + 1e-12
        return Normalize(lo, hi)

    # norms[row][specimen] -> the Normalize shared by that specimen's family
    norms = []
    for key in ("uz", "ah", "fv"):
        per = {}
        for grp in SCALE_GROUPS:
            nz = rng(key, grp)
            for s in grp:
                per[s] = nz
        norms.append(per)
    n = len(specimens)
    fig, axes = plt.subplots(3, n, figsize=(2.15 * n + 0.6, 5.2))
    plt.subplots_adjust(left=0.082, right=0.938, top=0.93, bottom=0.075,
                        wspace=0.50, hspace=0.28)
    if n == 1:
        axes = axes.reshape(3, 1)

    for j, s in enumerate(specimens):
        axes[0][j].set_title(LABEL[s], pad=4)
        if s not in data:
            for i in range(3):
                placeholder(axes[i][j], PLACEHOLDER.get(s, "no data"))
            continue
        panel(axes[0][j], None, None, None, norms[0][s], ROWS[0][1], blocks=data[s]["uz"])
        for i, key in ((1, "ah"), (2, "fv")):
            xy, v, tr = data[s][key]
            panel(axes[i][j], xy, v, tr, norms[i][s], ROWS[i][1])
        axes[0][j].set_xlabel("axial (mm)", fontsize=6.5)
        for i in (1, 2):
            axes[i][j].set_xlabel("fracture plane (mm)")

    # A colourbar beside every populated panel. The NORMALISATION is shared
    # within each family (see SCALE_GROUPS), so panels of the same family remain
    # directly comparable; the per-panel bar just avoids the label collisions
    # that a single shared bar produces at this aspect ratio.
    from matplotlib.ticker import MaxNLocator
    for i, (lab, cmap) in enumerate(ROWS):
        axes[i][0].set_ylabel(lab)
        for j, sp in enumerate(specimens):
            if sp not in data:
                continue
            nz = norms[i][sp]
            if nz is None:
                continue
            p0 = axes[i][j].get_position()
            cax = fig.add_axes([p0.x1 + 0.008, p0.y0, 0.009, p0.height])
            cb = fig.colorbar(cm.ScalarMappable(norm=nz, cmap=cmap), cax=cax)
            cb.locator = MaxNLocator(nbins=4)
            cb.update_ticks()
            cb.ax.tick_params(labelsize=5.5, length=1.8, pad=1.0)
            cb.outline.set_linewidth(0.5)

    fig.savefig(out, dpi=600)
    fig.savefig(out.replace(".pdf", ".png"), dpi=200)
    print("wrote", out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--specimens", nargs="+", default=SPECIMENS)
    ap.add_argument("--stage", choices=("initial", "peak", "final"), default="peak")
    ap.add_argument("--out", default=os.path.join(
        HERE, os.pardir, "Figures", "Figure_Exodus_Fields.pdf"))
    ap.add_argument("--allow-inplane", action="store_true",
                    help="re-run the u_x/u_y check after the output is fixed")
    a = ap.parse_args()
    print("stage = %s" % a.stage)
    build(a.specimens, a.stage, os.path.abspath(a.out), a.allow_inplane)
