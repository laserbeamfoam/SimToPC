# Measure — metallographic mode

## Purpose

This example shows the metallographic mode of `simtopc measure`
(`geometry_mode: metallographic`) on four `laserbeamFoam` single tracks. The
mode measures a track as an etched cross-section is measured in the
laboratory: the fusion zone is what melted at some time (`meltHistory > 0`),
and the lengths are taken from the top of the plate.
The mode is explained in
[docs/METALLOGRAPHIC_MODE.md](../../docs/METALLOGRAPHIC_MODE.md).

The mode is for `laserbeamFoam` cases only, because it needs the field
`meltHistory`. `laserMeltFoam` cases are measured with the default mode
(`geometry_mode: single_track`).

The cases are read in their native `laserbeamFoam` axes (`x` across the
track, `y` vertical, `z` along the scan). No adaptation step is needed.

---

## The cases

Single tracks on a Ti-6Al-4V plate with a 30 µm powder layer, 195 W and a
100 µm spot (the process conditions of Dilip et al. 2017). The plate top is
at `y = 150 µm`, which is the `substrate_top` given in `config.yml` (the
user must give it; SimToPC does not find it from the case). The cells are cubes.

| Case | Scan speed (m/s) | Cell (µm) | Box x × y × z (µm) | Cells | Track along z (µm) |
|------|------------------|-----------|--------------------|-------|--------------------|
| `test_case_1` | 1.2 | 5    | 300 × 380 × 1400 | 1 276 800 | 100–1300 |
| `test_case_2` | 1.2 | 3.33 | 300 × 380 × 1400 | 4 309 200 | 100–1300 |
| `test_case_3` | 1.0 | 5    | 300 × 500 × 1600 | 1 920 000 | 300–1500 |
| `test_case_4` | 1.0 | 3.33 | 300 × 500 × 1600 | 6 480 000 | 300–1500 |

The two meshes of a scan speed use the same box.

`cases/test_case_N` holds what is needed to run each case: `system/`,
`constant/` (with the laser path and the powder particles in
`constant/location`) and the initial fields in `initial/`. The computed
fields are not distributed (several GB per case). The results of SimToPC
on the completed runs are in `expected_outputs/`.

---

## What is measured

In every cross-section of the mesh (one per cell along the track):

- **width:** the width of the fusion zone in the row of cells just below the
  plate top. When an edge cell of that row is not metal at the final time
  (`alpha.metal < 0.5`, the bead surface sank into it), the width is taken
  one row lower, at most two rows (`width_max_rows_down`).
- **depth:** from the plate top to the bottom of the lowest melted cell that
  is metal at the final time.
- **fill:** the metal fraction of the fusion zone at and below the plate top.
  It is a control of the section, not a filter.
- **surface:** the height of the metal on the centreline, from the plate top.

### The window

The means are taken over a window of the track that SimToPC finds from the
tracks themselves (`window_mode: steady_stretch`). It is the same for the
two cases of a scan speed, so that both meshes are measured over the same
part of the track.

1. **Profile.** The width and the depth are measured in every section along
   the track.
2. **Steady stretch of a case.** The two profiles are smoothed with a 50 µm
   running median (`steady_filter_length`). The steady stretch is the
   longest stretch of the track in which the smoothed width and the smoothed
   depth both stay within ±5 µm (`steady_tolerance`) of their median over
   that stretch. It leaves out the start of the track, where the melt pool
   is still growing, and its end, where the last melt pool froze.
3. **Window of a scan speed.** It starts 50 µm (`window_margin`) after the
   latest start of the steady stretches of that speed, rounded up to a
   multiple of 50 µm (`window_step`), and it is 400 µm long
   (`window_length`).
4. **Check.** The window must end inside the steady stretch of every case of
   that speed. Otherwise SimToPC stops with an error.

Track coordinates are measured from the first laser position
(`track_reference: laser_start`), because the tracks do not start at the
same `z` in the two boxes.

In this example (µm from the laser start):

| Case | Scan speed (m/s) | Steady stretch | Window |
|------|------------------|----------------|--------|
| `test_case_1` | 1.2 | 397.5–1157.5 | 450–850 |
| `test_case_2` | 1.2 | 241.7–1128.3 | 450–850 |
| `test_case_3` | 1.0 | 402.5–1147.5 | 500–900 |
| `test_case_4` | 1.0 | 435.0–1115.0 | 500–900 |

