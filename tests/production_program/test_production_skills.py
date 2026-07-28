"""Structural checks for the production Python skill and knowledge contract."""

from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
SKILLS = (
    "new-format-kickstart",
    "format-feature-expansion",
    "product-source-task",
)


def test_production_skills_are_not_poc_completion_checklists() -> None:
    forbidden = (
        "minimum viable slice",
        "min_7_tests",
        "min_9_tests",
        "no new external",
        "fewer than 7 tests",
        "fewer than 9 tests",
    )
    for skill_id in SKILLS:
        text = (ROOT / ".claude" / "commands" / f"{skill_id}.md").read_text(
            encoding="utf-8"
        ).lower()
        for phrase in forbidden:
            assert phrase not in text, (skill_id, phrase)
        assert "installed" in text
        assert "digest" in text
        assert "promotion" in text


def test_kickstart_routes_all_six_production_families() -> None:
    text = (
        ROOT / ".claude" / "commands" / "new-format-kickstart.md"
    ).read_text(encoding="utf-8")
    for family in (
        "json",
        "binary",
        "header_payload",
        "zip_container",
        "schema_xml",
        "large_schema_family",
    ):
        assert family in text


def test_production_knowledge_contract_is_current_and_complete() -> None:
    contract = yaml.safe_load(
        (ROOT / ".supervisor" / "knowledge" / "contracts" / "python-production-package.yaml")
        .read_text(encoding="utf-8")
    )
    assert contract["status"] == "VERIFIED_CURRENT"
    assert set(contract["required_layers"]) == {
        "model",
        "codec/reader",
        "codec/writer",
        "validation",
        "security",
        "adapters",
        "analytics",
        "cli",
    }
    assert any(
        "format_factory/__init__.py" in rule
        for rule in contract["distribution_rules"]
    )


def test_registry_handoffs_require_proof_inputs() -> None:
    registry = yaml.safe_load(
        (ROOT / ".supervisor" / "skill-registry.yaml").read_text(encoding="utf-8")
    )
    entries = {entry["skill_id"]: entry for entry in registry["skills"]}
    kickstart = entries["new-format-kickstart"]
    assert "product_contract_sha256" in kickstart["required_handoff_fields"]
    assert "authority_digests" in kickstart["required_handoff_fields"]
    expansion = entries["format-feature-expansion"]
    assert "obligation_id" in expansion["required_handoff_fields"]
    assert "proof_inputs" in expansion["required_handoff_fields"]
