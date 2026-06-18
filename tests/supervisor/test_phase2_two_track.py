"""TC-H-003: pytest regression suite for Phase 2 two-track separation.

Covers all 8 Phase 2 behavioral paths (TC-P2-001 through TC-P2-008):
  T1: validate_ledger_entry_exists — 4 scenarios
  T2: check_track_health — both tracks
  T3: grade_declared_work cache_path parameter
  T4: write_track_handoff round-trip
  T5: autonomous_orchestrator stream filter
  T6: generate_next_worker_prompt TRACK_GROUPS
  T7: validate_ledger_entry CLI (subprocess)
"""
import json
import subprocess
import sys
import tempfile
from pathlib import Path

import pytest

# Ensure tools/supervisor is on sys.path for all tests
_REPO_ROOT = Path(__file__).parent.parent.parent
_SUPERVISOR = _REPO_ROOT / "tools" / "supervisor"
if str(_SUPERVISOR) not in sys.path:
    sys.path.insert(0, str(_SUPERVISOR))


# ---------------------------------------------------------------------------
# T1: validate_ledger_entry_exists
# ---------------------------------------------------------------------------

class TestValidateLedgerEntry:
    """T1: 4 scenarios for G3/G4/G5 ledger enforcement."""

    def _make_item(self, group: str, name: str = "test_item") -> dict:
        return {"item_id": name, "work_group": group, "status": "COMPLETE"}

    def test_no_product_items_passes_without_ledger(self, tmp_path):
        """Non-product items (G1/G8) should pass even with empty ledger."""
        from validate_ledger_entry import validate_ledger_entry_exists

        items = [self._make_item("G1"), self._make_item("G8")]
        ledger_path = tmp_path / "ledger.json"
        ledger_path.write_text("[]", encoding="utf-8")

        is_valid, missing, err = validate_ledger_entry_exists("sprint-001", items, ledger_path)

        assert is_valid is True, f"Expected valid for non-product items, got: {missing}"
        assert missing == []

    def test_g4_item_empty_ledger_fails(self, tmp_path):
        """G4 work item with empty ledger should fail validation."""
        from validate_ledger_entry import validate_ledger_entry_exists

        items = [self._make_item("G4", "g4_item_001")]
        ledger_path = tmp_path / "ledger.json"
        ledger_path.write_text("[]", encoding="utf-8")

        is_valid, missing, err = validate_ledger_entry_exists("sprint-002", items, ledger_path)

        assert is_valid is False
        assert len(missing) > 0

    def test_g4_item_valid_entry_passes(self, tmp_path):
        """G4 item with matching ledger entry (all required fields) should pass."""
        from validate_ledger_entry import validate_ledger_entry_exists

        sprint_id = "sprint-003"
        items = [self._make_item("G4", "g4_item_valid")]
        ledger_entry = {
            "capability": "test_capability",
            "format": "fods",
            "test_delta": 10,
            "git_head": "abc123def456",
            "sprint_id": sprint_id,
        }
        ledger_path = tmp_path / "ledger.json"
        ledger_path.write_text(json.dumps([ledger_entry]), encoding="utf-8")

        is_valid, missing, err = validate_ledger_entry_exists(sprint_id, items, ledger_path)

        assert is_valid is True, f"Expected valid with correct ledger entry, got: {missing}"
        assert missing == []

    def test_g3_item_missing_required_fields_fails(self, tmp_path):
        """G3 item with ledger entry missing required fields should fail."""
        from validate_ledger_entry import validate_ledger_entry_exists

        sprint_id = "sprint-004"
        items = [self._make_item("G3", "g3_item_incomplete")]
        # Missing 'git_head' and 'test_delta'
        ledger_entry = {
            "capability": "test_cap",
            "format": "fodt",
            "sprint_id": sprint_id,
        }
        ledger_path = tmp_path / "ledger.json"
        ledger_path.write_text(json.dumps([ledger_entry]), encoding="utf-8")

        is_valid, missing, err = validate_ledger_entry_exists(sprint_id, items, ledger_path)

        assert is_valid is False, "Expected failure for missing required fields"

    def test_g5_item_passes_with_valid_entry(self, tmp_path):
        """G5 items are also product work and require ledger entry."""
        from validate_ledger_entry import validate_ledger_entry_exists

        sprint_id = "sprint-005"
        items = [self._make_item("G5", "g5_dogfood")]
        ledger_entry = {
            "capability": "dogfood_export",
            "format": "zst",
            "test_delta": 5,
            "git_head": "deadbeef1234",
            "sprint_id": sprint_id,
        }
        ledger_path = tmp_path / "ledger.json"
        ledger_path.write_text(json.dumps([ledger_entry]), encoding="utf-8")

        is_valid, missing, err = validate_ledger_entry_exists(sprint_id, items, ledger_path)

        assert is_valid is True

    def test_product_work_groups_constant(self):
        """PRODUCT_WORK_GROUPS must contain exactly G3, G4, G5."""
        from validate_ledger_entry import PRODUCT_WORK_GROUPS

        assert "G3" in PRODUCT_WORK_GROUPS
        assert "G4" in PRODUCT_WORK_GROUPS
        assert "G5" in PRODUCT_WORK_GROUPS
        assert "G1" not in PRODUCT_WORK_GROUPS
        assert "G8" not in PRODUCT_WORK_GROUPS

    def test_required_fields_constant(self):
        """REQUIRED_FIELDS must contain all 5 mandatory ledger fields."""
        from validate_ledger_entry import REQUIRED_FIELDS

        for field in ("capability", "format", "test_delta", "git_head", "sprint_id"):
            assert field in REQUIRED_FIELDS, f"Missing required field: {field}"


