from __future__ import annotations

import json

import numpy as np
import pandas as pd
import pytest

from cell_case_helpers import DILIP, load_module, make_case
from simtopc.measure.cells import AxesConfig, CellGrid, read_cell_grid
from simtopc.measure.main import build_measure_config, run as run_measure
from simtopc.measure.metallographic import laser_off_time_from_case, steady_sections


H = 5e-6
BASE = {"y_begin": 1e-4, "y_end": 2e-4, "x_min": 0.0, "x_max": 1e-4, "cell_size": H}
T_OFF = 1.0e-3


def _fields(n_track=12):
    """Track z (n_track sections), vertical y (8 rows, substrate top at 20 um = 4 rows),
    lateral x (6). Section k solidifies at st[k] (all its melted cells)."""
    melt = np.zeros((n_track, 8, 6))
    melt[:, 2:6, 1:5] = 1.0
    metal = np.ones((n_track, 8, 6))
    metal[:, 6:, :] = 0.0
    st_section = np.full(n_track, 0.5e-3)
    st_section[[0, 1]] = 1.5e-3            # start: solidified after the switch-off
    st_section[7] = 1.2e-3                 # a late section breaks the run
    st_section[9:] = 2e-3                  # end pool
    st = melt * st_section[:, None, None]
    melt[5, :, :] = 0.0                    # section 5 not melted: NaN percentile, not steady
    st[5] = 0.0
    return {"meltHistory": melt, "alpha.metal": metal, "solidificationTime": st}


def _grid(f):
    return CellGrid(melt=f["meltHistory"], metal=f["alpha.metal"], solidification_time=f["solidificationTime"],
                    cell_size=H, origin=(0.0, 0.0, 0.0), axes=AxesConfig("z", "y"), time="1")


def test_steady_sections_contiguous_run_from_the_first():
    g = _grid(_fields())
    ks, p90 = steady_sections(g, np.arange(12), 20e-6, T_OFF)
    np.testing.assert_array_equal(ks, [2, 3, 4])           # 5 has no melted substrate cells
    assert np.isnan(p90[5]) and p90[2] == pytest.approx(0.5e-3)
    ks, _ = steady_sections(g, np.arange(6, 12), 20e-6, T_OFF)
    np.testing.assert_array_equal(ks, [6])                  # 7 breaks the run; 8 is not taken
    ks, _ = steady_sections(g, np.arange(9, 12), 20e-6, T_OFF)
    assert ks.size == 0


def test_steady_sections_use_the_90th_percentile_of_the_substrate_cells():
    f = _fields()
    st = f["solidificationTime"]
    st[3, 2, 1:5] = 1.4e-3                 # one late row of 4 of the 16 substrate cells
    st[3, 4:6, :] = 5e-3                   # cells above the substrate top do not count
    st[4, 2, 1] = 1.4e-3                   # one late cell of 16: the 90th percentile stays early
    ks, p90 = steady_sections(_grid(f), np.arange(12), 20e-6, T_OFF)
    np.testing.assert_array_equal(ks, [2])
    vals = np.r_[np.full(4, 1.4e-3), np.full(4, 0.5e-3)]
    assert p90[3] == pytest.approx(np.percentile(vals, 90))
    assert p90[4] < T_OFF


def test_steady_sections_need_solidification_time():
    f = _fields()
    g = CellGrid(melt=f["meltHistory"], metal=f["alpha.metal"], solidification_time=None, cell_size=H,
                 origin=(0.0, 0.0, 0.0), axes=AxesConfig("z", "y"), time="1")
    with pytest.raises(ValueError, match="solidificationTime"):
        steady_sections(g, np.arange(3), 20e-6, T_OFF)


def test_laser_off_time_from_case(tmp_path):
    (tmp_path / "constant").mkdir()
    (tmp_path / "constant" / "timeVsLaserPower").write_text(
        "(\n    (0 195)\n    (0.000666666667 195)\n    (0.000666667667 0)\n)\n")
    assert laser_off_time_from_case(tmp_path) == pytest.approx(0.000666666667, rel=0, abs=1e-18)
    (tmp_path / "constant" / "timeVsLaserPower").write_text("(\n (0 0)\n (1 0)\n)\n")
    with pytest.raises(ValueError, match="laser on"):
        laser_off_time_from_case(tmp_path)
    with pytest.raises(FileNotFoundError, match="laser_off_time"):
        laser_off_time_from_case(tmp_path / "missing")


def _write(root, f, extra, geometry="metallographic", cell_centres=False):
    case = make_case(root / "cases" / "test_case_1", f, H, cell_centres=cell_centres)
    (case / "constant" / "timeVsLaserPower").write_text(f"(\n (0 100)\n ({T_OFF!r} 100)\n (0.0011 0)\n)\n")
    (root / "parameters.txt").write_text("# v P spot\n 1.0 100 1e-5\n")
    axes = "{track: z, vertical: y}" if geometry == "metallographic" else "{track: y, vertical: z}"
    (root / "config.yml").write_text(
        "mesh_density: cases\nparameters_file: parameters.txt\noutput_dir: results\nrunning_on: local\n"
        "measure:\n  y_begin: 0\n  y_end: 60e-6\n  x_min: 0\n  x_max: 30e-6\n  cell_size: 5e-6\n"
        f"  geometry_mode: {geometry}\n  axes: {axes}\n  substrate_top: 20e-6\n  steady_sections: true\n{extra}")
    return case


