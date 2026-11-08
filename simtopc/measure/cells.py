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
  Cell reader of the cell-based measurement modes (metallographic geometry,
  closed_pores_3d porosity and steady sections).

  Reads the cell fields of the final time of a reconstructed OpenFOAM case
  (melt history, metal volume fraction and, when present, solidification
  time) directly from the ASCII field files, without pvpython, and arranges
  them as uniform 3D arrays indexed (track, vertical, lateral), following
  the axes given in the configuration.

  The cell layout comes either from the cell-centre fields Cx, Cy and Cz of
  the final time (written by `postProcess -func writeCellCentres`) or from
  a single-block uniform blockMeshDict (cell index i + nx (j + ny k)).

Assumptions
  - Uniform cubic cells (the same cell size along x, y and z)
  - ASCII field files (binary files are rejected with an error)
  - The case is in its native axes (not remapped by
    tools/adapt_case_to_simtopc.py); the axes are given in the configuration

Authors
  Simon A. Rodriguez, University College Dublin (UCD)
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Tuple

import numpy as np


AXIS_NAMES = ("x", "y", "z")
_FOAM_AXIS_POSITION = {"z": 0, "y": 1, "x": 2}   # blockMesh fields reshape to (nz, ny, nx)
_NUMBER = r"[-+0-9.eE]+"
_CASE_SUBFOLDERS = {"0", "constant", "system"}


@dataclass(frozen=True)
class AxesConfig:
    """Which case axis is the scan (track) direction and which is vertical."""
    track: str = "y"
    vertical: str = "z"

    @property
    def lateral(self) -> str:
        return next(a for a in AXIS_NAMES if a not in (self.track, self.vertical))

    @property
    def order(self) -> Tuple[str, str, str]:
        """Case axes of the array dimensions (track, vertical, lateral)."""
        return (self.track, self.vertical, self.lateral)

    def validate(self) -> None:
        for name, value in (("track", self.track), ("vertical", self.vertical)):
            if value not in AXIS_NAMES:
                raise ValueError(
                    f"measure.axes.{name} must be one of x, y, z, got {value!r}."
                )
        if self.track == self.vertical:
            raise ValueError(
                "measure.axes.track and measure.axes.vertical must differ, "
                f"got {self.track!r} for both."
            )


@dataclass
class CellGrid:
    """Final-time cell fields on a uniform grid, arrays indexed (track, vertical, lateral)."""
    melt: np.ndarray                    # melt_field values
    metal: np.ndarray                   # metal_field values
    solidification_time: Optional[np.ndarray]
    cell_size: float                    # m
    origin: Tuple[float, float, float]  # lower corner along (track, vertical, lateral), m
    axes: AxesConfig
    time: str

    @property
    def shape(self):
        return self.melt.shape

    def melted(self) -> np.ndarray:
        """Cells that were melted at some time (melt_field > 0)."""
        return self.melt > 0

    def is_metal(self) -> np.ndarray:
        """Cells that are metal at the final time (metal_field >= 0.5)."""
        return self.metal >= 0.5

    def centres(self, dim: int) -> np.ndarray:
        """Cell-centre coordinates (m) along array dimension dim (0 track, 1 vertical, 2 lateral)."""
        return self.origin[dim] + (np.arange(self.shape[dim]) + 0.5) * self.cell_size

    def faces(self, dim: int) -> np.ndarray:
        """Lower-face coordinates (m) of the cells along array dimension dim."""
        return self.origin[dim] + np.arange(self.shape[dim]) * self.cell_size

    def to_case_coordinates(self, track, vertical, lateral) -> dict:
        """Map (track, vertical, lateral) coordinates to the case axes x, y, z."""
        values = dict(zip(self.axes.order, (track, vertical, lateral)))
        return {a: values[a] for a in AXIS_NAMES}


def last_time_dir(case_dir) -> Path:
    """The latest time directory of the case (time 0 excluded)."""
    times = []
    for d in Path(case_dir).iterdir():
        if not d.is_dir() or d.name in _CASE_SUBFOLDERS:
            continue
        try:
            t = float(d.name)
        except ValueError:
            continue
        if t != 0:
            times.append((t, d))
    if not times:
        raise FileNotFoundError(f"No time directory other than 0 found in {case_dir}")
    return max(times, key=lambda p: p[0])[1]


def _check_ascii(text: str, path: Path) -> None:
    if re.search(r"\bformat\s+binary\s*;", text):
        raise ValueError(
            f"{path} is a binary OpenFOAM file; the cell reader needs ASCII files "
            "(foamFormatConvert, or writeFormat ascii)."
        )


