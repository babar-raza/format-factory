# Deep Machinery Assurance — V149 Stub Gate: Structural Defect and Durable Fix
# plan: twinkly-nibbling-platypus
# plan_type: machinery_hardening
# mission_id: DMA-STUB-V149-001
# created: 2026-07-10

---

## What Was Read

Before writing this plan, the following were read in full from source:

- `tools/review/no_stub_scan.py` (228 lines, complete)
- `tools/supervisor/governance_validators_ext4.py` lines 790–872 (V149 implementation)
- `tools/supervisor/governance_validators_ext3.py` lines 450–650 (V105/V106 with `_load_baseline`)
- `registry/source-structure-baseline.json` schema (V105/V106 baseline model)
- `git diff HEAD -- tools/review/no_stub_scan.py` (exact uncommitted changes)
- `governance_validator_runner.py` for `expected_count` (167) and V149 registration (lines 757–765)
- `grep -rn "raise NotImplementedError" src/python` (1 match: `fodp_codec.py:216`)

---

## Symptoms, Root Causes, and Structural Weaknesses

### Symptoms (visible)

1. `parallel-foraging-fairy` had to clean up 9 pre-existing violations before V149 could go blocking.
2. TC-SC-003 introduced `re.compile(r"raise\s+NotImplementedError\(")` — an unconditional allowlist pattern that suppresses any line matching `raise NotImplementedError(...)` anywhere in `src/python/`.
3. MEMORY.md records `expected_count=165`; the runner contains `expected_count: 167`. One is stale.
4. V105/V106 use a 500/600-char window documented with a comment explaining why the old 300/400-char windows silently missed violations after a 97-char comment was added.

### Root Causes

**Root cause 1 (primary): V149 is a global zero-tolerance gate with no baseline mechanism.**

V105/V106 call `_load_baseline(repo_root)`, which reads `registry/source-structure-baseline.json`. That file tracks which violations are pre-existing (known) vs. new (introduced by the current sprint). Known violations produce `WARN, blocks_sprint=False`. New violations produce `FAIL, blocks_sprint=True`.

V149 has no equivalent. It scans all of `src/python/`, aggregates all violations, and blocks any sprint with `PRODUCT_SOURCE` or `RELEASE_GATE` items if *any* violation exists anywhere in the directory. There is no distinction between a violation in a file you touched today and a violation in a file last touched three months ago.

This means:
- A stub introduced in any sprint by any format blocks ALL future product sprints until fixed.
- The only escape valve is the allowlist — which is scanner code, not governance data.
- The parallel-foraging-fairy cleanup sprint exists precisely because this escape valve was needed before the gate could go blocking. This cycle will repeat.

**Root cause 2 (secondary): The allowlist is being used as a baseline substitute, which inverts the safety model.**

The correct use of the allowlist is to suppress structural false positives — patterns that appear in legitimate code but superficially resemble stubs (e.g., `text:placeholder` as an ODF XML element name). These are genuinely impossible to distinguish from stubs by term matching alone.

TC-SC-003 used the allowlist for a different purpose: to govern an intentional design decision (FODP is read-only; its write function deliberately raises `NotImplementedError`). The correct place to record this is a governance data file, not scanner code. When the allowlist is used for governance, it becomes unbounded: every future intentional stub adds a pattern, patterns accumulate, and the gate's sensitivity degrades.

The `raise\s+NotImplementedError\(` pattern is the most acute example. It was added to govern one line in `fodp_codec.py:216`. But it silently allows every future `raise NotImplementedError(...)` anywhere in `src/python/`. The grep confirms this risk: today there is 1 instance. Next sprint there could be 5.

**Root cause 3 (secondary): V105/V106 detection windows are magic numbers.**

The windows (500 chars for V105, 600 for V106) are headroom above the observed failure point (97-char comment pushed dict accesses past 300/400). The comment in the code documents this. But the headroom has no structural guarantee — it correlates with current code patterns and will fail again when code structure changes. No test verifies that the current window is sufficient for the actual method bodies being scanned.

### Structural Weaknesses

| Weakness | Impact | Recurrence |
|---|---|---|
| V149 global scan with no baseline | Any violation anywhere blocks all product work globally | Every sprint that introduces a stub anywhere |
| Allowlist as governance substitute | Gate sensitivity degrades as allowlist grows | Every new "false positive" that is actually an intentional design |
| `raise NotImplementedError(` pattern | Entire class of stubs silently allowed | Any future stub using this common Python pattern |
| V105/V106 character windows | Silent misses when method preambles exceed window | Any code change that adds comments/guards to scanned methods |

