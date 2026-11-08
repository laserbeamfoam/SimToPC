# Measure — metallographic mode (laserbeamFoam single track on a substrate)

## Purpose

This example measures a single track on a substrate plate in the way an etched
cross-section is measured in the laboratory, with `geometry_mode:
metallographic`, keeping the steady part of the track. The simulated conditions are those of the Ti-6Al-4V single
tracks of Dilip et al. (2017): 195 W, 1200 mm/s, a spot of 100 µm, a 30 µm
powder layer on a plate whose top is at 300 µm.

The reference data of that paper (micrographs and figures) are not
distributed with SimToPC.

## The case

`cases/test_case_1` must be a completed, reconstructed `laserbeamFoam` run in
its native axes (no `adapt_case_to_simtopc.py`):

- `x` across the track, `y` vertical (gravity along `-y`), `z` along the scan;
- a box of 400 × 430 × 1000 µm³ with uniform 5 µm cells (one `blockMeshDict`
  block, or `Cx`, `Cy`, `Cz` written with `postProcess -func writeCellCentres`);
- in the last time directory, the ASCII fields `meltHistory`, `alpha.metal`
  and `solidificationTime` (the `meltPoolHistory` option of the solver), and
  `constant/timeVsLaserPower`.

A symbolic link to the run directory is enough: SimToPC only reads the case
and writes `measure_aux/` and `measure_results/` in it.

## Running

    simtopc measure config.yml

## Outputs (`cases/test_case_1/measure_results/`)

- `cross_sections_statistics.csv`: per section, `iy` (cell centre along the
  track), `width` (fusion width at the plate top), `height` (top of the
  consolidated bead above the plate top), `depth` (penetration below the plate
  top), `porosity_at_iy` (operational void fraction of the section) and
  `total_volume_material_at_iy`;
- `metallographic_sections.csv`: the same geometry with the fusion flag and the
  cell counts of each section;
- `steady_sections.csv`: the 90th percentile of the solidification time of the
  fusion zone of each candidate section, and which sections are steady;
- the plots `Width.png`, `Height.png`, `Depth.png`, `Porosity.png`, `DByW.png`.

`measure_aux/continuous.joblib` is true when every measured section is fused
into the plate.

## Reference

J. J. S. Dilip, S. Zhang, C. Teng, K. Zeng, C. Robinson, D. Pal, B. Stucker,
"Influence of processing parameters on the evolution of melt pool, porosity,
and microstructures in Ti-6Al-4V alloy parts fabricated by selective laser
melting", Progress in Additive Manufacturing 2 (2017) 157-167,
doi:10.1007/s40964-017-0030-2.
