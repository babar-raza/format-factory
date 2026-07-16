"""V238 focused tests: freshness/drift branch coverage (ISS-FCL-L1-004).

check_freshness() staleness is a digest mismatch, and input_digests are
recorded inside the contract body by design -- so a naive full-body
canonical_dump comparison would report DRIFT on every staleness, collapsing
the WARN (stale-but-unchanged) branch into dead code. These tests prove all
three V238 branches (PASS / WARN-stale-unchanged / FAIL-drifted) are real
and reachable, using one real compiled contract as the fresh baseline and a
monkeypatched recompile step to control the other two branches deterministically.
"""

from __future__ import annotations

import copy
import sys
from pathlib import Path

import pytest

import contract_compiler as cc
import contract_validator as cv

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
# append (not insert(0, ...)): tools/supervisor/ and tools/format_contract/ both
# define a module named quality_scorer.py with different APIs -- inserting at
# position 0 would shadow format_contract's copy for every later-collected test
# in the same pytest session (proven: broke test_quality_oracle.py when this
# used insert(0, ...)).
sys.path.append(str(REPO_ROOT / "tools" / "supervisor"))

import governance_validators_format_contract as g  # noqa: E402


@pytest.fixture
def fresh_csv_doc():
    _, doc = cc.compile_contract("csv")
    assert doc is not None
    return doc


def test_drift_comparable_strips_only_input_digests(fresh_csv_doc):
    stripped = g._drift_comparable(fresh_csv_doc)
    assert "input_digests" not in stripped["contract_metadata"]
    assert "input_digests" in fresh_csv_doc["contract_metadata"]
    assert stripped["capabilities"] == fresh_csv_doc["capabilities"]


def _patch_one_contract(monkeypatch, tmp_path, fmt, stale_doc, recompiled_doc):
    fake_path = tmp_path / f"{fmt}.yaml"
    fake_path.write_text("placeholder", encoding="utf-8")
    monkeypatch.setattr(g, "_contracts", lambda repo_root: [fake_path])

    import canonical_io
    monkeypatch.setattr(canonical_io, "load_yaml", lambda p: stale_doc if p == fake_path else None)
    monkeypatch.setattr(cc, "compile_contract", lambda f: ("ok", recompiled_doc))


def test_v238_pass_when_fresh(monkeypatch, tmp_path, fresh_csv_doc):
    _patch_one_contract(monkeypatch, tmp_path, "csv", fresh_csv_doc, fresh_csv_doc)
    res = g.validate_contract_freshness({}, REPO_ROOT)
    assert res["result"] == "PASS"
    assert res["blocks_sprint"] is False


def test_v238_warn_when_stale_but_content_unchanged(monkeypatch, tmp_path, fresh_csv_doc):
    stale = copy.deepcopy(fresh_csv_doc)
    stale["contract_metadata"]["input_digests"]["sal_facts_sha256"] = "0" * 64
    assert cv.check_freshness(stale)["result"] == "FAIL"

    recompiled = copy.deepcopy(fresh_csv_doc)
    _patch_one_contract(monkeypatch, tmp_path, "csv", stale, recompiled)

    res = g.validate_contract_freshness({}, REPO_ROOT)
    assert res["result"] == "WARN"
    assert res["blocks_sprint"] is False
    assert "content unchanged" in res["items"][0]["issue"]


def test_v238_fails_when_stale_and_drifted(monkeypatch, tmp_path, fresh_csv_doc):
    stale = copy.deepcopy(fresh_csv_doc)
    stale["contract_metadata"]["input_digests"]["sal_facts_sha256"] = "0" * 64
    assert cv.check_freshness(stale)["result"] == "FAIL"

    recompiled = copy.deepcopy(fresh_csv_doc)
    recompiled["capabilities"] = recompiled["capabilities"][:-1]
    _patch_one_contract(monkeypatch, tmp_path, "csv", stale, recompiled)

    res = g.validate_contract_freshness({}, REPO_ROOT)
    assert res["result"] == "FAIL"
    assert res["blocks_sprint"] is True
    assert "DRIFTED" in res["items"][0]["issue"]
