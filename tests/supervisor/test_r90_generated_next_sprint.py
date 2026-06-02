"""R90 supervisor generator acceleration integration regressions."""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from generate_next_worker_prompt import generate_prompt
from generate_supervisor_packet import (
    generate_next_sprint_md,
    generate_ruflo_lanes_json,
    generate_taskmaster_json,
    synthesize_sprint_tasks,
    validate_against_schema,
)


def _review() -> dict:
    return {
        "sprint_id": "FORMAT-FACTORY-R89-TEST",
        "verdict": "ACCEPTED",
        "overall_verdict": "ACCEPTED",
        "autonomous_continue": True,
        "facts": {"test_count": 10, "fail_count": 0, "skip_count": 0},
        "item_grades": [],
    }


def _tasks() -> list[dict]:
    return synthesize_sprint_tasks(
        _review(),
        {"critical_count": 0, "contradictions": [], "autonomous_continue": True},
        REPO_ROOT,
    )


def test_mega_train_prompt_requires_governed_acceleration_inputs():
    prompt = generate_prompt(_review(), repo_root=REPO_ROOT)
    assert ".local/supervisor/selected-product-gaps.json" in prompt
    assert ".supervisor/skill-registry.yaml" in prompt
    assert "No direct ad-hoc `src/` edits" in prompt
    assert "reports/r90/product-code-change-ledger.json" in prompt
    assert "autonomous-cycle" in prompt


def test_packet_prompt_requires_dogfood_package_declaration_and_cycle():
    prompt = generate_next_sprint_md(
        _review(),
        {"critical_count": 0, "contradictions": [], "autonomous_continue": True},
        "(memory)",
        _tasks(),
    )
    assert ".local/supervisor/selected-product-gaps.json" in prompt
    assert ".supervisor/skill-registry.yaml" in prompt
    assert "No direct ad-hoc `src/` edits" in prompt
    assert "product-code-change-ledger.json" in prompt
    assert "Dogfood export" in prompt
    assert "Package/install proof" in prompt
    assert "evidence-declaration.yaml" in prompt
    assert "autonomous-cycle" in prompt


def test_taskmaster_product_tasks_name_product_target_and_validate_schema():
    tasks = _tasks()
    product_tasks = [task for task in tasks if "Product target:" in task.get("description", "")]
    assert product_tasks
    assert all("Product target:" in task["description"] for task in product_tasks)

    data = generate_taskmaster_json(_review(), {}, tasks)
    errors = validate_against_schema(
        data, REPO_ROOT / ".supervisor" / "schemas" / "next-sprint-taskmaster.schema.json"
    )
    assert errors == []


def test_taskmaster_critical_repair_tasks_validate_schema():
    contradictions = {
        "critical_count": 1,
        "contradictions": [
            {
                "severity": "CRITICAL",
                "description": "Tests failed: 12 failures detected",
                "detail": "Repair inherited evidence defects.",
            }
        ],
        "autonomous_continue": False,
    }
    tasks = synthesize_sprint_tasks(_review(), contradictions, REPO_ROOT)
    data = generate_taskmaster_json(_review(), contradictions, tasks)
    errors = validate_against_schema(
        data, REPO_ROOT / ".supervisor" / "schemas" / "next-sprint-taskmaster.schema.json"
    )
    assert errors == []


def test_ruflo_product_lanes_name_objective_and_validate_schema():
    data = generate_ruflo_lanes_json(_review(), {}, _tasks())
    product_lanes = [lane for lane in data["lanes"] if lane["lane_id"] in {"C3", "C4", "C5"}]
    assert product_lanes
    assert all("Product objective:" in lane["description"] for lane in product_lanes)

    errors = validate_against_schema(
        data, REPO_ROOT / ".supervisor" / "schemas" / "next-ruflo-lanes.schema.json"
    )
    assert errors == []


def test_templates_preserve_acceleration_requirements():
    for relative in (
        ".supervisor/prompts/next-sprint-generator.md",
        ".supervisor/prompts/mega-train-template.md",
    ):
        text = (REPO_ROOT / relative).read_text(encoding="utf-8")
        assert "selected-product-gaps.json" in text
        assert "skill-registry.yaml" in text
        assert "ad-hoc" in text
        assert "product-code-change-ledger.json" in text
        assert "dogfood" in text.lower()
        assert "package" in text.lower()
        assert "evidence-declaration.yaml" in text
        assert "autonomous-cycle" in text
