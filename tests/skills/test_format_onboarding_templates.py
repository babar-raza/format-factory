"""
tests/skills/test_format_onboarding_templates.py

Tests for format onboarding schema and templates — Lane D CONWAY-R7R8.
"""

from __future__ import annotations

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "skills"))


SCHEMA_PATH = REPO_ROOT / "schemas" / "skills" / "format-onboarding.schema.yaml"
TEMPLATES_DIR = REPO_ROOT / "templates" / "format-onboarding"
PUBLIC_SPEC_TEMPLATE = TEMPLATES_DIR / "public-spec-onboarding-template.yaml"
RE_SAFE_TEMPLATE = TEMPLATES_DIR / "reverse-engineering-safe-template.yaml"


def _load_yaml(path: Path) -> dict:
    import yaml
    return yaml.safe_load(path.read_text(encoding="utf-8")) or {}


class TestSchemaExists:
    def test_schema_file_exists(self):
        assert SCHEMA_PATH.exists(), f"Schema not found: {SCHEMA_PATH}"

    def test_schema_is_valid_yaml(self):
        data = _load_yaml(SCHEMA_PATH)
        assert isinstance(data, dict)
        assert "properties" in data

    def test_schema_has_required_fields(self):
        data = _load_yaml(SCHEMA_PATH)
        required = data.get("required", [])
        mandatory = {"format_id", "format_name", "extensions",
                     "legal_provenance_classification", "public_spec_availability",
                     "support_matrix_audit_status", "parser_classification",
                     "reverse_engineering_safe", "onboarding_readiness"}
        for field in mandatory:
            assert field in required, f"Required field {field!r} missing from schema"


class TestPublicSpecTemplate:
    def test_template_exists(self):
        assert PUBLIC_SPEC_TEMPLATE.exists()

    def test_template_is_valid_yaml(self):
        data = _load_yaml(PUBLIC_SPEC_TEMPLATE)
        assert isinstance(data, dict)

    def test_template_legal_provenance_is_public_spec(self):
        data = _load_yaml(PUBLIC_SPEC_TEMPLATE)
        assert data.get("legal_provenance_classification") == "PUBLIC_SPEC"

    def test_template_audit_status_needs_audit(self):
        """All templates must start with NEEDS_AUDIT."""
        data = _load_yaml(PUBLIC_SPEC_TEMPLATE)
        assert data.get("support_matrix_audit_status") == "NEEDS_AUDIT"

    def test_template_onboarding_readiness_is_candidate(self):
        data = _load_yaml(PUBLIC_SPEC_TEMPLATE)
        readiness = data.get("onboarding_readiness", {})
        assert readiness.get("overall") == "CANDIDATE"

    def test_template_has_warning_about_human_authorization(self):
        """Template notes must mention human authorization."""
        data = _load_yaml(PUBLIC_SPEC_TEMPLATE)
        notes = data.get("onboarding_readiness", {}).get("notes", "")
        assert "human" in notes.lower() or "authorization" in notes.lower()

    def test_template_reverse_engineering_safe_true(self):
        data = _load_yaml(PUBLIC_SPEC_TEMPLATE)
        assert data.get("reverse_engineering_safe") is True


class TestReverseEngineeringSafeTemplate:
    def test_template_exists(self):
        assert RE_SAFE_TEMPLATE.exists()

    def test_template_is_valid_yaml(self):
        data = _load_yaml(RE_SAFE_TEMPLATE)
        assert isinstance(data, dict)

    def test_template_audit_status_needs_audit(self):
        data = _load_yaml(RE_SAFE_TEMPLATE)
        assert data.get("support_matrix_audit_status") == "NEEDS_AUDIT"

    def test_template_onboarding_readiness_is_candidate(self):
        data = _load_yaml(RE_SAFE_TEMPLATE)
        readiness = data.get("onboarding_readiness", {})
        assert readiness.get("overall") == "CANDIDATE"

    def test_template_notes_mention_human_verification(self):
        data = _load_yaml(RE_SAFE_TEMPLATE)
        notes = data.get("onboarding_readiness", {}).get("notes", "")
        assert "human" in notes.lower()

    def test_template_legal_classification_is_community_documented(self):
        data = _load_yaml(RE_SAFE_TEMPLATE)
        assert data.get("legal_provenance_classification") == "COMMUNITY_DOCUMENTED"


class TestTemplatesConsistency:
    def test_both_templates_start_as_candidate(self):
        for path in [PUBLIC_SPEC_TEMPLATE, RE_SAFE_TEMPLATE]:
            data = _load_yaml(path)
            assert data["onboarding_readiness"]["overall"] == "CANDIDATE", (
                f"{path.name} must start as CANDIDATE"
            )

    def test_both_templates_have_audit_warning(self):
        for path in [PUBLIC_SPEC_TEMPLATE, RE_SAFE_TEMPLATE]:
            data = _load_yaml(path)
            assert data.get("support_matrix_audit_status") == "NEEDS_AUDIT", (
                f"{path.name} must have NEEDS_AUDIT"
            )

    def test_all_readiness_fields_not_ready_in_templates(self):
        """All readiness fields in templates should NOT be READY (no premature readiness)."""
        not_ready_values = {"REQUIRES_AUDIT", "REQUIRES_SPEC_RETRIEVAL",
                            "REQUIRES_REQUIREMENTS", "REQUIRES_VERIFIER_REVIEW",
                            "NOT_APPLICABLE", "BLOCKED", "UNKNOWN"}
        readiness_fields = [
            "normalization_readiness", "requirements_generation_readiness",
            "implementation_readiness", "iv_readiness",
        ]
        for path in [PUBLIC_SPEC_TEMPLATE, RE_SAFE_TEMPLATE]:
            data = _load_yaml(path)
            for field in readiness_fields:
                val = data.get(field)
                if val is not None:
                    assert val in not_ready_values, (
                        f"{path.name} has {field}={val!r} — templates must not be READY"
                    )
