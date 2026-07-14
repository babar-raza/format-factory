"""product_quality_audit.py — TC-SPW-005: Sprint-independent product quality audit.

Surfaces 6 product-state checks for .NET formats, independent of sprint grades.
Runs as Step 3b_pqa in autonomous_cycle.py (non-blocking).

Output: reports/product-quality/audit-{sprint_id}-{format}.yaml
"""
from __future__ import annotations

import json
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Literal

_REPO_ROOT = Path(__file__).resolve().parent.parent.parent
_TESTS_NET_ROOT = _REPO_ROOT / "tests" / "net"
_SRC_NET_ROOT = _REPO_ROOT / "src" / "net"

# Round-trip patterns (reuse from V152)
_RT_WRITE = re.compile(r"\b(?:Save|Write)\s*\(", re.IGNORECASE)
_RT_READ = re.compile(r"\b(?:Load|Parse)\s*\(", re.IGNORECASE)

# Public method/property without XML doc
_PUBLIC_MEMBER = re.compile(r"^\s*public\s+(?!class|interface|struct|enum|delegate|abstract|sealed|static\s+class)", re.MULTILINE)
_XML_DOC_LINE = re.compile(r"^\s*///")

# Dictionary state
_DICT_FIELD = re.compile(r"Dictionary\s*<", re.IGNORECASE)

CheckVerdict = Literal["PASS", "WARN", "FAIL", "SKIP"]


@dataclass
class CheckResult:
    check_name: str
    verdict: CheckVerdict
    detail: str
    count: int = 0

    def to_dict(self) -> dict:
        return {
            "check": self.check_name,
            "verdict": self.verdict,
            "detail": self.detail,
            "count": self.count,
        }


@dataclass
class AuditResult:
    format_id: str
    language: str
    sprint_id: str
    checks: list[CheckResult] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "format_id": self.format_id,
            "language": self.language,
            "sprint_id": self.sprint_id,
            "checks": [c.to_dict() for c in self.checks],
            "warn_count": sum(1 for c in self.checks if c.verdict == "WARN"),
            "fail_count": sum(1 for c in self.checks if c.verdict == "FAIL"),
            "pass_count": sum(1 for c in self.checks if c.verdict == "PASS"),
        }

    def to_yaml(self) -> str:
        try:
            import yaml
            return yaml.dump(self.to_dict(), default_flow_style=False, allow_unicode=True)
        except ImportError:
            return json.dumps(self.to_dict(), indent=2)


