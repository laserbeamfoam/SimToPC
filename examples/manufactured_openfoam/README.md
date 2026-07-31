# Manufactured OpenFOAM-field example

This example builds a compact OpenFOAM case with an artificially constructed melt pool. It is intended for illustration and software verification, not as a physical LPBF simulation.

The case contains three mesh-aligned tapered sections with prescribed geometric descriptors:

| Scan position | Width | Height | Depth |
| --- | ---: | ---: | ---: |
| 50 um | 40 um | 20 um | 15 um |
| 120 um | 60 um | 25 um | 20 um |
| 240 um | 80 um | 30 um | 25 um |

No thermo-fluid solver is run. Instead, the script creates a structured mesh, assigns artificial `alpha.material` and `solidificationTime` point fields, then runs the standard `simtopc measure` workflow. The generated outputs can be inspected with ParaView and compared with the known discrete geometry.

## Run

From the repository root:

```bash
SIMTOPC_OPENFOAM_BASHRC=/path/to/OpenFOAM/etc/bashrc \
python examples/manufactured_openfoam/run_manufactured_case.py
```

For example, on a local OpenFOAM v2506 installation:

```bash
SIMTOPC_OPENFOAM_BASHRC=/home/simon/OpenFOAM/OpenFOAM-v2506/etc/bashrc \
python examples/manufactured_openfoam/run_manufactured_case.py
```

The generated case and SimToPC outputs are written to:

```text
examples/manufactured_openfoam/generated_case/
```

Key files after running:

```text
generated_case/config.yml
generated_case/MANUFACTURED/test_case_1/0.0012/
generated_case/MANUFACTURED/test_case_1/measure_results/cross_sections_statistics.csv
generated_case/MANUFACTURED/test_case_1/measure_results/row_statistics.csv
```

The expected representative values are printed at the end of the run.
