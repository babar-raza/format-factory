"""
TC-P5-001-04 — Tests for validate_prompt_registry.py

Tests:
  1. All current prompt registrations pass validation
  2. Missing file entry fails
  3. Missing front matter in operational_prompts fails
  4. Duplicate id fails
"""
import subprocess
import sys
import textwrap
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parent.parent.parent
VALIDATOR = REPO / "tools" / "supervisor" / "validate_prompt_registry.py"
PYTHON = sys.executable


def _run_validator(*extra_args: str) -> subprocess.CompletedProcess:
    return subprocess.run(
        [PYTHON, str(VALIDATOR)] + list(extra_args),
        capture_output=True,
        text=True,
        cwd=str(REPO),
    )


def test_all_current_registrations_pass():
    """Live registry + index must pass all checks."""
    result = _run_validator()
    assert result.returncode == 0, (
        f"validate_prompt_registry.py failed against live system:\n{result.stdout}\n{result.stderr}"
    )


def test_missing_file_fails(tmp_path):
    """A registry pointing to a nonexistent .md file should fail Check 1."""
    fake_registry = tmp_path / "prompt-registry.yaml"
    fake_registry.write_text(
        yaml.dump({
            "prompts": [],
            "operational_prompts": [
                {"id": "TEST-MISSING-FILE", "file": ".supervisor/prompts/nonexistent_does_not_exist.md"}
            ],
            "existing_prompts": [],
        }),
        encoding="utf-8",
    )
    result = _run_validator("--registry", str(fake_registry))
    assert result.returncode == 1, "Should fail when file reference is missing"
    assert "CHECK1_MISSING_FILE" in result.stdout or "CHECK1_MISSING_FILE" in result.stderr


def test_missing_front_matter_fails(tmp_path):
    """An operational prompt without front matter should fail Check 2."""
    # Create a .md file without front matter
    md_file = tmp_path / "no_frontmatter.md"
    md_file.write_text("# Just a heading\nNo front matter here.\n", encoding="utf-8")

    # Create a fake registry pointing to it (use a relative path trick)
    # Use tmp_path as a fake prompts location, register via --prompts-dir
    fake_registry = tmp_path / "prompt-registry.yaml"
    # Write relative path — the validator uses REPO_ROOT / file_val
    # So we need to write the path relative to REPO_ROOT
    import os
    try:
        rel_path = os.path.relpath(str(md_file), str(REPO)).replace("\\", "/")
    except ValueError:
        # On Windows, tmp_path may be on a different drive
        rel_path = str(md_file).replace("\\", "/")

    fake_registry.write_text(
        yaml.dump({
            "prompts": [],
            "operational_prompts": [
                {"id": "TEST-NO-FM", "file": rel_path}
            ],
            "existing_prompts": [],
        }),
        encoding="utf-8",
    )

    # Register the file by writing a relative path that matches the tmp file
    # Since the validator uses REPO_ROOT / file_val, we make the md_file under REPO_ROOT
    actual_md = REPO / "tmp_test_no_frontmatter.md"
    actual_md.write_text("# Just a heading\nNo front matter here.\n", encoding="utf-8")
    try:
        real_registry = tmp_path / "real-registry.yaml"
        real_registry.write_text(
            yaml.dump({
                "prompts": [],
                "operational_prompts": [
                    {"id": "TEST-NO-FM", "file": "tmp_test_no_frontmatter.md"}
                ],
                "existing_prompts": [],
            }),
            encoding="utf-8",
        )
        result = _run_validator("--registry", str(real_registry))
        assert result.returncode == 1, "Should fail when front matter is missing"
        assert "CHECK2_NO_FRONTMATTER" in result.stdout or "CHECK2_NO_FRONTMATTER" in result.stderr
    finally:
        if actual_md.exists():
            actual_md.unlink()


def test_duplicate_id_fails(tmp_path):
    """A registry with the same id in two sections should fail Check 3."""
    fake_registry = tmp_path / "prompt-registry.yaml"
    fake_registry.write_text(
        yaml.dump({
            "prompts": [
                {"id": "DUPLICATE-ID", "file": ".supervisor/prompts/bounded-executor.md"}
            ],
            "operational_prompts": [
                {"id": "DUPLICATE-ID", "file": ".supervisor/prompts/bounded-executor.md"}
            ],
            "existing_prompts": [],
        }),
        encoding="utf-8",
    )
    result = _run_validator("--registry", str(fake_registry))
    assert result.returncode == 1, "Should fail on duplicate id"
    assert "CHECK3_DUPLICATE_ID" in result.stdout or "CHECK3_DUPLICATE_ID" in result.stderr
