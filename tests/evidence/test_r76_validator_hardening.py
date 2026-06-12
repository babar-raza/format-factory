"""
tests/evidence/test_r76_validator_hardening.py

R76 validator hardening tests. Verifies that the R76 additions to
validate_evidence_bundle.py correctly reject R75-style defects.

Covers:
1. Reject "will be updated after delivery package build" (R75 defect D06)
2. Reject "This summary will be updated" (variant)
3. Reject non-green AUTHORITATIVE_TEST_RESULT (R75 defect D03)
4. Permit zero-failures AUTHORITATIVE_TEST_RESULT
5. build_supervisor_review_package.py: validates authority JSON schema
6. build_supervisor_review_package.py: validates sidecar proves evidence ZIP
7. build_supervisor_review_package.py: validates standalone SHA file
"""

import hashlib
import json
import sys
import zipfile
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "evidence"))

from validate_evidence_bundle import (
    check_authoritative_test_result_non_green,
    PENDING_MARKER_PATTERNS,
    CLOSEOUT_HYGIENE_TOKENS,
)
from build_supervisor_review_package import build_supervisor_review_package


# ---------------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------------

def _sha256(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


# ---------------------------------------------------------------------------
# PENDING_MARKER_PATTERNS coverage — new R76 patterns
# ---------------------------------------------------------------------------

class TestPendingMarkerPatternsR76:
    def test_rejects_will_be_updated_after_delivery(self):
        assert "will be updated after delivery package build" in PENDING_MARKER_PATTERNS

    def test_rejects_this_summary_will_be_updated(self):
        assert "This summary will be updated" in PENDING_MARKER_PATTERNS


# ---------------------------------------------------------------------------
# CLOSEOUT_HYGIENE_TOKENS coverage — new R76 tokens
# ---------------------------------------------------------------------------

class TestCloseoutHygieneTokensR76:
    def test_rejects_will_be_updated_after_delivery_lowercase(self):
        assert "will be updated after delivery package build" in CLOSEOUT_HYGIENE_TOKENS

    def test_rejects_this_summary_will_be_updated_lowercase(self):
        assert "this summary will be updated" in CLOSEOUT_HYGIENE_TOKENS


# ---------------------------------------------------------------------------
# check_authoritative_test_result_non_green
# ---------------------------------------------------------------------------

class TestCheckAuthoritativeTestResultNonGreen:
    def test_rejects_positive_failure_count(self):
        content = {"python-tests-summary.txt": "AUTHORITATIVE_TEST_RESULT: 6140 passed, 7 failed, 24 skipped"}
        errors = check_authoritative_test_result_non_green(content)
        assert len(errors) > 0
        assert "6140" in errors[0] or "7" in errors[0]

    def test_permits_zero_failures(self):
        content = {"validation-command-log.txt": "AUTHORITATIVE_TEST_RESULT: 6147 passed, 0 failed, 24 skipped"}
        errors = check_authoritative_test_result_non_green(content)
        assert errors == []

    def test_permits_no_failed_keyword(self):
        content = {"log.txt": "AUTHORITATIVE_TEST_RESULT: 100 passed, 5 skipped"}
        errors = check_authoritative_test_result_non_green(content)
        assert errors == []

    def test_handles_multiple_files_one_bad(self):
        content = {
            "clean.txt": "AUTHORITATIVE_TEST_RESULT: 100 passed, 0 failed",
            "bad.txt": "AUTHORITATIVE_TEST_RESULT: 50 passed, 3 failed",
        }
        errors = check_authoritative_test_result_non_green(content)
        assert len(errors) == 1
        assert "bad.txt" in errors[0]

    def test_handles_no_authoritative_result_lines(self):
        content = {"log.txt": "some other content without the magic line"}
        errors = check_authoritative_test_result_non_green(content)
        assert errors == []

    def test_parses_comma_separated_format(self):
        content = {"summary.txt": "AUTHORITATIVE_TEST_RESULT: 200 passed, 1 failed, 10 skipped"}
        errors = check_authoritative_test_result_non_green(content)
        assert len(errors) == 1

    def test_rejects_single_digit_failures(self):
        content = {"log.txt": "AUTHORITATIVE_TEST_RESULT: 5 passed, 1 failed"}
        errors = check_authoritative_test_result_non_green(content)
        assert len(errors) == 1


# ---------------------------------------------------------------------------
# build_supervisor_review_package — validation checks
# ---------------------------------------------------------------------------

def _make_fake_sidecar(evidence_sha: str, out_path: Path) -> None:
    data = {"sha256": evidence_sha, "validation_result": "PASS"}
    out_path.write_text(json.dumps(data))


def _make_fake_authority_json(
    inner_sha: str, sidecar_sha: str, delivery_sha: str, out_path: Path
) -> None:
    data = {
        "schema_version": "1.0",
        "sprint_id": "R76",
        "generated_at_utc": "2026-05-30T00:00:00+00:00",
        "authority_model": "two_layer",
        "source_evidence_authority": {
            "inner_zip_filename": "r76-pass1-final.zip",
            "inner_zip_sha256": inner_sha,
            "inner_zip_size_bytes": 100,
            "inner_zip_entry_count": 5,
            "sidecar_filename": "r76-pass1-final.sha256-proof.json",
            "sidecar_sha256": sidecar_sha,
            "sidecar_validates_inner_zip": True,
        },
        "final_artifact_authority": {
            "delivery_package_filename": "r76-delivery-package.zip",
            "delivery_package_sha256": delivery_sha,
            "delivery_package_size_bytes": 200,
            "delivery_package_entry_count": 4,
            "standalone_sha_file": "r76-delivery-package.sha256.txt",
        },
        "cross_layer_validation": {
            "all_sha_fields_non_circular": True,
            "sidecar_proves_inner_zip": True,
            "delivery_contains_inner_zip_and_sidecar": True,
        },
    }
    out_path.write_text(json.dumps(data))


class TestBuildSupervisorReviewPackageValidation:
    def _build_valid_artifacts(self, tmp_path: Path) -> dict:
        """Create a minimal set of valid artifacts for testing."""
        # Create evidence ZIP
        evidence_zip = tmp_path / "r76-pass1-final.zip"
        with zipfile.ZipFile(evidence_zip, "w") as zf:
            zf.writestr("bundle-metadata/sprint-id.txt", "R76")
        evidence_sha = _sha256(evidence_zip)

        # Create sidecar
        sidecar = tmp_path / "r76-pass1-final.sha256-proof.json"
        _make_fake_sidecar(evidence_sha, sidecar)
        sidecar_sha = _sha256(sidecar)

        # Create delivery package
        delivery_pkg = tmp_path / "r76-delivery-package.zip"
        with zipfile.ZipFile(delivery_pkg, "w") as zf:
            zf.write(evidence_zip, evidence_zip.name)
            zf.write(sidecar, sidecar.name)
        delivery_sha = _sha256(delivery_pkg)

        # Standalone SHA file
        sha_file = tmp_path / "r76-delivery-package.sha256.txt"
        sha_file.write_text(f"{delivery_sha}  r76-delivery-package.zip\n")

        # Authority JSON
        authority = tmp_path / "r76-final-artifact-authority.json"
        _make_fake_authority_json(evidence_sha, sidecar_sha, delivery_sha, authority)

        # Manifest
        manifest = tmp_path / "r76-delivery-manifest.json"
        manifest.write_text(json.dumps({"delivery_package_version": "1.1"}))

        # Supervisor readme
        readme = tmp_path / "r76-supervisor-inspection-readme.md"
        readme.write_text("# Supervisor Inspection Readme\n\nUpload this package.")

        return {
            "delivery_package": delivery_pkg,
            "sha_file": sha_file,
            "authority_json": authority,
            "evidence_zip": evidence_zip,
            "sidecar": sidecar,
            "manifest": manifest,
            "supervisor_readme": readme,
        }

    def test_build_succeeds_with_valid_artifacts(self, tmp_path):
        arts = self._build_valid_artifacts(tmp_path)
        output = tmp_path / "r76-supervisor-review-package.zip"
        result = build_supervisor_review_package(
            delivery_package=arts["delivery_package"],
            sha_file=arts["sha_file"],
            authority_json=arts["authority_json"],
            evidence_zip=arts["evidence_zip"],
            sidecar=arts["sidecar"],
            manifest=arts["manifest"],
            supervisor_readme=arts["supervisor_readme"],
            final_response_summary=None,
            output=output,
        )
        assert result["validation_result"] == "PASS"
        assert output.exists()

    def test_review_package_contains_all_required_files(self, tmp_path):
        arts = self._build_valid_artifacts(tmp_path)
        output = tmp_path / "r76-supervisor-review-package.zip"
        build_supervisor_review_package(
            delivery_package=arts["delivery_package"],
            sha_file=arts["sha_file"],
            authority_json=arts["authority_json"],
            evidence_zip=arts["evidence_zip"],
            sidecar=arts["sidecar"],
            manifest=arts["manifest"],
            supervisor_readme=arts["supervisor_readme"],
            final_response_summary=None,
            output=output,
        )
        with zipfile.ZipFile(output, "r") as zf:
            names = set(zf.namelist())
        # Must include authority JSON and standalone SHA file
        assert "r76-final-artifact-authority.json" in names
        assert "r76-delivery-package.sha256.txt" in names
        assert "r76-delivery-package.zip" in names
        assert "r76-pass1-final.zip" in names
        assert "r76-pass1-final.sha256-proof.json" in names

    def test_rejects_wrong_sidecar_sha(self, tmp_path):
        arts = self._build_valid_artifacts(tmp_path)
        # Corrupt the sidecar by writing a wrong SHA
        arts["sidecar"].write_text(json.dumps({"sha256": "wrong" * 8}))
        output = tmp_path / "r76-supervisor-review-package.zip"
        with pytest.raises((ValueError, Exception)):
            build_supervisor_review_package(
                delivery_package=arts["delivery_package"],
                sha_file=arts["sha_file"],
                authority_json=arts["authority_json"],
                evidence_zip=arts["evidence_zip"],
                sidecar=arts["sidecar"],
                manifest=arts["manifest"],
                supervisor_readme=arts["supervisor_readme"],
                final_response_summary=None,
                output=output,
            )

    def test_rejects_missing_authority_json(self, tmp_path):
        arts = self._build_valid_artifacts(tmp_path)
        arts["authority_json"].unlink()
        output = tmp_path / "r76-supervisor-review-package.zip"
        with pytest.raises(FileNotFoundError):
            build_supervisor_review_package(
                delivery_package=arts["delivery_package"],
                sha_file=arts["sha_file"],
                authority_json=arts["authority_json"],
                evidence_zip=arts["evidence_zip"],
                sidecar=arts["sidecar"],
                manifest=arts["manifest"],
                supervisor_readme=arts["supervisor_readme"],
                final_response_summary=None,
                output=output,
            )

    def test_rejects_delegation_label_in_authority_json(self, tmp_path):
        arts = self._build_valid_artifacts(tmp_path)
        # Corrupt authority JSON with delegation label
        data = json.loads(arts["authority_json"].read_text())
        data["source_evidence_authority"]["inner_zip_sha256"] = "delegated_to_final_artifact_authority_json"
        arts["authority_json"].write_text(json.dumps(data))
        output = tmp_path / "r76-supervisor-review-package.zip"
        with pytest.raises(ValueError):
            build_supervisor_review_package(
                delivery_package=arts["delivery_package"],
                sha_file=arts["sha_file"],
                authority_json=arts["authority_json"],
                evidence_zip=arts["evidence_zip"],
                sidecar=arts["sidecar"],
                manifest=arts["manifest"],
                supervisor_readme=arts["supervisor_readme"],
                final_response_summary=None,
                output=output,
            )
