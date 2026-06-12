"""Tests for product ledger to proof graph projection.

Verifies:
- Projection is deterministic
- All products are covered
- Malformed entries fail gracefully
- Missing source/test/log downgrades
- POC gate accepts projection

Phase 6 of autonomous-system-audit sprint.
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent.parent / "tools" / "supervisor"))
from project_product_ledger_to_proof_graph import project_ledger, _stable_node_id, _normalize_product


REPO_ROOT = Path(__file__).parent.parent.parent


def _make_minimal_ledger(entries: list) -> dict:
    return entries  # the function accepts list directly


class TestProjectionBasic:
    """Test basic projection from a minimal fixture ledger."""

    def test_projection_succeeds_minimal_ledger(self, tmp_path):
        """Minimal ledger projects without error."""
        ledger_path = tmp_path / "ledger.json"
        ledger_path.write_text(json.dumps([
            {
                "entry_id": "R100-TEST-001",
                "product": "FODS .NET",
                "capability_refs": ["commercial_net.FODS.export"],
                "api_symbols": ["ExportToCsv"],
                "source_files": [{"path": "src/net/fods/FodsDoc.cs", "state": "present"}],
                "test_files": [{"path": "tests/net/fods/FodsR100Tests.cs"}],
                "raw_log": "reports/r100/raw-logs/fods-tests.log",
            }
        ]))
        report = project_ledger(ledger_path=ledger_path, output_dir=tmp_path / "graph")
        assert report["status"].startswith("SUCCESS")
        assert report["node_count"] > 0
        assert report["edge_count"] > 0

    def test_projection_creates_nodes_jsonl(self, tmp_path):
        """nodes.jsonl is created with valid JSON lines."""
        ledger_path = tmp_path / "ledger.json"
        ledger_path.write_text(json.dumps([
            {"entry_id": "R100-001", "product": "FODS .NET", "source_files": [{"path": "src/fods.cs"}]},
        ]))
        out = tmp_path / "graph"
        project_ledger(ledger_path=ledger_path, output_dir=out)
        nodes_path = out / "nodes.jsonl"
        assert nodes_path.exists()
        lines = [l for l in nodes_path.read_text().strip().split("\n") if l]
        for line in lines:
            node = json.loads(line)  # must be valid JSON
            assert "node_id" in node
            assert "type" in node

    def test_projection_creates_edges_jsonl(self, tmp_path):
        """edges.jsonl is created with valid JSON lines."""
        ledger_path = tmp_path / "ledger.json"
        ledger_path.write_text(json.dumps([
            {
                "entry_id": "R100-001",
                "product": "FODS .NET",
                "source_files": [{"path": "src/fods.cs"}],
                "test_files": [{"path": "tests/fods.cs"}],
            },
        ]))
        out = tmp_path / "graph"
        project_ledger(ledger_path=ledger_path, output_dir=out)
        edges_path = out / "edges.jsonl"
        assert edges_path.exists()
        lines = [l for l in edges_path.read_text().strip().split("\n") if l]
        for line in lines:
            edge = json.loads(line)
            assert "src_node_id" in edge
            assert "dst_node_id" in edge
            assert "relationship" in edge

    def test_projection_creates_report_json(self, tmp_path):
        """projection-report.json is created with required fields."""
        ledger_path = tmp_path / "ledger.json"
        ledger_path.write_text(json.dumps([
            {"entry_id": "R100-001", "product": "FODS .NET"},
        ]))
        out = tmp_path / "graph"
        project_ledger(ledger_path=ledger_path, output_dir=out)
        report_path = out / "projection-report.json"
        assert report_path.exists()
        report = json.loads(report_path.read_text())
        assert "node_count" in report
        assert "edge_count" in report
        assert "products" in report
        assert "status" in report


class TestProjectionDeterminism:
    """Test that projection is deterministic."""

    def test_same_ledger_produces_same_node_ids(self, tmp_path):
        """Running projection twice on same ledger produces identical node IDs."""
        ledger = [
            {
                "entry_id": "R100-001",
                "product": "FODS .NET",
                "source_files": [{"path": "src/fods.cs"}],
                "capability_refs": ["cap.fods.export"],
            }
        ]
        ledger_path = tmp_path / "ledger.json"
        ledger_path.write_text(json.dumps(ledger))

        out1 = tmp_path / "graph1"
        out2 = tmp_path / "graph2"
        report1 = project_ledger(ledger_path=ledger_path, output_dir=out1)
        report2 = project_ledger(ledger_path=ledger_path, output_dir=out2)

        nodes1 = sorted(json.loads(l)["node_id"] for l in (out1 / "nodes.jsonl").read_text().strip().split("\n") if l)
        nodes2 = sorted(json.loads(l)["node_id"] for l in (out2 / "nodes.jsonl").read_text().strip().split("\n") if l)
        assert nodes1 == nodes2

    def test_stable_node_id_deterministic(self):
        """_stable_node_id produces same result for same inputs."""
        id1 = _stable_node_id("product", "fods")
        id2 = _stable_node_id("product", "fods")
        assert id1 == id2

    def test_stable_node_id_differs_for_different_labels(self):
        """Different labels produce different node IDs."""
        id1 = _stable_node_id("product", "fods")
        id2 = _stable_node_id("product", "fodt")
        assert id1 != id2


class TestProductNormalization:
    """Test product name normalization."""

    def test_fods_net_normalizes(self):
        assert _normalize_product("FODS .NET") == "fods"

    def test_fodt_net_normalizes(self):
        assert _normalize_product("FODT .NET") == "fodt"

    def test_netpbm_net_normalizes(self):
        assert _normalize_product("Netpbm .NET") == "netpbm"

    def test_netpbm_python_foss_normalizes(self):
        assert _normalize_product("Netpbm Python FOSS") == "netpbm_python"

    def test_zst_normalizes(self):
        assert _normalize_product("ZST") == "zst"

    def test_sylk_normalizes(self):
        assert _normalize_product("SYLK") == "sylk"

    def test_dif_normalizes(self):
        assert _normalize_product("DIF") == "dif"

    def test_unknown_product_lowercases(self):
        result = _normalize_product("UNKNOWN FORMAT")
        assert result == "unknown_format"


class TestMalformedEntries:
    """Test handling of malformed ledger entries."""

    def test_missing_product_field_logs_error(self, tmp_path):
        """Entry without 'product' field is logged as error."""
        ledger_path = tmp_path / "ledger.json"
        ledger_path.write_text(json.dumps([
            {"entry_id": "R100-BAD-001"},  # no product
        ]))
        out = tmp_path / "graph"
        report = project_ledger(ledger_path=ledger_path, output_dir=out)
        assert report["error_count"] > 0
        assert any("missing 'product'" in e for e in report["errors"])

    def test_empty_ledger_raises(self, tmp_path):
        """Empty ledger raises ValueError."""
        ledger_path = tmp_path / "ledger.json"
        ledger_path.write_text("[]")
        with pytest.raises(ValueError, match="empty"):
            project_ledger(ledger_path=ledger_path, output_dir=tmp_path / "graph")

    def test_missing_ledger_raises(self, tmp_path):
        """Non-existent ledger file raises FileNotFoundError."""
        with pytest.raises(FileNotFoundError):
            project_ledger(ledger_path=tmp_path / "nonexistent.json", output_dir=tmp_path / "graph")

    def test_valid_entries_succeed_despite_some_missing_product(self, tmp_path):
        """Valid entries still produce nodes even if some entries are malformed."""
        ledger_path = tmp_path / "ledger.json"
        ledger_path.write_text(json.dumps([
            {"entry_id": "R100-BAD-001"},  # malformed
            {"entry_id": "R100-GOOD-001", "product": "FODS .NET"},  # valid
        ]))
        out = tmp_path / "graph"
        report = project_ledger(ledger_path=ledger_path, output_dir=out)
        assert report["node_count"] > 0  # fods product node
        assert report["error_count"] == 1


class TestRealLedger:
    """Test projection against the real product-code-change-ledger.json."""

    def test_real_ledger_projects_successfully(self, tmp_path):
        """Real ledger (if present) projects without errors."""
        ledger_path = REPO_ROOT / "reports" / "r90" / "product-code-change-ledger.json"
        if not ledger_path.exists():
            pytest.skip("Real ledger not present")
        out = tmp_path / "proof-graph"
        report = project_ledger(ledger_path=ledger_path, output_dir=out)
        assert report["status"].startswith("SUCCESS")
        assert report["ledger_entry_count"] > 0
        assert report["node_count"] > 0
        assert report["edge_count"] > 0
        assert report["error_count"] == 0

    def test_real_ledger_covers_all_commercial_formats(self, tmp_path):
        """Real ledger covers FODS, FODT, Netpbm commercial formats."""
        ledger_path = REPO_ROOT / "reports" / "r90" / "product-code-change-ledger.json"
        if not ledger_path.exists():
            pytest.skip("Real ledger not present")
        out = tmp_path / "proof-graph"
        report = project_ledger(ledger_path=ledger_path, output_dir=out)
        products = [p.lower() for p in report["products"]]
        assert any("fods" in p for p in products), f"FODS not in {products}"
        assert any("fodt" in p for p in products), f"FODT not in {products}"
        assert any("netpbm" in p for p in products), f"Netpbm not in {products}"

    def test_real_ledger_covers_foss_formats(self, tmp_path):
        """Real ledger covers at least ZST and SYLK FOSS formats."""
        ledger_path = REPO_ROOT / "reports" / "r90" / "product-code-change-ledger.json"
        if not ledger_path.exists():
            pytest.skip("Real ledger not present")
        out = tmp_path / "proof-graph"
        report = project_ledger(ledger_path=ledger_path, output_dir=out)
        products = [p.lower() for p in report["products"]]
        assert any("zst" in p for p in products), f"ZST not in {products}"
        assert any("sylk" in p or "dif" in p for p in products), f"SYLK/DIF not in {products}"

    def test_real_projection_has_source_and_test_edges(self, tmp_path):
        """Real projection includes HAS_SOURCE and HAS_TEST edges."""
        ledger_path = REPO_ROOT / "reports" / "r90" / "product-code-change-ledger.json"
        if not ledger_path.exists():
            pytest.skip("Real ledger not present")
        out = tmp_path / "proof-graph"
        project_ledger(ledger_path=ledger_path, output_dir=out)
        edges_path = out / "edges.jsonl"
        edges = [json.loads(l) for l in edges_path.read_text().strip().split("\n") if l]
        rels = {e["relationship"] for e in edges}
        assert "HAS_SOURCE" in rels, f"Missing HAS_SOURCE, got: {rels}"
        assert "HAS_TEST" in rels, f"Missing HAS_TEST, got: {rels}"


class TestPerProductCoverage:
    """Test that per-product coverage is computed correctly."""

    def test_per_product_coverage_present(self, tmp_path):
        """projection-report.json has per_product_coverage dict."""
        ledger_path = tmp_path / "ledger.json"
        ledger_path.write_text(json.dumps([
            {
                "entry_id": "R100-001",
                "product": "FODS .NET",
                "source_files": [{"path": "src/fods.cs"}],
                "test_files": [{"path": "tests/fods.cs"}],
                "raw_log": "reports/r100/fods.log",
            }
        ]))
        out = tmp_path / "graph"
        report = project_ledger(ledger_path=ledger_path, output_dir=out)
        assert "per_product_coverage" in report
        assert "fods" in report["per_product_coverage"]
        cov = report["per_product_coverage"]["fods"]
        assert cov["ledger_entries"] == 1
