"""Tests for governance_validators_dotnet.py — V73 + V78_AGG.

TC-SPW-001-07: V78_AGG tests (≥5 cases).
"""
from __future__ import annotations

import json
import textwrap
from pathlib import Path

import pytest

import sys
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "tools" / "supervisor"))

from governance_validators_dotnet import (
    collect_partial_class_aggregates,
    validate_dotnet_aggregate_loc_cap,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _write_cs(directory: Path, filename: str, content: str) -> Path:
    f = directory / filename
    f.write_text(content, encoding="utf-8")
    return f


def _make_declaration(changed_files=None):
    return {"planned_work_items": [], "changed_files": changed_files or []}


def _make_baseline(aggregates: dict) -> dict:
    """Return a minimal source-structure-baseline.json dict."""
    return {"known_violations": {}, "partial_class_aggregates": aggregates}


# ---------------------------------------------------------------------------
# collect_partial_class_aggregates tests
# ---------------------------------------------------------------------------

class TestCollectPartialClassAggregates:

    def test_single_non_partial_class_not_returned(self, tmp_path):
        """Single non-partial class file → not in results (no multi-file group)."""
        _write_cs(tmp_path, "MyClass.cs", "public class MyClass { }\n")
        result = collect_partial_class_aggregates(tmp_path)
        # No class appears ≥2 times → empty result
        assert "MyClass" not in result

    def test_two_partial_files_collected(self, tmp_path):
        """Two partial class files for the same class → returned as a group."""
        _write_cs(tmp_path, "Widget.cs", "public partial class Widget { int x; }\n" * 10)
        _write_cs(tmp_path, "WidgetOps.cs", "public partial class Widget { void F() {} }\n" * 10)
        result = collect_partial_class_aggregates(tmp_path)
        assert "Widget" in result
        assert len(result["Widget"]) == 2

    def test_generated_file_excluded(self, tmp_path):
        """*.g.cs files are excluded from aggregate calculation."""
        _write_cs(tmp_path, "Foo.cs", "public partial class Foo { int a; }\n" * 20)
        _write_cs(tmp_path, "Foo.g.cs", "public partial class Foo { int b; }\n" * 100)
        result = collect_partial_class_aggregates(tmp_path)
        if "Foo" in result:
            # Only the non-generated file should be in the group
            names = [f.name for f, _ in result["Foo"]]
            assert "Foo.g.cs" not in names

    def test_designer_file_excluded(self, tmp_path):
        """*.designer.cs files are excluded."""
        _write_cs(tmp_path, "Bar.cs", "public partial class Bar { int x; }\n" * 20)
        _write_cs(tmp_path, "Bar.designer.cs", "public partial class Bar { int y; }\n" * 50)
        result = collect_partial_class_aggregates(tmp_path)
        if "Bar" in result:
            names = [f.name for f, _ in result["Bar"]]
            assert "Bar.designer.cs" not in names

    def test_missing_directory_returns_empty(self):
        """Missing src_net_root returns empty dict without error."""
        result = collect_partial_class_aggregates(Path("/nonexistent/path/xyz"))
        assert result == {}


# ---------------------------------------------------------------------------
# validate_dotnet_aggregate_loc_cap (V78_AGG) tests
# ---------------------------------------------------------------------------

class TestValidateDotnetAggregateLocCap:

    def test_no_partial_classes_returns_pass(self, tmp_path):
        """No partial class groups in src_net_root → PASS, blocks_sprint=False."""
        (tmp_path / "src" / "net").mkdir(parents=True)
        _write_cs(tmp_path / "src" / "net", "Solo.cs", "public class Solo { }\n")
        decl = _make_declaration()
        result = validate_dotnet_aggregate_loc_cap(decl, tmp_path)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_known_violation_stable_returns_warn(self, tmp_path, monkeypatch):
        """Known aggregate violation stable (not touched, not grown) → WARN, blocks_sprint=False."""
        net_root = tmp_path / "src" / "net" / "myformat"
        net_root.mkdir(parents=True)
        # 2 partial files for BigClass totaling 600 LOC
        big_content = "public partial class BigClass { int x; }\n" * 300
        _write_cs(net_root, "BigClass.cs", big_content)
        _write_cs(net_root, "BigClassOps.cs", big_content)

        # Patch baseline: BigClass is known with cap=600
        baseline = _make_baseline({
            "BigClass": {"aggregate_cap": 600, "trajectory": "decrease_required_on_touch"}
        })
        baseline_path = tmp_path / "registry" / "source-structure-baseline.json"
        baseline_path.parent.mkdir(parents=True)
        baseline_path.write_text(json.dumps(baseline), encoding="utf-8")

        import governance_validators_dotnet as gvd
        monkeypatch.setattr(gvd, "_BASELINE_PATH", baseline_path)
        monkeypatch.setattr(gvd, "_REPO_ROOT", tmp_path)

        decl = _make_declaration(changed_files=[])  # No files touched
        result = gvd.validate_dotnet_aggregate_loc_cap(decl, tmp_path)
        assert result["result"] == "WARN"
        assert result["blocks_sprint"] is False
        assert any(i["issue"] == "KNOWN_VIOLATION" for i in result["items"])

    def test_trajectory_fail_when_known_violation_grows(self, tmp_path, monkeypatch):
        """Known aggregate violation where sprint touched file and aggregate grew → FAIL blocks_sprint=True."""
        net_root = tmp_path / "src" / "net" / "myformat"
        net_root.mkdir(parents=True)
        # BigClass aggregate currently 1000 LOC across 2 files
        content_a = "public partial class BigClass { int x; }\n" * 500
        content_b = "public partial class BigClass { int y; }\n" * 500
        fa = _write_cs(net_root, "BigClass.cs", content_a)
        fb = _write_cs(net_root, "BigClassOps.cs", content_b)

        # Baseline says cap was 800 (aggregate has grown beyond cap)
        baseline = _make_baseline({
            "BigClass": {"aggregate_cap": 800, "trajectory": "decrease_required_on_touch"}
        })
        baseline_path = tmp_path / "registry" / "source-structure-baseline.json"
        baseline_path.parent.mkdir(parents=True)
        baseline_path.write_text(json.dumps(baseline), encoding="utf-8")

        import governance_validators_dotnet as gvd
        monkeypatch.setattr(gvd, "_BASELINE_PATH", baseline_path)
        monkeypatch.setattr(gvd, "_REPO_ROOT", tmp_path)

        # Declare that BigClass.cs was changed this sprint
        decl = _make_declaration(changed_files=[str(fa.as_posix())])
        result = gvd.validate_dotnet_aggregate_loc_cap(decl, tmp_path)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True
        assert any(i["issue"] == "TRAJECTORY_FAIL" for i in result["items"])

    def test_new_aggregate_violation_fails(self, tmp_path, monkeypatch):
        """New partial class group exceeding cap (not in baselines) → FAIL blocks_sprint=True."""
        net_root = tmp_path / "src" / "net" / "myformat"
        net_root.mkdir(parents=True)
        # NewGiant: 3 files totaling 2500 LOC → exceeds 2000 default cap
        content = "public partial class NewGiant { int x; }\n" * 834
        for i in range(3):
            _write_cs(net_root, f"NewGiant{i}.cs", content)

        # Empty baselines (no known violations)
        baseline = _make_baseline({})
        baseline_path = tmp_path / "registry" / "source-structure-baseline.json"
        baseline_path.parent.mkdir(parents=True)
        baseline_path.write_text(json.dumps(baseline), encoding="utf-8")

        import governance_validators_dotnet as gvd
        monkeypatch.setattr(gvd, "_BASELINE_PATH", baseline_path)
        monkeypatch.setattr(gvd, "_REPO_ROOT", tmp_path)

        decl = _make_declaration()
        result = gvd.validate_dotnet_aggregate_loc_cap(decl, tmp_path)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True
        assert any(i["issue"] == "NEW_AGGREGATE_VIOLATION" for i in result["items"])

    def test_generated_cs_not_counted_in_aggregate(self, tmp_path, monkeypatch):
        """*.g.cs files excluded — aggregate stays within cap even if *.g.cs is large."""
        net_root = tmp_path / "src" / "net" / "myformat"
        net_root.mkdir(parents=True)
        # Real file: 400 LOC
        _write_cs(net_root, "Comp.cs", "public partial class Comp { int x; }\n" * 200)
        # Real file: 400 LOC
        _write_cs(net_root, "CompOps.cs", "public partial class Comp { int y; }\n" * 200)
        # Generated file: 5000 LOC — must NOT count
        _write_cs(net_root, "Comp.g.cs", "public partial class Comp { int z; }\n" * 2500)

        # No baselines (new class, cap=2000)
        baseline = _make_baseline({})
        baseline_path = tmp_path / "registry" / "source-structure-baseline.json"
        baseline_path.parent.mkdir(parents=True)
        baseline_path.write_text(json.dumps(baseline), encoding="utf-8")

        import governance_validators_dotnet as gvd
        monkeypatch.setattr(gvd, "_BASELINE_PATH", baseline_path)
        monkeypatch.setattr(gvd, "_REPO_ROOT", tmp_path)

        decl = _make_declaration()
        result = gvd.validate_dotnet_aggregate_loc_cap(decl, tmp_path)
        # Real aggregate is 800 LOC (under 2000 cap) → PASS
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_actual_repo_fods_returns_warn_not_fail(self):
        """Running V78_AGG against actual src/net/ returns WARN for known violations, not FAIL."""
        decl = _make_declaration()
        result = validate_dotnet_aggregate_loc_cap(decl, Path("."))
        # Known violations (FodsDocument, FodtDocument) are stable → WARN not FAIL
        assert result["result"] in ("WARN", "PASS")
        assert result["blocks_sprint"] is False


# ---------------------------------------------------------------------------
# V88 new/existing distinction tests (TC-SPW-002-04)
# ---------------------------------------------------------------------------

class TestV88NewExistingDistinction:
    """Tests for V88 TC-SPW-002: new additions FAIL, pre-existing WARN."""

    _DICT_METHOD_CS = textwrap.dedent("""\
        public partial class MyDoc
        {
            private readonly System.Collections.Generic.Dictionary<string, string> _cellData = new();

            public void SetCellValue(string key, string val)
            {
                _cellData[key] = val;
            }

            public string GetCellValue(string key)
            {
                return _cellData[key];
            }
        }
    """)

    _WIRED_METHOD_CS = textwrap.dedent("""\
        public partial class MyDoc
        {
            private readonly System.Collections.Generic.Dictionary<string, string> _cellData = new();

            public void SetCellValue(string key, string val)
            {
                SetAttributeValue(key, val);
            }
        }
    """)

    def test_new_dict_method_fails_with_git_state(self, tmp_path, monkeypatch):
        """New dict-only method introduced this sprint → V88 FAIL, blocks_sprint=True."""
        import governance_validators_dotnet_semantic as gvds

        # git show would return empty string (method NOT found in old version)
        monkeypatch.setattr(
            gvds,
            "_method_existed_at_git_head",
            lambda sha, path, method, repo: False,  # method is NEW
        )

        cs_file = tmp_path / "MyDoc.cs"
        cs_file.write_text(self._DICT_METHOD_CS, encoding="utf-8")

        rel_path = "src/net/myformat/MyDoc.cs"
        decl = {
            "planned_work_items": [{"item_type": "PRODUCT_SOURCE"}],
            "changed_files": [rel_path],
            "git_head_start": "abc1234",
        }

        # Patch the source file lookup
        full_path = tmp_path / rel_path
        full_path.parent.mkdir(parents=True)
        full_path.write_text(self._DICT_METHOD_CS, encoding="utf-8")

        result = gvds.validate_dotnet_detached_dictionary_fields(decl, tmp_path)
        assert result["result"] == "FAIL", f"Expected FAIL, got {result['result']}"
        assert result["blocks_sprint"] is True
        new_items = [i for i in result["items"] if i.get("origin") == "new_this_sprint"]
        assert len(new_items) >= 1

    def test_preexisting_dict_method_warns_with_git_state(self, tmp_path, monkeypatch):
        """Pre-existing dict-only method (existed before sprint) → V88 WARN, blocks_sprint=False."""
        import governance_validators_dotnet_semantic as gvds

        monkeypatch.setattr(
            gvds,
            "_method_existed_at_git_head",
            lambda sha, path, method, repo: True,  # method existed before sprint
        )

        rel_path = "src/net/myformat/MyDoc.cs"
        decl = {
            "planned_work_items": [{"item_type": "PRODUCT_SOURCE"}],
            "changed_files": [rel_path],
            "git_head_start": "abc1234",
        }

        full_path = tmp_path / rel_path
        full_path.parent.mkdir(parents=True)
        full_path.write_text(self._DICT_METHOD_CS, encoding="utf-8")

        result = gvds.validate_dotnet_detached_dictionary_fields(decl, tmp_path)
        assert result["result"] == "WARN", f"Expected WARN, got {result['result']}"
        assert result["blocks_sprint"] is False
        existing_items = [i for i in result["items"] if i.get("origin") == "pre_existing"]
        assert len(existing_items) >= 1

    def test_wired_dict_method_passes(self, tmp_path):
        """Dict field with XML write path reference → V88 PASS."""
        import governance_validators_dotnet_semantic as gvds

        rel_path = "src/net/myformat/MyDoc.cs"
        decl = {
            "planned_work_items": [{"item_type": "PRODUCT_SOURCE"}],
            "changed_files": [rel_path],
            "git_head_start": "",
        }

        full_path = tmp_path / rel_path
        full_path.parent.mkdir(parents=True)
        full_path.write_text(self._WIRED_METHOD_CS, encoding="utf-8")

        result = gvds.validate_dotnet_detached_dictionary_fields(decl, tmp_path)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_no_changed_cs_files_passes(self, tmp_path):
        """No changed .cs files in sprint → V88 PASS immediately."""
        import governance_validators_dotnet_semantic as gvds

        decl = {
            "planned_work_items": [],
            "changed_files": [],  # no .cs files changed
        }
        result = gvds.validate_dotnet_detached_dictionary_fields(decl, tmp_path)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_no_git_state_falls_back_to_fail(self, tmp_path):
        """No git_head_start → violations are FAIL (conservative: cannot prove pre-existing).

        TC-FGSQ-003: When git_head_start is absent, V88 cannot distinguish new from
        pre-existing methods, so it treats all violations as new (FAIL) to prevent
        dict-backed methods from accumulating without detection.
        """
        import governance_validators_dotnet_semantic as gvds

        rel_path = "src/net/myformat/MyDoc.cs"
        decl = {
            "planned_work_items": [{"item_type": "PRODUCT_SOURCE"}],
            "changed_files": [rel_path],
            # No git_head_start — conservative FAIL (TC-FGSQ-003)
        }

        full_path = tmp_path / rel_path
        full_path.parent.mkdir(parents=True)
        full_path.write_text(self._DICT_METHOD_CS, encoding="utf-8")

        result = gvds.validate_dotnet_detached_dictionary_fields(decl, tmp_path)
        # Without git_head_start, violations are unknown-origin → FAIL (conservative)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True


# ---------------------------------------------------------------------------
# V152 validate_format_roundtrip_coverage tests (TC-SPW-003B-03)
# ---------------------------------------------------------------------------

class TestV152FormatRoundtripCoverage:
    """Tests for V152: Gate-1 formats must have .NET round-trip test coverage."""

    def _make_fake_registry(self, tmp_path: Path, gate1_formats: list) -> Path:
        """Write a minimal format-registry.yaml with the given formats at gate_1 passed."""
        import yaml
        formats = []
        for fmt_id in gate1_formats:
            formats.append({
                "format_id": fmt_id,
                "gates": {"gate_1": {"status": "passed"}},
            })
        reg_dir = tmp_path / "registry"
        reg_dir.mkdir(parents=True, exist_ok=True)
        reg_path = reg_dir / "format-registry.yaml"
        reg_path.write_text(yaml.dump({"formats": formats}), encoding="utf-8")
        return reg_path

    def _write_roundtrip_test(self, tmp_path: Path, format_id: str) -> None:
        """Write a .cs test file with both Load() and Save() calls."""
        test_dir = tmp_path / "tests" / "net" / format_id
        test_dir.mkdir(parents=True, exist_ok=True)
        (test_dir / "RoundtripTest.cs").write_text(
            "var doc = FodsDocument.Load(path);\ndoc.Save(outpath);\n",
            encoding="utf-8",
        )

    def test_no_format_targets_passes(self, tmp_path, monkeypatch):
        """Declaration with no format_targets and no src/net/ paths → PASS (no scope)."""
        import governance_validators_dotnet as gvd
        self._make_fake_registry(tmp_path, ["fods"])
        monkeypatch.setattr(gvd, "_FORMAT_REGISTRY_PATH", tmp_path / "registry" / "format-registry.yaml")
        monkeypatch.setattr(gvd, "_TESTS_NET_ROOT", tmp_path / "tests" / "net")

        decl = {"planned_work_items": [], "changed_files": [], "format_targets": []}
        result = gvd.validate_format_roundtrip_coverage(decl, tmp_path)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_gate1_format_with_roundtrip_passes(self, tmp_path, monkeypatch):
        """Gate-1 format with a matching round-trip test → PASS."""
        import governance_validators_dotnet as gvd
        self._make_fake_registry(tmp_path, ["fods"])
        self._write_roundtrip_test(tmp_path, "fods")
        monkeypatch.setattr(gvd, "_FORMAT_REGISTRY_PATH", tmp_path / "registry" / "format-registry.yaml")
        monkeypatch.setattr(gvd, "_TESTS_NET_ROOT", tmp_path / "tests" / "net")

        decl = {"planned_work_items": [], "format_targets": ["fods"]}
        result = gvd.validate_format_roundtrip_coverage(decl, tmp_path)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_gate1_format_missing_roundtrip_fails(self, tmp_path, monkeypatch):
        """Gate-1 format with no round-trip test → FAIL, blocks_sprint=True."""
        import governance_validators_dotnet as gvd
        self._make_fake_registry(tmp_path, ["fods"])
        # Write a test that only has Load() but no Save() — not a round-trip
        test_dir = tmp_path / "tests" / "net" / "fods"
        test_dir.mkdir(parents=True, exist_ok=True)
        (test_dir / "LoadOnlyTest.cs").write_text(
            "var doc = FodsDocument.Load(path);\n",
            encoding="utf-8",
        )
        monkeypatch.setattr(gvd, "_FORMAT_REGISTRY_PATH", tmp_path / "registry" / "format-registry.yaml")
        monkeypatch.setattr(gvd, "_TESTS_NET_ROOT", tmp_path / "tests" / "net")

        decl = {"planned_work_items": [], "format_targets": ["fods"]}
        result = gvd.validate_format_roundtrip_coverage(decl, tmp_path)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True
        assert any(i["issue"] == "NO_ROUNDTRIP_TEST" for i in result["items"])

    def test_non_gate1_format_not_checked(self, tmp_path, monkeypatch):
        """Format not at gate_1 → skipped (not in scope) → PASS."""
        import governance_validators_dotnet as gvd
        import yaml
        # no formats have gate_1 passed
        reg_path = tmp_path / "registry" / "format-registry.yaml"
        reg_path.parent.mkdir(parents=True, exist_ok=True)
        reg_path.write_text(yaml.dump({"formats": [
            {"format_id": "fods", "gates": {"gate_1": {"status": "pending"}}}
        ]}), encoding="utf-8")
        monkeypatch.setattr(gvd, "_FORMAT_REGISTRY_PATH", reg_path)
        monkeypatch.setattr(gvd, "_TESTS_NET_ROOT", tmp_path / "tests" / "net")

        decl = {"planned_work_items": [], "format_targets": ["fods"]}
        result = gvd.validate_format_roundtrip_coverage(decl, tmp_path)
        assert result["result"] == "PASS"

    def test_actual_repo_fods_passes(self):
        """Actual repo FODS has round-trip tests → V152 PASS for fods."""
        from governance_validators_dotnet import validate_format_roundtrip_coverage
        decl = {"planned_work_items": [], "format_targets": ["fods"]}
        result = validate_format_roundtrip_coverage(decl, Path("."))
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False
