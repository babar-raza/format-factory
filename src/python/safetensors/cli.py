"""CLI entry point for the safetensors codec."""

from __future__ import annotations

import argparse
import json
import sys

from safetensors.safetensors_codec import load_safetensors, probe_safetensors


def main(argv: list[str] | None = None) -> None:
    """Run the command-line interface for the SafeTensors codec."""
    parser = argparse.ArgumentParser(
        prog="ff-safetensors",
        description="Format Factory SafeTensors tool",
    )
    sub = parser.add_subparsers(dest="command")

    probe_p = sub.add_parser("probe", help="Check if a file is valid SafeTensors")
    probe_p.add_argument("file", help="Path to .safetensors file")

    load_p = sub.add_parser("load", help="Parse and display tensor metadata")
    load_p.add_argument("file", help="Path to .safetensors file")

    args = parser.parse_args(argv)

    if args.command == "probe":
        result = probe_safetensors(args.file)
        print(json.dumps({"probe": result, "file": args.file}))
        sys.exit(0 if result else 1)
    elif args.command == "load":
        model = load_safetensors(args.file)
        print(json.dumps(model, indent=2))
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
