"""Structural architecture tests for src/ — enforces production library checklist.

These tests validate that the source code organization follows the specification-
derived architecture governance rules. They run as part of the regular pytest
suite (layer 0) and catch violations early.

Baseline: registry/source-structure-baseline.json
Validator: tools/validators/source_structure_validator.py
Checklist: docs/code-quality/production-library-checklist.md
"""
from __future__ import annotations

import ast
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[1]
_SRC_PYTHON = _REPO / "src" / "python"
_SRC_NET = _REPO / "src" / "net"
_BASELINE_PATH = _REPO / "registry" / "source-structure-baseline.json"
_ONTOLOGY_DIR = _REPO / "registry" / "odf-ontology"

_MAX_LOC = 800
_MAX_FUNCTIONS = 60

_ODF_FORMATS = {"fods", "fodt", "ods", "odt", "fodp", "fodg"}

_ALL_FORMATS = {
    "abw", "csv", "dif", "fodg", "fodp", "fods", "fodt",
    "gnumeric", "ndjson", "ods", "odt", "pbm", "pgm", "ppm",
    "qoi", "sylk", "toml", "tsv", "xcf", "zst",
}


def _load_baseline() -> dict:
    if _BASELINE_PATH.is_file():
        return json.loads(_BASELINE_PATH.read_text(encoding="utf-8"))
    return {}


def _count_loc(path: Path) -> int:
    try:
        return sum(1 for _ in path.open(encoding="utf-8", errors="replace"))
    except OSError:
        return 0


def _count_functions(path: Path) -> int:
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(path))
        return sum(1 for n in ast.iter_child_nodes(tree)
                   if isinstance(n, ast.FunctionDef))
    except (SyntaxError, OSError):
        return 0


def _find_duplicate_defs(path: Path) -> list[str]:
    try:
        source = path.read_text(encoding="utf-8", errors="replace")
        tree = ast.parse(source, filename=str(path))
    except (SyntaxError, OSError):
        return []
    seen: dict[str, int] = {}
    dups: list[str] = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef):
            if node.name in seen:
                dups.append(f"{node.name} (lines {seen[node.name]} and {node.lineno})")
            else:
                seen[node.name] = node.lineno
    return dups


def _all_python_src_files():
    """Yield (relative_path_str, Path) for all .py files in src/python/."""
    for py_file in sorted(_SRC_PYTHON.rglob("*.py")):
        if py_file.name in ("__init__.py", "conftest.py"):
            continue
        # Skip build artifacts
        if "build" in py_file.parts or "__pycache__" in py_file.parts:
            continue
        rel = str(py_file.relative_to(_REPO)).replace("\\", "/")
        yield rel, py_file


def _all_dotnet_src_files():
    """Yield (relative_path_str, Path) for all .cs files in src/net/."""
    if not _SRC_NET.is_dir():
        return
    for cs_file in sorted(_SRC_NET.rglob("*.cs")):
        if "obj" in cs_file.parts:
            continue
        rel = str(cs_file.relative_to(_REPO)).replace("\\", "/")
        yield rel, cs_file


# ─── Tests ────────────────────────────────────────────────────────────────


class TestNoNewMonolithFiles:
    """No source file exceeds 800 LOC unless grandfathered in baseline."""

    def test_python_no_new_monoliths(self):
        baseline = _load_baseline()
        known = baseline.get("known_violations", {})
        new_violations = []
        for rel, py_file in _all_python_src_files():
            loc = _count_loc(py_file)
            if loc > _MAX_LOC and rel not in known:
                new_violations.append(f"{rel} ({loc} LOC)")
        assert not new_violations, (
            f"New monolith files exceed {_MAX_LOC} LOC (not in baseline):\n"
            + "\n".join(f"  - {v}" for v in new_violations)
        )

    def test_dotnet_no_new_monoliths(self):
        baseline = _load_baseline()
        known = baseline.get("known_violations", {})
        new_violations = []
        for rel, cs_file in _all_dotnet_src_files():
            loc = _count_loc(cs_file)
            if loc > _MAX_LOC and rel not in known:
                new_violations.append(f"{rel} ({loc} LOC)")
        assert not new_violations, (
            f"New .NET monolith files exceed {_MAX_LOC} LOC (not in baseline):\n"
            + "\n".join(f"  - {v}" for v in new_violations)
        )


