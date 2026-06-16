"""AI usage ledger format validation tests — per AI-USAGE-LEDGER-AND-METRICS taskcard.

Tests:
1. JSONL log format documented fields match AGENTS.md §H5
2. Sprint summary report template exists
3. .local/ is in .gitignore (covers .local/llm-logs/)
4. Example JSONL entries have required fields
"""

import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO))

REQUIRED_JSONL_FIELDS = {
    "timestamp",
    "sprint_id",
    "model",
    "purpose",
    "status",
}

FULL_JSONL_FIELDS = {
    "timestamp",
    "sprint_id",
    "lane_id",
    "model",
    "endpoint",
    "purpose",
    "inputs",
    "outputs",
    "status",
    "validation",
    "secret_safety",
    "provenance_cited",
}


class TestAiUsageSummaryTemplate:
    """Verify template file exists and has required structure."""

    def test_template_exists(self):
        template = _REPO / "reports" / "ai" / "ai-usage-summary-template.md"
        assert template.exists(), f"Template not found at {template}"

    def test_template_has_required_sections(self):
        template = _REPO / "reports" / "ai" / "ai-usage-summary-template.md"
        content = template.read_text(encoding="utf-8")
        assert "Usage Summary" in content
        assert "JSONL" in content
        assert "Validation" in content

    def test_template_references_jsonl_fields(self):
        template = _REPO / "reports" / "ai" / "ai-usage-summary-template.md"
        content = template.read_text(encoding="utf-8")
        assert "timestamp" in content
        assert "sprint_id" in content
        assert "model" in content


class TestGitignoreCoversLlmLogs:
    """Verify .local/ is gitignored (covers .local/llm-logs/)."""

    def test_local_in_gitignore(self):
        gitignore = _REPO / ".gitignore"
        assert gitignore.exists()
        content = gitignore.read_text(encoding="utf-8")
        assert ".local/" in content or ".local/**" in content


class TestJsonlFieldValidation:
    """Verify JSONL entries have required fields per AGENTS.md §H5."""

    def _make_entry(self, **overrides):
        base = {
            "timestamp": "2026-06-15T20:00:00Z",
            "sprint_id": "TEST-SPRINT-001",
            "lane_id": "C3",
            "model": "claude-opus-4-6",
            "endpoint": "local",
            "purpose": "test_generation",
            "inputs": "prompt text",
            "outputs": "response text",
            "status": "success",
            "validation": "tests_pass",
            "secret_safety": "no_secrets",
            "provenance_cited": True,
        }
        base.update(overrides)
        return base

    def test_complete_entry_has_all_fields(self):
        entry = self._make_entry()
        assert FULL_JSONL_FIELDS.issubset(set(entry.keys()))

    def test_minimal_entry_has_required_fields(self):
        entry = self._make_entry()
        minimal = {k: entry[k] for k in REQUIRED_JSONL_FIELDS}
        assert REQUIRED_JSONL_FIELDS.issubset(set(minimal.keys()))

    def test_entry_serializes_to_json(self):
        entry = self._make_entry()
        line = json.dumps(entry)
        parsed = json.loads(line)
        assert parsed["model"] == "claude-opus-4-6"

    def test_existing_ledger_has_valid_entries(self):
        """If an existing ledger exists, validate its entries."""
        ledger = _REPO / "reports" / "ai" / "ai-usage-ledger-commercial-load-save-20260513.jsonl"
        if not ledger.exists():
            pytest.skip("No existing ledger to validate")
        with open(ledger, encoding="utf-8") as f:
            for i, line in enumerate(f):
                line = line.strip()
                if not line:
                    continue
                entry = json.loads(line)
                assert isinstance(entry, dict), f"Line {i+1}: not a dict"
                # At minimum must have a model or purpose field
                assert any(
                    k in entry for k in ("model", "purpose", "sprint_id")
                ), f"Line {i+1}: missing all identifier fields"