def read_scalar_field(path, n_cells: Optional[int] = None) -> np.ndarray:
    """Internal field of an ASCII OpenFOAM volScalarField (nonuniform list or uniform value)."""
    path = Path(path)
    text = path.read_text()
    _check_ascii(text, path)
    m = re.search(r"internalField\s+nonuniform\s+List<scalar>\s*\n?\s*(\d+)\s*\n?\s*\(", text)
    if m:
        n = int(m.group(1))
        end = text.index(")", m.end())
        values = np.array(text[m.end():end].split(), dtype=float)
        if values.size != n:
            raise ValueError(f"Expected {n} values in {path}, found {values.size}.")
        if n_cells is not None and n != n_cells:
            raise ValueError(f"{path} has {n} cells, the mesh has {n_cells}.")
        return values
    u = re.search(r"internalField\s+uniform\s+(" + _NUMBER + r")\s*;", text)
    if u:
        if n_cells is None:
            raise ValueError(f"{path} has a uniform internal field; the number of cells is needed.")
        return np.full(n_cells, float(u.group(1)))
    raise ValueError(f"Could not parse the internal field of {path}.")


def _strip_comments(text: str) -> str:
    text = re.sub(r"/\*.*?\*/", " ", text, flags=re.S)
    return re.sub(r"//[^\n]*", " ", text)


def read_blockmesh_geometry(case_dir):
    """Cells per axis (nx, ny, nz), lower corner and upper corner (m) of a single-block,
    uniformly graded blockMeshDict."""
    case_dir = Path(case_dir)
    path = case_dir / "system" / "blockMeshDict"
    if not path.exists():
        path = case_dir / "constant" / "polyMesh" / "blockMeshDict"
    if not path.exists():
        raise FileNotFoundError(f"No blockMeshDict found in {case_dir}")
    text = _strip_comments(path.read_text())
    sm = re.search(r"\b(?:convertToMeters|scale)\s+(" + _NUMBER + r")\s*;", text)
    scale = float(sm.group(1)) if sm else 1.0
    vm = re.search(r"\bvertices\s*\((.*?)\)\s*;", text, flags=re.S)
    if not vm:
        raise ValueError(f"No vertices in {path}")
    vertices = np.array(
        [[float(v) for v in t] for t in re.findall(
            r"\(\s*(" + _NUMBER + r")\s+(" + _NUMBER + r")\s+(" + _NUMBER + r")\s*\)", vm.group(1))]
    ) * scale
    blocks = re.findall(
        r"hex\s*\(([^)]*)\)\s*\(\s*(\d+)\s+(\d+)\s+(\d+)\s*\)\s*simpleGrading\s*\(([^)]*)\)", text)
    if len(blocks) != 1:
        raise ValueError(
            f"{path}: the cell reader handles a single hex block, found {len(blocks)}; "
            "write the cell centres (postProcess -func writeCellCentres) instead."
        )
    labels, nx, ny, nz, grading = blocks[0]
    if any(abs(float(g) - 1.0) > 1e-12 for g in grading.split()):
        raise ValueError(f"{path}: the block is graded ({grading.strip()}); uniform cells are needed.")
    corners = vertices[[int(i) for i in labels.split()]]
    lower, upper = corners.min(axis=0), corners.max(axis=0)
    # an axis-aligned box: every corner on the bounding box
    on_box = np.isclose(corners, lower, rtol=0, atol=1e-12) | np.isclose(corners, upper, rtol=0, atol=1e-12)
    if not on_box.all():
        raise ValueError(f"{path}: the block is not an axis-aligned box.")
    return (int(nx), int(ny), int(nz)), lower, upper


def _last_point(points_path: Path):
    """Last point of an ASCII constant/polyMesh/points file (read from its end)."""
    with open(points_path, "rb") as f:
        f.seek(0, 2)
        size = f.tell()
        f.seek(max(0, size - 4096))
        tail = f.read().decode("ascii", errors="replace")
    found = re.findall(r"\(\s*(" + _NUMBER + r")\s+(" + _NUMBER + r")\s+(" + _NUMBER + r")\s*\)", tail)
    return np.array([float(v) for v in found[-1]]) if found else None


