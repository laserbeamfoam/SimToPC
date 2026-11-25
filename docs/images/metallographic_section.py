"""Figure of docs/METALLOGRAPHIC_MODE.md: one cross-section of a completed laserbeamFoam case
with the metallographic width and depth marked, drawn from the cells that SimToPC reads.

    python3 docs/images/metallographic_section.py <case_dir> <track_coordinate_m> [out.png]

The figure in the repository is the section at z = 1.0 mm of test_case_3 of
examples/measure_metallographic (1.0 m/s, 5 um cells), with substrate_top = 150e-6."""
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.patches import Patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
from simtopc.measure.cells import AxesConfig, read_cell_grid          # noqa: E402
from simtopc.measure.metallographic import measure_section, substrate_row  # noqa: E402

case, coordinate = sys.argv[1], float(sys.argv[2])
out = sys.argv[3] if len(sys.argv) > 3 else str(Path(__file__).with_name("metallographic_section.png"))
TOP = 150e-6
grid = read_cell_grid(case, AxesConfig(track="z", vertical="y"))
h, v0, x0 = grid.cell_size, grid.origin[1], grid.origin[2]
k = int(np.argmin(np.abs(grid.centres(0) - coordinate)))
melted, metal = grid.melted()[k], grid.is_metal()[k]
jt = substrate_row(grid, TOP)
m = measure_section(melted, metal, jt, h, v0, TOP, grid.centres(0)[k], alpha=grid.metal[k])
row = jt - m.width_rows_down
cols = np.nonzero(melted[row])[0]

# 0 gas, 1 metal that never melted, 2 fusion zone (melted) and metal, 3 melted, now gas
kind = np.where(melted, np.where(metal, 2, 3), np.where(metal, 1, 0))
um = 1e6
xf, yf = (x0 + h * np.arange(kind.shape[1] + 1)) * um, (v0 + h * np.arange(kind.shape[0] + 1)) * um
fig, ax = plt.subplots(figsize=(9, 5.6), dpi=160)
colours = ["#ffffff", "#c9c9c4", "#e2803a", "#f7d9bf"]
ax.pcolormesh(xf, yf, kind, cmap=ListedColormap(colours), vmin=-0.5, vmax=3.5,
              edgecolors="#00000022", linewidth=0.3)
top = TOP * um
ax.axhline(top, color="#1b1b1b", lw=1.3, ls="--")
ax.text(xf[0] + 3, top - 4, "plate top", ha="left", va="top", fontsize=9)
xl, xr = xf[cols.min()], xf[cols.max() + 1]
yw = (yf[row] + yf[row + 1]) / 2
ax.annotate("", (xl, yw), (xr, yw), arrowprops=dict(arrowstyle="<->", color="#10335c", lw=1.8))
ax.text((xl + xr) / 2, top + 52, f"width = {m.width * um:.0f} µm\n(row of cells just below the plate top)",
        ha="center", va="bottom", fontsize=9.5, color="#10335c", weight="bold")
bottom = top - m.depth * um
xd = xr + 0.3 * (xf[-1] - xr)
ax.plot([(xl + xr) / 2, xd + 6], [bottom, bottom], color="#10335c", lw=0.9, ls=":")
ax.annotate("", (xd, top), (xd, bottom), arrowprops=dict(arrowstyle="<->", color="#10335c", lw=1.8))
ax.text(xd + 4, (top + bottom) / 2, f"depth =\n{m.depth * um:.0f} µm", ha="left", va="center",
        fontsize=9.5, color="#10335c", weight="bold")
ax.set_aspect("equal")
ax.set_ylim(max(yf[0], top - m.depth * um - 45), min(yf[-1], top + 95))
ax.set_xlabel("across the track (µm)")
ax.set_ylabel("vertical (µm)")
ax.legend(handles=[Patch(fc=colours[2], ec="#888", label="fusion zone (melted at some time): metal at the end"),
                   Patch(fc=colours[3], ec="#888", label="fusion zone: gas at the end"),
                   Patch(fc=colours[1], ec="#888", label="metal that never melted (plate, powder)"),
                   Patch(fc=colours[0], ec="#888", label="gas")],
          loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2, frameon=False, fontsize=9)
for s in ("top", "right"):
    ax.spines[s].set_visible(False)
fig.tight_layout()
fig.savefig(out)
print(f"section {k} at {grid.centres(0)[k]:.7f} m: width {m.width * um:.1f} um (rows down {m.width_rows_down}), "
      f"depth {m.depth * um:.1f} um -> {out}")
