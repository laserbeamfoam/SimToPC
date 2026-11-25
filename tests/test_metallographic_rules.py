"""Rules of the metallographic mode (2026-11-24): the width at the substrate top taken lower
when its edge cells ended as gas, the depth to the lowest melted-metal cell, the fill and the
centreline surface, the steady stretch, the window of each scan speed and the track reference."""
from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from cell_case_helpers import make_case
from simtopc.measure.main import build_measure_config, run as run_measure
from simtopc.measure.metallographic import (fusion_width, laser_start_from_case, measure_section,
                                            speed_window, steady_stretch)

H = 5e-6
BASE = {"y_begin": 0.0, "y_end": 1e-4, "x_min": 0.0, "x_max": 1e-4, "cell_size": H,
        "geometry_mode": "metallographic", "axes": {"track": "z", "vertical": "y"},
        "substrate_top": 30e-6}


def _pool():
    """(vertical, lateral) section of 10 x 11 cells, substrate top at row 6 (jt = 5): a fusion
    zone of rows 2-5, cells 2-8 wide in the top substrate row; all of it metal."""
    melted = np.zeros((10, 11), bool)
    metal = np.zeros((10, 11), bool)
    metal[:6] = True
    for j, (a, b) in zip(range(2, 6), ((4, 6), (3, 7), (2, 8), (2, 8))):
        melted[j, a:b + 1] = True
    return melted, metal


# ------------------------------------------------------------------ width

def test_width_at_the_substrate_top_row():
    melted, metal = _pool()
    assert fusion_width(melted, metal, 5, H) == (pytest.approx(7 * H), 0)


def test_width_one_row_lower_when_an_edge_ended_as_gas():
    melted, metal = _pool()
    metal[5, 2] = False                                  # the left edge of the top row is gas now
    assert fusion_width(melted, metal, 5, H) == (pytest.approx(7 * H), 1)   # row 4: cells 2-8
    metal[4, 8] = False                                  # and the right edge of row 4
    assert fusion_width(melted, metal, 5, H) == (pytest.approx(5 * H), 2)   # row 3: cells 3-7


def test_width_not_measured_beyond_the_rows_allowed():
    melted, metal = _pool()
    metal[5, 2] = metal[4, 8] = metal[3, 3] = False
    w, down = fusion_width(melted, metal, 5, H)
    assert np.isnan(w) and down == -1
    w, down = fusion_width(melted, metal, 5, H, max_rows_down=3)           # row 2: cells 4-6
    assert w == pytest.approx(3 * H) and down == 3
    melted0, metal0 = _pool()
    metal0[5, 8] = False
    w, down = fusion_width(melted0, metal0, 5, H, max_rows_down=0)
    assert np.isnan(w) and down == -1


def test_width_zero_without_melted_cells_in_the_top_row():
    melted, metal = _pool()
    melted[5] = False
    assert fusion_width(melted, metal, 5, H) == (0.0, 0)


def test_interior_gas_cells_do_not_change_the_width():
    melted, metal = _pool()
    metal[5, 4:6] = False                                # gas inside the extent, edges metal
    assert fusion_width(melted, metal, 5, H) == (pytest.approx(7 * H), 0)


# ------------------------------------------------------------------ depth, fill, surface

def test_depth_to_the_lowest_melted_metal_cell():
    melted, metal = _pool()
    r = measure_section(melted, metal, 5, H, 0.0, 30e-6, 0.0)
    assert r.depth == pytest.approx(30e-6 - 2 * H)
    metal[2] = False                                     # the lowest melted row ended as gas
    r = measure_section(melted, metal, 5, H, 0.0, 30e-6, 0.0)
    assert r.depth == pytest.approx(30e-6 - 3 * H)


def test_fill_is_the_metal_fraction_of_the_fusion_zone():
    melted, metal = _pool()
    alpha = metal.astype(float)
    alpha[5, 2:9] = 0.5                                  # the top row half full
    alpha[2, 5] = 1.7                                    # clipped to 1
    r = measure_section(melted, alpha >= 0.5, 5, H, 0.0, 30e-6, 0.0, alpha=alpha)
    n = int(melted[:6].sum())
    assert r.fill == pytest.approx((n - 7 + 7 * 0.5) / n)


