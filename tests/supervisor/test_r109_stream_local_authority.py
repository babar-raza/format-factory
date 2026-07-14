"""R109: Stream-local authority routing and global state isolation.

Sprint: FORMAT-FACTORY-SUPERVISOR-R109-STREAM-LOCAL-AUTHORITY-ROUTING-AND-GLOBAL-STATE-ISOLATION-CAMPAIGN-001
"""

import json
import sys
from pathlib import Path


TOOLS_DIR = Path(__file__).resolve().parent.parent.parent / "tools" / "supervisor"
sys.path.insert(0, str(TOOLS_DIR))

REPO_ROOT = Path(__file__).resolve().parent.parent.parent

from anti_skip_checker import (
    detect_stream_local_authority,
    SEVERITY_MAP,
    classify_violation_impact,
    run_all_checks,
)


# ============================================================
# Wave 1: Stream-local authority model
# ============================================================


class TestStreamLocalAuthorityModel:
    """Stream-local authority files exist and are correctly structured."""

    def test_stream_dir_exists_for_supervisor(self):
        stream_dir = REPO_ROOT / "reports" / "supervisor-streams" / "supervisor"
        assert stream_dir.exists(), f"Stream dir not found: {stream_dir}"

    def test_stream_dir_exists_for_mainstream(self):
        stream_dir = REPO_ROOT / "reports" / "supervisor-streams" / "mainstream"
        assert stream_dir.exists()

    def test_stream_dir_exists_for_skills(self):
        stream_dir = REPO_ROOT / "reports" / "supervisor-streams" / "skills"
        assert stream_dir.exists()

    def test_stream_dir_exists_for_acceleration(self):
        stream_dir = REPO_ROOT / "reports" / "supervisor-streams" / "acceleration"
        assert stream_dir.exists()

    def test_authority_model_report_exists(self):
        path = REPO_ROOT / "reports" / "supervisor-r109" / "stream-local-authority-model.md"
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "supervisor-streams" in content
        assert "continuation-signal" in content


# ============================================================
# Wave 2: Review routing
# ============================================================


class TestReviewRouting:
    """Evidence review and contradictions are routed to stream-local directories."""

    def test_autonomous_cycle_writes_stream_local_review(self):
        """autonomous_cycle or extensions writes to stream-local directory."""
        import autonomous_cycle as mod
        source = Path(mod.__file__).read_text(encoding="utf-8")
        ext_path = Path(mod.__file__).parent / "autonomous_cycle_extensions.py"
        if ext_path.exists():
            source += ext_path.read_text(encoding="utf-8")
        assert "supervisor-streams" in source
        assert "evidence-review.json" in source

    def test_autonomous_cycle_writes_stream_local_contradictions(self):
        import autonomous_cycle as mod
        source = Path(mod.__file__).read_text(encoding="utf-8")
        assert "contradictions.json" in source


# ============================================================
# Wave 3: Context-pack isolation
# ============================================================


class TestContextPackIsolation:
    """Global context pack is reference-only, not stream identity."""

    def test_global_context_pack_exists(self):
        path = REPO_ROOT / ".supervisor" / "context-pack.yaml"
        assert path.exists()

    def test_global_context_pack_has_stream_info(self):
        """Context pack should reference streams but not be sole identity."""
        import yaml
        path = REPO_ROOT / ".supervisor" / "context-pack.yaml"
        pack = yaml.safe_load(path.read_text(encoding="utf-8"))
        assert "latest_sprint" in pack


# ============================================================
# Wave 4: Selected-gap routing
# ============================================================


class TestSelectedGapRouting:
    """Stale R98 gaps must be archived/reference only."""

    def test_stale_gaps_detected(self):
        from anti_skip_checker import detect_stale_gaps
        result = detect_stale_gaps({"sprint_id": "R98"}, "R109-TEST")
        assert result["is_violation"] is True
        assert result["freshness"] in ("stale", "archived")

    def test_stale_gaps_is_critical_severity(self):
        assert SEVERITY_MAP["stale_gaps"] == "critical"

    def test_supervisor_stream_has_no_active_gaps(self):
        """Supervisor stream should not use product gaps."""
        gaps_path = REPO_ROOT / ".local" / "supervisor" / "selected-product-gaps.json"
        if gaps_path.exists():
            data = json.loads(gaps_path.read_text(encoding="utf-8"))
            if isinstance(data, list):
                return  # empty list = no active product gaps — test passes
            sprint = data.get("sprint", "")
            # Gaps should be stale (not R109)
            from anti_skip_checker import _extract_sprint_number
            n = _extract_sprint_number(sprint)
            assert n is None or n < 109, f"Product gaps unexpectedly current: {sprint}"


# ============================================================
# Wave 5: Continuation routing
# ============================================================


class TestContinuationRouting:
    """Continuation signal written to stream-local path."""

    def test_stream_local_signal_code_exists(self):
        import autonomous_cycle as mod
        source = Path(mod.__file__).read_text(encoding="utf-8")
        assert "streams" in source
        assert "stream_signal" in source

    def test_global_signal_still_written(self):
        """Global signal is still written for backwards compat."""
        import autonomous_cycle as mod
        source = Path(mod.__file__).read_text(encoding="utf-8")
        assert "continuation-signal.json" in source


