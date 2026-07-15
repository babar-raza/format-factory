"""CLI entry point for the ipynb codec."""

from __future__ import annotations

import argparse
import json
import sys

from ipynb.ipynb_codec import load_ipynb, probe_ipynb


def main(argv: list[str] | None = None) -> None:
    """Run the command-line interface for the Jupyter Notebook codec."""
    parser = argparse.ArgumentParser(
        prog="ff-ipynb",
        description="Format Factory Jupyter Notebook (.ipynb) tool",
    )
    sub = parser.add_subparsers(dest="command")

    probe_p = sub.add_parser("probe", help="Check if a file is a valid .ipynb")
    probe_p.add_argument("file", help="Path to .ipynb file")

    load_p = sub.add_parser("load", help="Parse and display notebook structure")
    load_p.add_argument("file", help="Path to .ipynb file")

    args = parser.parse_args(argv)

    if args.command == "probe":
        result = probe_ipynb(args.file)
        print(json.dumps({"probe": result, "file": args.file}))
        sys.exit(0 if result else 1)
    elif args.command == "load":
        model = load_ipynb(args.file)
        print(json.dumps(model, indent=2))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
