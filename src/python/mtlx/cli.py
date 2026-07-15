"""CLI entry point for the mtlx codec."""

from __future__ import annotations

import argparse
import json
import sys

from mtlx.mtlx_codec import load_mtlx, probe_mtlx


def main(argv: list[str] | None = None) -> None:
    """Run the command-line interface for the MaterialX codec."""
    parser = argparse.ArgumentParser(prog="ff-mtlx", description="Format Factory MaterialX tool")
    sub = parser.add_subparsers(dest="command")

    probe_p = sub.add_parser("probe", help="Check if a file is valid MaterialX")
    probe_p.add_argument("file")

    load_p = sub.add_parser("load", help="Parse and display MaterialX structure")
    load_p.add_argument("file")

    args = parser.parse_args(argv)

    if args.command == "probe":
        result = probe_mtlx(args.file)
        print(json.dumps({"probe": result, "file": args.file}))
        sys.exit(0 if result else 1)
    elif args.command == "load":
        model = load_mtlx(args.file)
        print(json.dumps(model, indent=2))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
