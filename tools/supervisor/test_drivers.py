"""Template-based test driver renderer for FeatureFactory patterns.

Replaces inline f-string test skeleton generation with string.Template-based
rendering from .py.tmpl driver files under drivers/python/.

Language: Python only. This driver explicitly supports Python test generation.
For other languages, a new driver module must be registered.
PYTHON_ONLY_BY_DESIGN: No .NET or other language drivers exist in this module.
"""
from __future__ import annotations

import ast
import re
from pathlib import Path
from string import Template
from typing import List


_DRIVERS_DIR = Path(__file__).resolve().parents[2] / "drivers" / "python"
_SUPPORTED_LANGUAGE = "python"

# --- Language policy ---

def _validate_language(language: str) -> None:
    """Raise ValueError if language is not 'python' (case-insensitive)."""
    if language.lower() != _SUPPORTED_LANGUAGE:
        raise ValueError(
            f"Unsupported language {language!r}. "
            "This driver is PYTHON_ONLY_BY_DESIGN."
        )


# --- Contract validation ---

class ContractViolationError(Exception):
    """Raised when a template/renderer argument contract is violated."""


def validate_template_renderer_compatibility() -> None:
    """Load driver-contracts.yaml and verify template/renderer argument parity.

    Raises ContractViolationError on any mismatch.
    """
    contracts_path = _DRIVERS_DIR / "driver-contracts.yaml"
    if not contracts_path.is_file():
        raise FileNotFoundError(f"driver-contracts.yaml not found: {contracts_path}")

    try:
        import yaml  # type: ignore[import]
        data = yaml.safe_load(contracts_path.read_text(encoding="utf-8"))
    except ImportError:
        _validate_contracts_without_yaml(contracts_path)
        return

    templates = {t["template_id"]: set(t["required_arguments"]) for t in data.get("driver_templates", [])}
    renderers = {r["renderer_id"]: set(r["provided_arguments"]) for r in data.get("driver_renderers", [])}

    for tmpl_id, required in templates.items():
        tmpl_entry = next((t for t in data["driver_templates"] if t["template_id"] == tmpl_id), None)
        if not tmpl_entry:
            continue
        renderer_id = tmpl_entry.get("renderer_id")
        provided = renderers.get(renderer_id, set())
        missing_from_renderer = required - provided
        extra_in_renderer = provided - required
        if missing_from_renderer or extra_in_renderer:
            raise ContractViolationError(
                f"Template {tmpl_id!r} / renderer {renderer_id!r}: "
                f"missing_from_renderer={sorted(missing_from_renderer)}, "
                f"extra_in_renderer={sorted(extra_in_renderer)}"
            )


def _validate_contracts_without_yaml(contracts_path: Path) -> None:
    """Fallback contract validation using plain text when PyYAML is unavailable."""
    content = contracts_path.read_text(encoding="utf-8")
    if "required_arguments" not in content:
        raise ContractViolationError("driver-contracts.yaml missing required_arguments sections")


# --- Placeholder scanning ---

FORBIDDEN_PLACEHOLDER_PATTERNS: List[str] = [
    r"assert\s+\w+\s+is\s+not\s+None\b",
    r"isinstance\(\w+,\s*object\)",
    r"#\s*TODO",
    r"#\s*FIXTURE_REQUIRED",
    r"#\s*EXPECTED_VALUE_REQUIRED",
    r"#\s*ORACLE_REQUIRED",
    r"#\s*TEST_SCAFFOLD_INCOMPLETE",
    r"#\s*FORMAT_ADAPTATION_REQUIRED",
    r"SCAFFOLD_STATUS:\s*FORMAT_ADAPTATION_REQUIRED",
]

FORBIDDEN_PLACEHOLDER_LITERALS: List[str] = [
    "# TODO: provide a real model or input",
    "# TODO: provide real source bytes",
    "# TODO: Replace with a real fixture",
    "ADD FORMAT-SPECIFIC MINIMAL BYTES HERE",
]

VALID_FIXTURE_SOURCES: List[str] = [
    "repository_golden_sample",
    "deterministic_builder",
    "spec_example",
    "minimal_valid_bytes",
    "intentionally_malformed",
    "verified_roundtrip",
    "empty_input_contract",
]

WEAK_ASSERTION_PATTERNS: List[str] = [
    "assert result is not None",
    "assert isinstance(result, object)",
    "assert True",
    "pass",
]

MEANINGFUL_ASSERTION_KINDS: List[str] = [
    "assertEqual",
    "assert result ==",
    "assert len(",
    "assert model[",
    "assert dest.stat().st_size >",
]


