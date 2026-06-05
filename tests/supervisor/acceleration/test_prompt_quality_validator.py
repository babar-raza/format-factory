"""Tests for validate_prompt_quality.py — Stream Prompt Quality Validator."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "tools" / "supervisor"))

from validate_prompt_quality import validate_prompt_quality


REPO_ROOT = Path(__file__).resolve().parent.parent.parent.parent


def test_acceleration_prompt_quality():
    """R105 acceleration prompt passes quality checks."""
    prompt_path = REPO_ROOT / "reports" / "acceleration-r105" / "generated-stream-prompts" / "next-acceleration-prompt.md"
    if not prompt_path.exists():
        pytest.skip("R105 acceleration prompt not yet generated")
    prompt = prompt_path.read_text(encoding="utf-8")
    result = validate_prompt_quality(prompt, "acceleration", has_repairs=True)
    assert result["valid"] is True, f"Failed checks: {[c for c in result['checks'] if not c['pass']]}"


def test_mainstream_prompt_quality():
    """R105 mainstream prompt passes quality checks."""
    prompt_path = REPO_ROOT / "reports" / "acceleration-r105" / "generated-stream-prompts" / "next-mainstream-prompt.md"
    if not prompt_path.exists():
        pytest.skip("R105 mainstream prompt not yet generated")
    prompt = prompt_path.read_text(encoding="utf-8")
    result = validate_prompt_quality(prompt, "mainstream")
    assert result["valid"] is True, f"Failed checks: {[c for c in result['checks'] if not c['pass']]}"


def test_skills_prompt_quality():
    """R105 skills prompt passes quality checks."""
    prompt_path = REPO_ROOT / "reports" / "acceleration-r105" / "generated-stream-prompts" / "next-skills-prompt.md"
    if not prompt_path.exists():
        pytest.skip("R105 skills prompt not yet generated")
    prompt = prompt_path.read_text(encoding="utf-8")
    result = validate_prompt_quality(prompt, "skills")
    assert result["valid"] is True, f"Failed checks: {[c for c in result['checks'] if not c['pass']]}"


def test_supervisor_prompt_quality():
    """R105 supervisor prompt passes quality checks."""
    prompt_path = REPO_ROOT / "reports" / "acceleration-r105" / "generated-stream-prompts" / "next-supervisor-prompt.md"
    if not prompt_path.exists():
        pytest.skip("R105 supervisor prompt not yet generated")
    prompt = prompt_path.read_text(encoding="utf-8")
    result = validate_prompt_quality(prompt, "supervisor")
    assert result["valid"] is True, f"Failed checks: {[c for c in result['checks'] if not c['pass']]}"


def test_generic_prompt_fails():
    """Generic prompt should fail quality check."""
    result = validate_prompt_quality("Do stuff.", "acceleration")
    assert result["valid"] is False


def test_wrong_stream_fails():
    """Acceleration prompt with product code refs should fail no_wrong_stream."""
    prompt = (
        "Edit src/net/fods/FodsDocument.cs to add export. "
        "Modify src/python/fodt/parser.py for paragraph support. "
        "This is an acceleration sprint with tool improvements and gap selector and anti-skip and package validator. "
        "Write evidence-declaration.yaml and run autonomous-cycle."
    )
    result = validate_prompt_quality(prompt, "acceleration")
    wrong_stream = [c for c in result["checks"] if c["check"] == "no_wrong_stream"]
    assert len(wrong_stream) == 1
    assert wrong_stream[0]["pass"] is False


def test_missing_evidence_fails():
    """Prompt without evidence requirement should fail."""
    prompt = (
        "Acceleration sprint: improve anti-skip checker tool and add gap selector tests. "
        "Add package validator and prompt quality checker. No closeout needed."
    )
    result = validate_prompt_quality(prompt, "acceleration")
    evidence_check = [c for c in result["checks"] if c["check"] == "evidence_requirement"]
    assert len(evidence_check) == 1
    assert evidence_check[0]["pass"] is False