class TestMonolithBaselineNoRegression:
    """Grandfathered files must not grow beyond their baseline LOC."""

    def test_no_loc_regression(self):
        baseline = _load_baseline()
        known = baseline.get("known_violations", {})
        regressions = []
        for rel, entry in known.items():
            path = _REPO / rel
            if not path.is_file():
                continue
            current_loc = _count_loc(path)
            # Prefer write-once baseline_loc_cap (defense in depth); fall back to loc
            baseline_loc = entry.get("baseline_loc_cap", entry.get("loc", 0))
            if current_loc > baseline_loc:
                regressions.append(
                    f"{rel}: {current_loc} LOC (cap {baseline_loc})"
                )
        assert not regressions, (
            "Baseline files have grown beyond baseline_loc_cap:\n"
            + "\n".join(f"  - {r}" for r in regressions)
        )

    def test_no_function_count_regression(self):
        baseline = _load_baseline()
        known = baseline.get("known_violations", {})
        regressions = []
        for rel, entry in known.items():
            path = _REPO / rel
            if not path.is_file() or not rel.endswith(".py"):
                continue
            current = _count_functions(path)
            # Prefer write-once baseline_functions_cap; fall back to functions
            baseline_count = entry.get("baseline_functions_cap",
                                        entry.get("functions", 0))
            if current > baseline_count:
                regressions.append(
                    f"{rel}: {current} functions (cap {baseline_count})"
                )
        assert not regressions, (
            "Baseline files have more functions than baseline_functions_cap:\n"
            + "\n".join(f"  - {r}" for r in regressions)
        )

    def test_baseline_loc_cap_exists(self):
        """Verify all known_violations have baseline_loc_cap (write-once ceiling)."""
        baseline = _load_baseline()
        violations = baseline.get("known_violations", {})
        missing_cap = [k for k, v in violations.items()
                       if "baseline_loc_cap" not in v]
        assert not missing_cap, (
            "These known_violations entries are missing baseline_loc_cap "
            "(run TC-MACH-001 to add write-once caps):\n"
            + "\n".join(f"  - {k}" for k in missing_cap)
        )


class TestNoDuplicateFunctionDefinitions:
    """No Python source file should have two def statements with the same name."""

    def test_no_duplicates_in_non_baselined_files(self):
        baseline = _load_baseline()
        known = baseline.get("known_violations", {})
        violations = []
        for rel, py_file in _all_python_src_files():
            # Skip baselined files (pre-existing duplicates grandfathered)
            if rel in known:
                continue
            dups = _find_duplicate_defs(py_file)
            if dups:
                violations.append(f"{rel}: {', '.join(dups)}")
        assert not violations, (
            "Duplicate function definitions in non-baselined files:\n"
            + "\n".join(f"  - {v}" for v in violations)
        )


class TestInitExportsCompleteness:
    """Every public function in submodules should appear in __init__.py __all__."""

    def test_init_has_all(self):
        missing_all: list[str] = []
        for fmt in sorted(_ALL_FORMATS):
            init_path = _SRC_PYTHON / fmt / "__init__.py"
            if not init_path.is_file():
                continue
            try:
                source = init_path.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(source)
            except (SyntaxError, OSError):
                continue
            has_all = any(
                isinstance(node, ast.Assign)
                and any(isinstance(t, ast.Name) and t.id == "__all__"
                        for t in node.targets)
                for node in ast.iter_child_nodes(tree)
            )
            if not has_all:
                missing_all.append(fmt)
        assert not missing_all, (
            f"Format modules missing __all__ in __init__.py: {missing_all}"
        )