def scan_for_forbidden_placeholders(rendered_code: str) -> List[str]:
    """Scan rendered test code for forbidden placeholder patterns.

    Returns a list of matched forbidden markers. Empty list = no forbidden markers.
    """
    found: List[str] = []
    for pattern in FORBIDDEN_PLACEHOLDER_PATTERNS:
        if re.search(pattern, rendered_code):
            found.append(pattern)
    for literal in FORBIDDEN_PLACEHOLDER_LITERALS:
        if literal in rendered_code:
            found.append(literal)
    return found


def is_maintained_test(rendered_code: str) -> bool:
    """Return True only when no forbidden placeholder markers remain in the code."""
    return len(scan_for_forbidden_placeholders(rendered_code)) == 0


# --- Fixture contract ---

def validate_fixture_contract(fixture_bytes: bytes, fixture_source: str) -> None:
    """Raise ValueError if fixture_bytes are empty and source is not empty_input_contract."""
    if fixture_bytes == b"" and fixture_source != "empty_input_contract":
        raise ValueError(
            f"Empty fixture bytes are not allowed for source {fixture_source!r}. "
            "Use fixture_source='empty_input_contract' to explicitly permit b\"\"."
        )


def _load_template(name: str) -> Template:
    """Load a .py.tmpl template from the drivers/python/ directory."""
    tmpl_path = _DRIVERS_DIR / name
    if not tmpl_path.is_file():
        raise FileNotFoundError(f"Template not found: {tmpl_path}")
    return Template(tmpl_path.read_text(encoding="utf-8"))


def _source_to_import(source_path: str) -> str:
    """Convert 'src/python/abw/abw_codec.py' -> 'abw.abw_codec'."""
    parts = Path(source_path).parts
    try:
        idx = list(parts).index("python")
        module_parts = list(parts[idx + 1:])
        if module_parts and module_parts[-1].endswith(".py"):
            module_parts[-1] = module_parts[-1][:-3]
        return ".".join(module_parts)
    except ValueError:
        return source_path.replace("/", ".").removesuffix(".py")


def _safe_return_type(return_type: str) -> str:
    """Sanitize return type for use in test method names."""
    return (
        return_type
        .replace("[", "_")
        .replace("]", "")
        .replace(",", "_")
        .strip()
    )


def render_getter_test(
    source_path: str, function_name: str, params: str, return_type: str
) -> str:
    """Render Pattern A (Getter) test skeleton from template."""
    tmpl = _load_template("getter_test.py.tmpl")
    module = _source_to_import(source_path)
    class_name = function_name.replace("_", " ").title().replace(" ", "")
    return tmpl.substitute(
        function_name=function_name,
        module=module,
        class_name=class_name,
        return_type_safe=_safe_return_type(return_type),
    )


def render_export_csv_test(
    source_path: str, function_name: str, format_name: str
) -> str:
    """Render Pattern B (ExportCsv) test skeleton from template."""
    tmpl = _load_template("export_csv_test.py.tmpl")
    module = _source_to_import(source_path)
    return tmpl.substitute(
        function_name=function_name,
        module=module,
        format_cap=format_name.capitalize(),
    )


def render_roundtrip_test(
    format_name: str,
    source_path: str,
    load_function: str,
    write_function: str,
    compare_field: str,
) -> str:
    """Render Pattern C (Roundtrip) test skeleton from template."""
    tmpl = _load_template("roundtrip_test.py.tmpl")
    module_path = source_path.replace("/", ".").removesuffix(".py")
    module_parts = module_path.split(".")
    test_import = (
        f"from {'.'.join(module_parts[:-1])} import {load_function}, {write_function}"
    )
    return tmpl.substitute(
        format_upper=format_name.upper(),
        format_cap=format_name.capitalize(),
        format_name=format_name,
        test_import=test_import,
        load_function=load_function,
        write_function=write_function,
        compare_field=compare_field,
    )


def render_append_test(
    source_path: str, function_name: str, format_name: str, collection_key: str
) -> str:
    """Render Pattern D (Append) test skeleton from template."""
    tmpl = _load_template("append_test.py.tmpl")
    module = _source_to_import(source_path)
    return tmpl.substitute(
        function_name=function_name,
        module=module,
        format_cap=format_name.capitalize(),
        collection_key=collection_key,
    )


def render_probe_test(
    source_path: str, function_name: str, format_name: str
) -> str:
    """Render Pattern E (Probe) test skeleton from template."""
    tmpl = _load_template("probe_test.py.tmpl")
    module = _source_to_import(source_path)
    return tmpl.substitute(
        function_name=function_name,
        module=module,
        format_cap=format_name.capitalize(),
        format_lower=format_name.lower(),
    )