def test_surface_is_the_centreline_metal_height():
    melted, metal = _pool()
    alpha = metal.astype(float)
    alpha[6, 4:7] = [1.0, 0.4, 0.7]                      # a bead row above the substrate top
    r = measure_section(melted, metal, 5, H, 0.0, 30e-6, 0.0, alpha=alpha, centre=5)
    assert r.surface == pytest.approx(np.mean([1.0, 0.4, 0.7]) * H)
    r = measure_section(melted, metal, 5, H, 0.0, 30e-6, 0.0, alpha=alpha)   # centre = 11 // 2
    assert r.surface == pytest.approx(np.mean([1.0, 0.4, 0.7]) * H)
    assert np.isnan(measure_section(melted, metal, 5, H, 0.0, 30e-6, 0.0).fill)


# ------------------------------------------------------------------ steady stretch and window

def _profile(n=100, h=H):
    track = (np.arange(n) + 0.5) * h
    width = np.full(n, 140e-6)
    depth = np.full(n, 60e-6)
    width[:30] = 160e-6                                  # start transient
    depth[85:] = 40e-6                                   # end of the track
    width[50] = np.nan                                   # one unmeasured section: filtered out
    return track, width, depth


def test_steady_stretch_is_the_longest_flat_stretch():
    track, width, depth = _profile()
    k0, k1 = steady_stretch(track, width, depth, H, 0.0, 1.0, filter_length=25e-6)
    assert (k0, k1) == (30, 84)                          # a running median keeps the steps where they are


def test_steady_stretch_respects_the_tolerance_and_range():
    track, width, depth = _profile()
    width[:30] = 144e-6                                  # within 5 um: no transient
    k0, k1 = steady_stretch(track, width, depth, H, 0.0, 1.0, filter_length=25e-6)
    assert k0 == 0
    k0, k1 = steady_stretch(track, width, depth, H, 20 * H, 70 * H, filter_length=25e-6)
    assert (k0, k1) == (20, 69)


def test_speed_window():
    assert speed_window([292e-6, 498e-6], [1.2e-3, 1.22e-3]) == pytest.approx((550e-6, 950e-6))
    assert speed_window([435e-6], [1.1e-3]) == pytest.approx((500e-6, 900e-6))
    assert speed_window([450e-6], [1.1e-3]) == pytest.approx((500e-6, 900e-6))   # exact multiple
    with pytest.raises(ValueError, match="ends outside"):
        speed_window([500e-6], [0.9e-3])
    with pytest.raises(ValueError, match="No case"):
        speed_window([], [])


def test_laser_start_from_case(tmp_path):
    (tmp_path / "constant").mkdir()
    (tmp_path / "constant" / "timeVsLaserPosition").write_text(
        "(\n    (0 (0.00015 2e-05 0.0003))\n    (0.0012 (0.00015 2e-05 0.0015))\n)\n")
    assert laser_start_from_case(tmp_path, "z") == pytest.approx(3e-4)
    assert laser_start_from_case(tmp_path, "x") == pytest.approx(1.5e-4)
    with pytest.raises(FileNotFoundError):
        laser_start_from_case(tmp_path / "missing", "z")


# ------------------------------------------------------------------ configuration

def test_config_defaults_and_auto_cell_size():
    cfg = build_measure_config(dict(BASE))
    assert (cfg.window_mode, cfg.track_reference, cfg.width_max_rows_down) == ("fixed", "case", 2)
    cfg = build_measure_config({**BASE, "cell_size": "auto", "window_mode": "steady_stretch",
                                "track_reference": "laser_start", "width_max_rows_down": 1})
    assert cfg.cell_size is None and cfg.window_mode == "steady_stretch" and cfg.width_max_rows_down == 1


@pytest.mark.parametrize("extra,message", [
    ({"window_mode": "auto"}, "window_mode"),
    ({"track_reference": "start"}, "track_reference"),
    ({"width_max_rows_down": -1}, "width_max_rows_down"),
    ({"window_length": 0}, "window_length"),
    ({"geometry_mode": "single_track", "axes": {"track": "y", "vertical": "z"}, "cell_size": "auto"}, "auto"),
    ({"geometry_mode": "single_track", "axes": {"track": "y", "vertical": "z"},
      "window_mode": "steady_stretch"}, "options of measure.geometry_mode metallographic"),
])
def test_config_invalid(extra, message):
    with pytest.raises(ValueError, match=message):
        build_measure_config({**BASE, **extra})


# ------------------------------------------------------------------ end to end: two speeds, shifted tracks

