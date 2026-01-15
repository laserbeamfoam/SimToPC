# measure

## Purpose

The `measure` mode performs post-processing and characterisation of completed
LPBF simulation cases.

Starting from simulation outputs generated using OpenFOAM-based solvers, this
mode assesses melt-track continuity and extracts track-resolved melt-pool
geometry and porosity metrics along the full scan path.

This command implements the core functionality of SimToPC and produces the
primary outputs analysed in the associated publication.

---

## Input data

The `measure` mode operates on a directory containing one or more completed
simulation cases, typically generated using the `generate` mode.

Each simulation case directory is expected to follow the standard OpenFOAM
output structure required for post-processing with ParaView and `pvpython`.

For the tutorials provided with this repository, precomputed simulation results
are supplied and used as input to the `measure` command.

---

## Basic usage

Before running SimToPC, ensure that the Python environment in which the package
was installed is active, as described in the main repository `README.md`.

The `measure` mode is invoked through the SimToPC command-line interface:

    simtopc measure config.yml

The configuration file specifies the location of the simulation case directories
and the settings required for post-processing and metric extraction.

---

## Measurement procedure

For each simulation case, SimToPC processes the melt track on a
cross-section-by-cross-section basis along the scan direction.

First, a **track continuity check** is performed. Based on the known mesh
resolution, expected cross-sections are enumerated along the track. If one or
more expected cross-sections contain no material cells, the track is classified
as discontinuous.

For **continuous tracks only**, geometric and porosity metrics are evaluated at
each cross-section:

- **W (width)**: maximum lateral extent of the melt pool,
- **H (height)**: vertical extent of the melt pool, accounting for surface and
  internal pores,
- **D (depth)**: vertical distance from the lowest material point to the
  location of maximum width,
- **Porosity**: ratio of pore cells to total cells in the cross-section.

These quantities are defined consistently with the methodology described in the
associated publication.

---

## Outputs

For each simulation case, the `measure` mode produces:

- A **track continuity flag**, indicating whether a continuous melt track is
  formed.
- **Per-cross-section characterisation data** (W, H, D, porosity) for continuous
  tracks.
- **Aggregated datasets** stored as CSV files, with one row per cross-section.
- **Diagnostic plots** illustrating the spatial variation of the extracted
  metrics along the scan path.

These outputs correspond directly to the quantities reported and analysed in the
associated publication and are suitable for downstream statistical analysis and
machine learning workflows.

---

## Notes

The `measure` mode relies on ParaView and `pvpython` for post-processing and
metric extraction.

Simulation cases classified as discontinuous are excluded from geometric
characterisation to ensure physically meaningful comparisons across simulations.
