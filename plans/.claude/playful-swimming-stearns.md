# Specialist Machinery and Output Assurance Sprint
## Plan: playful-swimming-stearns
## Scope: ALL formats, ALL platforms (current and future)
**Mission ID:** MA-SYSTEM-WIDE-2026-07-04

---

## Current-State Reassessment (verified 2026-07-04)

Before execution, all assumptions were verified against the live codebase. Key changes since initial planning:

| Finding | Impact on Plan |
|---|---|
| CsvDocument.cs was **split** by PQLM-GOV-001 (commit `2554193f`) — analytics moved to `CsvDocumentAnalytics.cs` (604 LOC) | All analytics defects (GAP-CSV-003/004/008/009) target `CsvDocumentAnalytics.cs`, not `CsvDocument.cs` |
| CsvDocument.cs is now **275 LOC** (under 816 cap) | GAP-CSV-002 (LOC cap breach) is **obsolete** — no action needed |
| V130–V133 are **taken** by `governance_validators_found_issue.py` (added 2026-07-04) | Output quality validators must use **V134, V135, V136** |
| Governance validator count is now **133** (not 85) | Updated throughout |
| `tools/assurance/` directory does not exist | TC-A1 creates it from scratch |
| `governance_validators_output_quality.py` does not exist | TC-B1 creates it from scratch |
| All Sprint 2 tooling (CAQA, parity runner, gap hygiene) does not exist | TC-C1/C2/C3 start from zero |

---

## Context

This assurance sprint covers the complete format-factory system — 25 Python FOSS formats, all current .NET formats (CSV, FODS, FODT, HTML, NDJSON, TSV, TXT, ZST, NetPBM), and any future platform additions. The goal is to verify every format on every platform, heal all confirmed defects, and install durable gates that prevent the same defect classes from re-entering on any current or future format.

This is a production problem, not a library bug report. The standard is: after this sprint, defects of the confirmed classes cannot enter the codebase without tripping a governance gate.

---

## What the Investigation Found (verified against live source)

### 1. Defect class scan across all formats

| Defect Class | Python (25 formats) | .NET CSV | .NET FODS/FODT/HTML/NDJSON/etc. |
|---|---|---|---|
| A: Manual JSON escaping without control chars | SAFE — all use `json.dumps()` | **DEFECT** — `_JsonEsc` in `CsvDocumentAnalytics.cs:504` missing `\n\r\t` | SAFE — all use `JsonSerializer.Serialize()` |
| B: HTML output without escaping | SAFE — ABW uses `str.maketrans()`, others delegate | **DEFECT** — `ToHtml()` in `CsvDocumentAnalytics.cs:495` raw `{cell}` in `<td>` | SAFE — all use `WebUtility.HtmlEncode()` or `HtmlWriter.EscapeHtml()` |
| C: O(N²) column parse in loop/lambda | SAFE — no instances found | **DEFECT** — `RemoveOutliers` in `CsvDocumentAnalytics.cs:491` computes column inside `Where` | Not applicable (no analytics in other .NET formats) |
| D: Math.Log(2) divisor (units bug) | SAFE — all use `math.log2()` correctly | **DEFECT** — `GetColumnInformationContent` in `CsvDocumentAnalytics.cs:272` divides by `Math.Log(2)` | Not applicable (no analytics in other .NET formats) |

**Architectural root cause (unchanged):**
The CSV analytics layer uses private string helper methods (`_JsonEsc`, raw interpolation in `ToHtml()`) rather than delegating to stdlib (`System.Text.Json`, `WebUtility.HtmlEncode`). All other formats and all Python implementations use the delegation pattern, which is naturally safe. The private-helper pattern is risky and must be guarded by governance validators.

Note: The source was previously monolithic in `CsvDocument.cs`. PQLM-GOV-001 split it. The defects survived the split — they now live in `CsvDocumentAnalytics.cs`. The split did not fix the defects.

### 2. Confirmed issues in CSV .NET (verified against live source)

