"""Tests for V242/V243/V244 (governance_validators_package_integrity.py).

Standalone package-integrity hardening task. These validators are full-repo-scan,
declaration-ignoring validators modeled on V230 (governance_validators_gate9_drift.py) --
NOT the declaration-scoped shallow pattern used by V76. All fixtures below build a
synthetic src/python/<fmt>/ tree under tmp_path and pass it as repo_root, so none of
these tests touch the real repository's src/python/ tree.

NOTE: this suite intentionally does NOT assert anything about the real repo's current
pass/fail state. The real repo currently has known V242/V243/V244 violations (duplicate
parser-local exception classes, ValueError-based hierarchies in fods/fodt, unwired
analytics in pgm/odt/ndjson/fods/dif) that are fixed in a later, separate step -- see the
ad-hoc real-repo proof run performed alongside this task instead of a pytest assertion.
"""
from __future__ import annotations

import sys
from pathlib import Path

_REPO = Path(__file__).resolve().parent.parent.parent
_SUPERVISOR = _REPO / "tools" / "supervisor"
if str(_SUPERVISOR) not in sys.path:
    sys.path.insert(0, str(_SUPERVISOR))

from governance_validators_package_integrity import (  # noqa: E402
    validate_analytics_module_wiring,
    validate_exception_class_single_source,
    validate_exception_hierarchy_correctness,
    validate_no_nested_duplicate_packages,
    validate_oracle_registry_reconciliation,
)


