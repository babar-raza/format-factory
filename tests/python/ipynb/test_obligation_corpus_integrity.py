"""Content-addressed IPYNB corpus quarantine and replacement proof.

generated_by: codex
visibility: generated
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path

import nbformat
import pytest
import yaml
from nbformat.warnings import MissingIDFieldWarning

from format_factory.ipynb import IpynbParseError, load
from format_factory.ipynb.validation.schema import schema_diagnostics

ROOT = Path(__file__).resolve().parents[3]
CORPUS = ROOT / "samples" / "by-format" / "ipynb"
VALID = CORPUS / "valid"
QUARANTINE = CORPUS / "quarantine"
UPSTREAM_COMMIT = "60b6151fedcbdc9f137fb2d223eeb10c935a8378"

VALID_HASHES = {
    "minimal.ipynb": "60b1be44941df5d0394431f5c4a900937c6106d65888bd39ea9da9c76ca29b2b",
    "code-and-markdown.ipynb": "77c6d7cc3b70c2a34a2dc4f9c08a71ca20a146c579a9e41e21514bfc5c903a00",
    "with-outputs.ipynb": "03ac5f4dfae9bb393b88e39b11c2b12a7df7599e7918791e1ef837eb939e53ba",
}
QUARANTINE_HASHES = {
    "c8caeff0a36013b17b3c910f0b9ffe24b9b855aad958d02affb25147c9700b1a-code-and-markdown.ipynb": (
        "c8caeff0a36013b17b3c910f0b9ffe24b9b855aad958d02affb25147c9700b1a"
    ),
    "3b7d9f72565a7d916baa527976f00b5de4142ee148306bfed4bd16016b735e09-with-outputs.ipynb": (
        "3b7d9f72565a7d916baa527976f00b5de4142ee148306bfed4bd16016b735e09"
    ),
}
LICENSE_HASH = "41a8cd573abd9e43e6f644bb623ac1b0c1e977dae50b0c7740f82b84a427f78a"


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _json(path: Path) -> dict:
    value = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


def _yaml(path: Path) -> dict:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    assert isinstance(value, dict)
    return value


@pytest.mark.parametrize(("filename", "expected"), VALID_HASHES.items())
def test_active_valid_corpus_is_digest_bound_and_strictly_valid(
    filename: str,
    expected: str,
) -> None:
    path = VALID / filename
    assert _sha256(path) == expected
    value = _json(path)
    minor = value["nbformat_minor"]

    assert value["nbformat"] == 4
    assert 0 <= minor <= 5
    assert schema_diagnostics(value, minor=minor) == []
    nbformat.validate(copy.deepcopy(value), version=4, version_minor=minor)
    assert load(path, mode="strict").nbformat_minor == minor


@pytest.mark.parametrize(("filename", "expected"), QUARANTINE_HASHES.items())
def test_quarantined_bytes_are_retained_and_fail_the_declared_minor_schema(
    filename: str,
    expected: str,
) -> None:
    path = QUARANTINE / filename
    assert _sha256(path) == expected
    value = _json(path)

    assert (value["nbformat"], value["nbformat_minor"]) == (4, 5)
    diagnostics = schema_diagnostics(value, minor=5)
    missing_id_paths = {
        diagnostic.location.path
        for diagnostic in diagnostics
        if diagnostic.code == "IPYNB_SCHEMA_REQUIRED"
        and diagnostic.location is not None
        and diagnostic.location.path[-1:] == ("id",)
    }
    assert missing_id_paths
    with pytest.raises(IpynbParseError):
        load(path, mode="strict")


@pytest.mark.parametrize("filename", QUARANTINE_HASHES)
def test_reference_normalization_cannot_relabel_original_bytes_valid(
    filename: str,
) -> None:
    original = _json(QUARANTINE / filename)
    normalized = copy.deepcopy(original)

    with pytest.warns(MissingIDFieldWarning):
        nbformat.validate(normalized, version=4, version_minor=5)

    assert all("id" not in cell for cell in original["cells"])
    assert all("id" in cell for cell in normalized["cells"])
    assert schema_diagnostics(original, minor=5)


def test_redistribution_license_is_exact_and_bound_from_provenance() -> None:
    license_path = CORPUS / "LICENSE.nbformat-BSD-3-Clause.txt"
    provenance = _yaml(CORPUS / "_provenance.yaml")

    assert _sha256(license_path) == LICENSE_HASH
    assert provenance["authority"]["commit"] == UPSTREAM_COMMIT
    assert provenance["authority"]["license"] == "BSD-3-Clause"
    assert provenance["authority"]["license_sha256"] == LICENSE_HASH

    samples = {entry["sample_id"]: entry for entry in provenance["samples"]}
    for filename in ("code-and-markdown.ipynb", "with-outputs.ipynb"):
        entry = samples[f"valid/{filename}"]
        assert entry["source_type"] == "official-upstream-test-corpus"
        assert entry["source_commit"] == UPSTREAM_COMMIT
        assert entry["license"] == "BSD-3-Clause"
        assert entry["file_hash"] == f"sha256:{VALID_HASHES[filename]}"


def test_manifests_exclude_quarantine_from_positive_evidence() -> None:
    corpus_manifest = _yaml(CORPUS / "_corpus-manifest.yaml")
    quarantine_manifest = _yaml(QUARANTINE / "_manifest.yaml")
    oracle_package = _yaml(ROOT / "oracle" / "formats" / "ipynb" / "oracle-package.yaml")

    active = {
        entry["filename"]: entry["sha256"]
        for entry in corpus_manifest["valid_samples"]
    }
    assert active == {f"valid/{name}": digest for name, digest in VALID_HASHES.items()}
    assert corpus_manifest["summary"]["quarantined_count"] == 2
    assert all(
        not entry["positive_evidence_eligible"]
        for entry in corpus_manifest["quarantined_samples"]
    )
    assert all(
        not entry["positive_evidence_eligible"]
        for entry in quarantine_manifest["entries"]
    )

    refs = {
        Path(entry["sample_ref"]).name: entry["sha256"]
        for entry in oracle_package["corpus_refs"]
    }
    assert refs == {name: f"sha256:{digest}" for name, digest in VALID_HASHES.items()}
    assert oracle_package["status"] == "STALE"
    assert "production proof replay" in oracle_package["stale_reason"]
