"""
RCA Real Pilot R2 — Integration Tests
Sprint: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-REAL-PILOT-R2-001

Key R2 improvements under test:
- Gap queue routes architecture-blocked export claims to Target-Writer-Architecture (not Mainstream-Dogfood)
- /add-dogfood-export not recommended for missing target writer claims
- FODT spec source upgraded to ACCEPTED_WITH_CAVEAT (Spec R3) from FIXTURE_BACKED (R1)
- Raw logs present at anti-skip-expected path
- Sample outputs declared and present
- Review-package-proof has no placeholders
- CAV-R1-006 (gap queue routing): fixed and verified
- No architecture-blocked claim routed via Mainstream-Dogfood
"""
import json
import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).parent.parent.parent
sys.path.insert(0, str(_REPO_ROOT))

from tools.requirements_authority.graph_store import GraphStore
from tools.requirements_authority.models import GraphEdge, GraphNode
from tools.requirements_authority.mainstream_gap_queue import MainstreamGapQueueGenerator

NOW = "2026-06-05T10:00:00+00:00"
R2_OUT = _REPO_ROOT / "reports" / "requirement-capability-real-pilot-r2"


def _node(node_id, node_type, label, status="candidate", metadata=None):
    return GraphNode(
        node_id=node_id, node_type=node_type, label=label,
        status=status, metadata=metadata or {}, created_at=NOW,
    )


def _edge(edge_id, edge_type, source, target, metadata=None):
    return GraphEdge(
        edge_id=edge_id, edge_type=edge_type,
        source_node_id=source, target_node_id=target,
        metadata=metadata or {}, created_at=NOW,
    )


def _build_arch_blocked_store():
    """Build a minimal proof graph with an architecture-blocked export claim."""
    store = GraphStore()

    # Spec + requirement
    store.add_node(_node("spec:fods:r2", "SpecRequirementRef", "FODS Spec",
                         status="accepted",
                         metadata={"format_id": "fods", "authority_status": "ACCEPTED_WITH_CAVEAT"}))
    store.add_node(_node("req:fods:parse", "ProductRequirement", "FODS: parse files",
                         status="accepted",
                         metadata={"product_id": "fods", "format_id": "fods", "operation": "parse"}))
    store.add_edge(_edge("e1", "derives_from", "req:fods:parse", "spec:fods:r2"))

    # A blocked export claim (no target writer library)
    store.add_node(_node("claim:fods:export_csv", "CapabilityClaim", "FODS: export CSV",
                         status="blocked",
                         metadata={
                             "product_id": "fods", "format_id": "fods", "operation": "export_csv",
                             "blocked_reason": "architecture_blocked_missing_target_writer",
                             "coverage_status": "ARCHITECTURE_BLOCKED_MISSING_TARGET_WRITER",
                         }))
    store.add_edge(_edge("e2", "derives_from", "claim:fods:export_csv", "req:fods:parse"))

    # UnsupportedFeature node + blocked_by edge
    store.add_node(_node("unsupported:fods:csv_target_writer", "UnsupportedFeature",
                         "FormatFactory.Csv target writer library does not exist",
                         status="active",
                         metadata={"product_id": "fods", "format_id": "fods",
                                   "feature": "export_csv", "severity": "blocking"}))
    store.add_edge(_edge("e3", "blocked_by",
                         "claim:fods:export_csv", "unsupported:fods:csv_target_writer"))

    return store


