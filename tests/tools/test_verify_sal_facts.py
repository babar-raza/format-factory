"""Regression tests for exact, content-addressed SAL fact verification."""

from __future__ import annotations

import hashlib
import io
import json
import tarfile
from pathlib import Path

import pytest
import yaml

from tools.spec.sal_proof import (
    canonical_json_bytes,
    claim_digest,
    sha256_bytes,
    sha256_file,
    validate_fact_promotion,
)
from tools.spec.verify_sal_facts import (
    VerificationError,
    apply_receipt,
    verify_format,
)


def _authority_archive(path: Path, schema: dict) -> tuple[str, str]:
    member = "authority/schema.json"
    content = json.dumps(schema, sort_keys=True).encode("utf-8")
    with tarfile.open(path, "w:gz") as archive:
        info = tarfile.TarInfo(member)
        info.size = len(content)
        info.mtime = 0
        archive.addfile(info, io.BytesIO(content))
    return member, sha256_bytes(content)


def _fixture_repo(tmp_path: Path) -> tuple[Path, str]:
    repo = tmp_path / "repo"
    for relative in (
        "shared/format-contracts/research",
        "shared/sal-facts/evidence",
        "shared/sal-facts",
        "tools/spec",
    ):
        (repo / relative).mkdir(parents=True, exist_ok=True)
    verifier_source = Path(__file__).resolve().parents[2] / "tools" / "spec"
    for name in ("verify_sal_facts.py", "sal_proof.py"):
        (repo / "tools" / "spec" / name).write_bytes(
            (verifier_source / name).read_bytes()
        )

    archive = repo / ".local" / "authority.tar.gz"
    archive.parent.mkdir(parents=True)
    member, member_digest = _authority_archive(
        archive,
        {
            "type": "object",
            "required": ["cells"],
            "properties": {"cells": {"type": "array"}},
        },
    )
    research = {
        "format_id": "testfmt",
        "source_records": [
            {
                "source_id": "SRC-TEST-001",
                "acquisition_status": "ACQUIRED",
                "local_path": ".local/authority.tar.gz",
                "content_hash": sha256_file(archive),
            }
        ],
    }
    (repo / "shared/format-contracts/research/testfmt.yaml").write_text(
        yaml.safe_dump(research, sort_keys=False), encoding="utf-8"
    )
    claim = "A document requires a cells array."
    store = {
        "format_id": "testfmt",
        "facts": [
            {
                "fact_id": "SAL-TESTFMT-00001",
                "qname": "FACT-TESTFMT-001",
                "claim": claim,
                "verification_status": "structural_derivation",
                "provenance": {"extraction_method": "structural_derivation"},
            }
        ],
    }
    (repo / "shared/sal-facts/testfmt.yaml").write_text(
        yaml.safe_dump(store, sort_keys=False), encoding="utf-8"
    )
    manifest = {
        "schema_version": "1.0",
        "format_id": "testfmt",
        "coverage": "complete",
        "facts": [
            {
                "fact_id": "SAL-TESTFMT-00001",
                "claim_sha256": claim_digest(claim),
                "assertions": [
                    {
                        "assertion_id": "required-cells",
                        "kind": "json_pointer_contains",
                        "source_id": "SRC-TEST-001",
                        "member": member,
                        "member_sha256": member_digest,
                        "pointer": "/required",
                        "expected": "cells",
                    },
                    {
                        "assertion_id": "cells-array",
                        "kind": "json_pointer_equals",
                        "source_id": "SRC-TEST-001",
                        "member": member,
                        "member_sha256": member_digest,
                        "pointer": "/properties/cells/type",
                        "expected": "array",
                    },
                ],
            }
        ],
    }
    (repo / "shared/sal-facts/evidence/testfmt.yaml").write_text(
        yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8"
    )
    return repo, member_digest


