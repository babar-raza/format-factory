"""Citation verifier — deep citation validation for synthesis outputs.

Verifies that citations reference real spec sections, have extractable text,
and do not reference fabricated sources.
"""

from __future__ import annotations

import hashlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class CitationResult:
    """Result of verifying a single citation."""
    citation_index: int
    source: str
    text: str
    source_exists: bool = False
    text_found_in_source: bool = False
    verification_hash: str = ""
    errors: list[str] = field(default_factory=list)

    @property
    def valid(self) -> bool:
        return self.source_exists and self.text_found_in_source and not self.errors


@dataclass
class VerificationReport:
    """Aggregate report for all citations in a synthesis output."""
    total: int = 0
    verified: int = 0
    failed: int = 0
    missing_source: int = 0
    results: list[CitationResult] = field(default_factory=list)

    @property
    def all_valid(self) -> bool:
        return self.total > 0 and self.failed == 0 and self.missing_source == 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "total": self.total,
            "verified": self.verified,
            "failed": self.failed,
            "missing_source": self.missing_source,
            "all_valid": self.all_valid,
            "results": [
                {
                    "index": r.citation_index,
                    "source": r.source,
                    "valid": r.valid,
                    "errors": r.errors,
                }
                for r in self.results
            ],
        }


KNOWN_SPEC_DIRS = [
    "specs/normalization",
    "generated-requirements",
    "docs/ai",
    "acquisition-packs",
]


def resolve_source_path(source: str, repo_root: Path) -> Path | None:
    """Try to resolve a citation source to a real file path."""
    direct = repo_root / source
    if direct.exists():
        return direct
    for spec_dir in KNOWN_SPEC_DIRS:
        candidate = repo_root / spec_dir / source
        if candidate.exists():
            return candidate
    return None


def verify_single_citation(
    citation: dict[str, str],
    index: int,
    source_texts: dict[str, str] | None = None,
    repo_root: Path | None = None,
) -> CitationResult:
    """Verify a single citation against available sources."""
    result = CitationResult(
        citation_index=index,
        source=citation.get("source", ""),
        text=citation.get("text", ""),
    )

    if not result.source:
        result.errors.append("missing_source_field")
        return result
    if not result.text:
        result.errors.append("missing_text_field")
        return result

    result.verification_hash = hashlib.sha256(
        f"{result.source}:{result.text}".encode()
    ).hexdigest()[:16]

    # Check source existence
    if source_texts and result.source in source_texts:
        result.source_exists = True
        if result.text in source_texts[result.source]:
            result.text_found_in_source = True
        else:
            result.errors.append("text_not_found_in_source")
    elif repo_root:
        resolved = resolve_source_path(result.source, repo_root)
        if resolved:
            result.source_exists = True
            content = resolved.read_text(encoding="utf-8", errors="ignore")
            if result.text in content:
                result.text_found_in_source = True
            else:
                result.errors.append("text_not_found_in_source")
        else:
            result.errors.append("source_file_not_found")
    else:
        result.errors.append("no_verification_context")

    return result


def verify_all_citations(
    citations: list[dict[str, str]],
    source_texts: dict[str, str] | None = None,
    repo_root: Path | None = None,
) -> VerificationReport:
    """Verify all citations in a synthesis output."""
    report = VerificationReport(total=len(citations))

    for i, cit in enumerate(citations):
        result = verify_single_citation(cit, i, source_texts, repo_root)
        report.results.append(result)
        if result.valid:
            report.verified += 1
        elif not result.source_exists:
            report.missing_source += 1
            report.failed += 1
        else:
            report.failed += 1

    return report