def test_metallographic_steady_sections_end_to_end(tmp_path):
    case = _write(tmp_path, _fields(), "")
    run_measure(tmp_path / "config.yml")
    res = case / "measure_results"
    stats = pd.read_csv(res / "cross_sections_statistics.csv")
    np.testing.assert_allclose(stats["iy"], (np.array([2, 3, 4]) + 0.5) * H)
    steady = pd.read_csv(res / "steady_sections.csv")
    assert len(steady) == 12 and list(steady["section"][steady["steady"]]) == [2, 3, 4]


def test_laser_off_time_key_overrides_the_case(tmp_path):
    case = _write(tmp_path, _fields(), "  laser_off_time: 1.3e-3\n")       # 7 (1.2 ms) is now steady
    run_measure(tmp_path / "config.yml")
    stats = pd.read_csv(case / "measure_results" / "cross_sections_statistics.csv")
    np.testing.assert_allclose(stats["iy"], (np.array([2, 3, 4]) + 0.5) * H)   # 5 still breaks the run
    case2 = _write(tmp_path / "b", _fields(), "  laser_off_time: 3e-3\n")    # the end pool too
    text = (tmp_path / "b" / "config.yml").read_text().replace("y_begin: 0", "y_begin: 30e-6")
    (tmp_path / "b" / "config.yml").write_text(text)
    run_measure(tmp_path / "b" / "config.yml")
    stats = pd.read_csv(case2 / "measure_results" / "cross_sections_statistics.csv")
    np.testing.assert_allclose(stats["iy"], (np.arange(6, 12) + 0.5) * H)


def test_no_steady_section_is_an_error(tmp_path):
    _write(tmp_path, _fields(), "  laser_off_time: 1e-4\n")
    with pytest.raises(ValueError, match="No steady section"):
        run_measure(tmp_path / "config.yml")


def test_single_track_steady_sections_end_to_end(tmp_path):
    """Cell-centre single-track case (track y): the steady filter keeps the sections whose
    cells (lower face iy) are steady; all the sections stay in the _all_sections file."""
    f = _fields(n_track=16)
    # SimToPC axes: (nz, ny, nx) = (vertical, track, lateral)
    tr = {k: np.transpose(v, (1, 0, 2)) for k, v in f.items()}
    tr["cellAlpha.material"] = tr["meltHistory"].copy()
    tr["cellAlpha.material"][:, 5, :] = tr["cellAlpha.material"][:, 4, :]   # continuous melt pool cloud
    case = _write(tmp_path, tr, "  extraction_mode: cell_centres\n  min_points_per_zrow: 2\n",
                  geometry="single_track", cell_centres=True)
    run_measure(tmp_path / "config.yml")
    res = case / "measure_results"
    all_sections = pd.read_csv(res / "cross_sections_statistics_all_sections.csv")
    stats = pd.read_csv(res / "cross_sections_statistics.csv")
    assert len(all_sections) > len(stats) > 0
    np.testing.assert_allclose(stats["iy"], np.array([2, 3, 4]) * H)
    pd.testing.assert_frame_equal(stats.reset_index(drop=True),
                                  all_sections[np.isin(np.rint(all_sections["iy"] / H), [2, 3, 4])].reset_index(drop=True))


# ------------------------------------------------------------------ configuration

def test_config_steady_sections_defaults_and_validation():
    cfg = build_measure_config(dict(BASE))
    assert cfg.steady_sections is False and cfg.laser_off_time is None
    cfg = build_measure_config({**BASE, "steady_sections": True, "substrate_top": 3e-4, "laser_off_time": "6.6e-4"})
    assert cfg.steady_sections and cfg.laser_off_time == pytest.approx(6.6e-4)
    with pytest.raises(ValueError, match="needed by measure.steady_sections"):
        build_measure_config({**BASE, "steady_sections": True})
    with pytest.raises(ValueError, match="true or false"):
        build_measure_config({**BASE, "steady_sections": "yes please", "substrate_top": 3e-4})
    with pytest.raises(ValueError, match="laser_off_time must be positive"):
        build_measure_config({**BASE, "laser_off_time": 0})


# ------------------------------------------------------------------ reference (real runs)

@pytest.mark.parametrize("name", ["P195_v1200", "P100_v1200"])
def test_steady_sections_match_dilip_tools(name):
    run = DILIP / "runs" / name
    if not (run / "VIRGIN_CASE.json").exists() or (run / ".to_reconstruct").exists():
        pytest.skip("Dilip run data not available")
    dt = load_module("dilip_tools_ref", DILIP / "dilip_tools.py")
    d = dt.load(run)
    t_off = json.loads((DILIP / "cases" / name / "CASE.json").read_text())["laser_on_s"]
    ks_ref, p90_ref = dt.steady_sections(d, t_off)
    g = read_cell_grid(run, axes=AxesConfig("z", "y"), cell_size=5e-6, need_solidification_time=True)
    candidates = np.nonzero(g.centres(0) >= 300e-6 - 1e-12)[0]
    for off in (t_off, laser_off_time_from_case(run)):
        ks, p90 = steady_sections(g, candidates, d["plate"] * 1e-6, off)
        np.testing.assert_array_equal(ks, ks_ref)
        np.testing.assert_array_equal(p90, p90_ref[candidates])
