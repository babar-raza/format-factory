"""Tests that SAL qname prefixes match their format_id (regression for template mutation bug)."""
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_REPO / "tools" / "specification-authority-layer"))

from sal_master_runner import _spec_facts_for_format, _FORMAT_SPECIFIC_FACTS  # noqa: E402


# ── Formats that use DEFAULT template (should get FORMAT_ID-FACT-* qnames) ──

_DEFAULT_FORMATS = [
    {"format_id": "tsv", "spec_body": "IANA"},
    {"format_id": "xpm", "spec_body": "X Consortium"},
    {"format_id": "pam", "spec_body": "Netpbm"},
    {"format_id": "qoi", "spec_body": "QOI Spec"},
    {"format_id": "xcf", "spec_body": "GIMP"},
    {"format_id": "zpaq", "spec_body": "ZPAQ"},
    {"format_id": "abw", "spec_body": "AbiWord"},
    {"format_id": "ora", "spec_body": "freedesktop.org"},
    {"format_id": "pbm", "spec_body": "Netpbm"},
    {"format_id": "pgm", "spec_body": "Netpbm"},
    {"format_id": "ppm", "spec_body": "Netpbm"},
]


@pytest.mark.parametrize("fmt", _DEFAULT_FORMATS, ids=lambda f: f["format_id"])
def test_default_template_qnames_match_format(fmt):
    """Each DEFAULT-template format must produce qnames starting with its own format_id."""
    facts = _spec_facts_for_format(fmt)
    fid = fmt["format_id"].upper()
    for fact in facts:
        assert fact["qname"].startswith(fid + "-"), (
            f"Expected qname starting with '{fid}-', got '{fact['qname']}'"
        )


def test_default_template_not_mutated_across_calls():
    """Calling _spec_facts_for_format for multiple DEFAULT formats must not cross-contaminate qnames."""
    fmt_tsv = {"format_id": "tsv", "spec_body": "IANA"}
    fmt_xpm = {"format_id": "xpm", "spec_body": "X Consortium"}

    facts_tsv = _spec_facts_for_format(fmt_tsv)
    facts_xpm = _spec_facts_for_format(fmt_xpm)

    for f in facts_tsv:
        assert f["qname"].startswith("TSV-"), f"TSV qname mutated to: {f['qname']}"
    for f in facts_xpm:
        assert f["qname"].startswith("XPM-"), f"XPM qname mutated to: {f['qname']}"


# ── Format-specific facts ──

@pytest.mark.parametrize("fid", list(_FORMAT_SPECIFIC_FACTS.keys()))
def test_format_specific_facts_have_correct_prefix(fid):
    """Format-specific facts must have qnames starting with their format_id."""
    fmt = {"format_id": fid, "spec_body": "test"}
    facts = _spec_facts_for_format(fmt)
    prefix = fid.upper() + "-"
    for fact in facts:
        assert fact["qname"].startswith(prefix), (
            f"{fid}: expected prefix '{prefix}', got '{fact['qname']}'"
        )


# ── OASIS formats ──

def test_oasis_spreadsheet_format_not_mutated():
    """ODS facts should not mutate the OASIS template for subsequent ODS calls."""
    fmt = {"format_id": "ods", "spec_body": "OASIS", "family": "cells"}
    facts1 = _spec_facts_for_format(fmt)
    facts2 = _spec_facts_for_format(fmt)
    qnames1 = [f["qname"] for f in facts1]
    qnames2 = [f["qname"] for f in facts2]
    assert qnames1 == qnames2


# ── Pipeline-level check ──

def test_full_pipeline_produces_no_cross_contaminated_qnames():
    """Run SAL pipeline and verify no format has another format's prefix in its qnames."""
    import json
    sal_path = _REPO / ".local" / "sal-output" / "sal-facts-latest.json"
    if not sal_path.exists():
        pytest.skip("SAL output not generated yet")
    data = json.loads(sal_path.read_text(encoding="utf-8"))
    all_fids = {r["format_id"].upper() for r in data["results"]}
    for r in data["results"]:
        fid = r["format_id"].upper()
        for fact in r.get("spec_facts", []):
            qname = fact["qname"]
            # qname must start with own fid, ODF- (OASIS generics), or
            # a standards-body prefix (IETF-, W3C-, ISO-) for formats
            # governed by those bodies (e.g. ZST is RFC 8478).
            _STANDARDS_PREFIXES = ("ODF-", "IETF-", "W3C-", "ISO-")
            assert qname.startswith(fid + "-") or any(
                qname.startswith(p) for p in _STANDARDS_PREFIXES
            ), (
                f"Format {fid} has cross-contaminated qname: {qname}"
            )
            # Must NOT start with any OTHER format's prefix
            for other in all_fids:
                if other != fid and not any(
                    qname.startswith(p) for p in _STANDARDS_PREFIXES
                ):
                    assert not qname.startswith(other + "-"), (
                        f"Format {fid} has qname with {other} prefix: {qname}"
                    )