| Issue ID | Current Location | Description | Status |
|---|---|---|---|
| GAP-CSV-001 | `CsvReader.cs:36` | `ReadRows(string)` strips header row via `GetRange(1, all.Count - 1)` when auto-detecting file path | STILL EXISTS |
| GAP-CSV-002 | ~~CsvDocument.cs~~ | ~~866 LOC, baseline_loc_cap: 816~~ | **OBSOLETE** — file split done, now 275 LOC |
| GAP-CSV-003 | `CsvDocumentAnalytics.cs:272` | `GetColumnInformationContent` divides by `Math.Log(2)` — wrong units (produces nats not bits) | STILL EXISTS |
| GAP-CSV-004 | `CsvDocumentAnalytics.cs:491` | `RemoveOutliers` calls `ParseNumericColumn(GetColumn(...))` inside `Where` lambda — O(N²) | STILL EXISTS |
| GAP-CSV-005 | `CsvDocument.cs:128-129` | `[ThreadStatic] _filterHeaders` has a comment but no warning about async predicate incompatibility | STILL EXISTS |
| GAP-CSV-006 | `CsvDocument.cs:118-124` | `SetCellValue` silently returns on out-of-bounds; inconsistent with newer `SetCell()` which throws | STILL EXISTS |
| GAP-CSV-008 | `CsvDocumentAnalytics.cs:504` | `_JsonEsc` only escapes `\\` and `\"` — no `\n`, `\r`, `\t` — produces invalid JSON | STILL EXISTS |
| GAP-CSV-009 | `CsvDocumentAnalytics.cs:495` | `ToHtml()` interpolates `{cell}` and `{h}` raw into `<td>`/`<th>` — no `_HtmlEsc` method exists | STILL EXISTS |

### 3. What is already working and must not be changed

- Python implementations are clean (stdlib usage throughout). Do not alter this.
- Other .NET formats (FODS, FODT, HTML, NDJSON, TSV, TXT, ZST, NetPBM) are clean. Do not alter export logic in these.
- Oracle system (73/73 PASS), governance validators (133 active, V1–V133), SAL facts (14,441), control index — preserve as-is.
- The Python AST-based assertion quality classifier (`proof_adequacy_contract.py`) genuinely enforces strong assertions in Python sprints — preserve this.
- PQLM-GOV-001 split of `CsvDocument.cs` into main + analytics partials — do not undo this. Build on the split.

---

## Implementation Plan

**Part A: Verify all existing formats, heal confirmed defects.** Mandatory. Scope: all formats, all platforms.

**Part B: Install durable gates.** Prevents these defect classes from re-entering any current or future format.

**Part C (Sprint 2): Structural grading gaps.** C# assertion quality, cross-platform parity fixtures, gap ledger hygiene.

---

## Part A: Verification and Healing

### TC-A1: Build the Output Invariant Checker (OIC)

**Directory to create:** `tools/assurance/` (does not exist — create it)
**File to create:** `tools/assurance/output_invariant_checker.py`

**Purpose:** Given a format's export output, verify structural validity. Runs against ALL formats.

**Invariants to implement:**

```python
class OutputInvariantChecker:
    def check_json(self, output: str, context: str) -> InvariantResult:
        """JSON must be parseable by stdlib. Catches: manual escaping without control chars."""
        import json
        try:
            json.loads(output)
            return InvariantResult.pass_()
        except json.JSONDecodeError as e:
            return InvariantResult.fail(f"{context}: {e}")

    def check_xml(self, output: str, context: str) -> InvariantResult:
        """XML must be parseable. Catches: missing entity escaping, malformed tags."""
        import xml.etree.ElementTree as ET
        try:
            ET.fromstring(output)
            return InvariantResult.pass_()
        except ET.ParseError as e:
            return InvariantResult.fail(f"{context}: {e}")

    def check_html_cell_safety(self, output: str, context: str) -> InvariantResult:
        """HTML cell content must not contain raw < > & characters."""
        import re
        for tag in ('td', 'th'):
            for content in re.findall(rf'<{tag}>(.*?)</{tag}>', output, re.DOTALL):
                clean = re.sub(r'&(?:amp|lt|gt|quot|#\d+);', '', content)
                if re.search(r'[<>&]', clean):
                    return InvariantResult.fail(f"{context}: unescaped entity in <{tag}>: {content[:80]!r}")
        return InvariantResult.pass_()

    def check_csv_roundtrip(self, csv_output: str, expected_row_count: int, context: str) -> InvariantResult:
        """CSV output must re-parse to the same row count."""
        lines = [l for l in csv_output.splitlines() if l.strip()]
        actual = len(lines) - 1  # subtract header
        if actual != expected_row_count:
            return InvariantResult.fail(f"{context}: roundtrip row count {actual} != {expected_row_count}")
        return InvariantResult.pass_()
```

**Test suite:** `tests/supervisor/test_output_invariant_checker.py`
- `test_json_with_literal_newline_fails()` — `'{"k":"line1\nline2"}'` must fail (literal `\n`, not `\\n`)
- `test_json_with_escaped_newline_passes()` — `'{"k":"line1\\nline2"}'` must pass
- `test_html_with_script_tag_fails()` — `'<td><script>alert(1)</script></td>'` must fail
- `test_html_with_escaped_script_passes()` — `'<td>&lt;script&gt;</td>'` must pass
- `test_xml_malformed_fails()` — missing closing tag must fail
- `test_xml_valid_passes()` — well-formed XML must pass
- `test_csv_roundtrip_correct_count()` — 3-row CSV parses back to 3 rows