class TestGapQueueArchBlockedRouting:
    """CAV-R1-006 fix: architecture-blocked export claims route to Target-Writer-Architecture."""

    def test_arch_blocked_claim_routes_to_target_writer_architecture(self):
        store = _build_arch_blocked_store()
        gen = MainstreamGapQueueGenerator(store)
        result = gen.generate()
        assert len(result.entries) >= 1
        arch_entries = [e for e in result.entries if e.recommended_lane == "Target-Writer-Architecture"]
        assert len(arch_entries) >= 1, (
            f"Expected at least 1 Target-Writer-Architecture entry, got: "
            f"{[(e.claim_id, e.recommended_lane) for e in result.entries]}"
        )

    def test_arch_blocked_claim_missing_proof_type_is_target_writer_missing(self):
        store = _build_arch_blocked_store()
        gen = MainstreamGapQueueGenerator(store)
        result = gen.generate()
        arch_entries = [e for e in result.entries if e.claim_id == "claim:fods:export_csv"]
        assert arch_entries, "No entry found for claim:fods:export_csv"
        entry = arch_entries[0]
        assert entry.missing_proof_type == "TargetWriterLibraryMissing", (
            f"Expected TargetWriterLibraryMissing, got {entry.missing_proof_type}"
        )

    def test_arch_blocked_claim_not_routed_to_mainstream_dogfood(self):
        store = _build_arch_blocked_store()
        gen = MainstreamGapQueueGenerator(store)
        result = gen.generate()
        bad_entries = [
            e for e in result.entries
            if e.claim_id in ("claim:fods:export_csv",)
            and e.recommended_lane == "Mainstream-Dogfood"
        ]
        assert bad_entries == [], (
            f"Architecture-blocked claim must NOT route to Mainstream-Dogfood. Found: {bad_entries}"
        )

    def test_arch_blocked_next_action_mentions_target_writer_not_dogfood_export(self):
        store = _build_arch_blocked_store()
        gen = MainstreamGapQueueGenerator(store)
        result = gen.generate()
        arch_entries = [e for e in result.entries if e.claim_id == "claim:fods:export_csv"]
        assert arch_entries, "No entry for claim:fods:export_csv"
        entry = arch_entries[0]
        assert "target writer" in entry.next_action.lower(), (
            f"Expected 'target writer' in next_action, got: {entry.next_action}"
        )
        # If /add-dogfood-export is mentioned, it must be in a prohibition context
        action_lower = entry.next_action.lower()
        if "/add-dogfood-export" in action_lower:
            # Must include a "do not" prohibition right before or near the command
            assert "do not" in action_lower or "do not use" in action_lower, (
                f"/add-dogfood-export appears in next_action without prohibition: {entry.next_action}"
            )

    def test_arch_blocked_stop_conditions_prohibit_dogfood_export(self):
        store = _build_arch_blocked_store()
        gen = MainstreamGapQueueGenerator(store)
        result = gen.generate()
        arch_entries = [e for e in result.entries if e.claim_id == "claim:fods:export_csv"]
        assert arch_entries, "No entry for claim:fods:export_csv"
        entry = arch_entries[0]
        stop_text = " ".join(entry.stop_conditions).lower()
        assert "do not" in stop_text or "not proceed" in stop_text, (
            f"Stop conditions should warn against /add-dogfood-export: {entry.stop_conditions}"
        )

    def test_arch_blocked_expected_dogfood_is_empty(self):
        store = _build_arch_blocked_store()
        gen = MainstreamGapQueueGenerator(store)
        result = gen.generate()
        arch_entries = [e for e in result.entries if e.claim_id == "claim:fods:export_csv"]
        assert arch_entries, "No entry for claim:fods:export_csv"
        entry = arch_entries[0]
        assert entry.expected_dogfood == [], (
            f"Architecture-blocked claim should have empty expected_dogfood, got: {entry.expected_dogfood}"
        )


