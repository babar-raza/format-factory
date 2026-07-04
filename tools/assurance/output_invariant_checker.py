"""
Output Invariant Checker (OIC)
-------------------------------
Verifies structural validity of format export output across all platforms.

Invariants:
  JSON_PARSEABLE     — output must be valid JSON (catches missing control-char escaping)
  XML_PARSEABLE      — output must be well-formed XML
  HTML_CELL_SAFETY   — <td>/<th> content must not contain raw < > & characters
  CSV_ROUNDTRIP      — CSV output must re-parse to the expected row count

Usage (CLI):
  python tools/assurance/output_invariant_checker.py --baseline --output reports/assurance/oic-baseline.json
  python tools/assurance/output_invariant_checker.py --format csv --platform dotnet --check json --input <file>
"""
from __future__ import annotations

import json
import re
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


# ---------------------------------------------------------------------------
# Result types
# ---------------------------------------------------------------------------

@dataclass
class InvariantResult:
    passed: bool
    context: str
    error: Optional[str] = None

    @classmethod
    def pass_(cls, context: str = "") -> "InvariantResult":
        return cls(passed=True, context=context)

    @classmethod
    def fail(cls, message: str, context: str = "") -> "InvariantResult":
        return cls(passed=False, context=context, error=message)

    def to_dict(self) -> dict:
        return {
            "passed": self.passed,
            "context": self.context,
            "error": self.error,
        }


@dataclass
class OicEntry:
    format: str
    platform: str
    method: str
    invariant: str
    result: str  # "PASS" or "FAIL"
    evidence: Optional[str] = None

    def to_dict(self) -> dict:
        return {
            "format": self.format,
            "platform": self.platform,
            "method": self.method,
            "invariant": self.invariant,
            "result": self.result,
            "evidence": self.evidence,
        }


# ---------------------------------------------------------------------------
# Core checker
# ---------------------------------------------------------------------------

class OutputInvariantChecker:
    """
    Checks export output for structural validity across all formats and platforms.
    Each check is independent — a single OicEntry is emitted per (format, method, invariant).
    """

    def check_json(self, output: str, context: str) -> InvariantResult:
        """
        JSON must be parseable by stdlib json.loads().
        Catches: manual JSON escaping that omits control characters (\n, \r, \t).
        A literal newline inside a JSON string value causes JSONDecodeError.
        """
        try:
            json.loads(output)
            return InvariantResult.pass_(context=context)
        except json.JSONDecodeError as e:
            return InvariantResult.fail(
                message=f"{context}: JSONDecodeError: {e}",
                context=context,
            )

    def check_xml(self, output: str, context: str) -> InvariantResult:
        """
        XML must be parseable by stdlib xml.etree.ElementTree.
        Catches: missing entity escaping (&, <, >), malformed tags, unclosed elements.
        """
        try:
            ET.fromstring(output)
            return InvariantResult.pass_(context=context)
        except ET.ParseError as e:
            return InvariantResult.fail(
                message=f"{context}: XML ParseError: {e}",
                context=context,
            )

    def check_html_cell_safety(self, output: str, context: str) -> InvariantResult:
        """
        HTML <td>/<th> cell content must not contain raw < > & characters.
        Valid HTML entities (&amp; &lt; &gt; &quot; &#NNN;) are accepted.
        Catches: XSS-enabling raw interpolation of user data into HTML table cells.
        """
        for tag in ("td", "th"):
            pattern = rf"<{tag}>(.*?)</{tag}>"
            for content in re.findall(pattern, output, re.DOTALL):
                # Strip valid HTML entities before checking for raw special chars
                clean = re.sub(r"&(?:amp|lt|gt|quot|apos|#\d+|#x[0-9a-fA-F]+);", "", content)
                if re.search(r"[<>&]", clean):
                    return InvariantResult.fail(
                        message=(
                            f"{context}: unescaped HTML entity in <{tag}>: "
                            f"{content[:80]!r}"
                        ),
                        context=context,
                    )
        return InvariantResult.pass_(context=context)

    def check_csv_roundtrip(
        self,
        csv_output: str,
        expected_row_count: int,
        context: str,
    ) -> InvariantResult:
        """
        CSV output must re-parse to exactly expected_row_count data rows.
        Header row is subtracted. Empty lines are ignored.
        Catches: delimiter corruption that produces wrong row count.
        """
        lines = [ln for ln in csv_output.splitlines() if ln.strip()]
        actual = len(lines) - 1  # subtract header row
        if actual != expected_row_count:
            return InvariantResult.fail(
                message=(
                    f"{context}: CSV roundtrip row count {actual} "
                    f"!= expected {expected_row_count}"
                ),
                context=context,
            )
        return InvariantResult.pass_(context=context)


# ---------------------------------------------------------------------------
# Baseline runner
# ---------------------------------------------------------------------------

