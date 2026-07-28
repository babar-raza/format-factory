"""generate_fact_id_mapping.py — Generate complete old→new fact ID mapping (TC-SAL-ID-002).

Reads sal-facts-latest.json, runs the allocator for every fact, and writes:
  .local/sal-id/fact-id-mapping.json   (forward + reverse mapping)

CLI:
    python generate_fact_id_mapping.py [--input PATH] [--output PATH]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_DEFAULT_INPUT = _REPO_ROOT / ".local" / "spec-cache" / "sal-facts-latest.json"
_DEFAULT_OUTPUT = _REPO_ROOT / ".local" / "sal-id" / "fact-id-mapping.json"


def generate_mapping(
    input_path: Path | None = None,
    output_path: Path | None = None,
    ledger_path: Path | None = None,
) -> dict:
    from fact_id_allocator import allocate_bulk

    inp = input_path or _DEFAULT_INPUT
    out = output_path or _DEFAULT_OUTPUT

    if not inp.exists():
        print(f"ERROR: input file not found: {inp}", file=sys.stderr)
        sys.exit(1)

    result = allocate_bulk(inp, ledger_path)
    mapping = result["mapping"]

    reverse = {v: k for k, v in mapping.items()}

    collision_count = len(mapping) - len(reverse)
    if collision_count:
        print(f"ERROR: {collision_count} collision(s) detected in mapping", file=sys.stderr)
        sys.exit(1)

    output_data = {
        "schema_version": "1.0",
        "total_mapped": result["total_mapped"],
        "new_count": result["new_count"],
        "existing_count": result["existing_count"],
        "mappings": mapping,
        "reverse": reverse,
    }

    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(output_data, indent=2) + "\n", encoding="utf-8")
    print(f"Mapping written to {out} ({result['total_mapped']} facts)")
    return output_data


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate SAL fact ID mapping (TC-SAL-ID-002)")
    parser.add_argument("--input", type=Path, default=None)
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--ledger", type=Path, default=None)
    args = parser.parse_args()
    generate_mapping(args.input, args.output, args.ledger)


if __name__ == "__main__":
    main()
