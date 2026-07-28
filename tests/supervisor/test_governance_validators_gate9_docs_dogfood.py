"""TC-S6P4-SYS-003 (select-6 Phase 4): V228 (README) + V229 (dogfood export).
Hardened TC-S6P4-FINAL-001c (select-6 Phase 4 final re-audit, 2026-07-16):
V228 now runs real readme_sync content validation, not just existence; V229
now actually executes the cited dogfood test via pytest, not just checks
that the test file exists.

Closes SF3: neither requirement was checked by any validator before this.
"""
from __future__ import annotations

from pathlib import Path

import yaml

from governance_validators_gate9_docs_dogfood import (
    _validate_readme_content,
    validate_dogfood_export_exists as v229,
)
from governance_validators_gate9_docs_dogfood import (
    validate_format_readme_exists as v228,
)


def _write_registry(tmp_path, formats):
    (tmp_path / "registry").mkdir(parents=True, exist_ok=True)
    (tmp_path / "registry" / "format-registry.yaml").write_text(
        yaml.safe_dump({"formats": formats}), encoding="utf-8")


def _write_baseline(tmp_path, grandfathered_ids):
    (tmp_path / "registry" / "gate9-coverage-baseline.yaml").write_text(
        yaml.safe_dump({"grandfathered_pre_phase3":
                        [{"format_id": f} for f in grandfathered_ids]}),
        encoding="utf-8")


class TestV228Readme:
    def test_grandfathered_skipped(self, tmp_path):
        _write_registry(tmp_path, [{"format_id": "old", "implementation_authorized": True}])
        _write_baseline(tmp_path, ["old"])
        assert v228({}, tmp_path)["result"] == "PASS"

    def test_missing_readme_fails(self, tmp_path):
        _write_registry(tmp_path, [{"format_id": "new", "implementation_authorized": True}])
        _write_baseline(tmp_path, [])
        (tmp_path / "src" / "python" / "new").mkdir(parents=True)
        r = v228({}, tmp_path)
        assert r["result"] == "FAIL"
        assert r["blocks_sprint"] is True
        assert "new" in r["summary"]

    def test_present_readme_unverifiable_never_blocks(self, tmp_path):
        """A synthetic tmp_path fixture has no real src/python/new/ state
        for readme_sync's collect_format_state() to read against the real
        repo, so content validation is unverifiable -- existence still
        passed, so this must WARN at worst, never FAIL/block."""
        _write_registry(tmp_path, [{"format_id": "new", "implementation_authorized": True}])
        _write_baseline(tmp_path, [])
        d = tmp_path / "src" / "python" / "new"
        d.mkdir(parents=True)
        (d / "README.md").write_text("# new\n", encoding="utf-8")
        r = v228({}, tmp_path)
        assert r["result"] in ("PASS", "WARN")
        assert r["blocks_sprint"] is False

    def test_content_validation_catches_real_defect(self, tmp_path):
        """Unit-tests the hardened content-check directly against a real
        authorized format's actual README with one END marker deleted
        (begin/end mismatch) -- proves V228 does more than check
        Path.exists() (TC-S6P4-FINAL-001c: the original V228 would have
        PASSed this since the file still exists)."""
        repo = Path(__file__).resolve().parents[2]
        real_readme = repo / "src" / "python" / "mtlx" / "README.md"
        if not real_readme.exists():
            return
        content = real_readme.read_text(encoding="utf-8")
        corrupted = content.replace(
            "<!-- END:README-PACKAGE_INFO -->", "", 1
        )
        assert corrupted != content, "fixture assumption failed: marker text not found"
        corrupted_path = tmp_path / "README.md"
        corrupted_path.write_text(corrupted, encoding="utf-8")
        status, problems = _validate_readme_content(repo, "mtlx", corrupted_path)
        assert status == "invalid"
        assert any("marker" in p.lower() for p in problems), problems

    def test_content_validation_ok_for_real_readme(self, tmp_path):
        """The hardened check against a real, unmodified authorized-format
        README must pass -- proves it isn't just structurally incapable of
        ever returning ok."""
        repo = Path(__file__).resolve().parents[2]
        real_readme = repo / "src" / "python" / "mtlx" / "README.md"
        if not real_readme.exists():
            return
        status, problems = _validate_readme_content(repo, "mtlx", real_readme)
        assert status == "ok", problems


class TestV229Dogfood:
    def test_grandfathered_skipped(self, tmp_path):
        _write_registry(tmp_path, [{"format_id": "old", "implementation_authorized": True}])
        _write_baseline(tmp_path, ["old"])
        assert v229({}, tmp_path)["result"] == "PASS"

    def test_no_export_module_fails(self, tmp_path):
        _write_registry(tmp_path, [{"format_id": "new", "implementation_authorized": True}])
        _write_baseline(tmp_path, [])
        (tmp_path / "src" / "python" / "new").mkdir(parents=True)
        r = v229({}, tmp_path)
        assert r["result"] == "FAIL"
        assert "no src/python/new/new_to_*.py" in r["summary"]

    def test_export_without_test_fails(self, tmp_path):
        _write_registry(tmp_path, [{"format_id": "new", "implementation_authorized": True}])
        _write_baseline(tmp_path, [])
        d = tmp_path / "src" / "python" / "new"
        d.mkdir(parents=True)
        (d / "new_to_csv.py").write_text("def export():\n    pass\n", encoding="utf-8")
        r = v229({}, tmp_path)
        assert r["result"] == "FAIL"
        assert "no matching test" in r["summary"]

    def test_export_with_test_passes(self, tmp_path):
        _write_registry(tmp_path, [{"format_id": "new", "implementation_authorized": True}])
        _write_baseline(tmp_path, [])
        d = tmp_path / "src" / "python" / "new"
        d.mkdir(parents=True)
        (d / "new_to_csv.py").write_text("def export():\n    pass\n", encoding="utf-8")
        t = tmp_path / "tests" / "python" / "new"
        t.mkdir(parents=True)
        (t / "test_new_to_csv.py").write_text("def test_export():\n    pass\n", encoding="utf-8")
        assert v229({}, tmp_path)["result"] == "PASS"

    def test_live_repo_passes(self):
        """Regression proof: the 6 non-grandfathered authorized (select-6)
        formats each have a README that passes real content validation and
        a dogfood export whose test actually executes and passes -- this
        exercises the hardened execution paths against real repo state, not
        just existence checks."""
        repo = Path(__file__).resolve().parents[2]
        r228 = v228({}, repo)
        r229 = v229({}, repo)
        assert r228["result"] == "PASS", r228["summary"]
        assert r229["result"] == "PASS", r229["summary"]
