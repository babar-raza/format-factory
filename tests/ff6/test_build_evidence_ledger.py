"""Tests for the per-format evidence-ledger builder.

The builder's job is to produce a ledger that cannot flatter the product. These
tests are aimed at the ways it could: inventing symbols, accepting
shadow-package tests as evidence, silently dropping an unmapped capability, or
emitting a status stronger than the evidence supports.
"""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from tools.ff6 import build_evidence_ledger as builder


@pytest.fixture
def demo(tmp_path: Path, monkeypatch: pytest.MonkeyPatch):
    """A self-contained format: register, ledger map, source, tests, evidence."""

    def make(
        *,
        capabilities: dict,
        obligations: list[dict] | None = None,
        source_files: dict[str, str] | None = None,
        test_files: dict[str, str] | None = None,
        execution_evidence: dict | None = None,
    ):
        src = tmp_path / "src/python/demo/src/format_factory/demo"
        tests = tmp_path / "tests/python/demo"
        maps = tmp_path / "maps"
        register_dir = tmp_path / "register"
        evidence_out = tmp_path / "evidence"
        reports = tmp_path / "reports"
        for directory in (src, tests, maps, register_dir, evidence_out, reports):
            directory.mkdir(parents=True, exist_ok=True)

        for name, body in (source_files or {"core.py": "def do_thing():\n    pass\n"}).items():
            (src / name).parent.mkdir(parents=True, exist_ok=True)
            (src / name).write_text(body, encoding="utf-8")
        for name, body in (
            test_files
            or {"test_ok.py": "from format_factory.demo import core\n\ndef test_a():\n    assert True\n"}
        ).items():
            (tests / name).write_text(body, encoding="utf-8")

        (reports / "evidence.json").write_text('{"result": "PASS"}', encoding="utf-8")
        (register_dir / "demo.yaml").write_text(
            yaml.safe_dump(
                {
                    "obligations": obligations
                    or [
                        {
                            "obligation_id": "OBL-1",
                            "capability_id": "DEMO-001",
                            "required_tests": ["One thing."],
                        }
                    ]
                }
            ),
            encoding="utf-8",
        )
        (maps / "demo.yaml").write_text(
            yaml.safe_dump(
                {
                    "execution_evidence": execution_evidence
                    or {
                        "path": "reports/evidence.json",
                        "result": "PASS",
                        "truth_boundary": "suite-level, non-promoting",
                    },
                    "capabilities": capabilities,
                }
            ),
            encoding="utf-8",
        )

        monkeypatch.setattr(builder, "REPO_ROOT", tmp_path)
        monkeypatch.setattr(builder, "MAP_DIR", maps)
        monkeypatch.setattr(builder, "REGISTER_DIR", register_dir)
        monkeypatch.setattr(builder, "EVIDENCE_DIR", evidence_out)
        return evidence_out / "demo.yaml"

    return make


def _ledger(path: Path) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8"))


# ── The shipped-namespace filter is not optional ───────────────────────────


def test_shadow_only_test_file_yields_missing_not_partial(demo) -> None:
    """A test importing only the legacy package is not evidence, however green."""
    out = demo(
        capabilities={"DEMO-001": {"modules": ["core.py"], "tests": ["test_shadow.py"]}},
        test_files={
            "test_shadow.py": "from demo.legacy import x\n\ndef test_a():\n    assert True\n"
        },
    )
    summary = builder.build("demo")
    entry = _ledger(out)["obligations"][0]
    assert summary["missing"] == 1
    assert entry["status"] == "missing"
    assert entry["positive_test_selectors"] == []
    assert any("NO SHIPPED-NAMESPACE" in m for m in entry["missing_behavior"])


def test_shadow_exclusion_is_recorded_when_other_evidence_exists(demo) -> None:
    """Dropping a file silently would hide why coverage is thinner than it looks."""
    out = demo(
        capabilities={
            "DEMO-001": {"modules": ["core.py"], "tests": ["test_ok.py", "test_shadow.py"]}
        },
        test_files={
            "test_ok.py": "from format_factory.demo import core\n\ndef test_a():\n    assert True\n",
            "test_shadow.py": "from demo.legacy import x\n\ndef test_b():\n    assert True\n",
        },
    )
    builder.build("demo")
    entry = _ledger(out)["obligations"][0]
    assert entry["status"] == "partial"
    assert any("test_shadow.py" in m for m in entry["missing_behavior"])


# ── Nothing is invented ────────────────────────────────────────────────────


def test_only_real_symbols_are_emitted(demo) -> None:
    out = demo(
        capabilities={"DEMO-001": {"modules": ["core.py"], "tests": ["test_ok.py"]}},
        source_files={"core.py": "class Real:\n    pass\n\ndef also_real():\n    pass\n"},
    )
    builder.build("demo")
    symbols = _ledger(out)["obligations"][0]["source_symbols"]
    assert any(s.endswith("::Real") for s in symbols)
    assert any(s.endswith("::also_real") for s in symbols)


def test_private_symbols_are_not_offered_as_public_evidence(demo) -> None:
    out = demo(
        capabilities={"DEMO-001": {"modules": ["core.py"], "tests": ["test_ok.py"]}},
        source_files={"core.py": "def _private():\n    pass\n\ndef public():\n    pass\n"},
    )
    builder.build("demo")
    symbols = _ledger(out)["obligations"][0]["source_symbols"]
    assert not any(s.endswith("::_private") for s in symbols)


