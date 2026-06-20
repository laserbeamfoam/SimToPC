"""
License
  This program is free software: you can redistribute it and/or modify
  it under the terms of the GNU General Public License as published
  by the Free Software Foundation, either version 3 of the License,
  or (at your option) any later version.

  This program is distributed in the hope that it will be useful,
  but WITHOUT ANY WARRANTY; without even the implied warranty of
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.

  See the GNU General Public License for more details.
  You should have received a copy of the GNU General Public License
  along with this program. If not, see <https://www.gnu.org/licenses/>.

Description
  Pre-processing utility to transform a completed OpenFOAM LPBF
  single-track simulation into the coordinate convention expected
  by SimToPC (x = track width, y = scan direction, z = build direction).

  The utility remaps point coordinates and the gravity vector, renames
  the metal VOF field to the name SimToPC expects, and copies the
  minimum set of files required for the SimToPC measure stage.

  Supported input coordinate conventions (scan_axis, build_axis):
    laserMeltFoam default: scan_axis=y  build_axis=z  (no-op)
    laserbeamFoam native:  scan_axis=z  build_axis=y

Usage
  python tools/adapt_case_to_simtopc.py \\
      --src  /path/to/original_case \\
      --dst  /path/to/adapted_case  \\
      --scan-axis z                  \\
      --build-axis y                 \\
      --alpha-field alpha.metal

  The --src case must be a reconstructed (serial) OpenFOAM case with
  constant/polyMesh/ and at least one completed time directory.

Authors
  Simon A. Rodriguez, University College Dublin (UCD)
"""

import re
import shutil
import argparse
from pathlib import Path


_AXIS_IDX = {"x": 0, "y": 1, "z": 2}

_COORD_RE = re.compile(
    r'\(\s*([^\s()]+)\s+([^\s()]+)\s+([^\s()]+)\s*\)'
)


def _remap_coord(match, width_idx, scan_idx, build_idx):
    src = [match.group(1), match.group(2), match.group(3)]
    return f"({src[width_idx]} {src[scan_idx]} {src[build_idx]})"


def _transform_vector_file(src: Path, dst: Path,
                           width_idx: int, scan_idx: int, build_idx: int,
                           new_object_name: str = None) -> None:
    """
    Copy an OpenFOAM file, remapping (x y z) triplets and optionally
    updating the FoamFile 'object' entry.
    """
    content = src.read_text()

    if new_object_name is not None:
        content = re.sub(
            r'(object\s+)[^\s;]+\s*;',
            lambda m: f'{m.group(1)}{new_object_name};',
            content,
            count=1,
        )

    remap = lambda m: _remap_coord(m, width_idx, scan_idx, build_idx)
    content = _COORD_RE.sub(remap, content)

    dst.write_text(content)


def _latest_time_dir(case_dir: Path) -> Path:
    time_dirs = []
    for d in case_dir.iterdir():
        if d.is_dir():
            try:
                float(d.name)
                time_dirs.append(d)
            except ValueError:
                pass
    if not time_dirs:
        raise RuntimeError(f"No time directories found in {case_dir}")
    return max(time_dirs, key=lambda d: float(d.name))


def _detect_alpha_field(time_dir: Path) -> str:
    if (time_dir / "alpha.metal").exists():
        return "alpha.metal"
    if (time_dir / "alpha.material").exists():
        return "alpha.material"
    raise RuntimeError(
        f"Could not find alpha.metal or alpha.material in {time_dir}"
    )