**Acceptance criterion:** 7/7 tests pass before TC-A2 begins.

---

### TC-A2: Run OIC baseline against ALL existing format exports

**Purpose:** Confirm the survey findings with machine-verified evidence before any fixes.

**Scope — Python formats:**

| Format | Export method to test | Expected |
|---|---|---|
| ndjson | `to_json()` / `ndjson_dumps()` | PASS |
| fods | `csv_exporter.py` export | PASS |
| ods | `ods_csv_exporter.py` export | PASS |
| abw | `export_to_html()` | PASS |
| All others | No JSON/HTML export → skip | N/A |

**Scope — .NET formats:**

| Format | Export method(s) | Expected (pre-fix) |
|---|---|---|
| csv | `ToJson()`, `ExportToNdjson()`, `ToHtml()`, `ExportToXml()` | **FAIL** on JSON and HTML |
| fods | `FodsJsonExporter`, `FodsHtmlExporter` | PASS |
| fodt | HTML exporter | PASS |
| html | `HtmlWriter.WriteTable()` | PASS |
| ndjson | `NdjsonWriter.WriteRecords()` | PASS |
| All others | No JSON/HTML export | N/A |

**Output:** `reports/assurance/oic-baseline-<run_id>.json`

```json
{
  "format": "csv",
  "platform": "dotnet",
  "method": "ToJson",
  "invariant": "JSON_PARSEABLE",
  "result": "FAIL",
  "evidence": "JSONDecodeError: Invalid control character at line 2, column 8"
}
```

**Acceptance criterion:** OIC baseline produces documented FAIL entries for CSV .NET `ToJson()` and `ToHtml()`. All other formats PASS. This is proof of instrument validity.

---

### TC-A3: Fix all confirmed defects

**Files to modify:**
- `src/net/csv/CsvDocumentAnalytics.cs` — primary target (GAP-CSV-003, 004, 008, 009)
- `src/net/csv/CsvDocument.cs` — secondary (GAP-CSV-005, 006)
- `src/net/csv/CsvReader.cs` — GAP-CSV-001

**Conway §5 governance compliance (mandatory before modifying any file):**
1. Read the COMPLETE file before any edit
2. Confirm file ownership (CsvDocumentAnalytics.cs is the analytics partial, CsvDocument.cs is the main partial)
3. Preserve all unrelated code — do not alter unaffected methods
4. Review the diff before finalizing

Apply fixes in this order:

**Fix 1 — `_JsonEsc` (GAP-CSV-008, HIGH):** Add control char escaping.
Target: `CsvDocumentAnalytics.cs:504`
```csharp
// Current (DEFECTIVE):
private static string _JsonEsc(string s) => s.Replace("\\", "\\\\").Replace("\"", "\\\"");

// Fixed:
private static string _JsonEsc(string s) =>
    s.Replace("\\", "\\\\").Replace("\"", "\\\"")
     .Replace("\n", "\\n").Replace("\r", "\\r").Replace("\t", "\\t");
```
**Before applying:** Search test files for `ToJson\|ExportToJson\|ExportToNdjson` — update any tests asserting the old literal-newline behavior.

**Fix 2 — `ToHtml()` (GAP-CSV-009, MEDIUM-SEC):** Add HTML escaping.
Target: `CsvDocumentAnalytics.cs` — add helper and update `ToHtml()`
```csharp
// Add helper (after _JsonEsc):
private static string _HtmlEsc(string s) =>
    s.Replace("&", "&amp;").Replace("<", "&lt;").Replace(">", "&gt;")
     .Replace("\"", "&quot;").Replace("'", "&#39;");

// In ToHtml(): change {cell} → {_HtmlEsc(cell)} and {h} → {_HtmlEsc(h)}
```
**Before applying:** Search for `ToHtml\|ExportToHtml` in test files for tests asserting unescaped content.

**Fix 3 — `GetColumnInformationContent` (GAP-CSV-003, MEDIUM):** Remove wrong unit conversion.
Target: `CsvDocumentAnalytics.cs:272`
```csharp
// Current (WRONG — converts bits to nats):
public double GetColumnInformationContent(string headerName) => GetColumnEntropy(headerName) / Math.Log(2);

// Fixed (information content = entropy in bits, no conversion needed):
public double GetColumnInformationContent(string headerName) => GetColumnEntropy(headerName);
```
**Before applying:** Search test files for `InformationContent` — update any test asserting the old nats value.

