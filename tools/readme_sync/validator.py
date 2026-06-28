"""Validate README freshness, preservation, and generated claims."""

from __future__ import annotations

import re
from dataclasses import dataclass
from pathlib import Path

from tools.readme_sync.collector import REPO_ROOT, collect_format_state
from tools.readme_sync.reconciler import BEGIN_RE, END_RE, verify_preservation
from tools.readme_sync.renderer import generate_blocks
from tools.readme_sync.section_schema import get_schema_for_format


@dataclass
class ValidationResult:
    ok: bool
    errors: list[str]
    warnings: list[str]


def validate_markers(content: str) -> ValidationResult:
    begins = BEGIN_RE.findall(content)
    ends = END_RE.findall(content)
    errors: list[str] = []
    if sorted(begins) != sorted(ends):
        errors.append("README marker begin/end mismatch")
    if len(begins) != len(set(begins)):
        errors.append("Duplicate README generated marker")
    return ValidationResult(not errors, errors, [])


def validate_generated_claims(content: str, state: dict) -> ValidationResult:
    errors: list[str] = []
    for value, label in ((state.get("package_name"), "package"), (state.get("version"), "version")):
        if value and "<!-- BEGIN:README-PACKAGE_INFO" in content and str(value) not in content:
            errors.append(f"Generated package info missing {label}: {value}")
    return ValidationResult(not errors, errors, [])


def validate_readme(path: Path, format_id: str, track: str, original: str | None = None) -> ValidationResult:
    content = path.read_text(encoding="utf-8", errors="replace")
    schema = get_schema_for_format(format_id, track)
    marker_result = validate_markers(content)
    state = collect_format_state(format_id, track)
    claim_result = validate_generated_claims(content, state)
    errors = [*marker_result.errors, *claim_result.errors]
    warnings = [*marker_result.warnings, *claim_result.warnings]
    if original is not None:
        ok, missing = verify_preservation(original, content, schema)
        if not ok:
            errors.extend(f"Maintained fragment missing: {m}" for m in missing)
    for rel in re.findall(r"\]\(([^):#][^)]+)\)", content):
        if rel.startswith(("http://", "https://", "mailto:")):
            continue
        candidate = (path.parent / rel).resolve()
        try:
            candidate.relative_to(REPO_ROOT)
        except ValueError:
            errors.append(f"Relative link escapes repository: {rel}")
            continue
        if not candidate.exists():
            warnings.append(f"Relative link target missing: {rel}")
    return ValidationResult(not errors, errors, warnings)


def expected_content(path: Path, format_id: str, track: str) -> str:
    from tools.readme_sync.reconciler import render_existing_with_generated

    state = collect_format_state(format_id, track)
    return render_existing_with_generated(path.read_text(encoding="utf-8", errors="replace"), generate_blocks(state, "STRIPPED"))
