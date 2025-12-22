import argparse
from simtopc.pipeline import run, surrogate, generate

def main():
    p = argparse.ArgumentParser(prog="simtopc")
    sub = p.add_subparsers(dest="cmd", required=True)

    run_p = sub.add_parser("run", help="Run SimToPC pipeline")
    run_p.add_argument("config", help="Path to config.yml")

    p_sur = sub.add_parser("surrogate", help="Train surrogate model (requires TensorFlow)")
    p_sur.add_argument("config", help="Path to config.yml")

    p_gen = sub.add_parser(
        "generate",
        help="Generate and run simulations (requires OpenFOAM environment)",
    )
    p_gen.add_argument("config", help="Path to config.yml")


    args = p.parse_args()
    if args.cmd == "run":
        run(args.config)
        
    if args.cmd == "surrogate":
        surrogate(args.config)

    if args.cmd == "generate":
        generate(args.config)
