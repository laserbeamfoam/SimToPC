#!/usr/bin/env python3
"""
Run regression tests for documented SimToPC tutorials.

The script intentionally runs tutorials in a temporary working directory so
that the repository examples are not modified. It is meant as a top-level
check that the documented workflow can be executed and that the expected
output files are produced. When reference outputs are available, it also
checks that the tutorial reproduces those outputs exactly.
"""

from __future__ import annotations

import argparse
import filecmp
import os
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_LBF_DATA_REPO = "https://github.com/ScimonCFD/SimToPC_laserbeamfoam_data.git"


class TutorialFailure(RuntimeError):
    """Raised when a tutorial regression test fails."""


def _print_step(message: str) -> None:
    print(f"[tutorial-test] {message}", flush=True)


def _run(cmd: list[str], cwd: Path, env: dict[str, str] | None = None) -> None:
    pretty = " ".join(cmd)
    _print_step(f"running: {pretty}")
    subprocess.run(cmd, cwd=cwd, env=env, check=True)


def _copy_example(example_name: str, work_root: Path) -> Path:
    src = REPO_ROOT / "examples" / example_name
    if not src.exists():
        raise TutorialFailure(f"Example directory not found: {src}")

    dst = work_root / "examples" / example_name
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst)
    return dst


def _obtain_laserbeamfoam_data(example_dir: Path, data_zip: Path | None) -> None:
    if data_zip is not None:
        zip_path = data_zip.resolve()
        if not zip_path.exists():
            raise TutorialFailure(f"Data zip not found: {zip_path}")
        shutil.copy2(zip_path, example_dir / "laserbeamfoam_native.zip")
    else:
        _run(["git", "clone", DEFAULT_LBF_DATA_REPO], cwd=example_dir)
        zip_path = example_dir / "SimToPC_laserbeamfoam_data" / "laserbeamfoam_native.zip"
        if not zip_path.exists():
            raise TutorialFailure(
                "Companion data repository did not contain laserbeamfoam_native.zip"
            )
        shutil.copy2(zip_path, example_dir / "laserbeamfoam_native.zip")
        shutil.rmtree(example_dir / "SimToPC_laserbeamfoam_data")

    with zipfile.ZipFile(example_dir / "laserbeamfoam_native.zip") as zf:
        zf.extractall(example_dir)

    native_dir = example_dir / "laserbeamfoam_native"
    if not native_dir.exists() and (example_dir / "test_case_1").exists():
        native_dir.mkdir()
        for case_name in ("test_case_1", "test_case_2"):
            shutil.move(str(example_dir / case_name), native_dir / case_name)

    expected = [
        native_dir / "test_case_1" / "constant" / "polyMesh" / "points",
        native_dir / "test_case_1" / "0.0012" / "alpha.metal",
        native_dir / "test_case_1" / "0.0012" / "solidificationTime",
        native_dir / "test_case_2" / "constant" / "polyMesh" / "points",
        native_dir / "test_case_2" / "0.0012" / "alpha.metal",
        native_dir / "test_case_2" / "0.0012" / "solidificationTime",
    ]
    _assert_files_exist(expected)


def _assert_files_exist(paths: list[Path]) -> None:
    missing = [str(path) for path in paths if not path.exists()]
    if missing:
        raise TutorialFailure("Missing expected files:\n" + "\n".join(missing))


def _assert_nonempty_csv(path: Path) -> None:
    if not path.exists():
        raise TutorialFailure(f"Expected CSV not found: {path}")
    if path.stat().st_size == 0:
        raise TutorialFailure(f"Expected CSV is empty: {path}")
    lines = path.read_text().splitlines()
    if len(lines) < 2:
        raise TutorialFailure(f"Expected CSV has no data rows: {path}")


def _assert_matches_reference(actual: Path, reference: Path) -> None:
    if not reference.exists():
        raise TutorialFailure(f"Reference output not found: {reference}")
    if not filecmp.cmp(actual, reference, shallow=False):
        raise TutorialFailure(
            "Tutorial output differs from the reference output:\n"
            f"  actual:    {actual}\n"
            f"  reference: {reference}"
        )


def _assert_laserbeamfoam_reference_outputs(example_dir: Path) -> None:
    reference_root = (
        REPO_ROOT / "examples" / "measure_laserbeamfoam" / "expected_outputs"
    )
    checked = 0
    for case_name in ("test_case_1", "test_case_2"):
        case_dir = example_dir / "laserbeamfoam_adapted" / case_name
        for relative_path in (
            Path("measure_results") / "row_statistics.csv",
            Path("measure_results") / "cross_sections_statistics.csv",
        ):
            _assert_matches_reference(
                actual=case_dir / relative_path,
                reference=reference_root / case_name / relative_path,
            )
            checked += 1
    _print_step(f"matched {checked} tutorial output files against references")


def _run_laserbeamfoam_adapter(example_dir: Path) -> None:
    adapter = REPO_ROOT / "tools" / "adapt_case_to_simtopc.py"
    for case_name in ("test_case_1", "test_case_2"):
        _run(
            [
                sys.executable,
                str(adapter),
                "--src",
                f"laserbeamfoam_native/{case_name}",
                "--dst",
                f"laserbeamfoam_adapted/{case_name}",
            ],
            cwd=example_dir,
        )

    expected = []
    for case_name in ("test_case_1", "test_case_2"):
        case_dir = example_dir / "laserbeamfoam_adapted" / case_name
        expected.extend(
            [
                case_dir / "constant" / "polyMesh" / "points",
                case_dir / "constant" / "g",
                case_dir / "0.0012" / "alpha.material",
                case_dir / "0.0012" / "solidificationTime",
                case_dir / "main.foam",
            ]
        )
    _assert_files_exist(expected)


