"""
Format Factory â€” Autonomous Task Generator
Sprint: FORMAT-FACTORY-AUTONOMY-ACCELERATION-SPRINT-1-001

Generates queue-item-v2 product task candidates from:
1. Capability expansion targets (predefined per-format expansion goals)
2. Capability gap ledger (reports/capability-layer/gap-ledger.json)
3. Source code introspection (detects missing functions)

Outputs:
  product-task-candidates.json   â€” top N scored tasks ready for queue dispatch
"""
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

_here = Path(__file__).resolve().parent
_REPO_ROOT = _here.parent.parent

# Default output path
DEFAULT_OUTPUT = _REPO_ROOT / "product-task-candidates.json"

# Per-format capability expansion goals: (format_name, function_name, action_type, pattern)
# These are functions known to be valuable but not yet in poc-targets.yaml
_EXPANSION_GOALS: List[Dict[str, Any]] = [
    {
        "format": "fodg",
        "function_name": "export_to_csv",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "export_csv",
        "source_file": "src/python/fodg/fodg_codec.py",
        "test_file": "tests/python/fodg/test_r130_fodg_csv_export.py",
        "spec_authority": "schema_authority_available",
        "product_value": 4,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Export FODG drawing to CSV (shape metadata per row)",
    },
    {
        "format": "tsv",
        "function_name": "append_row",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "append_mutation",
        "source_file": "src/python/tsv/tsv_parser.py",
        "test_file": "tests/python/tsv/test_r130_tsv_append_row.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 4,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Append a row to a TSV document in-memory and return bytes",
    },
    {
        "format": "ndjson",
        "function_name": "validate_schema",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "validator",
        "source_file": "src/python/ndjson/ndjson_codec.py",
        "test_file": "tests/python/ndjson/test_r130_ndjson_validate_schema.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Validate each NDJSON record against a provided dict schema",
    },
    {
        "format": "abw",
        "function_name": "search_paragraph",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/abw/abw_codec.py",
        "test_file": "tests/python/abw/test_r130_abw_search_paragraph.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Search for paragraphs matching a query string; return list of indices",
    },
    {
        "format": "gnumeric",
        "function_name": "delete_sheet",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "mutation",
        "source_file": "src/python/gnumeric/gnumeric_codec.py",
        "test_file": "tests/python/gnumeric/test_r130_gnumeric_delete_sheet.py",
        "spec_authority": "schema_authority_available",
        "product_value": 2,
        "autonomy_value": 2,
        "risk_level": "LOW",
        "description": "Delete a sheet by index from a Gnumeric document model",
    },
    {
        "format": "fodg",
        "function_name": "roundtrip",
        "action_type": "RUN_TARGETED_PYTEST",
        "pattern": "roundtrip_test",
        "source_file": "src/python/fodg/fodg_codec.py",
        "test_file": "tests/python/fodg/test_r131_fodg_roundtrip.py",
        "spec_authority": "schema_authority_available",
        "product_value": 3,
        "autonomy_value": 2,
        "risk_level": "LOW",
        "description": "Load â†’ write â†’ reload FODG roundtrip test",
    },
    {
        "format": "ndjson",
        "function_name": "roundtrip",
        "action_type": "RUN_TARGETED_PYTEST",
        "pattern": "roundtrip_test",
        "source_file": "src/python/ndjson/ndjson_codec.py",
        "test_file": "tests/python/ndjson/test_r131_ndjson_roundtrip.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 3,
        "autonomy_value": 2,
        "risk_level": "LOW",
        "description": "Load â†’ modify â†’ write_ndjson â†’ reload NDJSON roundtrip test",
    },
    {
        "format": "tsv",
        "function_name": "roundtrip",
        "action_type": "RUN_TARGETED_PYTEST",
        "pattern": "roundtrip_test",
        "source_file": "src/python/tsv/tsv_parser.py",
        "test_file": "tests/python/tsv/test_r131_tsv_roundtrip.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 2,
        "autonomy_value": 2,
        "risk_level": "LOW",
        "description": "Load â†’ write_tsv â†’ reload â†’ compare headers roundtrip test",
    },
    {
        "format": "abw",
        "function_name": "search_replace_paragraph",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "mutation",
        "source_file": "src/python/abw/abw_codec.py",
        "test_file": "tests/python/abw/test_r131_abw_search_replace.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 3,
        "autonomy_value": 2,
        "risk_level": "MEDIUM",
        "description": "Search and replace text within ABW paragraphs",
    },
    {
        "format": "gnumeric",
        "function_name": "rename_sheet",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "mutation",
        "source_file": "src/python/gnumeric/gnumeric_codec.py",
        "test_file": "tests/python/gnumeric/test_r131_gnumeric_rename_sheet.py",
        "spec_authority": "schema_authority_available",
        "product_value": 2,
        "autonomy_value": 2,
        "risk_level": "LOW",
        "description": "Rename a sheet in a Gnumeric document model",
    },
    {
        "format": "ndjson",
        "function_name": "export_to_csv",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "export_csv",
        "source_file": "src/python/ndjson/ndjson_codec.py",
        "test_file": "tests/python/ndjson/test_r132_ndjson_csv_export2.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 3,
        "autonomy_value": 2,
        "risk_level": "LOW",
        "description": "Export NDJSON records to CSV (deepen existing export_to_csv)",
    },
    {
        "format": "tsv",
        "function_name": "write_tsv_strict",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "writer",
        "source_file": "src/python/tsv/tsv_parser.py",
        "test_file": "tests/python/tsv/test_r132_tsv_write_strict.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 2,
        "autonomy_value": 2,
        "risk_level": "LOW",
        "description": "Write TSV with strict field quoting and encoding options",
    },
    {
        "format": "abw",
        "function_name": "export_to_html",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "export_html",
        "source_file": "src/python/abw/abw_codec.py",
        "test_file": "tests/python/abw/test_r132_abw_html_export.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 3,
        "autonomy_value": 2,
        "risk_level": "LOW",
        "description": "Export ABW document sections to HTML string",
    },
    {
        "format": "gnumeric",
        "function_name": "get_row",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/gnumeric/gnumeric_codec.py",
        "test_file": "tests/python/gnumeric/test_r132_gnumeric_get_row.py",
        "spec_authority": "schema_authority_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Get all cell values for a row in a Gnumeric sheet by row index",
    },
    {
        "format": "fodg",
        "function_name": "export_to_txt",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "export_txt",
        "source_file": "src/python/fodg/fodg_codec.py",
        "test_file": "tests/python/fodg/test_r132_fodg_txt_export_deepen.py",
        "spec_authority": "schema_authority_available",
        "product_value": 2,
        "autonomy_value": 2,
        "risk_level": "LOW",
        "description": "Deepen export_to_txt: include shape type annotations",
    },
    {
        "format": "ndjson",
        "function_name": "count_records",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/ndjson/ndjson_codec.py",
        "test_file": "tests/python/ndjson/test_r133_ndjson_count.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 2,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Count records in an NDJSON stream efficiently",
    },
    {
        "format": "tsv",
        "function_name": "get_column",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/tsv/tsv_parser.py",
        "test_file": "tests/python/tsv/test_r133_tsv_get_column.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Get all values for a named column from a TSV document",
    },
    {
        "format": "abw",
        "function_name": "get_word_count",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/abw/abw_codec.py",
        "test_file": "tests/python/abw/test_r133_abw_word_count.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 2,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Return total word count across all ABW document paragraphs",
    },
    {
        "format": "gnumeric",
        "function_name": "get_column",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/gnumeric/gnumeric_codec.py",
        "test_file": "tests/python/gnumeric/test_r133_gnumeric_get_column.py",
        "spec_authority": "schema_authority_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Get all cell values for a column in a Gnumeric sheet by column index",
    },
    {
        "format": "fodg",
        "function_name": "get_shapes",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/fodg/fodg_codec.py",
        "test_file": "tests/python/fodg/test_r133_fodg_get_shapes.py",
        "spec_authority": "schema_authority_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Return list of shape metadata dicts from a FODG drawing",
    },
    # --- Sprint 4 expansion goals ---
    {
        "format": "abw",
        "function_name": "merge_abw",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "mutation",
        "source_file": "src/python/abw/abw_codec.py",
        "test_file": "tests/python/abw/test_r136_abw_merge.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Merge two ABW document models into one (concatenate paragraphs)",
    },
    {
        "format": "gnumeric",
        "function_name": "get_sheet_by_name",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/gnumeric/gnumeric_codec.py",
        "test_file": "tests/python/gnumeric/test_r136_gnumeric_get_sheet_by_name.py",
        "spec_authority": "schema_authority_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Find and return a sheet dict from a Gnumeric model by name",
    },
    {
        "format": "gnumeric",
        "function_name": "add_sheet",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "mutation",
        "source_file": "src/python/gnumeric/gnumeric_codec.py",
        "test_file": "tests/python/gnumeric/test_r136_gnumeric_add_sheet.py",
        "spec_authority": "schema_authority_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Add a new empty sheet to a Gnumeric workbook model",
    },
    {
        "format": "tsv",
        "function_name": "get_row",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/tsv/tsv_parser.py",
        "test_file": "tests/python/tsv/test_r136_tsv_get_row.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Return a list of cell values for a given row index from a TSV source",
    },
    {
        "format": "ndjson",
        "function_name": "merge_ndjson",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "mutation",
        "source_file": "src/python/ndjson/ndjson_codec.py",
        "test_file": "tests/python/ndjson/test_r136_ndjson_merge.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Merge records from two NDJSON sources into a single list",
    },
    {
        "format": "gnumeric",
        "function_name": "copy_sheet",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "mutation",
        "source_file": "src/python/gnumeric/gnumeric_codec.py",
        "test_file": "tests/python/gnumeric/test_r137_gnumeric_copy_sheet.py",
        "spec_authority": "schema_authority_available",
        "product_value": 2,
        "autonomy_value": 2,
        "risk_level": "LOW",
        "description": "Copy a sheet by index within a Gnumeric workbook model",
    },
    {
        "format": "tsv",
        "function_name": "validate_headers",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "validator",
        "source_file": "src/python/tsv/tsv_parser.py",
        "test_file": "tests/python/tsv/test_r137_tsv_validate_headers.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 2,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Validate TSV headers against an expected list; return missing/extra headers",
    },
    {
        "format": "fodg",
        "function_name": "get_page_by_name",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/fodg/fodg_codec.py",
        "test_file": "tests/python/fodg/test_r136_fodg_get_page_by_name.py",
        "spec_authority": "schema_authority_available",
        "product_value": 2,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Return page metadata dict by page name from a FODG drawing model",
    },
    {
        "format": "ndjson",
        "function_name": "group_by",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/ndjson/ndjson_codec.py",
        "test_file": "tests/python/ndjson/test_r136_ndjson_group_by.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 3,
        "autonomy_value": 2,
        "risk_level": "LOW",
        "description": "Group NDJSON records by a field value; return dict of lists",
    },
    {
        "format": "abw",
        "function_name": "word_frequency",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/abw/abw_codec.py",
        "test_file": "tests/python/abw/test_r137_abw_word_frequency.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 2,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Return word frequency dict (word -> count) across all ABW paragraphs",
    },
    # --- Sprint 12 expansion goals ---
    {
        "format": "abw",
        "function_name": "count_words",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/abw/abw_codec.py",
        "test_file": "tests/python/abw/test_r152_abw_count_words.py",
        "spec_authority": "schema_authority_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Return total word count across all paragraphs in the ABW model",
    },
    {
        "format": "abw",
        "function_name": "paragraph_at",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/abw/abw_codec.py",
        "test_file": "tests/python/abw/test_r152_abw_paragraph_at.py",
        "spec_authority": "schema_authority_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Return paragraph at a given index; raise IndexError if out of range",
    },
    {
        "format": "gnumeric",
        "function_name": "sheet_names",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/gnumeric/gnumeric_codec.py",
        "test_file": "tests/python/gnumeric/test_r152_gnumeric_sheet_names.py",
        "spec_authority": "schema_authority_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Return list of sheet names from Gnumeric model",
    },
    {
        "format": "gnumeric",
        "function_name": "row_count",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/gnumeric/gnumeric_codec.py",
        "test_file": "tests/python/gnumeric/test_r152_gnumeric_row_count.py",
        "spec_authority": "schema_authority_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Return the number of rows with data in a Gnumeric sheet",
    },
    {
        "format": "tsv",
        "function_name": "filter_rows",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "filter",
        "source_file": "src/python/tsv/tsv_parser.py",
        "test_file": "tests/python/tsv/test_r152_tsv_filter_rows.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 4,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Filter TSV rows where a column value matches a predicate",
    },
    {
        "format": "tsv",
        "function_name": "column_count",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/tsv/tsv_parser.py",
        "test_file": "tests/python/tsv/test_r152_tsv_column_count.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Return the number of columns (headers) in a TSV source",
    },
    {
        "format": "ndjson",
        "function_name": "head",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/ndjson/ndjson_codec.py",
        "test_file": "tests/python/ndjson/test_r152_ndjson_head.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Return first N records from NDJSON source",
    },
    {
        "format": "ndjson",
        "function_name": "sum_field",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "aggregator",
        "source_file": "src/python/ndjson/ndjson_codec.py",
        "test_file": "tests/python/ndjson/test_r152_ndjson_sum_field.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Sum numeric values for a field across all NDJSON records",
    },
    {
        "format": "fodg",
        "function_name": "rename_page",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "mutation",
        "source_file": "src/python/fodg/fodg_codec.py",
        "test_file": "tests/python/fodg/test_r152_fodg_rename_page.py",
        "spec_authority": "schema_authority_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Rename a page in the FODG model by index; returns new model",
    },
    {
        "format": "fodg",
        "function_name": "add_page",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "mutation",
        "source_file": "src/python/fodg/fodg_codec.py",
        "test_file": "tests/python/fodg/test_r152_fodg_add_page.py",
        "spec_authority": "schema_authority_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Add a new blank page to the FODG model; returns new model",
    },
    # --- Sprint 11 expansion goals ---
    {
        "format": "abw",
        "function_name": "first_paragraph",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/abw/abw_codec.py",
        "test_file": "tests/python/abw/test_r150_abw_first_paragraph.py",
        "description": "Return first paragraph text; empty string if no paragraphs",
    },
    {
        "format": "abw",
        "function_name": "last_paragraph",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/abw/abw_codec.py",
        "test_file": "tests/python/abw/test_r150_abw_last_paragraph.py",
        "description": "Return last paragraph text; empty string if no paragraphs",
    },
    {
        "format": "gnumeric",
        "function_name": "get_sheet_as_rows",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/gnumeric/gnumeric_codec.py",
        "test_file": "tests/python/gnumeric/test_r150_gnumeric_sheet_as_rows.py",
        "description": "Return sheet cells as a list of row lists (row-major, str values)",
    },
    {
        "format": "gnumeric",
        "function_name": "fill_row",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "mutation",
        "source_file": "src/python/gnumeric/gnumeric_codec.py",
        "test_file": "tests/python/gnumeric/test_r150_gnumeric_fill_row.py",
        "description": "Fill a row with a list of string values starting at col 0",
    },
    {
        "format": "tsv",
        "function_name": "get_column_values",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/tsv/tsv_parser.py",
        "test_file": "tests/python/tsv/test_r150_tsv_column_values.py",
        "description": "Return all values in a named column as a list of strings",
    },
    {
        "format": "tsv",
        "function_name": "max_column_tsv",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "aggregate",
        "source_file": "src/python/tsv/tsv_parser.py",
        "test_file": "tests/python/tsv/test_r150_tsv_max_column.py",
        "description": "Return maximum numeric value in a named TSV column",
    },
    {
        "format": "ndjson",
        "function_name": "rename_field",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "mutation",
        "source_file": "src/python/ndjson/ndjson_codec.py",
        "test_file": "tests/python/ndjson/test_r150_ndjson_rename_field.py",
        "description": "Rename a field in all NDJSON records; skip records without the field",
    },
    {
        "format": "ndjson",
        "function_name": "average_value",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "aggregate",
        "source_file": "src/python/ndjson/ndjson_codec.py",
        "test_file": "tests/python/ndjson/test_r150_ndjson_average_value.py",
        "description": "Return float average of numeric values for a field; None if no values",
    },
    {
        "format": "fodg",
        "function_name": "page_names",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/fodg/fodg_codec.py",
        "test_file": "tests/python/fodg/test_r150_fodg_page_names.py",
        "description": "Return list of all page names in order",
    },
    {
        "format": "fodg",
        "function_name": "has_page",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/fodg/fodg_codec.py",
        "test_file": "tests/python/fodg/test_r150_fodg_has_page.py",
        "description": "Return True if a page with the given name exists in the model",
    },
    # --- Sprint 10 expansion goals ---
    {
        "format": "abw",
        "function_name": "word_wrap",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "mutation",
        "source_file": "src/python/abw/abw_codec.py",
        "test_file": "tests/python/abw/test_r148_abw_word_wrap.py",
        "description": "Wrap each paragraph at word boundaries to a max line width; return new model",
    },
    {
        "format": "abw",
        "function_name": "has_paragraph",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/abw/abw_codec.py",
        "test_file": "tests/python/abw/test_r148_abw_has_paragraph.py",
        "description": "Return True if any paragraph exactly matches the given text",
    },
    {
        "format": "gnumeric",
        "function_name": "get_all_values",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/gnumeric/gnumeric_codec.py",
        "test_file": "tests/python/gnumeric/test_r148_gnumeric_get_all_values.py",
        "description": "Return flat list of all cell values in a sheet, row-major order",
    },
    {
        "format": "gnumeric",
        "function_name": "clear_sheet",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "mutation",
        "source_file": "src/python/gnumeric/gnumeric_codec.py",
        "test_file": "tests/python/gnumeric/test_r148_gnumeric_clear_sheet.py",
        "description": "Remove all cell values from a sheet; return updated model",
    },
    {
        "format": "tsv",
        "function_name": "merge_tsv",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "mutation",
        "source_file": "src/python/tsv/tsv_parser.py",
        "test_file": "tests/python/tsv/test_r148_tsv_merge.py",
        "description": "Concatenate rows from two TSV sources with compatible headers",
    },
    {
        "format": "tsv",
        "function_name": "min_column_tsv",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "aggregate",
        "source_file": "src/python/tsv/tsv_parser.py",
        "test_file": "tests/python/tsv/test_r148_tsv_min_column.py",
        "description": "Return minimum numeric value in a named TSV column",
    },
    {
        "format": "ndjson",
        "function_name": "min_value",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "aggregate",
        "source_file": "src/python/ndjson/ndjson_codec.py",
        "test_file": "tests/python/ndjson/test_r148_ndjson_min_value.py",
        "description": "Return the minimum value for a field across all records; None if no values",
    },
    {
        "format": "ndjson",
        "function_name": "zip_records",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "mutation",
        "source_file": "src/python/ndjson/ndjson_codec.py",
        "test_file": "tests/python/ndjson/test_r148_ndjson_zip_records.py",
        "description": "Zip two record lists by position into merged dicts; stop at shorter list",
    },
    {
        "format": "fodg",
        "function_name": "clear_page",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "mutation",
        "source_file": "src/python/fodg/fodg_codec.py",
        "test_file": "tests/python/fodg/test_r148_fodg_clear_page.py",
        "description": "Remove all shapes from a page; return updated model",
    },
    {
        "format": "fodg",
        "function_name": "swap_pages",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "mutation",
        "source_file": "src/python/fodg/fodg_codec.py",
        "test_file": "tests/python/fodg/test_r148_fodg_swap_pages.py",
        "description": "Swap two pages by index; return updated model",
    },
    # --- Sprint 9 expansion goals ---
    {
        "format": "abw",
        "function_name": "reverse_paragraphs",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "mutation",
        "source_file": "src/python/abw/abw_codec.py",
        "test_file": "tests/python/abw/test_r146_abw_reverse_paragraphs.py",
        "description": "Return new ABW model with paragraphs in reversed order",
    },
    {
        "format": "abw",
        "function_name": "paragraph_lengths",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/abw/abw_codec.py",
        "test_file": "tests/python/abw/test_r146_abw_paragraph_lengths.py",
        "description": "Return list of character lengths per paragraph",
    },
    {
        "format": "gnumeric",
        "function_name": "fill_column",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "mutation",
        "source_file": "src/python/gnumeric/gnumeric_codec.py",
        "test_file": "tests/python/gnumeric/test_r146_gnumeric_fill_column.py",
        "description": "Fill a column with a list of string values starting at row 0",
    },
    {
        "format": "gnumeric",
        "function_name": "sum_row",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "aggregate",
        "source_file": "src/python/gnumeric/gnumeric_codec.py",
        "test_file": "tests/python/gnumeric/test_r146_gnumeric_sum_row.py",
        "description": "Sum numeric values in a row (row index); skip non-numeric cells",
    },
    {
        "format": "tsv",
        "function_name": "sample_rows",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/tsv/tsv_parser.py",
        "test_file": "tests/python/tsv/test_r146_tsv_sample_rows.py",
        "description": "Return TSV model with only the first n data rows",
    },
    {
        "format": "tsv",
        "function_name": "sum_column_tsv",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "aggregate",
        "source_file": "src/python/tsv/tsv_parser.py",
        "test_file": "tests/python/tsv/test_r146_tsv_sum_column.py",
        "description": "Sum numeric values in a named TSV column; skip non-numeric cells",
    },
    {
        "format": "ndjson",
        "function_name": "count_by",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "aggregate",
        "source_file": "src/python/ndjson/ndjson_codec.py",
        "test_file": "tests/python/ndjson/test_r146_ndjson_count_by.py",
        "description": "Count occurrences of each unique value for a field; return dict",
    },
    {
        "format": "ndjson",
        "function_name": "max_value",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "aggregate",
        "source_file": "src/python/ndjson/ndjson_codec.py",
        "test_file": "tests/python/ndjson/test_r146_ndjson_max_value.py",
        "description": "Return the maximum value for a field across all records; None if no values",
    },
    {
        "format": "fodg",
        "function_name": "get_page_index",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/fodg/fodg_codec.py",
        "test_file": "tests/python/fodg/test_r146_fodg_page_index.py",
        "description": "Return zero-based index of a page by name; raise KeyError if not found",
    },
    {
        "format": "fodg",
        "function_name": "duplicate_page",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "mutation",
        "source_file": "src/python/fodg/fodg_codec.py",
        "test_file": "tests/python/fodg/test_r146_fodg_duplicate_page.py",
        "description": "Append a copy of a page (by index) to the end of the pages list",
    },
    # --- Sprint 8 expansion goals ---
    {
        "format": "abw",
        "function_name": "export_to_markdown",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "export",
        "source_file": "src/python/abw/abw_codec.py",
        "test_file": "tests/python/abw/test_r144_abw_export_markdown.py",
        "description": "Export ABW model to Markdown string (paragraphs as lines with blank line between)",
    },
    {
        "format": "abw",
        "function_name": "get_paragraph_at",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/abw/abw_codec.py",
        "test_file": "tests/python/abw/test_r144_abw_paragraph_at.py",
        "description": "Return single paragraph text by index; raise IndexError if out of range",
    },
    {
        "format": "gnumeric",
        "function_name": "sum_column",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "aggregate",
        "source_file": "src/python/gnumeric/gnumeric_codec.py",
        "test_file": "tests/python/gnumeric/test_r144_gnumeric_sum_column.py",
        "description": "Sum numeric values in a column (col index); skip non-numeric cells",
    },
    {
        "format": "gnumeric",
        "function_name": "get_sheet_index",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/gnumeric/gnumeric_codec.py",
        "test_file": "tests/python/gnumeric/test_r144_gnumeric_sheet_index.py",
        "description": "Return sheet index by name; raise KeyError if not found",
    },
    {
        "format": "tsv",
        "function_name": "sort_rows",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "mutation",
        "source_file": "src/python/tsv/tsv_parser.py",
        "test_file": "tests/python/tsv/test_r144_tsv_sort_rows.py",
        "description": "Sort TSV rows by named column; return updated model dict",
    },
    {
        "format": "tsv",
        "function_name": "drop_column",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "mutation",
        "source_file": "src/python/tsv/tsv_parser.py",
        "test_file": "tests/python/tsv/test_r144_tsv_drop_column.py",
        "description": "Remove a column by name from TSV; raise TsvError if column not found",
    },
    {
        "format": "ndjson",
        "function_name": "pick",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "projection",
        "source_file": "src/python/ndjson/ndjson_codec.py",
        "test_file": "tests/python/ndjson/test_r144_ndjson_pick.py",
        "description": "Project only specified fields from each record; missing fields omitted",
    },
    {
        "format": "ndjson",
        "function_name": "distinct_values",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/ndjson/ndjson_codec.py",
        "test_file": "tests/python/ndjson/test_r144_ndjson_distinct_values.py",
        "description": "Return list of unique values for a field across all records",
    },
    {
        "format": "fodg",
        "function_name": "count_shapes",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/fodg/fodg_codec.py",
        "test_file": "tests/python/fodg/test_r144_fodg_count_shapes.py",
        "description": "Count total shapes across all pages in FODG model",
    },
    {
        "format": "fodg",
        "function_name": "export_to_json",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "export",
        "source_file": "src/python/fodg/fodg_codec.py",
        "test_file": "tests/python/fodg/test_r144_fodg_export_json.py",
        "description": "Export FODG model to JSON string representation",
    },
    # --- Sprint 7 expansion goals ---
    {
        "format": "abw",
        "function_name": "get_char_count",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/abw/abw_codec.py",
        "test_file": "tests/python/abw/test_r142_abw_char_count.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Return total character count across all ABW document paragraphs",
    },
    {
        "format": "gnumeric",
        "function_name": "get_column",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/gnumeric/gnumeric_codec.py",
        "test_file": "tests/python/gnumeric/test_r142_gnumeric_get_column.py",
        "spec_authority": "schema_authority_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Return all cell values for a column index in a Gnumeric sheet",
    },
    {
        "format": "tsv",
        "function_name": "filter_rows",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/tsv/tsv_parser.py",
        "test_file": "tests/python/tsv/test_r142_tsv_filter_rows.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Return all rows where a named column equals a given value",
    },
    {
        "format": "ndjson",
        "function_name": "sort_by",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/ndjson/ndjson_codec.py",
        "test_file": "tests/python/ndjson/test_r142_ndjson_sort_by.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Sort NDJSON records by a field value; return sorted list",
    },
    {
        "format": "fodg",
        "function_name": "get_page_count",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/fodg/fodg_codec.py",
        "test_file": "tests/python/fodg/test_r142_fodg_get_page_count.py",
        "spec_authority": "schema_authority_available",
        "product_value": 2,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Return the number of pages in a FODG drawing model",
    },
    {
        "format": "ndjson",
        "function_name": "aggregate",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/ndjson/ndjson_codec.py",
        "test_file": "tests/python/ndjson/test_r142_ndjson_aggregate.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Aggregate NDJSON field values: sum, count, min, or max",
    },
    {
        "format": "tsv",
        "function_name": "add_column",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "mutation",
        "source_file": "src/python/tsv/tsv_parser.py",
        "test_file": "tests/python/tsv/test_r142_tsv_add_column.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Return new TSV model with an additional column of values",
    },
    {
        "format": "abw",
        "function_name": "replace_in_paragraphs",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "mutation",
        "source_file": "src/python/abw/abw_codec.py",
        "test_file": "tests/python/abw/test_r142_abw_replace.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Return a new ABW model with all occurrences of old_text replaced by new_text",
    },
    {
        "format": "gnumeric",
        "function_name": "get_row",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/gnumeric/gnumeric_codec.py",
        "test_file": "tests/python/gnumeric/test_r142_gnumeric_get_row.py",
        "spec_authority": "schema_authority_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Return all cell values for a row index in a Gnumeric sheet",
    },
    {
        "format": "fodg",
        "function_name": "get_all_text",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/fodg/fodg_codec.py",
        "test_file": "tests/python/fodg/test_r142_fodg_get_all_text.py",
        "spec_authority": "schema_authority_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Return a flat list of all non-empty text strings across all FODG pages",
    },
    {
        "format": "abw",
        "function_name": "join_paragraphs",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/abw/abw_codec.py",
        "test_file": "tests/python/abw/test_r142_abw_join_paragraphs.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 2,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Join all ABW paragraphs into a single string with a separator",
    },
    {
        "format": "gnumeric",
        "function_name": "count_nonempty_cells",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/gnumeric/gnumeric_codec.py",
        "test_file": "tests/python/gnumeric/test_r142_gnumeric_count_nonempty.py",
        "spec_authority": "schema_authority_available",
        "product_value": 2,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Count cells with non-empty values in a Gnumeric sheet",
    },
    {
        "format": "tsv",
        "function_name": "rename_column",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "mutation",
        "source_file": "src/python/tsv/tsv_parser.py",
        "test_file": "tests/python/tsv/test_r142_tsv_rename_column.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 2,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Return a new TSV model with a column renamed in the header row",
    },
    {
        "format": "ndjson",
        "function_name": "to_jsonl_str",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "writer",
        "source_file": "src/python/ndjson/ndjson_codec.py",
        "test_file": "tests/python/ndjson/test_r142_ndjson_to_jsonl_str.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Serialize a list of records to a NDJSON/JSONL string",
    },
    # --- Sprint 6 expansion goals ---
    {
        "format": "abw",
        "function_name": "split_paragraphs",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "mutation",
        "source_file": "src/python/abw/abw_codec.py",
        "test_file": "tests/python/abw/test_r140_abw_split_paragraphs.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Split ABW paragraphs into chunks of chunk_size; return list of ABW models",
    },
    {
        "format": "gnumeric",
        "function_name": "get_column_count",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/gnumeric/gnumeric_codec.py",
        "test_file": "tests/python/gnumeric/test_r140_gnumeric_column_count.py",
        "spec_authority": "schema_authority_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Return the number of distinct populated columns in a Gnumeric sheet",
    },
    {
        "format": "tsv",
        "function_name": "deduplicate_rows",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "mutation",
        "source_file": "src/python/tsv/tsv_parser.py",
        "test_file": "tests/python/tsv/test_r140_tsv_deduplicate_rows.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Remove duplicate data rows from a TSV source; return list of unique rows",
    },
    {
        "format": "ndjson",
        "function_name": "tail",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/ndjson/ndjson_codec.py",
        "test_file": "tests/python/ndjson/test_r140_ndjson_tail.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Return the last N records from an NDJSON source",
    },
    {
        "format": "fodg",
        "function_name": "remove_page",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "mutation",
        "source_file": "src/python/fodg/fodg_codec.py",
        "test_file": "tests/python/fodg/test_r140_fodg_remove_page.py",
        "spec_authority": "schema_authority_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Return a new FODG model with a page removed by index",
    },
    {
        "format": "ndjson",
        "function_name": "pluck",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/ndjson/ndjson_codec.py",
        "test_file": "tests/python/ndjson/test_r140_ndjson_pluck.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Extract single field values from NDJSON records as a flat list",
    },
    {
        "format": "tsv",
        "function_name": "get_row_by_key",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/tsv/tsv_parser.py",
        "test_file": "tests/python/tsv/test_r140_tsv_get_row_by_key.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Find the first row where a named column equals a given value",
    },
    {
        "format": "abw",
        "function_name": "append_paragraph",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "mutation",
        "source_file": "src/python/abw/abw_codec.py",
        "test_file": "tests/python/abw/test_r140_abw_append_paragraph.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Return a new ABW model with an additional paragraph appended",
    },
    {
        "format": "gnumeric",
        "function_name": "read_cell",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/gnumeric/gnumeric_codec.py",
        "test_file": "tests/python/gnumeric/test_r140_gnumeric_read_cell.py",
        "spec_authority": "schema_authority_available",
        "product_value": 4,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Return the value of a single cell from a Gnumeric sheet by (row, col)",
    },
    {
        "format": "fodg",
        "function_name": "rename_page",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "mutation",
        "source_file": "src/python/fodg/fodg_codec.py",
        "test_file": "tests/python/fodg/test_r140_fodg_rename_page.py",
        "spec_authority": "schema_authority_available",
        "product_value": 2,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Return a new FODG model with a page renamed by index",
    },
    # --- Sprint 5 expansion goals ---
    {
        "format": "abw",
        "function_name": "get_unique_words",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/abw/abw_codec.py",
        "test_file": "tests/python/abw/test_r138_abw_unique_words.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Return sorted list of unique words across all ABW paragraphs",
    },
    {
        "format": "abw",
        "function_name": "truncate_paragraphs",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "mutation",
        "source_file": "src/python/abw/abw_codec.py",
        "test_file": "tests/python/abw/test_r138_abw_truncate.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 2,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Return a new ABW model with at most max_count paragraphs",
    },
    {
        "format": "gnumeric",
        "function_name": "clear_cell",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "mutation",
        "source_file": "src/python/gnumeric/gnumeric_codec.py",
        "test_file": "tests/python/gnumeric/test_r138_gnumeric_clear_cell.py",
        "spec_authority": "schema_authority_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Set a specific cell to empty string in a Gnumeric workbook model",
    },
    {
        "format": "gnumeric",
        "function_name": "get_row_count",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/gnumeric/gnumeric_codec.py",
        "test_file": "tests/python/gnumeric/test_r138_gnumeric_row_count.py",
        "spec_authority": "schema_authority_available",
        "product_value": 2,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Return the number of populated rows in a given sheet",
    },
    {
        "format": "tsv",
        "function_name": "count_rows",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/tsv/tsv_parser.py",
        "test_file": "tests/python/tsv/test_r138_tsv_count_rows.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Return the number of data rows in a TSV source (excluding header)",
    },
    {
        "format": "tsv",
        "function_name": "to_csv",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "export_csv",
        "source_file": "src/python/tsv/tsv_parser.py",
        "test_file": "tests/python/tsv/test_r138_tsv_to_csv.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 4,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Convert a TSV source to a CSV string (comma-separated)",
    },
    {
        "format": "ndjson",
        "function_name": "deduplicate",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "mutation",
        "source_file": "src/python/ndjson/ndjson_codec.py",
        "test_file": "tests/python/ndjson/test_r138_ndjson_deduplicate.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Remove duplicate NDJSON records by a field key; keep first occurrence",
    },
    {
        "format": "ndjson",
        "function_name": "head",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/ndjson/ndjson_codec.py",
        "test_file": "tests/python/ndjson/test_r138_ndjson_head.py",
        "spec_authority": "no_public_spec_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Return the first N records from an NDJSON source",
    },
    {
        "format": "fodg",
        "function_name": "get_text_shapes",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "getter",
        "source_file": "src/python/fodg/fodg_codec.py",
        "test_file": "tests/python/fodg/test_r138_fodg_text_shapes.py",
        "spec_authority": "schema_authority_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Return only shapes that contain non-empty text from a FODG drawing model",
    },
    {
        "format": "fodg",
        "function_name": "add_page",
        "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
        "pattern": "mutation",
        "source_file": "src/python/fodg/fodg_codec.py",
        "test_file": "tests/python/fodg/test_r138_fodg_add_page.py",
        "spec_authority": "schema_authority_available",
        "product_value": 3,
        "autonomy_value": 3,
        "risk_level": "LOW",
        "description": "Return a new FODG model with an additional page appended",
    },
]

