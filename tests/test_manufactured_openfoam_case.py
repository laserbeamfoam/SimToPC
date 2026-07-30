from __future__ import annotations

import json
import os
import shutil
import subprocess
from pathlib import Path

import pandas as pd
import pytest
from joblib import load

from simtopc.measure.main import run as run_measure


OPENFOAM_BASHRC = os.environ.get("SIMTOPC_OPENFOAM_BASHRC")

MANUFACTURED_SECTIONS = [
    (25.0e-6, 110.0e-6, 20.0e-6, 40.0e-6),
    (110.0e-6, 195.0e-6, 25.0e-6, 60.0e-6),
    (195.0e-6, 275.0e-6, 30.0e-6, 80.0e-6),
]

# Optional internal missing points. The main manufactured case keeps this
# empty so that the width, height, and depth verification remains a clean
# three-step reference.
PRESCRIBED_VOID_POINTS = []
COORD_TOL = 1.0e-12

REPRESENTATIVE_SECTIONS = {
    50.0e-6: (40.0e-6, 20.0e-6, 15.0e-6),
    120.0e-6: (60.0e-6, 25.0e-6, 20.0e-6),
    240.0e-6: (80.0e-6, 30.0e-6, 25.0e-6),
}


def _write_minimal_case(case_dir: Path) -> None:
    (case_dir / "system").mkdir(parents=True)
    (case_dir / "constant").mkdir()
    (case_dir / "0").mkdir()
    (case_dir / "main.foam").write_text("")

    (case_dir / "system" / "blockMeshDict").write_text(
        r"""
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      blockMeshDict;
}
scale 1;
vertices
(
    (0 0 0)
    (200e-6 0 0)
    (200e-6 300e-6 0)
    (0 300e-6 0)
    (0 0 120e-6)
    (200e-6 0 120e-6)
    (200e-6 300e-6 120e-6)
    (0 300e-6 120e-6)
);
blocks
(
    hex (0 1 2 3 4 5 6 7) (40 60 24) simpleGrading (1 1 1)
);
edges
(
);
boundary
(
    back { type patch; faces ((0 4 7 3)); }
    front { type patch; faces ((1 2 6 5)); }
    leftWall { type patch; faces ((0 1 5 4)); }
    rightWall { type patch; faces ((3 7 6 2)); }
    bottomWall { type patch; faces ((0 3 2 1)); }
    topWall { type patch; faces ((4 5 6 7)); }
);
mergePatchPairs
(
);
"""
    )
    (case_dir / "system" / "controlDict").write_text(
        r"""
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      controlDict;
}
application     manufacturedFields;
startFrom       startTime;
startTime       0;
stopAt          endTime;
endTime         0.0012;
deltaT          1;
writeControl    timeStep;
writeInterval   1;
purgeWrite      0;
writeFormat     ascii;
writePrecision  10;
writeCompression off;
timeFormat      general;
timePrecision   6;
runTimeModifiable true;
"""
    )
    (case_dir / "system" / "fvSchemes").write_text(
        r"""
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvSchemes;
}
ddtSchemes { default Euler; }
gradSchemes { default Gauss linear; }
divSchemes { default none; }
laplacianSchemes { default Gauss linear corrected; }
interpolationSchemes { default linear; }
snGradSchemes { default corrected; }
wallDist { method meshWave; }
"""
    )
    (case_dir / "system" / "fvSolution").write_text(
        r"""
FoamFile
{
    version     2.0;
    format      ascii;
    class       dictionary;
    object      fvSolution;
}
solvers {}
SIMPLE {}
PIMPLE {}
PISO {}
"""
    )


def _run_openfoam(command: str, cwd: Path) -> None:
    subprocess.run(
        ["bash", "-lc", f"source {OPENFOAM_BASHRC} && {command}"],
        cwd=cwd,
        check=True,
    )


def _read_scalar_internal_field(path: Path) -> list[float]:
    lines = path.read_text().splitlines()
    start = None
    count = None
    for i, line in enumerate(lines):
        if line.strip().isdigit():
            count = int(line.strip())
            start = i + 2
            break
    if start is None or count is None:
        raise ValueError(f"Could not parse OpenFOAM scalar field: {path}")

    values = []
    for line in lines[start:]:
        stripped = line.strip()
        if stripped == ")":
            break
        if stripped:
            values.append(float(stripped))
    if len(values) != count:
        raise ValueError(f"Expected {count} values in {path}, found {len(values)}")
    return values


