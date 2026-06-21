"""
TC-CHAIN-ODF-001: Verify FODT SPEC→SAL→QNAME chain.

Tests that:
1. FODT spec requirements reference text:p as paragraph QName
2. FODT SAL facts exist in sal-facts-latest.json (non-synthetic)
3. Spec/Text/Paragraph.cs contains SpecQName = "text:p" and SpecFactRef = "FACT-FODT-003"
"""
import json
import re
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent


# ── Step 1: SPEC artifact is real ────────────────────────────────────────────

def test_fodt_spec_requirements_exist_and_real():
    """FODT-SPEC-001-requirements.json must exist and have non-zero requirements."""
    req_path = _REPO / ".local" / "spec-artifacts" / "FODT-SPEC-001-requirements.json"
    assert req_path.exists(), "FODT-SPEC-001-requirements.json not found"
    data = json.loads(req_path.read_text())
    assert data.get("requirements_count", 0) > 0, "requirements_count must be > 0"
    reqs = data.get("requirements", [])
    assert len(reqs) > 0, "requirements list must not be empty"


def test_fodt_spec_has_text_p_requirement():
    """At least one FODT spec requirement must reference the text:p QName."""
    req_path = _REPO / ".local" / "spec-artifacts" / "FODT-SPEC-001-requirements.json"
    data = json.loads(req_path.read_text())
    text_p_reqs = [
        r for r in data.get("requirements", [])
        if "text:p" in r.get("text_fragment", "")
    ]
    assert len(text_p_reqs) >= 1, (
        "Expected at least one requirement referencing 'text:p'; "
        f"found {len(text_p_reqs)}"
    )


def test_fodt_not_in_quarantine():
    """FODT must NOT have a synthetic/quarantined spec artifact."""
    quarantine = _REPO / ".local" / "spec-artifacts" / "FODT-SPEC-001-requirements-synthetic-DO-NOT-USE.json"
    assert not quarantine.exists(), (
        f"FODT has a quarantined synthetic spec artifact at {quarantine}. "
        "This must not exist — FODT requirements must come from the real spec."
    )


# ── Step 2: SAL facts ────────────────────────────────────────────────────────

def test_fodt_sal_facts_present():
    """sal-facts-latest.json must include FODT with FACT-FODT-* entries."""
    sal_path = _REPO / ".local" / "sal-output" / "sal-facts-latest.json"
    assert sal_path.exists(), "sal-facts-latest.json not found"
    sal = json.loads(sal_path.read_text())
    results = sal.get("results", [])
    fodt = [r for r in results if r.get("format_id", "") == "fodt"]
    assert len(fodt) == 1, f"Expected exactly 1 fodt entry in SAL results, got {len(fodt)}"
    facts = fodt[0].get("spec_facts", [])
    fodt_facts = [f for f in facts if f.get("qname", "").startswith("FACT-FODT-")]
    assert len(fodt_facts) > 0, "Expected FACT-FODT-* entries in SAL results"


def test_fodt_sal_facts_non_synthetic():
    """FODT SAL facts must not contain synthetic markers."""
    sal_path = _REPO / ".local" / "sal-output" / "sal-facts-latest.json"
    sal = json.loads(sal_path.read_text())
    results = sal.get("results", [])
    fodt = [r for r in results if r.get("format_id", "") == "fodt"]
    assert fodt, "FODT not in SAL results"
    facts = fodt[0].get("spec_facts", [])
    synthetic_markers = [
        f for f in facts
        if "synthetic" in str(f).lower() or "DO_NOT_USE" in str(f)
    ]
    assert len(synthetic_markers) == 0, (
        f"Found {len(synthetic_markers)} synthetic markers in FODT SAL facts"
    )


# ── Step 3: QNAME constant in Paragraph.cs ───────────────────────────────────

def test_fodt_paragraph_cs_qname_constant():
    """Spec/Text/Paragraph.cs must declare SpecQName = 'text:p'."""
    para_path = _REPO / "src" / "net" / "fodt" / "Spec" / "Text" / "Paragraph.cs"
    assert para_path.exists(), f"Paragraph.cs not found at {para_path}"
    content = para_path.read_text()
    assert 'SpecQName = "text:p"' in content, (
        "Paragraph.cs must contain: SpecQName = \"text:p\"\n"
        f"File content snippet: {content[:300]}"
    )


def test_fodt_paragraph_cs_spec_fact_ref():
    """Spec/Text/Paragraph.cs must declare SpecFactRef = 'FACT-FODT-003'."""
    para_path = _REPO / "src" / "net" / "fodt" / "Spec" / "Text" / "Paragraph.cs"
    content = para_path.read_text()
    assert 'SpecFactRef = "FACT-FODT-003"' in content, (
        "Paragraph.cs must contain: SpecFactRef = \"FACT-FODT-003\"\n"
        f"File content snippet: {content[:300]}"
    )


def test_fodt_paragraph_cs_is_not_static_class():
    """Spec/Text/Paragraph.cs must be a real class (not static-class-with-constants only)."""
    para_path = _REPO / "src" / "net" / "fodt" / "Spec" / "Text" / "Paragraph.cs"
    content = para_path.read_text()
    assert "public sealed class Paragraph" in content or "public class Paragraph" in content, (
        "Paragraph.cs must be a non-static class (sealed or open). "
        "Found static class — TC-QNAME-IMPL-001 conversion not complete."
    )
    # Must not be static-only
    assert "public static class Paragraph" not in content, (
        "Paragraph.cs must NOT be a static class after TC-QNAME-IMPL-001 conversion."
    )


# ── Step 4+5: Chain proof document exists ────────────────────────────────────

def test_fodt_chain_proof_document_exists():
    """Chain proof document must have been written for TC-CHAIN-ODF-001."""
    evidence_root = _REPO / ".local" / "evidences" / "FF-HEALING-TASKCARDS-EXEC-20260621"
    chain_proof = evidence_root / "fodt-spec-sal-qname-chain-proof.md"
    assert chain_proof.exists(), (
        f"TC-CHAIN-ODF-001 chain proof document not found at {chain_proof}"
    )
    content = chain_proof.read_text()
    assert "Chain Status" in content, "Chain proof must have a 'Chain Status' header"
    assert "PASS" in content, "Chain proof must contain PASS verdict for at least one step"
