from __future__ import annotations


import numpy as np
import pandas as pd
import pytest
from joblib import load

from cell_case_helpers import make_case
from simtopc.measure.cells import AxesConfig, read_cell_grid
from simtopc.measure.legacy_funcs import _evaluate_section_row
from simtopc.measure.main import build_measure_config, run as run_measure
from simtopc.measure.metallographic import (lateral_cells, measure_section, measure_sections,
                                            row_voids, sections_in_window, substrate_row)


H = 5e-6
BASE = {"y_begin": 1e-4, "y_end": 2e-4, "x_min": 0.0, "x_max": 1e-4, "cell_size": H}


def _section():
    """(vertical, lateral) section of 10 x 9 cells, substrate top at row 6 (30 um)."""
    melted = np.zeros((10, 9), bool)
    metal = np.zeros((10, 9), bool)
    metal[:6] = True                       # substrate
    melted[3:6, 2:7] = True                # fusion zone: rows 3-5, cells 2-6 in the top row
    melted[5, 1] = True                    # top substrate row: cells 1-6 -> 6 cells wide
    melted[6:8, 3:6] = True                # bead above the substrate top
    metal[6:8, 3:6] = True
    metal[6, 4] = False                    # a gas cell inside the bead
    melted[9, 4] = True                    # melted powder at row 9, gas now (not metal)
    return melted, metal


def test_measure_section_definitions():
    melted, metal = _section()
    r = measure_section(melted, metal, jt=5, h=H, v0=0.0, substrate_top=30e-6, track=1e-4)
    assert r.width == pytest.approx(6 * H)                  # cells 1..6 of the top substrate row
    assert r.depth == pytest.approx(30e-6 - 3 * H)          # bottom face of row 3
    assert r.height == pytest.approx(8 * H - 30e-6)         # top face of row 7 (row 9 is not metal)
    assert r.fused
    assert r.void_cells == 1                                # the gas cell between bead cells
    assert r.solid_cells == int((melted & metal).sum())


def test_measure_section_ignores_gaps_below_the_top_bead_cell():
    melted, metal = _section()
    melted[9, 4] = metal[9, 4] = True      # a consolidated cell above a gap (row 8 empty)
    r = measure_section(melted, metal, jt=5, h=H, v0=0.0, substrate_top=30e-6, track=0.0)
    assert r.height == pytest.approx(10 * H - 30e-6)


def test_measure_section_unfused_and_empty():
    melted = np.zeros((10, 9), bool)
    metal = np.zeros((10, 9), bool)
    melted[8, 4] = metal[8, 4] = True      # a melted droplet above the substrate only
    r = measure_section(melted, metal, jt=5, h=H, v0=0.0, substrate_top=30e-6, track=0.0)
    assert not r.fused and r.width == 0.0
    assert r.depth == pytest.approx(30e-6 - 8 * H)          # negative: above the substrate top
    r = measure_section(np.zeros((10, 9), bool), metal, jt=5, h=H, v0=0.0, substrate_top=30e-6, track=0.0)
    assert not r.fused and r.depth == 0.0 and np.isnan(r.height) and r.width == 0.0


def test_height_negative_for_a_depression():
    melted = np.zeros((10, 9), bool)
    metal = np.zeros((10, 9), bool)
    metal[:5] = True
    melted[3:6, 2:6] = True                # row 5 melted but gas now: a depression
    r = measure_section(melted, metal, jt=5, h=H, v0=0.0, substrate_top=30e-6, track=0.0)
    assert r.height == pytest.approx(5 * H - 30e-6)


def test_row_voids_equals_the_single_track_row_count():
    rng = np.random.default_rng(4)
    section = rng.random((6, 12)) > 0.4
    voids, solid = row_voids(section)
    exp_voids = exp_solid = 0
    for j, row in enumerate(section):
        x = np.nonzero(row)[0] * H
        if not x.size:
            continue
        cells = pd.DataFrame({"Points_0": x, "Points_1": 0.0, "Points_2": j * H})
        r = _evaluate_section_row(cells, cells["Points_0"].to_numpy(), cells["Points_2"].to_numpy(),
                                  j * H, H, coordinate_mode="cell_centres")
        exp_voids += r.n_pores
        exp_solid += r.number_non_void_cells
    assert (voids, solid) == (exp_voids, exp_solid)


def _grid(tmp_path, origin=(0.0, 0.0, 0.0)):
    """A case with track along z (8 sections), vertical y (10 rows), lateral x (9 cells)."""
    melted, metal = _section()
    mh = np.repeat(melted[None], 8, axis=0).astype(float)
    am = np.repeat(metal[None], 8, axis=0).astype(float)
    mh[2] = 0.0                            # section 2 not melted
    case = make_case(tmp_path / "c", {"meltHistory": mh, "alpha.metal": am}, H, origin=origin)
    return read_cell_grid(case, axes=AxesConfig("z", "y"), cell_size=H)


def test_window_lateral_and_substrate_row(tmp_path):
    g = _grid(tmp_path, origin=(0.0, -10e-6, 0.0))
    np.testing.assert_array_equal(sections_in_window(g, 7.5e-6, 22.5e-6), [1, 2, 3, 4])
    np.testing.assert_array_equal(sections_in_window(g, 7.6e-6, 22.4e-6), [2, 3])
    np.testing.assert_array_equal(lateral_cells(g, 10e-6, 22.5e-6), [False, False, True, True, True] + [False] * 4)
    assert substrate_row(g, 20e-6) == 5                     # origin -10 um: 30 um of cells
    with pytest.raises(ValueError, match="not on a cell face"):
        substrate_row(g, 21e-6)
    with pytest.raises(ValueError, match="outside the mesh"):
        substrate_row(g, 200e-6)


