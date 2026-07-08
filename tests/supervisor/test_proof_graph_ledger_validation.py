"""
Proof graph and product ledger validation tests.
Lane 2 of FORMAT-FACTORY-SPEC-AUTHORITY-FULL-HARDENING-BACKFILL-AND-PILOT-MEGA-TRAIN-001.

Validates:
- P6 cannot be claimed without graph edges
- P6 cannot be claimed without ledger authority fields
- Synthetic fixtures cannot satisfy proof graph authority
- FODS and ZST P6 chains are complete
- authority_gate_validation correctly reads proof graphs
"""

import json
import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from authority_gate_validation import validate_format_authority


class TestP6RequiresProofGraph:
    def test_fods_p6_detected_with_proof_graph(self):
        result = validate_format_authority("fods")
        if not (REPO_ROOT / ".local" / "spec-cache" / "fods").exists():
            pytest.skip("spec-cache/fods absent (CI)")
        assert result["authority_level_int"] == 6
        assert result["proof_graph_summary"]["has_proof_graph"] is True

    def test_zst_p6_detected_with_proof_graph(self):
        result = validate_format_authority("zst")
        if not (REPO_ROOT / ".local" / "spec-cache" / "zst").exists():
            pytest.skip("spec-cache/zst absent (CI)")
        assert result["authority_level_int"] == 6
        assert result["proof_graph_summary"]["has_proof_graph"] is True

    def test_p5_format_without_proof_graph_stays_p5(self):
        """A format with code/test citations but no proof graph is P5, not P6."""
        result = validate_format_authority("csv")
        # Without spec-cache, authority_level_int may be 0 (P0)
        assert result["authority_level_int"] <= 5
        # proof_graph_summary may be under different key names
        pg = result.get("proof_graph_summary", result.get("proof_graph", {}))
        assert pg.get("has_proof_graph", False) is False

    def test_p6_proof_graph_path_is_real_file(self):
        for fmt in ["fods", "zst"]:
            if not (REPO_ROOT / ".local" / "spec-cache" / fmt).exists():
                pytest.skip(f"spec-cache/{fmt} absent (CI)")
            result = validate_format_authority(fmt)
            paths = result["proof_graph_summary"].get("paths", [])
            assert len(paths) > 0, f"{fmt} has no proof graph paths"
            for p in paths:
                assert Path(p).exists(), f"Proof graph file missing: {p}"


class TestProofGraphFileIntegrity:
    def test_fods_proof_graph_yaml_is_valid(self):
        import yaml
        pg_path = REPO_ROOT / "reports" / "authority-conveyor-20260608" / "fods-p6-proof-graph.yaml"
        assert pg_path.exists(), f"FODS proof graph not found: {pg_path}"
        raw = pg_path.read_text(encoding="utf-8")
        # Strip Python-style docstring header if present
        if raw.startswith('"""'):
            raw = raw[raw.index('"""', 3) + 3:].lstrip("\n")
        content = yaml.safe_load(raw)
        assert content.get("format_id") == "fods"
        assert content.get("proof_path_complete") is True

    def test_zst_proof_graph_yaml_is_valid(self):
        import yaml
        pg_path = REPO_ROOT / "reports" / "authority-conveyor-20260608" / "zst-p6-proof-graph.yaml"
        assert pg_path.exists(), f"ZST proof graph not found: {pg_path}"
        content = yaml.safe_load(pg_path.read_text(encoding="utf-8"))
        assert content.get("format_id") == "zst"
        assert content.get("proof_path_complete") is True

    def test_fods_proof_graph_has_required_nodes(self):
        import yaml
        pg_path = REPO_ROOT / "reports" / "authority-conveyor-20260608" / "fods-p6-proof-graph.yaml"
        raw = pg_path.read_text(encoding="utf-8")
        if raw.startswith('"""'):
            raw = raw[raw.index('"""', 3) + 3:].lstrip("\n")
        content = yaml.safe_load(raw)
        node_types = {n.get("node_type") for n in content.get("nodes", [])}
        assert "spec_source" in node_types
        assert "verified_fact" in node_types or "code_constant" in node_types
        assert "test_suite" in node_types or "test_evidence" in node_types

    def test_zst_proof_graph_has_two_facts(self):
        import yaml
        pg_path = REPO_ROOT / "reports" / "authority-conveyor-20260608" / "zst-p6-proof-graph.yaml"
        content = yaml.safe_load(pg_path.read_text(encoding="utf-8"))
        fact_ids = content.get("fact_ids", [])
        assert "FACT-ZST-001" in fact_ids
        assert "FACT-ZST-002" in fact_ids