**Fix 4 — `RemoveOutliers` O(N²) (GAP-CSV-004, LOW-PERF):** Move column parse outside lambda.
Target: `CsvDocumentAnalytics.cs:491`
Compute `vals`, `mean`, `stddev` ONCE before the `Where` lambda — not once per row.

**Fix 5 — ReadRows asymmetry (GAP-CSV-001, MEDIUM):**
Target: `CsvReader.cs:36`
Remove `all.GetRange(1, all.Count - 1)`. The header strip is not the contract of `ReadRows()`. Callers that need data-only rows strip it themselves (as `CsvDocument.LoadFile` already does).
**Before applying:** Search test files for `ReadRows(` with temp file paths — update any that depend on current stripping behavior.

**Fix 6 — Documentation gaps (GAP-CSV-005, GAP-CSV-006):**
- `CsvDocument.cs:128-129` — add `<remarks>` warning: async predicates are not supported due to `[ThreadStatic]` storage. `ConfigureAwait(false)` paths will see null `_filterHeaders`.
- `CsvDocument.cs:118-124` — add `<remarks>` documenting the intentional silent-return contract, and noting that `SetCell()` is the throwing alternative.

~~**Fix 7 — Baseline registry (GAP-CSV-002):**~~
**OBSOLETE.** CsvDocument.cs is now 275 LOC (under 816 cap). The split already happened via PQLM-GOV-001. No cap breach to acknowledge.

**After all fixes:**
```
dotnet build src/net/csv/FormatFactory.Csv.csproj --configuration Release
dotnet test tests/net/csv/FormatFactory.Csv.Tests.csproj --configuration Release
```
Target: 0 build errors, ≥ 1609 tests passing, 0 failing.

---

### TC-A4: Run OIC post-fix verification against ALL formats

Re-run the same OIC baseline from TC-A2 after all fixes are applied.

**Expected:**
- CSV .NET `ToJson()`: **PASS** (was FAIL before)
- CSV .NET `ToHtml()`: **PASS** (was FAIL before)
- All other formats: unchanged (still PASS)

**Output:** `reports/assurance/oic-post-fix-<run_id>.json`

**Acceptance criterion:** `FORMATS_WITH_FAIL_POST_FIX = 0`

---

## Part B: Durable Gates (Current and Future Formats)

### TC-B1: Add governance validators for the unsafe architectural pattern

**Governance compliance (verified against live system):**
- V1–V133 are all in use (133 validators total as of 2026-07-04)
- V130 = `validate_dotnet_loc_cap_static`, V131 = `validate_found_issue_disposition`, V132 = `validate_found_issue_escalation`, V133 = `validate_found_issue_invalid_disposition` — ALL TAKEN in `governance_validators_found_issue.py`
- **Next available IDs: V134, V135, V136**
- File to create: `tools/supervisor/governance_validators_output_quality.py` (does not exist — new file, domain-specific naming pattern matching `governance_validators_layers.py`, `governance_validators_path.py`, etc.)
- Do NOT add to `governance_validators_ext4.py` (owns V111–V129, TC-ARC-012 domain)
- Do NOT add to `governance_validators_found_issue.py` (owns V130–V133, PQLM-GOV-001 domain)

**V134 — `validate_no_manual_json_escaping_in_dotnet`**
```python
def validate_no_manual_json_escaping_in_dotnet(repo_root: Path, changed_files: list[str]) -> ValidationResult:
    """
    V134: .NET source files must not use manual string Replace chains to escape JSON.
    All JSON output must go through System.Text.Json.JsonSerializer or JsonDocument.
    Detects: .Replace("\\\\", ...).Replace("\\\"", ...) chain without System.Text.Json import.
    Root cause: CsvDocumentAnalytics.cs _JsonEsc bug (GAP-CSV-008). Prevents recurrence.
    """
    import re
    failures = []
    for rel_path in changed_files:
        if not rel_path.endswith('.cs') or '/src/net/' not in rel_path.replace('\\', '/'):
            continue
        content = (repo_root / rel_path).read_text(encoding='utf-8', errors='replace')
        if re.search(r'\.Replace\s*\(\s*"\\\\\\\\"\s*,.*\.Replace\s*\(\s*"\\\\\\""\s*,', content):
            if 'System.Text.Json' not in content:
                failures.append(f"{rel_path}: manual JSON escaping without System.Text.Json import")
    return ValidationResult(passed=len(failures) == 0, failures=failures,
                            rule="V134: Use System.Text.Json for JSON output, not manual Replace chains")
```

