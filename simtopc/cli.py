import argparse

from simtopc.measure.main import run as run_measure_cmd
# from simtopc.pipeline import surrogate, generate
from simtopc.generate.main import run_generate


def main():
    p = argparse.ArgumentParser(prog="simtopc")
    sub = p.add_subparsers(dest="cmd", required=True)

    measure_parser = sub.add_parser("measure", help="Measure melt-pool metrics")
    measure_parser.add_argument("config", help="Path to config.yml")

    surrogate_parser = sub.add_parser("surrogate", help="Train surrogate model (requires TensorFlow)")
    surrogate_parser.add_argument("config", help="Path to config.yml")

    generate_parser = sub.add_parser(
        "generate",
        help="Generate and run simulations (requires OpenFOAM environment)",
    )
    generate_parser.add_argument("config", help="Path to config.yml")

    args = p.parse_args()

    if args.cmd == "measure":
        run_measure_cmd(args.config)
    elif args.cmd == "surrogate":
        from simtopc.surrogate.main import run as run_surrogate_cmd
        run_surrogate_cmd(args.config)
    # elif args.cmd == "generate":
    #     generate(args.config)
    elif args.cmd == "generate":
        run_generate(args.config)
