from __future__ import annotations

import os
import shutil
from pathlib import Path

import pandas as pd
import pytest
import yaml

from cell_case_helpers import DILIP
from simtopc.measure.cells import last_time_dir
from simtopc.measure.main import build_measure_config, run as run_measure


EXAMPLE = Path(__file__).resolve().parents[1] / "examples" / "measure_metallographic"


def test_example_config_is_valid():
    cfg = build_measure_config(yaml.safe_load((EXAMPLE / "config.yml").read_text())["measure"])
    assert cfg.geometry_mode == "metallographic"
    assert cfg.axes.order == ("z", "y", "x") and cfg.steady_sections
    assert cfg.substrate_top == pytest.approx(300e-6)


RUN = DILIP / "runs" / "P195_v1200"


@pytest.mark.skipif(not (RUN / "VIRGIN_CASE.json").exists(), reason="Dilip run data not available")
def test_example_on_the_dilip_run(tmp_path):
    for name in ("config.yml", "parameters.txt"):
        shutil.copy(EXAMPLE / name, tmp_path / name)
    case = tmp_path / "cases" / "test_case_1"
    case.mkdir(parents=True)
    for name in ("system", "constant", last_time_dir(RUN).name):
        os.symlink(RUN / name, case / name)
    run_measure(tmp_path / "config.yml")
    res = case / "measure_results"
    stats = pd.read_csv(res / "cross_sections_statistics.csv")
    # results/compare.csv of the Dilip comparison: steady z 302-478 um, W 147.4, P 50.0
    assert len(stats) == 36
    assert round(stats["iy"].iloc[0] * 1e6, 1) == 302.5 and round(stats["iy"].iloc[-1] * 1e6, 1) == 477.5
    assert round(stats["width"].mean() * 1e6, 1) == 147.4
    assert round(stats["depth"].mean() * 1e6, 1) == 50.0
    steady = pd.read_csv(res / "steady_sections.csv")
    assert int(steady["steady"].sum()) == 36
