"""Generate the stable UBL 2.3 document-root inventory and typed root classes."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path


def _roots(manifest: dict[str, object]) -> list[str]:
    roots = manifest["roots"]
    if not isinstance(roots, list) or not all(isinstance(item, str) for item in roots):
        raise ValueError("root manifest must contain a string list")
    if roots != sorted(set(roots)):
        raise ValueError("root names must be sorted and unique")
    digest = hashlib.sha256("\n".join(roots).encode()).hexdigest()
    if digest != manifest["root_names_sha256"]:
        raise ValueError("root-name digest does not match the pinned manifest")
    return roots


def _render_catalog(manifest: dict[str, object]) -> str:
    roots = _roots(manifest)
    lines = [
        '"""Generated UBL 2.3 root inventory. Do not edit by hand.',
        "",
        "visibility: generated",
        "generated_by: codex",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "from typing import Final",
        "",
        f'AUTHORITY_SHA256: Final = "{manifest["authority_sha256"]}"',
        f'ARCHIVE_MEMBER_NAMES_SHA256: Final = "{manifest["archive_member_names_sha256"]}"',
        f'ROOT_NAMES_SHA256: Final = "{manifest["root_names_sha256"]}"',
        'PROFILE: Final = "UBL-2.3"',
        "ROOT_NAMES: Final = (",
    ]
    lines.extend(f'    "{name}",' for name in roots)
    lines.extend(
        [
            ")",
            "ROOT_NAME_SET: Final = frozenset(ROOT_NAMES)",
            "ROOT_NAMESPACES: Final = {",
            '    name: f"urn:oasis:names:specification:ubl:schema:xsd:{name}-2"',
            "    for name in ROOT_NAMES",
            "}",
            "",
        ]
    )
    return "\n".join(lines)


def _render_types(manifest: dict[str, object]) -> str:
    roots = _roots(manifest)
    lines = [
        '"""Generated typed UBL 2.3 document roots. Do not edit by hand.',
        "",
        "visibility: generated",
        "generated_by: codex",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "from typing import Final",
        "",
        "from .document import UblDocument",
        "",
        "",
    ]
    for name in roots:
        lines.extend(
            [
                f"class {name}(UblDocument):",
                f'    """Typed UBL 2.3 {name} document root."""',
                "",
                f'    ROOT_NAME = "{name}"',
                "",
                "",
            ]
        )
    lines.append("ROOT_CLASSES: Final[dict[str, type[UblDocument]]] = {")
    lines.extend(f'    "{name}": {name},' for name in roots)
    lines.extend(["}", ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    package = Path(__file__).resolve().parents[1] / "src" / "format_factory" / "ubl"
    manifest_path = package / "_generated" / "root_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    outputs = {
        package / "_generated" / "root_catalog.py": _render_catalog(manifest),
        package / "model" / "root_types.py": _render_types(manifest),
    }
    if args.check:
        stale = [
            str(output)
            for output, expected in outputs.items()
            if not output.exists() or output.read_text(encoding="utf-8") != expected
        ]
        if stale:
            raise SystemExit(f"generated UBL source is stale: {', '.join(stale)}")
        return 0
    for output, expected in outputs.items():
        output.write_text(expected, encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
