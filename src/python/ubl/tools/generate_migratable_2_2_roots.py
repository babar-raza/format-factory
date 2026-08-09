"""Generate the pinned UBL-2.2-to-2.3 migration-eligible root-type table.

Dev-time-only generator. Diffs the acquired OASIS UBL 2.2 release package
(SRC-UBL-006) against the already-vendored UBL 2.3 maindoc schemas
(SRC-UBL-002) to determine, once, which of the 91 UBL 2.3 root document
types have a UBL 2.2 maindoc schema whose root-level element sequence
differs from 2.3 only by newly-added optional elements and/or cardinality
relaxations -- never a removal or reordering -- mirroring
generate_migratable_2_1_roots.py's own eligibility rule exactly (UBL-UPGRADE-001).

Requires the acquired UBL 2.2 package to be materialized locally
(``python -m tools.format_contract.authority_materializer materialize
--format ubl``) since 2.2 is not bundled with the shipped wheel -- only
its own migration-eligibility VERDICT is (this generator's own output),
matching the exact dependency-free pattern already established by
generate_migratable_2_1_roots.py.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import xml.etree.ElementTree as ET
import zipfile
from pathlib import Path

_PACKAGE_ROOT = Path(__file__).resolve().parents[1] / "src"
sys.path.insert(0, str(_PACKAGE_ROOT))

_REPO_ROOT = Path(__file__).resolve().parents[4]
_ACQUIRED_2_2 = _REPO_ROOT / ".local" / "format-contracts" / "acquired" / "ubl" / "src-ubl-006.bin"
_ACQUIRED_2_3 = _REPO_ROOT / ".local" / "format-contracts" / "acquired" / "ubl" / "src-ubl-002.bin"
_XSD = "{http://www.w3.org/2001/XMLSchema}"


def _root_sequence(zf: zipfile.ZipFile, member: str) -> list[tuple[str, str, str]] | None:
    try:
        data = zf.read(member)
    except KeyError:
        return None
    root = ET.fromstring(data)
    doc_el = root.find(f"{_XSD}element")
    if doc_el is None:
        return None
    type_name = doc_el.get("type")
    complex_type = next(
        (c for c in root.findall(f"{_XSD}complexType") if c.get("name") == type_name), None
    )
    if complex_type is None:
        return None
    sequence = complex_type.find(f"{_XSD}sequence")
    if sequence is None:
        return None
    return [
        (child.get("ref") or "", child.get("minOccurs", "1"), child.get("maxOccurs", "1"))
        for child in sequence
    ]


def _is_migration_eligible(seq22: list[tuple[str, str, str]], seq23: list[tuple[str, str, str]]) -> bool:
    names22 = [x[0] for x in seq22]
    names23 = [x[0] for x in seq23]
    if [n for n in names22 if n not in names23]:
        return False  # an element was removed between 2.2 and 2.3
    if [n for n in names22 if n in names23] != [n for n in names23 if n in names22]:
        return False  # shared elements were reordered
    d22 = {x[0]: x for x in seq22}
    d23 = {x[0]: x for x in seq23}
    for name in names22:
        before, after = d22[name][1:], d23[name][1:]
        if before == after:
            continue
        min_before, max_before = before
        min_after, max_after = after
        if int(min_after) > int(min_before):
            return False  # minOccurs tightened
        if max_before != "unbounded" and max_after != "unbounded" and int(max_after) < int(max_before):
            return False  # maxOccurs tightened
        if max_before == "unbounded" and max_after != "unbounded":
            return False  # maxOccurs tightened from unbounded
    for name in names23:
        if name not in names22 and d23[name][1] != "0":
            return False  # a newly added element is not optional
    return True


def _compute_manifest() -> dict[str, object]:
    from format_factory.ubl._generated.root_catalog import ROOT_NAMES

    with (
        zipfile.ZipFile(_ACQUIRED_2_2) as zf22,
        zipfile.ZipFile(_ACQUIRED_2_3) as zf23,
    ):
        authority_sha256_2_2 = hashlib.sha256(_ACQUIRED_2_2.read_bytes()).hexdigest()
        authority_sha256_2_3 = hashlib.sha256(_ACQUIRED_2_3.read_bytes()).hexdigest()
        eligible: list[str] = []
        for name in ROOT_NAMES:
            seq22 = _root_sequence(zf22, f"xsd/maindoc/UBL-{name}-2.2.xsd")
            seq23 = _root_sequence(zf23, f"xsd/maindoc/UBL-{name}-2.3.xsd")
            if seq22 is None or seq23 is None:
                continue  # no UBL 2.2 schema for this root type at all
            if _is_migration_eligible(seq22, seq23):
                eligible.append(name)

    eligible.sort()
    table_sha256 = hashlib.sha256(
        json.dumps(eligible, sort_keys=True, separators=(",", ":")).encode()
    ).hexdigest()
    return {
        "authority_sha256_2_2": authority_sha256_2_2,
        "authority_sha256_2_3": authority_sha256_2_3,
        "source_version": "2.2",
        "target_version": "2.3",
        "table_sha256": table_sha256,
        "migratable_root_names": eligible,
    }


def _render(manifest: dict[str, object]) -> str:
    names = manifest["migratable_root_names"]
    if not isinstance(names, list):
        raise TypeError("manifest migratable_root_names must be a list")
    lines = [
        '"""Generated UBL 2.2-to-2.3 migration-eligibility table. Do not edit by hand.',
        "",
        "visibility: generated",
        "generated_by: claude",
        '"""',
        "",
        "from __future__ import annotations",
        "",
        "from typing import Final",
        "",
        f'AUTHORITY_SHA256_2_2: Final = "{manifest["authority_sha256_2_2"]}"',
        f'AUTHORITY_SHA256_2_3: Final = "{manifest["authority_sha256_2_3"]}"',
        f'TABLE_SHA256: Final = "{manifest["table_sha256"]}"',
        'SOURCE_VERSION: Final = "2.2"',
        'TARGET_VERSION: Final = "2.3"',
        "MIGRATABLE_2_2_ROOT_NAMES: Final[frozenset[str]] = frozenset({",
    ]
    lines.extend(f'    "{name}",' for name in names)
    lines.extend(["})", ""])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    package = _PACKAGE_ROOT / "format_factory" / "ubl"
    manifest_path = package / "_generated" / "migratable_2_2_roots_manifest.json"
    output_path = package / "_generated" / "migratable_2_2_roots.py"

    manifest = _compute_manifest()

    if args.check:
        stale = []
        if not manifest_path.exists() or json.loads(
            manifest_path.read_text(encoding="utf-8")
        ) != manifest:
            stale.append(str(manifest_path))
        if not output_path.exists() or output_path.read_text(encoding="utf-8") != _render(manifest):
            stale.append(str(output_path))
        if stale:
            raise SystemExit(f"generated UBL migration-eligibility source is stale: {', '.join(stale)}")
        return 0

    manifest_path.write_text(
        json.dumps(manifest, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n"
    )
    output_path.write_text(_render(manifest), encoding="utf-8", newline="\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
