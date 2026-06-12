"""Tests for Phase 2 telemetry and Agent Metrics mapping — Lane C."""

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.ai.schemas.models import AIUsageRecord
from tools.ai.telemetry.call_logger import log_call, read_spool
from tools.ai.telemetry.spool_manager import (
    AGENT_METRICS_MAPPING,
    AI_LOCAL_ONLY_FIELDS,
    validate_spool_record,
    validate_spool_for_replay,
)


class TestAgentMetricsMapping:
    def test_mapping_covers_core_fields(self):
        assert "timestamp" in AGENT_METRICS_MAPPING
        assert "run_id" in AGENT_METRICS_MAPPING
        assert "status" in AGENT_METRICS_MAPPING
        assert "api_calls_count" in AGENT_METRICS_MAPPING

    def test_ai_local_fields_preserved(self):
        assert "model" in AI_LOCAL_ONLY_FIELDS
        assert "role" in AI_LOCAL_ONLY_FIELDS
        assert "provider" in AI_LOCAL_ONLY_FIELDS
        assert "prompt_hash" in AI_LOCAL_ONLY_FIELDS
        assert "model_fingerprint" in AI_LOCAL_ONLY_FIELDS
        assert "fallback_used" in AI_LOCAL_ONLY_FIELDS

    def test_record_contains_all_mapped_fields(self):
        record = AIUsageRecord(
            provider="openai",
            model="gpt-oss",
            role="structured_extraction",
            operation="test",
            sprint_id="R26",
            run_id="run-001",
        )
        data = record.model_dump(mode="json")
        for field in AGENT_METRICS_MAPPING:
            assert field in data, f"Missing mapped field: {field}"

    def test_record_contains_all_local_fields(self):
        record = AIUsageRecord(
            provider="openai",
            model="gpt-oss",
            role="test",
            operation="test",
        )
        data = record.model_dump(mode="json")
        for field in AI_LOCAL_ONLY_FIELDS:
            assert field in data, f"Missing local field: {field}"


class TestSpoolRecordValidation:
    def test_valid_record(self):
        record = {
            "timestamp": "2026-05-19T12:00:00Z",
            "sprint_id": "R26",
            "run_id": "run-001",
            "provider": "openai",
            "model": "gpt-oss",
            "status": "success",
        }
        errors = validate_spool_record(record)
        assert errors == []

    def test_missing_timestamp(self):
        record = {"sprint_id": "R26", "model": "gpt-oss"}
        errors = validate_spool_record(record)
        assert "missing_timestamp" in errors

    def test_missing_run_context(self):
        record = {"timestamp": "2026-05-19T12:00:00Z"}
        errors = validate_spool_record(record)
        assert "missing_run_context" in errors

    def test_secret_leak_detection(self):
        record = {
            "timestamp": "2026-05-19T12:00:00Z",
            "sprint_id": "R26",
            "model": "sk-abcdef1234567890",
        }
        errors = validate_spool_record(record)
        assert any("secret_leak" in e for e in errors)

    def test_bearer_leak_detection(self):
        record = {
            "timestamp": "2026-05-19T12:00:00Z",
            "sprint_id": "R26",
            "evidence_path": "Bearer eyJhbGci",
        }
        errors = validate_spool_record(record)
        assert any("secret_leak" in e for e in errors)

    def test_taskcard_satisfies_context(self):
        record = {
            "timestamp": "2026-05-19T12:00:00Z",
            "taskcard_id": "TC-001",
        }
        errors = validate_spool_record(record)
        assert "missing_run_context" not in errors

    def test_gate_id_satisfies_context(self):
        record = {
            "timestamp": "2026-05-19T12:00:00Z",
            "gate_id": "G8",
        }
        errors = validate_spool_record(record)
        assert "missing_run_context" not in errors


class TestSpoolReplayValidation:
    def test_validate_empty_spool(self, tmp_path):
        result = validate_spool_for_replay(tmp_path)
        assert result["total"] == 0
        assert result["valid"] == 0
        assert result["posted_externally"] is False
        assert result["blocked_by_policy"] is True

    def test_validate_spool_with_records(self, tmp_path):
        record = AIUsageRecord(
            provider="openai",
            model="gpt-oss",
            role="test",
            operation="test",
            sprint_id="R26",
        )
        log_call(record, tmp_path)
        result = validate_spool_for_replay(tmp_path)
        assert result["total"] == 1
        assert result["valid"] == 1
        assert result["invalid"] == 0
        assert result["posted_externally"] is False

    def test_posted_to_agent_metrics_always_false(self, tmp_path):
        record = AIUsageRecord(
            provider="openai",
            model="gpt-oss",
            role="test",
            operation="test",
            sprint_id="R26",
        )
        log_call(record, tmp_path)
        records = read_spool(tmp_path)
        assert records[0]["posted_to_agent_metrics"] is False
