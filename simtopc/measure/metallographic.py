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
  along the scan direction). The fusion zone is the cells with
  melt_field > 0; metal = metal_field >= 0.5; melted metal = both:
    width   extent across the track of the fusion zone in the row of
            cells just below the substrate top (the fusion width at the
            substrate top, as in Dilip et al. 2017, Fig. 5). When an edge
            cell of that extent ended as gas (the bead surface sank into the
            row), the width is taken one row lower, and so on down to
            width_max_rows_down rows; if no row qualifies, it is not
            measured (NaN). Taking the nearest row below is a zero-order
            one-sided extrapolation of the width to the substrate top, with
            an error of order (cell size) x dW/dy;
    depth   substrate top minus the bottom face of the lowest melted-metal
            cell (the depth of penetration); 0 in a section without any;
    height  top face of the highest cell that was melted and is metal,
            minus the substrate top (gaps of powder or gas below it are
            ignored); negative for a depression below the substrate top;
    fill    metal fraction (metal_field, clipped to [0, 1], averaged) of the
            fusion zone at and below the substrate top: a control of how
            full the melt pool is, not a filter of the sections;
    surface centreline metal height: the metal_field summed over the
            column of cells at the middle of the lateral range (mean of the
            middle three columns) times the cell size, from the bottom of
            the mesh, minus the substrate top;
    fused   the section has melted cells at or below the substrate top.
  The track is continuous when every measured section is fused.

  The void fraction of each section is the row
  count of the current single-track mode applied to the consolidated cells
  of the section (melted and metal): in each row of cells, the cells
  missing between the first and the last consolidated cell are voids.

  Measurement window (window_mode):
    fixed           the sections whose cell centre lies in [y_begin, y_end];
    steady_stretch  one window for each scan speed, the same for all the
                    cases of that speed: the steady stretch of each case is
                    the longest stretch of [y_begin, y_end] in which the width
                    and the depth, after a running median of
                    steady_filter_length, both stay within steady_tolerance
                    of their median over the stretch; the window starts
                    window_margin after the latest start of the steady
                    stretches of the cases of that speed (cases whose cell is
                    larger than steady_tolerance are measured but do not set
                    the window), rounded up to a multiple of window_step, and
                    is window_length long; it must end inside the steady
                    stretch of every case that sets it.
  With track_reference: laser_start, the coordinates along the track
  (y_begin, y_end and the window) are measured from the first position of
  the laser (constant/timeVsLaserPosition), so that cases whose tracks start
  at different positions share the window.

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
    width_rows_down: int = 0     # rows below the substrate-top row where the width was taken; -1 not measured
    fill: float = float("nan")   # metal fraction of the fusion zone at and below the substrate top
    surface: float = float("nan")  # centreline metal height above the substrate top


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


def fusion_width(melted: np.ndarray, metal: np.ndarray, jt: int, h: float, max_rows_down: int = 2):
    """(width, rows down) of a section: the extent of the fusion zone in the row jt just below
    the substrate top; when an edge cell of the extent is not metal, the same one row lower, down
    to max_rows_down rows; (NaN, -1) if no row qualifies, (0, 0) if row jt has no melted cell."""
    if not melted[jt].any():
        return 0.0, 0
    for j in range(jt, max(jt - max_rows_down, 0) - 1, -1):
        i = np.nonzero(melted[j])[0]
        if i.size and metal[j, i[0]] and metal[j, i[-1]]:
            return float((i[-1] - i[0] + 1) * h), jt - j
    return float("nan"), -1


def measure_section(melted: np.ndarray, metal: np.ndarray, jt: int, h: float,
                    v0: float, substrate_top: float, track: float, alpha=None,
                    max_rows_down: int = 2, centre=None) -> SectionMeasurement:
    """Metallographic measurement of one section; melted (melt_field > 0) and metal
    (metal_field >= 0.5) are boolean (vertical, lateral) arrays, alpha the metal_field values
    (for the fill and the centreline surface; NaN without it) and centre the lateral index of
    the middle column (default: the middle of the section)."""
    width, down = fusion_width(melted, metal, jt, h, max_rows_down)
    consolidated = melted & metal
    rows = np.nonzero(consolidated.any(axis=1))[0]
    depth = float(substrate_top - (v0 + rows.min() * h)) if rows.size else 0.0
    height = float(v0 + (rows.max() + 1) * h - substrate_top) if rows.size else float("nan")
    fused = bool(melted[: jt + 1].any())
    voids, solid = row_voids(consolidated)
    fill = surface = float("nan")
    if alpha is not None:
        a = np.clip(alpha, 0.0, 1.0)
        below = melted[: jt + 1]
        if below.any():
            fill = float(a[: jt + 1][below].mean())
        ic = melted.shape[1] // 2 if centre is None else int(centre)
        surface = float(v0 + alpha[:, max(ic - 1, 0):ic + 2].mean(axis=1).sum() * h - substrate_top)
    return SectionMeasurement(track=float(track), width=width, depth=depth, height=height,
                              fused=fused, void_cells=voids, solid_cells=solid,
                              width_rows_down=down, fill=fill, surface=surface)