def test_exact_assertions_produce_a_deterministic_passing_receipt(
    tmp_path: Path,
) -> None:
    repo, _ = _fixture_repo(tmp_path)
    first = verify_format(repo, "testfmt")
    second = verify_format(repo, "testfmt")
    assert first == second
    assert first["result"] == "PASS"
    assert first["facts"][0]["result"] == "PASS"
    assert canonical_json_bytes(first) == canonical_json_bytes(second)


def test_claim_change_fails_instead_of_reusing_old_evidence(tmp_path: Path) -> None:
    repo, _ = _fixture_repo(tmp_path)
    store_path = repo / "shared/sal-facts/testfmt.yaml"
    store = yaml.safe_load(store_path.read_text(encoding="utf-8"))
    store["facts"][0]["claim"] = "A document may omit cells."
    store_path.write_text(yaml.safe_dump(store, sort_keys=False), encoding="utf-8")
    receipt = verify_format(repo, "testfmt")
    assert receipt["result"] == "FAIL"
    assert receipt["facts"][0]["result"] == "FAIL"


def test_authority_member_change_fails_closed(tmp_path: Path) -> None:
    repo, _ = _fixture_repo(tmp_path)
    manifest_path = repo / "shared/sal-facts/evidence/testfmt.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest["facts"][0]["assertions"][0]["member_sha256"] = "0" * 64
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    with pytest.raises(VerificationError, match="member digest mismatch"):
        verify_format(repo, "testfmt")


def test_incomplete_manifest_cannot_promote(tmp_path: Path) -> None:
    repo, _ = _fixture_repo(tmp_path)
    manifest_path = repo / "shared/sal-facts/evidence/testfmt.yaml"
    manifest = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    manifest["facts"] = []
    manifest_path.write_text(yaml.safe_dump(manifest, sort_keys=False), encoding="utf-8")
    with pytest.raises(VerificationError, match="coverage mismatch"):
        verify_format(repo, "testfmt")


def test_apply_binds_receipt_and_live_proof_validator(tmp_path: Path) -> None:
    repo, _ = _fixture_repo(tmp_path)
    receipt = verify_format(repo, "testfmt")
    receipt_path, store_path = apply_receipt(repo, "testfmt", receipt)
    fact = yaml.safe_load(store_path.read_text(encoding="utf-8"))["facts"][0]
    valid, reason = validate_fact_promotion(fact, repo)
    assert valid, reason
    assert fact["verification_status"] == "verified"
    assert hashlib.sha256(receipt_path.read_bytes()).hexdigest() == (
        fact["provenance"]["verification"]["receipt_sha256"]
    )


def test_manual_status_edit_is_not_proof(tmp_path: Path) -> None:
    repo, _ = _fixture_repo(tmp_path)
    store_path = repo / "shared/sal-facts/testfmt.yaml"
    fact = yaml.safe_load(store_path.read_text(encoding="utf-8"))["facts"][0]
    fact["verification_status"] = "verified"
    valid, reason = validate_fact_promotion(fact, repo)
    assert not valid
    assert "no content-addressed verification record" in reason


def test_changed_manifest_receipt_tool_and_authority_each_revoke_proof(
    tmp_path: Path,
) -> None:
    repo, _ = _fixture_repo(tmp_path)
    receipt = verify_format(repo, "testfmt")
    _, store_path = apply_receipt(repo, "testfmt", receipt)
    original_fact = yaml.safe_load(store_path.read_text(encoding="utf-8"))["facts"][0]

    cases = [
        repo / "shared/sal-facts/evidence/testfmt.yaml",
        repo / "reports/sal-verification/testfmt.json",
        repo / "tools/spec/verify_sal_facts.py",
        repo / ".local/authority.tar.gz",
    ]
    for path in cases:
        original = path.read_bytes()
        path.write_bytes(original + b"\n")
        valid, _ = validate_fact_promotion(original_fact, repo)
        assert not valid, f"changed input did not revoke proof: {path}"
        path.write_bytes(original)