# Global forbidden paths for all generated tasks
_GLOBAL_FORBIDDEN = [
    "src/net/",
    "registry/",
    "product-capability-matrix/poc-targets.yaml",
    ".supervisor/",
    "AGENTS.md",
    "GOVERNANCE.md",
]


_GAP_LEDGER_PATH = _REPO_ROOT / "reports" / "capability-layer" / "gap-ledger.json"
_SAL_FACTS_PATH = _REPO_ROOT / ".local" / "sal-output" / "sal-facts-latest.json"

# Format name â†’ Python source module mapping for gap-ledger integration
_FORMAT_SOURCE_MAP: Dict[str, str] = {
    "FODS": "src/python/fods/__init__.py",
    "FODT": "src/python/fodt/__init__.py",
    "ZST": "src/python/zst/zst_codec.py",
    "ODS": "src/python/ods/ods_parser.py",
    "ABW": "src/python/abw/abw_codec.py",
    "NDJSON": "src/python/ndjson/ndjson_codec.py",
    "TSV": "src/python/tsv/tsv_parser.py",
    "CSV": "src/python/csv/csv_parser.py",
    "DIF": "src/python/dif/dif_parser.py",
    "SYLK": "src/python/sylk/sylk_parser.py",
    "FODG": "src/python/fodg/fodg_codec.py",
    "FODP": "src/python/fodp/fodp_codec.py",
    "GNUMERIC": "src/python/gnumeric/gnumeric_codec.py",
    "QOI": "src/python/qoi/qoi_parser.py",
    "PBM": "src/python/pbm/pbm_parser.py",
    "PGM": "src/python/pgm/pgm_parser.py",
    "PPM": "src/python/ppm/ppm_parser.py",
    "XCF": "src/python/xcf/xcf_parser.py",
    "TOML": "src/python/toml/toml_codec.py",
}