class TestNoOrphanSourceFiles:
    """Every source file must match a recognized purpose."""

    _KNOWN_STEMS = {
        "__init__", "parser", "writer", "codec", "stats", "constants",
        "exceptions", "models", "neutral_model", "list_traversal",
        "csv_exporter", "conftest", "compat",
        # CLI and exporter entry points
        "cli", "exporters",
        # Spec-derived domain module names (ODF canonical element names)
        "drawing_document", "word_document", "tabular_document",
        "interchange_document", "spreadsheet_document", "spreadsheet_model_document",
        "text_document", "presentation_document", "workbook_document",
        "json_stream", "compressed_stream",
        "frame_header",
        "bitmap_image", "grayscale_image", "color_image", "image_document",
        "drawing_metrics", "compression_metrics", "xcf_image_metrics",
        "config_document",
        # Analytics modules named after entity type (not format prefix)
        "tabular_document_analytics", "text_document_analytics",
        "drawing_document_analytics", "spreadsheet_document_analytics",
        "word_document_analytics",
    }
    # D-group extraction target suffixes (format-prefixed domain module files)
    _DOMAIN_SUFFIXES = {
        "word_stats", "workbook_stats", "record_stats",
        "neutral_ops", "document_edit", "document_query", "drawing_metrics",
        "image_metrics", "compression_metrics",
        # Workflow and iterator modules added by product deepening sprints
        "workflow",
    }
    _CONVERTER_PATTERNS = {"_to_", "_exporter", "_encoder"}

    def _is_recognized(self, filename: str, format_id: str) -> bool:
        stem = Path(filename).stem
        if stem in self._KNOWN_STEMS:
            return True
        if stem.startswith(f"{format_id}_"):
            suffix = stem[len(format_id) + 1:]
            if suffix in ("parser", "writer", "codec", "stats", "encoder", "analytics"):
                return True
            if suffix in self._DOMAIN_SUFFIXES:
                return True
            # Secondary analytics split: {format}_analytics_{category}.py (master-plan.md §24.11)
            if suffix.startswith("analytics_"):
                return True
            # Analytics and stats split modules: {format}_{word}_analytics.py / {format}_{word}_stats.py
            if suffix.endswith("_analytics") or suffix.endswith("_stats"):
                return True
            # Iterator and inspector modules: {format}_{type}_{iterator|inspector}.py
            if suffix.endswith("_iterator") or suffix.endswith("_inspector"):
                return True
            # Metrics and operations split modules (TC-PA-017 monolith healing,
            # PORTFOLIO-AUDIT-2026-07-16): {format}_{word}_metrics.py (e.g.
            # fods_workbook_metrics, ndjson_stream_metrics, tsv_row_metrics),
            # bare {format}_metrics.py (gnumeric_metrics, sylk_metrics), and
            # {format}_{word}_ops.py (tsv_column_ops, fodg_page_ops). These are
            # self-descriptive domain-split modules, exactly parallel to the
            # sanctioned _stats/_analytics/_iterator/_inspector suffixes above.
            if suffix == "metrics" or suffix.endswith("_metrics") or suffix.endswith("_ops"):
                return True
        for pat in self._CONVERTER_PATTERNS:
            if pat in stem:
                return True
        return False

    def test_no_orphans(self):
        orphans: list[str] = []
        for fmt in sorted(_ALL_FORMATS):
            pkg = _SRC_PYTHON / fmt
            if not pkg.is_dir():
                continue
            for py_file in sorted(pkg.glob("*.py")):
                if py_file.name == "conftest.py":
                    continue
                if not self._is_recognized(py_file.name, fmt):
                    orphans.append(f"{fmt}/{py_file.name}")
        assert not orphans, (
            "Orphan source files (unrecognized purpose):\n"
            + "\n".join(f"  - {o}" for o in orphans)
        )


class TestOdfFormatsHaveQnameConstants:
    """ODF format modules should define QName constants or namespace URIs."""

    def test_odf_qname_constants(self):
        missing: list[str] = []
        for fmt in sorted(_ODF_FORMATS):
            pkg = _SRC_PYTHON / fmt
            if not pkg.is_dir():
                continue
            # Check constants.py or any file for QN_ or urn:oasis
            found = False
            for py_file in pkg.glob("*.py"):
                try:
                    text = py_file.read_text(encoding="utf-8", errors="replace")
                    if "QN_" in text or "urn:oasis" in text:
                        found = True
                        break
                except OSError:
                    continue
            if not found:
                missing.append(fmt)
        assert not missing, (
            f"ODF formats missing QName constants: {missing}"
        )


class TestCanonicalClassInventoryNoRegression:
    """canonical-class-inventory.yaml must exist and not regress."""

    def test_inventory_exists(self):
        inv_path = _ONTOLOGY_DIR / "canonical-class-inventory.yaml"
        assert inv_path.is_file(), (
            f"Missing: {inv_path.relative_to(_REPO)}"
        )

    def test_baseline_tracks_inventory(self):
        baseline = _load_baseline()
        qname_baseline = baseline.get("qname_ownership_baseline", {})
        assert "canonical_classes_defined" in qname_baseline, (
            "Baseline missing qname_ownership_baseline.canonical_classes_defined"
        )
        assert qname_baseline["canonical_classes_defined"] >= 25, (
            f"Expected >= 25 canonical classes defined, got "
            f"{qname_baseline['canonical_classes_defined']}"
        )
