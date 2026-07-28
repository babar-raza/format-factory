"""TC-FCL-010 focused tests: schema, canonical serializer, readiness gate,
compiler idempotency, validator checks, denylist, registry accessor.

Read-only against committed stores (csv/ubl SAL facts); all writes go to
tmp_path via monkeypatched module paths.
"""

from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

import canonical_io
import contract_compiler as cc
import contract_registry
import contract_validator as cv
import stores

REPO_ROOT = Path(__file__).resolve().parent.parent.parent


# ---------------------------------------------------------------------------
# canonical_io (TC-FCL-010-02)
# ---------------------------------------------------------------------------

def test_canonical_dump_is_byte_stable():
    data = {"b": [3, 1, 2], "a": {"y": 1, "x": [{"k": "v", "a": 1}]}}
    assert canonical_io.canonical_dump(data) == canonical_io.canonical_dump(data)


def test_canonical_dump_key_order_independent():
    d1 = {"alpha": 1, "beta": {"c": 1, "d": 2}}
    d2 = {"beta": {"d": 2, "c": 1}, "alpha": 1}
    assert canonical_io.canonical_dump(d1) == canonical_io.canonical_dump(d2)


def test_digest_normalizes_crlf(tmp_path):
    lf = tmp_path / "lf.yaml"
    crlf = tmp_path / "crlf.yaml"
    lf.write_bytes(b"a: 1\nb: 2\n")
    crlf.write_bytes(b"a: 1\r\nb: 2\r\n")
    assert canonical_io.digest_file(lf) == canonical_io.digest_file(crlf)


def test_digest_missing_file_is_empty_digest(tmp_path):
    import hashlib
    assert canonical_io.digest_file(tmp_path / "absent.yaml") == hashlib.sha256(b"").hexdigest()


# ---------------------------------------------------------------------------
# readiness gate (TC-FCL-010-05) — the RC1 control
# ---------------------------------------------------------------------------

def test_csv_is_ready():
    report = cc.readiness(cc.classify("csv"))
    assert report["ready"] is True
    assert report["score"] >= report["threshold"]


def test_thin_sal_store_is_blocked(tmp_path, monkeypatch):
    """The RC1 invariant: a thin SAL store can NEVER pass a complex family's
    readiness gate. Uses a synthetic 3-fact store so the invariant stays
    testable after real pilot stores are seeded (they were seeded in
    TC-FCL-050 via the governed intake -> ingest-spec-sal path)."""
    thin = {
        "format_id": "ubl", "schema_version": "1.0", "canonical": True,
        "facts": [
            {"fact_id": f"SAL-UBL-{i:05d}", "qname": f"FACT-UBL-{i}",
             "element_qname": "ubl:doc",
             "claim": "A document is rooted at an element in a namespace with components referenced externally",
             "section": "s", "authority": "a", "source": "structural_fact_manual",
             "fact_status": "verified"}
            for i in (1, 2, 3)
        ],
    }
    sal_dir = tmp_path / "sal"
    sal_dir.mkdir()
    canonical_io.canonical_write(sal_dir / "ubl.yaml", thin)
    monkeypatch.setattr(stores, "SAL_FACTS_DIR", sal_dir)
    report = cc.readiness(cc.classify("ubl"))
    assert report["ready"] is False, "3 facts must never pass the xml_business gate"
    assert report["missing_categories"], "blocked report must name missing categories"


def test_weighted_score_cannot_mask_a_missing_required_category():
    context = {
        "format_id": "synthetic",
        "family": "synthetic_family",
        "sal": {
            "facts": [
                {
                    "fact_id": "SAL-SYNTHETIC-00001",
                    "claim": "root document structure",
                }
            ]
        },
        "research": {"findings": []},
        "categories_policy": {
            "categories": {
                "structure_roots": {
                    "match_keywords": ["root"],
                    "min_facts": 1,
                },
                "syntax_encoding": {
                    "match_keywords": ["encoding"],
                    "min_facts": 1,
                },
            },
            "families": {
                "synthetic_family": {
                    "threshold": 0.8,
                    "required_categories": [
                        "structure_roots",
                        "syntax_encoding",
                    ],
                    "weights": {
                        "structure_roots": 0.9,
                        "syntax_encoding": 0.1,
                    },
                }
            },
        },
    }

    report = cc.readiness(context)

    assert report["score"] == 0.9
    assert report["score"] >= report["threshold"]
    assert report["missing_categories"] == ["syntax_encoding"]
    assert report["ready"] is False