def _load_gap_ledger_goals(
    require_spec_facts: bool = False,
    exclude_gap_ids: "Optional[set]" = None,
) -> "tuple[List[Dict[str, Any]], bool]":
    """Load FOSS reduced gaps from gap-ledger.json as expansion goal dicts.

    Args:
        require_spec_facts: If True, only return gaps with spec_facts populated.
        exclude_gap_ids: Set of gap_ids to skip (from failure exclusion).

    Returns:
        tuple[list[dict], bool]: (goals_list, spec_grounded_available)
          - goals_list: list of goal dicts (may be empty if 0 open FOSS gaps)
          - spec_grounded_available: True if spec-grounded goals exist before filtering

    CRITICAL â€” TC-V4-009 (2026-06-25): This function returns a TUPLE, not a list.
    ALWAYS unpack: goals, spec_grounded = _load_gap_ledger_goals()
    NEVER call len() on the return value â€” len((list, bool)) == 2, not the goal count.
    FOSS depletion check: if len(goals) == 0 â†’ _expansion_goal_fallback = True.
    See: plans/velvet-hatching-lark.md TC-V4-009.
    """
    if not _GAP_LEDGER_PATH.exists():
        return [], False
    try:
        data = json.loads(_GAP_LEDGER_PATH.read_text(encoding="utf-8"))
        gaps = data.get("gaps", []) if isinstance(data, dict) else data
    except Exception:
        return [], False

    _excluded = exclude_gap_ids or set()
    spec_grounded_available = False
    goals = []
    for gap in gaps:
        # Only generate tasks for OPEN FOSS gaps with missing test coverage.
        # TC-FINDING-021 (2026-06-25): status filter was missing â€” caused all 1,130 CLOSED
        # foss_reduced/test_coverage gaps to be returned as "goals", making
        # _expansion_goal_fallback evaluate to False (wrong). Fixed by adding status check.
        if gap.get("status") != "open":
            continue
        if gap.get("product_type") != "foss_reduced":
            continue
        if gap.get("gap_type") not in ("missing_test_coverage", "no_test_coverage"):
            continue
        if gap.get("blockers"):
            continue  # Skip gated gaps

        gap_id = gap.get("gap_id", "")
        if gap_id in _excluded:
            continue

        fmt = gap.get("format", "").upper()
        cap_name = gap.get("capability_name", "")
        # Convert "Probe Csv" -> "probe_csv"
        fn = cap_name.lower().replace(" ", "_")
        if not fn or not fmt:
            continue

        source_file = _FORMAT_SOURCE_MAP.get(fmt)
        if not source_file:
            continue

        spec_facts = gap.get("spec_facts") or []
        if spec_facts:
            spec_grounded_available = True
        if require_spec_facts and not spec_facts:
            continue

        fmt_lower = fmt.lower()
        test_file = f"tests/python/{fmt_lower}/test_gap_{fn}.py"
        priority = gap.get("priority", "P2")
        product_value = {"P0": 5, "P1": 4, "P2": 3, "P3": 2}.get(priority, 2)

        goals.append({
            "format": fmt_lower,
            "function_name": fn,
            "action_type": "IMPLEMENT_SMALL_PRODUCT_FEATURE",
            "pattern": "test_coverage",
            "source_file": source_file,
            "test_file": test_file,
            "spec_authority": gap.get("notes", "no_spec_reference"),
            "product_value": product_value,
            "autonomy_value": 3,
            "risk_level": "LOW",
            "description": f"Close gap {gap_id}: add test coverage for {cap_name}",
            "gap_id": gap_id,
            "gap_source": "gap_ledger",
            "spec_facts": spec_facts,
        })

    # TC-C2-005-MONITORING-001 (2026-06-25): Depletion warning
    # Emit WARNING when open FOSS goals drop below threshold so depletion is caught early.
    # Depletion already occurred (0 goals as of 2026-06-25T12:31:44Z) without prior warning.
    # This prevents silent recurrence after TC-GAP-REGEN-001 restores new gaps.
    _DEPLETION_THRESHOLD = 10
    if len(goals) < _DEPLETION_THRESHOLD:
        import sys as _sys_monitor
        _msg = (
            f"WARNING [TC-C2-005-MONITORING]: FOSS DEPLETION â€” "
            f"only {len(goals)} open FOSS goals remain "
            f"(threshold={_DEPLETION_THRESHOLD}). "
            f"_expansion_goal_fallback will activate at 0. "
            f"Run TC-GAP-REGEN-001 to regenerate open FOSS gaps before depletion."
        )
        print(_msg, file=_sys_monitor.stderr)
        del _sys_monitor

    return goals, spec_grounded_available


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _function_exists_in_source(source_file: str, function_name: str) -> bool:
    """Check if function_name is already defined in source_file."""
    path = _REPO_ROOT / source_file
    if not path.exists():
        return False
    content = path.read_text(encoding="utf-8")
    return f"def {function_name}" in content