---

## What Must Be Preserved

| Component | Reason |
|---|---|
| Forbidden terms list | Correct scope; catches real stubs |
| Allowlist mechanism for STRUCTURAL false positives | ODF XML names, anti-stub docs, gap-ledger refs — these cannot be distinguished by structure |
| TC-SC-001 patterns (NamedTemporaryFile, ruff:noqa) | Genuine false positives, not governance exceptions |
| TC-SC-002 nested-package exclusion | Correct; editable-install artifacts should be excluded |
| TC-SC-004 governed-TODO pattern | Correct; explicitly tracked TODOs are not stubs |
| `NotImplementedError:\s+Always` pattern | Governs the FODP docstring at line 214 |
| AST pass-only detection | Correct and valuable |
| V149 `has_product` blocking condition | Correct scope for blocking |
| `_load_baseline()` helper in ext3 | Reuse directly; don't reimplement |

## What Must Be Changed

| Component | Change | Reason |
|---|---|---|
| V149 | Add baseline-tracking (mirror V105/V106) | Eliminates global cascade blocking |
| `raise\s+NotImplementedError\(` allowlist | Remove | Over-broad; FODP case moves to baseline registry |
| FODP exception | Move from allowlist to `registry/stub-violations-baseline.json` | Governance data, not scanner code |
| V105/V106 window scan | Replace with method-boundary extraction | Eliminates recurrence |
| `expected_count` assertion | Verify actual test assertion; fix if `==` not `>=` | Eliminates test-break on each new validator |
| MEMORY.md expected_count entry | Correct 165 → 167 | Stale |

---

## The Durable Design

V149 gets a parallel baseline registry: `registry/stub-violations-baseline.json`.

Schema mirrors `source-structure-baseline.json`:
```json
{
  "policy": "stub-violations-baseline v1 — known/governed violations; new violations always fail",
  "known_violations": {
    "src/python/fodp/fodp_codec.py": {
      "governing_id": "TC-SC-003",
      "governing_reason": "write_fodp deliberately raises NotImplementedError — FODP is read-only by design",
      "violation_kinds": ["forbidden_term"],
      "added_at": "2026-07-10",
      "added_by": "twinkly-nibbling-platypus"
    }
  }
}
```

V149's evaluation logic becomes:

```python
baseline = _load_stub_baseline(repo)  # reads stub-violations-baseline.json
result = _stub_report([scan_root])
violations = result.get("violations", [])

known_paths = set(baseline.get("known_violations", {}).keys())

new_violations = [
    v for v in violations
    if not _violation_is_known(v, known_paths, baseline)
]
known_violations = [v for v in violations if v not in new_violations]
```

Where `_violation_is_known(v, known_paths, baseline)` checks:
- The violation's file path (relative to repo root) is in `known_paths`
- AND the violation's `kind` is in the baseline entry's `violation_kinds`

This matches the V105/V106 pattern exactly. New violations → FAIL. Known violations → WARN.

**Why file-path keying (not file+line)?**
Line numbers shift when code is reformatted or neighbors change. File-path keying matches the V105/V106 precedent. If a new genuine stub is added to `fodp_codec.py`, it is still flagged — the baseline doesn't grant blanket immunity to a file, it only grandfathers violations of the specified kinds that were present when the baseline entry was added. The governance entry must explicitly list the `violation_kinds`.

**Why a separate file rather than adding to source-structure-baseline.json?**
`source-structure-baseline.json` governs LOC/function count violations for V66/V77/V105/V106. Mixing stub violation records into the same file conflates two distinct governance concerns. A separate file has a clearer scope and can be independently reviewed.

---

## Taskcard Status Table