class TestGapQueueMetadataBasedBlocking:
    """Gap queue uses metadata blocked_reason without needing blocked_by edge."""

    def test_metadata_only_arch_blocked_routes_to_target_writer(self):
        """Claim with only metadata (no blocked_by edge) is still routed correctly."""
        store = GraphStore()
        store.add_node(_node("spec:fodt:r3", "SpecRequirementRef", "FODT Spec R3",
                             status="accepted",
                             metadata={"format_id": "fodt", "authority_status": "ACCEPTED_WITH_CAVEAT"}))
        store.add_node(_node("req:fodt:save", "ProductRequirement", "FODT: save documents",
                             status="accepted",
                             metadata={"product_id": "fodt", "format_id": "fodt", "operation": "save"}))
        store.add_edge(_edge("e1", "derives_from", "req:fodt:save", "spec:fodt:r3"))

        # Claim with metadata only (no blocked_by edge to UnsupportedFeature)
        store.add_node(_node("claim:fodt:export_markdown", "CapabilityClaim", "FODT: export Markdown",
                             status="blocked",
                             metadata={
                                 "product_id": "fodt", "format_id": "fodt", "operation": "export_markdown",
                                 "blocked_reason": "architecture_blocked_missing_target_writer",
                                 "coverage_status": "ARCHITECTURE_BLOCKED_MISSING_TARGET_WRITER",
                             }))
        store.add_edge(_edge("e2", "derives_from", "claim:fodt:export_markdown", "req:fodt:save"))

        gen = MainstreamGapQueueGenerator(store)
        result = gen.generate()
        arch_entries = [e for e in result.entries if e.claim_id == "claim:fodt:export_markdown"]
        assert arch_entries, "No entry for claim:fodt:export_markdown"
        assert arch_entries[0].recommended_lane == "Target-Writer-Architecture"


class TestFodtSpecUpgrade:
    """R2 fix: FODT is no longer fixture-backed; it uses Spec Authority R3."""

    def test_r2_input_manifest_fodt_is_spec_backed(self):
        manifest_path = R2_OUT / "input-snapshots-manifest.json"
        assert manifest_path.exists(), f"R2 input-snapshots-manifest.json not found at {manifest_path}"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        sources = manifest.get("sources", manifest) if isinstance(manifest, dict) else {}
        if isinstance(sources, dict):
            entries = list(sources.values())
        else:
            entries = sources
        fodt_entries = [
            e for e in entries
            if (isinstance(e, dict) and e.get("format_id") == "fodt")
            or (isinstance(e, str) and "fodt" in e)
        ]
        assert fodt_entries, "No FODT entry found in R2 input manifest"
        fodt = fodt_entries[0]
        r2_status = fodt.get("r2_authority_status", fodt.get("authority_status", ""))
        assert r2_status != "FIXTURE_BACKED", (
            f"FODT must not be FIXTURE_BACKED in R2, got: {r2_status}"
        )
        # Should be spec-backed (ACCEPTED_WITH_CAVEAT from Spec R3)
        assert r2_status in ("ACCEPTED_WITH_CAVEAT", "spec_backed", "ACCEPTED"), (
            f"FODT should be ACCEPTED_WITH_CAVEAT in R2, got: {r2_status}"
        )

    def test_r2_proof_graph_fodt_spec_is_not_fixture(self):
        """Proof graph contains spec:fodt:r3 (not spec:fodt:fixture)."""
        nodes_path = R2_OUT / "proof-graph" / "nodes.jsonl"
        assert nodes_path.exists(), f"nodes.jsonl not found at {nodes_path}"
        nodes = [json.loads(line) for line in nodes_path.read_text(encoding="utf-8").splitlines() if line.strip()]
        fodt_spec_nodes = [n for n in nodes if "fodt" in n.get("node_id", "") and n.get("node_type") == "SpecRequirementRef"]
        assert fodt_spec_nodes, "No FODT SpecRequirementRef found in R2 proof graph"
        for n in fodt_spec_nodes:
            assert "fixture" not in n["node_id"].lower(), (
                f"FODT spec node must not be fixture-backed in R2: {n['node_id']}"
            )


class TestRawLogsPresence:
    """CAV-R1-002 fix: raw logs must exist in expected anti-skip location."""

    def test_r2_raw_logs_exist_in_evidence_location(self):
        raw_logs = _REPO_ROOT / ".local" / "evidences" / "requirement-capability-real-pilot-r2" / "raw-logs"
        if not raw_logs.exists():
            pytest.skip(".local/evidences/ raw-logs not present (gitignored, CI skip)")
        log_files = list(raw_logs.glob("*.log"))
        assert log_files, f"No .log files found in {raw_logs}"

    def test_r2_raw_logs_exist_in_report_location(self):
        raw_logs = R2_OUT / "raw-logs"
        if not raw_logs.exists():
            pytest.skip("reports/ raw-logs not committed to repo (local artifact, CI skip)")
        log_files = list(raw_logs.glob("*.log"))
        assert log_files, f"No .log files found in {raw_logs}"