class ProductQualityAudit:
    """Run all 6 product quality checks for a given format and language."""

    def __init__(self, repo_root: "Path | None" = None):
        self._repo = (repo_root or _REPO_ROOT).resolve()
        self._src_net = self._repo / "src" / "net"
        self._tests_net = self._repo / "tests" / "net"

    def run(self, format_id: str, language: str = "dotnet", sprint_id: str = "manual") -> AuditResult:
        result = AuditResult(format_id=format_id, language=language, sprint_id=sprint_id)
        if language != "dotnet":
            result.checks.append(CheckResult("all", "SKIP", f"Language {language} not supported by product_quality_audit"))
            return result

        src_dir = self._src_net / format_id
        if not src_dir.is_dir():
            result.checks.append(CheckResult("all", "SKIP", f"src/net/{format_id}/ not found"))
            return result

        result.checks.append(self._check_aggregate_loc(format_id, src_dir))
        result.checks.append(self._check_writer_surface(format_id, src_dir))
        result.checks.append(self._check_roundtrip_coverage(format_id))
        result.checks.append(self._check_dictionary_state(format_id, src_dir))
        result.checks.append(self._check_api_documentation(format_id, src_dir))
        result.checks.append(self._check_partial_class_count(format_id, src_dir))
        return result

    # ------------------------------------------------------------------
    # Check 1: Aggregate LOC (uses TC-SPW-001 helper)
    # ------------------------------------------------------------------
    def _check_aggregate_loc(self, format_id: str, src_dir: Path) -> CheckResult:
        try:
            from governance_validators_dotnet import (  # noqa: PLC0415
                collect_partial_class_aggregates, _load_aggregate_baselines, _get_aggregate_cap,
            )
            aggregates = collect_partial_class_aggregates(src_dir)
            baselines = _load_aggregate_baselines()
            if not aggregates:
                return CheckResult("check_aggregate_loc", "PASS", "No partial class groups found")

            violations = []
            for class_name, files in aggregates.items():
                total_loc = sum(loc for _, loc in files)
                cap = _get_aggregate_cap(class_name, len(files), baselines)
                if total_loc > cap:
                    violations.append(f"{class_name}: {total_loc} LOC > cap {cap}")

            if violations:
                return CheckResult(
                    "check_aggregate_loc", "WARN",
                    f"{len(violations)} partial class group(s) exceed aggregate cap: {'; '.join(violations[:3])}",
                    count=len(violations),
                )
            return CheckResult("check_aggregate_loc", "PASS",
                               f"{len(aggregates)} partial class group(s) within caps")
        except Exception as e:
            return CheckResult("check_aggregate_loc", "SKIP", f"Cannot run: {e}")

    # ------------------------------------------------------------------
    # Check 2: Writer surface LOC
    # ------------------------------------------------------------------
    def _check_writer_surface(self, format_id: str, src_dir: Path) -> CheckResult:
        # Find *Writer.cs or *writer.cs
        writer_files = list(src_dir.glob("*[Ww]riter.cs"))
        if not writer_files:
            return CheckResult("check_writer_surface", "SKIP", f"No *Writer.cs found in src/net/{format_id}/")

        # Gate-1 check
        gate1 = self._is_gate1(format_id)
        if not gate1:
            return CheckResult("check_writer_surface", "SKIP", f"{format_id} is not at Gate-1 yet")

        writer_loc = sum(
            sum(1 for _ in f.open(encoding="utf-8", errors="replace"))
            for f in writer_files
        )
        if writer_loc < 100:
            return CheckResult(
                "check_writer_surface", "FAIL",
                f"Writer total {writer_loc} LOC < 100 for Gate-1 format — writer may be a stub",
                count=writer_loc,
            )
        return CheckResult("check_writer_surface", "PASS",
                           f"Writer surface {writer_loc} LOC adequate for Gate-1 format", count=writer_loc)

    # ------------------------------------------------------------------
    # Check 3: Round-trip coverage (V152 heuristic reuse)
    # ------------------------------------------------------------------
    def _check_roundtrip_coverage(self, format_id: str) -> CheckResult:
        test_dir = self._tests_net / format_id
        if not test_dir.is_dir():
            return CheckResult("check_roundtrip_coverage", "FAIL",
                               f"No test directory at tests/net/{format_id}/")
        for cs_file in test_dir.rglob("*.cs"):
            try:
                content = cs_file.read_text(encoding="utf-8", errors="replace")
                if _RT_WRITE.search(content) and _RT_READ.search(content):
                    return CheckResult("check_roundtrip_coverage", "PASS",
                                       f"Round-trip test found: {cs_file.name}")
            except Exception:
                continue
        return CheckResult("check_roundtrip_coverage", "FAIL",
                           f"No .cs file in tests/net/{format_id}/ has both Load() and Save() calls")

    # ------------------------------------------------------------------
    # Check 4: Dictionary state field count
    # ------------------------------------------------------------------
    def _check_dictionary_state(self, format_id: str, src_dir: Path) -> CheckResult:
        count = 0
        for cs_file in src_dir.rglob("*.cs"):
            try:
                content = cs_file.read_text(encoding="utf-8", errors="replace")
                count += len(_DICT_FIELD.findall(content))
            except Exception:
                continue
        if count > 0:
            return CheckResult("check_dictionary_state", "WARN",
                               f"{count} Dictionary<> field occurrence(s) in src/net/{format_id}/",
                               count=count)
        return CheckResult("check_dictionary_state", "PASS",
                           "No Dictionary<> fields detected")

    # ------------------------------------------------------------------
    # Check 5: API documentation coverage
    # ------------------------------------------------------------------
    def _check_api_documentation(self, format_id: str, src_dir: Path) -> CheckResult:
        undocumented = 0
        for cs_file in src_dir.rglob("*.cs"):
            try:
                lines = cs_file.read_text(encoding="utf-8", errors="replace").splitlines()
                for i, line in enumerate(lines):
                    if _PUBLIC_MEMBER.match(line):
                        # Check if preceding lines (up to 3) contain /// <summary>
                        preceding = lines[max(0, i - 3): i]
                        if not any(_XML_DOC_LINE.match(p) for p in preceding):
                            undocumented += 1
            except Exception:
                continue
        if undocumented > 0:
            return CheckResult("check_api_documentation", "WARN",
                               f"{undocumented} public member(s) in src/net/{format_id}/ lack XML doc",
                               count=undocumented)
        return CheckResult("check_api_documentation", "PASS",
                           "All public members have XML documentation")

    # ------------------------------------------------------------------
    # Check 6: Partial class count per class
    # ------------------------------------------------------------------
    def _check_partial_class_count(self, format_id: str, src_dir: Path) -> CheckResult:
        try:
            from governance_validators_dotnet import collect_partial_class_aggregates  # noqa: PLC0415
            aggregates = collect_partial_class_aggregates(src_dir)
            over_limit = {cn: len(files) for cn, files in aggregates.items() if len(files) > 3}
            if over_limit:
                detail = "; ".join(f"{cn}: {n} files" for cn, n in sorted(over_limit.items()))
                return CheckResult("check_partial_class_count", "WARN",
                                   f"{len(over_limit)} class(es) have >3 partial files: {detail}",
                                   count=len(over_limit))
            return CheckResult("check_partial_class_count", "PASS",
                               f"No partial class has >3 files (checked {len(aggregates)} groups)")
        except Exception as e:
            return CheckResult("check_partial_class_count", "SKIP", f"Cannot run: {e}")

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _is_gate1(self, format_id: str) -> bool:
        """Return True if format_id has gate_1: passed in format-registry.yaml."""
        try:
            from governance_validators_dotnet import _gate1_formats_from_registry  # noqa: PLC0415
            return format_id.lower() in _gate1_formats_from_registry()
        except Exception:
            return False
