"""V47 quality threshold regression tests.

Tests that V47 (validate_spec_fact_refs_in_sal_output) enforces quality
thresholds per item_type:
  - PRODUCT_SOURCE: Level 0 OK (bootstrap_only accepted)
  - READINESS: Level 1+ required
  - RELEASE_GATE: Level 2+ required
"""

import json
import sys
import tempfile
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))
sys.path.insert(0, str(_REPO / "tools" / "specification-authority-layer"))

from governance_validators import validate_spec_fact_refs_in_sal_output


def _make_sal_facts(facts_by_format: dict) -> str:
    """Build a minimal sal-facts-latest.json string."""
    results = []
    for fmt, facts in facts_by_format.items():
        results.append({"format_id": fmt, "spec_facts": facts})
    return json.dumps({
        "generated_at": "2026-06-23T00:00:00Z",
        "generator": "test",
        "formats_processed": len(results),
        "spec_facts_total": sum(len(r["spec_facts"]) for r in results),
        "results": results,
    })


def _make_sources_jsonl(source_ids: list) -> str:
    """Build a minimal sources.jsonl."""
    lines = []
    for sid in source_ids:
        lines.append(json.dumps({
            "format_id": sid.split("-")[1].lower() if "-" in sid else "unknown",
            "source_id": sid,
            "status": "registered",
        }))
    return "\n".join(lines)


@pytest.fixture
def sal_env(tmp_path):
    """Create a temporary repo-like structure with SAL output and source registry."""
    sal_dir = tmp_path / ".local" / "sal-output"
    sal_dir.mkdir(parents=True)
    reg_dir = tmp_path / ".local" / "spec-source-registry"
    reg_dir.mkdir(parents=True)

    # Register one source
    (reg_dir / "sources.jsonl").write_text(
        _make_sources_jsonl(["SPEC-FODS-1_3"]),
        encoding="utf-8",
    )

    # Create sal-facts-latest.json with three quality levels
    facts = {
        "fods": [
            {
                "qname": "BOOTSTRAP-FACT-001",
                "fact_status": "bootstrap_only",
                "source_id": None,
                "description": "Bootstrap fact with null source_id",
            },
            {
                "qname": "REGISTERED-FACT-001",
                "fact_status": "bootstrap_only",
                "source_id": "SPEC-FODS-1_3",
                "description": "Bootstrap fact with registered source_id",
            },
            {
                "qname": "VERIFIED-FACT-001",
                "fact_status": "verified",
                "source_id": "SPEC-FODS-1_3",
                "description": "Text-verified fact",
            },
        ],
    }
    (sal_dir / "sal-facts-latest.json").write_text(
        _make_sal_facts(facts), encoding="utf-8"
    )

    return tmp_path


