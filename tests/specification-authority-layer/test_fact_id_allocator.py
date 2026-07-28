"""Tests for fact_id_allocator.py (TC-SAL-ID-001, TC-SAL-ID-007)."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent / "tools" / "specification-authority-layer"))

from fact_id_allocator import allocate, allocate_bulk, get_status, load_ledger


class TestAllocateSingle:
    def test_new_allocation(self, tmp_path):
        ledger = tmp_path / "ledger.json"
        r = allocate("fods", "FACT-FODS-001", ledger)
        assert r["new_id"] == "SAL-FODS-00001"
        assert r["verdict"] == "NEW"

    def test_idempotent(self, tmp_path):
        ledger = tmp_path / "ledger.json"
        r1 = allocate("fods", "FACT-FODS-001", ledger)
        r2 = allocate("fods", "FACT-FODS-001", ledger)
        assert r1["new_id"] == r2["new_id"]
        assert r2["verdict"] == "EXISTING"

    def test_sequential_within_format(self, tmp_path):
        ledger = tmp_path / "ledger.json"
        r1 = allocate("csv", "FACT-CSV-001", ledger)
        r2 = allocate("csv", "FACT-CSV-002", ledger)
        assert r1["new_id"] == "SAL-CSV-00001"
        assert r2["new_id"] == "SAL-CSV-00002"

    def test_independent_formats(self, tmp_path):
        ledger = tmp_path / "ledger.json"
        r1 = allocate("csv", "FACT-CSV-001", ledger)
        r2 = allocate("tsv", "FACT-TSV-001", ledger)
        assert r1["new_id"] == "SAL-CSV-00001"
        assert r2["new_id"] == "SAL-TSV-00001"

    def test_format_uppercased_in_id(self, tmp_path):
        ledger = tmp_path / "ledger.json"
        r = allocate("odf-pkg", "FACT-ODF-PKG-001", ledger)
        assert r["new_id"] == "SAL-ODF-PKG-00001"


class TestAllocateBulk:
    def _make_sal_db(self, tmp_path, facts_by_format):
        results = []
        total = 0
        for fmt_id, qnames in facts_by_format.items():
            spec_facts = [{"qname": q, "claim": f"test claim for {q}"} for q in qnames]
            results.append({"format_id": fmt_id, "spec_facts": spec_facts})
            total += len(spec_facts)
        data = {
            "generated_at": "2026-01-01T00:00:00",
            "generator": "test",
            "formats_processed": len(results),
            "spec_facts_total": total,
            "workbench_verified_fact_total": 0,
            "results": results,
        }
        path = tmp_path / "sal-facts.json"
        path.write_text(json.dumps(data), encoding="utf-8")
        return path

    def test_bulk_basic(self, tmp_path):
        sal_path = self._make_sal_db(tmp_path, {
            "fods": ["FACT-FODS-001", "FACT-FODS-002"],
            "csv": ["FACT-CSV-001"],
        })
        ledger = tmp_path / "ledger.json"
        r = allocate_bulk(sal_path, ledger)
        assert r["total_mapped"] == 3
        assert r["new_count"] == 3
        assert r["mapping"]["FACT-FODS-001"] == "SAL-FODS-00001"
        assert r["mapping"]["FACT-CSV-001"] == "SAL-CSV-00001"

    def test_bulk_workbench_before_ex(self, tmp_path):
        sal_path = self._make_sal_db(tmp_path, {
            "fods": ["FACT-FODS-EX-0001", "FACT-FODS-001", "FACT-FODS-EX-0002", "FACT-FODS-002"],
        })
        ledger = tmp_path / "ledger.json"
        r = allocate_bulk(sal_path, ledger)
        assert r["mapping"]["FACT-FODS-001"] == "SAL-FODS-00001"
        assert r["mapping"]["FACT-FODS-002"] == "SAL-FODS-00002"
        assert r["mapping"]["FACT-FODS-EX-0001"] == "SAL-FODS-00003"
        assert r["mapping"]["FACT-FODS-EX-0002"] == "SAL-FODS-00004"

    def test_bulk_idempotent(self, tmp_path):
        sal_path = self._make_sal_db(tmp_path, {
            "fods": ["FACT-FODS-001", "FACT-FODS-EX-0001"],
        })
        ledger = tmp_path / "ledger.json"
        r1 = allocate_bulk(sal_path, ledger)
        r2 = allocate_bulk(sal_path, ledger)
        assert r1["mapping"] == r2["mapping"]
        assert r2["existing_count"] == 2
        assert r2["new_count"] == 0


class TestStatus:
    def test_empty_ledger(self, tmp_path):
        s = get_status(tmp_path / "nonexistent.json")
        assert s["total_mapped"] == 0

    def test_after_allocation(self, tmp_path):
        ledger = tmp_path / "ledger.json"
        allocate("fods", "FACT-FODS-001", ledger)
        allocate("fods", "FACT-FODS-002", ledger)
        s = get_status(ledger)
        assert s["total_mapped"] == 2
        assert s["formats"]["fods"]["highest"] == 2
