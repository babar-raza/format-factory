"""
TC-PA-025: Regression tests for systemic defect classes.

These tests permanently guard against the defect classes identified in the
portfolio audit (PORTFOLIO-AUDIT-2026-07-16). They complement governance
validators V246/V249/V250/V251 with CI-level regression.

Each test scans the live repo and fails if a defect class recurs.
Known violations are tracked with explicit counts — the count must decrease
over time, never increase.
"""
import ast
import json
import pathlib
import subprocess
import sys

import pytest
import yaml

REPO_ROOT = pathlib.Path(__file__).resolve().parents[2]
SRC_PYTHON = REPO_ROOT / "src" / "python"
BASELINE_PATH = REPO_ROOT / "registry" / "source-structure-baseline.json"
MATRIX_PATH = REPO_ROOT / "registry" / "converter-compatibility-matrix.yaml"
SAL_DIR = REPO_ROOT / "shared" / "sal-facts"

FORMAT_PACKAGES = sorted(
    p.name
    for p in SRC_PYTHON.iterdir()
    if p.is_dir() and not p.name.startswith("_")
)


def _iter_python_files(root: pathlib.Path):
    for f in sorted(root.rglob("*.py")):
        if "__pycache__" in f.parts:
            continue
        yield f


def _has_sys_path_mutation(source: str) -> bool:
    try:
        tree = ast.parse(source)
    except SyntaxError:
        return False
    for node in ast.walk(tree):
        if not isinstance(node, ast.Attribute):
            continue
        if node.attr not in ("insert", "append"):
            continue
        val = node.value
        if isinstance(val, ast.Attribute) and val.attr == "path":
            if isinstance(val.value, ast.Name) and val.value.id == "sys":
                return True
            if isinstance(val.value, ast.Name):
                try:
                    for imp in ast.walk(tree):
                        if isinstance(imp, ast.Import):
                            for alias in imp.names:
                                if alias.name == "sys" and alias.asname == val.value.id:
                                    return True
                        elif isinstance(imp, ast.ImportFrom):
                            if imp.module == "sys":
                                return True
                except Exception:
                    pass
    return False


# ── Test 1: No sys.path mutation in product source ──────────────────────────

class TestNoSysPathInProductSource:
    """sys.path.insert/append in src/python/ is a process-global pollution defect."""

    KNOWN_VIOLATION_CAP = 152

    def test_no_new_sys_path_violations(self):
        violations = []
        for f in _iter_python_files(SRC_PYTHON):
            try:
                source = f.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if _has_sys_path_mutation(source):
                violations.append(f.relative_to(REPO_ROOT).as_posix())

        assert len(violations) <= self.KNOWN_VIOLATION_CAP, (
            f"sys.path mutations INCREASED: {len(violations)} files "
            f"(cap={self.KNOWN_VIOLATION_CAP}). New violations:\n"
            + "\n".join(violations[-10:])
        )

    def test_sys_path_count_is_tracked(self):
        """The count must be explicitly tracked — not silently ignored."""
        assert self.KNOWN_VIOLATION_CAP > 0, (
            "If all sys.path mutations are eliminated, set cap to 0 "
            "and remove this test."
        )


# ── Test 2: No nested duplicate packages ────────────────────────────────────

class TestNoNestedDuplicatePackages:
    """A package dir containing a same-named child dir is a structural defect."""

    def test_no_nested_duplicates(self):
        duplicates = []
        for pkg in SRC_PYTHON.iterdir():
            if not pkg.is_dir() or pkg.name.startswith("_"):
                continue
            child = pkg / pkg.name
            if child.is_dir():
                duplicates.append(child.relative_to(REPO_ROOT).as_posix())

        assert not duplicates, (
            f"Nested duplicate package directories found:\n"
            + "\n".join(duplicates)
        )


# ── Test 3: No stdlib namespace collisions ──────────────────────────────────

class TestNoStdlibCollisions:
    """Package names must not shadow stdlib modules.

    TC-PA-013 (2026-07-20) renamed src/python/csv -> src/python/ff_csv, resolving
    the one known stdlib collision. KNOWN_COLLISIONS is empty going forward — any
    stdlib collision found now is NEW and must block (see V250 policy: stdlib
    collisions always block; only popular-PyPI collisions like `toml` WARN
    non-blocking, per governance_validators_import_hygiene.py).
    """

    KNOWN_COLLISIONS: set = set()

    def test_no_new_stdlib_collisions(self):
        if not hasattr(sys, "stdlib_module_names"):
            pytest.skip("sys.stdlib_module_names requires Python 3.10+")

        collisions = {
            p.name
            for p in SRC_PYTHON.iterdir()
            if p.is_dir()
            and not p.name.startswith("_")
            and p.name in sys.stdlib_module_names
        }

        new_collisions = collisions - self.KNOWN_COLLISIONS
        assert not new_collisions, (
            f"New stdlib collisions detected: {new_collisions}. "
            f"Known: {self.KNOWN_COLLISIONS}"
        )

    def test_known_collisions_documented(self):
        if not self.KNOWN_COLLISIONS:
            pytest.skip(
                "No known stdlib collisions remain (csv -> ff_csv rename closed "
                "the last one via TC-PA-013). Skip rather than fail-on-empty."
            )
        assert self.KNOWN_COLLISIONS, (
            "When all collisions are fixed, remove this test "
            "and clear KNOWN_COLLISIONS."
        )


# ── Test 4: No public NotImplementedError stubs ─────────────────────────────