def _score_task(goal: Dict[str, Any]) -> float:
    """Compute priority score for a task (lower = higher priority)."""
    pv = goal.get("product_value", 1)
    av = goal.get("autonomy_value", 1)
    risk_penalty = {"LOW": 0, "MEDIUM": 1, "HIGH": 3}.get(goal.get("risk_level", "LOW"), 0)
    # Lower score = higher priority
    return 10.0 - (pv + av) + risk_penalty


def _goal_to_queue_item(goal: Dict[str, Any], run_number: int) -> Dict[str, Any]:
    """Convert an expansion goal to a queue-item-v2 dict."""
    fmt = goal["format"]
    fn = goal["function_name"]
    source_file = goal["source_file"]
    test_file = goal["test_file"]
    action_type = goal["action_type"]
    src_dir = "/".join(source_file.split("/")[:-1]) + "/"
    test_dir = "/".join(test_file.split("/")[:-1]) + "/"

    action_id = f"atg-{fmt}-{fn.replace('_', '-')}-{run_number:03d}"

    # TC-FALLBACK-REF-001: inject gap_ledger_ref so TC-GUARD-001 check passes.
    # Gap-ledger sourced items carry gap_id â€” use it directly.
    # Expansion fallback items get a synthetic EXPANSION-FALLBACK ref.
    if goal.get("gap_source") == "gap_ledger" and goal.get("gap_id"):
        _gap_ledger_ref = goal["gap_id"]
    else:
        _gap_ledger_ref = f"EXPANSION-FALLBACK-{fmt.upper()}-{fn}"

    return {
        "action_id": action_id,
        "action_type": action_type,
        "stream": "product",
        "lane": "product_feature",
        "priority": run_number,
        "source": f"capability_expansion:{fmt}-{fn}",
        "gap_ledger_ref": _gap_ledger_ref,
        "reason": goal["description"],
        "objective": f"Implement {fn}() for {fmt.upper()} format: {goal['description']}",
        "autonomy_value": goal.get("autonomy_value", 2),
        "product_value": goal.get("product_value", 2),
        "risk_level": goal.get("risk_level", "LOW"),
        "gate_classification": "LOCAL_AUTONOMOUS",
        "human_approval_required": False,
        "allowed_paths": [src_dir, test_dir],
        "forbidden_paths": _GLOBAL_FORBIDDEN,
        "expected_files_to_change": [source_file],
        "target_path": source_file,
        "expected_tests": [test_file],
        "expected_ledgers": ["reports/r90/product-code-change-ledger.json"],
        "expected_capability_updates": [f"{fmt.upper()}-{fn} -> test_verified"],
        "expected_spec_refs": [],
        "rollback_strategy": f"git checkout {source_file}",
        "max_attempts": 3,
        "repair_allowed": True,
        "evidence_required": True,
        "done_criteria": (
            f"pytest {test_file} passes; "
            f"{fn}() defined in {source_file}; "
            "ledger entry added"
        ),
        "status": "pending",
        "external_gate": False,
        "queued_at": None,
        "started_at": None,
        "completed_at": None,
        "result_path": None,
        "error": None,
        "sprint_id": None,
        "pattern": goal.get("pattern"),
        "spec_authority": goal.get("spec_authority"),
        "format": fmt,
        "function_name": fn,
        "advisory_only": goal.get("advisory_only", False),
        "compiled_taskcard_id": goal.get("compiled_taskcard_id"),
        "compiled_taskcard_path": goal.get("compiled_taskcard_path"),
    }


