"""CLI entry point for the nrrd codec."""

from __future__ import annotations

import argparse
import json
import sys

from nrrd.nrrd_codec import load_nrrd, probe_nrrd


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(prog="ff-nrrd", description="Format Factory NRRD tool")
    sub = parser.add_subparsers(dest="command")

    probe_p = sub.add_parser("probe", help="Check if a file is valid NRRD")
    probe_p.add_argument("file")

    load_p = sub.add_parser("load", help="Parse and display NRRD metadata")
    load_p.add_argument("file")

    args = parser.parse_args(argv)

    if args.command == "probe":
        result = probe_nrrd(args.file)
        print(json.dumps({"probe": result, "file": args.file}))
        sys.exit(0 if result else 1)
    elif args.command == "load":
        model = load_nrrd(args.file)
        print(json.dumps(model, indent=2))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
