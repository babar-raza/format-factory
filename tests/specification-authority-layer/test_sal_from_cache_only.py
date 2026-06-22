"""
test_sal_from_cache_only.py — Integration tests for --from-cache-only mode
and the semantic census tool (spec_census.py).

TC-SAL-IMPL-001: --from-cache-only suppresses template facts, emits only workbench-verified facts.
TC-SAL-IMPL-006: spec_census.py produces per-category semantic unit counts.
TC-SAL-DIAG-008: FODS census establishes extraction denominator.
ROOT-07: ZST extraction pipeline finds RFC text via fallback path.
ROOT-09: FODS extraction pipeline extracts >200 candidates with raised cap.
"""
import json
import sys
from pathlib import Path

import pytest

_REPO = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_REPO / "tools" / "specification-authority-layer"))

from sal_master_runner import run_sal_pipeline


# ---------------------------------------------------------------------------
# TC-SAL-IMPL-001: --from-cache-only mode
# ---------------------------------------------------------------------------

class TestFromCacheOnlyMode:
    """Verify that from_cache_only=True suppresses template facts."""

    def test_from_cache_only_returns_dict(self, tmp_path):
        result = run_sal_pipeline(
            formats=["fods"], output_dir=tmp_path, from_cache_only=True,
        )
        assert isinstance(result, dict)

    def test_from_cache_only_fods_emits_workbench_facts(self, tmp_path):
        result = run_sal_pipeline(
            formats=["fods"], output_dir=tmp_path, from_cache_only=True,
        )
        assert result["spec_facts_total"] >= 70, (
            f"Expected >= 70 FODS workbench facts, got {result['spec_facts_total']}"
        )

    def test_from_cache_only_fods_no_template_qnames(self, tmp_path):
        run_sal_pipeline(
            formats=["fods"], output_dir=tmp_path, from_cache_only=True,
        )
        latest = tmp_path / "sal-facts-latest.json"
        data = json.loads(latest.read_text(encoding="utf-8"))
        fods = next(r for r in data["results"] if r["format_id"] == "fods")
        qnames = [f["qname"] for f in fods["spec_facts"]]
        # All facts should be FACT-FODS-NNN pattern (workbench), not template pattern
        for q in qnames:
            assert q.startswith("FACT-FODS-") or q.startswith("FODS-FACT-"), (
                f"Unexpected qname in from-cache-only mode: {q}"
            )

    def test_from_cache_only_zst_emits_workbench_facts(self, tmp_path):
        result = run_sal_pipeline(
            formats=["zst"], output_dir=tmp_path, from_cache_only=True,
        )
        assert result["spec_facts_total"] >= 15, (
            f"Expected >= 15 ZST workbench facts, got {result['spec_facts_total']}"
        )

    def test_from_cache_only_fodt_emits_workbench_facts(self, tmp_path):
        result = run_sal_pipeline(
            formats=["fodt"], output_dir=tmp_path, from_cache_only=True,
        )
        assert result["spec_facts_total"] >= 27, (
            f"Expected >= 27 FODT workbench facts, got {result['spec_facts_total']}"
        )

    def test_from_cache_only_fewer_facts_than_default(self, tmp_path):
        """from_cache_only should emit fewer facts (no templates)."""
        default_result = run_sal_pipeline(
            formats=["fods"], output_dir=tmp_path / "default",
        )
        cache_result = run_sal_pipeline(
            formats=["fods"], output_dir=tmp_path / "cache_only",
            from_cache_only=True,
        )
        assert cache_result["spec_facts_total"] <= default_result["spec_facts_total"], (
            "from_cache_only should not produce MORE facts than default mode"
        )

    def test_from_cache_only_format_without_workbench_emits_zero(self, tmp_path):
        """A format with no workbench should emit 0 facts in cache-only mode."""
        # ORA has no spec-cache workbench directory — from_cache_only emits 0 facts.
        # CSV was previously used but its structural workbench has verified_with_note facts.
        result = run_sal_pipeline(
            formats=["ora"], output_dir=tmp_path, from_cache_only=True,
        )
        latest = tmp_path / "sal-facts-latest.json"
        data = json.loads(latest.read_text(encoding="utf-8"))
        ora_result = next(r for r in data["results"] if r["format_id"] == "ora")
        assert len(ora_result["spec_facts"]) == 0, (
            "ORA has no workbench — from_cache_only should emit 0 facts"
        )

    def test_from_cache_only_all_three_formats_combined(self, tmp_path):
        result = run_sal_pipeline(
            formats=["fods", "zst", "fodt"], output_dir=tmp_path,
            from_cache_only=True,
        )
        assert result["spec_facts_total"] >= 118, (
            f"Expected >= 118 combined workbench facts (76+15+27), "
            f"got {result['spec_facts_total']}"
        )