# ---------------------------------------------------------------------------
# T2: check_track_health
# ---------------------------------------------------------------------------

class TestCheckTrackHealth:
    """T2: Per-track health check returns valid verdict dict."""

    def test_check_track_product_returns_verdict_dict(self, tmp_path):
        """check_track('product') returns a dict with required keys."""
        from check_track_health import check_track

        result = check_track("product", tmp_path)

        assert isinstance(result, dict)
        assert "track" in result
        assert "verdict" in result
        assert result["track"] == "product"
        assert result["verdict"] in ("HEALTHY", "WARNING", "CRITICAL")

    def test_check_track_machinery_returns_verdict_dict(self, tmp_path):
        """check_track('machinery') returns a dict with required keys."""
        from check_track_health import check_track

        result = check_track("machinery", tmp_path)

        assert isinstance(result, dict)
        assert result["track"] == "machinery"
        assert result["verdict"] in ("HEALTHY", "WARNING", "CRITICAL")

    def test_check_track_invalid_track_returns_critical(self, tmp_path):
        """Unknown track name returns CRITICAL verdict."""
        from check_track_health import check_track

        result = check_track("unknown_track_xyz", tmp_path)

        assert result["verdict"] == "CRITICAL"

    def test_check_track_has_findings_list(self, tmp_path):
        """Result always includes a findings list (even if empty)."""
        from check_track_health import check_track

        result = check_track("product", tmp_path)

        assert "findings" in result
        assert isinstance(result["findings"], list)

    def test_check_track_healthy_when_signal_present(self, tmp_path):
        """Track P with valid signal file should yield at least WARNING or HEALTHY."""
        from check_track_health import check_track
        from atomic_io import atomic_write_json

        prod_dir = tmp_path / ".local" / "supervisor" / "product"
        prod_dir.mkdir(parents=True, exist_ok=True)
        atomic_write_json(prod_dir / "continuation-signal.json", {
            "autonomous_continue": True,
            "iteration": 1,
            "track": "product",
            "session_id": "test-sid",
        })

        result = check_track("product", tmp_path)

        # Should not be CRITICAL when signal exists
        assert result["verdict"] in ("HEALTHY", "WARNING")


# ---------------------------------------------------------------------------
# T3: grade_declared_work cache_path parameter
# ---------------------------------------------------------------------------