At 1.2 m/s the latest start is 397.5 µm; 50 µm later is 447.5 µm, rounded
up to 450 µm, and the window is 450–850 µm. It ends before 1128.3 µm, the
earliest end of the two steady stretches. At 1.0 m/s the latest start is
435.0 µm; 50 µm later is 485.0 µm, rounded up to 500 µm, and the window is
500–900 µm, which ends before 1115.0 µm.

---

## Requirements

- SimToPC installed (see main [README](../../README.md)). The metallographic
  mode reads the ASCII fields directly; ParaView is not used.
- To run the cases: `laserbeamFoam` (see below) and a cluster.

---

## Step 1 — Run the cases

```bash
cd examples/measure_metallographic
./Allrun test_case_1      # and test_case_2, test_case_3, test_case_4
```

`Allrun` prepares the case (`blockMesh`, `setFields`, `setSolidFraction`,
`decomposePar`), runs `laserbeamFoam` with the number of ranks of
`system/decomposeParDict` and reconstructs the last time.

**Solver version.** These cases were run with laserbeamFoam (branch
`OpenFoam_com_main`) together with the changes of pull requests #148, #149,
#157, #159 and #160, now merged into that branch, and of #151, #156 and
#169, which were still under review when these results were published. The
case files use options of two of them: `longPause` in
`constant/LaserProperties` (#151) and `latentHeatMethod apparentCapacity` in
`system/fvSolution` (#159). Results with another version of the solver may
differ slightly.

**Cost.** The runs behind `expected_outputs/` took, on nodes of 128 cores:

| Case | Ranks | Wall time (h) | Node-hours |
|------|-------|---------------|------------|
| `test_case_1` | 128 | 5.7  | 6  |
| `test_case_2` | 512 | 9.0  | 36 |
| `test_case_3` | 128 | 11.9 | 12 |
| `test_case_4` | 512 | 19.3 | 77 |

After a run, the case directory must hold `system/`, `constant/` and the
last time directory, reconstructed and in ASCII, with `meltHistory` and
`alpha.metal`.

---

## Step 2 — Run SimToPC

```bash
simtopc measure config.yml
```

SimToPC writes:

- `metallographic_summary.csv`, next to `config.yml`: one row per case with
  the window, the steady stretch, the mean, standard deviation and median of
  the width, the number of sections measured one or two rows lower, the mean
  and standard deviation of the depth, the fill and the centreline surface.
- `cases/test_case_N/measure_results/`:
  - `metallographic_sections.csv`: the sections of the window;
  - `metallographic_profile.csv`: every section of the mesh;
  - `cross_sections_statistics.csv` and the plots.

---

## Expected results

| Case | Window from the laser start (µm) | Sections | Width (µm) | Depth (µm) | Fill (%) |
|------|----------------------------------|----------|------------|------------|----------|
| `test_case_1` | 450–850 | 80  | 138.4 ± 2.9 | 60.0 ± 0.0 | 95.6 |
| `test_case_2` | 450–850 | 120 | 132.6 ± 1.9 | 63.3 ± 0.0 | 92.5 |
| `test_case_3` | 500–900 | 80  | 140.0 ± 0.0 | 75.0 ± 0.0 | 88.7 |
| `test_case_4` | 500–900 | 120 | 135.6 ± 2.0 | 79.9 ± 0.5 | 87.7 |

Mean ± standard deviation over the sections of the window. The complete
numbers are in `expected_outputs/metallographic_summary.csv`, and the
profile of every case along the track in
`expected_outputs/test_case_N/metallographic_profile.csv`.

`tests/test_metallographic_validation.py` compares a new measurement with
these files. It runs when the environment variable
`SIMTOPC_METALLOGRAPHIC_RUNS` points to a folder with the four completed
cases (`test_case_1` … `test_case_4`), and is skipped otherwise.

---

## Reference

Dilip, J.J.S., Zhang, S., Teng, C. et al. Influence of processing parameters
on the evolution of melt pool, porosity, and microstructures in Ti-6Al-4V
alloy parts fabricated by selective laser melting. *Progress in Additive
Manufacturing* 2, 157–167 (2017).