def test_measure_sections_with_lateral_restriction(tmp_path):
    g = _grid(tmp_path)
    full = measure_sections(g, [0, 2], 30e-6)
    assert full[0].width == pytest.approx(6 * H) and full[0].fused
    assert not full[1].fused
    part = measure_sections(g, [0], 30e-6, lateral_cells(g, 0.0, 22.5e-6))   # cells 0..4
    assert part[0].width == pytest.approx(4 * H)


def _write_run(root, case_fields, h=H, config_extra=""):
    case = make_case(root / "cases" / "test_case_1", case_fields, h)
    (root / "parameters.txt").write_text("# v P spot\n 1.0 100 1e-5\n")
    (root / "config.yml").write_text(
        "mesh_density: cases\nparameters_file: parameters.txt\noutput_dir: results\n"
        "running_on: local\nmeasure:\n  y_begin: 0\n  y_end: 40e-6\n  x_min: 0\n  x_max: 45e-6\n"
        f"  cell_size: {h!r}\n  geometry_mode: metallographic\n  axes: {{track: z, vertical: y}}\n"
        f"  substrate_top: 30e-6\n{config_extra}")
    return case


def test_metallographic_end_to_end(tmp_path):
    melted, metal = _section()
    mh = np.repeat(melted[None], 8, axis=0).astype(float)
    am = np.repeat(metal[None], 8, axis=0).astype(float)
    case = _write_run(tmp_path, {"meltHistory": mh, "alpha.metal": am})
    run_measure(tmp_path / "config.yml")
    stats = pd.read_csv(case / "measure_results" / "cross_sections_statistics.csv")
    assert list(stats.columns) == ["iy", "width", "height", "depth", "porosity_at_iy",
                                   "total_volume_material_at_iy"]
    np.testing.assert_allclose(stats["iy"], (np.arange(8) + 0.5) * H)
    np.testing.assert_allclose(stats["width"], 6 * H)
    np.testing.assert_allclose(stats["depth"], 15e-6)
    np.testing.assert_allclose(stats["height"], 10e-6)
    solid = int((melted & metal).sum())
    np.testing.assert_allclose(stats["porosity_at_iy"], 1 / (solid + 1))
    np.testing.assert_allclose(stats["total_volume_material_at_iy"], (solid + 1) * H**3)
    assert load(case / "measure_aux" / "continuous.joblib") is True
    assert (case / "measure_results" / "Width.png").exists()
    sections = pd.read_csv(case / "measure_results" / "metallographic_sections.csv")
    assert sections["fused"].all() and list(sections["section"]) == list(range(8))


def test_metallographic_reports_discontinuity(tmp_path):
    melted, metal = _section()
    mh = np.repeat(melted[None], 8, axis=0).astype(float)
    am = np.repeat(metal[None], 8, axis=0).astype(float)
    mh[3, :6] = 0.0                        # section 3: no fusion into the substrate
    case = _write_run(tmp_path, {"meltHistory": mh, "alpha.metal": am})
    run_measure(tmp_path / "config.yml")
    assert load(case / "measure_aux" / "continuous.joblib") is False
    np.testing.assert_allclose(load(case / "measure_aux" / "void_iy_levels.joblib"), [17.5e-6])


def test_metallographic_empty_window_is_an_error(tmp_path):
    melted, metal = _section()
    mh = np.repeat(melted[None], 8, axis=0).astype(float)
    _write_run(tmp_path, {"meltHistory": mh, "alpha.metal": mh}, config_extra="")
    text = (tmp_path / "config.yml").read_text().replace("y_begin: 0", "y_begin: 100e-6").replace(
        "y_end: 40e-6", "y_end: 200e-6")
    (tmp_path / "config.yml").write_text(text)
    with pytest.raises(ValueError, match="No cross-section"):
        run_measure(tmp_path / "config.yml")


# ------------------------------------------------------------------ configuration

def test_config_geometry_mode_default_and_values():
    assert build_measure_config(dict(BASE)).geometry_mode == "single_track"
    cfg = build_measure_config({**BASE, "geometry_mode": "metallographic", "substrate_top": "300e-6",
                                "axes": {"track": "z", "vertical": "y"}})
    assert cfg.geometry_mode == "metallographic" and cfg.substrate_top == pytest.approx(3e-4)


@pytest.mark.parametrize("extra,message", [
    ({"geometry_mode": "cross_section"}, "geometry_mode must be one of"),
    ({"geometry_mode": "metallographic"}, "substrate_top"),
    ({"geometry_mode": "metallographic", "substrate_top": "abc"}, "substrate_top must be numeric"),
    ({"axes": {"track": "z", "vertical": "y"}}, "single_track measures the point cloud"),
])
def test_config_geometry_mode_invalid(extra, message):
    with pytest.raises(ValueError, match=message):
        build_measure_config({**BASE, **extra})


# ------------------------------------------------------------------ reference (real runs)
# The comparison with real runs is tests/test_metallographic_validation.py (the four case D runs
# of bed2_gprops_mid_tall against tall_profiles.py and measure_tall.json). The earlier comparison
# with compare.py on the P195_v1200 runs (powder bed later rejected, width without the lower-row
# rule and depth to the lowest melted cell even if gas) was removed with the 2026-11-24 rules.
