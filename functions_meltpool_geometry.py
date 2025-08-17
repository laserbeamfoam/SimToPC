'''
License
  This program is free software: you can redistribute it and/or modify 
  it under the terms of the GNU General Public License as published 
  by the Free Software Foundation, either version 3 of the License, 
  or (at your option) any later version.

  This program is distributed in the hope that it will be useful, 
  but WITHOUT ANY WARRANTY; without even the implied warranty of 
  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. 

  See the GNU General Public License for more details. You should have 
  received a copy of the GNU General Public License along with this 
  program. If not, see <https://www.gnu.org/licenses/>. 

Description
  Script for calculating geometric quantities from the meltpool extracted
  via postproc2.py.

Authors
    Simon A. Rodriguez, University College Dublin (UCD). All rights reserved
    Petar Cosic, University College Dublin (UCD). All rights reserved
    Tom Flint, University of Manchester. All rights reserved
    Philip Cardiff, University College Dublin (UCD). All rights reserved
    
'''

import pandas as pd
import numpy as np
import input_data
from input_data import *
from joblib import dump, load


def is_meltpool_continuous(csv_file = "y_z_slice_meltpool.csv", 
                           print_missing_columns = False):
    df = pd.read_csv(csv_file)   
    continuous = True
    y = df["Points_1"].to_numpy()
    y0 = y.min()
    iy = np.rint((y - y0) / CELL_SIZE).astype(int)   # Y-column index
    present = np.unique(iy)
    first_c, last_c = present.min(), present.max()
    expected = np.arange(first_c, last_c + 1)
    
    missing = np.setdiff1d(expected, present)  # missing columns
    continuous = (missing.size == 0)
    
    if (print_missing_columns):
        print("Continuous (no missing Y columns):", continuous)
        if missing.size:
            # Ranges of the missing columns (useful for debugging)
            gaps = [(y0 + m*CELL_SIZE, y0 + (m+1)*CELL_SIZE) for m in missing]
            print("Missing Y columns (m):", gaps)
            print("SIMON")
    
    dump(continuous, "./continuous.joblib")
    
    return continuous


def calculate_geometry_middle_sections(CSV_XZ = "x_z_slice_meltpool.csv", 
                                       MIN_POINTS_PER_ROW = 3):
    df = pd.read_csv(CSV_XZ)
    x = df["Points_0"].to_numpy()
    z = df["Points_2"].to_numpy()

    # --- snap/quantize Z levels using known grid spacing ---
    DZ = CELL_SIZE  # assume Z spacing equals CELL_SIZE (grid is isotropic)

    # z = df["Points_2"].to_numpy()

    # Optionally align the origin to the grid (helps if z.min() is slightly off)
    z0 = z.min()
    z0_aligned = np.round(z0 / DZ) * DZ  # snap the origin to the nearest grid level

    # Number of rows from z0_aligned to z.max()
    nrows = int(np.round((z.max() - z0_aligned) / DZ)) + 1
    levels = z0_aligned + np.arange(nrows) * DZ  # exact Z levels of the grid

    # This is the CURING/QUANTIZATION step:
    # Map each raw z to an integer row index (nearest grid level)
    zi = np.rint((z - z0_aligned) / DZ).astype(int)
    zi = np.clip(zi, 0, nrows - 1)  # safety in case of tiny rounding overshoots

    # Optional: the "snapped" Z values (purely for inspection/export)
    z_snapped = levels[zi]
    # --------------------------------------------------------

    # --- sanity checks: look at the *snapped* uniqueness, not raw z ---
    print("raw unique z:", np.unique(z).size)
    print("unique row indices (zi):", np.unique(zi).size)
    print("unique snapped z:", np.unique(z_snapped).size)


    # --- width-by-row using the snapped indices ---
    rows = []
    for k in np.unique(zi):              # <--- unique on zi (snapped rows)
        mask = (zi == k)
        if mask.sum() < MIN_POINTS_PER_ROW:
            continue
        xk = x[mask]
        wk = xk.max() - xk.min()
        zk = levels[k]                   # exact snapped Z level for this row
        rows.append((k, zk, wk))

    if not rows:
        raise RuntimeError("No valid Z-rows found. Check MIN_POINTS_PER_ROW or input data.")

    # unpack rows -> arrays
    idx, z_levels, widths = zip(*rows)
    z_levels = np.array(z_levels, dtype=float)
    widths   = np.array(widths, dtype=float)

    # width: max horizontal chord across Z 
    max_width = float(widths.max())
    z_at_max  = float(z_levels[widths.argmax()])

    # height: total vertical extent of the (snapped) slice
    height = float(z_levels.max() - z_levels.min())

    # D
    D = float(z_at_max - z_levels.min())


    # report
    print(f"W:      {max_width:.3e} m")
    print(f"H (total Z span):  {height:.3e} m")
    print(f"D:        {D:.3e} m")
    print(f"Z at W_max:             {z_at_max:.3e} m")
    print(" ")

    dump(max_width, "./W.joblib")
    dump(height, "./H.joblib")
    dump(D, "./D.joblib")
    dump(z_at_max, "./z_at_max.joblib")