def _scalar_field_text(
    name: str,
    dimensions: str,
    values: list[float],
    field_class: str = "volScalarField",
) -> str:
    body = "\n".join(f"{value:.12g}" for value in values)
    if field_class == "pointScalarField":
        boundary_type = "calculated"
        boundary_value = "value uniform 0;"
    else:
        boundary_type = "zeroGradient"
        boundary_value = ""
    return f"""/*--------------------------------*- C++ -*----------------------------------*\\
| =========                 |                                                 |
| \\\\      /  F ield         | OpenFOAM: The Open Source CFD Toolbox           |
|  \\\\    /   O peration     | Version:  2506                                  |
|   \\\\  /    A nd           | Website:  www.openfoam.com                      |
|    \\\\/     M anipulation  |                                                 |
\\*---------------------------------------------------------------------------*/
FoamFile
{{
    version     2.0;
    format      ascii;
    arch        "LSB;label=32;scalar=64";
    class       {field_class};
    location    "0.0012";
    object      {name};
}}
// * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * * //

dimensions      {dimensions};

internalField   nonuniform List<scalar>
{len(values)}
(
{body}
)
;

boundaryField
{{
    back {{ type {boundary_type}; {boundary_value} }}
    front {{ type {boundary_type}; {boundary_value} }}
    leftWall {{ type {boundary_type}; {boundary_value} }}
    rightWall {{ type {boundary_type}; {boundary_value} }}
    bottomWall {{ type {boundary_type}; {boundary_value} }}
    topWall {{ type {boundary_type}; {boundary_value} }}
}}

// ************************************************************************* //
"""


def _parse_openfoam_points(path: Path) -> list[tuple[float, float, float]]:
    lines = path.read_text().splitlines()
    start = None
    count = None
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.isdigit():
            count = int(stripped)
            start = i + 2
            break
    if start is None or count is None:
        raise ValueError(f"Could not parse OpenFOAM points: {path}")

    points = []
    for line in lines[start:]:
        stripped = line.strip()
        if stripped == ")":
            break
        if not stripped:
            continue
        x, y, z = stripped.strip("()").split()
        points.append((float(x), float(y), float(z)))
    if len(points) != count:
        raise ValueError(f"Expected {count} points in {path}, found {len(points)}")
    return points


def _manufactured_x_bounds(y: float, z: float) -> tuple[float, float] | None:
    x_centre = 100.0e-6
    z_surface = 90.0e-6
    cell_size = 5.0e-6
    for y_min, y_max, height, top_width in MANUFACTURED_SECTIONS:
        if y_min <= y < y_max:
            z_bottom = z_surface - height
            if z < z_bottom - 1.0e-12 or z > z_surface + 1.0e-12:
                return None
            level = int(round((z - z_bottom) / cell_size))
            n_levels = int(round(height / cell_size))
            top_intervals = int(round(top_width / cell_size))
            width_intervals = max(2, top_intervals - 2 * (n_levels - level))
            width = width_intervals * cell_size
            return x_centre - 0.5 * width, x_centre + 0.5 * width
    return None


def _inside_manufactured_pool(x: float, y: float, z: float) -> bool:
    bounds = _manufactured_x_bounds(y, z)
    if bounds is None:
        return False
    x_min, x_max = bounds
    return x_min - 1.0e-12 <= x <= x_max + 1.0e-12


def _is_prescribed_void_point(x: float, y: float, z: float) -> bool:
    return any(
        abs(x - vx) < COORD_TOL
        and abs(y - vy) < COORD_TOL
        and abs(z - vz) < COORD_TOL
        for vx, vy, vz in PRESCRIBED_VOID_POINTS
    )


def _is_prescribed_void_cell(x: float, y: float, z: float) -> bool:
    half_cell = 2.5e-6 + COORD_TOL
    return any(
        abs(x - vx) <= half_cell
        and abs(y - vy) <= half_cell
        and abs(z - vz) <= half_cell
        for vx, vy, vz in PRESCRIBED_VOID_POINTS
    )