# ---------------------------------------------------------------------------
# TC-SAL-IMPL-006: Semantic Census Tool
# ---------------------------------------------------------------------------

class TestSemanticCensus:
    """Verify spec_census.py produces valid census output."""

    @pytest.fixture(autouse=True)
    def _import_census(self):
        from spec_census import run_census
        self.run_census = run_census

    def test_fods_census_returns_dict(self):
        result = self.run_census("fods")
        assert isinstance(result, dict)
        assert result["status"] == "ok"

    def test_fods_census_has_all_categories(self):
        result = self.run_census("fods")
        categories = result["categories"]
        expected = {
            "NORM-REQ", "ELEM-DEF", "ATTR-DEF", "ENUM-VAL", "CARD-RULE",
            "DATA-TYPE", "GRAMMAR", "ENCODING", "ERROR", "CONFORM",
        }
        assert set(categories.keys()) == expected

    def test_fods_census_substantial_units(self):
        result = self.run_census("fods")
        assert result["total_units"] >= 3000, (
            f"Expected >= 3000 FODS semantic units, got {result['total_units']}"
        )

    def test_fods_census_elem_def_significant(self):
        result = self.run_census("fods")
        assert result["categories"]["ELEM-DEF"] >= 500, (
            f"Expected >= 500 ELEM-DEF, got {result['categories']['ELEM-DEF']}"
        )

    def test_fods_census_attr_def_significant(self):
        result = self.run_census("fods")
        assert result["categories"]["ATTR-DEF"] >= 1000, (
            f"Expected >= 1000 ATTR-DEF, got {result['categories']['ATTR-DEF']}"
        )

    def test_zst_census_returns_dict(self):
        result = self.run_census("zst")
        assert isinstance(result, dict)
        assert result["status"] == "ok"

    def test_zst_census_has_encoding_units(self):
        result = self.run_census("zst")
        assert result["categories"]["ENCODING"] >= 50, (
            f"Expected >= 50 ENCODING units in ZST, got {result['categories']['ENCODING']}"
        )

    def test_zst_census_total(self):
        result = self.run_census("zst")
        assert result["total_units"] >= 100, (
            f"Expected >= 100 ZST semantic units, got {result['total_units']}"
        )

    def test_unknown_format_returns_no_text(self):
        result = self.run_census("nonexistent_format_xyz")
        assert result["status"] == "no_text"
        assert result["total_units"] == 0


# ---------------------------------------------------------------------------
# ROOT-07: ZST path resolution fix
# ---------------------------------------------------------------------------

class TestZSTPathResolution:
    """Verify extraction pipeline finds ZST RFC text via fallback."""

    @pytest.fixture(autouse=True)
    def _import_pipeline(self):
        from run_extraction_pipeline import _find_normalized_text
        self._find_text = _find_normalized_text

    def test_zst_text_found(self):
        path = self._find_text("zst")
        assert path is not None, "ZST text should be found via fallback path"
        assert path.exists(), f"ZST text path does not exist: {path}"

    def test_zst_text_is_rfc(self):
        path = self._find_text("zst")
        assert path is not None
        assert "rfc" in str(path).lower(), (
            f"ZST text should be RFC file, got: {path}"
        )

    def test_fods_text_found_primary(self):
        path = self._find_text("fods")
        assert path is not None, "FODS text should be found via primary path"
        assert "normalized" in str(path), (
            f"FODS should use primary normalized path, got: {path}"
        )


# ---------------------------------------------------------------------------
# ROOT-09: Extraction cap increase
# ---------------------------------------------------------------------------

class TestExtractionCap:
    """Verify extraction cap is raised from 200."""

    def test_cap_is_above_200(self):
        from run_extraction_pipeline import _MAX_CANDIDATES_PER_FORMAT
        assert _MAX_CANDIDATES_PER_FORMAT > 200, (
            f"Cap should be >200, got {_MAX_CANDIDATES_PER_FORMAT}"
        )

    def test_cap_is_5000(self):
        from run_extraction_pipeline import _MAX_CANDIDATES_PER_FORMAT
        assert _MAX_CANDIDATES_PER_FORMAT == 5000


# ---------------------------------------------------------------------------
# TC-SAL-IMPL-002: Verification algorithm improvements
# ---------------------------------------------------------------------------