| Task ID | Title | Status |
|---|---|---|
| TC-TNP-001 | BIND: copy plan, write lock, confirm current clean baseline (0 violations) | OPEN |
| TC-TNP-002 | PROVE the structural defect with a live reproduction | OPEN |
| TC-TNP-003 | CREATE `registry/stub-violations-baseline.json` with FODP entry | OPEN |
| TC-TNP-004 | ADD `_load_stub_baseline` + baseline-aware classification to V149 | OPEN |
| TC-TNP-005 | REMOVE `raise\s+NotImplementedError\(` from allowlist; verify FODP still passes | OPEN |
| TC-TNP-006 | FIX V105/V106: replace character windows with method-boundary extraction | OPEN |
| TC-TNP-007 | VERIFY: expected_count assertion in tests; correct MEMORY.md | OPEN |
| TC-TNP-008 | CLEAN UP: .runner_system_id → .gitignore; document stale continuation signal | OPEN |
| TC-TNP-009 | VERIFY: full governance suite (≥167), test suite (≥1169), idempotency | OPEN |
| TC-TNP-010 | COMMIT + LIFECYCLE AUDIT + TERMINAL CLOSE | OPEN |

---

## TC-TNP-001: BIND Mission

**Steps:**
1. Copy this plan to `plans/.claude/twinkly-nibbling-platypus.md`
2. `python tools/supervisor/write_plan_lock.py --plan-path plans/.claude/twinkly-nibbling-platypus.md`
3. Run `python tools/review/no_stub_scan.py src/python --json` → confirm `"status": "CLEAN"` (0 violations). Record output as baseline evidence.
4. Run `git diff HEAD -- tools/review/no_stub_scan.py tools/supervisor/governance_validators_ext4.py` → record as TC-TNP-001 evidence.
5. Read `src/python/fodp/fodp_codec.py` lines 210–225 → confirm the exact lines the FODP allowlist entries govern.

**Accept when:** Lock confirmed IN_PROGRESS, 0-violation scan output captured.

---

## TC-TNP-002: PROVE the Structural Defect

**Objective:** Demonstrate concretely that V149's global gate has no sprint-scoping, and that the `raise NotImplementedError(` allowlist suppresses genuine stubs.

**Reproduction A — global scope:**
1. Create `src/python/fods/test_canary_delete_me.py` with content:
   ```python
   def canary_not_implemented():
       raise NotImplementedError("unfinished")  # genuine stub — should be caught
   ```
2. Run `python tools/review/no_stub_scan.py src/python --json`
3. **Expected (if gate were working correctly):** `canary_not_implemented` flagged as violation
4. **Actual (defective):** 0 violations — the `raise\s+NotImplementedError\(` allowlist suppresses it silently
5. Delete the canary file.

**Reproduction B — cascading block:**
1. Create `src/python/xcf/test_canary_delete_me.py` with content:
   ```python
   # TODO: implement this properly
   def fake_xcf_function():
       pass
   ```
   (No governed TODO ID, bare `TODO`)
2. Run V149 with a FODS PRODUCT_SOURCE declaration:
   ```python
   python -c "
   import sys; sys.path.insert(0, '.')
   from tools.supervisor.governance_validators_ext4 import validate_source_stubs
   decl = {'planned_work_items': [{'work_item_type': 'PRODUCT_SOURCE', 'format_id': 'fods'}]}
   import json; print(json.dumps(validate_source_stubs(decl), indent=2))
   "
   ```
3. **Expected (if baseline existed):** WARN (xcf violation is pre-existing relative to fods work)
4. **Actual:** FAIL, blocks_sprint=True — FODS sprint is blocked by XCF's stub
5. Delete the canary file.

**Record:** Both reproductions documented in `.local/evidences/dma-stub-v149-001/` with raw output.

**Accept when:** Both reproductions captured, structural flaw concretely confirmed.

---

## TC-TNP-003: CREATE `registry/stub-violations-baseline.json`

**Objective:** Create the baseline data file governing pre-existing, intentional stub violations.

**File to create:** `registry/stub-violations-baseline.json`

```json
{
  "policy": "stub-violations-baseline v1 — known/governed violations that existed before V149 went blocking. New violations (files not listed here, or violation kinds not listed) always FAIL. Do not add entries without a governing_id.",
  "known_violations": {
    "src/python/fodp/fodp_codec.py": {
      "governing_id": "TC-SC-003",
      "governing_reason": "write_fodp() deliberately raises NotImplementedError — FODP is a read-only format by design. Write path is intentionally unsupported.",
      "violation_kinds": ["forbidden_term"],
      "added_at": "2026-07-10",
      "added_by": "twinkly-nibbling-platypus"
    }
  }
}
```