def _write_manufactured_fields(case_dir: Path) -> None:
    _run_openfoam("blockMesh >/dev/null", cwd=case_dir)
    _run_openfoam("postProcess -func writeCellCentres -time 0 >/dev/null", cwd=case_dir)

    time_dir = case_dir / "0.0012"
    shutil.copytree(case_dir / "0", time_dir)
    for field_path in time_dir.iterdir():
        if field_path.is_file():
            field_path.write_text(
                field_path.read_text().replace('location    "0";', 'location    "0.0012";')
            )

    xs = _read_scalar_internal_field(time_dir / "Cx")
    ys = _read_scalar_internal_field(time_dir / "Cy")
    zs = _read_scalar_internal_field(time_dir / "Cz")

    occupied_cells = [
        _inside_manufactured_pool(x, y, z) and not _is_prescribed_void_cell(x, y, z)
        for x, y, z in zip(xs, ys, zs)
    ]

    points = _parse_openfoam_points(case_dir / "constant" / "polyMesh" / "points")
    dx = dy = dz = 5.0e-6
    point_alpha = []
    point_solidification_time = []
    point_pressure = []
    for x, y, z in points:
        touches_occupied_cell = False
        for x_offset in (-0.5 * dx, 0.5 * dx):
            for y_offset in (-0.5 * dy, 0.5 * dy):
                for z_offset in (-0.5 * dz, 0.5 * dz):
                    if _inside_manufactured_pool(x + x_offset, y + y_offset, z + z_offset):
                        touches_occupied_cell = True
                        break
                if touches_occupied_cell:
                    break
            if touches_occupied_cell:
                break
        point_is_material = touches_occupied_cell and not _is_prescribed_void_point(x, y, z)
        point_alpha.append(1.0 if point_is_material else 0.0)
        point_solidification_time.append(1.0e-4 if point_is_material else -1.0)
        point_pressure.append(0.0)

    cell_alpha = [1.0 if occupied else 0.0 for occupied in occupied_cells]
    cell_solidification_time = [1.0e-4 if occupied else -1.0 for occupied in occupied_cells]
    cell_pressure = [0.0 for _ in occupied_cells]

    # SimToPC's ParaView extractor thresholds point data, so the canonical
    # manufactured fields are point fields. Cell fields with explicit names are
    # kept only to make the prescribed cell-centre mask inspectable.
    (time_dir / "alpha.material").write_text(
        _scalar_field_text(
            "alpha.material",
            "[0 0 0 0 0 0 0]",
            point_alpha,
            field_class="pointScalarField",
        )
    )
    (time_dir / "solidificationTime").write_text(
        _scalar_field_text(
            "solidificationTime",
            "[0 0 1 0 0 0 0]",
            point_solidification_time,
            field_class="pointScalarField",
        )
    )
    (time_dir / "p").write_text(
        _scalar_field_text("p", "[1 -1 -2 0 0 0 0]", point_pressure, field_class="pointScalarField")
    )
    (time_dir / "cellAlpha.material").write_text(
        _scalar_field_text("cellAlpha.material", "[0 0 0 0 0 0 0]", cell_alpha)
    )
    (time_dir / "cellSolidificationTime").write_text(
        _scalar_field_text("cellSolidificationTime", "[0 0 1 0 0 0 0]", cell_solidification_time)
    )
    (time_dir / "cellP").write_text(
        _scalar_field_text("cellP", "[1 -1 -2 0 0 0 0]", cell_pressure)
    )


def _write_measure_config(work_dir: Path) -> None:
    (work_dir / "parameters.txt").write_text(
        "laser_power scanning_speed laser_diameter\n"
        "100 1.0 40e-6\n"
    )
    (work_dir / "config.yml").write_text(
        f"""
mesh_density: MANUFACTURED
parameters_file: parameters.txt
output_dir: results
running_on: local

environment:
  of_location: "{OPENFOAM_BASHRC}"

measure:
  y_begin: 25e-6
  y_end: 275e-6
  x_min: 0
  x_max: 200e-6
  cell_size: 5e-6
  min_points_per_zrow: 2
"""
    )


@pytest.mark.skipif(
    not OPENFOAM_BASHRC,
    reason="Set SIMTOPC_OPENFOAM_BASHRC to run the manufactured OpenFOAM case test.",
)
def test_measure_recovers_manufactured_openfoam_meltpool(tmp_path, monkeypatch):
    work_dir = tmp_path / "manufactured_openfoam"
    case_dir = work_dir / "MANUFACTURED" / "test_case_1"
    case_dir.mkdir(parents=True)
    _write_minimal_case(case_dir)
    _write_manufactured_fields(case_dir)
    _write_measure_config(work_dir)

    monkeypatch.chdir(work_dir)
    run_measure("config.yml")

    assert load(case_dir / "measure_aux" / "continuous.joblib") is True

    cross_sections = pd.read_csv(case_dir / "measure_results" / "cross_sections_statistics.csv")
    row_statistics = pd.read_csv(case_dir / "measure_results" / "row_statistics.csv")

    for y_coord, (expected_width, expected_height, expected_depth) in REPRESENTATIVE_SECTIONS.items():
        section = cross_sections[cross_sections["iy"].sub(y_coord).abs() < 1.0e-12].iloc[0]
        assert section["width"] == pytest.approx(expected_width)
        assert section["height"] == pytest.approx(expected_height)
        assert section["depth"] == pytest.approx(expected_depth)
        assert section["porosity_at_iy"] == pytest.approx(0.0)

    assert cross_sections["porosity_at_iy"].max() == pytest.approx(0.0)
    assert not row_statistics["row_has_pores"].any()
