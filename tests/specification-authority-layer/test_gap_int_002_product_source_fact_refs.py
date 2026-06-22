"""
GAP-INT-002 — Product Source Fact Reference Integration Tests

Proves that:
1. Product source files cite specific SAL fact IDs (FACT-<FORMAT>-NNN) in code comments
2. Every cited fact ID is present in the published sal-facts-latest.json output
3. The wiring between spec authority (SAL) and product implementation is non-empty

This test file addresses GAP-INT-002 as documented in plans/snoopy-juggling-seal.md.
Evidence: these tests pass = product source is traceable to spec authority.
"""

import json
import re
from pathlib import Path

import pytest

_REPO = Path(__file__).parent.parent.parent
_SAL_FACTS = _REPO / ".local" / "sal-output" / "sal-facts-latest.json"
_SRC_PYTHON = _REPO / "src" / "python"

# Pattern: FACT-<FORMAT>-NNN (e.g., FACT-FODS-001, FACT-ZST-003)
_FACT_PATTERN = re.compile(r"FACT-([A-Z0-9]+)-(\d+)")


def _load_sal_facts() -> dict[str, set[str]]:
    """Load sal-facts-latest.json and index only workbench-verified fact IDs by format_id.

    Only includes facts with source='workbench_verified' to ensure citations in product
    source are traceable to reviewed workbench evidence, not bootstrap template facts.
    """
    if not _SAL_FACTS.is_file():
        return {}
    data = json.loads(_SAL_FACTS.read_text(encoding="utf-8"))
    index: dict[str, set[str]] = {}
    for result in data.get("results", []):
        fmt = result.get("format_id", "").lower()
        for fact in result.get("spec_facts", []):
            if fact.get("source") != "workbench_verified":
                continue  # skip bootstrap template facts
            qname = fact.get("qname", "")
            if qname:
                index.setdefault(fmt, set()).add(qname)
    return index


def _scan_source_fact_refs(path: Path) -> list[str]:
    """Scan a Python source file for FACT-<FORMAT>-NNN references."""
    if not path.is_file():
        return []
    text = path.read_text(encoding="utf-8", errors="replace")
    return [m.group(0) for m in _FACT_PATTERN.finditer(text)]