class TestGradeDeclaredWorkCachePath:
    """T3: cache_path parameter routes grade cache to track-specific location."""

    def test_get_cached_grade_uses_provided_cache_path(self, tmp_path):
        """_get_cached_grade returns None (cache miss) for non-existent path."""
        from grade_declared_work import _get_cached_grade

        custom_path = tmp_path / "my-grade-cache.json"

        result = _get_cached_grade("item-001", "hash-aaa", cache_path=custom_path)

        assert result is None  # cache miss

    def test_cache_grade_writes_to_provided_cache_path(self, tmp_path):
        """_cache_grade writes to custom cache_path, not default location."""
        from grade_declared_work import _cache_grade, _get_cached_grade

        custom_path = tmp_path / "custom-cache.json"
        test_result = {"adequate": True, "confidence": 0.9, "source": "test"}

        _cache_grade("item-002", "hash-bbb", test_result, cache_path=custom_path)

        assert custom_path.exists(), "Cache file should be created at custom_path"

        # Verify round-trip
        cached = _get_cached_grade("item-002", "hash-bbb", cache_path=custom_path)
        assert cached is not None
        assert cached.get("adequate") is True

    def test_grade_all_accepts_grade_cache_path_param(self):
        """grade_all() function signature must accept grade_cache_path kwarg."""
        from grade_declared_work import grade_all
        import inspect

        sig = inspect.signature(grade_all)
        assert "grade_cache_path" in sig.parameters, (
            "grade_all must accept grade_cache_path parameter"
        )

    def test_cache_miss_returns_none_for_missing_item(self, tmp_path):
        """Cache hit for wrong item_id returns None."""
        from grade_declared_work import _cache_grade, _get_cached_grade

        cache_path = tmp_path / "test-cache.json"
        _cache_grade("item-001", "hash-aaa", {"adequate": True}, cache_path=cache_path)

        # Different item_id should miss
        result = _get_cached_grade("item-999", "hash-aaa", cache_path=cache_path)
        assert result is None

    def test_cache_miss_on_hash_change(self, tmp_path):
        """When evidence hash changes, cache must miss."""
        from grade_declared_work import _cache_grade, _get_cached_grade

        cache_path = tmp_path / "test-cache2.json"
        _cache_grade("item-003", "hash-original", {"adequate": True}, cache_path=cache_path)

        # Same item, different hash
        result = _get_cached_grade("item-003", "hash-changed", cache_path=cache_path)
        assert result is None


# ---------------------------------------------------------------------------
# T4: write_track_handoff round-trip
# ---------------------------------------------------------------------------

class TestWriteTrackHandoff:
    """T4: Track handoff protocol write/read round-trip."""

    def test_write_machinery_handoff_creates_correct_schema(self, tmp_path):
        """write_machinery_handoff creates track-handoff.json with version 1."""
        from write_track_handoff import write_machinery_handoff

        result = write_machinery_handoff(tmp_path)

        handoff_path = tmp_path / ".local" / "supervisor" / "shared" / "track-handoff.json"
        assert handoff_path.exists()

        hf = json.loads(handoff_path.read_text())
        assert hf.get("handoff_version") == 1
        assert "machinery_to_product" in hf

    def test_write_machinery_handoff_preserves_product_section(self, tmp_path):
        """Existing product_to_machinery section is preserved by machinery write."""
        from write_track_handoff import write_machinery_handoff
        from atomic_io import atomic_write_json

        shared_dir = tmp_path / ".local" / "supervisor" / "shared"
        shared_dir.mkdir(parents=True, exist_ok=True)
        handoff_path = shared_dir / "track-handoff.json"

        # Pre-write a product_to_machinery section
        atomic_write_json(handoff_path, {
            "handoff_version": 1,
            "product_to_machinery": {
                "sprint_id": "pre-existing-sprint",
                "new_capabilities_count": 3,
            }
        })

        write_machinery_handoff(tmp_path)

        hf = json.loads(handoff_path.read_text())
        assert "product_to_machinery" in hf, "product_to_machinery section should be preserved"
        assert hf["product_to_machinery"]["sprint_id"] == "pre-existing-sprint"

    def test_read_machinery_handoff_returns_none_when_missing(self, tmp_path):
        """read_machinery_handoff returns None when no handoff file exists."""
        from write_track_handoff import read_machinery_handoff

        result = read_machinery_handoff(tmp_path)

        assert result is None

    def test_write_then_read_round_trip(self, tmp_path):
        """Writing then reading machinery handoff returns the machinery_to_product dict."""
        from write_track_handoff import write_machinery_handoff, read_machinery_handoff

        write_machinery_handoff(tmp_path, session_id="test-session-xyz")

        # read_machinery_handoff returns the machinery_to_product section directly
        m2p = read_machinery_handoff(tmp_path)

        assert m2p is not None
        assert "written_at" in m2p
        assert "validated_gap_count" in m2p
        assert "high_priority_gap_count" in m2p

    def test_machinery_to_product_required_fields(self, tmp_path):
        """machinery_to_product section has all schema-required fields."""
        from write_track_handoff import write_machinery_handoff

        write_machinery_handoff(tmp_path)
        hf = json.loads(
            (tmp_path / ".local" / "supervisor" / "shared" / "track-handoff.json").read_text()
        )
        m2p = hf["machinery_to_product"]

        for field in ("written_at", "gap_ledger_snapshot_path", "validated_gap_count", "high_priority_gap_count"):
            assert field in m2p, f"Missing field in machinery_to_product: {field}"