**V135 — `validate_html_escaping_in_dotnet`**
```python
def validate_html_escaping_in_dotnet(repo_root: Path, changed_files: list[str]) -> ValidationResult:
    """
    V135: .NET source files that produce <td>/<th> HTML must use WebUtility.HtmlEncode or HtmlWriter.EscapeHtml.
    Detects: C# string interpolation with <td>{...} without an escaping call on the value.
    Root cause: CsvDocumentAnalytics.cs ToHtml() bug (GAP-CSV-009). Prevents recurrence.
    """
    import re
    failures = []
    for rel_path in changed_files:
        if not rel_path.endswith('.cs') or '/src/net/' not in rel_path.replace('\\', '/'):
            continue
        content = (repo_root / rel_path).read_text(encoding='utf-8', errors='replace')
        if re.search(r'<td>\{(?!_HtmlEsc|HtmlEncode|EscapeHtml)', content):
            failures.append(f"{rel_path}: HTML <td> interpolation without escaping call")
    return ValidationResult(passed=len(failures) == 0, failures=failures,
                            rule="V135: HTML output must escape values with WebUtility.HtmlEncode or equivalent")
```

**V136 — `validate_html_escaping_in_python`**
```python
def validate_html_escaping_in_python(repo_root: Path, changed_files: list[str]) -> ValidationResult:
    """
    V136: Python source files that produce <td>/<th> HTML must use html.escape() or str.maketrans().
    Detects: f-string with <td>{variable} without html.escape() or .translate() call.
    Confirms existing Python baseline is clean; blocks future regressions.
    """
    import re
    failures = []
    for rel_path in changed_files:
        if not rel_path.endswith('.py') or '/src/python/' not in rel_path.replace('\\', '/'):
            continue
        content = (repo_root / rel_path).read_text(encoding='utf-8', errors='replace')
        if re.search(r'f["\']<t[dh]>\{(?!html\.escape|\.translate)', content):
            failures.append(f"{rel_path}: HTML <td>/<th> interpolation without html.escape() or str.maketrans()")
    return ValidationResult(passed=len(failures) == 0, failures=failures,
                            rule="V136: Python HTML output must escape values with html.escape() or str.maketrans()")
```

**Registration:** Wire V134/V135/V136 into the governance runner following the pattern used by `governance_validators_found_issue.py` — add to the runner's try-block as WARN (non-blocking) initially.

**Test suite:** `tests/supervisor/test_governance_validators_output_quality.py`
- `test_v134_catches_manual_json_replace()` — .cs snippet with Replace chain + no JsonSerializer import → FAIL
- `test_v134_passes_with_json_serializer()` — .cs snippet with `JsonSerializer.Serialize()` → PASS
- `test_v135_catches_unescaped_td()` — .cs snippet with `$"<td>{cell}</td>"` → FAIL
- `test_v135_passes_with_htmlencode()` — .cs snippet with `$"<td>{WebUtility.HtmlEncode(cell)}</td>"` → PASS
- `test_v136_catches_python_unescaped_td()` — Python snippet with `f"<td>{value}</td>"` → FAIL
- `test_v136_passes_with_html_escape()` — Python snippet with `f"<td>{html.escape(value)}</td>"` → PASS

---

### TC-B2: Wire OIC into sprint closeout

**File to modify:** `tools/supervisor/autonomous_cycle.py`

Add OIC execution as `STEP_0B` (after evidence collection, before grading). Triggers only when `changed_files` contains export method signatures:

```python
EXPORT_METHOD_SIGNATURES = [
    'ToJson', 'ExportToJson', 'ExportToNdjson',
    'ToHtml', 'ExportToHtml', 'ExportToXml',
    'to_json', 'export_json', 'to_html', 'export_html',
]

def _should_run_oic(changed_files: list[str], diff_content: str) -> bool:
    return any(sig in diff_content for sig in EXPORT_METHOD_SIGNATURES)
```

When triggered:
1. Run OIC against the modified format's canonical test fixture (see TC-B3)
2. If any invariant fails: add to `rework_items` in the continuation signal
3. Never block the sprint (best-effort, Supreme Directive compliance)
4. Write `reports/assurance/oic-<run_id>.json` with results

---

### TC-B3: Create canonical test fixtures for OIC

**Directory to create:** `tests/assurance/fixtures/` (does not exist)