class TestQualityThresholdEnforcement:
    """V47 enforces quality thresholds per item_type."""

    def test_product_source_accepts_bootstrap_level_0(self, sal_env):
        """PRODUCT_SOURCE items can cite bootstrap-only facts (Level 0 threshold)."""
        decl = {
            "planned_work_items": [{
                "item_id": "WI-QT-001",
                "item_type": "PRODUCT_SOURCE",
                "spec_fact_refs": ["BOOTSTRAP-FACT-001"],
            }],
        }
        result = validate_spec_fact_refs_in_sal_output(decl, repo_root=sal_env)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_readiness_rejects_bootstrap_level_0(self, sal_env):
        """READINESS items must not cite bootstrap-only facts (Level 0 < Level 1 threshold)."""
        decl = {
            "planned_work_items": [{
                "item_id": "WI-QT-002",
                "item_type": "READINESS",
                "spec_fact_refs": ["BOOTSTRAP-FACT-001"],
            }],
        }
        result = validate_spec_fact_refs_in_sal_output(decl, repo_root=sal_env)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True
        assert any("quality=0" in str(v) for v in result["items"])

    def test_readiness_accepts_registered_level_1(self, sal_env):
        """READINESS items can cite facts with registered source_id (Level 1)."""
        decl = {
            "planned_work_items": [{
                "item_id": "WI-QT-003",
                "item_type": "READINESS",
                "spec_fact_refs": ["REGISTERED-FACT-001"],
            }],
        }
        result = validate_spec_fact_refs_in_sal_output(decl, repo_root=sal_env)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_release_gate_rejects_registered_level_1(self, sal_env):
        """RELEASE_GATE items must not cite Level 1 facts (Level 1 < Level 2 threshold)."""
        decl = {
            "planned_work_items": [{
                "item_id": "WI-QT-004",
                "item_type": "RELEASE_GATE",
                "spec_fact_refs": ["REGISTERED-FACT-001"],
            }],
        }
        result = validate_spec_fact_refs_in_sal_output(decl, repo_root=sal_env)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True
        assert any("quality=1" in str(v) for v in result["items"])

    def test_release_gate_accepts_verified_level_2(self, sal_env):
        """RELEASE_GATE items can cite text-verified facts (Level 2)."""
        decl = {
            "planned_work_items": [{
                "item_id": "WI-QT-005",
                "item_type": "RELEASE_GATE",
                "spec_fact_refs": ["VERIFIED-FACT-001"],
            }],
        }
        result = validate_spec_fact_refs_in_sal_output(decl, repo_root=sal_env)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_missing_fact_always_fails(self, sal_env):
        """Missing facts fail regardless of item_type."""
        decl = {
            "planned_work_items": [{
                "item_id": "WI-QT-006",
                "item_type": "PRODUCT_SOURCE",
                "spec_fact_refs": ["NONEXISTENT-FACT-999"],
            }],
        }
        result = validate_spec_fact_refs_in_sal_output(decl, repo_root=sal_env)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True
        assert any("not found" in str(v) for v in result["items"])

    def test_governance_taskcard_exempt(self, sal_env):
        """GOVERNANCE_TASKCARD items are exempt from V47 quality checks."""
        decl = {
            "planned_work_items": [{
                "item_id": "WI-QT-007",
                "item_type": "GOVERNANCE_TASKCARD",
                "spec_fact_refs": ["NONEXISTENT-FACT-999"],
            }],
        }
        result = validate_spec_fact_refs_in_sal_output(decl, repo_root=sal_env)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_mixed_items_one_failure_blocks(self, sal_env):
        """If any item fails quality check, the whole sprint blocks."""
        decl = {
            "planned_work_items": [
                {
                    "item_id": "WI-QT-008A",
                    "item_type": "PRODUCT_SOURCE",
                    "spec_fact_refs": ["BOOTSTRAP-FACT-001"],  # Level 0 -> PASS
                },
                {
                    "item_id": "WI-QT-008B",
                    "item_type": "READINESS",
                    "spec_fact_refs": ["BOOTSTRAP-FACT-001"],  # Level 0 < 1 -> FAIL
                },
            ],
        }
        result = validate_spec_fact_refs_in_sal_output(decl, repo_root=sal_env)
        assert result["result"] == "FAIL"
        assert result["blocks_sprint"] is True
        assert len(result["items"]) == 1
        assert result["items"][0]["item_id"] == "WI-QT-008B"

    def test_product_test_accepts_bootstrap(self, sal_env):
        """PRODUCT_TEST items use Level 0 threshold like PRODUCT_SOURCE."""
        decl = {
            "planned_work_items": [{
                "item_id": "WI-QT-009",
                "item_type": "PRODUCT_TEST",
                "spec_fact_refs": ["BOOTSTRAP-FACT-001"],
            }],
        }
        result = validate_spec_fact_refs_in_sal_output(decl, repo_root=sal_env)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False

    def test_sal_absent_is_pass(self, tmp_path):
        """When sal-facts-latest.json doesn't exist, V47 returns PASS (bootstrap tolerance)."""
        decl = {
            "planned_work_items": [{
                "item_id": "WI-QT-010",
                "item_type": "RELEASE_GATE",
                "spec_fact_refs": ["FACT-ANYTHING"],
            }],
        }
        result = validate_spec_fact_refs_in_sal_output(decl, repo_root=tmp_path)
        assert result["result"] == "PASS"
        assert result["blocks_sprint"] is False
