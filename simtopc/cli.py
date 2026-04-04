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
  Command-line interface (CLI) entry point for the SimToPC software
  package. This module defines the user-facing commands used to
  orchestrate the SimToPC workflow, including:

  - Generation of simulation cases from a configuration file
  - Execution of post-processing routines for melt-pool characterisation
  - Invocation of optional surrogate-modelling utilities

  The CLI provides a reproducible and scriptable interface intended
  for both local execution and automated workflows.

Assumptions
  - This module is executed via the simtopc command-line entry point
  - Lower-level workflow logic is implemented in dedicated submodules
    (e.g. generate, measure, surrogate)
  - Configuration files provided by the user follow the documented
    SimToPC YAML schema

Authors
  Simon A. Rodriguez, University College Dublin (UCD)
  Alojz Ivankovic, University College Dublin (UCD)
  Petar Cosic, University College Dublin (UCD)
  Tom Flint, University of Manchester (UoM)
  Philip Cardiff, University College Dublin (UCD)
"""


import argparse
import sys
from simtopc.measure.main import run as run_measure_cmd
from simtopc.generate.main import run_generate

def main():
    p = argparse.ArgumentParser(prog="simtopc")
    sub = p.add_subparsers(dest="cmd", required=True)

    measure_parser = sub.add_parser(
        "measure",
        help="Measure melt-pool metrics",
    )
    measure_parser.add_argument("config", help="Path to config.yml")

    surrogate_parser = sub.add_parser(
      "surrogate",
      help="Train surrogate model (requires TensorFlow)",
    )
    surrogate_parser.add_argument("config", help="Path to config.yml")

    generate_parser = sub.add_parser(
        "generate",
        help="Generate and run simulations (requires OpenFOAM environment)",
    )
    generate_parser.add_argument("config", help="Path to config.yml")

    args = p.parse_args()

    if args.cmd == "measure":
        try:
            run_measure_cmd(args.config)
        except (ValueError, FileNotFoundError) as exc:
            print(f"Measure configuration error: {exc}", file=sys.stderr)
            raise SystemExit(2) from None
    elif args.cmd == "surrogate":
        from simtopc.surrogate.main import run as run_surrogate_cmd
        run_surrogate_cmd(args.config)
    elif args.cmd == "generate":
        run_generate(args.config)
