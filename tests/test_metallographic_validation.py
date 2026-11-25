"""The metallographic example on its real runs (examples/measure_metallographic): SimToPC applied to
the four completed laserbeamFoam cases must give the reference outputs stored with the example
(expected_outputs/: metallographic_summary.csv and the profile of every case).

The fields of the runs are not distributed (several GB). The test runs when
SIMTOPC_METALLOGRAPHIC_RUNS points to a folder holding the completed runs as test_case_1 ...
test_case_4 (the order of the example's parameters.txt), each with system/, constant/ and its last
time directory (reconstructed, ASCII); it is skipped otherwise. The runs are only read: the
measurement is made in a temporary copy of the example with links to them."""
from __future__ import annotations

import os
import shutil

import numpy as np
import pandas as pd
import pytest

from cell_case_helpers import EXAMPLE_METALLOGRAPHIC, metallographic_runs
from simtopc.measure.cells import last_time_dir
from simtopc.measure.main import run as run_measure

EXPECTED = EXAMPLE_METALLOGRAPHIC / "expected_outputs"
CASES = [f"test_case_{i}" for i in range(1, 5)]
RUNS = metallographic_runs()

pytestmark = pytest.mark.skipif(
    RUNS is None or not all((RUNS / c / "system").exists() for c in CASES)
    or not (EXPECTED / "metallographic_summary.csv").exists(),
    reason="SIMTOPC_METALLOGRAPHIC_RUNS (completed runs of the metallographic example) not given")


@pytest.fixture(scope="module")
def measured(tmp_path_factory):
    root = tmp_path_factory.mktemp("metallographic_example")
    for name in ("config.yml", "parameters.txt"):
        shutil.copy(EXAMPLE_METALLOGRAPHIC / name, root / name)
    for c in CASES:
        case = root / "cases" / c
        case.mkdir(parents=True)
        t = last_time_dir(RUNS / c)
        for item in ("system", "constant", t.name):
            os.symlink((RUNS / c / item).resolve(), case / item)
    cwd = os.getcwd()
    os.chdir(root)
    try:
        run_measure(root / "config.yml")
    finally:
        os.chdir(cwd)
    return root


def _same(actual, expected):
    assert list(actual.columns) == list(expected.columns)
    assert len(actual) == len(expected)
    for col in expected.columns:
        if expected[col].dtype.kind in "fi":
            np.testing.assert_allclose(actual[col].to_numpy(float), expected[col].to_numpy(float),
                                       rtol=1e-9, atol=1e-12, equal_nan=True, err_msg=col)
        else:
            assert list(actual[col]) == list(expected[col]), col


def test_summary_matches_the_reference(measured):
    _same(pd.read_csv(measured / "metallographic_summary.csv"),
          pd.read_csv(EXPECTED / "metallographic_summary.csv"))


@pytest.mark.parametrize("case", CASES)
def test_profile_matches_the_reference(measured, case):
    _same(pd.read_csv(measured / "cases" / case / "measure_results" / "metallographic_profile.csv"),
          pd.read_csv(EXPECTED / case / "metallographic_profile.csv"))