class TestVerificationAlgorithm:
    """Verify run_fact_verification.py handles slug-style section IDs and full-text fallback."""

    @pytest.fixture(autouse=True)
    def _import_verifier(self):
        from run_fact_verification import (
            _normalize_section_id,
            _tokenize_claim,
            _find_section_line,
            _score_claim_fulltext,
        )
        self._normalize = _normalize_section_id
        self._tokenize = _tokenize_claim
        self._find_section = _find_section_line
        self._fulltext = _score_claim_fulltext

    # _normalize_section_id tests
    def test_normalize_numeric(self):
        assert self._normalize("3.1.1") == "3.1.1"

    def test_normalize_slug_with_heading(self):
        assert self._normalize("section-3.1.1.1.--frame-header") == "3.1.1.1"

    def test_normalize_slug_trailing_dot(self):
        assert self._normalize("section-2.--definitions") == "2"

    def test_normalize_unknown(self):
        assert self._normalize("section-unknown") == ""

    def test_normalize_empty(self):
        assert self._normalize("") == ""

    def test_normalize_complex_slug(self):
        assert self._normalize("section-3.1.1.3.2.1.2.--decoding-sequences") == "3.1.1.3.2.1.2"

    # _tokenize_claim tests
    def test_tokenize_basic(self):
        terms = self._tokenize("The frame begins with a 4-byte magic number")
        assert "frame" in terms
        assert "magic" in terms
        assert "number" in terms
        # "the" should be filtered (stop word)
        assert "the" not in terms

    # _score_claim_fulltext tests
    def test_fulltext_match(self):
        lines = [
            "The frame begins with a 4-byte magic number 0xFD2FB528.\n",
            "A compliant decompressor must handle window descriptor bytes.\n",
            "Zstandard compressed data uses dictionary identifier fields.\n",
        ]
        terms = ["frame", "magic", "number", "0xfd2fb528", "compliant",
                 "decompressor", "window", "descriptor", "zstandard", "compressed"]
        status, matched = self._fulltext(lines, terms)
        assert status == "verified_with_note"
        assert len(matched) >= 5

    def test_fulltext_no_match(self):
        lines = ["This is completely unrelated text about cooking.\n"]
        terms = ["frame", "magic", "number", "0xfd2fb528", "zstandard"]
        status, matched = self._fulltext(lines, terms)
        assert status == "not_found_in_normalized_text"


# ---------------------------------------------------------------------------
# TC-SAL-DIAG-011: Consumer Reachability
# ---------------------------------------------------------------------------

class TestConsumerReachability:
    """Verify sal-facts-latest.json reaches downstream consumers."""

    @pytest.fixture(autouse=True)
    def _setup(self):
        self._sal_path = _REPO / ".local" / "sal-output" / "sal-facts-latest.json"

    def test_sal_facts_file_exists(self):
        assert self._sal_path.is_file(), "sal-facts-latest.json must exist"

    def test_sal_facts_has_results(self):
        data = json.loads(self._sal_path.read_text(encoding="utf-8"))
        assert "results" in data
        assert len(data["results"]) >= 15, (
            f"Expected at least 15 format results, got {len(data['results'])}"
        )

    def test_sal_facts_total_above_5000(self):
        data = json.loads(self._sal_path.read_text(encoding="utf-8"))
        total = sum(len(r.get("spec_facts", [])) for r in data["results"])
        assert total >= 5000, f"Expected >=5000 total facts, got {total}"

    def test_fods_facts_above_4900(self):
        data = json.loads(self._sal_path.read_text(encoding="utf-8"))
        fods = next((r for r in data["results"] if r["format_id"] == "fods"), None)
        assert fods is not None, "FODS must be in results"
        assert len(fods["spec_facts"]) >= 4900, (
            f"FODS should have >=4900 facts, got {len(fods['spec_facts'])}"
        )

    def test_zst_facts_above_90(self):
        data = json.loads(self._sal_path.read_text(encoding="utf-8"))
        zst = next((r for r in data["results"] if r["format_id"] == "zst"), None)
        assert zst is not None, "ZST must be in results"
        assert len(zst["spec_facts"]) >= 90, (
            f"ZST should have >=90 facts, got {len(zst['spec_facts'])}"
        )

    def test_capability_compiler_reads_facts(self):
        """Verify capability_compiler.load_sal_facts() reads the real file."""
        sys.path.insert(0, str(_REPO / "tools" / "supervisor"))
        from capability_compiler import load_sal_facts, reset_sal_cache
        reset_sal_cache()
        facts = load_sal_facts(self._sal_path)
        assert "FODS" in facts, "Capability compiler should index FODS"
        assert len(facts["FODS"]) >= 4900
        reset_sal_cache()

    def test_capability_map_generator_reads_facts(self):
        """Verify capability_map_generator._load_sal_facts() works."""
        sys.path.insert(0, str(_REPO / "tools" / "capability_layer"))
        import capability_map_generator as cmg
        cmg._sal_facts_cache = None  # reset cache
        cmg._SAL_OUTPUT = self._sal_path
        facts = cmg._load_sal_facts()
        assert "FODS" in facts, "Capability map generator should index FODS"
        assert len(facts["FODS"]) >= 4900
        cmg._sal_facts_cache = None  # cleanup

    def test_governance_validator_reads_facts(self):
        """Verify governance_validators.validate_min_spec_facts_per_format works."""
        sys.path.insert(0, str(_REPO / "tools" / "supervisor"))
        from governance_validators import validate_min_spec_facts_per_format
        result = validate_min_spec_facts_per_format(
            declaration={
                "planned_work_items": [{
                    "item_id": "TEST-001",
                    "title": "FODS test",
                    "item_type": "PRODUCT_SOURCE",
                    "format_id": "FODS",
                }],
            },
            repo_root=_REPO,
        )
        # Should pass since FODS has >3 facts
        assert result.get("result") in ("PASS", "WARN", "SKIP"), (
            f"Validator should pass for FODS, got: {result}"
        )