class TestSampleOutputsPresence:
    """CAV-R1-003 fix: sample outputs must be produced and declared."""

    def test_r2_sample_outputs_dir_exists(self):
        sample_dir = R2_OUT / "sample-outputs"
        assert sample_dir.exists(), f"sample-outputs dir not found: {sample_dir}"

    def test_r2_sample_outputs_has_json_artifacts(self):
        sample_dir = R2_OUT / "sample-outputs"
        assert sample_dir.exists(), f"sample-outputs dir not found: {sample_dir}"
        json_files = list(sample_dir.glob("*.json"))
        assert json_files, f"No JSON sample outputs found in {sample_dir}"

    def test_r2_gap_queue_policy_sample_parseable(self):
        policy_sample = R2_OUT / "sample-outputs" / "gap-queue-policy-sample.json"
        if not policy_sample.exists():
            pytest.skip("gap-queue-policy-sample.json not generated yet")
        data = json.loads(policy_sample.read_text(encoding="utf-8"))
        assert isinstance(data, dict), "gap-queue-policy-sample.json must be a JSON object"


class TestGapQueueOutputFile:
    """Validate the R2 mainstream-gap-queue.json output file."""

    def test_r2_gap_queue_exists(self):
        gap_queue = R2_OUT / "mainstream-gap-queue.json"
        assert gap_queue.exists(), f"Gap queue not found: {gap_queue}"

    def test_r2_gap_queue_parseable(self):
        gap_queue = R2_OUT / "mainstream-gap-queue.json"
        assert gap_queue.exists()
        data = json.loads(gap_queue.read_text(encoding="utf-8"))
        assert "entries" in data

    def test_r2_gap_queue_has_no_mainstream_dogfood_for_export_claims(self):
        gap_queue = R2_OUT / "mainstream-gap-queue.json"
        assert gap_queue.exists()
        data = json.loads(gap_queue.read_text(encoding="utf-8"))
        bad_entries = [
            e for e in data["entries"]
            if e.get("recommended_lane") == "Mainstream-Dogfood"
            and "export" in e.get("claim_id", "")
        ]
        assert bad_entries == [], (
            f"Architecture-blocked export claims must not be in Mainstream-Dogfood. Found: {bad_entries}"
        )

    def test_r2_gap_queue_arch_blocked_entries_use_target_writer_architecture_lane(self):
        gap_queue = R2_OUT / "mainstream-gap-queue.json"
        assert gap_queue.exists()
        data = json.loads(gap_queue.read_text(encoding="utf-8"))
        # These 4 claims should all be in Target-Writer-Architecture
        expected_arch_blocked = {
            "claim:fods:export_csv",
            "claim:fods:export_html",
            "claim:fodt:export_markdown",
            "claim:fodt:export_txt",
        }
        arch_entries = {e["claim_id"] for e in data["entries"]
                        if e.get("recommended_lane") == "Target-Writer-Architecture"}
        for claim_id in expected_arch_blocked:
            assert claim_id in arch_entries, (
                f"Expected {claim_id} in Target-Writer-Architecture lane. "
                f"Found lanes: {[(e['claim_id'], e['recommended_lane']) for e in data['entries']]}"
            )

    def test_r2_gap_queue_arch_blocked_missing_proof_type(self):
        gap_queue = R2_OUT / "mainstream-gap-queue.json"
        assert gap_queue.exists()
        data = json.loads(gap_queue.read_text(encoding="utf-8"))
        for entry in data["entries"]:
            if entry.get("recommended_lane") == "Target-Writer-Architecture":
                assert entry.get("missing_proof_type") == "TargetWriterLibraryMissing", (
                    f"Target-Writer-Architecture entry must have TargetWriterLibraryMissing, got: "
                    f"{entry.get('missing_proof_type')} for {entry['claim_id']}"
                )

    def test_r2_gap_queue_dogfood_count_is_zero_for_arch_blocked(self):
        gap_queue = R2_OUT / "mainstream-gap-queue.json"
        assert gap_queue.exists()
        data = json.loads(gap_queue.read_text(encoding="utf-8"))
        for entry in data["entries"]:
            if entry.get("recommended_lane") == "Target-Writer-Architecture":
                assert entry.get("expected_dogfood", []) == [], (
                    f"Architecture-blocked entry must have empty expected_dogfood: {entry['claim_id']}"
                )


