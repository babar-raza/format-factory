"""
R100 — Review Package Builder Unit Tests
Tests build_package() and add_file_to_zip() for ZIP self-containment.
"""
import sys
import json
import zipfile
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "tools" / "supervisor"))

from build_declaration_review_package import build_package, add_file_to_zip, sha256_file


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _create_test_repo(tmp_path, run_id="test-pkg-run"):
    """Create a minimal repo with all expected artifacts for a review package."""
    # Evidence declaration
    evidence_dir = tmp_path / ".local" / "evidences" / run_id
    evidence_dir.mkdir(parents=True, exist_ok=True)
    decl = {
        "run_id": run_id,
        "sprint_id": "test-sprint",
        "evidence_root": f".local/evidences/{run_id}",
        "test_results": {"passed": 10, "failed": 0},
        "planned_work_items": [],
    }
    decl_path = evidence_dir / "evidence-declaration.yaml"
    decl_path.write_text(yaml.dump(decl), encoding="utf-8")

    # Supervisor outputs
    sup_dir = tmp_path / "reports" / "supervisor"
    sup_dir.mkdir(parents=True, exist_ok=True)
    for fname in [
        "work-item-grades.json", "work-item-grades.md", "work-item-grades.yaml",
        "session-resume.md", "next-sprint.md", "materialized-evidence-review.md",
        "latest-cycle-summary.md", "approval-gates.md",
        "evidence-review.md", "contradictions.md",
    ]:
        (sup_dir / fname).write_text(f"# {fname}\ntest content\n", encoding="utf-8")

    # MCP status
    for mcp_f in ["mcp-status.md", "mcp-status.json"]:
        (sup_dir / mcp_f).write_text(f"# {mcp_f}\n", encoding="utf-8")

    # Materialized evidence
    mat_dir = tmp_path / ".local" / "supervisor" / "materialized" / run_id
    mat_dir.mkdir(parents=True, exist_ok=True)
    (mat_dir / "materialized-evidence-manifest.yaml").write_text("test: true\n", encoding="utf-8")
    (mat_dir / "missing-evidence-report.md").write_text("# None\n", encoding="utf-8")
    (mat_dir / "source-change-diffs.patch").write_text("# no diffs\n", encoding="utf-8")

    # Ledger
    ledger_dir = tmp_path / "reports" / "r90"
    ledger_dir.mkdir(parents=True, exist_ok=True)
    (ledger_dir / "product-code-change-ledger.json").write_text("{}", encoding="utf-8")

    # POC matrix
    poc_dir = tmp_path / "product-capability-matrix"
    poc_dir.mkdir(parents=True, exist_ok=True)
    (poc_dir / "poc-targets.yaml").write_text("test: true\n", encoding="utf-8")

    # Context pack
    config_dir = tmp_path / ".supervisor"
    config_dir.mkdir(parents=True, exist_ok=True)
    (config_dir / "context-pack.yaml").write_text("test: true\n", encoding="utf-8")
    (sup_dir / "context-pack.md").write_text("# Context\n", encoding="utf-8")

    # Continuation signal
    signal_dir = tmp_path / ".local" / "supervisor"
    signal_dir.mkdir(parents=True, exist_ok=True)
    (signal_dir / "continuation-signal.json").write_text(json.dumps({"autonomous_continue": True}), encoding="utf-8")

    # Cycle manifest
    review_dir = tmp_path / ".local" / "supervisor" / "reviews" / run_id
    review_dir.mkdir(parents=True, exist_ok=True)
    (review_dir / "supervisor-cycle-manifest.yaml").write_text("test: true\n", encoding="utf-8")

    return decl_path


# ---------------------------------------------------------------------------
# add_file_to_zip
# ---------------------------------------------------------------------------

def test_add_file_to_zip_existing(tmp_path):
    f = tmp_path / "test.txt"
    f.write_text("hello")
    zip_path = tmp_path / "test.zip"
    missing = []
    with zipfile.ZipFile(zip_path, "w") as zf:
        result = add_file_to_zip(zf, f, "inner/test.txt", missing)
    assert result is True
    assert missing == []
    with zipfile.ZipFile(zip_path, "r") as zf:
        assert "inner/test.txt" in zf.namelist()


