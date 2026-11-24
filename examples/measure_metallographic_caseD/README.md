# Measure — metallographic mode with one window per scan speed

## Purpose

Four laserbeamFoam single tracks on a Ti-6Al-4V plate (195 W, spot 100 µm,
30 µm powder layer; 1.2 and 1.0 m/s, each on 5 µm and 3.33 µm cells), measured
as etched cross-sections are measured in the laboratory (Dilip et al. 2017):

- **width:** the fusion width at the plate top. When the edge cells of that
  row ended as gas (the bead surface sank into it), the width is taken one row
  lower, at most two rows.
- **depth:** from the plate top to the bottom of the lowest melted-metal cell.
- **fill:** the metal fraction of the fusion zone below the plate top. It is a
  control, not a filter of the sections.

The window is the same for all the tracks of a scan speed. It starts 50 µm
after the latest start of their steady stretches, rounded up to a multiple of
50 µm, and is 400 µm long. A steady stretch is where the width and the depth
stay within ±5 µm of their median.

The track coordinates are measured from the first laser position
(`track_reference: laser_start`), because one of the cases lies in a longer box
with its track further along.

The reference data of that paper (micrographs and figures) are not
distributed with SimToPC.

## The cases

`cases/test_case_1` … `test_case_4`, in the order of `parameters.txt`. Each one
is a completed, reconstructed `laserbeamFoam` run in its native axes, with:

- one uniform `blockMeshDict` block;
- the ASCII fields `meltHistory` and `alpha.metal` in the last time directory;
- `constant/timeVsLaserPosition`.

SimToPC writes `measure_aux/` and `measure_results/` in each case directory. To
leave the runs untouched, the case directory can hold symbolic links to the
run's `system/`, `constant/` and last time directory.

## Running

    simtopc measure config.yml

## Outputs

- `metallographic_summary.csv`, next to `config.yml`: one row per case with the
  window, the steady stretch, the mean, sd and median of the width, the
  sections measured one or two rows lower, the mean and sd of the depth, the
  fill and the centreline surface.
- `cases/test_case_N/measure_results/`:
  - `metallographic_sections.csv`: the window sections.
  - `metallographic_profile.csv`: every section of the mesh.
  - `cross_sections_statistics.csv` and the plots.

`tests/test_metallographic_validation.py` checks these numbers against the
reference scripts of the study. It is skipped when the runs are not available.
