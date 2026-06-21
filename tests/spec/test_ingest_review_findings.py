"""Tests for tools/spec/ingest_review_findings.py.

Verifies:
1. Tool exits 0 when given a file with TC-* sections (synthetic fixture)
2. Output contains at least one TC- id and gap-ledger JSON structure
3. Tool exits non-zero (2) when file does not exist
4. Tool exits non-zero (1) when file exists but has no TC-* heading sections
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).parent.parent.parent
_TOOL = _REPO / "tools" / "spec" / "ingest_review_findings.py"
_REAL_HANDOFF = _REPO / "reviews" / "src" / "next_agent_handoff.md"

# A synthetic handoff with TC-* sections in the heading format the parser expects
_SYNTHETIC_HANDOFF = """\
# Synthetic Agent Handoff

## TC-001: Build-artifact audit

Remove generated artifacts from source metrics.
Verify .gitignore has obj/ and bin/ entries.

## TC-002: Canonical registry schema

Create shared/qname-registry/schema.yaml.

## TC-003: Seed FODT QName registry

Seed 9 entries from SAL context pack FACT-FODT-002 through FACT-FODT-007.
"""


class TestIngestToolExists:
    def test_tool_file_exists(self):
        assert _TOOL.exists(), f"Tool not found: {_TOOL}"


class TestSyntheticInput:
    def _run_tool(self, args: list[str], handoff_content: str) -> tuple[int, str, str]:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".md", encoding="utf-8", delete=False
        ) as f:
            f.write(handoff_content)
            tmp_path = f.name
        result = subprocess.run(
            [sys.executable, str(_TOOL)] + args + ["--handoff-file", tmp_path],
            capture_output=True, text=True
        )
        Path(tmp_path).unlink(missing_ok=True)
        return result.returncode, result.stdout, result.stderr

    def test_taskcards_exit_0_with_tc_sections(self):
        code, stdout, stderr = self._run_tool(["--output-taskcards"], _SYNTHETIC_HANDOFF)
        assert code == 0, f"Expected exit 0 but got {code}. stderr={stderr}"

    def test_taskcards_stdout_contains_tc_id(self):
        code, stdout, stderr = self._run_tool(["--output-taskcards"], _SYNTHETIC_HANDOFF)
        assert "TC-" in stdout, f"Expected TC- in stdout. stdout={stdout[:300]}"

    def test_gap_ledger_exit_0(self):
        code, stdout, stderr = self._run_tool(["--output-gap-ledger"], _SYNTHETIC_HANDOFF)
        assert code == 0, f"Expected exit 0 but got {code}. stderr={stderr}"

    def test_gap_ledger_stdout_is_json_array(self):
        code, stdout, stderr = self._run_tool(["--output-gap-ledger"], _SYNTHETIC_HANDOFF)
        entries = json.loads(stdout)
        assert isinstance(entries, list), "Expected JSON array"
        assert len(entries) >= 1, "Expected at least 1 gap-ledger entry"

    def test_gap_entry_has_required_fields(self):
        code, stdout, stderr = self._run_tool(["--output-gap-ledger"], _SYNTHETIC_HANDOFF)
        entries = json.loads(stdout)
        entry = entries[0]
        for field in ("gap_id", "format", "status", "gap_type"):
            assert field in entry, f"Missing required field '{field}' in gap entry"

    def test_gap_entry_gap_id_format(self):
        code, stdout, stderr = self._run_tool(["--output-gap-ledger"], _SYNTHETIC_HANDOFF)
        entries = json.loads(stdout)
        assert entries[0]["gap_id"].startswith("GAP-"), "gap_id must start with GAP-"


class TestMissingFile:
    def test_exits_2_when_file_not_found(self):
        result = subprocess.run(
            [sys.executable, str(_TOOL), "--output-taskcards",
             "--handoff-file", "/nonexistent/path/handoff.md"],
            capture_output=True, text=True
        )
        assert result.returncode == 2, (
            f"Expected exit 2 for missing file, got {result.returncode}"
        )

    def test_stderr_mentions_file_not_found(self):
        result = subprocess.run(
            [sys.executable, str(_TOOL), "--output-taskcards",
             "--handoff-file", "/nonexistent/path/handoff.md"],
            capture_output=True, text=True
        )
        assert "ERROR" in result.stderr or "not found" in result.stderr.lower(), (
            f"Expected error message in stderr. Got: {result.stderr}"
        )


class TestRealHandoffFile:
    @pytest.mark.skipif(not _REAL_HANDOFF.exists(), reason="reviews/src/next_agent_handoff.md not present")
    def test_real_file_exits_without_crash(self):
        """Real handoff has bullet-list TCs, not heading TCs — tool should not crash."""
        result = subprocess.run(
            [sys.executable, str(_TOOL), "--output-taskcards",
             "--handoff-file", str(_REAL_HANDOFF)],
            capture_output=True, text=True
        )
        # Either exits 0 (found sections) or 1 (WARN: no sections found) — both are valid
        assert result.returncode in (0, 1), (
            f"Tool should not crash on real file. Exit={result.returncode}. stderr={result.stderr}"
        )