class TestODFFamilyContextPacks:
    """Verify context packs rebuilt for FODP, FODG, ODS, ODT with ODF workbench facts.

    TC-SAL-IMPL-005 (extended): Rebuild covers all 7 ODF-family formats.
    """

    _CONTEXT_PACK_DIR = _REPO / "reports" / "specification-authority-layer-mwp" / "context-pack-sample"

    def _load_pack(self, format_id: str) -> dict:
        path = self._CONTEXT_PACK_DIR / f"{format_id}-context-pack.json"
        assert path.is_file(), f"Context pack missing: {path}"
        return json.loads(path.read_text(encoding="utf-8"))

    def test_fodp_context_pack_exists(self):
        pack = self._load_pack("fodp")
        assert pack["format_id"] == "fodp"

    def test_fodp_context_pack_has_requirements(self):
        pack = self._load_pack("fodp")
        reqs = pack.get("requirement_summary", [])
        assert len(reqs) >= 50, f"FODP context pack should have >=50 requirements, got {len(reqs)}"

    def test_fodg_context_pack_exists(self):
        pack = self._load_pack("fodg")
        assert pack["format_id"] == "fodg"

    def test_fodg_context_pack_has_requirements(self):
        pack = self._load_pack("fodg")
        reqs = pack.get("requirement_summary", [])
        assert len(reqs) >= 50, f"FODG context pack should have >=50 requirements, got {len(reqs)}"

    def test_ods_context_pack_exists(self):
        pack = self._load_pack("ods")
        assert pack["format_id"] == "ods"

    def test_ods_context_pack_has_requirements(self):
        pack = self._load_pack("ods")
        reqs = pack.get("requirement_summary", [])
        assert len(reqs) >= 50, f"ODS context pack should have >=50 requirements, got {len(reqs)}"

    def test_odt_context_pack_exists(self):
        pack = self._load_pack("odt")
        assert pack["format_id"] == "odt"

    def test_odt_context_pack_has_requirements(self):
        pack = self._load_pack("odt")
        reqs = pack.get("requirement_summary", [])
        assert len(reqs) >= 50, f"ODT context pack should have >=50 requirements, got {len(reqs)}"

    def test_odf_family_source_sha_consistent(self):
        """All ODF-family context packs must reference the same ODF spec SHA."""
        odf_sha = "92cfe64ee30a8cca1be19a76d38628fdc8ef9153eb59547f6c96fe7b9b81b066"
        for fmt in ("fods", "fodt", "fodp", "fodg", "ods", "odt"):
            pack = self._load_pack(fmt)
            for src in pack.get("included_sources", []):
                assert src.get("sha256") == odf_sha, (
                    f"{fmt}: expected ODF SHA {odf_sha[:16]}..., got {src.get('sha256', '')[:16]}"
                )

    def test_total_odf_family_requirements_above_600(self):
        """All 7 ODF-family packs combined must have >=600 requirements."""
        total = 0
        for fmt in ("fods", "fodt", "fodp", "fodg", "ods", "odt"):
            pack = self._load_pack(fmt)
            total += len(pack.get("requirement_summary", []))
        assert total >= 600, f"ODF family should have >=600 total requirements, got {total}"

    def test_rebuild_from_workbench_covers_odf_family(self):
        """rebuild_all_from_workbench() produces packs for all 7 formats."""
        import tempfile
        from context_pack_builder import rebuild_all_from_workbench
        with tempfile.TemporaryDirectory() as tmpdir:
            packs = rebuild_all_from_workbench(_REPO, output_dir=tmpdir)
            fmt_ids = {p.format_id for p in packs}
            for expected in ("fods", "fodt", "zst", "fodp", "fodg", "ods", "odt"):
                assert expected in fmt_ids, f"rebuild_all_from_workbench missing: {expected}"
