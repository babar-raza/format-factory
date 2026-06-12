"""
test_r3_prompt_path_validator.py

Sprint: FORMAT-FACTORY-EXPERT-REVIEW-R3-EVIDENCE-TRUST-AND-PRODUCT-QUALITY-001
Lane: LANE_2 — Validator hardening

Validates that generated next-sprint prompts do not contain nonexistent path references.
Regression: package-104 generated prompt contained src/python/netpbm/ and
tests/python/netpbm/ which do not exist. The Python Netpbm implementation uses
src/python/pbm/, src/python/pgm/, src/python/ppm/.
"""

import json
import pathlib
import pytest

REPO_ROOT = pathlib.Path(__file__).parent.parent.parent

# Paths that must NOT appear in generated prompts
NONEXISTENT_PATHS = [
    "src/python/netpbm",
    "tests/python/netpbm",
]

# Paths that SHOULD be used instead for Python Netpbm
CORRECT_PYTHON_NETPBM_PATHS = [
    "src/python/pbm",
    "src/python/pgm",
    "src/python/ppm",
]


def _collect_prompt_files():
    """Find all generated next-sprint prompt files."""
    patterns = [
        ".local/supervisor/reviews/**/combined-next-worker-prompt.md",
        "reports/supervisor/latest-next-worker-prompt.md",
    ]
    files = []
    for pat in patterns:
        files.extend(REPO_ROOT.glob(pat))
    return files


@pytest.mark.parametrize("bad_path", NONEXISTENT_PATHS)
def test_generated_prompt_no_nonexistent_paths(bad_path):
    """Generated prompts must not reference nonexistent src/python/netpbm paths."""
    prompts = _collect_prompt_files()
    if not prompts:
        pytest.skip("No generated prompts found")

    violations = []
    for prompt_file in prompts:
        content = prompt_file.read_text(encoding="utf-8", errors="replace")
        if bad_path in content:
            lines_with_bad = [
                (i + 1, line.strip())
                for i, line in enumerate(content.splitlines())
                if bad_path in line
            ]
            violations.append(
                f"{prompt_file.relative_to(REPO_ROOT)}: "
                f"found '{bad_path}' at lines {[l for l, _ in lines_with_bad[:3]]}"
            )

    # Allow the defect to exist in historical packages but not in the latest prompt
    latest = REPO_ROOT / "reports/supervisor/latest-next-worker-prompt.md"
    if latest.exists():
        content = latest.read_text(encoding="utf-8", errors="replace")
        if bad_path in content:
            pytest.fail(
                f"latest-next-worker-prompt.md contains nonexistent path '{bad_path}'. "
                f"Use pbm/pgm/ppm instead."
            )
    else:
        pytest.skip("latest-next-worker-prompt.md not found")


def test_correct_python_netpbm_paths_exist():
    """The correct Python Netpbm package directories must exist."""
    for path in CORRECT_PYTHON_NETPBM_PATHS:
        full = REPO_ROOT / path
        assert full.exists(), f"Expected Python Netpbm package directory {path} to exist"


def test_evidence_quality_score_sources_documented():
    """
    Regression for package-104 F-104-06: evidence_quality_score discrepancy.
    The reconciliation doc must exist and explain both scores.
    """
    doc_path = REPO_ROOT / "reports/expert-review-r3/evidence/evidence-quality-score-reconciliation.md"
    assert doc_path.exists(), "evidence-quality-score-reconciliation.md must exist"
    content = doc_path.read_text(encoding="utf-8")
    assert "0.25" in content, "Reconciliation doc must mention the 0.25 supervisor score"
    assert "1.0" in content, "Reconciliation doc must mention the 1.0 anti-skip score"
    assert "tests_supporting" in content, "Reconciliation doc must explain tests_supporting root cause"


def test_package_104_audit_exists():
    """Package-104 audit JSON must exist and have findings."""
    audit_path = REPO_ROOT / "reports/expert-review-r3/evidence/package-104-audit.json"
    assert audit_path.exists(), "package-104-audit.json must exist"
    data = json.loads(audit_path.read_text(encoding="utf-8"))
    assert data.get("findings_count", 0) >= 1, "Audit must have at least one finding"