def adapt_case(src_dir: Path, dst_dir: Path,
               scan_axis: str, build_axis: str,
               alpha_field: str) -> None:

    scan_idx = _AXIS_IDX[scan_axis]
    build_idx = _AXIS_IDX[build_axis]
    width_idx = 3 - scan_idx - build_idx

    if dst_dir.exists():
        raise FileExistsError(
            f"Destination already exists: {dst_dir}\n"
            "Remove it or choose a different destination."
        )
    dst_dir.mkdir(parents=True)

    print(f"Source      : {src_dir}")
    print(f"Destination : {dst_dir}")
    print(f"Coordinate mapping  : x→x  {scan_axis}→y  {build_axis}→z")
    print(f"Alpha field : {alpha_field} → alpha.material")
    print()

    # --- constant/polyMesh: transform points, copy rest as-is ---
    src_polymesh = src_dir / "constant" / "polyMesh"
    dst_polymesh = dst_dir / "constant" / "polyMesh"
    dst_polymesh.mkdir(parents=True)

    for f in src_polymesh.iterdir():
        if f.name == "points":
            print(f"  Transforming  constant/polyMesh/points ...")
            _transform_vector_file(f, dst_polymesh / "points",
                                   width_idx, scan_idx, build_idx)
        else:
            shutil.copy2(f, dst_polymesh / f.name)

    # --- constant/: copy other files, updating g vector ---
    src_const = src_dir / "constant"
    dst_const = dst_dir / "constant"
    for f in src_const.iterdir():
        if f.is_file():
            if f.name == "g":
                print(f"  Transforming  constant/g ...")
                _transform_vector_file(f, dst_const / "g",
                                       width_idx, scan_idx, build_idx)
            else:
                shutil.copy2(f, dst_const / f.name)

    # --- system/: copy as-is (needed by OpenFOAMReader) ---
    src_system = src_dir / "system"
    if src_system.exists():
        shutil.copytree(src_system, dst_dir / "system")
        print(f"  Copied        system/")

    # --- Final time directory: copy relevant fields ---
    src_time = _latest_time_dir(src_dir)
    dst_time = dst_dir / src_time.name
    dst_time.mkdir()
    print(f"  Using timestep: {src_time.name}")

    # solidificationTime — scalar, copy as-is
    src_st = src_time / "solidificationTime"
    if src_st.exists():
        shutil.copy2(src_st, dst_time / "solidificationTime")
        print(f"  Copied        {src_time.name}/solidificationTime")
    else:
        raise RuntimeError(
            f"solidificationTime not found in {src_time}. "
            "SimToPC requires this field."
        )

    # alpha field — scalar, rename to alpha.material
    src_alpha = src_time / alpha_field
    if not src_alpha.exists():
        raise RuntimeError(f"{alpha_field} not found in {src_time}")
    dst_alpha = dst_time / "alpha.material"
    content = src_alpha.read_text()
    content = re.sub(
        r'(object\s+)[^\s;]+\s*;',
        r'\g<1>alpha.material;',
        content,
        count=1,
    )
    dst_alpha.write_text(content)
    print(f"  Renamed       {src_time.name}/{alpha_field} → alpha.material")

    # --- .foam marker file ---
    foam_marker = dst_dir / f"{dst_dir.name}.foam"
    foam_marker.touch()
    print(f"  Created       {foam_marker.name}")

    print()
    print("Done. Run SimToPC measure on:", dst_dir)


def main():
    parser = argparse.ArgumentParser(
        description="Adapt an OpenFOAM LPBF case to SimToPC's coordinate convention."
    )
    parser.add_argument("--src", required=True,
                        help="Path to the original (reconstructed) OpenFOAM case.")
    parser.add_argument("--dst", required=True,
                        help="Path where the adapted case will be written.")
    parser.add_argument("--scan-axis", default="z", choices=["x", "y", "z"],
                        help="Axis that is the scan direction in the source case "
                             "(default: z for laserbeamFoam native).")
    parser.add_argument("--build-axis", default="y", choices=["x", "y", "z"],
                        help="Axis that is the build direction in the source case "
                             "(default: y for laserbeamFoam native).")
    parser.add_argument("--alpha-field", default="auto",
                        help="Name of the metal VOF field in the source case "
                             "('auto' detects alpha.metal or alpha.material, "
                             "default: auto).")
    args = parser.parse_args()

    src_dir = Path(args.src).resolve()
    dst_dir = Path(args.dst).resolve()

    if not src_dir.exists():
        parser.error(f"Source directory does not exist: {src_dir}")

    scan_axis = args.scan_axis
    build_axis = args.build_axis
    if scan_axis == build_axis:
        parser.error("--scan-axis and --build-axis must be different.")

    alpha_field = args.alpha_field
    if alpha_field == "auto":
        src_time = _latest_time_dir(src_dir)
        alpha_field = _detect_alpha_field(src_time)
        print(f"Auto-detected alpha field: {alpha_field}")

    adapt_case(src_dir, dst_dir, scan_axis, build_axis, alpha_field)


if __name__ == "__main__":
    main()
