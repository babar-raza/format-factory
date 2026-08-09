"""Generate the pinned UBL 2.3 per-root schema child-order table.

This is a dev-time-only generator: it imports the optional `xmlschema`
dependency and the package's own `_schema_root_order_live()` (which itself
requires `xmlschema`) to compute, once, the declared child-element order
for every one of the 91 bundled maindoc root types. The result is written
as a plain-data generated module with no `xmlschema` import at all, so the
public `schema_root_order()` can consult it at runtime without requiring
the optional dependency to be installed -- see
FF6-UBL-EDIT-FIRST-OCCURRENCE-002 in schema_validator.py's own docstring
for why this table exists.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

_PACKAGE_ROOT = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(_PACKAGE_ROOT))


def _compute_manifest() -> dict[str, object]:
    from format_factory.ubl._generated.root_catalog import AUTHORITY_SHA256, ROOT_NAMES
    from format_factory.ubl.validation.schema_validator import _schema_root_order_live

    table: dict[str, list[str]] = {}
    for name in ROOT_NAMES:
        table[name] = list(_schema_root_order_live(name))

    table_sha256 = hashlib.sha256(
        json.dumps(table, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return {
        "authority_sha256": AUTHORITY_SHA256,
        "profile": "UBL-2.3",
        "table_sha256": table_sha256,
        "root_order": table,
    }


def _render(manifest: dict[str, object]) -> str:
    root_order = manifest["root_order"]
    if not isinstance(root_order, dict):
        raise TypeError("manifest root_order must be a dict")
    lines = [
        '"""Generated UBL 2.3 per-root schema child-order table. Do not edit by hand.',
        "",
        "visibility: generated",
        "generated_by: claude",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "from typing import Final",
        "",
        f'AUTHORITY_SHA256: Final = "{manifest["authority_sha256"]}"',
        f'TABLE_SHA256: Final = "{manifest["table_sha256"]}"',
        'PROFILE: Final = "UBL-2.3"',
        "SCHEMA_ROOT_ORDER: Final[dict[str, tuple[str, ...]]] = {",
    ]
    for name in sorted(root_order):
        children = ", ".join(f'"{child}"' for child in root_order[name])
        comma = "," if len(root_order[name]) == 1 else ""
        lines.append(f'    "{name}": ({children}{comma}),')
    lines.extend(["}", ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    package = _PACKAGE_ROOT / "format_factory" / "ubl"
    manifest_path = package / "_generated" / "schema_root_order_manifest.json"
    output_path = package / "_generated" / "schema_root_order.py"

    manifest = _compute_manifest()

    if args.check:
        stale = []
        if not manifest_path.exists() or json.loads(
            manifest_path.read_text(encoding="utf-8")
        ) != manifest:
            stale.append(str(manifest_path))
        if not output_path.exists() or output_path.read_text(encoding="utf-8") != _render(
            manifest
        ):
            stale.append(str(output_path))
        if stale:
            raise SystemExit(f"generated UBL schema-root-order source is stale: {', '.join(stale)}")
        return 0

    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    output_path.write_text(_render(manifest), encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
