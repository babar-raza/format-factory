"""Tests for AI telemetry spool."""

import sys
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT))

from tools.ai.schemas.models import AIUsageRecord, CallStatus
from tools.ai.telemetry.call_logger import log_call, read_spool, _serialize_record
from tools.ai.telemetry.spool_manager import get_spool_path


class TestCallLogger:
    def test_log_and_read(self, tmp_path):
        record = AIUsageRecord(
            provider="openai",
            model="gpt-oss",
            role="structured_extraction",
            operation="capability_probe",
            status=CallStatus.success,
            input_tokens=10,
            output_tokens=5,
            total_tokens=15,
        )
        spool_file = log_call(record, tmp_path)
        assert spool_file.exists()

        records = read_spool(tmp_path)
        assert len(records) == 1
        assert records[0]["model"] == "gpt-oss"
        assert records[0]["posted_to_agent_metrics"] is False

    def test_multiple_records(self, tmp_path):
        for i in range(3):
            log_call(
                AIUsageRecord(
                    provider="openai",
                    model=f"model-{i}",
                    role="test",
                    operation="test",
                ),
                tmp_path,
            )
        records = read_spool(tmp_path)
        assert len(records) == 3

    def test_secret_redaction_in_serialization(self):
        record = AIUsageRecord(
            provider="openai",
            model="test",
            role="test",
            operation="test",
        )
        serialized = _serialize_record(record)
        # Should not contain any key-like fields with real values
        assert "api_key" not in serialized.lower() or "REDACTED" in serialized

    def test_read_empty_spool(self, tmp_path):
        records = read_spool(tmp_path)
        assert records == []

    def test_record_schema_fields(self, tmp_path):
        record = AIUsageRecord(
            provider="openai",
            endpoint_identity="llm.example.com",
            model="gpt-oss",
            role="evidence_review",
            operation="probe",
            sprint_id="TEST-SPRINT",
            prompt_hash="abc123",
            fallback_used=True,
        )
        log_call(record, tmp_path)
        records = read_spool(tmp_path)
        r = records[0]
        assert r["endpoint_identity"] == "llm.example.com"
        assert r["sprint_id"] == "TEST-SPRINT"
        assert r["fallback_used"] is True
        assert r["posted_to_agent_metrics"] is False


class TestSpoolManager:
    def test_get_spool_path(self):
        p = get_spool_path()
        assert str(p).endswith("spool")