# ---------------------------------------------------------------------------
# T5: autonomous_orchestrator stream filter
# ---------------------------------------------------------------------------

class TestOrchestratorStreamFilter:
    """T5: Stream filter _STREAM_ALLOWED table is correctly populated."""

    def test_stream_filter_machinery_rejects_product_stream_item(self):
        """'product' stream is not allowed for --stream machinery."""
        from autonomous_orchestrator import AutonomousOrchestrator

        allowed = AutonomousOrchestrator._STREAM_ALLOWED.get("machinery", set())
        assert "product" not in allowed, "Product stream should be rejected by machinery filter"

    def test_stream_filter_machinery_accepts_autonomy_stream_item(self):
        """'autonomy' stream is allowed for --stream machinery."""
        from autonomous_orchestrator import AutonomousOrchestrator

        allowed = AutonomousOrchestrator._STREAM_ALLOWED.get("machinery", set())
        assert "autonomy" in allowed, "Autonomy stream should be allowed for machinery"

    def test_stream_filter_product_accepts_product_stream(self):
        """'product' stream is allowed for --stream product."""
        from autonomous_orchestrator import AutonomousOrchestrator

        allowed = AutonomousOrchestrator._STREAM_ALLOWED.get("product", set())
        assert "product" in allowed

    def test_stream_filter_product_rejects_autonomy_stream(self):
        """'autonomy' stream is rejected for --stream product."""
        from autonomous_orchestrator import AutonomousOrchestrator

        allowed = AutonomousOrchestrator._STREAM_ALLOWED.get("product", set())
        assert "autonomy" not in allowed

    def test_stream_filter_all_accepts_any_stream_item(self):
        """'all' mode has empty set (no filtering — all streams pass)."""
        from autonomous_orchestrator import AutonomousOrchestrator

        allowed = AutonomousOrchestrator._STREAM_ALLOWED.get("all", set())
        assert allowed == set(), "all mode should have empty set (accept anything)"

    def test_stream_allowed_table_complete(self):
        """_STREAM_ALLOWED must contain exactly: machinery, product, all."""
        from autonomous_orchestrator import AutonomousOrchestrator

        keys = set(AutonomousOrchestrator._STREAM_ALLOWED.keys())
        assert "machinery" in keys
        assert "product" in keys
        assert "all" in keys

    def test_machinery_allowed_streams_include_evidence(self):
        """'evidence' stream is allowed for machinery (Track M evidence work)."""
        from autonomous_orchestrator import AutonomousOrchestrator

        allowed = AutonomousOrchestrator._STREAM_ALLOWED.get("machinery", set())
        assert "evidence" in allowed


# ---------------------------------------------------------------------------
# T6: generate_next_worker_prompt TRACK_GROUPS
# ---------------------------------------------------------------------------

