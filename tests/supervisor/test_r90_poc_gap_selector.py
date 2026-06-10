"""Focused tests for the R90 POC gap selector and decision tree."""

import json
import subprocess
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
SUPERVISOR_DIR = REPO_ROOT / "tools" / "supervisor"
sys.path.insert(0, str(SUPERVISOR_DIR))

from choose_skill_or_handoff import choose_skill_or_handoff
from select_poc_gaps import select_gaps


def test_decision_tree_routes_repeatable_dogfood_work_to_governed_skill():
    decision = choose_skill_or_handoff(
        {
            "capability_path": "dogfood_status.pbm_to_ppm_python",
            "current_status": "NOT_YET",
            "description": "Implement dogfood export.",
        }
    )

    assert decision["decision"] == "GOVERNED_SKILL_REQUIRED"
    assert decision["governed_skill"] == "governed-dogfood-export"
    assert decision["handoff_required"] is False


def test_decision_tree_never_routes_gate_approval_to_autonomous_skill():
    decision = choose_skill_or_handoff(
        {
            "capability_path": "blockers.1",
            "current_status": "BLOCKED",
            "description": "Gate 11 G11-G: requires Babar Raza written approval",
        }
    )

    assert decision["decision"] == "EXTERNAL_GATE_ESCALATION"
    assert decision["external_gate"] is True
    assert decision["handoff_required"] is True


def test_selector_prioritizes_poc_implementation_before_external_gate():
    matrix = {
        "commercial_net_products": [
            {
                "format": "Example",
                "dogfood_status": {"export": "GAP_DOGFOOD_EXTERNAL"},
                "blockers": ["Gate 11 G11-G: requires Babar Raza written approval"],
            }
        ],
        "foss_reduced_products": [],
    }

    gaps = select_gaps(matrix)

    assert [gap["capability_path"] for gap in gaps] == [
        "dogfood_status.export",
        "blockers.1",
    ]
    assert gaps[0]["priority_score"] > gaps[1]["priority_score"]


def test_selector_extracts_current_matrix_product_gaps():
    matrix = yaml.safe_load(
        (REPO_ROOT / "product-capability-matrix" / "poc-targets.yaml").read_text(
            encoding="utf-8"
        )
    )

    gaps = select_gaps(matrix)
    indexed = {
        (gap["product_track"], gap["format"], gap["capability_path"]): gap
        for gap in gaps
    }

    # Fully implemented — no longer gaps
    assert (
        "foss_reduced",
        "Netpbm",
        "python_status.write_ppm",
    ) not in indexed
    assert (
        "foss_reduced",
        "Netpbm",
        "dogfood_status.ppm_to_pgm",
    ) not in indexed
    assert (
        "commercial_net",
        "FODS",
        "dogfood_status.fods_to_csv_dotnet",
    ) not in indexed

    # All known formats are fully implemented — matrix has no remaining gaps
    assert len(gaps) == 0


def test_selector_cli_writes_json_and_markdown(tmp_path):
    matrix_path = tmp_path / "matrix.yaml"
    json_path = tmp_path / "selected.json"
    report_path = tmp_path / "selected.md"
    matrix_path.write_text(
        yaml.safe_dump(
            {
                "poc_matrix_version": "test",
                "sprint": "R90-test",
                "commercial_net_products": [],
                "foss_reduced_products": [
                    {
                        "format": "Example",
                        "python_status": {"write_example": "NOT_IMPLEMENTED"},
                    }
                ],
            }
        ),
        encoding="utf-8",
    )

    result = subprocess.run(
        [
            sys.executable,
            str(SUPERVISOR_DIR / "select_poc_gaps.py"),
            "--matrix",
            str(matrix_path),
            "--json-output",
            str(json_path),
            "--report-output",
            str(report_path),
        ],
        check=True,
        capture_output=True,
        text=True,
    )

    payload = json.loads(json_path.read_text(encoding="utf-8"))
    assert "SELECTED_PRODUCT_GAPS: 1" in result.stdout
    assert payload["selected_gap_count"] == 1
    assert payload["selected_gaps"][0]["decision"] == "GOVERNED_HANDOFF_REQUIRED"
    assert "# Product Gap Selection" in report_path.read_text(encoding="utf-8")
