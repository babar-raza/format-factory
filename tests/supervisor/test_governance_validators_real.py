"""Real-file detection tests for V187-V193 governance validators.

Extracted from test_governance_validators.py to keep it within baseline_loc_cap.
FI-021 / FIOP-FULL-001: LOC healing 2026-07-15.

Original location: lively-leaping-elephant, TC-GOV-LLE-004C.
"""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


# ---------------------------------------------------------------------------
# Real-file detection tests (lively-leaping-elephant, TC-GOV-LLE-004C)
# ---------------------------------------------------------------------------

@pytest.mark.real_src
class TestValidatorDetectionRealFiles:
    """Tests that V187-V193 fire on known-violating real source files.

    These tests INTENTIONALLY fail if the target files are healed below the threshold.
    That is the correct behavior: a green result here means the governance gap is closed.
    Do NOT suppress or skip these tests when they fail — investigate and fix the violation.

    Uses @pytest.mark.real_src to allow CI to exclude from fast runs:
        pytest -m "not real_src"   # skip this class
        pytest -m real_src -v      # run only this class
    """

    REPO_ROOT = Path(__file__).resolve().parent.parent.parent

    def _decl_with_file(self, *paths: str) -> dict:
        return {"changed_files": list(paths), "planned_work_items": [], "work_items": []}

    def test_v187_warns_on_xcf_image_metrics(self):
        """V187 should WARN on xcf_image_metrics.py (104 top-level fn, in baseline -> WARN not FAIL)."""
        from governance_validators_ext5 import validate_function_count_per_file
        decl = self._decl_with_file("src/python/xcf/xcf_image_metrics.py")
        result = validate_function_count_per_file(decl, repo_root=self.REPO_ROOT)
        assert result["result"] in ("WARN", "FAIL"), (
            f"V187 expected WARN or FAIL on xcf_image_metrics.py (104 fn) but got {result['result']}. "
            "If this file has been healed below 80 functions, update this test."
        )

    def test_v187_warns_on_abw_word_document(self):
        """V187 should WARN on word_document.py (101 top-level fn, in baseline -> WARN not FAIL)."""
        from governance_validators_ext5 import validate_function_count_per_file
        decl = self._decl_with_file("src/python/abw/word_document.py")
        result = validate_function_count_per_file(decl, repo_root=self.REPO_ROOT)
        assert result["result"] in ("WARN", "FAIL"), (
            f"V187 expected WARN or FAIL on word_document.py (101 fn) but got {result['result']}. "
            "If this file has been healed below 80 functions, update this test."
        )

    def test_v187_passes_on_clean_file(self):
        """V187 should PASS on csv/models.py (0 top-level functions)."""
        from governance_validators_ext5 import validate_function_count_per_file
        decl = self._decl_with_file("src/python/csv/models.py")
        result = validate_function_count_per_file(decl, repo_root=self.REPO_ROOT)
        assert result["result"] == "PASS", (
            f"V187 expected PASS on csv/models.py (0 fn) but got {result['result']}: {result.get('summary')}"
        )

    def test_v188_warns_not_fails_on_baseline_domain_model(self):
        """V188 should WARN (not FAIL) on csv/models.py -- baseline file, so WARN not sprint-blocking FAIL."""
        from governance_validators_ext5 import validate_io_in_domain_model
        decl = self._decl_with_file("src/python/csv/models.py")
        result = validate_io_in_domain_model(decl, repo_root=self.REPO_ROOT)
        # csv/models.py is in the baseline and imports pathlib -> WARN expected (not FAIL)
        # PASS is also acceptable if the pathlib import was removed during healing
        assert result["result"] in ("WARN", "PASS"), (
            f"V188 expected WARN or PASS for baseline domain model but got FAIL: {result.get('violations')}"
        )
        # Must NOT block sprint for baseline files
        assert not result.get("blocks_sprint", False), (
            "V188 must not block sprint for baseline domain model files"
        )

    def test_v192_warns_on_nonexistent_path(self):
        """V192 should WARN when a declared changed_file does not exist on disk."""
        from governance_validators_ext5 import validate_changed_files_exist
        decl = self._decl_with_file("src/python/does_not_exist.py")
        result = validate_changed_files_exist(decl, repo_root=self.REPO_ROOT)
        assert result["result"] == "WARN", (
            f"V192 expected WARN for nonexistent path but got {result['result']}"
        )
        assert "src/python/does_not_exist.py" in str(result.get("violations", []))

    def test_v192_passes_on_real_path(self):
        """V192 should PASS when all declared changed_files exist on disk."""
        from governance_validators_ext5 import validate_changed_files_exist
        decl = self._decl_with_file("src/python/csv/models.py")
        result = validate_changed_files_exist(decl, repo_root=self.REPO_ROOT)
        assert result["result"] == "PASS", (
            f"V192 expected PASS for existing path but got {result['result']}"
        )

    def test_v193_warns_on_past_deadline(self, monkeypatch, tmp_path):
        """V193 should WARN when baseline has a past remediation_deadline with no complete status."""
        import json
        from governance_validators_ext5 import validate_remediation_deadline_expired

        baseline = {
            "known_violations": {
                "src/python/fake/expired_file.py": {
                    "loc": 900,
                    "baseline_loc_cap": 900,
                    "remediation_deadline": "2020-01-01",
                    "remediation_status": "pending",
                    "healing_sprint": "TC-HEAL-SRC-TEST",
                }
            }
        }
        baseline_path = tmp_path / "source-structure-baseline.json"
        baseline_path.write_text(json.dumps(baseline), encoding="utf-8")

        import governance_validators_ext5 as _ext5
        monkeypatch.setattr(_ext5, "_BASELINE_PATH", baseline_path)

        decl = {"changed_files": [], "planned_work_items": [], "work_items": []}
        result = validate_remediation_deadline_expired(decl, repo_root=self.REPO_ROOT)
        assert result["result"] == "WARN", (
            f"V193 expected WARN for past deadline but got {result['result']}"
        )
        assert any("expired_file.py" in v for v in result.get("violations", []))

    def test_v193_passes_when_status_complete(self, monkeypatch, tmp_path):
        """V193 should PASS when remediation_status == 'complete' even if deadline is past."""
        import json
        from governance_validators_ext5 import validate_remediation_deadline_expired

        baseline = {
            "known_violations": {
                "src/python/fake/healed_file.py": {
                    "loc": 400,
                    "baseline_loc_cap": 900,
                    "remediation_deadline": "2020-01-01",
                    "remediation_status": "complete",
                }
            }
        }
        baseline_path = tmp_path / "source-structure-baseline.json"
        baseline_path.write_text(json.dumps(baseline), encoding="utf-8")

        import governance_validators_ext5 as _ext5
        monkeypatch.setattr(_ext5, "_BASELINE_PATH", baseline_path)

        decl = {"changed_files": [], "planned_work_items": [], "work_items": []}
        result = validate_remediation_deadline_expired(decl, repo_root=self.REPO_ROOT)
        assert result["result"] == "PASS", (
            f"V193 expected PASS when status='complete' but got {result['result']}"
        )
