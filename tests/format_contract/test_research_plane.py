"""TC-FCL-030: research-plane tests — review gate, source closure, normative
routing, and findings-to-contract flow."""

from __future__ import annotations

import copy
from pathlib import Path

import pytest

import contract_compiler as cc
import research_intake as ri
import source_researcher as sr
import stores
from canonical_io import canonical_write, load_yaml

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


def _draft_base() -> dict:
    return {
        "format_id": "csv",
        "source_records": [{
            "source_id": "SRC-CSV-002",
            "title": "IETF RFC 4180",
            "authority_class": "AUTHORITATIVE",
            "acquisition_status": "URL_ONLY",
        }],
        "findings": [{
            "finding_id": "RF-CSV-00099",
            "kind": "product_requirement",
            "capability_domain": "PARSE",
            "requirement": "Provide a bounded-memory streaming parse mode for very large files with identical row output.",
            "source_ids": ["SRC-CSV-002"],
            "authority_class": "PRODUCT_REQUIREMENT",
            "review": {"verdict": "ACCEPTED", "reviewer": "test-fixture"},
        }],
        "sal_candidates": [],
    }


def _run_intake(tmp_path, monkeypatch, draft: dict) -> dict:
    """Run intake against tmp copies so the committed CSV store is untouched."""
    monkeypatch.setattr(stores, "RESEARCH_DIR", tmp_path / "research")
    monkeypatch.setattr(ri, "SAL_CANDIDATES_DIR", tmp_path / "sal-candidates")
    draft_path = tmp_path / "csv-draft.yaml"
    canonical_write(draft_path, draft)
    return ri.intake("csv", draft_path)


def test_intake_accepts_reviewed_finding(tmp_path, monkeypatch):
    result = _run_intake(tmp_path, monkeypatch, _draft_base())
    assert result["committed_findings"] == 1


def test_intake_refuses_pending_review(tmp_path, monkeypatch):
    draft = _draft_base()
    draft["findings"][0]["review"]["verdict"] = "PENDING"
    with pytest.raises(stores.StoreError, match="review gate refused"):
        _run_intake(tmp_path, monkeypatch, draft)


def test_intake_refuses_unknown_source(tmp_path, monkeypatch):
    draft = _draft_base()
    draft["findings"][0]["source_ids"] = ["SRC-CSV-999"]
    with pytest.raises(stores.StoreError, match="unknown source_id|validation failed"):
        _run_intake(tmp_path, monkeypatch, draft)


def test_intake_refuses_unsourced_finding(tmp_path, monkeypatch):
    draft = _draft_base()
    draft["findings"][0]["source_ids"] = []
    with pytest.raises(stores.StoreError):
        _run_intake(tmp_path, monkeypatch, draft)


def test_intake_routes_normative_claims_away_from_research_store(tmp_path, monkeypatch):
    draft = _draft_base()
    draft["findings"][0]["requirement"] = (
        "The specification defines that each record ends with CRLF and parsers must honor it."
    )
    with pytest.raises(stores.StoreError, match="normative"):
        _run_intake(tmp_path, monkeypatch, draft)


def test_sal_candidates_go_to_queue_not_sal_store(tmp_path, monkeypatch):
    draft = _draft_base()
    draft["sal_candidates"] = [{
        "claim": "A CSV header line, when present, carries the same field count as data records",
        "element_qname": "csv:header",
        "section": "RFC 4180 section 2",
        "authority": "IETF RFC 4180",
    }]
    result = _run_intake(tmp_path, monkeypatch, draft)
    assert result["sal_candidates_queued"] == 1
    queue = load_yaml(tmp_path / "sal-candidates" / "csv.yaml")
    assert "ingest-spec-sal" in queue["route"]
    assert len(queue["candidates"]) == 1


def test_committed_csv_research_store_is_schema_valid():
    store = load_yaml(stores.research_path("csv"))
    errors = ri._validate_store_shape(store)
    assert not errors, errors


def test_findings_reach_compiled_contract_provenance():
    _, doc = cc.compile_contract("csv")
    parse_cap = next(c for c in doc["capabilities"] if c["capability_id"] == "CSV-PARSE-001")
    assert "RF-CSV-00001" in parse_cap["provenance"]
    assert any("streaming row iterator" in b.lower() or "bounded memory" in b.lower()
               for b in parse_cap["required_behavior"])
    assert "read_operations" in doc.get("public_api_contract", {})


def test_researcher_upgrades_existing_url_only_authority(
    tmp_path, monkeypatch
):
    monkeypatch.setattr(sr, "DRAFTS_DIR", tmp_path / "drafts")
    monkeypatch.setattr(sr, "ACQUIRED_DIR", tmp_path / "acquired")
    monkeypatch.setattr(
        stores,
        "load_format_registry_entry",
        lambda _format_id: {
            "display_name": "CSV",
            "spec_body": "IETF",
            "spec_version": "4180",
            "spec_url": "https://example.invalid/old",
        },
    )
    monkeypatch.setattr(
        stores,
        "load_research",
        lambda _format_id: {
            "source_records": [
                {
                    "source_id": "SRC-CSV-002",
                    "title": "RFC",
                    "authority_class": "AUTHORITATIVE",
                    "canonical_url": "https://example.invalid/old",
                    "acquisition_status": "URL_ONLY",
                }
            ],
            "findings": _draft_base()["findings"],
        },
    )

    def fake_fetch(_url: str, destination: Path) -> str:
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(b"authority")
        return "a" * 64

    monkeypatch.setattr(sr, "_fetch", fake_fetch)
    result = sr.research_sources(
        "csv",
        True,
        source_id="SRC-CSV-002",
        source_url="https://example.invalid/pinned",
        source_version="commit-123",
        prepare_intake=True,
    )
    draft = load_yaml(Path(result["intake_draft"]))
    source = draft["source_records"][0]
    assert source["acquisition_status"] == "ACQUIRED"
    assert source["content_hash"] == "a" * 64
    assert source["version"] == "commit-123"
    assert draft["findings"] == _draft_base()["findings"]
