import sys
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
FIXTURE_ROOT = Path(__file__).resolve().parent / "fixtures" / "git_safety"
sys.path.insert(0, str(REPO_ROOT))

from tools.governance import check_git_safety as safety


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def test_detects_root_bundle_metadata_contamination(tmp_path):
    write(tmp_path / "bundle-metadata" / "verdict.md", "# Verdict\nSprint: old-sprint\n")
    contaminated, hits = safety.root_bundle_metadata_contaminated(tmp_path)
    assert contaminated is True
    assert "verdict.md" in hits


def test_detects_mixed_sprint_identity(tmp_path):
    meta = FIXTURE_ROOT / "mixed-metadata"
    ok, identities, _messages = safety.check_metadata_identity(meta)
    assert ok is False
    assert identities == ["memory-ai-direction-sync", "tc0050"]


def test_detects_forbidden_command_strings():
    assert safety.forbidden_commands_in_text("git add .\n")
    assert safety.forbidden_commands_in_text("git add -A\n")
    assert safety.scan_command_logs(FIXTURE_ROOT / "command-logs")


def test_accepts_clean_sprint_specific_metadata(tmp_path):
    meta = FIXTURE_ROOT / "clean-metadata"
    ok, identities, messages = safety.check_metadata_identity(meta)
    assert ok is True
    assert identities == ["gov-revert-001"]
    assert messages


def test_classification_required_when_dirty_in_strict_mode(monkeypatch, tmp_path):
    responses = {
        ("branch", "--show-current"): (0, "main\n"),
        ("rev-parse", "HEAD"): (0, "abc123\n"),
        ("status", "--short"): (0, " M AGENTS.md\n"),
        ("stash", "list"): (0, ""),
        ("reflog", "--date=iso", "-50"): (0, ""),
        ("ls-files", "-v"): (0, "H AGENTS.md\n"),
    }

    def fake_run_git(args, repo_root):
        return responses.get(tuple(args), (0, ""))

    monkeypatch.setattr(safety, "run_git", fake_run_git)
    args = type("Args", (), {
        "repo_root": str(tmp_path),
        "strict": True,
        "classification_file": None,
        "metadata_dir": None,
    })()
    report, exit_code = safety.build_report(args)
    assert exit_code == 1
    assert any("classification-file" in e for e in report["errors"])


def test_warns_on_reset_reflog_text(monkeypatch, tmp_path):
    responses = {
        ("branch", "--show-current"): (0, "main\n"),
        ("rev-parse", "HEAD"): (0, "abc123\n"),
        ("status", "--short"): (0, ""),
        ("stash", "list"): (0, ""),
        ("reflog", "--date=iso", "-50"): (0, "abc HEAD@{0}: reset: moving to HEAD\n"),
        ("ls-files", "-v"): (0, "H AGENTS.md\n"),
    }

    def fake_run_git(args, repo_root):
        return responses.get(tuple(args), (0, ""))

    monkeypatch.setattr(safety, "run_git", fake_run_git)
    args = type("Args", (), {
        "repo_root": str(tmp_path),
        "strict": False,
        "classification_file": None,
        "metadata_dir": None,
    })()
    report, exit_code = safety.build_report(args)
    assert exit_code == 0
    assert any("reset: moving to HEAD" in w for w in report["warnings"])