def _write(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# V242 — validate_exception_class_single_source
# ---------------------------------------------------------------------------

class TestV242ExceptionClassSingleSource:
    def test_duplicate_class_definition_fails(self, tmp_path):
        """A class defined independently in exceptions.py AND a parser file → FAIL."""
        pkg = tmp_path / "src" / "python" / "dup"
        _write(pkg / "exceptions.py", (
            "class DupError(Exception):\n"
            "    pass\n"
            "\n"
            "class DupParseError(DupError):\n"
            "    pass\n"
        ))
        _write(pkg / "dup_parser.py", (
            "class DupError(Exception):\n"
            "    \"\"\"Locally re-declared -- should be imported, not redefined.\"\"\"\n"
        ))

        result = validate_exception_class_single_source({}, repo_root=tmp_path)

        assert result["validator"] == "validate_exception_class_single_source"
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True
        assert len(result["items"]) == 1
        item = result["items"][0]
        assert item["package"] == "dup"
        assert item["class_name"] == "DupError"
        assert len(item["defined_in"]) == 2
        assert any("exceptions.py" in f for f in item["defined_in"])
        assert any("dup_parser.py" in f for f in item["defined_in"])

    def test_clean_single_definition_passes(self, tmp_path):
        """Each Error class defined exactly once in the package → PASS."""
        pkg = tmp_path / "src" / "python" / "clean"
        _write(pkg / "exceptions.py", (
            "class CleanError(Exception):\n"
            "    pass\n"
            "\n"
            "class CleanParseError(CleanError):\n"
            "    pass\n"
        ))
        _write(pkg / "clean_parser.py", "def parse():\n    return {}\n")

        result = validate_exception_class_single_source({}, repo_root=tmp_path)

        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False
        assert result["items"] == []

    def test_import_only_reference_is_not_a_false_positive(self, tmp_path):
        """A file that IMPORTS the exception class (no local ClassDef) must not count
        as a second definition."""
        pkg = tmp_path / "src" / "python" / "importer"
        _write(pkg / "exceptions.py", (
            "class ImporterError(Exception):\n"
            "    pass\n"
        ))
        _write(pkg / "importer_parser.py", (
            "from .exceptions import ImporterError\n"
            "\n"
            "def parse():\n"
            "    raise ImporterError('boom')\n"
        ))

        result = validate_exception_class_single_source({}, repo_root=tmp_path)

        assert result["result"] == "PASS"
        assert result["items"] == []


# ---------------------------------------------------------------------------
# V243 — validate_exception_hierarchy_correctness
# ---------------------------------------------------------------------------

class TestV243ExceptionHierarchyCorrectness:
    def test_wrong_base_fails(self, tmp_path):
        """Root exception class based on something other than FormatFactoryError → FAIL."""
        pkg = tmp_path / "src" / "python" / "badbase"
        _write(pkg / "exceptions.py", (
            "class BadbaseError(RuntimeError):\n"
            "    pass\n"
            "\n"
            "class BadbaseParseError(BadbaseError):\n"
            "    pass\n"
        ))

        result = validate_exception_hierarchy_correctness({}, repo_root=tmp_path)

        assert result["validator"] == "validate_exception_hierarchy_correctness"
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True
        assert len(result["items"]) == 1
        item = result["items"][0]
        assert item["package"] == "badbase"
        assert item["class_name"] == "BadbaseError"
        assert item["actual_base"] == "RuntimeError"
        assert item["expected_base"] == "FormatFactoryError"

    def test_clean_hierarchy_passes(self, tmp_path):
        """Root exception class based directly on FormatFactoryError → PASS."""
        pkg = tmp_path / "src" / "python" / "goodbase"
        _write(pkg / "exceptions.py", (
            "class FormatFactoryError(Exception):\n"
            "    pass\n"
            "\n"
            "class GoodbaseError(FormatFactoryError):\n"
            "    pass\n"
            "\n"
            "class GoodbaseParseError(GoodbaseError):\n"
            "    pass\n"
        ))

        result = validate_exception_hierarchy_correctness({}, repo_root=tmp_path)

        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False
        assert result["items"] == []

    def test_valueerror_base_fails(self, tmp_path):
        pkg = tmp_path / "src" / "python" / "vfmt"
        _write(pkg / "exceptions.py", (
            "class VfmtError(ValueError):\n"
            "    pass\n"
            "\n"
            "class VfmtParseError(VfmtError):\n"
            "    pass\n"
        ))

        result = validate_exception_hierarchy_correctness({}, repo_root=tmp_path)

        assert result["result"] == "FAIL"
        item = result["items"][0]
        assert item["package"] == "vfmt"
        assert item["actual_base"] == "ValueError"

    def test_exception_base_fails(self, tmp_path):
        pkg = tmp_path / "src" / "python" / "efmt"
        _write(pkg / "exceptions.py", (
            "class EfmtError(Exception):\n"
            "    pass\n"
        ))

        result = validate_exception_hierarchy_correctness({}, repo_root=tmp_path)

        assert result["result"] == "FAIL"
        item = result["items"][0]
        assert item["package"] == "efmt"
        assert item["actual_base"] == "Exception"

    def test_core_package_is_excluded(self, tmp_path):
        """`core` is the shared-infra package where FormatFactoryError itself is
        DEFINED -- checking whether its own root class "derives from" FormatFactoryError
        is a category error and must be skipped, not FAILed for a missing file."""
        pkg = tmp_path / "src" / "python" / "core"
        _write(pkg / "src" / "format_factory" / "core" / "errors.py", (
            "class FormatFactoryError(Exception):\n"
            "    pass\n"
        ))

        result = validate_exception_hierarchy_correctness({}, repo_root=tmp_path)

        assert result["result"] == "PASS"
        assert result["items"] == []

    def test_nested_errors_module_preferred_over_stray_top_level_shim(self, tmp_path):
        """A package migrated to the nested src-layout (`src/format_factory/<pkg>/
        errors.py`) is checked there -- a stray top-level exceptions.py left over from
        before the migration (and excluded from the built wheel) must not shadow it."""
        pkg = tmp_path / "src" / "python" / "migrated"
        _write(pkg / "exceptions.py", (
            "class MigratedError(RuntimeError):\n"
            "    \"\"\"Stray pre-migration file -- not part of the built wheel.\"\"\"\n"
        ))
        _write(pkg / "src" / "format_factory" / "migrated" / "errors.py", (
            "from format_factory.core import FormatFactoryError\n"
            "\n"
            "\n"
            "class MigratedError(FormatFactoryError):\n"
            "    pass\n"
        ))

        result = validate_exception_hierarchy_correctness({}, repo_root=tmp_path)

        assert result["result"] == "PASS"
        assert result["items"] == []

    def test_root_basing_on_a_core_category_class_passes(self, tmp_path):
        """A root class based on one of format_factory.core's own four category
        classes (not FormatFactoryError itself) still ultimately terminates at
        FormatFactoryError one hop away -- e.g. ora's `OraError(FormatParseError)`,
        safetensors' `SafeTensorsError(FormatValidationError)` -- and must PASS."""
        pkg = tmp_path / "src" / "python" / "catfmt"
        _write(pkg / "src" / "format_factory" / "catfmt" / "errors.py", (
            "from format_factory.core import FormatParseError\n"
            "\n"
            "\n"
            "class CatfmtError(FormatParseError):\n"
            "    pass\n"
        ))

        result = validate_exception_hierarchy_correctness({}, repo_root=tmp_path)

        assert result["result"] == "PASS"
        assert result["items"] == []

    def test_root_basing_on_an_unrelated_class_via_nested_path_still_fails(self, tmp_path):
        """The nested-path preference and the widened accepted-base set must not turn
        this into a rubber stamp -- a genuinely wrong base still FAILs."""
        pkg = tmp_path / "src" / "python" / "badnested"
        _write(pkg / "src" / "format_factory" / "badnested" / "errors.py", (
            "class BadnestedError(RuntimeError):\n"
            "    pass\n"
        ))

        result = validate_exception_hierarchy_correctness({}, repo_root=tmp_path)

        assert result["result"] == "FAIL"
        item = result["items"][0]
        assert item["package"] == "badnested"
        assert item["actual_base"] == "RuntimeError"

    def test_try_except_fallback_pattern_passes(self, tmp_path):
        """The documented try/except _shared._shared_exceptions fallback aliasing is
        accepted -- what matters is the literal AST base name, not how it was bound."""
        pkg = tmp_path / "src" / "python" / "tryfmt"
        _write(pkg / "exceptions.py", (
            "try:\n"
            "    from _shared._shared_exceptions import FormatFactoryError\n"
            "except ImportError:\n"
            "    FormatFactoryError = Exception\n"
            "\n"
            "\n"
            "class TryfmtError(FormatFactoryError):\n"
            "    \"\"\"Base exception for all tryfmt format errors.\"\"\"\n"
            "\n"
            "\n"
            "class TryfmtParseError(TryfmtError):\n"
            "    pass\n"
        ))

        result = validate_exception_hierarchy_correctness({}, repo_root=tmp_path)

        assert result["result"] == "PASS"
        assert result["items"] == []


# ---------------------------------------------------------------------------
# V244 — validate_analytics_module_wiring
# ---------------------------------------------------------------------------

class TestV244AnalyticsModuleWiring:
    def test_unwired_analytics_file_fails(self, tmp_path):
        pkg = tmp_path / "src" / "python" / "unwiredfmt"
        _write(pkg / "unwiredfmt_analytics.py", "def compute_x(doc):\n    return 1\n")
        _write(pkg / "__init__.py", (
            "from .unwiredfmt_parser import *  # noqa: F401, F403\n"
        ))
        _write(pkg / "unwiredfmt_parser.py", "def parse():\n    return {}\n")

        result = validate_analytics_module_wiring({}, repo_root=tmp_path)

        assert result["validator"] == "validate_analytics_module_wiring"
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True
        assert len(result["items"]) == 1
        item = result["items"][0]
        assert item["package"] == "unwiredfmt"
        assert "unwiredfmt_analytics.py" in item["unwired_file"]

    def test_wired_analytics_file_passes(self, tmp_path):
        pkg = tmp_path / "src" / "python" / "wiredfmt"
        _write(pkg / "wiredfmt_analytics.py", "def compute_x(doc):\n    return 1\n")
        _write(pkg / "__init__.py", (
            "from .wiredfmt_analytics import *  # noqa: F401, F403\n"
        ))

        result = validate_analytics_module_wiring({}, repo_root=tmp_path)

        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False
        assert result["items"] == []

    def test_absolute_style_import_counts_as_wired(self, tmp_path):
        """Newer packages (ipynb, mtlx, nrrd, safetensors, ubl, xliff) import analytics
        via an ABSOLUTE dotted path (`from pkg.foo_analytics import x`) rather than a
        relative one (`from .foo_analytics import *`). Both must be recognized as wired
        -- comparing only the last dotted segment, not the full module string."""
        pkg = tmp_path / "src" / "python" / "abscheck"
        _write(pkg / "abscheck_analytics.py", "def compute_y(doc):\n    return 2\n")
        _write(pkg / "__init__.py", (
            "from abscheck.abscheck_analytics import compute_y  # noqa: F401\n"
        ))

        result = validate_analytics_module_wiring({}, repo_root=tmp_path)

        assert result["result"] == "PASS"
        assert result["items"] == []

    def test_no_analytics_file_passes(self, tmp_path):
        """A package with no analytics file at all has nothing to wire → PASS."""
        pkg = tmp_path / "src" / "python" / "noanalyticsfmt"
        _write(pkg / "__init__.py", "from .parser import *  # noqa: F401, F403\n")
        _write(pkg / "parser.py", "def parse():\n    return {}\n")

        result = validate_analytics_module_wiring({}, repo_root=tmp_path)

        assert result["result"] == "PASS"
        assert result["items"] == []


# ---------------------------------------------------------------------------
# V246 -- validate_no_nested_duplicate_packages
# ---------------------------------------------------------------------------

class TestV246NoNestedDuplicatePackages:
    def test_clean_tree_passes(self, tmp_path):
        pkg = tmp_path / "src" / "python" / "cleanfmt"
        _write(pkg / "__init__.py", "x = 1\n")
        _write(pkg / "parser.py", "def parse(): return {}\n")
        _write(pkg / "exceptions.py", "class CleanfmtError(Exception): pass\n")

        result = validate_no_nested_duplicate_packages({}, repo_root=tmp_path)

        assert result["validator"] == "validate_no_nested_duplicate_packages"
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False
        assert result["items"] == []

    def test_self_nested_directory_fails(self, tmp_path):
        pkg = tmp_path / "src" / "python" / "fods"
        _write(pkg / "__init__.py", "x = 1\n")
        _write(pkg / "parser.py", "def parse(): return {}\n")
        nested = pkg / "fods"
        _write(nested / "__init__.py", "x = 1\n")
        _write(nested / "parser.py", "def parse(): return {}\n")

        result = validate_no_nested_duplicate_packages({}, repo_root=tmp_path)

        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True
        assert len(result["items"]) == 1
        item = result["items"][0]
        assert item["package"] == "fods"
        assert "fods/fods" in item["nested_path"]
        assert item["file_count"] == 2

    def test_multiple_nested_duplicates_all_reported(self, tmp_path):
        for fmt in ["fods", "fodt"]:
            pkg = tmp_path / "src" / "python" / fmt
            _write(pkg / "__init__.py", "")
            nested = pkg / fmt
            _write(nested / "__init__.py", "")

        result = validate_no_nested_duplicate_packages({}, repo_root=tmp_path)

        assert result["result"] == "FAIL"
        assert len(result["items"]) == 2
        packages = {item["package"] for item in result["items"]}
        assert packages == {"fods", "fodt"}

    def test_different_named_subdirectory_passes(self, tmp_path):
        pkg = tmp_path / "src" / "python" / "fods"
        _write(pkg / "__init__.py", "")
        _write(pkg / "Compat" / "__init__.py", "")
        _write(pkg / "spec" / "office" / "document.py", "")

        result = validate_no_nested_duplicate_packages({}, repo_root=tmp_path)

        assert result["result"] == "PASS"
        assert result["items"] == []

    def test_nested_duplicate_with_diverged_files_fails(self, tmp_path):
        pkg = tmp_path / "src" / "python" / "demo"
        _write(pkg / "__init__.py", "# canonical")
        _write(pkg / "models.py", "class Doc: pass")
        nested = pkg / "demo"
        _write(nested / "__init__.py", "# stale copy")
        _write(nested / "models.py", "class Doc: pass  # old")

        result = validate_no_nested_duplicate_packages({}, repo_root=tmp_path)

        assert result["result"] == "FAIL"
        assert result["items"][0]["package"] == "demo"

    def test_infra_dirs_ignored(self, tmp_path):
        (tmp_path / "src" / "python" / "__pycache__" / "__pycache__").mkdir(parents=True)
        (tmp_path / "src" / "python" / "build" / "build").mkdir(parents=True)

        result = validate_no_nested_duplicate_packages({}, repo_root=tmp_path)

        assert result["result"] == "PASS"
        assert result["items"] == []

    def test_underscore_prefixed_dirs_ignored(self, tmp_path):
        _write(tmp_path / "src" / "python" / "_shared" / "_shared" / "base.py", "")

        result = validate_no_nested_duplicate_packages({}, repo_root=tmp_path)

        assert result["result"] == "PASS"
        assert result["items"] == []

    def test_no_src_python_dir_passes(self, tmp_path):
        result = validate_no_nested_duplicate_packages({}, repo_root=tmp_path)

        assert result["result"] == "PASS"
        assert result["items"] == []

    def test_empty_nested_dir_still_fails(self, tmp_path):
        pkg = tmp_path / "src" / "python" / "emptyfmt"
        _write(pkg / "__init__.py", "")
        nested = pkg / "emptyfmt"
        nested.mkdir(parents=True, exist_ok=True)

        result = validate_no_nested_duplicate_packages({}, repo_root=tmp_path)

        assert result["result"] == "FAIL"
        assert result["items"][0]["package"] == "emptyfmt"
        assert result["items"][0]["file_count"] == 0


# ---------------------------------------------------------------------------
# V245 — validate_oracle_registry_reconciliation (TC-PA-031)
#
# `oracle/registry/format-oracle-registry.yaml` is the single source of truth for
# oracle status. The `status:` in oracle/formats/<fmt>/oracle-package.yaml is a
# derived mirror with no producer, which is how 6 formats (ipynb, mtlx, nrrd,
# safetensors, ubl, xliff) shipped `status: VERIFIED` at birth while the registry
# recorded CASES_DEFINED at proof level 1/4. These tests pin the drift gate.
# ---------------------------------------------------------------------------

def _oracle_fixture(root: Path, entries: list[dict], packages: dict[str, str]) -> None:
    """Build a synthetic oracle/ tree. entries -> registry rows; packages -> {fmt: status}."""
    import yaml as _yaml

    reg_dir = root / "oracle" / "registry"
    reg_dir.mkdir(parents=True, exist_ok=True)
    (reg_dir / "format-oracle-registry.yaml").write_text(
        _yaml.safe_dump({"format_oracles": entries}), encoding="utf-8"
    )
    for fmt, status in packages.items():
        pkg_dir = root / "oracle" / "formats" / fmt
        pkg_dir.mkdir(parents=True, exist_ok=True)
        body = {"oracle_id": f"oracle-{fmt}-v1", "format_id": fmt}
        if status is not None:
            body["status"] = status
        (pkg_dir / "oracle-package.yaml").write_text(_yaml.safe_dump(body), encoding="utf-8")


def _reg_row(fmt: str, product_status: str, **kw) -> dict:
    row = {
        "format_id": fmt,
        "oracle_package": f"oracle/formats/{fmt}/oracle-package.yaml",
        "product_oracle_status": product_status,
    }
    row.update(kw)
    return row


class TestV245OracleRegistryReconciliation:
    def test_status_drift_fails_and_blocks(self, tmp_path):
        """PRE-FIX REPLAY: package claims VERIFIED, registry says CASES_DEFINED → FAIL.

        This is the exact 2026-07-15 defect (commit 1adfdc47, select-6 onboarding):
        the package was born VERIFIED from a template literal while its oracle had
        actually run 1/5 PASS + 4 NOT_APPLICABLE. Without this assertion V245 would
        report "all packages reconcile" while 6 formats contradicted the registry.
        """
        _oracle_fixture(
            tmp_path,
            [_reg_row("ipynb", "CASES_DEFINED", depth_achieved="D0",
                      current_proof_level=1, target_proof_level=4,
                      blockers=["Oracle PARTIAL_PASS (4/5 NOT_APPLICABLE)"])],
            {"ipynb": "VERIFIED"},
        )

        result = validate_oracle_registry_reconciliation({}, repo_root=tmp_path)

        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True
        drift = [i for i in result["items"] if i["issue"].startswith("STATUS_DRIFT")]
        assert len(drift) == 1
        assert drift[0]["format"] == "ipynb"
        assert drift[0]["package_status"] == "VERIFIED"
        assert drift[0]["registry_product_oracle_status"] == "CASES_DEFINED"
        # the registry's audit trail must travel with the finding
        assert drift[0]["current_proof_level"] == 1
        assert drift[0]["blockers"]
        # remedy must point at the package, never at promoting the registry
        assert "oracle/formats/ipynb/oracle-package.yaml" in drift[0]["remedy"]

    def test_matching_status_passes(self, tmp_path):
        """Package status == registry product_oracle_status → PASS."""
        _oracle_fixture(
            tmp_path,
            [_reg_row("ipynb", "CASES_DEFINED"), _reg_row("fods", "VERIFIED")],
            {"ipynb": "CASES_DEFINED", "fods": "VERIFIED"},
        )

        result = validate_oracle_registry_reconciliation({}, repo_root=tmp_path)

        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_drift_in_either_direction_fails(self, tmp_path):
        """A package UNDER-claiming vs the registry is also drift — SSoT is exact."""
        _oracle_fixture(
            tmp_path, [_reg_row("fods", "VERIFIED")], {"fods": "CASES_DEFINED"}
        )

        result = validate_oracle_registry_reconciliation({}, repo_root=tmp_path)

        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True

    def test_missing_status_field_is_the_reconciled_desired_state(self, tmp_path):
        """TC-PA-041: the mirror field is ELIMINATED. Absence is reconciliation.

        The whole point of TC-PA-041 is that no package should carry a `status:` field
        at all — coverage derives status from the registry. So a package with no status
        (registry entry present) is the DESIRED steady state and must PASS, not WARN.
        """
        _oracle_fixture(tmp_path, [_reg_row("fods", "VERIFIED")], {"fods": None})

        result = validate_oracle_registry_reconciliation({}, repo_root=tmp_path)

        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False
        assert not any("no status" in i.get("issue", "") for i in result["items"])

    def test_reintroduced_conflicting_status_still_blocks(self, tmp_path):
        """TC-PA-041 REINTRODUCTION GUARD: a revert/re-onboard writing a conflicting
        `status:` back into a package (the exact 1adfdc47 failure mode) still FAILs.
        """
        _oracle_fixture(
            tmp_path,
            [_reg_row("ipynb", "CASES_DEFINED", depth_achieved="D0",
                      current_proof_level=1, target_proof_level=4)],
            {"ipynb": "VERIFIED"},  # mirror reintroduced with a false-green value
        )

        result = validate_oracle_registry_reconciliation({}, repo_root=tmp_path)

        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True
        drift = [i for i in result["items"] if i["issue"].startswith("STATUS_DRIFT")]
        assert len(drift) == 1
        # remedy must tell the caller to REMOVE the reintroduced field, not to author it
        assert "remove" in drift[0]["remedy"].lower()

    def test_reintroduced_but_matching_status_is_tolerated(self, tmp_path):
        """A reintroduced status that MATCHES the registry is harmless -> PASS."""
        _oracle_fixture(
            tmp_path, [_reg_row("fods", "VERIFIED")], {"fods": "VERIFIED"}
        )

        result = validate_oracle_registry_reconciliation({}, repo_root=tmp_path)

        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_uncomparable_vocabulary_is_reported_not_passed(self, tmp_path):
        """OBLIGATION_CREATED is not in the package enum → report, never silent-pass."""
        _oracle_fixture(
            tmp_path, [_reg_row("pam", "OBLIGATION_CREATED")], {"pam": "SCAFFOLDED"}
        )

        result = validate_oracle_registry_reconciliation({}, repo_root=tmp_path)

        assert result["result"] == "WARN"
        assert any("UNCOMPARABLE_STATUS_VOCABULARY" in i["issue"] for i in result["items"])

    def test_package_without_registry_entry_still_warns(self, tmp_path):
        """Original V245 behavior preserved: on-disk package, no registry row → WARN."""
        _oracle_fixture(tmp_path, [], {"orphan": "VERIFIED"})

        result = validate_oracle_registry_reconciliation({}, repo_root=tmp_path)

        assert result["result"] == "WARN"
        assert any("no registry entry" in i["issue"] for i in result["items"])
