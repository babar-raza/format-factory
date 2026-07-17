"""test_direct_generator_gap_triage.py — TC-RG-002 (2026-07-17).

DIRECT-GENERATOR-GAP triage: scan_ungoverned_generators() (tightened by the
sibling proximity fix, test_scan_ungoverned_generators_proximity.py) reduced
125 flagged files to 5 real candidates. Manual review classified them:

  - tools/supervisor/bounded_repair_engine.py: CONFIRMED real gap. Writes
    directly to src/ with no skill/manifest resolution, and its
    MISSING_ATTRIBUTE/NAME_ERROR repairs write literal `# TODO: implement`
    stubs into product source -- a direct EP-1 conflict. Confirmed NOT wired
    into any live path (no importer outside its own test) -- marked
    deprecated-pending-redesign in its own docstring rather than governance-
    wrapped, since wrapping would legitimize code that shouldn't run as-is.
  - tools/supervisor/build_context_pack.py: CONFIRMED real gap, GOVERNED this
    pass (added to the hot-governance-files manifest + gate.py
    GENERATOR_PATTERNS — see test_hotfile_generator_guard.py).
  - tools/supervisor/supervisor_loop.py: outputs already declared under the
    pre-existing tools/supervisor/autonomous-cycle-output-manifest.yaml;
    gate.py doesn't yet route it through guard-run enforcement -- backlogged,
    not urgent (single-writer ephemeral run-state heartbeat file, not a
    shared multi-writer canonical policy document).
  - tools/review/architecture_audit.py,
    tools/oracle/self_test_oracle_harness.py: reclassified FALSE POSITIVE on
    manual read -- both write only to reports/self-test scratch dirs; the
    nearby src/python or oracle/ match was a docstring/error-message
    describing what the tool *reads*, not its write target.

This test asserts the two load-bearing facts from that triage so a future
regression (someone wiring bounded_repair_engine into a live path, or its
test-import assumption changing) is caught rather than silently drifting.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))


def _importers_of(module_dotted: str) -> list[str]:
    hits = []
    for p in sorted((REPO_ROOT / "tools").rglob("*.py")):
        if p.name == "bounded_repair_engine.py":
            continue
        try:
            tree = ast.parse(p.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.ImportFrom) and node.module and module_dotted in node.module:
                hits.append(p.relative_to(REPO_ROOT).as_posix())
            elif isinstance(node, ast.Import):
                for alias in node.names:
                    if module_dotted in alias.name:
                        hits.append(p.relative_to(REPO_ROOT).as_posix())
    return hits


def test_bounded_repair_engine_has_no_live_tools_importer():
    """Confirms the dead-code finding this triage relied on. If this starts
    failing, bounded_repair_engine.py has been wired into a live path and its
    EP-1 stub-write conflict (see its module docstring) must be resolved
    first -- do not just update this test to make it pass."""
    assert _importers_of("bounded_repair_engine") == []


def test_bounded_repair_engine_docstring_documents_ep1_conflict():
    text = (REPO_ROOT / "tools" / "supervisor" / "bounded_repair_engine.py").read_text(
        encoding="utf-8")
    assert "EP-1" in text
    assert "NOT WIRED IN" in text


def test_build_context_pack_is_governed_via_hot_files_manifest():
    import yaml
    manifest = yaml.safe_load(
        (REPO_ROOT / "tools" / "governance" / "hot-governance-files" /
         "output-manifest.yaml").read_text(encoding="utf-8"))
    outputs = {o.replace("\\", "/") for o in manifest["outputs"]}
    assert ".supervisor/context-pack.yaml" in outputs

    sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))
    from coordination.hooks.gate import GENERATOR_PATTERNS
    matched = [gid for gid, pat in GENERATOR_PATTERNS
               if pat.search("tools/supervisor/build_context_pack.py")]
    assert "hot-governance-files" in matched


def test_supervisor_loop_current_run_json_already_declared_elsewhere():
    """supervisor_loop.py's write is not newly-ungoverned -- it's already
    declared in the pre-existing autonomous-cycle-output-manifest.yaml.
    Documents why this candidate was backlogged, not governed, this pass."""
    text = (REPO_ROOT / "tools" / "supervisor" /
            "autonomous-cycle-output-manifest.yaml").read_text(encoding="utf-8")
    assert ".supervisor/state/current-run.json" in text