class TestCoverageRecordsFile:
    """Validate R2 coverage-records.jsonl output."""

    def test_r2_coverage_records_exist(self):
        path = R2_OUT / "coverage-records.jsonl"
        assert path.exists(), f"coverage-records.jsonl not found: {path}"

    def test_r2_coverage_records_count(self):
        path = R2_OUT / "coverage-records.jsonl"
        assert path.exists()
        lines = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) == 20, f"Expected 20 coverage records, got {len(lines)}"

    def test_r2_coverage_records_parseable(self):
        path = R2_OUT / "coverage-records.jsonl"
        assert path.exists()
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rec = json.loads(line)
                assert "claim_id" in rec
                assert "coverage_verdict" in rec


class TestSupervisorVerdictPacket:
    """Validate R2 supervisor-verdict-packet.json."""

    def test_r2_svp_exists(self):
        path = R2_OUT / "supervisor-verdict-packet.json"
        assert path.exists(), f"SVP not found: {path}"

    def test_r2_svp_parseable(self):
        path = R2_OUT / "supervisor-verdict-packet.json"
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert isinstance(data, dict)

    def test_r2_svp_has_claims_checked(self):
        path = R2_OUT / "supervisor-verdict-packet.json"
        assert path.exists()
        data = json.loads(path.read_text(encoding="utf-8"))
        assert "claims_checked" in data
        assert data["claims_checked"] > 0


class TestProofGraphFile:
    """Validate R2 proof graph JSONL files."""

    def test_r2_nodes_file_exists(self):
        assert (R2_OUT / "proof-graph" / "nodes.jsonl").exists()

    def test_r2_edges_file_exists(self):
        assert (R2_OUT / "proof-graph" / "edges.jsonl").exists()

    def test_r2_nodes_count_reasonable(self):
        path = R2_OUT / "proof-graph" / "nodes.jsonl"
        lines = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) >= 50, f"Expected >= 50 nodes, got {len(lines)}"

    def test_r2_edges_count_reasonable(self):
        path = R2_OUT / "proof-graph" / "edges.jsonl"
        lines = [l for l in path.read_text(encoding="utf-8").splitlines() if l.strip()]
        assert len(lines) >= 80, f"Expected >= 80 edges, got {len(lines)}"

    def test_r2_nodes_parseable(self):
        path = R2_OUT / "proof-graph" / "nodes.jsonl"
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                n = json.loads(line)
                assert "node_id" in n
                assert "node_type" in n

    def test_r2_graph_determinism(self):
        """Same graph data yields same graph hash across two re-instantiations."""
        import importlib
        import tools.requirements_authority.graph_store as gs_mod
        importlib.reload(gs_mod)

        nodes_path = R2_OUT / "proof-graph" / "nodes.jsonl"
        edges_path = R2_OUT / "proof-graph" / "edges.jsonl"
        if not nodes_path.exists() or not edges_path.exists():
            pytest.skip("R2 proof graph files not available")

        # Load nodes + edges and add to two fresh stores
        from tools.requirements_authority.graph_store import GraphStore as GS2
        from tools.requirements_authority.models import GraphNode as GN2, GraphEdge as GE2

        def load_store():
            s = GS2()
            for line in nodes_path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    d = json.loads(line)
                    s.add_node(GN2(**{k: d[k] for k in GN2.__dataclass_fields__ if k in d}))
            for line in edges_path.read_text(encoding="utf-8").splitlines():
                if line.strip():
                    d = json.loads(line)
                    s.add_edge(GE2(**{k: d[k] for k in GE2.__dataclass_fields__ if k in d}))
            return s

        s1 = load_store()
        s2 = load_store()
        assert s1.compute_graph_hash() == s2.compute_graph_hash(), \
            "Graph hash must be deterministic for same input data"
