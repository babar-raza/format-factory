"""TC-FCL-020-06/07: consumption proof + idempotency for the CSV vertical slice.

Proves the RC4 control: contract-originated gaps flow through the ACTIVE
supervisor chain (capability_feature_compiler.compile_gaps — the function
autonomous_cycle.py calls) into selectable work items, and the L14 compiler
exposes contract content via load_format_contract() (HO-011).
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

import canonical_io
import contract_compiler as cc
import gap_compiler
import contract_reconciler

GAP_LEDGER = REPO_ROOT / "reports" / "capability-layer" / "gap-ledger.json"


def _csv_contract_gaps() -> list[dict]:
    ledger = json.loads(GAP_LEDGER.read_text(encoding="utf-8"))
    return [g for g in ledger["gaps"] if str(g.get("gap_id", "")).startswith("GAP-FCL-CSV-")]


def test_contract_gaps_present_in_canonical_ledger():
    gaps = _csv_contract_gaps()
    assert gaps, "gap_compiler must have appended GAP-FCL-CSV-* records"
    for gap in gaps:
        assert gap["related_capability_id"].startswith("CSV-")
        assert gap["status"] == "open"
        assert "contract" in gap["notes"].lower()


def test_active_supervisor_chain_selects_contract_gap():
    """The consumption proof: capability_feature_compiler.compile_gaps (the
    function invoked by autonomous_cycle.py) must emit a work item for a
    contract-originated gap, with traceable gap_ledger_ref."""
    import capability_feature_compiler as cfc

    ledger = json.loads(GAP_LEDGER.read_text(encoding="utf-8"))
    items, _dedup = cfc.compile_gaps(ledger["gaps"], max_items=2000)
    contract_items = [
        i for i in items if str(i.get("gap_ledger_ref", "")).startswith("GAP-FCL-CSV-")
    ]
    assert contract_items, (
        "no contract-originated work item emerged from the active chain — "
        "L30 output is not being consumed (RC4 regression)"
    )
    item = contract_items[0]
    assert item["source"] == "gap_ledger"
    assert item["item_id"].startswith("WI-GAP-FCL-CSV-")
    assert "quarantine" not in item.get("lane", "")


def test_l14_loader_exposes_contract(tmp_path):
    import capability_compiler as l14

    doc = l14.load_format_contract("csv")
    assert doc is not None, "load_format_contract must return the compiled CSV contract"
    assert doc["contract_metadata"]["contract_id"] == "FC-CSV-V1"
    caps = {c["capability_id"] for c in doc["capabilities"]}
    assert "CSV-PARSE-001" in caps
    assert l14.load_format_contract("no_such_format") is None


def test_full_slice_second_run_is_idempotent():
    """Recompile + re-reconcile + re-gap: contract bytes identical, ledger
    gap set identical (no duplicates, no drift)."""
    _, doc1 = cc.compile_contract("csv")
    _, doc2 = cc.compile_contract("csv")
    assert canonical_io.canonical_dump(doc1) == canonical_io.canonical_dump(doc2)

    committed = (REPO_ROOT / "shared" / "format-contracts" / "csv.yaml").read_text(
        encoding="utf-8").replace("\r\n", "\n")
    assert committed == canonical_io.canonical_dump(doc1), (
        "committed CSV contract must equal recompiled output (V239/V240 invariant)"
    )

    before = {g["gap_id"]: g for g in _csv_contract_gaps()}
    recon = contract_reconciler.reconcile("csv")
    (contract_reconciler.REPORTS_DIR / "csv-reconciliation.json").write_text(
        json.dumps(recon, indent=2) + "\n", encoding="utf-8")
    gap_compiler.compile_gaps("csv")
    after = {g["gap_id"]: g for g in _csv_contract_gaps()}
    assert set(before) == set(after), "second gap-compile run must not add/drop gap ids"
    for gap_id in before:
        assert before[gap_id] == after[gap_id], f"gap {gap_id} drifted on rerun"