def _track_case(case, start, n=60, transient=12, h=H):
    """A uniform track along z (n sections) starting at `start`: width 7 cells and depth 4 cells
    after a wider start transient of `transient` sections; the laser starts at `start`."""
    melted, metal = _pool()
    mh = np.repeat(melted[None], n, axis=0).astype(float)
    am = np.repeat(metal[None], n, axis=0).astype(float)
    mh[:transient, 5, 1:10] = 1.0                        # 9 cells wide at the start
    make_case(case, {"meltHistory": mh, "alpha.metal": am}, h)
    (case / "constant" / "timeVsLaserPosition").write_text(
        f"(\n    (0 (2.5e-05 3e-05 {start!r}))\n    (0.001 (2.5e-05 3e-05 {start + 2e-4!r}))\n)\n")


def test_steady_stretch_windows_end_to_end(tmp_path):
    cases = tmp_path / "cases"
    _track_case(cases / "test_case_1", 0.0, transient=12)
    _track_case(cases / "test_case_2", 50e-6, transient=22)          # its track starts 10 cells later
    _track_case(cases / "test_case_3", 0.0, transient=12)
    (tmp_path / "parameters.txt").write_text("# v P spot\n 1.0 100 1e-5\n 1.0 100 1e-5\n 0.5 100 1e-5\n")
    (tmp_path / "config.yml").write_text(
        "mesh_density: cases\nparameters_file: parameters.txt\noutput_dir: results\nrunning_on: local\n"
        "measure:\n  y_begin: 0\n  y_end: 300e-6\n  x_min: 0\n  x_max: 55e-6\n  cell_size: auto\n"
        "  geometry_mode: metallographic\n  axes: {track: z, vertical: y}\n  substrate_top: 30e-6\n"
        "  window_mode: steady_stretch\n  track_reference: laser_start\n"
        "  steady_filter_length: 15e-6\n  window_margin: 10e-6\n  window_length: 50e-6\n  window_step: 10e-6\n")
    run_measure(tmp_path / "config.yml")
    s = pd.read_csv(tmp_path / "metallographic_summary.csv").set_index("case")
    # speed 1.0: the transients end 12 sections after the laser start in both cases (case 2: 22
    # cells from the mesh start, 10 of them before its laser start), so the steady stretches start
    # at 62.5 um from the laser start: window from 62.5 + 10 um rounded up to 80 um
    assert s.loc["test_case_1", "window_begin"] == pytest.approx(80e-6)
    assert s.loc["test_case_2", "window_begin"] == pytest.approx(80e-6)
    assert s.loc["test_case_3", "window_begin"] == pytest.approx(80e-6)       # speed 0.5: its own window
    assert (s["sections"] == 10).all()
    np.testing.assert_allclose(s["width_mean"], 7 * H)
    np.testing.assert_allclose(s["depth_mean"], 30e-6 - 2 * H)
    assert (s["width_sections_one_row_lower"] == 0).all() and s["continuous"].all()
    np.testing.assert_allclose(s["fill_mean"], 1.0)
    prof = pd.read_csv(cases / "test_case_2" / "measure_results" / "metallographic_profile.csv")
    assert prof["in_window"].sum() == 10 and prof["steady_stretch"].any()
    np.testing.assert_allclose(prof.loc[prof["in_window"], "track_from_reference"].min(), 82.5e-6)


def test_example_caseD_config_is_valid():
    from pathlib import Path
    from simtopc.config import load_config
    example = Path(__file__).resolve().parents[1] / "examples" / "measure_metallographic_caseD"
    cfg = build_measure_config(load_config(str(example / "config.yml")).measure)
    assert cfg.window_mode == "steady_stretch" and cfg.track_reference == "laser_start"
    assert cfg.cell_size is None and cfg.substrate_top == pytest.approx(150e-6)
    assert np.loadtxt(example / "parameters.txt", skiprows=1).shape == (4, 3)


def test_metallographic_rejects_a_case_without_melt_history(tmp_path):
    """A laserMeltFoam case has no meltHistory: the metallographic mode stops with a clear error."""
    melted, metal = _pool()
    am = np.repeat(metal[None], 6, axis=0).astype(float)
    make_case(tmp_path / "cases" / "test_case_1", {"alpha.metal": am}, H)
    (tmp_path / "parameters.txt").write_text("# v P spot\n 1.0 100 1e-5\n")
    (tmp_path / "config.yml").write_text(
        "mesh_density: cases\nparameters_file: parameters.txt\noutput_dir: results\nrunning_on: local\n"
        "measure:\n  y_begin: 0\n  y_end: 30e-6\n  x_min: 0\n  x_max: 55e-6\n  cell_size: auto\n"
        "  geometry_mode: metallographic\n  axes: {track: z, vertical: y}\n  substrate_top: 30e-6\n")
    with pytest.raises(ValueError, match="laserbeamFoam cases.*laserMeltFoam"):
        run_measure(tmp_path / "config.yml")