class TestNoPublicNotImplementedError:
    """Public functions must not raise NotImplementedError unconditionally."""

    def test_no_unconditional_not_implemented(self):
        stubs = []
        for f in _iter_python_files(SRC_PYTHON):
            try:
                source = f.read_text(encoding="utf-8", errors="replace")
                tree = ast.parse(source)
            except (OSError, SyntaxError):
                continue
            for node in ast.iter_child_nodes(tree):
                if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                    continue
                if node.name.startswith("_"):
                    continue
                body = node.body
                if len(body) == 1 and isinstance(body[0], ast.Raise):
                    exc = body[0].exc
                    if isinstance(exc, ast.Call) and isinstance(exc.func, ast.Name):
                        if exc.func.id == "NotImplementedError":
                            stubs.append(
                                f"{f.relative_to(REPO_ROOT).as_posix()}"
                                f":{node.lineno} {node.name}()"
                            )

        assert not stubs, (
            f"Public functions that unconditionally raise NotImplementedError:\n"
            + "\n".join(stubs)
        )


# ── Test 5: Converter compatibility registry complete ───────────────────────

class TestConverterCompatibilityRegistryComplete:
    """Every converter module must have a compatibility matrix entry."""

    def test_all_converters_registered(self):
        if not MATRIX_PATH.exists():
            pytest.skip("converter-compatibility-matrix.yaml not found")

        matrix = yaml.safe_load(MATRIX_PATH.read_text(encoding="utf-8"))
        registered = set(matrix.get("converters", {}).keys())

        converter_files = set()
        for f in _iter_python_files(SRC_PYTHON):
            if "_to_" in f.stem and f.suffix == ".py":
                converter_files.add(f.relative_to(REPO_ROOT).as_posix())

        unregistered = converter_files - registered
        assert not unregistered, (
            f"{len(unregistered)} converter(s) have no compatibility matrix entry:\n"
            + "\n".join(sorted(unregistered)[:20])
        )

    def test_no_incompatible_converters_on_disk(self):
        """INCOMPATIBLE converters should not exist as source files."""
        if not MATRIX_PATH.exists():
            pytest.skip("converter-compatibility-matrix.yaml not found")

        matrix = yaml.safe_load(MATRIX_PATH.read_text(encoding="utf-8"))
        converters = matrix.get("converters", {})

        incompatible_on_disk = []
        for path, entry in converters.items():
            if entry.get("category") == "INCOMPATIBLE":
                full = REPO_ROOT / path
                if full.exists():
                    incompatible_on_disk.append(path)

        # Known: 3 csv INCOMPATIBLE converters deferred to post-rename
        assert len(incompatible_on_disk) <= 3, (
            f"INCOMPATIBLE converters still on disk (beyond 3 csv deferred):\n"
            + "\n".join(incompatible_on_disk)
        )


# ── Test 6: All formats have minimum SAL facts ─────────────────────────────

class TestAllFormatsHaveMinimumSalFacts:
    """Every format with a SAL file must have >= 15 facts."""

    MINIMUM_FACTS = 15

    def test_minimum_sal_facts(self):
        if not SAL_DIR.exists():
            pytest.skip("shared/sal-facts/ not found")

        below_minimum = []
        for f in sorted(SAL_DIR.glob("*.yaml")):
            data = yaml.safe_load(f.read_text(encoding="utf-8"))
            facts = data.get("facts", []) if isinstance(data, dict) else (data or [])
            count = len(facts)
            if count < self.MINIMUM_FACTS:
                below_minimum.append(f"{f.stem}: {count} facts")

        assert not below_minimum, (
            f"Formats with fewer than {self.MINIMUM_FACTS} SAL facts:\n"
            + "\n".join(below_minimum)
        )


# ── Test 7: No __pycache__ tracked in git ──────────────────────────────────

class TestSourceHygieneNoPycacheTracked:
    """__pycache__ and .pyc files must not be tracked by git."""

    def test_no_pycache_tracked(self):
        result = subprocess.run(
            ["git", "ls-files", "*__pycache__*", "*.pyc"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
        )
        tracked = [
            line.strip() for line in result.stdout.splitlines() if line.strip()
        ]
        assert not tracked, (
            f"{len(tracked)} __pycache__/pyc files tracked by git:\n"
            + "\n".join(tracked[:20])
        )


# ── Test 8: No monolith files over 800 LOC without healing plan ────────────

class TestNoMonolithFilesOver800Loc:
    """No Python source file may exceed 800 LOC unless it has a healing_plan."""

    LOC_LIMIT = 800

    def test_no_unplanned_monoliths(self):
        if not BASELINE_PATH.exists():
            pytest.skip("source-structure-baseline.json not found")

        baseline = json.loads(BASELINE_PATH.read_text(encoding="utf-8"))
        known_violations = baseline.get("known_violations", {})

        healed = {
            k
            for k, v in known_violations.items()
            if "healing_plan" in v
        }

        unhealed_monoliths = []
        for f in _iter_python_files(SRC_PYTHON):
            try:
                loc = sum(1 for _ in f.open(encoding="utf-8", errors="replace"))
            except OSError:
                continue
            if loc > self.LOC_LIMIT:
                rel = f.relative_to(REPO_ROOT).as_posix()
                if rel not in healed:
                    unhealed_monoliths.append(f"{rel} ({loc} LOC)")

        assert not unhealed_monoliths, (
            f"Files exceeding {self.LOC_LIMIT} LOC without healing_plan:\n"
            + "\n".join(unhealed_monoliths)
        )
