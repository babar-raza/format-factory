"""C# xunit assertion quality analyzer.

Classifies C# test assertions as STRONG, WEAK, or NEUTRAL based on patterns,
then grades test files as STRONG_PROOF, PARTIAL_PROOF, or WEAK_PROOF.

Used by grade_declared_work.py for .NET test grading and by TC-C1 reports.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Assertion patterns
# ---------------------------------------------------------------------------

# STRONG: contains a specific expected value or range
STRONG_PATTERNS: list[re.Pattern] = [
    re.compile(r'Assert\.Equal\s*\(\s*[-\d]+\.\d', re.IGNORECASE),      # Assert.Equal(2.75, ...)
    re.compile(r'Assert\.Equal\s*\(\s*"[^"]+"\s*,', re.IGNORECASE),     # Assert.Equal("Alice", ...)
    re.compile(r'Assert\.Equal\s*\(\s*\d+\s*,\s*\w', re.IGNORECASE),   # Assert.Equal(3, result)
    re.compile(r'Assert\.InRange\s*\(', re.IGNORECASE),                 # Assert.InRange(x, lo, hi)
    re.compile(r'Assert\.Equal\s*\(.*?precision\s*:', re.IGNORECASE),   # precision: N overload
    re.compile(r'Assert\.Contains\s*\(\s*"[^"]+"\s*,', re.IGNORECASE), # Assert.Contains("Alice", list)
    re.compile(r'Assert\.Equal\s*\(\s*new\s*\[', re.IGNORECASE),       # Assert.Equal(new[] {...}, ...)
    re.compile(r'Assert\.Equal\s*\(\s*true\b', re.IGNORECASE),         # Assert.Equal(true, ...)
    re.compile(r'Assert\.Equal\s*\(\s*false\b', re.IGNORECASE),        # Assert.Equal(false, ...)
    re.compile(r'Assert\.Throws\s*<', re.IGNORECASE),                   # Assert.Throws<T>
    re.compile(r'Assert\.ThrowsAsync\s*<', re.IGNORECASE),
    re.compile(r'Assert\.StartsWith\s*\(\s*"', re.IGNORECASE),
    re.compile(r'Assert\.EndsWith\s*\(\s*"', re.IGNORECASE),
    re.compile(r'Assert\.Matches\s*\(', re.IGNORECASE),                 # regex match
]

# WEAK: existential / boolean-only checks without specific value
WEAK_PATTERNS: list[re.Pattern] = [
    re.compile(r'Assert\.NotNull\s*\(', re.IGNORECASE),
    re.compile(r'Assert\.NotEmpty\s*\(', re.IGNORECASE),
    re.compile(r'Assert\.True\s*\(\s*\w+\s*[><!]=?\s*[\d\w]', re.IGNORECASE),
    re.compile(r'Assert\.False\s*\(\s*string\.IsNullOrEmpty\s*\(', re.IGNORECASE),
    re.compile(r'Assert\.True\s*\(\s*\w+\.Length\s*>', re.IGNORECASE),
    re.compile(r'Assert\.True\s*\(\s*\w+\.Count\s*>', re.IGNORECASE),
]

STRONG_RATIO_THRESHOLD = 0.3  # Lower than Python's 0.5 — calibrated for C# style


@dataclass
class AssertionCount:
    strong: int = 0
    weak: int = 0
    total: int = 0

    @property
    def strong_ratio(self) -> float:
        return self.strong / self.total if self.total > 0 else 0.0

    @property
    def grade(self) -> str:
        if self.total == 0:
            return "NO_ASSERTIONS"
        if self.strong_ratio >= STRONG_RATIO_THRESHOLD:
            return "STRONG_PROOF"
        if self.strong > 0:
            return "PARTIAL_PROOF"
        return "WEAK_PROOF"


@dataclass
class FileAnalysis:
    path: str
    assertion_count: AssertionCount
    grade: str
    weak_lines: list[str] = field(default_factory=list)
    strong_lines: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "path": self.path,
            "grade": self.grade,
            "strong": self.assertion_count.strong,
            "weak": self.assertion_count.weak,
            "total": self.assertion_count.total,
            "strong_ratio": round(self.assertion_count.strong_ratio, 3),
            "weak_lines_sample": self.weak_lines[:5],
        }


class CSharpAssertionAnalyzer:
    """Analyze C# xunit test files for assertion quality."""

    def analyze_content(self, content: str, path: str = "") -> FileAnalysis:
        """Analyze a single C# file's assertions."""
        counts = AssertionCount()
        weak_lines: list[str] = []
        strong_lines: list[str] = []

        for line in content.splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("//"):
                continue

            is_strong = any(p.search(stripped) for p in STRONG_PATTERNS)
            is_weak = any(p.search(stripped) for p in WEAK_PATTERNS)

            if is_strong:
                counts.strong += 1
                counts.total += 1
                strong_lines.append(stripped[:120])
            elif is_weak:
                counts.weak += 1
                counts.total += 1
                weak_lines.append(stripped[:120])
            elif "Assert." in stripped:
                # Catch-all Assert calls (neutral — counted but not classified)
                counts.total += 1

        return FileAnalysis(
            path=path,
            assertion_count=counts,
            grade=counts.grade,
            weak_lines=weak_lines,
            strong_lines=strong_lines,
        )

    def analyze_file(self, path: Path) -> FileAnalysis:
        """Analyze a single .cs file."""
        try:
            content = path.read_text(encoding="utf-8", errors="replace")
        except OSError as e:
            return FileAnalysis(
                path=str(path),
                assertion_count=AssertionCount(),
                grade="FILE_ERROR",
                weak_lines=[str(e)],
            )
        return self.analyze_content(content, str(path))

    def analyze_directory(self, directory: Path, pattern: str = "*.cs") -> list[FileAnalysis]:
        """Analyze all .cs files in a directory (non-recursive)."""
        results = []
        for cs_file in sorted(directory.glob(pattern)):
            if "bin" in cs_file.parts or "obj" in cs_file.parts:
                continue
            results.append(self.analyze_file(cs_file))
        return results

    def analyze_directory_recursive(self, directory: Path) -> list[FileAnalysis]:
        """Analyze all .cs files in a directory tree."""
        results = []
        for cs_file in sorted(directory.rglob("*.cs")):
            if "bin" in cs_file.parts or "obj" in cs_file.parts:
                continue
            results.append(self.analyze_file(cs_file))
        return results

    def grade_summary(self, results: list[FileAnalysis]) -> dict:
        """Produce a distribution summary across all analyzed files."""
        counts: dict[str, int] = {}
        total_strong = 0
        total_weak = 0
        total_assertions = 0

        for r in results:
            counts[r.grade] = counts.get(r.grade, 0) + 1
            total_strong += r.assertion_count.strong
            total_weak += r.assertion_count.weak
            total_assertions += r.assertion_count.total

        weak_proof_files = [r for r in results if r.grade == "WEAK_PROOF"]
        return {
            "total_files": len(results),
            "grade_distribution": counts,
            "total_assertions": total_assertions,
            "total_strong": total_strong,
            "total_weak": total_weak,
            "overall_strong_ratio": round(total_strong / total_assertions, 3) if total_assertions else 0.0,
            "weak_proof_files": [r.to_dict() for r in weak_proof_files],
        }