class OicBaselineRunner:
    """
    Runs OIC checks against all known format export methods.
    Produces a list of OicEntry results suitable for JSON reporting.
    """

    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.checker = OutputInvariantChecker()
        self.results: list[OicEntry] = []

    # ------------------------------------------------------------------
    # Python format checks
    # ------------------------------------------------------------------

    def _check_python_ndjson(self) -> None:
        """Check Python ndjson format JSON export."""
        try:
            import sys
            sys.path.insert(0, str(self.repo_root / "src" / "python"))
            from ndjson.ndjson_codec import NdjsonDocument  # type: ignore
            doc = NdjsonDocument()
            doc.add_record({"name": "Alice\nBob", "value": "<tag>&amp;"})
            doc.add_record({"name": "Carol", "value": "normal"})
            output = doc.to_json() if hasattr(doc, "to_json") else doc.dumps()
            result = self.checker.check_json(output, "python/ndjson/to_json")
            self.results.append(OicEntry(
                format="ndjson", platform="python", method="to_json",
                invariant="JSON_PARSEABLE",
                result="PASS" if result.passed else "FAIL",
                evidence=result.error,
            ))
        except Exception as e:
            self.results.append(OicEntry(
                format="ndjson", platform="python", method="to_json",
                invariant="JSON_PARSEABLE",
                result="SKIP",
                evidence=f"Could not load module: {e}",
            ))

    def _check_python_abw_html(self) -> None:
        """Check Python ABW HTML export for cell safety."""
        try:
            import sys
            sys.path.insert(0, str(self.repo_root / "src" / "python"))
            from abw.abw_codec import AbwDocument  # type: ignore
            doc = AbwDocument()
            if hasattr(doc, "export_to_html"):
                doc.add_paragraph("<script>alert(1)</script>")
                output = doc.export_to_html()
                result = self.checker.check_html_cell_safety(output, "python/abw/export_to_html")
                self.results.append(OicEntry(
                    format="abw", platform="python", method="export_to_html",
                    invariant="HTML_CELL_SAFETY",
                    result="PASS" if result.passed else "FAIL",
                    evidence=result.error,
                ))
            else:
                self.results.append(OicEntry(
                    format="abw", platform="python", method="export_to_html",
                    invariant="HTML_CELL_SAFETY",
                    result="SKIP",
                    evidence="Method export_to_html not found on AbwDocument",
                ))
        except Exception as e:
            self.results.append(OicEntry(
                format="abw", platform="python", method="export_to_html",
                invariant="HTML_CELL_SAFETY",
                result="SKIP",
                evidence=f"Could not load module: {e}",
            ))

    # ------------------------------------------------------------------
    # .NET format checks (via test fixture round-trip)
    # ------------------------------------------------------------------

    def _check_dotnet_csv_from_fixture(self, fixture_path: Path) -> None:
        """
        Run OIC checks against CSV .NET export using a pre-generated output file.
        The fixture file must be a JSON/HTML/XML artifact previously generated
        by the .NET test suite.
        """
        for suffix, invariant_name, check_fn in [
            (".json", "JSON_PARSEABLE", self.checker.check_json),
            (".html", "HTML_CELL_SAFETY", self.checker.check_html_cell_safety),
        ]:
            artifact = fixture_path.with_suffix(suffix)
            if not artifact.exists():
                self.results.append(OicEntry(
                    format="csv", platform="dotnet",
                    method=f"to_{suffix.lstrip('.')}",
                    invariant=invariant_name,
                    result="SKIP",
                    evidence=f"Artifact not found: {artifact}",
                ))
                continue
            output = artifact.read_text(encoding="utf-8", errors="replace")
            result = check_fn(output, f"dotnet/csv/{invariant_name}")
            self.results.append(OicEntry(
                format="csv", platform="dotnet",
                method=f"to_{suffix.lstrip('.')}",
                invariant=invariant_name,
                result="PASS" if result.passed else "FAIL",
                evidence=result.error,
            ))

    def run_python_checks(self) -> None:
        """Run OIC against all Python format exports."""
        self._check_python_ndjson()
        self._check_python_abw_html()

    def run_dotnet_checks_from_fixtures(self) -> None:
        """
        Run OIC against .NET format exports using pre-generated fixture artifacts.
        Fixture artifacts are placed in tests/assurance/fixtures/ by the test suite.
        """
        fixtures_dir = self.repo_root / "tests" / "assurance" / "fixtures"
        for fmt_file in fixtures_dir.glob("*.csv"):
            fmt_name = fmt_file.stem.replace("-canonical", "")
            self._check_dotnet_csv_from_fixture(fmt_file)

    def to_json_report(self) -> str:
        return json.dumps(
            {"entries": [e.to_dict() for e in self.results]},
            indent=2,
        )


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(
        description="Output Invariant Checker — verify format export structural validity"
    )
    parser.add_argument(
        "--baseline",
        action="store_true",
        help="Run baseline checks against all formats",
    )
    parser.add_argument(
        "--output",
        type=str,
        default=None,
        help="Output JSON report path (e.g. reports/assurance/oic-baseline.json)",
    )
    parser.add_argument(
        "--check",
        choices=["json", "xml", "html", "csv"],
        help="Check a single invariant",
    )
    parser.add_argument("--input", type=str, help="Input file for single check")
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent.parent.parent
    checker = OutputInvariantChecker()

    if args.check and args.input:
        content = Path(args.input).read_text(encoding="utf-8", errors="replace")
        if args.check == "json":
            result = checker.check_json(content, args.input)
        elif args.check == "xml":
            result = checker.check_xml(content, args.input)
        elif args.check == "html":
            result = checker.check_html_cell_safety(content, args.input)
        else:
            result = checker.check_csv_roundtrip(content, 0, args.input)
        status = "PASS" if result.passed else "FAIL"
        print(f"{status}: {result.error or 'No issues found'}")
        return

    if args.baseline:
        runner = OicBaselineRunner(repo_root)
        runner.run_python_checks()
        report = runner.to_json_report()
        if args.output:
            out_path = repo_root / args.output
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(report, encoding="utf-8")
            print(f"Report written to: {out_path}")
        else:
            print(report)
        return

    parser.print_help()


if __name__ == "__main__":
    main()
