from __future__ import annotations

import numpy as np
import pytest

from cell_case_helpers import (DILIP, load_module, make_case, write_blockmesh,
                               write_scalar_field, write_uniform_field)
from simtopc.measure.cells import (AxesConfig, last_time_dir, read_blockmesh_geometry,
                                   read_cell_grid, read_scalar_field)
from simtopc.measure.main import build_measure_config


H = 5e-6
BASE = {"y_begin": 1e-4, "y_end": 2e-4, "x_min": 0.0, "x_max": 1e-4, "cell_size": H}


def _fields(shape=(4, 3, 2), seed=0):
    rng = np.random.default_rng(seed)
    mh = (rng.random(shape) > 0.5).astype(float)
    am = rng.random(shape)
    st = rng.random(shape) * 1e-3
    return {"meltHistory": mh, "alpha.metal": am, "solidificationTime": st}


# ------------------------------------------------------------------ field files

def test_read_scalar_field_nonuniform(tmp_path):
    write_scalar_field(tmp_path / "f", [1.5, -2.0, 3e-7], "f")
    np.testing.assert_array_equal(read_scalar_field(tmp_path / "f"), [1.5, -2.0, 3e-7])


def test_read_scalar_field_uniform_needs_cell_count(tmp_path):
    write_uniform_field(tmp_path / "f", 0.25, "f")
    np.testing.assert_array_equal(read_scalar_field(tmp_path / "f", 3), [0.25] * 3)
    with pytest.raises(ValueError, match="number of cells"):
        read_scalar_field(tmp_path / "f")


def test_read_scalar_field_rejects_wrong_count_and_binary(tmp_path):
    write_scalar_field(tmp_path / "f", [1, 2, 3], "f")
    with pytest.raises(ValueError, match="has 3 cells"):
        read_scalar_field(tmp_path / "f", 4)
    text = (tmp_path / "f").read_text().replace("format ascii;", "format binary;")
    (tmp_path / "g").write_text(text)
    with pytest.raises(ValueError, match="binary"):
        read_scalar_field(tmp_path / "g")


def test_last_time_dir_skips_zero_and_non_times(tmp_path):
    for name in ("0", "1e-05", "0.0002", "constant", "system", "measure_aux", "3e-06"):
        (tmp_path / name).mkdir()
    assert last_time_dir(tmp_path).name == "0.0002"
    empty = tmp_path / "empty"
    (empty / "0").mkdir(parents=True)
    with pytest.raises(FileNotFoundError):
        last_time_dir(empty)


# ------------------------------------------------------------------ geometry

def test_blockmesh_geometry_parses_scale_and_comments(tmp_path):
    write_blockmesh(tmp_path, (4, 3, 2), H, origin=(1e-5, 0, -1e-5), keyword="scale")
    n, lower, upper = read_blockmesh_geometry(tmp_path)
    assert n == (4, 3, 2)
    np.testing.assert_allclose(lower, [1e-5, 0, -1e-5])
    np.testing.assert_allclose(upper, [1e-5 + 4 * H, 3 * H, -1e-5 + 2 * H])


def test_blockmesh_rejects_grading(tmp_path):
    write_blockmesh(tmp_path, (4, 3, 2), H, grading="1 2 1")
    with pytest.raises(ValueError, match="graded"):
        read_blockmesh_geometry(tmp_path)


@pytest.mark.parametrize("track,vertical", [("y", "z"), ("z", "y"), ("x", "z"), ("z", "x")])
def test_blockmesh_layout_follows_axes(tmp_path, track, vertical):
    f = _fields()
    case = make_case(tmp_path / "c", f, H, origin=(1e-5, 2e-5, 3e-5))
    axes = AxesConfig(track=track, vertical=vertical)
    g = read_cell_grid(case, axes=axes, cell_size=H, geometry="blockmesh")
    pos = {"z": 0, "y": 1, "x": 2}
    expected = np.transpose(f["meltHistory"], [pos[a] for a in axes.order])
    np.testing.assert_array_equal(g.melt, expected)
    np.testing.assert_array_equal(g.metal, np.transpose(f["alpha.metal"], [pos[a] for a in axes.order]))
    origin = {"x": 1e-5, "y": 2e-5, "z": 3e-5}
    np.testing.assert_allclose(g.origin, [origin[a] for a in axes.order])
    assert g.cell_size == pytest.approx(H)
    assert g.time == "0.001"


@pytest.mark.parametrize("track,vertical", [("y", "z"), ("z", "y")])
def test_cell_centres_layout_equals_blockmesh_layout(tmp_path, track, vertical):
    f = _fields(shape=(5, 4, 3), seed=1)
    axes = AxesConfig(track=track, vertical=vertical)
    a = read_cell_grid(make_case(tmp_path / "a", f, H), axes=axes, cell_size=H, geometry="blockmesh")
    b = read_cell_grid(make_case(tmp_path / "b", f, H, cell_centres=True, shuffle_seed=3),
                       axes=axes, cell_size=H)          # auto: cell centres present
    for name in ("melt", "metal", "solidification_time"):
        np.testing.assert_array_equal(getattr(a, name), getattr(b, name))
    np.testing.assert_allclose(a.origin, b.origin, atol=1e-15)