def calculate_geometry_full_meltpool(CSV_3D = "meltpool.csv", 
                                     MIN_POINTS_PER_ZROW = 3):
   
    df = pd.read_csv(CSV_3D)
    x = df["Points_0"].to_numpy()
    y = df["Points_1"].to_numpy()
    z = df["Points_2"].to_numpy()
    
    DX = DY = DZ = CELL_SIZE
    
    # snap Y and Z to grid indices (like part 2 for Z)
    y0 = float(np.floor(y.min() / DY) * DY)
    # z0 = float(np.floor(z.min() / DZ) * DZ)
    z0_aligned = float(np.round(z.min() / DZ) * DZ)   # same as Part 2
    iy = np.rint((y - y0) / DY).astype(int)
    # iz = np.rint((z - z0) / DZ).astype(int)
    iz = np.rint((z - z0_aligned) / DZ).astype(int)
        
    def xz_metrics_for_section(x_sec, iz_sec, DZ, z0_aligned, min_pts_per_row=3):
        """
        Replicates Part 2 on an XZ slice at fixed Y, using snapped Z semantics:
          - W: max horizontal chord in X across snapped Z rows
          - height:    (kz_max - kz_min) * DZ               [snapped]
          - Z_at_D:    z0_aligned + kz_at_max_width * DZ          [snapped]
          - D:         (kz_at_max_width - kz_min) * DZ            [snapped]
        """
        if x_sec.size == 0 or iz_sec.size == 0:
            return np.nan, np.nan, np.nan, np.nan
    
        # Build w(z) over snapped rows
        widths = []
        for kz in np.unique(iz_sec):
            m = (iz_sec == kz)
            if m.sum() < min_pts_per_row:
                continue
            xk = x_sec[m]
            wk = float(xk.max() - xk.min())
            widths.append((kz, wk))
    
        if not widths:
            # No valid rows: we can still report height from iz indices (0 if empty)
            if iz_sec.size == 0:
                return np.nan, np.nan, np.nan, np.nan
            kz_min = int(np.min(iz_sec))
            kz_max = int(np.max(iz_sec))
            height = float((kz_max - kz_min) * DZ)
            return np.nan, height, np.nan, np.nan
    
        kz_list, w_vals = map(np.array, zip(*widths))
        kmax = int(np.argmax(w_vals))
        W = float(w_vals[kmax])
    
        # Snapped indices for bottom/top
        kz_at_max_width = int(kz_list[kmax])
        kz_min   = int(np.min(iz_sec))
        kz_max   = int(np.max(iz_sec))
    
        # Snapped outputs (match Part 2)
        Z_at_D = float(z0_aligned + kz_at_max_width * DZ)
        height = float((kz_max - kz_min) * DZ)
        D      = float((kz_at_max_width - kz_min) * DZ)
    
        return W, height, Z_at_D, D
    
    
    # iterate all Y sections
    records = []
    for ky in np.unique(iy):
        mY = (iy == ky)
        width, height, Z_at_D, D = xz_metrics_for_section(
            x_sec=x[mY], iz_sec=iz[mY],
            DZ=DZ, z0_aligned=z0_aligned,
            min_pts_per_row=MIN_POINTS_PER_ZROW
        )
        y_pos = float(y0 + ky * DY)  # snapped Y position
        records.append({
            "y_m": y_pos,
            "width_m": width,
            "height_m": height,
            "Z_at_D_m": Z_at_D,
            "D_m": D,
            "n_points": int(mY.sum())
        })
    
    out = pd.DataFrame.from_records(records).sort_values("y_m").reset_index(drop=True)
    out.to_csv("section_metrics_along_y.csv", index=False)
    dump(out, "section_metrics_along_y.joblib")
    
    # global mean/std across sections (skip NaNs)
    summary = {
        "width_mean_m": float(out["width_m"].mean(skipna=True)),
        "width_std_m":  float(out["width_m"].std(skipna=True, ddof=1)),
        "height_mean_m":    float(out["height_m"].mean(skipna=True)),
        "height_std_m":     float(out["height_m"].std(skipna=True, ddof=1)),
        "D_mean_m": float(out["D_m"].mean(skipna=True)),
        "D_std_m":  float(out["D_m"].std(skipna=True, ddof=1)),
        "n_sections": int(len(out))
    }
    pd.Series(summary).to_csv("section_metrics_summary_y.csv")
    dump(summary, "section_metrics_summary_y.joblib")
    
    print("Computed Y-sections:", len(out))
    print(out.head(6))
    print("\nSummary:", summary)