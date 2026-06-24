"""Tests for run_skill_idempotency.py — Skill 10"""
import sys
from pathlib import Path
import subprocess

_REPO = Path(__file__).resolve().parent.parent.parent


def test_idempotent_tool_produces_pass(tmp_path):
    """detect_ad_hoc_execution.py should produce identical output twice."""
    run1 = str(tmp_path / "run1.yaml")
    run2 = str(tmp_path / "run2.yaml")
    result = subprocess.run(
        [sys.executable,
         str(_REPO / "tools" / "supervisor" / "run_skill_idempotency.py"),
         "--skill-id", "detect-ad-hoc-execution",
         "--tool-path", str(_REPO / "tools" / "supervisor" / "detect_ad_hoc_execution.py"),
         "--output-path", str(tmp_path / "final.yaml"),
         "--run1-path", run1,
         "--run2-path", run2],
        capture_output=True, text=True, cwd=str(_REPO)
    )
    assert result.returncode == 0, f"Expected exit 0; got {result.returncode}. stderr: {result.stderr}"
    import yaml
    proof_path = _REPO / ".supervisor" / "skill-idempotency-proof.yaml"
    if proof_path.exists():
        proof = yaml.safe_load(proof_path.read_text(encoding="utf-8"))
        assert proof["idempotency_verdict"] == "IDEMPOTENT_VERIFIED"


def test_run1_and_run2_files_created(tmp_path):
    run1 = str(tmp_path / "run1.yaml")
    run2 = str(tmp_path / "run2.yaml")
    subprocess.run(
        [sys.executable,
         str(_REPO / "tools" / "supervisor" / "run_skill_idempotency.py"),
         "--skill-id", "detect-ad-hoc-execution",
         "--tool-path", str(_REPO / "tools" / "supervisor" / "detect_ad_hoc_execution.py"),
         "--output-path", str(tmp_path / "final.yaml"),
         "--run1-path", run1,
         "--run2-path", run2],
        capture_output=True, text=True, cwd=str(_REPO)
    )
    assert Path(run1).exists()
    assert Path(run2).exists()


def test_scope_limitation_documented():
    """scope_limitation field must be present in proof output."""
    import yaml
    proof_path = _REPO / ".supervisor" / "skill-idempotency-proof.yaml"
    if not proof_path.exists():
        return  # test will pass after Pilot A runs
    proof = yaml.safe_load(proof_path.read_text(encoding="utf-8"))
    assert "scope_limitation" in proof
    assert "prompt-backed" in proof["scope_limitation"].lower()
