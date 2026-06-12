"""Tests for generate_execution_handoff.py — R100 Train D."""

import json
import sys
from pathlib import Path


sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "tools" / "supervisor"))

from generate_execution_handoff import (
    generate_handoff,
    generate_handoffs_for_gaps,
    write_handoffs,
)


def _gap(track="foss_reduced", fmt="fods", cap="api.save", work_type="product_source_change",
         decision="GOVERNED_HANDOFF_REQUIRED", status="NOT_IMPLEMENTED"):
    return {
        "product_track": track,
        "format": fmt,
        "capability_path": cap,
        "work_type": work_type,
        "decision": decision,
        "current_status": status,
        "gap_id": f"{track}-{fmt}-{cap}",
    }


def test_generate_handoff_basic():
    h = generate_handoff(_gap(), sprint_id="R100")
    assert h["format"] == "fods"
    assert h["sprint_id"] == "R100"
    assert "src/python/fods/" in h["allowed_files"][0]
    assert len(h["safety_gates"]) > 0


def test_handoff_commercial_track():
    h = generate_handoff(_gap(track="commercial_net"), sprint_id="R100")
    assert "src/net/fods/" in h["allowed_files"][0]
    assert "src/python/" in h["forbidden_files"][0]


def test_handoff_foss_track():
    h = generate_handoff(_gap(track="foss_reduced"), sprint_id="R100")
    assert "src/python/fods/" in h["allowed_files"][0]
    assert "src/net/" in h["forbidden_files"][0]


def test_handoff_tests_required_product_source():
    h = generate_handoff(_gap(work_type="product_source_change"))
    assert any("unit tests" in t.lower() for t in h["tests_required"])


def test_handoff_tests_required_package_proof():
    h = generate_handoff(_gap(work_type="package_proof"))
    assert any("pip install" in t.lower() for t in h["tests_required"])


def test_handoff_has_matrix_update():
    h = generate_handoff(_gap())
    assert h["capability_matrix_update"]["file"] == "product-capability-matrix/poc-targets.yaml"


def test_generate_handoffs_filters_decisions():
    gaps = [
        _gap(decision="GOVERNED_HANDOFF_REQUIRED"),
        _gap(decision="GOVERNED_SKILL_REQUIRED", cap="api.load"),
        _gap(decision="NEED_PLAN_HARDENING", cap="api.migrate"),
    ]
    handoffs = generate_handoffs_for_gaps(gaps, "R100")
    assert len(handoffs) == 2  # only HANDOFF and PLAN_HARDENING


def test_write_handoffs(tmp_path):
    gaps = [_gap(), _gap(cap="api.load", decision="GOVERNED_HANDOFF_REQUIRED")]
    gaps_file = tmp_path / "gaps.json"
    gaps_file.write_text(json.dumps({"selected_gaps": gaps}))
    output_dir = tmp_path / "handoffs"
    result = write_handoffs(gaps_file, output_dir, "R100")
    assert result["handoffs_generated"] == 2
    assert len(list(output_dir.glob("*.yaml"))) == 2


def test_handoff_rollback_command():
    h = generate_handoff(_gap())
    assert "git checkout" in h["rollback"]


# --- v2 (R101): new handoff fields ---


def test_handoff_has_implementation_steps():
    h = generate_handoff(_gap(work_type="product_source_change"))
    assert "implementation_steps" in h
    assert len(h["implementation_steps"]) >= 3


def test_handoff_implementation_steps_product():
    h = generate_handoff(_gap(work_type="product_source_change"))
    steps_text = " ".join(h["implementation_steps"]).lower()
    assert "implement" in steps_text
    assert "test" in steps_text


def test_handoff_implementation_steps_test_only():
    h = generate_handoff(_gap(work_type="test_only_change"))
    steps_text = " ".join(h["implementation_steps"]).lower()
    assert "test" in steps_text


def test_handoff_implementation_steps_dogfood():
    h = generate_handoff(_gap(work_type="dogfood_export"))
    steps_text = " ".join(h["implementation_steps"]).lower()
    assert "export" in steps_text


def test_handoff_has_stop_conditions():
    h = generate_handoff(_gap())
    assert "stop_conditions" in h
    assert len(h["stop_conditions"]) >= 2
    assert any("fail" in c.lower() for c in h["stop_conditions"])


def test_handoff_has_evidence_declaration_entries():
    h = generate_handoff(_gap(), sprint_id="R101")
    assert "evidence_declaration_entries" in h
    assert len(h["evidence_declaration_entries"]) >= 1
    entry = h["evidence_declaration_entries"][0]
    assert "item_id" in entry
    assert "R101" in entry["item_id"]


def test_handoff_has_purpose():
    h = generate_handoff(_gap(fmt="fods", cap="api.save"))
    assert "purpose" in h
    assert "fods" in h["purpose"].lower()


def test_handoff_has_source_track():
    h = generate_handoff(_gap(track="commercial_net"))
    assert "source_track" in h
    assert h["source_track"] == "commercial_dotnet"


def test_handoff_source_track_foss():
    h = generate_handoff(_gap(track="foss_reduced"))
    assert h["source_track"] == "foss_python"


def test_handoff_has_raw_logs():
    h = generate_handoff(_gap())
    assert "raw_logs" in h
    assert len(h["raw_logs"]) >= 1


def test_handoff_has_product_code_ledger():
    h = generate_handoff(_gap())
    assert "product_code_ledger" in h
    assert "ledger" in h["product_code_ledger"].lower()


def test_handoff_negative_no_extra_fields():
    """Negative: handoff should not have unexpected top-level keys."""
    h = generate_handoff(_gap())
    expected_keys = {
        "handoff_id", "generated_at", "sprint_id", "purpose", "gap_id",
        "format", "product_track", "source_track", "capability_path",
        "work_type", "decision", "allowed_files", "forbidden_files",
        "implementation_steps", "tests_required", "raw_logs",
        "product_code_ledger", "rollback", "evidence_outputs",
        "evidence_declaration_entries", "ledger_requirements",
        "capability_matrix_update", "stop_conditions", "safety_gates",
    }
    assert set(h.keys()) == expected_keys
