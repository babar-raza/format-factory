"""Command-line UBL structural inspection."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence

from ..analytics import element_count
from ..codec import load
from ..validation import validate


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ff-ubl")
    parser.add_argument("source")
    args = parser.parse_args(argv)
    document = load(args.source)
    report = validate(document)
    print(
        json.dumps(
            {
                "element_count": element_count(document),
                "format": "ubl",
                "profile": "UBL-2.3",
                "root": document.root_name,
                "valid": report.is_valid,
            },
            sort_keys=True,
        )
    )
    return 0 if report.is_valid else 1


__all__ = ["main"]