def _layout_from_blockmesh(case_dir, cell_size):
    (nx, ny, nz), lower, upper = read_blockmesh_geometry(case_dir)
    sizes = (upper - lower) / np.array([nx, ny, nz])
    if not np.allclose(sizes, sizes[0], rtol=1e-6, atol=0):
        raise ValueError(f"blockMeshDict cells are not cubic: {sizes} m.")
    h = float(sizes[0])
    if cell_size is not None and not np.isclose(h, cell_size, rtol=1e-6, atol=0):
        raise ValueError(f"measure.cell_size ({cell_size}) differs from the blockMeshDict cell size ({h}).")
    points = Path(case_dir) / "constant" / "polyMesh" / "points"
    if points.exists():
        last = _last_point(points)      # blockMesh writes the upper corner last
        if last is not None and not np.allclose(last, upper, rtol=0, atol=1e-3 * h):
            raise ValueError(
                f"The mesh of {case_dir} does not match its blockMeshDict (last point {last}, "
                f"block corner {upper}); was it remapped by adapt_case_to_simtopc.py? "
                "The cell-based modes read the case in its native axes (measure.axes)."
            )
    return (nx, ny, nz), lower, h


def _arrange_blockmesh(values, n_xyz, axes):
    nx, ny, nz = n_xyz
    a = values.reshape(nz, ny, nx)
    return np.transpose(a, [_FOAM_AXIS_POSITION[ax] for ax in axes.order])


def read_cell_grid(case_dir, axes: AxesConfig = AxesConfig(), melt_field="meltHistory",
                   metal_field="alpha.metal", cell_size=None, geometry="auto",
                   time_dir=None, need_solidification_time=False) -> CellGrid:
    """Final-time cell fields of case_dir as a CellGrid.

    geometry: 'cell_centres' (Cx, Cy, Cz in the time directory), 'blockmesh' (single
    uniform block) or 'auto' (cell centres when present, the blockMeshDict otherwise)."""
    case_dir = Path(case_dir)
    axes.validate()
    t = Path(time_dir) if time_dir is not None else last_time_dir(case_dir)
    if geometry == "auto":
        geometry = "cell_centres" if all((t / c).exists() for c in ("Cx", "Cy", "Cz")) else "blockmesh"
    st_path = t / "solidificationTime"
    if need_solidification_time and not st_path.exists():
        raise FileNotFoundError(f"{st_path} is needed (steady sections).")

    if geometry == "blockmesh":
        n_xyz, lower, h = _layout_from_blockmesh(case_dir, cell_size)
        n = int(np.prod(n_xyz))
        melt = read_scalar_field(t / melt_field, n)
        metal = read_scalar_field(t / metal_field, n)
        st = read_scalar_field(st_path, n) if st_path.exists() else None
        arrange = lambda v: _arrange_blockmesh(v, n_xyz, axes)
        lower_by_axis = dict(zip(AXIS_NAMES, lower))
        origin = tuple(float(lower_by_axis[a]) for a in axes.order)
        return CellGrid(melt=arrange(melt), metal=arrange(metal),
                        solidification_time=arrange(st) if st is not None else None,
                        cell_size=h, origin=origin, axes=axes, time=t.name)

    if geometry != "cell_centres":
        raise ValueError(f"Unknown cell geometry source {geometry!r}.")
    if cell_size is None:
        raise ValueError("measure.cell_size is needed to place the cell centres on the grid.")
    h = float(cell_size)
    centres = {a: read_scalar_field(t / f"C{a}") for a in AXIS_NAMES}
    n = centres["x"].size
    melt = read_scalar_field(t / melt_field, n)
    metal = read_scalar_field(t / metal_field, n)
    st = read_scalar_field(st_path, n) if st_path.exists() else None
    idx, origin, shape = [], [], []
    for a in axes.order:
        c = centres[a]
        c0 = float(c.min())
        k = np.rint((c - c0) / h).astype(np.int64)
        if not np.allclose(c0 + k * h, c, rtol=0, atol=1e-3 * h):
            raise ValueError(f"The cell centres along {a} are not on a uniform grid of {h} m.")
        idx.append(k)
        origin.append(c0 - 0.5 * h)
        shape.append(int(k.max()) + 1)
    if int(np.prod(shape)) != n:
        raise ValueError(
            f"The {n} cells do not fill the {shape} box of the grid: the cell-based modes "
            "need a complete uniform mesh."
        )
    flat = np.ravel_multi_index(tuple(idx), shape)
    if np.unique(flat).size != n:
        raise ValueError("Two cells share a grid position: the mesh is not uniform.")

    def arrange(v):
        out = np.empty(n, dtype=float)
        out[flat] = v
        return out.reshape(shape)

    return CellGrid(melt=arrange(melt), metal=arrange(metal),
                    solidification_time=arrange(st) if st is not None else None,
                    cell_size=h, origin=tuple(origin), axes=axes, time=t.name)