def test_add_file_to_zip_missing(tmp_path):
    zip_path = tmp_path / "test.zip"
    missing = []
    with zipfile.ZipFile(zip_path, "w") as zf:
        result = add_file_to_zip(zf, tmp_path / "nonexistent.txt", "inner/x.txt", missing)
    assert result is False
    assert len(missing) == 1


# ---------------------------------------------------------------------------
# sha256_file
# ---------------------------------------------------------------------------

def test_sha256_file_deterministic(tmp_path):
    f = tmp_path / "hash_test.txt"
    f.write_text("deterministic content")
    h1 = sha256_file(f)
    h2 = sha256_file(f)
    assert h1 == h2
    assert len(h1) == 64


# ---------------------------------------------------------------------------
# build_package — full integration
# ---------------------------------------------------------------------------

def test_build_package_success(tmp_path):
    decl_path = _create_test_repo(tmp_path)
    out_dir = tmp_path / "output"

    result = build_package(decl_path, tmp_path, out_dir)

    assert result["exit_code"] == 0 or result["exit_code"] == 2  # some optional files may be missing
    assert result["run_id"] == "test-pkg-run"
    assert result["zip_sha256"] is not None
    assert len(result["zip_sha256"]) == 64

    # ZIP should exist
    zip_path = Path(result["zip_path"])
    assert zip_path.exists()

    # Check sidecar
    sidecar_path = Path(result["sidecar_path"])
    assert sidecar_path.exists()
    sidecar = json.loads(sidecar_path.read_text(encoding="utf-8"))
    assert sidecar["zip_sha256"] == result["zip_sha256"]


def test_build_package_contains_key_files(tmp_path):
    decl_path = _create_test_repo(tmp_path)
    out_dir = tmp_path / "output"

    result = build_package(decl_path, tmp_path, out_dir)
    zip_path = Path(result["zip_path"])

    with zipfile.ZipFile(zip_path, "r") as zf:
        names = zf.namelist()

        # R99/R105 self-containment items (R105 moved global state to global-state/ prefix)
        assert "package-manifest.json" in names
        assert "evidence/evidence-declaration.yaml" in names
        assert "supervisor/work-item-grades.json" in names
        assert "global-state/supervisor/session-resume.md" in names
        assert "global-state/supervisor/next-sprint.md" in names
        assert "global-state/poc-targets.yaml" in names
        assert "global-state/context-pack.yaml" in names
        assert "global-state/continuation-signal.json" in names
        assert "global-state/supervisor/latest-cycle-summary.md" in names
        assert "global-state/supervisor/approval-gates.md" in names
        assert "global-state/supervisor/evidence-review.md" in names
        assert "global-state/supervisor/contradictions.md" in names


def test_build_package_manifest_tracks_missing(tmp_path):
    # Create minimal repo (some files intentionally missing)
    evidence_dir = tmp_path / ".local" / "evidences" / "partial-run"
    evidence_dir.mkdir(parents=True, exist_ok=True)
    decl_path = evidence_dir / "evidence-declaration.yaml"
    decl_path.write_text(yaml.dump({
        "run_id": "partial-run",
        "sprint_id": "test",
    }), encoding="utf-8")

    # Only create minimal dirs
    (tmp_path / "reports" / "supervisor").mkdir(parents=True, exist_ok=True)

    out_dir = tmp_path / "output"
    result = build_package(decl_path, tmp_path, out_dir)

    assert result["missing_count"] > 0  # Many files intentionally absent

    # Check package-manifest.json inside ZIP
    with zipfile.ZipFile(result["zip_path"], "r") as zf:
        manifest = json.loads(zf.read("package-manifest.json"))
        assert manifest["artifacts_missing_count"] > 0
        assert len(manifest["artifacts_missing"]) > 0