@pytest.mark.parametrize("fmt", ["ubl", "xliff", "ipynb", "mtlx", "nrrd"])
def test_seeded_pilot_stores_are_ready(fmt):
    """Post-TC-FCL-050 state: pilots were seeded through the governed research
    intake + SAL candidate path and must now pass their family gates."""
    report = cc.readiness(cc.classify(fmt))
    assert report["ready"] is True, (
        f"{fmt} seeded store regressed below gate "
        f"(score {report['score']}, threshold {report['threshold']})"
    )


# ---------------------------------------------------------------------------
# compiler determinism (TC-FCL-010-07/08)
# ---------------------------------------------------------------------------

def test_compile_csv_idempotent():
    _, doc1 = cc.compile_contract("csv")
    _, doc2 = cc.compile_contract("csv")
    assert doc1, "csv must compile (readiness passed)"
    assert canonical_io.canonical_dump(doc1) == canonical_io.canonical_dump(doc2)


def test_safetensors_contract_respects_expanded_family_exclusions():
    report, document = cc.compile_contract("safetensors")
    assert report["ready"] is True
    text = canonical_io.canonical_dump(document).casefold()
    for excluded in (
        "detached",
        "compression",
        "spatial",
        "raster",
        "line ending",
        "comment",
        "magic",
    ):
        assert excluded not in text, (
            f"compiled SafeTensors contract leaked excluded concept {excluded!r}"
        )
    assert document["security_contract"]["limits"]
    assert all(
        "tensor" in limit.casefold() or "payload" in limit.casefold()
        for limit in document["security_contract"]["limits"]
    )
    assert cv.check_schema(document)["result"] == "PASS"
    interoperability = [
        capability
        for capability in document["capabilities"]
        if capability["category"] == "interoperability"
    ]
    assert len(interoperability) == 1


def test_schema_still_rejects_unknown_capability_category():
    _, document = cc.compile_contract("safetensors")
    bad = copy.deepcopy(document)
    bad["capabilities"][0]["category"] = "convenient_but_unregistered"
    assert cv.check_schema(bad)["result"] == "FAIL"


def test_compiled_csv_has_traceable_capabilities():
    _, doc = cc.compile_contract("csv")
    assert len(doc["capabilities"]) >= 8
    for cap in doc["capabilities"]:
        assert cap["provenance"], f"{cap['capability_id']} must cite provenance"
        assert cap["depth_required"] >= 2
    ids = [c["capability_id"] for c in doc["capabilities"]]
    assert ids == sorted(ids), "capabilities must be ID-ordered for determinism"


def test_acquired_research_authority_replaces_synthetic_url_record(
    monkeypatch,
):
    original = stores.load_research

    def acquired(format_id: str) -> dict:
        document = copy.deepcopy(original(format_id))
        document["source_records"].insert(
            0,
            {
                "source_id": "SRC-CSV-099",
                "title": "Pinned authority",
                "authority_class": "AUTHORITATIVE",
                "canonical_url": "https://example.invalid/pinned",
                "content_hash": "a" * 64,
                "acquisition_status": "ACQUIRED",
            },
        )
        return document

    monkeypatch.setattr(stores, "load_research", acquired)
    _, document = cc.compile_contract("csv")
    assert any(
        source["source_id"] == "SRC-CSV-099"
        for source in document["authoritative_sources"]
    )
    assert all(
        source["source_id"] != "SRC-CSV-001"
        for source in document["authoritative_sources"]
    )


def test_contract_body_has_no_timestamps():
    _, doc = cc.compile_contract("csv")
    text = canonical_io.canonical_dump(doc).lower()
    for token in ("generated_at", "timestamp", "updated_at"):
        assert token not in text, f"canonical body must not carry '{token}'"


# ---------------------------------------------------------------------------
# schema + validator (TC-FCL-010-01/09)
# ---------------------------------------------------------------------------

def test_schema_accepts_compiled_csv():
    _, doc = cc.compile_contract("csv")
    assert cv.check_schema(doc)["result"] == "PASS", cv.check_schema(doc)["items"]


def test_validator_full_pass_on_compiled_csv():
    _, doc = cc.compile_contract("csv")
    report = cv.validate_contract(doc)
    failing = [c for c in report["checks"] if c["result"] != "PASS"]
    assert report["verdict"] == "PASS", failing


def test_schema_rejects_capability_without_provenance():
    _, doc = cc.compile_contract("csv")
    bad = copy.deepcopy(doc)
    bad["capabilities"][0]["provenance"] = []
    assert cv.check_schema(bad)["result"] == "FAIL"


def test_schema_accepts_content_stable_sal_provenance_ids():
    _, doc = cc.compile_contract("csv")
    doc["capabilities"][0]["provenance"].append(
        "SAL-CSV-0123456789ABCDEF"
    )
    assert cv.check_schema(doc)["result"] == "PASS"


