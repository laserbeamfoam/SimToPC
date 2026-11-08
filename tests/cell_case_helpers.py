"""Small synthetic OpenFOAM cases for the tests of the cell-based measurement modes,
and the locations of the real runs used by the comparisons (skipped when missing)."""
from __future__ import annotations

import importlib.util
from pathlib import Path

import numpy as np


PHILIPS = Path(
    "/media/simon/28188c55-61a7-4153-8d95-b056ff7f5f56/Andrea spinal cage ct + gcode/"
    "raw data/PhilipsNNApproach"
)
DILIP = PHILIPS / "validacion_claude" / "dilip2017"
RVE_PIPELINE = PHILIPS / "rve_pipeline"
RVE_TEST_CASE = RVE_PIPELINE / "tests" / "uniform700" / "ray_fix_meluxina" / "run_meluxina" / "d4x8" / "case"


def load_module(name, path):
    """Import a reference script from its path without touching it."""
    spec = importlib.util.spec_from_file_location(name, str(path))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_scalar_field(path: Path, values, name: str) -> None:
    values = np.asarray(values, dtype=float).ravel()
    body = "\n".join(repr(float(v)) for v in values)
    path.write_text(
        "FoamFile\n{\n    version 2.0;\n    format ascii;\n    class volScalarField;\n"
        f"    object {name};\n}}\n\ndimensions [0 0 0 0 0 0 0];\n\n"
        f"internalField   nonuniform List<scalar> \n{values.size}\n(\n{body}\n)\n;\n\n"
        "boundaryField\n{\n    walls\n    {\n        type zeroGradient;\n    }\n}\n"
    )


def write_uniform_field(path: Path, value: float, name: str) -> None:
    path.write_text(
        "FoamFile\n{\n    version 2.0;\n    format ascii;\n    class volScalarField;\n"
        f"    object {name};\n}}\n\ndimensions [0 0 0 0 0 0 0];\n\n"
        f"internalField   uniform {value};\n\nboundaryField\n{{\n}}\n"
    )


def write_blockmesh(case: Path, n_xyz, h, origin=(0.0, 0.0, 0.0), grading="1 1 1",
                    keyword="convertToMeters") -> None:
    nx, ny, nz = n_xyz
    x0, y0, z0 = origin
    x1, y1, z1 = x0 + nx * h, y0 + ny * h, z0 + nz * h
    (case / "system").mkdir(parents=True, exist_ok=True)
    (case / "system" / "blockMeshDict").write_text(
        "FoamFile\n{\n    format ascii;\n    object blockMeshDict;\n}\n"
        f"{keyword} 1.0;\n\nvertices\n(\n"
        f"    ({x0!r} {y0!r} {z0!r})\n    ({x1!r} {y0!r} {z0!r})\n    ({x1!r} {y1!r} {z0!r})\n"
        f"    ({x0!r} {y1!r} {z0!r})\n    ({x0!r} {y0!r} {z1!r})\n    ({x1!r} {y0!r} {z1!r})\n"
        f"    ({x1!r} {y1!r} {z1!r})\n    ({x0!r} {y1!r} {z1!r})\n);\n\n"
        f"blocks\n(\n    hex (0 1 2 3 4 5 6 7) ({nx} {ny} {nz}) simpleGrading ({grading})\n);\n"
        "// a comment (with parentheses)\nedges\n(\n);\n"
    )


def foam_order(array_zyx):
    """Flatten an (nz, ny, nx) array in OpenFOAM blockMesh cell order (x fastest)."""
    return np.asarray(array_zyx).ravel()


def make_case(case: Path, fields_zyx: dict, h: float, origin=(0.0, 0.0, 0.0),
              time="0.001", cell_centres=False, shuffle_seed=None) -> Path:
    """A case with the given (nz, ny, nx) cell fields at time `time`.

    cell_centres=True also writes Cx, Cy, Cz; with shuffle_seed the cells are written in a
    random order (the cell-centre reader must not depend on the blockMesh order)."""
    nz, ny, nx = next(iter(fields_zyx.values())).shape
    write_blockmesh(case, (nx, ny, nz), h, origin)
    (case / "constant").mkdir(exist_ok=True)
    t = case / time
    t.mkdir(parents=True, exist_ok=True)
    (case / "0").mkdir(exist_ok=True)
    order = np.arange(nx * ny * nz)
    if shuffle_seed is not None:
        order = np.random.default_rng(shuffle_seed).permutation(order)
    for name, arr in fields_zyx.items():
        write_scalar_field(t / name, foam_order(arr)[order], name)
    if cell_centres:
        k, j, i = np.meshgrid(np.arange(nz), np.arange(ny), np.arange(nx), indexing="ij")
        for name, idx, o in (("Cx", i, origin[0]), ("Cy", j, origin[1]), ("Cz", k, origin[2])):
            write_scalar_field(t / name, (o + (foam_order(idx) + 0.5) * h)[order], name)
    return case