**Rationale for single entry:**
The grep of `src/python/` for `raise NotImplementedError` returned exactly 1 match (`fodp_codec.py:216`). That is the only violation that needs to be baselined. Starting with a minimal baseline is intentional — it ensures the gate remains strict for all other files.

**Accept when:** File written, JSON validates, contains exactly 1 entry for `fodp_codec.py`.

---

## TC-TNP-004: ADD Baseline-Aware Classification to V149

**File to modify:** `tools/supervisor/governance_validators_ext4.py`

**Add a helper function** (before `validate_source_stubs`):

```python
def _load_stub_baseline(repo_root: "Path") -> dict:
    """Load stub-violations-baseline.json (parallel to source-structure-baseline.json)."""
    import json as _json
    bp = repo_root / "registry" / "stub-violations-baseline.json"
    if not bp.exists():
        return {"known_violations": {}}
    try:
        return _json.loads(bp.read_text(encoding="utf-8", errors="replace"))
    except Exception:
        return {"known_violations": {}}


def _violation_is_known(violation: dict, baseline: dict) -> bool:
    """Return True if violation is in the stub baseline (known/governed)."""
    known = baseline.get("known_violations", {})
    file_path = violation.get("file", "")
    # Normalize to repo-relative posix path for baseline lookup
    try:
        rel = str(Path(file_path).relative_to(Path(file_path).parts[0]))
    except Exception:
        rel = file_path
    # Normalize separator
    rel = rel.replace("\\", "/")
    # Remove leading 'src/python/' prefix variants — match what baseline stores
    for prefix in ("src/python/", "./src/python/"):
        if rel.startswith(prefix):
            break

    entry = known.get(rel) or known.get("src/python/" + rel.lstrip("/"))
    if entry is None:
        # Try matching the full absolute path's tail against baseline keys
        for key in known:
            if file_path.replace("\\", "/").endswith(key):
                entry = known[key]
                break

    if entry is None:
        return False

    allowed_kinds = entry.get("violation_kinds", [])
    return violation.get("kind") in allowed_kinds
```

**Modify `validate_source_stubs`** to classify violations:

```python
    baseline = _load_stub_baseline(repo)
    result = _stub_report([scan_root])
    violations = result.get("violations", [])

    new_violations = [v for v in violations if not _violation_is_known(v, baseline)]
    known_violations = [v for v in violations if _violation_is_known(v, baseline)]

    has_product = any(
        i.get("work_item_type") in ("PRODUCT_SOURCE", "RELEASE_GATE")
        for i in declaration.get("planned_work_items", [])
    )

    if not new_violations:
        base_msg = f"V149: No new stub violations in src/python"
        if known_violations:
            base_msg += f" ({len(known_violations)} known/governed violation(s) in baseline)"
        return {
            "validator": "validate_source_stubs",
            "result": "PASS" if not known_violations else "WARN",
            "summary": base_msg,
            "blocks_sprint": False,
        }

    return {
        "validator": "validate_source_stubs",
        "result": "FAIL" if has_product else "WARN",
        "summary": (
            f"V149: {len(new_violations)} NEW stub violation(s) not in baseline. "
            f"First: {new_violations[0]['file']}:{new_violations[0]['line']}. "
            f"Fix the stub, or add a governed baseline entry with a governing_id."
        ),
        "items": new_violations[:10],
        "known_violations_count": len(known_violations),
        "blocks_sprint": has_product and bool(new_violations),
    }
```

**Key properties of this design:**
- `new_violations` only contains violations NOT in the baseline → only these can block
- `known_violations` are reported as context but never block (always WARN/PASS)
- The error message for new violations explains how to resolve them (fix OR baseline with governing_id)
- Baseline lookup normalizes path separators and handles absolute/relative path variants

