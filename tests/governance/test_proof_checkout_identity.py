"""Cross-platform checkout invariants for content-addressed proof inputs."""

from __future__ import annotations

import hashlib
import subprocess
from pathlib import Path

import pytest


REPO_ROOT = Path(__file__).resolve().parents[2]

PROOF_TEXT_PATHS = (
    ".gitattributes",
    ".claude/commands/command-registry.yaml",
    ".supervisor/skill-registry.yaml",
    "AGENTS.md",
    "plans/codex/handover/CURRENT-MACHINE-STATE.yaml",
    "pyproject.toml",
    "reports/ff6/xliff-core-obligation-denominator.yaml",
    "reports/sal-verification/xliff.json",
    "schemas/sal-facts/sal-facts-schema.json",
    "shared/sal-facts/evidence/xliff.yaml",
    "tests/tools/test_xliff_core_candidate_adjudication.py",
    "tools/spec/xliff_core_candidate_adjudication.py",
    "virtual/proof.pyi",
    "virtual/proof.jsonl",
    "virtual/proof.yml",
    "virtual/proof.rst",
    "virtual/proof.ini",
    "virtual/proof.cfg",
    "virtual/proof.xsd",
    "virtual/proof.sch",
    "virtual/proof.xml",
    "virtual/proof.xlf",
    "virtual/proof.xliff",
    "virtual/proof.sh",
    "virtual/proof.lock",
)

BYTE_EXACT_PATHS = (
    "samples/by-format/ipynb/line-ending-case.ipynb",
    "tests/fixtures/nrrd/line-ending-case.nrrd",
    "oracle/formats/xliff/fixtures/line-ending-case.xliff",
    "samples/by-format/openraster/layers.ora",
    "samples/by-format/safetensors/tensors.safetensors",
    "samples/by-format/ubl/invoice.xml",
    "samples/by-format/image/thumbnail.png",
    "samples/by-format/archive/source.zip",
    "tests/fixtures/json/byte-exact.json",
    "oracle/formats/ubl/fixtures/byte-exact.xml",
    "virtual/format.nhdr",
    "virtual/authority.bin",
    "virtual/array.npy",
    "virtual/array.npz",
    "virtual/document.pdf",
    "virtual/archive.gz",
    "virtual/archive.bz2",
    "virtual/archive.zst",
)


def _git(cwd: Path, *args: str) -> bytes:
    return subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    ).stdout


def _attributes(*paths: str) -> dict[str, dict[str, str]]:
    output = _git(REPO_ROOT, "check-attr", "text", "eol", "--", *paths).decode(
        "utf-8"
    )
    result: dict[str, dict[str, str]] = {path: {} for path in paths}
    for line in output.splitlines():
        path, attribute, value = line.split(": ", 2)
        result[path][attribute] = value
    return result


@pytest.mark.parametrize("path", PROOF_TEXT_PATHS)
def test_proof_bearing_text_has_explicit_lf_checkout(path: str) -> None:
    attributes = _attributes(path)[path]
    assert attributes == {"text": "set", "eol": "lf"}


@pytest.mark.parametrize("path", BYTE_EXACT_PATHS)
def test_byte_sensitive_format_inputs_are_never_text_normalized(path: str) -> None:
    attributes = _attributes(path)[path]
    assert attributes["text"] == "unset"
    assert attributes["eol"] == "unspecified"


def _checkout_bytes(repo: Path, path: Path, autocrlf: str) -> bytes:
    _git(repo, "config", "core.autocrlf", autocrlf)
    path.unlink()
    _git(repo, "checkout", "--", path.relative_to(repo).as_posix())
    return path.read_bytes()


def test_supported_checkout_modes_keep_one_raw_proof_identity(
    tmp_path: Path,
) -> None:
    repo = tmp_path / "repository"
    repo.mkdir()
    (repo / ".gitattributes").write_bytes(
        (REPO_ROOT / ".gitattributes").read_bytes()
    )
    proof = repo / "proof.yaml"
    proof.write_bytes(b"alpha: one\r\nbeta: two\r\n")
    fixture = repo / "samples" / "by-format" / "nrrd" / "line-endings.nrrd"
    fixture.parent.mkdir(parents=True)
    fixture_bytes = b"NRRD0005\r\n# exact fixture\r\n\x00payload"
    fixture.write_bytes(fixture_bytes)

    _git(repo, "init", "--quiet")
    _git(repo, "config", "user.email", "proof-checkout@example.invalid")
    _git(repo, "config", "user.name", "Proof Checkout Test")
    _git(repo, "config", "core.autocrlf", "true")
    _git(repo, "add", ".gitattributes", "proof.yaml", "samples")
    _git(repo, "commit", "--quiet", "-m", "fixture")

    committed_proof = _git(repo, "show", "HEAD:proof.yaml")
    assert committed_proof == b"alpha: one\nbeta: two\n"
    assert _git(
        repo,
        "show",
        "HEAD:samples/by-format/nrrd/line-endings.nrrd",
    ) == fixture_bytes

    checkouts = {
        mode: _checkout_bytes(repo, proof, mode)
        for mode in ("false", "input", "true")
    }
    assert set(checkouts.values()) == {committed_proof}
    raw_hashes = {
        hashlib.sha256(content).hexdigest() for content in checkouts.values()
    }
    assert raw_hashes == {hashlib.sha256(committed_proof).hexdigest()}

    fixture_checkout = _checkout_bytes(repo, fixture, "true")
    assert fixture_checkout == fixture_bytes

    tampered = committed_proof.replace(b"beta: two", b"beta: three")
    assert hashlib.sha256(tampered).hexdigest() not in raw_hashes
