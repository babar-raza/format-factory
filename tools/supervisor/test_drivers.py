"""Template-based test driver renderer for FeatureFactory patterns.

Replaces inline f-string test skeleton generation with string.Template-based
rendering from .py.tmpl driver files under drivers/python/.

Pilot 2 deliverable for LibForge Integration.
"""
from __future__ import annotations

from pathlib import Path
from string import Template


_DRIVERS_DIR = Path(__file__).resolve().parents[2] / "drivers" / "python"


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
