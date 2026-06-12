"""Lane G tests — telemetry drain and Agent Metrics integration.

Tests for drain payload validation, secret detection, dry-run mode,
and field mapping.
"""

import json

from tools.ai.telemetry.drain import (
    drain_spool,
    map_spool_to_agent_metrics,
    validate_drain_payload,
)


class TestPayloadMapping:
    def test_valid_mapping(self):
        record = {
            "timestamp": "2026-05-19T10:00:00Z",
            "sprint_id": "R27",
            "run_id": "run001",
            "status": "success",
            "input_tokens": 100,
            "output_tokens": 50,
            "total_tokens": 150,
            "api_calls_count": 1,
            "model": "gpt-oss",
            "endpoint_identity": "llm.professionalize.com",
            "taskcard_id": "AI-001",
        }
        payload = map_spool_to_agent_metrics(record)
        assert payload["agent_name"] == "format-factory-ai"
        assert payload["product"] == "format-factory"
        assert payload["token_usage"]["input"] == 100
        assert payload["token_usage"]["total"] == 150

    def test_missing_fields_get_defaults(self):
        record = {}
        payload = map_spool_to_agent_metrics(record)
        assert payload["model"] == ""
        assert payload["api_calls_count"] == 1


class TestPayloadValidation:
    def test_valid_payload(self):
        record = {"timestamp": "2026-05-19T10:00:00Z", "status": "success", "api_calls_count": 1}
        payload = map_spool_to_agent_metrics(record)
        errors = validate_drain_payload(payload)
        assert errors == []

    def test_secret_in_payload(self):
        record = {"timestamp": "t", "status": "s", "api_calls_count": 1}
        payload = map_spool_to_agent_metrics(record)
        payload["model"] = "sk-1234567890abcdef"
        errors = validate_drain_payload(payload)
        assert any("secret" in e for e in errors)

    def test_bearer_token_detected(self):
        record = {"timestamp": "t", "status": "s", "api_calls_count": 1}
        payload = map_spool_to_agent_metrics(record)
        payload["endpoint_identity"] = "Bearer abcdefghijk"
        errors = validate_drain_payload(payload)
        assert any("secret" in e for e in errors)


class TestDrySpool:
    def test_dry_run_empty_spool(self, tmp_path):
        spool_path = tmp_path / "spool"
        spool_path.mkdir()
        result = drain_spool(spool_path, dry_run=True)
        assert result["total"] == 0
        assert result["dry_run"] is True

    def test_dry_run_with_records(self, tmp_path):
        spool_path = tmp_path / "spool"
        spool_path.mkdir()
        spool_file = spool_path / "ai-telemetry.jsonl"
        record = {
            "timestamp": "2026-05-19T10:00:00Z",
            "sprint_id": "R27",
            "status": "success",
            "api_calls_count": 1,
            "provider": "openai",
            "model": "gpt-oss",
        }
        spool_file.write_text(json.dumps(record) + "\n")
        result = drain_spool(spool_path, dry_run=True)
        assert result["total"] == 1
        assert result["valid"] >= 0
        assert result["posted"] == 0