def measure_sections(grid, sections, substrate_top: float, lateral=None, max_rows_down: int = 2):
    """SectionMeasurement of each section index (along the track)."""
    jt = substrate_row(grid, substrate_top)
    melted = grid.melted()
    metal = grid.is_metal()
    alpha = grid.metal
    centre = None
    if lateral is not None:
        melted = melted & lateral[None, None, :]
        metal = metal & lateral[None, None, :]
        inside = np.nonzero(lateral)[0]
        centre = int(inside[inside.size // 2]) if inside.size else None
    centres = grid.centres(0)
    return [measure_section(melted[k], metal[k], jt, grid.cell_size, grid.origin[1],
                            substrate_top, centres[k], alpha=alpha[k],
                            max_rows_down=max_rows_down, centre=centre) for k in sections]


def steady_stretch(track, width, depth, cell_size: float, begin: float, end: float,
                   tolerance: float = 5e-6, filter_length: float = 50e-6):
    """(first, last) section indices of the steady stretch of a case: the longest stretch of
    the sections with track coordinate in [begin, end] (track sorted, one entry per section of
    the mesh) in which the width (NaN taken as 0) and the depth, after a running median of
    filter_length (an odd number of cells, edges repeated), both stay within tolerance of
    their median over the stretch."""
    from scipy.ndimage import median_filter
    track = np.asarray(track, dtype=float)
    nf = int(round(filter_length / cell_size)) | 1
    filtered = [median_filter(np.asarray(x, dtype=float), nf, mode="nearest")
                for x in (np.nan_to_num(np.asarray(width, dtype=float)), depth)]
    kmin = int(np.searchsorted(track, begin))
    kmax = int(np.searchsorted(track, end)) - 1
    if kmax <= kmin:
        raise ValueError(f"No section between {begin} and {end} along the track.")
    best = (0, kmin, kmin)
    eps = 1e-6 * cell_size
    for k0 in range(kmin, kmax):
        for k1 in range(kmax, k0 + best[0], -1):
            if all(np.abs(f[k0:k1 + 1] - np.median(f[k0:k1 + 1])).max() <= tolerance + eps for f in filtered):
                best = (k1 - k0, k0, k1)
                break
    return best[1], best[2]


def speed_window(starts, ends, margin: float = 50e-6, length: float = 400e-6, step: float = 50e-6):
    """Window (begin, end) of one scan speed from the steady stretches (start, end) of the
    cases that set it: it starts margin after the latest start, rounded up to a multiple of
    step, and is length long; an error if it does not end inside every steady stretch."""
    if not len(starts):
        raise ValueError("No case sets the window of this speed (all cells larger than the tolerance?).")
    q = (max(starts) + margin) / step
    begin = float(np.ceil(q - 1e-9) * step)
    end = begin + length
    if end > min(ends) + 1e-9 * step:
        raise ValueError(
            f"The window [{begin}, {end}] ends outside the steady stretch of a case "
            f"(the shortest ends at {min(ends)}).")
    return begin, end


def laser_start_from_case(case_dir, track_axis: str) -> float:
    """Coordinate along the track (axis x, y or z of the case) of the first laser position of
    constant/timeVsLaserPosition."""
    path = Path(case_dir) / "constant" / "timeVsLaserPosition"
    if not path.exists():
        raise FileNotFoundError(f"{path} not found: needed by measure.track_reference laser_start.")
    m = re.search(r"\(\s*(" + _NUMBER + r")\s+\(\s*(" + _NUMBER + r")\s+(" + _NUMBER + r")\s+("
                  + _NUMBER + r")\s*\)\s*\)", path.read_text())
    if m is None:
        raise ValueError(f"{path} has no (time (x y z)) entry.")
    return float(m.group(2 + "xyz".index(track_axis)))


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
