"""
test_format_context_resolver.py

Tests for tools/skills/format_context_resolver.py

Covers:
- FODS and FODT return REQUIREMENTS_AUTHORITATIVE (post-Lane-A registry update)
- REQUIREMENTS_MISSING for unknown formats
- REQUIREMENTS_GENERATED_UNVERIFIED for missing verifier-review
- REQUIREMENTS_VERIFIED_NO_IV when verifier passes but no iv_status
- BLOCKED when iv_status = FAIL
- FODT-REQ-040 critical constraint surfaced
- Gate 11 NOT approved → commercial_product_ready always False
- Resolver is read-only (no mutations)

Run:
  PYTHONPATH=C:/Users/prora/AppData/Roaming/Python/Python313/site-packages python -m pytest tests/skills -v
"""

import json
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT / "tools" / "skills"))

from format_context_resolver import (
    resolve_format_context,
    _resolve_requirements_state,
)


# ============================================================
# Helpers
# ============================================================

def _write_yaml(path: Path, data: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(data, encoding="utf-8")


MINIMAL_COMMERCIAL_REQS = """\
format: fods
schema_version: "1.0"
requirements:
  - requirement_id: FODS-REQ-001
    format: fods
    capability_level: C4
    requirement_type: object_model
    title: FodsDocument class
    description: Load FODS.
    source_type: EXISTING_SOURCE
    status: ACCEPTED_FOR_VERTICAL_SLICE
"""

MINIMAL_OBJECT_MODEL_REQS = """\
format: fods
schema_version: "1.0"
requirements: []
"""

MINIMAL_SAVE_EDIT_REQS = """\
format: fods
schema_version: "1.0"
requirements: []
"""

MINIMAL_CONVERSION_REQS = """\
format: fods
schema_version: "1.0"
requirements: []
"""

MINIMAL_TRACEABILITY = """\
format: fods
schema_version: "1.0"
accepted_for_vertical_slice:
  - FODS-REQ-001
deferred:
  []
AI_PROPOSAL: 0
"""

VERIFIER_PASS = """\
format: fods
schema_version: "1.0"
verifier_verdict:
  result: LANE_R5_PASS
  implementation_authorization:
    status: AUTHORIZED
"""

VERIFIER_FAIL = """\
format: fods
schema_version: "1.0"
verifier_verdict:
  result: LANE_R5_FAIL
  implementation_authorization:
    status: BLOCKED
"""


def _make_complete_requirements_dir(tmpdir: Path, fmt: str = "fods",
                                    verifier_yaml: str = None) -> Path:
    """Create a complete requirements directory for a format in tmpdir."""
    fmt_dir = tmpdir / "generated-requirements" / fmt
    fmt_dir.mkdir(parents=True, exist_ok=True)
    _write_yaml(fmt_dir / "commercial-requirements.yaml", MINIMAL_COMMERCIAL_REQS)
    _write_yaml(fmt_dir / "object-model-requirements.yaml", MINIMAL_OBJECT_MODEL_REQS)
    _write_yaml(fmt_dir / "save-edit-requirements.yaml", MINIMAL_SAVE_EDIT_REQS)
    _write_yaml(fmt_dir / "conversion-requirements.yaml", MINIMAL_CONVERSION_REQS)
    _write_yaml(fmt_dir / "traceability-map.yaml", MINIMAL_TRACEABILITY)
    _write_yaml(fmt_dir / "verifier-review.yaml", verifier_yaml or VERIFIER_PASS)
    return fmt_dir


# ============================================================
# Class 1: Live FODS/FODT resolution (real repo files)
# ============================================================

class TestLiveResolution:
    """Tests against actual repo files — require FODS/FODT requirements to exist."""

    def test_fods_returns_requirements_authoritative(self):
        ctx = resolve_format_context("fods")
        assert ctx["requirements_state"]["status"] == "REQUIREMENTS_AUTHORITATIVE", (
            f"Expected REQUIREMENTS_AUTHORITATIVE, got {ctx['requirements_state']['status']}; "
            f"blocker: {ctx['requirements_state'].get('blocker_reason')}"
        )

    def test_fodt_returns_requirements_authoritative(self):
        ctx = resolve_format_context("fodt")
        assert ctx["requirements_state"]["status"] == "REQUIREMENTS_AUTHORITATIVE", (
            f"Expected REQUIREMENTS_AUTHORITATIVE, got {ctx['requirements_state']['status']}; "
            f"blocker: {ctx['requirements_state'].get('blocker_reason')}"
        )

    def test_fods_iv_status_is_pass(self):
        ctx = resolve_format_context("fods")
        assert ctx["requirements_state"]["iv_status"] == "PASS"

    def test_fodt_iv_status_is_pass(self):
        ctx = resolve_format_context("fodt")
        assert ctx["requirements_state"]["iv_status"] == "PASS"

    def test_fods_verifier_result_is_lane_r5_pass(self):
        ctx = resolve_format_context("fods")
        assert ctx["requirements_state"]["verifier_result"] == "LANE_R5_PASS"

    def test_fodt_verifier_result_is_lane_r5_pass(self):
        ctx = resolve_format_context("fodt")
        assert ctx["requirements_state"]["verifier_result"] == "LANE_R5_PASS"

    def test_fods_accepted_count_is_20(self):
        ctx = resolve_format_context("fods")
        assert ctx["requirements_state"]["accepted_count"] == 20

    def test_fodt_accepted_count_is_20(self):
        ctx = resolve_format_context("fodt")
        assert ctx["requirements_state"]["accepted_count"] == 20

    def test_fods_gates_passed_is_10(self):
        ctx = resolve_format_context("fods")
        assert ctx["gate_state"]["gates_passed"] == 10

    def test_fodt_gates_passed_is_10(self):
        ctx = resolve_format_context("fodt")
        assert ctx["gate_state"]["gates_passed"] == 10

    def test_fods_gate_11_not_approved(self):
        ctx = resolve_format_context("fods")
        assert ctx["gate_state"]["gate_11_status"] == "commercial_readiness_in_progress"

    def test_fodt_gate_11_not_approved(self):
        ctx = resolve_format_context("fodt")
        assert ctx["gate_state"]["gate_11_status"] == "commercial_readiness_in_progress"

    def test_fods_commercial_product_ready_false(self):
        ctx = resolve_format_context("fods")
        assert ctx["gate_state"]["commercial_product_ready"] is False
        assert ctx["governance"]["commercial_product_ready"] is False

    def test_fodt_commercial_product_ready_false(self):
        ctx = resolve_format_context("fodt")
        assert ctx["gate_state"]["commercial_product_ready"] is False
        assert ctx["governance"]["commercial_product_ready"] is False

    def test_gate_self_approval_not_allowed(self):
        ctx = resolve_format_context("fods")
        assert ctx["governance"]["gate_self_approval_allowed"] is False

    def test_autonomous_implementation_not_allowed(self):
        ctx = resolve_format_context("fods")
        assert ctx["governance"]["autonomous_implementation_allowed"] is False

    def test_fodt_req_040_constraint_surfaced(self):
        ctx = resolve_format_context("fodt")
        constraints = ctx["known_constraints"]
        assert len(constraints) >= 1, "FODT must surface at least 1 critical constraint"
        constraint_texts = " ".join(
            c.get("constraint", "") for c in constraints
        )
        assert "iterative" in constraint_texts.lower() or "FODT-REQ-040" in str(constraints), (
            f"FODT-REQ-040 iterative constraint not found in: {constraints}"
        )

    def test_resolver_returns_dict(self):
        ctx = resolve_format_context("fods")
        assert isinstance(ctx, dict)
        assert "format_id" in ctx
        assert "requirements_state" in ctx
        assert "gate_state" in ctx
        assert "known_constraints" in ctx
        assert "governance" in ctx

    def test_resolver_json_serializable(self):
        ctx = resolve_format_context("fods")
        dumped = json.dumps(ctx)
        assert isinstance(dumped, str)


# ============================================================
# Class 2: State machine isolation tests (temp dirs)
# ============================================================

class TestStateMachineIsolation:
    """Isolated tests using temp directories — no dependency on live repo files."""

    def setup_method(self):
        self._tmpdir = Path(tempfile.mkdtemp())

    def teardown_method(self):
        shutil.rmtree(self._tmpdir, ignore_errors=True)

    def _patch_reqs_dir(self, reqs_dir: Path):
        """Patch REQS_DIR in the resolver module."""
        import format_context_resolver as resolver_mod
        return patch.object(resolver_mod, "REQS_DIR", reqs_dir)

    def test_missing_format_returns_requirements_missing(self):
        reqs_dir = self._tmpdir / "generated-requirements"
        reqs_dir.mkdir()
        with self._patch_reqs_dir(reqs_dir):
            state = _resolve_requirements_state("nonexistent_format_xyz")
        assert state["status"] == "REQUIREMENTS_MISSING"
        assert state["blocker_reason"] is not None

    def test_partial_files_returns_generated_unverified(self):
        reqs_dir = self._tmpdir / "generated-requirements"
        fmt_dir = reqs_dir / "testfmt"
        fmt_dir.mkdir(parents=True)
        # Only create 3 of 6 required files
        _write_yaml(fmt_dir / "commercial-requirements.yaml", MINIMAL_COMMERCIAL_REQS)
        _write_yaml(fmt_dir / "object-model-requirements.yaml", MINIMAL_OBJECT_MODEL_REQS)
        _write_yaml(fmt_dir / "save-edit-requirements.yaml", MINIMAL_SAVE_EDIT_REQS)
        with self._patch_reqs_dir(reqs_dir):
            state = _resolve_requirements_state("testfmt")
        assert state["status"] == "REQUIREMENTS_GENERATED_UNVERIFIED"
        assert len(state["missing_files"]) > 0

    def test_lane_r5_fail_returns_generated_unverified(self):
        reqs_dir = self._tmpdir / "generated-requirements"
        _make_complete_requirements_dir(self._tmpdir, fmt="testfmt", verifier_yaml=VERIFIER_FAIL)
        with self._patch_reqs_dir(reqs_dir):
            state = _resolve_requirements_state("testfmt")
        assert state["status"] == "REQUIREMENTS_GENERATED_UNVERIFIED"
        assert state["verifier_result"] == "LANE_R5_FAIL"

    def test_no_iv_status_returns_verified_no_iv(self):
        reqs_dir = self._tmpdir / "generated-requirements"
        _make_complete_requirements_dir(self._tmpdir, fmt="testfmt")
        # No registry_iv_override provided → no IV → REQUIREMENTS_VERIFIED_NO_IV
        with self._patch_reqs_dir(reqs_dir):
            state = _resolve_requirements_state("testfmt")
        assert state["status"] == "REQUIREMENTS_VERIFIED_NO_IV"
        assert state["verifier_result"] == "LANE_R5_PASS"
        assert state["iv_status"] is None

    def test_registry_iv_override_pass_returns_authoritative(self):
        reqs_dir = self._tmpdir / "generated-requirements"
        _make_complete_requirements_dir(self._tmpdir, fmt="testfmt")
        with self._patch_reqs_dir(reqs_dir):
            state = _resolve_requirements_state("testfmt", registry_iv_override="PASS")
        assert state["status"] == "REQUIREMENTS_AUTHORITATIVE"
        assert state["iv_status"] == "PASS"

    def test_iv_status_fail_returns_blocked(self):
        reqs_dir = self._tmpdir / "generated-requirements"
        _make_complete_requirements_dir(self._tmpdir, fmt="testfmt")
        with self._patch_reqs_dir(reqs_dir):
            state = _resolve_requirements_state("testfmt", registry_iv_override="FAIL")
        assert state["status"] == "BLOCKED"
        assert state["iv_status"] == "FAIL"

    def test_resolver_does_not_write_files(self):
        """Verify resolve_format_context does not create or modify any files."""
        reqs_dir = self._tmpdir / "generated-requirements"
        _make_complete_requirements_dir(self._tmpdir, fmt="testfmt")
        files_before = set(self._tmpdir.rglob("*"))
        with self._patch_reqs_dir(reqs_dir):
            resolve_format_context("testfmt")
        files_after = set(self._tmpdir.rglob("*"))
        assert files_before == files_after, (
            f"Resolver wrote files: {files_after - files_before}"
        )
