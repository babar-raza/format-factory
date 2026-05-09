"""
neutral_model.py -- Neutral model builder and validator for format-factory-fodt.

Builds and validates the 7-entity FODT neutral model output:
  Document -> Block (paragraph|heading) | List (-> ListItem) | Table (-> TableRow -> TableCell)
  plus Warning (in warnings list)

Gate 5 neutral model: schemas/neutral-model/fodt/ (7 entities, 26 mappings, 19 rules).
Gate 5 PASSED: Babar Raza, 2026-05-08, run046.
IR-FODT-015: validate against neutral model before returning.

License: Apache-2.0
Package: format-factory-fodt v0.1.0
"""

from __future__ import annotations

from typing import Any

from .constants import FORMAT_ID, SPEC_VERSION


# ---------------------------------------------------------------------------
# Warning helper
# ---------------------------------------------------------------------------

def make_warning(code: str, message: str, source: str | None = None) -> dict[str, Any]:
    """Build a structured Warning dict matching the neutral model Warning entity."""
    w: dict[str, Any] = {"code": code, "message": message}
    if source is not None:
        w["source"] = source
    return w


# ---------------------------------------------------------------------------
# Document builder
# ---------------------------------------------------------------------------

def build_document(
    odf_version_attr: str,
    mimetype: str | None,
    blocks: list[dict[str, Any]],
    lists: list[dict[str, Any]],
    tables: list[dict[str, Any]],
    warnings: list[dict[str, Any]],
    unsupported_features: list[str],
    parse_errors: list[dict[str, Any]],
) -> dict[str, Any]:
    """Assemble the Document-level result dict matching the FODT neutral model.

    Fields conform to the Document entity in schemas/neutral-model/fodt/model.yaml.
    Additional fields (unsupported_features, parse_errors) extend the neutral
    model for product parser transparency.
    """
    return {
        "format_id": FORMAT_ID,
        "spec_version": SPEC_VERSION,
        "odf_version_attr": odf_version_attr,
        "mimetype": mimetype,
        "blocks": blocks,
        "lists": lists,
        "tables": tables,
        "warnings": warnings,
        "unsupported_features": sorted(unsupported_features),
        "parse_errors": parse_errors,
    }


# ---------------------------------------------------------------------------
# Document validator (IR-FODT-015)
# ---------------------------------------------------------------------------

def validate_document(result: dict[str, Any]) -> list[str]:
    """Validate a parse_fodt() result against the 7-entity neutral model.

    Returns a list of violation strings. Empty list means valid.
    Does NOT raise -- callers decide whether to treat violations as fatal.
    """
    violations: list[str] = []

    # Required top-level fields
    for field in ("format_id", "spec_version", "odf_version_attr", "blocks", "lists", "tables", "warnings"):
        if field not in result:
            violations.append(f"Document missing required field: {field!r}")

    if result.get("format_id") != FORMAT_ID:
        violations.append(
            f"Document.format_id must be {FORMAT_ID!r}; got {result.get('format_id')!r}"
        )

    blocks = result.get("blocks")
    if not isinstance(blocks, list):
        violations.append("Document.blocks must be a list")
    else:
        for i, block in enumerate(blocks):
            violations.extend(_validate_block(block, i))

    lists = result.get("lists")
    if not isinstance(lists, list):
        violations.append("Document.lists must be a list")
    else:
        for i, lst in enumerate(lists):
            violations.extend(_validate_list(lst, i))

    tables = result.get("tables")
    if not isinstance(tables, list):
        violations.append("Document.tables must be a list")
    else:
        for i, table in enumerate(tables):
            violations.extend(_validate_table(table, i))

    warnings = result.get("warnings")
    if not isinstance(warnings, list):
        violations.append("Document.warnings must be a list")

    return violations


def _validate_block(block: dict[str, Any], idx: int) -> list[str]:
    violations: list[str] = []
    prefix = f"Block[{idx}]"

    for field in ("type", "text"):
        if field not in block:
            violations.append(f"{prefix} missing required field: {field!r}")

    btype = block.get("type")
    if btype not in ("paragraph", "heading"):
        violations.append(f"{prefix}.type must be 'paragraph' or 'heading'; got {btype!r}")

    if btype == "heading":
        hl = block.get("heading_level")
        if not isinstance(hl, int) or hl < 1 or hl > 6:
            violations.append(f"{prefix}.heading_level must be int 1-6 for headings; got {hl!r}")

    return violations


def _validate_list(lst: dict[str, Any], idx: int) -> list[str]:
    violations: list[str] = []
    prefix = f"List[{idx}]"

    if "items" not in lst:
        violations.append(f"{prefix} missing required field: 'items'")
        return violations

    items = lst["items"]
    if not isinstance(items, list):
        violations.append(f"{prefix}.items must be a list")
        return violations

    for j, item in enumerate(items):
        violations.extend(_validate_list_item(item, idx, j))

    return violations


def _validate_list_item(item: dict[str, Any], list_idx: int, item_idx: int) -> list[str]:
    violations: list[str] = []
    prefix = f"List[{list_idx}].Item[{item_idx}]"

    for field in ("text", "level"):
        if field not in item:
            violations.append(f"{prefix} missing required field: {field!r}")

    level = item.get("level")
    if not isinstance(level, int) or level < 1:
        violations.append(f"{prefix}.level must be a positive int; got {level!r}")

    return violations


def _validate_table(table: dict[str, Any], idx: int) -> list[str]:
    violations: list[str] = []
    prefix = f"Table[{idx}]"

    if "rows" not in table:
        violations.append(f"{prefix} missing required field: 'rows'")
        return violations

    rows = table["rows"]
    if not isinstance(rows, list):
        violations.append(f"{prefix}.rows must be a list")
        return violations

    for j, row in enumerate(rows):
        violations.extend(_validate_table_row(row, idx, j))

    return violations


def _validate_table_row(row: dict[str, Any], table_idx: int, row_idx: int) -> list[str]:
    violations: list[str] = []
    prefix = f"Table[{table_idx}].Row[{row_idx}]"

    if "cells" not in row:
        violations.append(f"{prefix} missing required field: 'cells'")
        return violations

    cells = row["cells"]
    if not isinstance(cells, list):
        violations.append(f"{prefix}.cells must be a list")
        return violations

    for k, cell in enumerate(cells):
        if "text" not in cell:
            violations.append(f"{prefix}.Cell[{k}] missing required field: 'text'")

    return violations