For each format with export methods, maintain a small canonical document (3–5 rows, 3 columns) that includes:
- A cell value with `\n` (tests JSON control char escaping)
- A cell value with `<script>alert(1)</script>` (tests HTML escaping)
- A cell value with `&` (tests both JSON and HTML)
- Normal values

**Fixture files to create:**
```
tests/assurance/fixtures/csv-canonical.csv
tests/assurance/fixtures/fods-canonical.fods
tests/assurance/fixtures/ndjson-canonical.ndjson
```

---

### TC-B4: Update format templates for future platform safety

**File to modify:** The `/new-format-kickstart` skill template (search `tools/supervisor/` for the template definition).

Wherever the kickstart skill generates:
1. JSON export template → always use `json.dumps()` (Python) or `JsonSerializer.Serialize()` (.NET), with a comment: `# OIC-REQUIRED: use stdlib JSON serialization`
2. HTML export template → always use `html.escape()` (Python) or `WebUtility.HtmlEncode()` (.NET), with a comment: `// OIC-REQUIRED: escape all HTML cell content`
3. Include an OIC smoke test in the generated test file for the new format

---

## Part C: Structural Grading Gaps — Sprint 2

These execute immediately after Sprint 1 completes. Sprint 2 does not require user authorization.

### TC-C1: C# Assertion Quality Analyzer

**Problem:** `proof_adequacy_contract.py` grades Python test assertion strength (STRONG/PARTIAL/WEAK). No equivalent exists for C# xunit tests. .NET tests are graded on count only, not assertion quality. The 179 CSV .NET test files have never been evaluated for assertion quality.

**File to create:** `tools/assurance/csharp_assertion_analyzer.py`

```python
class CSharpAssertionAnalyzer:
    STRONG_PATTERNS = [
        r'Assert\.Equal\s*\(\s*[-\d\.]+\s*,',       # Assert.Equal(2.75, ...)
        r'Assert\.Equal\s*\(\s*"[^"]+"\s*,',         # Assert.Equal("Alice", ...)
        r'Assert\.Equal\s*\(\s*\d+\s*,\s*\w',        # Assert.Equal(3, result)
        r'Assert\.InRange\s*\(',                     # Assert.InRange(x, lo, hi)
        r'Assert\.Equal\s*\(.*?precision\s*:',       # Assert.Equal(x, y, precision: 3)
        r'Assert\.Contains\s*\(\s*"[^"]+"\s*,',      # Assert.Contains("Alice", list)
    ]
    WEAK_PATTERNS = [
        r'Assert\.NotNull\s*\(',
        r'Assert\.NotEmpty\s*\(',
        r'Assert\.True\s*\(\s*\w+\s*[><!]=?\s*[\d\w]',
    ]
    STRONG_RATIO_THRESHOLD = 0.3  # Lower than Python's 0.5 — initial calibration
```

**Integration:** Wire into `grade_declared_work.py`. Route `.cs` test files through `CSharpAssertionAnalyzer` alongside existing Python grading. `_downgrade_map` fires identically.

**Tests:** `tests/supervisor/test_csharp_assertion_analyzer.py` — 6 tests covering STRONG/WEAK classification and file-level ratio thresholds.

**Apply:** Run against all 179 test files in `tests/net/csv/`. Generate `reports/assurance/dotnet-assertion-quality-<run_id>.json`. Upgrade WEAK_PROOF tests covering fixed methods.

---

### TC-C2: Cross-Platform Behavioral Parity Fixtures

**Problem:** Python and .NET both implement CSV analytics. There is no automated check that they agree numerically. The `GetColumnInformationContent` bug (wrong units) would NOT have been caught by any existing test.

**Files to create:**
- `tests/cross-platform/csv/parity-fixtures.yaml` — 15 behavioral contracts (hand-computed, NOT from any implementation)
- `tools/assurance/cross_platform_parity_runner.py` — runner

**Key fixtures (hand-computed expected values):**

```yaml
- id: CPF-CSV-001
  method_dotnet: GetColumnMean
  input: "Value\n1.0\n2.0\n3.0\n4.0\n"
  column: Value
  expected: 2.5
  derivation: "(1+2+3+4)/4 = 2.5"

- id: CPF-CSV-003
  method_dotnet: GetColumnEntropy
  input: "Label\nA\nA\nB\nB\n"
  column: Label
  expected: 1.0
  derivation: "-0.5*log2(0.5) - 0.5*log2(0.5) = 1.0 bit"

- id: CPF-CSV-004
  method_dotnet: GetColumnInformationContent
  input: "Label\nA\nA\nB\nB\n"
  column: Label
  expected: 1.0
  derivation: "Information content = entropy in bits = 1.0"
  note: "This fixture specifically catches the Math.Log(2) units bug"
  # ... 11 more covering StdDev, Median, Mode, Variance, IQR, Min, Max, Sum, Range, Correlation, Skewness
```