class TestTrackGroups:
    """T6: TRACK_GROUPS constant correctly separates product and machinery groups."""

    def test_track_groups_product_has_g3_g4_g5(self):
        """Product track must contain G3, G4, G5 work groups."""
        from generate_next_worker_prompt import TRACK_GROUPS

        product_groups = set(TRACK_GROUPS.get("product", ()))
        assert "G3" in product_groups
        assert "G4" in product_groups
        assert "G5" in product_groups

    def test_track_groups_machinery_has_g1_g2_g6_g7_g8(self):
        """Machinery track must contain G1, G2, G6, G7, G8 work groups."""
        from generate_next_worker_prompt import TRACK_GROUPS

        machinery_groups = set(TRACK_GROUPS.get("machinery", ()))
        for g in ("G1", "G2", "G6", "G7", "G8"):
            assert g in machinery_groups, f"{g} missing from machinery TRACK_GROUPS"

    def test_track_groups_no_overlap(self):
        """No work group should appear in both product and machinery tracks."""
        from generate_next_worker_prompt import TRACK_GROUPS

        product = set(TRACK_GROUPS.get("product", ()))
        machinery = set(TRACK_GROUPS.get("machinery", ()))
        overlap = product & machinery

        assert overlap == set(), f"Work groups appear in both tracks: {overlap}"

    def test_track_groups_machinery_excludes_product_groups(self):
        """Machinery should not contain G3, G4, G5."""
        from generate_next_worker_prompt import TRACK_GROUPS

        machinery_groups = set(TRACK_GROUPS.get("machinery", ()))
        for g in ("G3", "G4", "G5"):
            assert g not in machinery_groups, f"Product group {g} in machinery track"

    def test_track_groups_product_excludes_machinery_groups(self):
        """Product should not contain G1, G2, G6, G7, G8."""
        from generate_next_worker_prompt import TRACK_GROUPS

        product_groups = set(TRACK_GROUPS.get("product", ()))
        for g in ("G1", "G2", "G6", "G7", "G8"):
            assert g not in product_groups, f"Machinery group {g} in product track"


# ---------------------------------------------------------------------------
# T7: validate_ledger_entry CLI
# ---------------------------------------------------------------------------

