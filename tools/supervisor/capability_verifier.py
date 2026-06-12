"""
capability_verifier.py — 4-Bucket Capability Verification for Python FOSS Formats

Sprint: ff-libforge-integration-exec-20260610-133949
Taskcard: LFI-E-002
Pattern source: apidev/verifier.py CoverageReport + verify_coverage()

Classifies Python FOSS format functions into 4 verification buckets:
  FORMAT_MISSING  — capability record exists in map but no source module found
  UNTESTED        — function exported from source but no test file imports it
  SIGNATURE_DRIFT — function in capability map but not exported from source
  STALE_TEST      — test imports a function that is no longer exported

Pure Python, no LLM, no network, no product source writes.
Read-only scan of capability map + src/python/ + tests/python/.
"""

from __future__ import annotations

import ast
import json
import re
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Set

# Names that should never be classified as stale even if not in source exports.
# Includes: stdlib modules/names, pytest internals, typing helpers, common test utilities.
_IMPORT_NOISE: frozenset = frozenset({
    # stdlib top-level names commonly imported in tests
    "Path", "io", "os", "sys", "re", "json", "csv", "hashlib", "tempfile",
    "pathlib", "shutil", "subprocess", "time", "datetime", "uuid",
    "copy", "collections", "itertools", "functools", "operator",
    "typing", "types", "enum", "dataclasses", "abc",
    "Any", "Dict", "List", "Set", "Tuple", "Optional", "Union",
    "Callable", "Generator", "Iterator", "Sequence", "Mapping",
    "TYPE_CHECKING", "annotations", "dataclass", "field",
    # pytest
    "pytest", "fixture", "mark", "raises", "warns", "approx",
    "parametrize", "skip", "skipif", "xfail",
    # common test helpers
    "tmp_path", "capsys", "monkeypatch", "capfd",
    # format factory non-format modules
    "annotations",
})


@dataclass(frozen=True)
class FormatMissing:
    """Capability record exists in map but no source module directory found."""
    format_id: str
    capability_id: str
    capability_name: str


@dataclass(frozen=True)
class Untested:
    """Function exported from source __all__ but no test file imports it."""
    format_id: str
    function_name: str
    source_module: str


@dataclass(frozen=True)
class SignatureDrift:
    """Capability name in map but function not found in source exports."""
    format_id: str
    capability_id: str
    capability_name: str
    expected_function: str


@dataclass(frozen=True)
class StaleTest:
    """Test file imports a function name that is no longer in source exports."""
    format_id: str
    function_name: str
    test_file: str


@dataclass
class VerificationReport:
    """Aggregate verification result across all scanned formats.

    Pattern: apidev CoverageReport — `passed` is True when all buckets empty.
    """
    format_missing: List[FormatMissing] = field(default_factory=list)
    untested: List[Untested] = field(default_factory=list)
    signature_drift: List[SignatureDrift] = field(default_factory=list)
    stale_test: List[StaleTest] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return (
            len(self.format_missing) == 0
            and len(self.untested) == 0
            and len(self.signature_drift) == 0
            and len(self.stale_test) == 0
        )

    def to_json(self) -> str:
        return json.dumps(self._to_dict(), indent=2)

    def _to_dict(self) -> Dict[str, Any]:
        return {
            "passed": self.passed,
            "format_missing": [asdict(r) for r in self.format_missing],
            "untested": [asdict(r) for r in self.untested],
            "signature_drift": [asdict(r) for r in self.signature_drift],
            "stale_test": [asdict(r) for r in self.stale_test],
            "summary": {
                "format_missing_count": len(self.format_missing),
                "untested_count": len(self.untested),
                "signature_drift_count": len(self.signature_drift),
                "stale_test_count": len(self.stale_test),
            },
        }