def generate_task_candidates(
    output_path: Optional[Path] = None,
    max_candidates: int = 20,
    skip_existing: bool = True,
) -> List[Dict[str, Any]]:
    """Generate product task candidates from expansion goals.

    Args:
        output_path: Where to write product-task-candidates.json (None = DEFAULT_OUTPUT)
        max_candidates: Maximum number of candidates to generate
        skip_existing: If True, skip functions already in source

    Returns:
        List of queue-item-v2 dicts (sorted by score)
    """
    output_path = output_path or DEFAULT_OUTPUT

    # Load failure exclusions from failure memory (RC-02 fix)
    _excluded_gap_ids: "set[str]" = set()
    try:
        import sys as _sys_atg
        _sup_dir = Path(__file__).resolve().parent
        if str(_sup_dir) not in _sys_atg.path:
            _sys_atg.path.insert(0, str(_sup_dir))
        from failure_memory import FailureMemory as _FM
        _excluded_gap_ids = _FM(repo_root=_REPO_ROOT).load_excluded_gap_ids()
    except Exception:
        pass

    # TC-MACH-CAP-002: Load selected gap IDs for priority boosting (extracted to extensions)
    _selected_gap_ids: "set" = set()
    try:
        from autonomous_cycle_extensions import load_selected_gap_ids
        _selected_gap_ids = load_selected_gap_ids(_REPO_ROOT)
    except Exception:
        pass

    # Lane 6: gap-ledger is PRIMARY; hardcoded goals demoted to fallback (missing fns only).
    # TC-SA-HEAL-006: require spec_facts for formats with â‰¥15 SAL facts (MIN_FACTS_T=15).
    _req_sf = _SAL_FACTS_PATH.exists() and any(len(e.get("spec_facts", [])) >= 15 for e in json.loads(_SAL_FACTS_PATH.read_text()).get("results", []))
    gap_ledger_goals, _spec_grounded_available = _load_gap_ledger_goals(
        require_spec_facts=_req_sf,
        exclude_gap_ids=_excluded_gap_ids,
    )
    _expansion_goal_fallback = len(gap_ledger_goals) == 0
    all_goals = list(gap_ledger_goals)  # gap-ledger goals first (primary)
    existing_fns = {g["function_name"] for g in all_goals}

    # TC-SH-003: Enrich goals with compiled gap taskcard metadata (extracted to extensions)
    try:
        from autonomous_cycle_extensions import enrich_goals_with_compiled_taskcards
        enrich_goals_with_compiled_taskcards(all_goals, _REPO_ROOT)
    except Exception:
        pass  # Compiled gap enrichment is best-effort

    # TC-GUARD-001-EXPANSION-001 Path A (stop-gap, 2026-06-25):
    # EXPANSION_GOALS are DISABLED even when _expansion_goal_fallback=True.
    # Root cause: ALL 114 hardcoded _EXPANSION_GOALS lack gap_ledger_ref, so TC-GUARD-001
    # blocks every one at Step 2d3 post-grade, creating an infinite rework loop.
    # V42 also does NOT block them (they don't match _mod_N_times_M pattern).
    # Fix: emit a WARNING; sprint runs honestly with 0 FOSS tasks until TC-GAP-REGEN-001
    # generates new open gaps in the ledger and sets _expansion_goal_fallback=False.
    # See: plans/velvet-hatching-lark.md FINDING-001, TC-GUARD-001-EXPANSION-001.
    if _expansion_goal_fallback:
        import sys as _sys_guard
        print(
            "WARNING [TC-GUARD-001-EXPANSION-001]: FOSS fallback active but "
            "EXPANSION_GOALS disabled â€” all 114 hardcoded goals lack gap_ledger_ref "
            "and would be blocked by TC-GUARD-001. Sprint continues with 0 FOSS tasks. "
            "Resolution: run TC-GAP-REGEN-001 to regenerate open FOSS gaps.",
            file=_sys_guard.stderr,
        )
        del _sys_guard
        # Do NOT add any hardcoded goals â€” they will be blocked by TC-GUARD-001.

    candidates = []
    advisory_skipped = 0
    for goal in all_goals:
        fn = goal["function_name"]
        source_file = goal["source_file"]

        # Lane 6: Skip advisory-only items â€” they cannot be executed as product work
        if goal.get("advisory_only", False):
            advisory_skipped += 1
            continue

        # Skip if function already in source
        if skip_existing and _function_exists_in_source(source_file, fn):
            continue

        candidates.append(goal)

    # TC-LEARN-001: Load failure escalations for scoring penalty.
    # Escalated failures increase the task score (lower priority) so other work runs first.
    # Penalty decays by 50% per 3 sprint cycles since last failure (prevents permanent demotion).
    _fm_escalations: "dict[str, dict]" = {}
    try:
        from failure_memory import FailureMemory as _FM_Score
        _fm_obj = _FM_Score(repo_root=_REPO_ROOT)
        _current_sprint_num = 0
        try:
            from pathlib import Path as _P
            _signal_path = _REPO_ROOT / ".local" / "supervisor" / "continuation-signal.json"
            import json as _json_tc
            _sig_data = _json_tc.loads(_signal_path.read_text(encoding="utf-8"))
            _current_sprint_num = _sig_data.get("iteration", 0)
        except Exception:
            pass
        for _entry in _fm_obj.find_escalated():
            _fmt = _entry.get("format", "") or ""
            _fn = _entry.get("function_name", "") or ""
            _last_sprint = _entry.get("last_seen_sprint", "") or ""
            # Estimate sprints since failure via iteration count (best-effort)
            _sprints_since = max(0, _current_sprint_num - (_entry.get("escalation_count", 1) * 2))
            # Decay: base_penalty=2.0, halved every 3 sprints
            _base_penalty = 2.0
            _decayed_penalty = _base_penalty * (0.5 ** (_sprints_since // 3))
            _key_fn = f"{_fmt}:{_fn}"
            _key_fmt = f"{_fmt}:"
            _fm_escalations[_key_fn] = {"penalty": _decayed_penalty, "entry": _entry}
            if _key_fmt not in _fm_escalations:
                _fm_escalations[_key_fmt] = {"penalty": _decayed_penalty * 0.5, "entry": _entry}
    except Exception:
        pass  # Failure memory is best-effort; never block task generation

    def _score_task_with_memory(goal: "Dict[str, Any]") -> float:
        base = _score_task(goal)
        fmt = goal.get("format", "")
        fn = goal.get("function_name", "")
        # Check function-level escalation first, then format-level
        fn_key = f"{fmt}:{fn}"
        fmt_key = f"{fmt}:"
        penalty = 0.0
        if fn_key in _fm_escalations:
            penalty = _fm_escalations[fn_key]["penalty"]
        elif fmt_key in _fm_escalations:
            penalty = _fm_escalations[fmt_key]["penalty"]
        # TC-MACH-CAP-002: Boost priority for gaps selected by capability compiler
        _gid = goal.get("gap_id", "")
        if _gid and _gid in _selected_gap_ids:
            penalty -= 3.0  # Significant boost (lower score = higher priority)
        return base + penalty  # Higher score = lower priority (deprioritize failed items)

    _sort_key = _score_task_with_memory if _fm_escalations else _score_task

    # Sort by score (lower = higher priority)
    candidates.sort(key=_sort_key)
    candidates = candidates[:max_candidates]

    # Convert to queue items
    queue_items = [
        _goal_to_queue_item(goal, i + 1) for i, goal in enumerate(candidates)
    ]

    # Enrich with route metadata (task_category + route_decision_id)
    try:
        from tools.supervisor.autonomy_route_decider import enrich_work_item_with_route
        queue_items = [
            enrich_work_item_with_route(item) for item in queue_items
        ]
    except ImportError:
        pass  # Route enrichment unavailable â€” items remain unenriched

    # SUP-RECT-005: Circuit breaker for zero-task loops
    zero_task_tracker_path = Path(output_path).parent / ".zero-task-counter.json"
    if len(queue_items) == 0:
        zero_count = 0
        if zero_task_tracker_path.exists():
            try:
                zt = json.loads(zero_task_tracker_path.read_text(encoding="utf-8"))
                zero_count = zt.get("consecutive_zero_count", 0)
            except Exception:
                pass
        zero_count += 1
        zero_task_tracker_path.parent.mkdir(parents=True, exist_ok=True)
        zero_task_tracker_path.write_text(json.dumps({
            "consecutive_zero_count": zero_count,
            "last_zero_at": _now_iso(),
            "escalation_threshold": 3,
            "escalated": zero_count >= 3,
        }, indent=2), encoding="utf-8")
        if zero_count >= 3:
            print(f"CIRCUIT_BREAKER: {zero_count} consecutive zero-task cycles. "
                  "Escalation triggered â€” inspect gap-ledger and _EXPANSION_GOALS.",
                  file=sys.stderr)
    else:
        # Reset counter on successful generation
        if zero_task_tracker_path.exists():
            try:
                zero_task_tracker_path.unlink()
            except Exception:
                pass

    # Write output
    output = {
        "generated_at": _now_iso(),
        "generator_version": "1.3",
        "total_candidates": len(queue_items),
        "gap_ledger_goals_available": len(gap_ledger_goals),
        "hardcoded_fallback_goals_used": sum(1 for g in all_goals if g.get("gap_source") != "gap_ledger"),
        "advisory_only_skipped": advisory_skipped,
        "source": "gap_ledger_primary+expansion_goals_fallback",
        "expansion_goal_fallback": _expansion_goal_fallback,
        "excluded_gap_ids_count": len(_excluded_gap_ids),
        "zero_task_circuit_breaker": len(queue_items) == 0,
        "tasks": queue_items,
    }
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(output, indent=2), encoding="utf-8")

    return queue_items


def main() -> int:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output", type=Path, default=DEFAULT_OUTPUT,
        help="Output path for product-task-candidates.json"
    )
    parser.add_argument(
        "--max-candidates", type=int, default=20,
        help="Maximum number of candidates to generate"
    )
    parser.add_argument(
        "--no-skip-existing", action="store_true",
        help="Include tasks even if function already in source"
    )
    parser.add_argument(
        "--enqueue-top", type=int, default=0,
        help="Auto-enqueue top N tasks to action queue"
    )
    parser.add_argument(
        "--use-compiler", action="store_true",
        help="Use capability compiler as primary task source (opt-in)"
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Print candidates without writing to disk"
    )
    args = parser.parse_args()

    # TC-GOV-MACH-001: opt-in capability compiler path
    if args.use_compiler:
        try:
            # capability_compiler.py lives in the same directory (tools/supervisor/)
            sys.path.insert(0, str(_here))
            from capability_compiler import compile_gap, compile_gap_to_feature_ir
            gap_ledger_path = _REPO_ROOT / "reports" / "capability-layer" / "gap-ledger.json"
            if gap_ledger_path.exists():
                gl_data = json.loads(gap_ledger_path.read_text(encoding="utf-8"))
                gl_gaps = gl_data.get("gaps", []) if isinstance(gl_data, dict) else gl_data
                open_gaps = [g for g in gl_gaps if g.get("status") == "open"]
                compiler_candidates = []
                for gap in open_gaps[:args.max_candidates]:
                    # Normalize gap-ledger fields to compiler's expected schema
                    if "format_id" not in gap and "format" in gap:
                        gap["format_id"] = gap["format"].upper()
                    if "function_name" not in gap and "capability_name" in gap:
                        # Derive function_name: "Load" -> "fods_load", "Save Same Format" -> "fods_save_same_format"
                        fmt_lower = gap.get("format_id", gap.get("format", "unknown")).lower()
                        cap_slug = gap["capability_name"].lower().replace(" ", "_")
                        gap["function_name"] = f"{fmt_lower}_{cap_slug}"
                    try:
                        ir = compile_gap_to_feature_ir(gap)
                        compiler_candidates.append(ir)
                    except Exception:
                        continue
                if compiler_candidates:
                    print(f"TASK_GENERATOR: compiler produced {len(compiler_candidates)} candidates")
                    if not args.dry_run:
                        args.output.parent.mkdir(parents=True, exist_ok=True)
                        args.output.write_text(json.dumps(compiler_candidates, indent=2) + "\n")
                    else:
                        for c in compiler_candidates[:5]:
                            print(f"  - {c.get('feature_id', '?')}: {c.get('function_name', '?')}")
                    return 0
                else:
                    print("TASK_GENERATOR: compiler produced 0 candidates from gap-ledger, falling back")
            else:
                print("TASK_GENERATOR: gap-ledger.json not found, falling back to expansion goals")
        except ImportError as exc:
            print(f"TASK_GENERATOR: --use-compiler: compiler not importable ({exc}), falling back")
        except Exception as exc:
            print(f"TASK_GENERATOR: --use-compiler failed ({exc}), falling back to expansion goals")

    candidates = generate_task_candidates(
        output_path=args.output if not args.dry_run else None,
        max_candidates=args.max_candidates,
        skip_existing=not args.no_skip_existing,
    )

    if args.dry_run:
        print(f"TASK_GENERATOR: {len(candidates)} candidates (dry-run, not written)")
        for c in candidates[:5]:
            fn = c.get("function_name", "?")
            fmt = c.get("format", "?")
            print(f"  - {fmt}/{fn}")
        return 0

    print(f"TASK_GENERATOR: {len(candidates)} candidates written to {args.output}")

    if args.enqueue_top > 0:
        sys.path.insert(0, str(_here))
        from action_queue import enqueue
        enqueued = 0
        for item in candidates[: args.enqueue_top]:
            item["queued_at"] = _now_iso()
            enqueue(item)
            enqueued += 1
        print(f"TASK_GENERATOR: enqueued top {enqueued} tasks to action queue")

    return 0


if __name__ == "__main__":
    sys.exit(main())
