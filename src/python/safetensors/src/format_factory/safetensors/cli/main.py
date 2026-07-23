from __future__ import annotations

import argparse
import json
from collections.abc import Sequence

from ..codec.reader import load


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="ff-safetensors")
    parser.add_argument("path")
    args = parser.parse_args(argv)
    with load(args.path) as document:
        print(
            json.dumps(
                {
                    "profile": document.profile,
                    "metadata": dict(document.metadata),
                    "tensors": [
                        {
                            "name": item.name,
                            "dtype": item.dtype.value,
                            "shape": item.shape,
                            "data_offsets": item.data_offsets,
                        }
                        for item in sorted(document.tensors.values(), key=lambda x: x.name)
                    ],
                },
                indent=2,
            )
        )
    return 0
