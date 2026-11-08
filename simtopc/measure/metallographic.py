"""
License
  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published
  by the Free Software Foundation, either version 3 of the License,
  or (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

  See the GNU General Public License for more details.
  You should have received a copy of the GNU General Public License
  along with this program. If not, see <https://www.gnu.org/licenses/>.

Description
  Metallographic geometry mode: the melt-pool cross-section as it is
  measured on an etched cross-section of a single track on a substrate
  (Dilip et al. 2017, Fig. 5 and 6), from the cells of the final time.

  Each cross-section is one layer of cells across the track (one cell
  along the scan direction). With melted = melt_field > 0 and
  metal = metal_field >= 0.5:
    width   extent across the track of the melted cells in the row of
            cells just below the substrate top (the fusion width at the
            substrate top);
    depth   substrate top minus the bottom face of the lowest melted cell;
    height  top face of the highest cell that was melted and is metal,
            minus the substrate top (gaps of powder or gas below it are
            ignored); negative for a depression below the substrate top;
    fused   the section has melted cells at or below the substrate top.
  The track is continuous when every measured section is fused.

  The void fraction of each section is the row
  count of the current single-track mode applied to the consolidated cells
  of the section (melted and metal): in each row of cells, the cells
  missing between the first and the last consolidated cell are voids.

  Steady sections (optional, steady_sections: true): of the measured
  sections, those whose fusion zone in the substrate solidified before the
  laser was switched off (90 % of its melted cells, by solidificationTime),
  the contiguous run from the first one; the sections still liquid at the
  switch-off froze as the end pool, which a cut through the middle of a
  long track does not have.

Assumptions
  - Uniform cubic cells, arrays from simtopc.measure.cells
  - The substrate top lies on a cell face

Authors
  Simon A. Rodriguez, University College Dublin (UCD)
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

import numpy as np

_NUMBER = r"[-+0-9.eE]+"


@dataclass(frozen=True)
class SectionMeasurement:
    track: float            # cell-centre coordinate along the track (m)
    width: float
    depth: float
    height: float
    fused: bool
    void_cells: int         # rows porosity: missing cells between consolidated cells
    solid_cells: int        # rows porosity: consolidated cells


def _tolerance(grid) -> float:
    return 1e-6 * grid.cell_size


def sections_in_window(grid, begin: float, end: float) -> np.ndarray:
    """Indices of the cross-sections whose cell centre along the track lies in [begin, end]."""
    c = grid.centres(0)
    tol = _tolerance(grid)
    return np.nonzero((c >= begin - tol) & (c <= end + tol))[0]


def lateral_cells(grid, x_min: float, x_max: float) -> np.ndarray:
    """Cells across the track whose centre lies in [x_min, x_max]."""
    c = grid.centres(2)
    tol = _tolerance(grid)
    return (c >= x_min - tol) & (c <= x_max + tol)


def substrate_row(grid, substrate_top: float) -> int:
    """Index of the row of cells just below the substrate top (the top row of the substrate)."""
    h = grid.cell_size
    v0 = grid.origin[1]
    rows = (substrate_top - v0) / h
    j = int(round(rows)) - 1
    if abs(rows - round(rows)) > 1e-3:
        raise ValueError(
            f"measure.substrate_top ({substrate_top}) is not on a cell face "
            f"(vertical cells of {h} m from {v0} m)."
        )
    if not 0 <= j < grid.shape[1]:
        raise ValueError(
            f"measure.substrate_top ({substrate_top}) is outside the mesh "
            f"({v0} to {v0 + grid.shape[1] * h} m along {grid.axes.vertical})."
        )
    return j


def _extent(row: np.ndarray, h: float) -> float:
    i = np.nonzero(row)[0]
    return float((i.max() - i.min() + 1) * h) if i.size else 0.0


def row_voids(consolidated: np.ndarray):
    """(void cells, consolidated cells) of a section (vertical, lateral): the cells missing
    between the first and last consolidated cell of each row."""
    voids = solid = 0
    for row in consolidated:
        i = np.nonzero(row)[0]
        if i.size:
            solid += int(i.size)
            voids += int(i.max() - i.min() + 1 - i.size)
    return voids, solid


def measure_section(melted: np.ndarray, metal: np.ndarray, jt: int, h: float,
                    v0: float, substrate_top: float, track: float) -> SectionMeasurement:
    """Metallographic measurement of one section; melted and metal are (vertical, lateral)."""
    width = _extent(melted[jt], h)
    rows = np.nonzero(melted.any(axis=1))[0]
    depth = float(substrate_top - (v0 + rows.min() * h)) if rows.size else float("nan")
    bead_rows = np.nonzero((melted & metal).any(axis=1))[0]
    height = float(v0 + (bead_rows.max() + 1) * h - substrate_top) if bead_rows.size else float("nan")
    fused = bool(melted[: jt + 1].any())
    voids, solid = row_voids(melted & metal)
    return SectionMeasurement(track=float(track), width=width, depth=depth, height=height,
                              fused=fused, void_cells=voids, solid_cells=solid)


def measure_sections(grid, sections, substrate_top: float, lateral=None):
    """SectionMeasurement of each section index (along the track)."""
    jt = substrate_row(grid, substrate_top)
    melted = grid.melted()
    metal = grid.is_metal()
    if lateral is not None:
        melted = melted & lateral[None, None, :]
        metal = metal & lateral[None, None, :]
    centres = grid.centres(0)
    return [measure_section(melted[k], metal[k], jt, grid.cell_size, grid.origin[1],
                            substrate_top, centres[k]) for k in sections]


def laser_off_time_from_case(case_dir) -> float:
    """Time of the last non-zero power entry of constant/timeVsLaserPower."""
    path = Path(case_dir) / "constant" / "timeVsLaserPower"
    if not path.exists():
        raise FileNotFoundError(
            f"{path} not found: give measure.laser_off_time for the steady sections.")
    pairs = re.findall(r"\(\s*(" + _NUMBER + r")\s+(" + _NUMBER + r")\s*\)", path.read_text())
    on = [float(t) for t, p in pairs if float(p) > 0]
    if not on:
        raise ValueError(f"{path} has no entry with the laser on.")
    return max(on)


def steady_sections(grid, candidates, substrate_top: float, laser_off_time: float, lateral=None):
    """Steady sections of the track (dilip_tools.steady_sections): among the candidate
    sections (the measured window), those whose fusion zone in the substrate solidified
    before the laser was switched off, by the 90th percentile of the solidificationTime
    of their melted substrate cells; the contiguous run from the first one.

    Returns the steady section indices and the 90th percentile of every candidate."""
    if grid.solidification_time is None:
        raise ValueError("The steady sections need the solidificationTime field.")
    jt = substrate_row(grid, substrate_top) + 1          # rows of the substrate: [:jt]
    melted = grid.melted()
    st = grid.solidification_time
    if lateral is not None:
        melted = melted & lateral[None, None, :]
    candidates = np.asarray(candidates, dtype=int)
    p90 = np.full(candidates.size, np.nan)
    for i, k in enumerate(candidates):
        m = melted[k, :jt] & (st[k, :jt] > 0)
        if m.any():
            p90[i] = np.percentile(st[k, :jt][m], 90)
    with np.errstate(invalid="ignore"):
        ok = p90 < laser_off_time
    ks = candidates[ok]
    if ks.size:                                          # the contiguous run from the first one
        br = np.nonzero(np.diff(ks) > 1)[0]
        ks = ks[: br[0] + 1] if br.size else ks
    return ks, p90
