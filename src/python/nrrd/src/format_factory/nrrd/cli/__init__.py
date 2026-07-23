"""Command-line entry point for bounded NRRD inspection."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence

from ..codec import load
from ..validation import validate


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ff-nrrd")
    parser.add_argument("source")
    args = parser.parse_args(argv)
    document = load(args.source)
    report = validate(document)
    print(
        json.dumps(
            {
                "format": "nrrd",
                "profile": f"NRRD000{document.version}",
                "type": document.nrrd_type,
                "sizes": document.sizes,
                "encoding": document.encoding,
                "valid": report.is_valid,
            },
            sort_keys=True,
        )
    )
    return 0 if report.is_valid else 1


__all__ = ["main"]