class TestProductSourceFactRefs:
    """Verify product source files cite verifiable SAL fact IDs."""

    @pytest.fixture(scope="class")
    def sal_index(self) -> dict[str, set[str]]:
        return _load_sal_facts()

    def test_sal_facts_file_exists(self):
        assert _SAL_FACTS.is_file(), f"sal-facts-latest.json not found at {_SAL_FACTS}"

    def test_sal_facts_has_fods_facts(self, sal_index):
        assert "fods" in sal_index, "No FODS facts in sal-facts-latest.json"
        assert len(sal_index["fods"]) >= 100

    def test_sal_facts_has_fodt_facts(self, sal_index):
        assert "fodt" in sal_index, "No FODT facts in sal-facts-latest.json"
        assert len(sal_index["fodt"]) >= 100

    def test_sal_facts_has_zst_facts(self, sal_index):
        assert "zst" in sal_index, "No ZST facts in sal-facts-latest.json"
        assert len(sal_index["zst"]) >= 10

    def test_fods_neutral_model_cites_fact_refs(self):
        path = _SRC_PYTHON / "fods" / "neutral_model.py"
        refs = _scan_source_fact_refs(path)
        assert len(refs) >= 1, f"fods/neutral_model.py has no FACT- references (GAP-INT-002 not wired)"

    def test_fods_cited_facts_exist_in_sal(self, sal_index):
        path = _SRC_PYTHON / "fods" / "neutral_model.py"
        refs = _scan_source_fact_refs(path)
        fods_facts = sal_index.get("fods", set())
        missing = [r for r in refs if r not in fods_facts]
        assert not missing, (
            f"FODS product source cites fact IDs not in sal-facts-latest.json: {missing}"
        )

    def test_fodt_neutral_model_cites_fact_refs(self):
        path = _SRC_PYTHON / "fodt" / "neutral_model.py"
        refs = _scan_source_fact_refs(path)
        assert len(refs) >= 1, f"fodt/neutral_model.py has no FACT- references (GAP-INT-002 not wired)"

    def test_fodt_cited_facts_exist_in_sal(self, sal_index):
        path = _SRC_PYTHON / "fodt" / "neutral_model.py"
        refs = _scan_source_fact_refs(path)
        fodt_facts = sal_index.get("fodt", set())
        missing = [r for r in refs if r not in fodt_facts]
        assert not missing, (
            f"FODT product source cites fact IDs not in sal-facts-latest.json: {missing}"
        )

    def test_zst_source_cites_fact_refs(self):
        # ZST has fact refs in __init__.py comment
        init_path = _SRC_PYTHON / "zst" / "__init__.py"
        codec_path = _SRC_PYTHON / "zst" / "zst_codec.py"
        refs = _scan_source_fact_refs(init_path) + _scan_source_fact_refs(codec_path)
        assert len(refs) >= 1, (
            f"ZST source (zst/__init__.py, zst/zst_codec.py) has no FACT- references"
        )

    def test_zst_cited_facts_exist_in_sal(self, sal_index):
        init_path = _SRC_PYTHON / "zst" / "__init__.py"
        codec_path = _SRC_PYTHON / "zst" / "zst_codec.py"
        refs = _scan_source_fact_refs(init_path) + _scan_source_fact_refs(codec_path)
        zst_facts = sal_index.get("zst", set())
        missing = [r for r in refs if r not in zst_facts]
        assert not missing, (
            f"ZST product source cites fact IDs not in sal-facts-latest.json: {missing}"
        )

    def test_fods_constants_cites_fact_refs(self):
        path = _SRC_PYTHON / "fods" / "constants.py"
        refs = _scan_source_fact_refs(path)
        assert len(refs) >= 1, "fods/constants.py has no FACT- references"

    def test_fods_constants_cited_facts_exist_in_sal(self, sal_index):
        path = _SRC_PYTHON / "fods" / "constants.py"
        refs = _scan_source_fact_refs(path)
        fods_facts = sal_index.get("fods", set())
        missing = [r for r in refs if r not in fods_facts]
        assert not missing, (
            f"fods/constants.py cites fact IDs not in sal-facts-latest.json: {missing}"
        )

    def test_total_fact_refs_across_product_source(self, sal_index):
        """Scan ALL Python source files and verify all FACT- refs are in SAL."""
        all_refs: list[tuple[str, str]] = []  # (file_path, fact_id)
        for py_file in _SRC_PYTHON.rglob("*.py"):
            if "build" in py_file.parts:
                continue  # skip build artifacts
            refs = _scan_source_fact_refs(py_file)
            for ref in refs:
                all_refs.append((str(py_file.relative_to(_REPO)), ref))

        assert len(all_refs) >= 5, (
            f"Only {len(all_refs)} total FACT- references in product source — "
            "GAP-INT-002 requires meaningful spec authority wiring"
        )

        # Verify all cited facts exist in SAL
        all_sal_fact_ids: set[str] = set()
        for fact_ids in sal_index.values():
            all_sal_fact_ids.update(fact_ids)

        missing = [(f, r) for f, r in all_refs if r not in all_sal_fact_ids]
        assert not missing, (
            f"Product source cites {len(missing)} fact IDs not in sal-facts-latest.json: "
            f"{missing[:5]}"
        )

    def test_gnumeric_has_workbench_verified_sal_facts(self, sal_index):
        """Gnumeric now has workbench-verified facts (FACT-GNUMERIC-001/002/003).

        Regression guard: if workbench YAML is removed or corrupted, this test catches it.
        """
        gnumeric_facts = sal_index.get("gnumeric", set())
        assert len(gnumeric_facts) >= 3, (
            f"Expected >= 3 Gnumeric workbench-verified facts, got {len(gnumeric_facts)}. "
            "Check .local/spec-cache/gnumeric/v10/workbench/verified-facts-review.yaml"
        )
        assert "FACT-GNUMERIC-001" in gnumeric_facts, "FACT-GNUMERIC-001 missing from SAL"

    def test_abw_has_workbench_verified_sal_facts(self, sal_index):
        """ABW now has workbench-verified facts (FACT-ABW-001 through FACT-ABW-005).

        Regression guard: if workbench YAML is removed or corrupted, this test catches it.
        """
        abw_facts = sal_index.get("abw", set())
        assert len(abw_facts) >= 5, (
            f"Expected >= 5 ABW workbench-verified facts, got {len(abw_facts)}. "
            "Check .local/spec-cache/abw/awml-1.0/workbench/verified-facts-review.yaml"
        )
        assert "FACT-ABW-001" in abw_facts, "FACT-ABW-001 missing from SAL"

    def test_csv_has_workbench_verified_sal_facts(self, sal_index):
        """CSV has workbench-verified facts (FACT-CSV-001 and FACT-CSV-002) from the
        structural workbench YAML. These are the same IDs cited in the gap-ledger.

        Regression guard: if the structural workbench YAML is removed or status degrades,
        this test catches it and prevents the gap-ledger refs from becoming stale.
        """
        csv_facts = sal_index.get("csv", set())
        assert "FACT-CSV-001" in csv_facts, (
            "FACT-CSV-001 missing from SAL workbench-verified index. "
            "Check .local/spec-cache/csv/structural/workbench/verified-facts-review.yaml"
        )
        assert "FACT-CSV-002" in csv_facts, (
            "FACT-CSV-002 missing from SAL workbench-verified index. "
            "Check .local/spec-cache/csv/structural/workbench/verified-facts-review.yaml"
        )
