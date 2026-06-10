"""Tests for R106 prompt quality hardening — new structure check."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parent.parent.parent.parent / "tools" / "supervisor"))

from validate_prompt_quality import validate_prompt_quality


def test_prompt_with_structure_passes():
    """Prompt with section markers passes structure check."""
    prompt = (
        "# Acceleration R107 Sprint\n"
        "## Lane A: Repair\n"
        "Fix anti-skip false positives from R106.\n"
        "## Lane B: Advancement\n"
        "Add 2 new detectors for package freshness.\n"
        "## Evidence Closeout\n"
        "Write evidence-declaration.yaml and run autonomous-cycle.\n"
        "Tools: gap selector, anti-skip checker, package validator.\n"
    )
    result = validate_prompt_quality(prompt, "acceleration", has_repairs=True)
    structure_checks = [c for c in result["checks"] if c["check"] == "prompt_structure"]
    assert len(structure_checks) == 1
    assert structure_checks[0]["pass"] is True


def test_prompt_without_structure_fails():
    """Flat prompt without sections fails structure check."""
    prompt = (
        "Do acceleration work. "
        "Improve the anti-skip tool and gap selector and package validator. "
        "Write evidence-declaration.yaml and run autonomous-cycle."
    )
    result = validate_prompt_quality(prompt, "acceleration")
    structure_checks = [c for c in result["checks"] if c["check"] == "prompt_structure"]
    assert len(structure_checks) == 1
    assert structure_checks[0]["pass"] is False


def test_prompt_quality_total_checks_r106():
    """R106 prompt quality has 8 checks (6 original + 1 structure + 1 unsafe-wording GEC-TC-005)."""
    prompt = (
        "# Acceleration Sprint\n"
        "## Lane A: Tool improvements\n"
        "Improve anti-skip checker and gap selector tools.\n"
        "## Lane B: Package validation\n"
        "Add package validator tests.\n"
        "## Evidence\n"
        "Write evidence-declaration.yaml and run autonomous-cycle.\n"
    )
    result = validate_prompt_quality(prompt, "acceleration", has_repairs=True, has_advancement=True)
    # Should have: not_generic, stream_identity, repair_lane, advancement_lane, evidence_requirement, no_wrong_stream, prompt_structure, no_unsafe_commit_push_wording (GEC-TC-005), no_unauthorized_mutation_instructions (V11/Check 9)
    assert result["total_checks"] == 9


def test_prompt_quality_r106_prompts():
    """R106-generated prompts should pass quality checks."""
    prompt_path = (
        Path(__file__).resolve().parent.parent.parent.parent
        / "reports" / "acceleration-r106" / "generated-stream-prompts" / "next-acceleration-prompt.md"
    )
    if not prompt_path.exists():
        pytest.skip("R106 acceleration prompt not yet generated")
    prompt = prompt_path.read_text(encoding="utf-8")
    result = validate_prompt_quality(prompt, "acceleration", has_repairs=True)
    assert result["valid"] is True, f"Failed: {[c for c in result['checks'] if not c['pass']]}"
