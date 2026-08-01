"""Exact obligation reconciliation is complete, explicit, and non-promoting."""

# pyright: reportMissingImports=false

from __future__ import annotations

from copy import deepcopy
import json
from pathlib import Path

import contract_reconciler
import pytest
import yaml


REPO_ROOT = Path(__file__).resolve().parents[2]


def _write_json(path: Path, value: object) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    return path


def test_exact_reconciliation_resolves_rows_and_is_deterministic(
    tmp_path: Path,
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    assert contract_reconciler.__file__ is not None
    schema_source = (
        Path(contract_reconciler.__file__).resolve().parents[2]
        / "schemas/format-contracts/implementation-evidence.schema.json"
    )
    _write_json(
        tmp_path / "schemas/format-contracts/implementation-evidence.schema.json",
        json.loads(schema_source.read_text(encoding="utf-8")),
    )
    source = tmp_path / "src/python/nrrd/pkg.py"
    source.parent.mkdir(parents=True)
    source.write_text("def parse_header():\n    return True\n", encoding="utf-8")
    test_file = tmp_path / "tests/python/nrrd/test_header.py"
    test_file.parent.mkdir(parents=True)
    test_file.write_text(
        "def test_header_roundtrip():\n    assert True\n",
        encoding="utf-8",
    )
    execution = _write_json(
        tmp_path / "reports/execution.json",
        {"result": "PASS", "source_checkpoint": "abc123", "tests_run": ["nrrd suite"]},
    )
    contract = _write_json(
        tmp_path / "shared/format-contracts/nrrd.yaml",
        {
            "contract_metadata": {"contract_id": "FC-NRRD-V1", "input_digests": {}},
            "capabilities": [{"capability_id": "NRRD-HEADER-001"}],
        },
    )
    obligations = _write_json(
        tmp_path / "plans/strategic/ff6/obligations/nrrd.yaml",
        {
            "schema": "ff6/format-obligations@2",
            "format_id": "nrrd",
            "obligation_count": 1,
            "obligations": [
                {
                    "obligation_id": "SAL-NRRD-OBL-0001",
                    "format_id": "nrrd",
                    "capability_id": "NRRD-HEADER-001",
                    "kind": "positive",
                }
            ],
        },
    )
    mapping = _write_json(
        tmp_path / "shared/format-contracts/implementation-evidence/nrrd.yaml",
        {
            "schema": "format-contracts/implementation-evidence@1",
            "format_id": "nrrd",
            "visibility": "generated",
            "generated_by": "codex",
            "execution_evidence": [
                {
                    "evidence_id": "NRRD-R1",
                    "path": execution.relative_to(tmp_path).as_posix(),
                    "expected_result": "PASS",
                    "granularity": "suite",
                }
            ],
            "obligations": [
                {
                    "obligation_id": "SAL-NRRD-OBL-0001",
                    "capability_id": "NRRD-HEADER-001",
                    "status": "implemented",
                    "source_symbols": [
                        "src/python/nrrd/pkg.py::parse_header",
                    ],
                    "positive_test_selectors": [
                        "tests/python/nrrd/test_header.py::test_header_roundtrip",
                    ],
                    "negative_test_selectors": [],
                    "execution_evidence_ids": ["NRRD-R1"],
                    "implemented_behavior": ["Parses the header."],
                    "missing_behavior": [],
                    "proof_requirements": {
                        "positive": ["Installed-wheel roundtrip."],
                        "negative": ["Malformed-header rejection."],
                    },
                }
            ],
        },
    )

    first = contract_reconciler.reconcile_obligations(
        "nrrd",
        obligation_path=obligations,
        evidence_path=mapping,
        contract_path=contract,
        repo_root=tmp_path,
    )
    second = contract_reconciler.reconcile_obligations(
        "nrrd",
        obligation_path=obligations,
        evidence_path=mapping,
        contract_path=contract,
        repo_root=tmp_path,
    )

    assert first == second
    assert first["summary"] == {
        "total": 1,
        "by_status": {"implemented": 1},
        "unresolved": 0,
    }
    assert first["obligations"][0]["proof_status"] == "SUPPORTED_NONPROMOTING"
    assert first["promotion_effect"] == "none"
    assert first["input_digests"]["implementation_evidence"]

    reports = tmp_path / "reports/format-contract-layer"
    monkeypatch.setattr(contract_reconciler.stores, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(contract_reconciler, "REPORTS_DIR", reports)
    assert contract_reconciler.main(
        [
            "--format-id",
            "nrrd",
            "--exact-obligations",
            "--obligation-register",
            str(obligations),
            "--implementation-evidence",
            str(mapping),
        ]
    ) == 0
    written = json.loads(
        (reports / "nrrd-obligation-reconciliation.json").read_text(encoding="utf-8")
    )
    assert written == first

    source.write_text("def parse_header():\n    return True\n# changed\n", encoding="utf-8")
    changed = contract_reconciler.reconcile_obligations(
        "nrrd",
        obligation_path=obligations,
        evidence_path=mapping,
        contract_path=contract,
        repo_root=tmp_path,
    )
    source_key = "src/python/nrrd/pkg.py"
    assert changed["referenced_input_digests"][source_key] != first[
        "referenced_input_digests"
    ][source_key]

    invalid = json.loads(mapping.read_text(encoding="utf-8"))
    del invalid["visibility"]
    _write_json(mapping, invalid)
    with pytest.raises(contract_reconciler.stores.StoreError, match="visibility"):
        contract_reconciler.reconcile_obligations(
            "nrrd",
            obligation_path=obligations,
            evidence_path=mapping,
            contract_path=contract,
            repo_root=tmp_path,
        )


@pytest.mark.parametrize(
    ("case", "message"),
    [
        ("missing_row", "set mismatch"),
        ("duplicate_row", "duplicate obligation"),
        ("foreign_format", "foreign-format"),
        ("capability_mismatch", "capability mismatch"),
        ("bad_source", "source symbol does not exist"),
        ("bad_test", "test symbol does not exist"),
        ("inconsistent_status", "implemented requires"),
        ("false_execution_result", "declared result"),
    ],
)
def test_exact_reconciliation_fails_closed(case: str, message: str, tmp_path: Path) -> None:
    mapping_path = REPO_ROOT / "shared/format-contracts/implementation-evidence/nrrd.yaml"
    mapping = yaml.safe_load(mapping_path.read_text(encoding="utf-8"))
    assert isinstance(mapping, dict)
    candidate = deepcopy(mapping)

    if case == "missing_row":
        candidate["obligations"].pop()
    elif case == "duplicate_row":
        candidate["obligations"].append(deepcopy(candidate["obligations"][0]))
    elif case == "foreign_format":
        candidate["format_id"] = "ipynb"
    elif case == "capability_mismatch":
        candidate["obligations"][0]["capability_id"] = "NRRD-NOT-REAL-001"
    elif case == "bad_source":
        candidate["obligations"][0]["source_symbols"] = [
            "src/python/nrrd/src/format_factory/nrrd/model/document.py::NotARealSymbol"
        ]
    elif case == "bad_test":
        candidate["obligations"][0]["positive_test_selectors"] = [
            "tests/python/nrrd/test_production_namespace.py::test_not_real"
        ]
    elif case == "inconsistent_status":
        implemented = next(
            row for row in candidate["obligations"] if row["status"] == "implemented"
        )
        implemented["missing_behavior"] = ["contradiction"]
    elif case == "false_execution_result":
        candidate["execution_evidence"][0]["expected_result"] = "FAIL"
    else:  # pragma: no cover - the parameter list is closed above
        raise AssertionError(case)

    candidate_path = _write_json(tmp_path / "candidate.yaml", candidate)
    with pytest.raises(contract_reconciler.stores.StoreError, match=message):
        contract_reconciler.reconcile_obligations(
            "nrrd",
            obligation_path=REPO_ROOT / "plans/strategic/ff6/obligations/nrrd.yaml",
            evidence_path=candidate_path,
            contract_path=REPO_ROOT / "shared/format-contracts/nrrd.yaml",
            repo_root=REPO_ROOT,
        )