class TestValidateLedgerEntryCLI:
    """T7: CLI exits with correct code via subprocess.

    The CLI accepts --sprint-id, --ledger-path, and --declaration (YAML with work_items).
    No --work-groups argument; work groups are extracted from the declaration file.
    """

    def _make_declaration_yaml(self, path: Path, work_items: list, sprint_id: str) -> None:
        """Write a minimal declaration YAML for CLI testing.

        Uses 'planned_work_items' key as expected by validate_ledger_entry.py CLI.
        """
        items_yaml = "\n".join(
            f"  - item_id: {item['item_id']}\n    work_group: {item['work_group']}\n    status: COMPLETE"
            for item in work_items
        )
        content = f"sprint_id: {sprint_id}\nplanned_work_items:\n{items_yaml}\n"
        path.write_text(content, encoding="utf-8")

    def _run_cli(self, args: list, timeout: int = 30) -> subprocess.CompletedProcess:
        return subprocess.run(
            [sys.executable, str(_SUPERVISOR / "validate_ledger_entry.py")] + args,
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(_REPO_ROOT),
        )

    def test_cli_exits_0_when_no_product_items(self, tmp_path):
        """CLI exits 0 when declaration has no G3/G4/G5 items (only G1/G8)."""
        ledger = tmp_path / "ledger.json"
        ledger.write_text("[]", encoding="utf-8")
        decl = tmp_path / "declaration.yaml"
        self._make_declaration_yaml(decl, [
            {"item_id": "g1_item", "work_group": "G1"},
            {"item_id": "g8_item", "work_group": "G8"},
        ], "sprint-cli-001")

        result = self._run_cli([
            "--sprint-id", "sprint-cli-001",
            "--declaration", str(decl),
            "--ledger-path", str(ledger),
        ])

        assert result.returncode == 0, (
            f"Expected exit 0 for non-product items, got {result.returncode}. "
            f"stderr: {result.stderr}"
        )

    def test_cli_exits_7_when_product_item_missing_ledger(self, tmp_path):
        """CLI exits 7 when G4 work item has no ledger entry."""
        ledger = tmp_path / "ledger.json"
        ledger.write_text("[]", encoding="utf-8")
        decl = tmp_path / "declaration.yaml"
        self._make_declaration_yaml(decl, [
            {"item_id": "g4_item", "work_group": "G4"},
        ], "sprint-cli-002")

        result = self._run_cli([
            "--sprint-id", "sprint-cli-002",
            "--declaration", str(decl),
            "--ledger-path", str(ledger),
        ])

        assert result.returncode == 7, (
            f"Expected exit 7 (LEDGER_ENTRY_MISSING), got {result.returncode}. "
            f"stdout: {result.stdout}. stderr: {result.stderr}"
        )

    def test_cli_exits_0_when_valid_ledger_entry_present(self, tmp_path):
        """CLI exits 0 when all required fields are in the ledger entry."""
        sprint_id = "sprint-cli-003"
        ledger = tmp_path / "ledger.json"
        ledger.write_text(json.dumps([{
            "capability": "some_cap",
            "format": "fods",
            "test_delta": 5,
            "git_head": "abc123",
            "sprint_id": sprint_id,
        }]), encoding="utf-8")
        decl = tmp_path / "declaration.yaml"
        self._make_declaration_yaml(decl, [
            {"item_id": "g4_valid", "work_group": "G4"},
        ], sprint_id)

        result = self._run_cli([
            "--sprint-id", sprint_id,
            "--declaration", str(decl),
            "--ledger-path", str(ledger),
        ])

        assert result.returncode == 0, (
            f"Expected exit 0 with valid entry, got {result.returncode}. "
            f"stdout: {result.stdout}"
        )


# ---------------------------------------------------------------------------
# T8: action_queue.enqueue_front (TC-H-007)
# ---------------------------------------------------------------------------

class TestEnqueueFront:
    """TC-H-007: enqueue_front prevents silent item loss on stream filter rejection."""

    def test_enqueue_front_exists(self):
        """enqueue_front must be importable from action_queue."""
        from action_queue import enqueue_front
        assert callable(enqueue_front)

    def test_enqueue_front_inserts_at_position_zero(self, tmp_path, monkeypatch):
        """enqueue_front places item before all existing pending items."""
        from action_queue import enqueue, enqueue_front, _load_queue, _save_queue, QUEUE_PATH

        # Redirect queue path to tmp for test isolation
        test_queue = tmp_path / "test-queue.jsonl"
        monkeypatch.setattr("action_queue.QUEUE_PATH", test_queue)

        _save_queue([])

        from action_queue import make_queue_item
        item1 = make_queue_item("original_action", stream="product")
        enqueue(item1)

        item2 = make_queue_item("requeued_action", stream="autonomy")
        item2["_wrong_track_rejected"] = True
        enqueue_front(item2)

        items = _load_queue()
        assert len(items) == 2
        assert items[0]["action_type"] == "requeued_action"
        assert items[1]["action_type"] == "original_action"
        assert items[0].get("_wrong_track_rejected") is True

    def test_enqueue_front_preserves_wrong_track_annotation(self, tmp_path, monkeypatch):
        """Item re-queued via enqueue_front retains _wrong_track_rejected annotation."""
        from action_queue import enqueue_front, _load_queue, _save_queue, make_queue_item

        test_queue = tmp_path / "annotation-test-queue.jsonl"
        monkeypatch.setattr("action_queue.QUEUE_PATH", test_queue)
        _save_queue([])

        item = make_queue_item("rejected_action", stream="product")
        item["_wrong_track_rejected"] = True
        item["_rejected_by_stream"] = "machinery"
        enqueue_front(item)

        items = _load_queue()
        assert items[0].get("_wrong_track_rejected") is True
        assert items[0].get("_rejected_by_stream") == "machinery"