def test_grid_masks_and_coordinates(tmp_path):
    f = _fields()
    g = read_cell_grid(make_case(tmp_path / "c", f, H), axes=AxesConfig("z", "y"), cell_size=H)
    np.testing.assert_array_equal(g.melted(), f["meltHistory"] > 0)
    np.testing.assert_array_equal(g.is_metal(), f["alpha.metal"] >= 0.5)
    np.testing.assert_allclose(g.centres(0), (np.arange(4) + 0.5) * H)
    np.testing.assert_allclose(g.faces(1), np.arange(3) * H)
    assert g.to_case_coordinates(1.0, 2.0, 3.0) == {"x": 3.0, "y": 2.0, "z": 1.0}


def test_solidification_time_optional_unless_needed(tmp_path):
    f = _fields()
    del f["solidificationTime"]
    case = make_case(tmp_path / "c", f, H)
    assert read_cell_grid(case, cell_size=H).solidification_time is None
    with pytest.raises(FileNotFoundError, match="solidificationTime"):
        read_cell_grid(case, cell_size=H, need_solidification_time=True)


def test_reader_rejects_cell_size_mismatch_and_remapped_mesh(tmp_path):
    case = make_case(tmp_path / "c", _fields(), H)
    with pytest.raises(ValueError, match="differs"):
        read_cell_grid(case, cell_size=2 * H, geometry="blockmesh")
    (case / "constant" / "polyMesh").mkdir(parents=True)
    (case / "constant" / "polyMesh" / "points").write_text(
        f"3\n(\n(0 0 0)\n(1e-6 0 0)\n({2 * H!r} {2 * H!r} {3 * H!r})\n)\n")   # not the corner of the 2x3x4 box
    with pytest.raises(ValueError, match="remapped"):
        read_cell_grid(case, cell_size=H, geometry="blockmesh")
    (case / "constant" / "polyMesh" / "points").write_text(
        f"3\n(\n(0 0 0)\n(1e-6 0 0)\n({2 * H!r} {3 * H!r} {4 * H!r})\n)\n")
    read_cell_grid(case, cell_size=H, geometry="blockmesh")


def test_cell_centres_reject_incomplete_or_non_uniform_mesh(tmp_path):
    f = _fields()
    case = make_case(tmp_path / "c", f, H, cell_centres=True)
    t = case / "0.001"
    cx = read_scalar_field(t / "Cx")
    cx[0] += 0.3 * H
    write_scalar_field(t / "Cx", cx, "Cx")
    with pytest.raises(ValueError, match="uniform grid"):
        read_cell_grid(case, cell_size=H)
    for name in ("Cx", "Cy", "Cz", "meltHistory", "alpha.metal", "solidificationTime"):
        v = read_scalar_field(t / name)
        if name == "Cx":
            v[0] -= 0.3 * H
        write_scalar_field(t / name, v[1:], name)                    # one cell missing
    with pytest.raises(ValueError, match="do not fill"):
        read_cell_grid(case, cell_size=H)


def test_cell_centres_need_cell_size(tmp_path):
    case = make_case(tmp_path / "c", _fields(), H, cell_centres=True)
    with pytest.raises(ValueError, match="cell_size"):
        read_cell_grid(case, geometry="cell_centres")


def test_custom_field_names(tmp_path):
    f = _fields()
    case = make_case(tmp_path / "c", {"mh2": f["meltHistory"], "alpha.material": f["alpha.metal"]}, H)
    g = read_cell_grid(case, melt_field="mh2", metal_field="alpha.material", cell_size=H)
    np.testing.assert_array_equal(g.metal, np.transpose(f["alpha.metal"], (1, 0, 2)))


# ------------------------------------------------------------------ configuration

def test_config_defaults_keep_current_behaviour():
    cfg = build_measure_config(dict(BASE))
    assert cfg.axes == AxesConfig("y", "z")
    assert cfg.axes.lateral == "x"
    assert (cfg.melt_field, cfg.metal_field) == ("meltHistory", "alpha.metal")
    assert cfg.extraction_mode == "point_fields"


def test_config_axes_mapping():
    cfg = build_measure_config({**BASE, "axes": {"track": "Z", "vertical": "y"},
                                "geometry_mode": "metallographic", "substrate_top": 3e-4})
    assert cfg.axes.order == ("z", "y", "x")


@pytest.mark.parametrize("axes,message", [
    ({"track": "y", "vertical": "y"}, "must differ"),
    ({"track": "w"}, "one of x, y, z"),
    ({"track": "z", "lateral": "x"}, "only the keys"),
    ("z", "must be a mapping"),
])
def test_config_axes_invalid(axes, message):
    with pytest.raises(ValueError, match=message):
        build_measure_config({**BASE, "axes": axes})


def test_config_field_names_must_not_be_empty():
    with pytest.raises(ValueError, match="measure.melt_field"):
        build_measure_config({**BASE, "melt_field": " "})


# ------------------------------------------------------------------ reference (real run)

DILIP_RUN = DILIP / "runs" / "P195_v1200"


@pytest.mark.skipif(not (DILIP_RUN / "VIRGIN_CASE.json").exists(), reason="Dilip run data not available")
def test_reader_reproduces_dilip_reference_arrays():
    dt = load_module("dilip_tools_ref", DILIP / "dilip_tools.py")
    ref = dt.load(DILIP_RUN)
    g = read_cell_grid(DILIP_RUN, axes=AxesConfig(track="z", vertical="y"), cell_size=5e-6)
    assert g.time == ref["time"]
    np.testing.assert_array_equal(g.melted(), ref["melted"])
    np.testing.assert_array_equal(g.metal, ref["alpha"])
    np.testing.assert_array_equal(g.solidification_time, ref["st"])
    assert g.cell_size * 1e6 == pytest.approx(ref["h"], rel=1e-12)