**Integration:** Run as `STEP_0C` in `autonomous_cycle.py` when changed files include `src/net/csv/` or `src/python/csv/`.

---

### TC-C3: Gap Ledger Orphan Detection

**Problem:** When capabilities are suspended, gap ledger entries remain OPEN → phantom work in next sprint → generates tests for deleted features → test count swings. No current mechanism detects orphaned entries.

**File to create:** `tools/supervisor/gap_ledger_hygiene.py`

```python
class GapLedgerHygiene:
    def find_orphaned_entries(self, ledger_path: Path, repo_root: Path) -> list[OrphanedEntry]:
        """An entry is orphaned when referenced test files no longer exist on disk."""
        ...

    def report(self, orphans: list, output_path: Path) -> None:
        """Always write a report. Never auto-close without explicit --apply flag."""
        ...

    def apply_closures(self, orphans: list, ledger_path: Path) -> CleanupResult:
        """Closes orphaned entries. Requires --apply flag."""
        ...
```

**Sprint 2 execution:** Run in dry-run mode first. Review output. Apply confirmed closures.

---

## Sprint Schedule

### Sprint 1 (This Sprint) — Parts A and B

| Phase | Tasks | Target |
|---|---|---|
| Phase 1: Instrument | TC-A1 (build OIC + 7 tests) | OIC tool + 7 tests passing |
| Phase 2: Baseline | TC-A2 (run OIC against all formats pre-fix) | FAIL confirmed for CSV .NET, PASS for all others |
| Phase 3: Heal | TC-A3 (fix 6 defects — GAP-CSV-001/003/004/005/006/008/009) | Build clean, ≥ 1609 tests passing |
| Phase 4: Verify | TC-A4 (re-run OIC post-fix) | ALL formats ALL invariants PASS |
| Phase 5: Gate | TC-B1 (V134/V135/V136 validators + 6 tests) | Validators active in governance runner |
| Phase 6: Wire | TC-B2 (OIC into closeout), TC-B3 (fixtures), TC-B4 (templates) | OIC triggered on export-method changes |

### Sprint 2 (Immediate Follow-On — No User Authorization Required) — Part C

| Phase | Tasks | Target |
|---|---|---|
| Phase 1: C# Grading | TC-C1: build analyzer, tests, wire, run against 179 .NET tests | Quality distribution report + WEAK_PROOF upgrades |
| Phase 2: Parity | TC-C2: 15 hand-computed fixtures, runner, run checks | All 15 CPF fixtures PASS |
| Phase 3: Hygiene | TC-C3: build orphan detector, dry-run, apply confirmed closures | Orphan report + ledger cleanup |

---

## Critical Files

| Role | Path | Action in This Sprint |
|---|---|---|
| Primary analytics defects | `src/net/csv/CsvDocumentAnalytics.cs` | Fix GAP-CSV-003,004,008,009 |
| Secondary defects | `src/net/csv/CsvDocument.cs` | Fix GAP-CSV-005,006 |
| Reader defect | `src/net/csv/CsvReader.cs` | Fix GAP-CSV-001 |
| Baseline registry | `registry/source-structure-baseline.json` | Verify CsvDocumentAnalytics.cs has a baseline entry |
| New tool | `tools/assurance/output_invariant_checker.py` | Create (directory does not exist) |
| New validators | `tools/supervisor/governance_validators_output_quality.py` | Create with V134/V135/V136 |
| New tests (OIC) | `tests/supervisor/test_output_invariant_checker.py` | Create |
| New tests (validators) | `tests/supervisor/test_governance_validators_output_quality.py` | Create |
| Sprint closeout integration | `tools/supervisor/autonomous_cycle.py` | Wire OIC as STEP_0B |
| Fixture files | `tests/assurance/fixtures/` | Create directory + 3 canonical fixtures |
| Kickstart template | `tools/supervisor/` (search for new-format-kickstart template) | Update JSON/HTML templates |

---

## Verification Steps