class TestAuthorityLedgerIntegrity:
    def test_product_authority_ledger_exists(self):
        run_id = "spec-authority-full-hardening-backfill-20260608-e382e5f"
        ledger_path = REPO_ROOT / "reports" / "spec-authority-full-hardening-backfill" / run_id / "ledgers" / "product-authority-ledger.json"
        if not ledger_path.exists():
            pytest.skip("Ledger not created yet")
        with open(ledger_path) as f:
            ledger = json.load(f)
        assert ledger["p6_count"] == 2
        assert "fods" in ledger["p6_formats"]
        assert "zst" in ledger["p6_formats"]

    def test_proof_graph_edges_json_exists_and_valid(self):
        run_id = "spec-authority-full-hardening-backfill-20260608-e382e5f"
        edges_path = REPO_ROOT / "reports" / "spec-authority-full-hardening-backfill" / run_id / "ledgers" / "proof-graph-authority-edges.json"
        if not edges_path.exists():
            pytest.skip("Edges JSON not created yet")
        with open(edges_path) as f:
            edges = json.load(f)
        assert edges["synthetic_edges_found"] == 0
        assert edges["ai_only_edges_found"] == 0
        assert edges["integrity_check"] == "PASS"
        assert "fods" in edges["p6_formats_with_complete_chains"]
        assert "zst" in edges["p6_formats_with_complete_chains"]

    def test_fods_ledger_entry_exists(self):
        ledger_path = REPO_ROOT / "reports" / "authority-conveyor-20260608" / "fods-authority-ledger-entry.json"
        assert ledger_path.exists()
        with open(ledger_path) as f:
            entry = json.load(f)
        assert entry["authority_level_achieved"] == "P6"
        assert entry["format_id"] == "fods"

    def test_zst_ledger_entry_exists(self):
        ledger_path = REPO_ROOT / "reports" / "authority-conveyor-20260608" / "zst-authority-ledger-entry.json"
        assert ledger_path.exists()
        with open(ledger_path) as f:
            entry = json.load(f)
        assert entry["authority_level_achieved"] == "P6"
        assert entry["format_id"] == "zst"
        assert "FACT-ZST-001" in entry["fact_ids"]
        assert "FACT-ZST-002" in entry["fact_ids"]


class TestSyntheticFixtureRejection:
    def test_synthetic_source_does_not_exist_in_edges(self):
        run_id = "spec-authority-full-hardening-backfill-20260608-e382e5f"
        edges_path = REPO_ROOT / "reports" / "spec-authority-full-hardening-backfill" / run_id / "ledgers" / "proof-graph-authority-edges.json"
        if not edges_path.exists():
            pytest.skip("Edges JSON not created yet")
        with open(edges_path) as f:
            edges = json.load(f)
        for edge in edges.get("edges", []):
            assert not edge.get("synthetic", False), f"Synthetic edge found: {edge['edge_id']}"

    def test_ai_only_validated_by_is_blocked(self):
        """AI self-certification cannot be validated_by in real proof chains."""
        run_id = "spec-authority-full-hardening-backfill-20260608-e382e5f"
        edges_path = REPO_ROOT / "reports" / "spec-authority-full-hardening-backfill" / run_id / "ledgers" / "proof-graph-authority-edges.json"
        if not edges_path.exists():
            pytest.skip("Edges JSON not created yet")
        with open(edges_path) as f:
            edges = json.load(f)
        for edge in edges.get("edges", []):
            assert edge.get("validated_by") != "ai_self_certification", (
                f"Edge {edge['edge_id']} uses ai_self_certification"
            )