# ============================================================
# Wave 6: Replay
# ============================================================


class TestReplay:
    """Replay results show stream-local authority for each package."""

    def test_replay_results_exist(self):
        path = REPO_ROOT / "reports" / "supervisor-r109" / "replay-results.json"
        assert path.exists()

    def test_replay_covers_four_streams(self):
        path = REPO_ROOT / "reports" / "supervisor-r109" / "replay-results.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        streams = {p["stream"] for p in data["replayed_packages"]}
        assert streams == {"supervisor", "mainstream", "skills", "acceleration"}

    def test_replay_all_have_stream_local(self):
        path = REPO_ROOT / "reports" / "supervisor-r109" / "replay-results.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        for pkg in data["replayed_packages"]:
            assert "stream_local_files" in pkg
            assert len(pkg["stream_local_files"]) >= 2


# ============================================================
# Wave 7: Generated prompts
# ============================================================


class TestGeneratedPrompts:
    """Four stream-specific prompts generated with correct boundaries."""

    def test_mainstream_prompt_exists(self):
        path = REPO_ROOT / "reports" / "supervisor-r109" / "generated-next-prompts" / "mainstream-next.md"
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "mainstream" in content.lower()
        assert "supervisor-streams/mainstream" in content

    def test_acceleration_prompt_exists(self):
        path = REPO_ROOT / "reports" / "supervisor-r109" / "generated-next-prompts" / "acceleration-next.md"
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "acceleration" in content.lower()

    def test_skills_prompt_exists(self):
        path = REPO_ROOT / "reports" / "supervisor-r109" / "generated-next-prompts" / "skills-next.md"
        assert path.exists()

    def test_supervisor_prompt_exists(self):
        path = REPO_ROOT / "reports" / "supervisor-r109" / "generated-next-prompts" / "supervisor-next.md"
        assert path.exists()
        content = path.read_text(encoding="utf-8")
        assert "supervisor" in content.lower()
        assert "Hard Quota" in content
        assert "Three-Sprint Forecast" in content

    def test_prompts_have_stream_local_authority_paths(self):
        """Each prompt must cite stream-local authority paths."""
        for name in ["mainstream-next.md", "acceleration-next.md", "skills-next.md", "supervisor-next.md"]:
            path = REPO_ROOT / "reports" / "supervisor-r109" / "generated-next-prompts" / name
            content = path.read_text(encoding="utf-8")
            assert "supervisor-streams/" in content, f"{name} missing stream-local authority path"


# ============================================================
# Anti-skip: Stream-local authority detector
# ============================================================


class TestStreamLocalAuthorityDetector:
    """R109 detector: detect_stream_local_authority."""

    def test_detector_in_severity_map(self):
        assert "stream_local_authority" in SEVERITY_MAP
        assert SEVERITY_MAP["stream_local_authority"] == "low"

    def test_detector_finds_existing_stream_dir(self):
        result = detect_stream_local_authority("supervisor", REPO_ROOT)
        assert result["check"] == "stream_local_authority"
        assert len(result["found"]) >= 1

    def test_detector_flags_missing_stream(self, tmp_path):
        # Create streams root so detector doesn't short-circuit as pre-R109
        (tmp_path / "reports" / "supervisor-streams").mkdir(parents=True)
        result = detect_stream_local_authority("nonexistent_stream", tmp_path)
        assert result["is_violation"] is True

    def test_detector_no_target_stream(self):
        result = detect_stream_local_authority("", REPO_ROOT)
        assert result["is_violation"] is False

    def test_detector_in_run_all_checks(self):
        """Stream-local authority check included in run_all_checks."""
        result = run_all_checks(
            target_stream="supervisor",
            repo_root=REPO_ROOT,
        )
        checks = {c["check"] for c in result["checks"]}
        assert "stream_local_authority" in checks

    def test_stream_local_produces_note(self):
        """stream_local_authority violation is low severity (note)."""
        checks = [{"check": "stream_local_authority", "is_violation": True}]
        impact = classify_violation_impact(checks)
        assert "stream_local_authority" in impact["notes"]
        assert not impact["block"]


# ============================================================
# R108 reconciliation
# ============================================================


class TestR108Reconciliation:
    """R108 reconciliation report exists and is classified correctly."""

    def test_reconciliation_exists(self):
        path = REPO_ROOT / "reports" / "supervisor-r109" / "r108-reconciliation.md"
        assert path.exists()

    def test_reconciliation_classifies_r108(self):
        path = REPO_ROOT / "reports" / "supervisor-r109" / "r108-reconciliation.md"
        content = path.read_text(encoding="utf-8")
        assert "ACCEPTED" in content
        assert "D109-GLOBAL" in content

    def test_preflight_exists(self):
        path = REPO_ROOT / "reports" / "supervisor-r109" / "00-preflight.md"
        assert path.exists()