def _detect_openfoam_bashrc(cli_value: str | None) -> str | None:
    if cli_value:
        return cli_value
    if os.environ.get("SIMTOPC_OPENFOAM_BASHRC"):
        return os.environ["SIMTOPC_OPENFOAM_BASHRC"]
    wm_project_dir = os.environ.get("WM_PROJECT_DIR")
    if wm_project_dir:
        candidate = Path(wm_project_dir) / "etc" / "bashrc"
        if candidate.exists():
            return str(candidate)
    return None


def _patch_config_openfoam_bashrc(config_path: Path, openfoam_bashrc: str) -> None:
    text = config_path.read_text()
    lines = []
    replaced = False
    for line in text.splitlines():
        if line.strip().startswith("of_location:"):
            lines.append(f'  of_location: "{openfoam_bashrc}"')
            replaced = True
        else:
            lines.append(line)
    if not replaced:
        raise TutorialFailure(f"Could not find environment.of_location in {config_path}")
    config_path.write_text("\n".join(lines) + "\n")


def _run_measure(example_dir: Path, openfoam_bashrc: str) -> None:
    _patch_config_openfoam_bashrc(example_dir / "config.yml", openfoam_bashrc)

    env = os.environ.copy()
    env["PYTHONPATH"] = str(REPO_ROOT) + os.pathsep + env.get("PYTHONPATH", "")
    command = (
        "from simtopc.measure.main import run; "
        "run('config.yml')"
    )
    _run([sys.executable, "-c", command], cwd=example_dir, env=env)

    expected_files = []
    for case_name in ("test_case_1", "test_case_2"):
        case_dir = example_dir / "laserbeamfoam_adapted" / case_name
        expected_files.extend(
            [
                case_dir / "measure_results" / "row_statistics.csv",
                case_dir / "measure_results" / "cross_sections_statistics.csv",
                case_dir / "measure_aux" / "continuous.joblib",
                case_dir / "measure_aux" / "meltpool.csv",
            ]
        )
    _assert_files_exist(expected_files)

    for case_name in ("test_case_1", "test_case_2"):
        case_dir = example_dir / "laserbeamfoam_adapted" / case_name
        _assert_nonempty_csv(case_dir / "measure_results" / "row_statistics.csv")
        _assert_nonempty_csv(case_dir / "measure_results" / "cross_sections_statistics.csv")
        _assert_nonempty_csv(case_dir / "measure_aux" / "meltpool.csv")
    _assert_laserbeamfoam_reference_outputs(example_dir)


def run_laserbeamfoam_tutorial(args: argparse.Namespace) -> None:
    work_root = Path(args.workdir) if args.workdir else Path(
        tempfile.mkdtemp(prefix="simtopc-tutorial-")
    )
    work_root.mkdir(parents=True, exist_ok=True)
    _print_step(f"work directory: {work_root}")

    example_dir = _copy_example("measure_laserbeamfoam", work_root)
    _obtain_laserbeamfoam_data(
        example_dir=example_dir,
        data_zip=Path(args.laserbeamfoam_data_zip) if args.laserbeamfoam_data_zip else None,
    )
    _run_laserbeamfoam_adapter(example_dir)

    if args.skip_measure:
        _print_step("skipping simtopc measure because --skip-measure was provided")
        return

    openfoam_bashrc = _detect_openfoam_bashrc(args.openfoam_bashrc)
    if not openfoam_bashrc:
        raise TutorialFailure(
            "OpenFOAM bashrc was not provided. Pass --openfoam-bashrc or set "
            "SIMTOPC_OPENFOAM_BASHRC. Use --skip-measure to test only the "
            "download/adaptation part of the tutorial."
        )
    if not Path(openfoam_bashrc).exists():
        raise TutorialFailure(f"OpenFOAM bashrc not found: {openfoam_bashrc}")
    _run_measure(example_dir, openfoam_bashrc)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Run SimToPC tutorial regression tests."
    )
    parser.add_argument(
        "--tutorial",
        choices=["measure_laserbeamfoam"],
        default="measure_laserbeamfoam",
        help="Tutorial workflow to run.",
    )
    parser.add_argument(
        "--workdir",
        help="Working directory for the temporary tutorial run. "
             "Defaults to a newly created /tmp directory.",
    )
    parser.add_argument(
        "--laserbeamfoam-data-zip",
        help="Path to laserbeamfoam_native.zip. If omitted, the companion "
             "data repository is cloned.",
    )
    parser.add_argument(
        "--openfoam-bashrc",
        help="Path to the OpenFOAM etc/bashrc file used by simtopc measure.",
    )
    parser.add_argument(
        "--skip-measure",
        action="store_true",
        help="Only test data acquisition and coordinate adaptation; do not run "
             "simtopc measure.",
    )
    args = parser.parse_args()

    try:
        if args.tutorial == "measure_laserbeamfoam":
            run_laserbeamfoam_tutorial(args)
    except (subprocess.CalledProcessError, TutorialFailure) as exc:
        print(f"[FAIL] {exc}", file=sys.stderr)
        return 1

    print("[PASS] tutorial regression test completed successfully")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