class CapabilityVerifier:
    """Read-only 4-bucket capability verifier for Python FOSS formats.

    Usage:
        verifier = CapabilityVerifier(
            capability_map_path=Path("reports/capability-layer/unified-capability-map.json"),
            source_root=Path("src/python"),
            test_root=Path("tests/python"),
        )
        report = verifier.verify()
        print(report.passed)
        print(report.to_json())
    """

    def __init__(
        self,
        capability_map_path: Path,
        source_root: Path,
        test_root: Path,
    ) -> None:
        self._cap_map_path = Path(capability_map_path)
        self._source_root = Path(source_root)
        self._test_root = Path(test_root)

    def verify(self) -> VerificationReport:
        """Run all 4 verification buckets and return the report."""
        cap_data = self._load_capability_map()
        if cap_data is None:
            report = VerificationReport()
            report.format_missing.append(
                FormatMissing(
                    format_id="ALL",
                    capability_id="N/A",
                    capability_name="capability_map_load_failed",
                )
            )
            return report

        foss_caps = [
            c for c in cap_data.get("capabilities", [])
            if c.get("product_type") == "foss_reduced"
        ]

        # Group FOSS capabilities by format
        caps_by_format: Dict[str, List[Dict[str, Any]]] = {}
        for cap in foss_caps:
            fmt = cap.get("format", "").lower()
            if fmt:
                caps_by_format.setdefault(fmt, []).append(cap)

        report = VerificationReport()

        # Collect all format directories that exist in source
        all_source_formats: Set[str] = set()
        if self._source_root.is_dir():
            for child in self._source_root.iterdir():
                if child.is_dir() and not child.name.startswith("_"):
                    all_source_formats.add(child.name)

        # Union of formats from cap map and source dirs
        all_formats = set(caps_by_format.keys()) | all_source_formats

        for fmt_lower in sorted(all_formats):
            caps = caps_by_format.get(fmt_lower, [])
            source_dir = self._source_root / fmt_lower
            if not source_dir.is_dir():
                # FORMAT_MISSING: cap exists but no source dir
                for cap in caps:
                    report.format_missing.append(
                        FormatMissing(
                            format_id=fmt_lower,
                            capability_id=cap.get("capability_id", ""),
                            capability_name=cap.get("capability_name", ""),
                        )
                    )
                continue

            # Get exported functions from source __init__.py or codec module
            exports = self._get_source_exports(source_dir)

            # Get functions imported in test files
            test_dir = self._test_root / fmt_lower
            test_imports = self._get_test_imports(test_dir) if test_dir.is_dir() else set()

            # SIGNATURE_DRIFT: capability in map but function not in source exports
            for cap in caps:
                func_name = self._capability_to_function_name(cap)
                if func_name and func_name not in exports:
                    report.signature_drift.append(
                        SignatureDrift(
                            format_id=fmt_lower,
                            capability_id=cap.get("capability_id", ""),
                            capability_name=cap.get("capability_name", ""),
                            expected_function=func_name,
                        )
                    )

            # UNTESTED: function exported but not imported in any test
            for func_name in sorted(exports):
                if func_name.startswith("_"):
                    continue  # skip private
                if self._is_class_name(func_name):
                    continue  # skip classes/exceptions
                if func_name not in test_imports:
                    report.untested.append(
                        Untested(
                            format_id=fmt_lower,
                            function_name=func_name,
                            source_module=str(source_dir),
                        )
                    )

            # STALE_TEST: test imports a function no longer in exports
            for func_name, test_file in sorted(self._get_test_import_details(test_dir) if test_dir.is_dir() else []):
                if func_name not in exports and not func_name.startswith("_"):
                    report.stale_test.append(
                        StaleTest(
                            format_id=fmt_lower,
                            function_name=func_name,
                            test_file=str(test_file),
                        )
                    )

        return report

    def _load_capability_map(self) -> Optional[Dict[str, Any]]:
        """Load and parse the unified capability map JSON."""
        try:
            with open(self._cap_map_path, encoding="utf-8") as f:
                return json.load(f)
        except (FileNotFoundError, json.JSONDecodeError, OSError):
            return None

    def _get_source_exports(self, source_dir: Path) -> Set[str]:
        """Extract __all__ from __init__.py, or scan top-level defs from codec module."""
        init_path = source_dir / "__init__.py"
        if init_path.is_file():
            exports = self._extract_all_from_init(init_path)
            if exports is not None:
                return exports

        # Fallback: scan all .py files for top-level function/class defs
        exports: Set[str] = set()
        for py_file in source_dir.glob("*.py"):
            if py_file.name == "__init__.py":
                continue
            exports.update(self._extract_top_level_defs(py_file))
        return exports

    def _extract_all_from_init(self, init_path: Path) -> Optional[Set[str]]:
        """Parse __init__.py and return __all__ if defined."""
        try:
            with open(init_path, encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=str(init_path))
        except (SyntaxError, OSError):
            return None

        for node in ast.walk(tree):
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if isinstance(target, ast.Name) and target.id == "__all__":
                        try:
                            return set(ast.literal_eval(node.value))
                        except (ValueError, TypeError):
                            return None
        return None

    def _extract_top_level_defs(self, py_file: Path) -> Set[str]:
        """Extract top-level function and class names from a Python file."""
        try:
            with open(py_file, encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=str(py_file))
        except (SyntaxError, OSError):
            return set()

        names: Set[str] = set()
        for node in ast.iter_child_nodes(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                names.add(node.name)
            elif isinstance(node, ast.ClassDef):
                names.add(node.name)
        return names

    def _get_test_imports(self, test_dir: Path) -> Set[str]:
        """Collect all function names imported in test files."""
        imports: Set[str] = set()
        for test_file in test_dir.rglob("test_*.py"):
            imports.update(self._extract_imports_from_test(test_file))
        return imports

    def _get_test_import_details(self, test_dir: Path) -> List[tuple]:
        """Return (function_name, test_file) pairs for stale test detection."""
        results: List[tuple] = []
        for test_file in test_dir.rglob("test_*.py"):
            for name in self._extract_imports_from_test(test_file):
                results.append((name, test_file.relative_to(test_dir)))
        return results

    def _extract_imports_from_test(self, test_file: Path) -> Set[str]:
        """Extract imported names from a test file using AST.

        Filters out stdlib, pytest, typing, and other non-product imports
        to reduce STALE_TEST false positives.
        """
        try:
            with open(test_file, encoding="utf-8") as f:
                tree = ast.parse(f.read(), filename=str(test_file))
        except (SyntaxError, OSError):
            return set()

        names: Set[str] = set()
        stdlib_top = sys.stdlib_module_names if hasattr(sys, "stdlib_module_names") else set()

        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom):
                if not node.names:
                    continue
                module = node.module or ""
                # Skip imports from stdlib, pytest, typing, pathlib etc.
                top_module = module.split(".")[0] if module else ""
                if top_module in stdlib_top:
                    continue
                if top_module in {"pytest", "typing", "pathlib", "_pytest"}:
                    continue
                for alias in node.names:
                    name = alias.name
                    if name not in _IMPORT_NOISE and not name.startswith("_"):
                        names.add(name)
        return names

    @staticmethod
    def _capability_to_function_name(cap: Dict[str, Any]) -> Optional[str]:
        """Convert a capability record to the expected Python function name.

        Uses operation_kind as the primary mapping. Falls back to snake_case
        of capability_name. Returns None for capabilities that don't map
        to individual functions (e.g., load, inspect_object_model).
        """
        op = cap.get("operation_kind", "")
        if op:
            return op
        name = cap.get("capability_name", "")
        if not name:
            return None
        # Convert to snake_case
        s = re.sub(r"([A-Z])", r"_\1", name).lower().strip("_")
        s = re.sub(r"[\s\-]+", "_", s)
        return s

    @staticmethod
    def _is_class_name(name: str) -> bool:
        """Heuristic: names starting with uppercase are likely classes/exceptions."""
        return bool(name) and name[0].isupper()

    @staticmethod
    def product_selection_helper(
        report: "VerificationReport",
        max_candidates: int = 20,
    ) -> List[Dict[str, Any]]:
        """Return prioritized candidate functions for product work.

        Summarizes the VerificationReport into an ordered list of work candidates:
          Priority 1 — UNTESTED: exported functions that need test coverage
          Priority 2 — SIGNATURE_DRIFT: capability map entries that need implementation

        Args:
            report: VerificationReport from CapabilityVerifier.verify()
            max_candidates: Maximum number of candidates to return (default: 20)

        Returns:
            List of dicts with keys: format_id, function_name, priority, bucket,
            sorted by (priority ASC, format_id ASC, function_name ASC).
        """
        candidates: List[Dict[str, Any]] = []

        for item in report.untested:
            candidates.append({
                "format_id": item.format_id,
                "function_name": item.function_name,
                "priority": 1,
                "bucket": "UNTESTED",
                "source_module": item.source_module,
            })

        for item in report.signature_drift:
            candidates.append({
                "format_id": item.format_id,
                "function_name": item.expected_function,
                "priority": 2,
                "bucket": "SIGNATURE_DRIFT",
                "capability_id": item.capability_id,
                "capability_name": item.capability_name,
            })

        candidates.sort(key=lambda c: (c["priority"], c["format_id"], c["function_name"]))
        return candidates[:max_candidates]
