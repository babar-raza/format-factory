"""TC-FCL-040: quality scorer, reference comparator, family-pack integrity,
and adversarial fixtures (schema-dump, parser-only, invented refs,
over-engineered simple format)."""

from __future__ import annotations

import copy

import pytest

import contract_compiler as cc
import contract_validator as cv
import quality_scorer as qs
import reference_comparator as rc
import stores

ALL_FAMILIES = [
    "tabular_text", "config_data", "xml_business", "xml_localization",
    "executable_document", "typed_graph", "scientific_raster",
    "archive_container", "image_raster", "xml_document",
]


# ---------------------------------------------------------------------------
# family-pack integrity (regression for the YAML comma-truncation defect)
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("family", ALL_FAMILIES)
def test_family_pack_loads_and_is_untruncated(family):
    pack = stores.load_family_pack(family)
    assert pack.get("domains"), f"{family}: pack must define domains"
    for dom in pack["domains"]:
        for item in dom.get("baseline_behavior", []):
            assert set(item.keys()) == {"id", "text"}, (
                f"{family}/{dom['domain']}: baseline item has junk keys "
                f"{set(item.keys())} — comma-truncation defect regressed"
            )
            assert len(item["text"]) >= 40, f"{family}/{dom['domain']}: suspiciously short baseline"
    for layer in pack.get("validation_layers", []):
        assert set(layer.keys()) == {"layer", "description"}


def test_every_mapped_format_has_a_pack():
    family_map = stores.load_family_map()
    for fmt, family in family_map.items():
        assert stores.family_pack_path(family).is_file(), f"{fmt} -> {family}: pack missing"


# ---------------------------------------------------------------------------
# quality scorer (determinism + honesty)
# ---------------------------------------------------------------------------

def test_scorer_is_deterministic():
    _, doc = cc.compile_contract("csv")
    r1, r2 = qs.score_contract(doc), qs.score_contract(doc)
    assert r1 == r2


def test_scorer_penalizes_missing_security():
    _, doc = cc.compile_contract("csv")
    bad = copy.deepcopy(doc)
    bad["security_contract"] = {"attack_surfaces": [], "safe_defaults": [], "limits": []}
    bad["capabilities"] = [c for c in bad["capabilities"] if c["category"] != "security"]
    assert qs.score_contract(bad)["score"] < qs.score_contract(doc)["score"]


# ---------------------------------------------------------------------------
# adversarial fixtures
# ---------------------------------------------------------------------------

def test_adversarial_schema_dump_is_rejected():
    """A schema dump disguised as a contract: element names as 'requirements'."""
    _, doc = cc.compile_contract("csv")
    bad = copy.deepcopy(doc)
    for cap in bad["capabilities"]:
        cap["required_behavior"] = ["field element", "record element", "header element"]
    report = cv.validate_contract(bad, skip={"freshness"})
    failing = {c["check"] for c in report["checks"] if c["result"] == "FAIL"}
    assert failing & {"schema", "shallow_language"}, (
        "element-name dumps must fail schema minLength or shallow-language checks"
    )


def test_adversarial_parser_only_contract_is_rejected():
    """Parser-only 'complete' library: family adequacy must fail on missing domains."""
    _, doc = cc.compile_contract("csv")
    bad = copy.deepcopy(doc)
    keep = {"CSV-PARSE-001", "CSV-ENCODING-001"}
    bad["capabilities"] = [c for c in bad["capabilities"] if c["capability_id"] in keep]
    bad["coverage_map"] = [m for m in bad["coverage_map"] if m["capability_id"] in keep]
    assert cv.check_family_adequacy(bad)["result"] == "FAIL"


def test_adversarial_invented_finding_reference_is_rejected():
    """Plausible-looking RF- reference with no committed finding behind it."""
    _, doc = cc.compile_contract("csv")
    bad = copy.deepcopy(doc)
    bad["capabilities"][0]["provenance"].append("RF-CSV-00042")
    assert cv.check_provenance(bad)["result"] == "FAIL"


def test_adversarial_overengineered_simple_format_is_rejected():
    """Simplicity budget: a simple format bloated past its family cap fails."""
    _, doc = cc.compile_contract("csv")
    bad = copy.deepcopy(doc)
    template = copy.deepcopy(bad["capabilities"][0])
    for i in range(25):
        clone = copy.deepcopy(template)
        clone["capability_id"] = f"CSV-BLOAT-{i + 1:03d}"
        bad["capabilities"].append(clone)
    assert cv.check_family_adequacy(bad)["result"] == "FAIL"


# ---------------------------------------------------------------------------
# reference comparator (oracle integrity + honest verdicts)
# ---------------------------------------------------------------------------

def test_reference_oracle_hash_is_verified():
    policy, ref = rc._load_reference()
    assert policy["role"] == "comparison_oracle_only"
    assert set(ref["formats"].keys()) == {"UBL", "XLIFF", "IPYNB", "MTLX", "NRRD"}


def test_reference_comparator_refuses_on_hash_mismatch(monkeypatch):
    import canonical_io
    monkeypatch.setattr(canonical_io, "digest_file", lambda p: "0" * 64)
    monkeypatch.setattr(rc, "digest_file", lambda p: "0" * 64)
    with pytest.raises(stores.StoreError, match="hash mismatch"):
        rc._load_reference()


def test_reference_comparator_rejects_uncovered_format():
    with pytest.raises(stores.StoreError, match="not covered"):
        rc.compare("csv")
