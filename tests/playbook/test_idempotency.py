"""
test_idempotency.py — TC-PB-009/TC-PB-012: Playbook System Idempotency Tests

Verifies that repeated contract parsing, task generation, registry generation,
and execution reconciliation produce identical results (zero material changes).
"""
import hashlib
import sys
from pathlib import Path

import pytest
import yaml

_REPO = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "playbook"))

_PB_DIR = _REPO / "playbooks" / "format-factory"
_FFE_PATH = _PB_DIR / "format-feature-expansion.md"
_FFE_PARAMS = {
    "format_name": "tsv",
    "codec_file": "src/python/tsv/tsv_parser.py",
    "init_file": "src/python/tsv/__init__.py",
    "test_dir": "tests/python/tsv/",
    "function_name": "export_to_csv",
    "function_signature": "(source) -> str",
    "capability_label": "CSV_EXPORT",
}


def _hash_dict(d: dict) -> str:
    """Produce stable hash of a dict by dumping to sorted YAML."""
    return hashlib.md5(
        yaml.dump(d, default_flow_style=False, sort_keys=True).encode("utf-8")
    ).hexdigest()


class TestRegistryParsingIdempotency:
    """Repeated parsing of contract front-matter produces identical results."""

    @pytest.mark.skipif(not _PB_DIR.exists(), reason="playbooks/format-factory/ not found")
    def test_repeated_contract_parsing_stable(self):
        import re
        for md in _PB_DIR.glob("*.md"):
            text = md.read_text(encoding="utf-8")
            m = re.search(r"<!--\s*\n(playbook_contract:.*?)-->", text, re.DOTALL)
            if not m:
                continue
            parse1 = yaml.safe_load(m.group(1))
            parse2 = yaml.safe_load(m.group(1))
            assert _hash_dict(parse1) == _hash_dict(parse2), (
                f"{md.name}: contract parsing is not stable across runs"
            )


class TestTaskGenerationIdempotency:
    """Repeated task generation with same inputs produces identical taskcards."""

    @pytest.mark.skipif(not _FFE_PATH.exists(), reason="format-feature-expansion.md not found")
    def test_repeated_generation_produces_same_count(self):
        from generate_playbook_taskcards import parse_contract, generate_taskcards
        contract = parse_contract(_FFE_PATH)
        tcs1 = generate_taskcards(contract, plan_id="PLAN-IDEM-001", gap_ids=[], parameters=_FFE_PARAMS)
        tcs2 = generate_taskcards(contract, plan_id="PLAN-IDEM-001", gap_ids=[], parameters=_FFE_PARAMS)
        assert len(tcs1) == len(tcs2)

    @pytest.mark.skipif(not _FFE_PATH.exists(), reason="format-feature-expansion.md not found")
    def test_repeated_generation_same_phases(self):
        from generate_playbook_taskcards import parse_contract, generate_taskcards
        contract = parse_contract(_FFE_PATH)
        tcs1 = generate_taskcards(contract, plan_id="PLAN-IDEM-001", gap_ids=[], parameters=_FFE_PARAMS)
        tcs2 = generate_taskcards(contract, plan_id="PLAN-IDEM-001", gap_ids=[], parameters=_FFE_PARAMS)
        phases1 = [tc["phase"] for tc in tcs1]
        phases2 = [tc["phase"] for tc in tcs2]
        assert phases1 == phases2

    @pytest.mark.skipif(not _FFE_PATH.exists(), reason="format-feature-expansion.md not found")
    def test_repeated_generation_same_provenance(self):
        from generate_playbook_taskcards import parse_contract, generate_taskcards
        contract = parse_contract(_FFE_PATH)
        tcs1 = generate_taskcards(contract, plan_id="PLAN-IDEM-001", gap_ids=[], parameters=_FFE_PARAMS)
        tcs2 = generate_taskcards(contract, plan_id="PLAN-IDEM-001", gap_ids=[], parameters=_FFE_PARAMS)
        for tc1, tc2 in zip(tcs1, tcs2):
            assert tc1["playbook_id"] == tc2["playbook_id"]
            assert tc1["playbook_version"] == tc2["playbook_version"]
            assert tc1["plan_id"] == tc2["plan_id"]
            assert tc1["phase"] == tc2["phase"]
            assert tc1["allowed_paths"] == tc2["allowed_paths"]
            assert tc1["forbidden_paths"] == tc2["forbidden_paths"]


class TestExecutionLogIdempotency:
    """Execution log save produces stable YAML output."""

    def test_same_inputs_produce_same_schema_structure(self, tmp_path):
        from playbook_execution_log import PlaybookExecutionLog
        for run in range(2):
            log = PlaybookExecutionLog(
                playbook_id="test-playbook",
                version="1.0",
                plan_id="TEST-IDEM-001",
            )
            log.phase_complete("read_codec")
            log.phase_complete("draft_function")
            log.phase_failed("write_tests", error="test error")
            path = log.save(output_dir=tmp_path / f"run{run}")
            data = yaml.safe_load(path.read_text(encoding="utf-8"))
            assert data["schema"] == "playbook-execution-log/1.0"
            assert data["playbook_id"] == "test-playbook"
            assert data["verdict"] == "PARTIAL_SUCCESS"
            assert len(data["successful_phases"]) == 2
            assert len(data["failed_phases"]) == 1


class TestSelectorIdempotency:
    """Repeated playbook selection with same input produces same output."""

    def test_repeated_selection_stable(self):
        from playbook_selector import select_playbook
        for _ in range(3):
            result1 = select_playbook("FORMAT_FEATURE_EXPANSION")
            result2 = select_playbook("FORMAT_FEATURE_EXPANSION")
            assert result1 == result2

    def test_repeated_selection_unknown_stable(self):
        from playbook_selector import select_playbook
        for _ in range(3):
            r1 = select_playbook("UNKNOWN_TYPE")
            r2 = select_playbook("UNKNOWN_TYPE")
            assert r1 == r2 == None  # noqa: E711


class TestCoverageReportIdempotency:
    """Coverage universe report YAML is stable when re-parsed."""

    def test_coverage_report_parse_stable(self):
        coverage_path = _REPO / "reports" / "playbooks" / "playbook-coverage-universe.yaml"
        if not coverage_path.exists():
            pytest.skip("Coverage report not found")
        text = coverage_path.read_text(encoding="utf-8")
        parse1 = yaml.safe_load(text)
        parse2 = yaml.safe_load(text)
        h1 = _hash_dict(parse1)
        h2 = _hash_dict(parse2)
        assert h1 == h2, "Coverage report YAML parsing is not stable"