```bash
# Step 1: OIC tool self-test
.venv/Scripts/pytest tests/supervisor/test_output_invariant_checker.py -v
# Expected: 7/7 PASS

# Step 2: Governance validator tests
.venv/Scripts/pytest tests/supervisor/test_governance_validators_output_quality.py -v
# Expected: 6/6 PASS

# Step 3: OIC baseline (pre-fix) — confirms tool detects the known defects
python tools/assurance/output_invariant_checker.py --baseline --output reports/assurance/oic-baseline.json
# Expected: CSV .NET ToJson → FAIL, CSV .NET ToHtml → FAIL, all others → PASS

# Step 4: Build CSV .NET after fixes
dotnet build src/net/csv/FormatFactory.Csv.csproj --configuration Release
# Expected: 0 errors

# Step 5: Full CSV .NET test suite
dotnet test tests/net/csv/FormatFactory.Csv.Tests.csproj --configuration Release
# Expected: >= 1609 PASS, 0 FAIL

# Step 6: OIC post-fix — confirms all defects healed
python tools/assurance/output_invariant_checker.py --baseline --output reports/assurance/oic-post-fix.json
# Expected: ALL formats ALL invariants → PASS
```

---

## Completion Gate

### Sprint 1 Gate
```
OIC_TOOL_BUILT_AND_TESTED = true           # TC-A1
OIC_BASELINE_DOCUMENTED = true             # TC-A2 — FAIL entries confirmed for CSV .NET before fix
CONFIRMED_DEFECTS_FIXED = 6                # TC-A3 — GAP-CSV-001/003/004/005/006/008/009
  (GAP-CSV-002 is OBSOLETE — split already done)
DOTNET_BUILD_CLEAN = true                  # TC-A3
DOTNET_TESTS_PASS >= 1609                  # TC-A3
OIC_POST_FIX_ALL_PASS = true               # TC-A4 — zero FAIL entries after fix
GOVERNANCE_VALIDATORS_ADDED = 3            # TC-B1 — V134, V135, V136
VALIDATOR_TESTS_PASS = 6                   # TC-B1
OIC_WIRED_INTO_CLOSEOUT = true             # TC-B2
CANONICAL_FIXTURES_CREATED = 3            # TC-B3
FORMAT_TEMPLATES_UPDATED = true            # TC-B4
PYTHON_FORMAT_BASELINE = ALL_PASS          # TC-A2 confirms Python is clean
DOTNET_OTHER_FORMATS_BASELINE = ALL_PASS   # TC-A2 confirms FODS/FODT/etc. are clean
```

### Sprint 2 Gate
```
CAQA_TOOL_BUILT_AND_TESTED = true          # TC-C1
CAQA_WIRED_INTO_GRADING = true             # TC-C1
DOTNET_TEST_QUALITY_REPORT_FILED = true    # TC-C1 — quality distribution for 179 CSV tests
WEAK_PROOF_TESTS_UPGRADED >= 1             # TC-C1
PARITY_FIXTURES_DEFINED = 15              # TC-C2
PARITY_RUNNER_BUILT = true                 # TC-C2
FAILED_PARITY_FIXTURES = 0                 # TC-C2
ORPHAN_DETECTOR_BUILT = true               # TC-C3
ORPHAN_REPORT_FILED = true                 # TC-C3
GAP_LEDGER_CLOSURES_APPLIED = true         # TC-C3
```

---

## Taskcard Status

### Sprint 1 — Parts A and B

| TC-ID | Title | Part | Priority | Status |
|---|---|---|---|---|
| TC-A1 | Build Output Invariant Checker | A | P0 | OPEN |
| TC-A2 | OIC baseline against ALL formats (pre-fix) | A | P0 | OPEN |
| TC-A3 | Fix all confirmed defects in CSV .NET (6 fixes, target: CsvDocumentAnalytics.cs + CsvDocument.cs + CsvReader.cs) | A | P0 | OPEN |
| TC-A4 | OIC post-fix verification against ALL formats | A | P0 | OPEN |
| TC-B1 | Add governance validators V134/V135/V136 in governance_validators_output_quality.py | B | P1 | OPEN |
| TC-B2 | Wire OIC into sprint closeout (autonomous_cycle.py STEP_0B) | B | P1 | OPEN |
| TC-B3 | Create canonical OIC fixtures (tests/assurance/fixtures/) | B | P1 | OPEN |
| TC-B4 | Update new-format-kickstart templates for safe JSON/HTML defaults | B | P2 | OPEN |

### Sprint 2 — Part C (immediate follow-on, no user authorization required)

| TC-ID | Title | Part | Priority | Status |
|---|---|---|---|---|
| TC-C1 | C# Assertion Quality Analyzer — build, test, wire into grading, apply to 179 .NET tests | C | P1 | OPEN |
| TC-C2 | Cross-Platform Parity Fixtures — 15 hand-computed contracts, runner, apply to CSV | C | P1 | OPEN |
| TC-C3 | Gap Ledger Orphan Detection — build, dry-run, apply confirmed closures | C | P2 | OPEN |
