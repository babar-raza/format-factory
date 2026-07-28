"""Command-line XLIFF structural inspection."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence

from ..codec import load
from ..validation import validate


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ff-xliff")
    parser.add_argument("source")
    args = parser.parse_args(argv)
    document = load(args.source)
    report = validate(document)
    print(
        json.dumps(
            {
                "format": "xliff",
                "version": document.version,
                "source_language": document.source_language,
                "target_language": document.target_language,
                "file_count": document.file_count,
                "unit_count": document.unit_count,
                "valid": report.is_valid,
            },
            sort_keys=True,
        )
    )
    return 0 if report.is_valid else 1


__all__ = ["main"]
