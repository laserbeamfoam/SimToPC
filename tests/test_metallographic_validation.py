"""Validation of the metallographic mode on real laserbeamFoam runs (skipped when the data are
missing): the four case D single tracks of the Dilip et al. 2017 comparison (195 W, 1.2 and
1.0 m/s, 5 and 3.33 um cells; bed2_gprops_mid_tall), measured with SimToPC exactly as by the
reference scripts of that study: tall_profiles.py (every section) and measure_tall.py (the window
of each speed, the means; measure_tall.json). The 3.33 um run at 1.0 m/s lies in a longer box
with its track 200 um further along (track_reference: laser_start puts it in the same frame)."""
from __future__ import annotations

import json
import os
import sys

import numpy as np
import pandas as pd
import pytest

from cell_case_helpers import DILIP, load_module
from simtopc.measure.main import run as run_measure

TALL = DILIP / "bed2_gprops_mid_tall"
RUNS = (("D_v1200_H380", 1.2), ("D_v1200_H380_3.333um", 1.2),
        ("D_v1000_H380", 1.0), ("D_v1000_H500_B300_3.333um_r2", 1.0))
TRACK_START_REF_UM = 100.0          # measure_tall.py frame: the track starts at z = 100 um
REFERENCE = TALL / "measure_tall.json"


def _available():
    return REFERENCE.exists() and all((TALL / "runs" / n / ".fetched").exists() for n, _ in RUNS)


pytestmark = pytest.mark.skipif(not _available(), reason="bed2_gprops_mid_tall runs not available")


def _last_time(run):
    times = [d for d in run.iterdir() if d.is_dir() and d.name != "0" and d.name.replace(".", "", 1).replace("e-", "", 1).isdigit()]
    return max(times, key=lambda d: float(d.name))


@pytest.fixture(scope="module")
def measured(tmp_path_factory):
    root = tmp_path_factory.mktemp("dilip_caseD")
    for i, (name, _) in enumerate(RUNS):
        run = TALL / "runs" / name
        case = root / "cases" / f"test_case_{i + 1}"
        case.mkdir(parents=True)
        for item in ("system", "constant"):
            os.symlink(run / item, case / item)
        t = _last_time(run)
        os.symlink(t, case / t.name)
    (root / "parameters.txt").write_text(
        "# Scanning Speed (m/s) | Power (W) | Spot size (m)\n"
        + "".join(f"  {v}   195   1.0e-04\n" for _, v in RUNS))
    (root / "config.yml").write_text(
        "mesh_density: cases\nparameters_file: parameters.txt\noutput_dir: results\nrunning_on: local\n"
        "measure:\n  y_begin: 0\n  y_end: 1200e-6\n  x_min: 0\n  x_max: 300e-6\n  cell_size: auto\n"
        "  geometry_mode: metallographic\n  axes: {track: z, vertical: y}\n  substrate_top: 150e-6\n"
        "  window_mode: steady_stretch\n  track_reference: laser_start\n")
    cwd = os.getcwd()
    os.chdir(root)
    try:
        run_measure(root / "config.yml")
    finally:
        os.chdir(cwd)
    summary = pd.read_csv(root / "metallographic_summary.csv")
    profiles = {name: pd.read_csv(root / "cases" / f"test_case_{i + 1}" / "measure_results"
                                  / "metallographic_profile.csv") for i, (name, _) in enumerate(RUNS)}
    return summary, profiles


@pytest.mark.parametrize("i,name", list(enumerate(n for n, _ in RUNS)))
def test_summary_matches_measure_tall(measured, i, name):
    summary, _ = measured
    ref = json.loads(REFERENCE.read_text())[name]
    s = summary.iloc[i]
    um = 1e6
    assert s["window_begin"] * um == pytest.approx(ref["window_um"][0] - TRACK_START_REF_UM, abs=1e-6)
    assert s["window_end"] * um == pytest.approx(ref["window_um"][1] - TRACK_START_REF_UM, abs=1e-6)
    assert s["steady_stretch_begin"] * um + TRACK_START_REF_UM == pytest.approx(ref["steady_stretch_um"][0], abs=1e-6)
    assert s["steady_stretch_end"] * um + TRACK_START_REF_UM == pytest.approx(ref["steady_stretch_um"][1], abs=1e-6)
    assert int(s["sections"]) == ref["sections"]
    for key, rk in (("width_mean", "W"), ("width_sd", "W_sd"), ("width_median", "W_median"),
                    ("depth_mean", "D"), ("depth_sd", "D_sd"), ("surface_min", "surface_min")):
        assert s[key] * um == pytest.approx(ref[rk], abs=1e-6), key
    for key, rk in (("width_sections_one_row_lower", "W_sections_one_row_lower"),
                    ("width_sections_two_rows_lower", "W_sections_two_rows_lower"),
                    ("width_sections_not_measured", "W_sections_not_measured")):
        assert int(s[key]) == ref[rk], key
    assert s["fill_mean"] == pytest.approx(ref["fill_mean"], abs=1e-12)
    assert s["fill_min"] == pytest.approx(ref["fill_min"], abs=1e-12)
    assert bool(s["continuous"])


@pytest.mark.parametrize("name", [n for n, _ in RUNS])
def test_every_section_matches_tall_profiles(measured, name):
    _, profiles = measured
    sys.path.insert(0, str(DILIP))
    sys.path.insert(0, str(TALL))
    try:
        tp = load_module("tall_profiles_ref", TALL / "tall_profiles.py")
        ref = tp.profiles(TALL / "runs" / name)
    finally:
        sys.path.remove(str(DILIP))
        sys.path.remove(str(TALL))
    p = profiles[name]
    um = 1e6
    np.testing.assert_allclose(p["width"] * um, ref["W"], rtol=0, atol=1e-6, equal_nan=True)
    np.testing.assert_array_equal(p["width_rows_down"], ref["down"])
    np.testing.assert_allclose(p["depth"] * um, ref["D"], rtol=0, atol=1e-6)
    np.testing.assert_allclose(p["fill"], ref["fill"], rtol=0, atol=1e-12, equal_nan=True)
    np.testing.assert_allclose(p["surface"] * um, ref["surface"], rtol=0, atol=1e-6)