def test_validator_rejects_duplicate_ids():
    _, doc = cc.compile_contract("csv")
    bad = copy.deepcopy(doc)
    bad["capabilities"].append(copy.deepcopy(bad["capabilities"][0]))
    assert cv.check_duplicate_ids(bad)["result"] == "FAIL"


def test_validator_rejects_shallow_phrase():
    _, doc = cc.compile_contract("csv")
    bad = copy.deepcopy(doc)
    bad["capabilities"][0]["required_behavior"].append("Support the format")
    assert cv.check_shallow_language(bad)["result"] == "FAIL"


def test_validator_rejects_unresolvable_provenance():
    _, doc = cc.compile_contract("csv")
    bad = copy.deepcopy(doc)
    bad["capabilities"][0]["provenance"].append("SAL-CSV-99999")
    assert cv.check_provenance(bad)["result"] == "FAIL"


def test_validator_rejects_depth_below_floor():
    _, doc = cc.compile_contract("csv")
    bad = copy.deepcopy(doc)
    validate_caps = [c for c in bad["capabilities"] if c["category"] == "validate"]
    assert validate_caps
    validate_caps[0]["depth_required"] = 2
    assert cv.check_depth(bad)["result"] == "FAIL"


def test_validator_rejects_must_without_tests():
    _, doc = cc.compile_contract("csv")
    bad = copy.deepcopy(doc)
    must_caps = [c for c in bad["capabilities"] if c["level"] == "MUST"]
    must_caps[0]["required_tests"] = []
    assert cv.check_test_gate(bad)["result"] == "FAIL"


def test_freshness_detects_input_drift():
    _, doc = cc.compile_contract("csv")
    bad = copy.deepcopy(doc)
    bad["contract_metadata"]["input_digests"]["sal_facts_sha256"] = "0" * 64
    assert cv.check_freshness(bad)["result"] == "FAIL"


def test_family_adequacy_detects_missing_domain():
    _, doc = cc.compile_contract("csv")
    bad = copy.deepcopy(doc)
    bad["capabilities"] = [c for c in bad["capabilities"] if "VALIDATE" not in c["capability_id"]]
    bad["coverage_map"] = [m for m in bad["coverage_map"] if "VALIDATE" not in m["capability_id"]]
    assert cv.check_family_adequacy(bad)["result"] == "FAIL"


# ---------------------------------------------------------------------------
# anti-copying denylist (DEC-038)
# ---------------------------------------------------------------------------

def test_reference_contract_path_is_denylisted():
    with pytest.raises(stores.StoreError):
        stores._check_denylist(
            REPO_ROOT / "plans" / "from_chat"
            / "format_library_feature_contracts_ubl_xliff_ipynb_mtlx_nrrd.yaml"
        )


# ---------------------------------------------------------------------------
# volatile registry accessor (TC-FCL-010-03)
# ---------------------------------------------------------------------------

def test_registry_roundtrip(tmp_path, monkeypatch):
    monkeypatch.setattr(contract_registry, "REGISTRY_PATH", tmp_path / "reg.yaml")
    contract_registry.update_entry("csv", state="COMPILED", capability_count=9)
    contract_registry.update_entry("csv", state="VALIDATED")
    entry = contract_registry.get_entry("csv")
    assert entry["state"] == "VALIDATED"
    assert entry["capability_count"] == 9
    assert "updated_at" in entry  # volatile store carries timestamps by design


def test_registry_rejects_invalid_state(tmp_path, monkeypatch):
    monkeypatch.setattr(contract_registry, "REGISTRY_PATH", tmp_path / "reg.yaml")
    with pytest.raises(ValueError):
        contract_registry.update_entry("csv", state="NOT_A_STATE")


def test_successful_compile_clears_stale_missing_categories(tmp_path, monkeypatch):
    captured: dict[str, object] = {}
    report = {
        "ready": True,
        "score": 1.0,
        "threshold": 0.8,
        "missing_categories": [],
    }
    document = {
        "capabilities": [],
        "contract_metadata": {"input_digests": {}},
    }

    monkeypatch.setattr(cc, "compile_contract", lambda _format_id: (report, document))
    monkeypatch.setattr(stores, "REPO_ROOT", tmp_path)
    monkeypatch.setattr(stores, "contract_path", lambda _format_id: tmp_path / "contract.yaml")
    monkeypatch.setattr(cc, "canonical_write", lambda _path, _document: None)
    monkeypatch.setattr(
        contract_registry,
        "update_entry",
        lambda _format_id, **fields: captured.update(fields),
    )

    assert cc.main(["--format-id", "synthetic"]) == 0
    assert captured["state"] == "COMPILED"
    assert captured["missing_categories"] == []
