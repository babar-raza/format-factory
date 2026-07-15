"""V226 validate_package_install_proof_coverage — unit tests.

Four fixtures prove the healed system's enforcement semantics:
  1. pre-fix replay  — matrix exists, NO proof manifest -> FAIL
                       (this is the exact GAP-FORENSIC-001 state; the old system
                       had no validator to catch it, so this test IS the proof
                       that the healed system would have caught it)
  2. stale digest    — proof exists but source changed since -> FAIL
  3. drift           — a src/python package missing from the matrix -> FAIL
  4. healthy         — fresh passing proof for the whole fleet -> PASS
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import pytest
import yaml

_REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(_REPO / "tools" / "supervisor"))

from governance_validators_package_proof import (  # noqa: E402
    validate_package_install_proof_coverage,
)
from package_proof_common import source_digest  # noqa: E402

_DECL = {"run_id": "v226-unit-test", "work_items": []}


def _make_repo(tmp_path: Path, formats: list[str]) -> Path:
    """Fake repo: src/python/<fmt>/ packages + a matrix covering them."""
    repo = tmp_path / "repo"
    for fmt in formats:
        pkg = repo / "src" / "python" / fmt
        pkg.mkdir(parents=True)
        (pkg / "pyproject.toml").write_text(f'[project]\nname = "format-factory-{fmt}"\n')
        (pkg / f"{fmt}_codec.py").write_text(f"def load(path):\n    return {{'format': '{fmt}'}}\n")
    matrix = {
        "packages": [
            {
                "format_id": fmt,
                "package_name": f"format-factory-{fmt}",
                "module_import": fmt,
                "install_proof": {
                    "smoke_module": f"{fmt}.{fmt}_codec",
                    "smoke_callable": "load",
                    "smoke_sample": f"samples/by-format/{fmt}/minimal.{fmt}",
                    "expected": "dict",
                },
            }
            for fmt in formats
        ]
    }
    matrix_path = repo / "packaging" / "python" / "package-matrix.yaml"
    matrix_path.parent.mkdir(parents=True)
    matrix_path.write_text(yaml.dump(matrix))
    return repo


def _write_manifest(repo: Path, formats: list[str], digests: dict[str, str]) -> None:
    manifest = {
        "schema_version": 1,
        "formats": {
            fmt: {
                "package_name": f"format-factory-{fmt}",
                "verdict": "PASS",
                "source_digest": digests[fmt],
            }
            for fmt in formats
        },
    }
    path = repo / "reports" / "package-install-proof" / "proof-manifest.json"
    path.parent.mkdir(parents=True)
    path.write_text(json.dumps(manifest))


def test_prefix_replay_no_manifest_fails(tmp_path):
    """The original GAP-FORENSIC-001 state: fleet defined, zero install proof.
    The healed system must block — proving it would have caught the gap."""
    repo = _make_repo(tmp_path, ["fods", "abw"])
    result = validate_package_install_proof_coverage(_DECL, repo_root=repo)
    assert result["result"] == "FAIL"
    assert result["blocks_sprint"] is True
    assert "MISSING" in result["summary"]
    assert "proof-manifest.json" in result["summary"]


def test_stale_digest_fails(tmp_path):
    """Proof of old source is not proof of current source."""
    repo = _make_repo(tmp_path, ["fods"])
    digests = {"fods": source_digest(repo, "fods")}
    _write_manifest(repo, ["fods"], digests)
    # source changes after the proof was produced
    (repo / "src" / "python" / "fods" / "fods_codec.py").write_text(
        "def load(path):\n    return {'format': 'fods', 'v': 2}\n")
    result = validate_package_install_proof_coverage(_DECL, repo_root=repo)
    assert result["result"] == "FAIL"
    assert result["blocks_sprint"] is True
    assert "STALE" in result["summary"]
    assert "fods" in result["summary"]


def test_drift_unmatrixed_package_fails(tmp_path):
    """The next-Python-product hook: a src package outside the matrix blocks."""
    repo = _make_repo(tmp_path, ["fods"])
    digests = {"fods": source_digest(repo, "fods")}
    _write_manifest(repo, ["fods"], digests)
    newpkg = repo / "src" / "python" / "newfmt"
    newpkg.mkdir()
    (newpkg / "pyproject.toml").write_text('[project]\nname = "format-factory-newfmt"\n')
    result = validate_package_install_proof_coverage(_DECL, repo_root=repo)
    assert result["result"] == "FAIL"
    assert result["blocks_sprint"] is True
    assert "DRIFT" in result["summary"]
    assert "newfmt" in result["summary"]


def test_healthy_state_passes(tmp_path):
    """Fresh passing proof for the whole fleet -> PASS, non-blocking."""
    repo = _make_repo(tmp_path, ["fods", "abw"])
    digests = {fmt: source_digest(repo, fmt) for fmt in ["fods", "abw"]}
    _write_manifest(repo, ["fods", "abw"], digests)
    result = validate_package_install_proof_coverage(_DECL, repo_root=repo)
    assert result["result"] == "PASS"
    assert result["blocks_sprint"] is False


def test_failing_verdict_fails(tmp_path):
    """A format with a recorded FAIL verdict blocks — no fake progress."""
    repo = _make_repo(tmp_path, ["fods"])
    digests = {"fods": source_digest(repo, "fods")}
    _write_manifest(repo, ["fods"], digests)
    manifest_path = repo / "reports" / "package-install-proof" / "proof-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["formats"]["fods"]["verdict"] = "FAIL"
    manifest_path.write_text(json.dumps(manifest))
    result = validate_package_install_proof_coverage(_DECL, repo_root=repo)
    assert result["result"] == "FAIL"
    assert "verdict != PASS" in result["summary"]


def test_waived_known_failure_warns_not_blocks(tmp_path):
    """A FAIL verdict covered by a gap-register waiver (install_proof.known_failure)
    downgrades to WARN — tracked exception, never silent, never blocking."""
    repo = _make_repo(tmp_path, ["fods", "csv"])
    digests = {fmt: source_digest(repo, fmt) for fmt in ["fods", "csv"]}
    _write_manifest(repo, ["fods", "csv"], digests)
    manifest_path = repo / "reports" / "package-install-proof" / "proof-manifest.json"
    manifest = json.loads(manifest_path.read_text())
    manifest["formats"]["csv"]["verdict"] = "FAIL"
    manifest_path.write_text(json.dumps(manifest))

    matrix_path = repo / "packaging" / "python" / "package-matrix.yaml"
    matrix = yaml.safe_load(matrix_path.read_text())
    csv_entry = next(p for p in matrix["packages"] if p["format_id"] == "csv")
    csv_entry["install_proof"]["known_failure"] = {
        "gap_id": "GAP-FORENSIC-025",
        "reason": "stdlib csv shadows the wheel module",
    }
    matrix_path.write_text(yaml.dump(matrix))

    result = validate_package_install_proof_coverage(_DECL, repo_root=repo)
    assert result["result"] == "WARN"
    assert result["blocks_sprint"] is False
    assert "GAP-FORENSIC-025" in result["summary"]

    # the waiver never applies to a MISSING proof entry — proof must still run
    manifest = json.loads(manifest_path.read_text())
    del manifest["formats"]["csv"]
    manifest_path.write_text(json.dumps(manifest))
    result = validate_package_install_proof_coverage(_DECL, repo_root=repo)
    assert result["result"] == "FAIL"
    assert "no proof entry" in result["summary"]


if __name__ == "__main__":
    sys.exit(pytest.main([__file__, "-v"]))