**Accept when:** V149 updated, reproduces from TC-TNP-002 now show: canary A flagged as FAIL (not suppressed), canary B shows FODS sprint blocked by XCF stub only if XCF stub is NOT in baseline (which it wouldn't be).

---

## TC-TNP-005: REMOVE `raise\s+NotImplementedError\(` from Allowlist

**File to modify:** `tools/review/no_stub_scan.py`

**Remove** this pattern from `_ALLOWLIST_PATTERNS`:
```python
    re.compile(r"raise\s+NotImplementedError\("),
```

**Verify the FODP case is now handled by baseline (not allowlist):**
After the removal, run:
```bash
python tools/review/no_stub_scan.py src/python/fodp --json
```
Expected: `fodp_codec.py:216` still appears as a violation (correctly detected by the scanner). V149 then classifies it as KNOWN via the baseline registry → WARN, not FAIL. The scanner and the baseline serve different responsibilities.

**Also check the 3 remaining TC-SC-003 patterns:**
- `write\s+stub\b.*read-only` — kept (specific phrase, low false-positive risk)
- `write\s+support\s+is\s+not\s+implemented` — kept (specific phrase)
- `NotImplementedError:\s+Always` — kept (governs line 214 of fodp_codec.py docstring)

These three are narrow enough to be genuine allowlist entries (structural false positives, not governance exceptions).

**Accept when:** Over-broad pattern removed, scanner correctly detects `fodp_codec.py:216` as a violation, V149 classifies it as KNOWN via baseline → gate passes.

---

## TC-TNP-006: FIX V105/V106 — Method-Boundary Extraction

**File to modify:** `tools/supervisor/governance_validators_ext3.py`

**Add helper** (near `_load_baseline`):

```python
def _extract_cs_method_body(content: str, sig_end: int, max_search: int = 4000) -> str:
    """Extract C# method body by tracking brace depth from sig_end.

    Returns the substring from the opening '{' to its matching '}'.
    Falls back to a 2000-char window if brace tracking fails (e.g., braces
    inside string literals, preprocessor blocks, or malformed source).

    The 4000-char search limit prevents runaway scanning on degenerate input.
    This heuristic is sufficient for the V105/V106 detection task — we are
    looking for dict accesses that appear in real method bodies, not edge cases
    in generated or adversarial C# source.
    """
    depth = 0
    i = sig_end
    start = -1
    limit = min(sig_end + max_search, len(content))
    while i < limit:
        c = content[i]
        if c == '{':
            if start == -1:
                start = i
            depth += 1
        elif c == '}':
            depth -= 1
            if depth == 0 and start != -1:
                return content[start:i + 1]
        i += 1
    # Fallback: brace tracking failed or method body too long
    # 2000-char window is generous (covers methods with comments and guard clauses)
    return content[sig_end:sig_end + 2000]
```

**Replace in V105** (`validate_getter_without_parser_source`):
```python
# Old:
snippet = content[start:start + 500]
# New:
snippet = _extract_cs_method_body(content, start)
```

**Replace in V106** (`validate_setter_without_writer_path`):
```python
# Old:
snippet = content[start:start + 600]
# New:
snippet = _extract_cs_method_body(content, start)
```

**Add regression test** to cover the GOV-WINDOW-FIX-001 scenario:
Create `tests/supervisor/test_v105_v106_method_boundary.py`:
- Synthetic C# content: public GetXxx method with 200-char TODO comment + dict access
- Confirm V105 detects the dict access (previously would have missed it at 300-char window)
- Synthetic C# content: public SetXxx method with 300-char guard clause + dict write
- Confirm V106 detects the dict write

**Tradeoffs (stated honestly):**
- Brace tracking can be fooled by `$"{x}"` string interpolations or `//`-commented braces.
  The fallback (2000 chars) handles this conservatively.
- True correctness requires a C# parser. The brace-tracking heuristic is sufficient
  for the detection task and eliminates the magic-number maintenance burden.
- The 4000-char search limit means a method body longer than 4000 chars won't be fully
  scanned. For a validator looking for dict access patterns in production methods,
  this is not a realistic concern.

**Accept when:** Helper function added, V105/V106 updated, regression test passes,
existing V105/V106 tests still pass.

---

## TC-TNP-007: VERIFY expected_count and MEMORY.md

**Steps:**
1. Find the test assertion: `grep -rn "expected_count\|165\|167" tests/supervisor/ --include="*.py"`
2. Read the actual assertion — if it's `== 165`, change to `>= 165`. If it's already `>= 165`, leave it.
   - Never change it to `== 167` (exact count creates the same maintenance burden again)
   - The floor (165) guards against accidental validator deletion; adding validators never breaks it
3. Update MEMORY.md: correct `expected_count=165` to `expected_count=167 (runner); test asserts >= 165`
4. Confirm the runner's `"expected_count": 167` comment (`# V149 added (TC-PFF-R1, 2026-07-09)`)
   is current — no change needed unless the count has changed again

**Accept when:** Test uses `>=` not `==`, MEMORY.md corrected.

---

## TC-TNP-008: CLEAN UP Orphaned Artifacts

**`.runner_system_id`:**
- The file exists in repo root, contains `s_6bd55f376669`, zero code references
- Determine: search ALL files (not just `tools/`) for `runner_system_id`:
  `grep -rn "runner_system_id" . --include="*.py" --include="*.json" --include="*.yaml"`
- If zero matches: `echo ".runner_system_id" >> .gitignore`
- If references found: read those files to understand purpose before deciding

**Continuation signal:**
- `continuation-signal.json` has `autonomous_continue: true` but `stop_reason:
  "critical_rework_blocks_continuation"` (generated 2026-07-04, 6 days stale)
- This is harmless — `check_continuation.py` uses `continuation_state`, not `stop_reason`
- TC-TNP-010 autonomous cycle will regenerate the signal. No manual fix needed.
- Document as known stale state in evidence declaration.

**Plan lock files (289 accumulated):**
- `cleanup_completed_locks(older_than_hours=72.0)` exists in `write_plan_lock.py`
- It is NOT called automatically. Verify whether it should be.
- Read `write_plan_lock.py` lines around the cleanup function to see if it's wired anywhere
- If it's only a utility (not called): add a call in the TERMINAL_CLOSED write path
- This is a housekeeping improvement, not a correctness fix

**Accept when:** `.runner_system_id` resolved, signal status documented.

---

## TC-TNP-009: VERIFY — Full Suite

**All must pass:**

1. **Stub scan (0 violations):**
   ```bash
   python tools/review/no_stub_scan.py src/python --json
   # Expected: status=CLEAN, total_violations=0
   ```

2. **V149 direct — PASS with PRODUCT_SOURCE declaration (all known violations in baseline):**
   ```python
   python -c "
   import sys; sys.path.insert(0, '.')
   from tools.supervisor.governance_validators_ext4 import validate_source_stubs
   decl = {'planned_work_items': [{'work_item_type': 'PRODUCT_SOURCE', 'format_id': 'fods'}]}
   import json; r = validate_source_stubs(decl); print(json.dumps(r, indent=2))
   assert r['result'] in ('PASS', 'WARN'), r
   assert not r['blocks_sprint'], r
   print('V149 non-blocking confirmed')
   "
   ```

3. **V149 canary — new violation FAILS:**
   - Create `src/python/fods/test_canary_delete_me.py` with `raise NotImplementedError("stub")`
   - Run V149 with PRODUCT_SOURCE declaration → confirm `FAIL` and `blocks_sprint=True`
   - Delete canary

4. **V149 canary — known violation does not block:**
   - The existing `fodp_codec.py:216` violation is in baseline
   - Run V149 with FODP PRODUCT_SOURCE → confirm non-blocking WARN
   - (No canary needed; use existing file)

5. **Governance validator suite (≥167, no new FAILs):**
   ```bash
   python tools/supervisor/governance_validator_runner.py
   ```

6. **Full test suite (≥1169, 0 failed):**
   ```bash
   .venv/Scripts/pytest tests/ -x -q --tb=short 2>&1 | tail -30
   ```

7. **Idempotency:**
   ```bash
   python tools/review/no_stub_scan.py src/python --json > /tmp/r1.json
   python tools/review/no_stub_scan.py src/python --json > /tmp/r2.json
   diff /tmp/r1.json /tmp/r2.json   # must be empty
   ```

8. **V105/V106 regression test:** New method-boundary test from TC-TNP-006 passes.

**Any failure reopens the relevant taskcard. Do not proceed to commit until all 8 pass.**

---

## TC-TNP-010: COMMIT + LIFECYCLE AUDIT + TERMINAL CLOSE

**Stage exactly these files:**
```bash
git add tools/review/no_stub_scan.py              # over-broad pattern removed
git add tools/supervisor/governance_validators_ext4.py  # V149 baseline-aware
git add tools/supervisor/governance_validators_ext3.py  # V105/V106 method-boundary
git add registry/stub-violations-baseline.json    # new baseline data file
git add .gitignore                                # .runner_system_id
git add plans/.claude/twinkly-nibbling-platypus.md
git add reports/machinery-assurance/             # assurance artifacts
# Add test files added in TC-TNP-006:
git add tests/supervisor/test_v105_v106_method_boundary.py
# Add MEMORY.md if updated in TC-TNP-007
```

**Commit message:**
```
fix(stub-gate): add V149 baseline registry + remove over-broad allowlist pattern

Root cause: V149 was a global zero-tolerance gate with no baseline mechanism.
Any violation anywhere in src/python/ blocked all PRODUCT_SOURCE sprints.
The allowlist was being used as a baseline substitute, which degraded gate
sensitivity — specifically the over-broad `raise NotImplementedError(` pattern.

Structural fix:
- registry/stub-violations-baseline.json: new baseline data file (mirrors
  source-structure-baseline.json used by V105/V106)
- governance_validators_ext4.py V149: loads baseline, classifies violations as
  NEW (FAIL if PRODUCT_SOURCE) vs KNOWN (WARN, never blocks)
- tools/review/no_stub_scan.py: removes `raise NotImplementedError(` pattern
  (too broad; FODP case now governed by baseline registry)
- FODP fodp_codec.py:216 governed by baseline entry TC-SC-003

Secondary fix (V105/V106):
- governance_validators_ext3.py: replace 500/600-char windows with
  _extract_cs_method_body() (brace-depth extraction, 2000-char fallback)
- tests/supervisor/test_v105_v106_method_boundary.py: regression test for
  GOV-WINDOW-FIX-001 class of failure

N tests pass / 0 failed / 0 new stub violations / baseline: 1 known entry

Co-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>
```

**Lifecycle audit and terminal close:**
```bash
python tools/supervisor/lifecycle_audit.py \
  --mission-id DMA-STUB-V149-001 --sprint-id TC-TNP-010

python tools/supervisor/write_plan_lock.py \
  --plan-path plans/.claude/twinkly-nibbling-platypus.md \
  --terminal --audit-gate
```

**Report:** "Plan twinkly-nibbling-platypus complete. All 10 taskcards closed."

---

## Tradeoffs and Honest Limits

**Baseline keyed by file path, not file+line:**
Pro: Stable across code reformatting.
Con: If `fodp_codec.py` acquires a SECOND genuine stub, it would be grandfathered as WARN
because the file is in the baseline. Mitigation: the baseline entry's `violation_kinds` field
limits scope (only `forbidden_term` is baselined for fodp_codec.py, not `pass_only_method`).
A new pass-only body in fodp_codec.py would still be caught.

**Brace tracking for V105/V106 can be confused by string interpolations:**
The fallback (2000 chars) is wider than the current windows and handles this conservatively.
This is a heuristic improvement, not a provably correct solution. True correctness
requires a C# parser, which is a disproportionate dependency for this validator.

**Baseline does not age violations out automatically:**
Known violations accumulate unless explicitly removed. This is the same behavior as
`source-structure-baseline.json` for V105/V106. Mitigation: baseline entries have
`added_at` and `added_by` fields for manual review. Future governance tooling could
enforce `review_by` dates, but that is out of scope for this plan.

**What this plan does NOT fix:**
- The `continuation-signal.json` stale state (harmless, resolves on next autonomous cycle)
- 289 accumulated plan lock files (no correctness impact; M7 handles evaluation)
- The structural tension in `_violation_is_known()` between absolute and relative paths
  (the helper normalizes multiple path formats, but production testing under Windows
  vs. Unix path separators should be included in the regression tests)

---

## Completion Gate Counters

| Counter | Required | Target taskcard |
|---|---|---|
| STRUCTURAL_DEFECTS_WITHOUT_BASELINE_FIX | 0 | TC-TNP-004 |
| OVER_BROAD_ALLOWLIST_PATTERNS_REMAINING | 0 | TC-TNP-005 |
| V105_V106_CHARACTER_WINDOWS_REMAINING | 0 | TC-TNP-006 |
| STUB_VIOLATIONS_SILENTLY_ALLOWED | 0 | TC-TNP-005 + TC-TNP-009 canary A |
| CROSS_FORMAT_CASCADE_BLOCKS_POSSIBLE | 0 | TC-TNP-004 (baseline isolates format work) |
| TEST_SUITE_FAILURES | 0 | TC-TNP-009 check 6 |
| MATERIAL_SECOND_RUN_CHANGES | 0 | TC-TNP-009 check 7 |