def test_missing_module_fails_loudly(demo) -> None:
    demo(capabilities={"DEMO-001": {"modules": ["absent.py"], "tests": ["test_ok.py"]}})
    with pytest.raises(builder.LedgerError, match="mapped module does not exist"):
        builder.build("demo")


def test_missing_test_file_fails_loudly(demo) -> None:
    demo(capabilities={"DEMO-001": {"modules": ["core.py"], "tests": ["absent.py"]}})
    with pytest.raises(builder.LedgerError, match="mapped test file does not exist"):
        builder.build("demo")


# ── No capability may be silently dropped ──────────────────────────────────


def test_unmapped_capability_is_an_error_not_an_omission(demo) -> None:
    """Skipping it would shrink the denominator and flatter the format."""
    demo(
        capabilities={"DEMO-001": {"modules": ["core.py"], "tests": ["test_ok.py"]}},
        obligations=[
            {"obligation_id": "OBL-1", "capability_id": "DEMO-001"},
            {"obligation_id": "OBL-2", "capability_id": "DEMO-UNMAPPED"},
        ],
    )
    with pytest.raises(builder.LedgerError, match="unmapped capabilities"):
        builder.build("demo")


# ── Execution evidence must be declared, not guessed ───────────────────────


def test_absent_execution_evidence_declaration_is_an_error(demo) -> None:
    demo(
        capabilities={"DEMO-001": {"modules": ["core.py"], "tests": ["test_ok.py"]}},
        execution_evidence={"path": "reports/evidence.json"},
    )
    with pytest.raises(builder.LedgerError, match="must declare execution_evidence"):
        builder.build("demo")


def test_execution_evidence_pointing_nowhere_is_an_error(demo) -> None:
    demo(
        capabilities={"DEMO-001": {"modules": ["core.py"], "tests": ["test_ok.py"]}},
        execution_evidence={
            "path": "reports/does-not-exist.json",
            "result": "PASS",
            "truth_boundary": "x",
        },
    )
    with pytest.raises(builder.LedgerError, match="does not exist"):
        builder.build("demo")


def test_declared_result_is_carried_through_verbatim(demo) -> None:
    """A non-PASS result must survive: the reconciler compares it to the
    artifact, and softening it here would launder a failing suite."""
    out = demo(
        capabilities={"DEMO-001": {"modules": ["core.py"], "tests": ["test_ok.py"]}},
        execution_evidence={
            "path": "reports/evidence.json",
            "result": "PASS_WITH_KNOWN_ENVIRONMENT_FAILURES",
            "truth_boundary": "four known failures",
        },
    )
    builder.build("demo")
    evidence = _ledger(out)["execution_evidence"][0]
    assert evidence["expected_result"] == "PASS_WITH_KNOWN_ENVIRONMENT_FAILURES"
    assert evidence["truth_boundary"] == "four known failures"


# ── Status is never stronger than the evidence ─────────────────────────────


def test_no_obligation_is_ever_emitted_implemented(demo) -> None:
    """Mapping is not proving. `implemented` requires an audit a reader does."""
    out = demo(
        capabilities={"DEMO-001": {"modules": ["core.py"], "tests": ["test_ok.py"]}}
    )
    builder.build("demo")
    assert {e["status"] for e in _ledger(out)["obligations"]} <= {"partial", "missing"}


def test_declared_requirements_are_carried_into_missing_behavior(demo) -> None:
    out = demo(
        capabilities={"DEMO-001": {"modules": ["core.py"], "tests": ["test_ok.py"]}},
        obligations=[
            {
                "obligation_id": "OBL-1",
                "capability_id": "DEMO-001",
                "required_tests": ["A matrix by type and encoding."],
            }
        ],
    )
    builder.build("demo")
    entry = _ledger(out)["obligations"][0]
    assert any("type and encoding" in m for m in entry["missing_behavior"])


def test_dry_run_writes_nothing(demo) -> None:
    out = demo(
        capabilities={"DEMO-001": {"modules": ["core.py"], "tests": ["test_ok.py"]}}
    )
    builder.build("demo", dry_run=True)
    assert not out.exists()


# ── Against the real repository ────────────────────────────────────────────


def test_real_safetensors_ledger_rebuilds_identically() -> None:
    """Determinism: rebuilding must not churn the committed ledger's DATA.

    Compares parsed YAML, not raw text: safetensors carries a hand-curated
    `implemented` obligation (FI-075/FI-078) that this rebuild preserves by
    loading and re-emitting it, not by copying its original bytes. Loading
    a block-folded (`>-`) scalar and re-dumping it through yaml.safe_dump
    legitimately changes ITS formatting style (e.g. to a wrapped single-quoted
    scalar) without changing its content -- a real, expected, harmless
    consequence of preserving data as a Python object rather than as raw
    text, not a regression this test should fail on.
    """
    path = builder.EVIDENCE_DIR / "safetensors.yaml"
    original_text = path.read_text(encoding="utf-8")
    before = yaml.safe_load(original_text)
    try:
        builder.build("safetensors")
        after = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert after == before
    finally:
        # This test writes the real repository file (build() has no dry-run
        # override for a real EVIDENCE_DIR); restore its exact original bytes
        # so running the suite never leaves the working tree dirty.
        path.write_text(original_text, encoding="utf-8")
