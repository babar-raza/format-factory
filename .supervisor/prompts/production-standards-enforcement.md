---
espanso_provenance:
  source_trigger: ":ffmgh:"
  source_block: 80
  source_line_range: [92463, 92793]
  gap_id: GAP-ESP-006
  extraction_date: "2026-07-03"
  capability_id: null
  note: "Execution driver for production-library-standard-v2.md. Not a standalone capability."
prompt_id: ESP-PROMPT-8
title: "Production Standards Enforcement Sprint"
version: "1.0"
status: ACTIVE
mutating: true
context_profile: full
---

# Master Governance and Production Standards Enforcement Sprint

## Purpose

Heal the project machinery and governance so that ALL source code under `src/` is forced
to be production-grade library code for both .NET and Python.

**This is a governance-first sprint.** Existing product code is healed AFTER the machinery
proves it can detect, prevent, and correct the same class of problems repeatedly.

Do not:
- Blindly rewrite `src/`
- Perform ad-hoc manual refactors without governed machinery
- Treat passing tests as sufficient if architecture or production readiness is weak
- Heal product code before the governance machinery is proven

## Short-Context View

1. Build a comprehensive code quality checklist for `src/` (both .NET and Python)
2. Detect which governance machinery (validators, schemas, LOC caps) already enforces each rule
3. For each rule NOT enforced: create a validator, schema gate, or test that enforces it
4. Prove the governance machinery works (catches real violations)
5. Only then: use the proven machinery to identify and fix product code violations

---

## Phase 1: Code Quality Checklist

Build the checklist from `docs/code-quality/production-library-standard-v2.md`.
At minimum cover:

**Repository and Library Structure**
- [ ] Clear separation: product libraries / shared libraries / CLI / tests / fixtures / generated artifacts
- [ ] No production logic in scripts, tests, prompts, or orchestration files
- [ ] Stable public API surfaces
- [ ] Internal implementation separated from public API
- [ ] No monolithic God files, God classes, or catch-all modules
- [ ] Folder structure aligned with product/domain/spec hierarchy
- [ ] Consistent packaging layout for .NET and Python

**.NET Production Library Standards**
- [ ] Proper solution/project organization
- [ ] Clear namespaces aligned with domain concepts
- [ ] Classes mapped to spec QNames (one class per spec concept)
- [ ] One responsibility per class
- [ ] Public/internal visibility boundaries correct
- [ ] Strong typing, no untyped catch-all parameters
- [ ] Meaningful exceptions, not raw Exception
- [ ] No monolithic static utility class as product architecture

**Python Production Library Standards**
- [ ] Proper package/module structure (`__init__.py`, `__all__`, `spec_qname: ClassVar[str]`)
- [ ] Typed APIs (type hints on public functions)
- [ ] Domain objects separated from parsing, serialization, and export logic
- [ ] No monolithic module with all behavior
- [ ] Explicit `__all__` exports
- [ ] No hidden global mutable state
- [ ] No script-style code in library modules (no `if __name__ == "__main__"` in library files)
- [ ] LOC per file ≤ 800, functions per file ≤ 60 (per source-structure-baseline.json)

**Cross-Language Architecture**
- [ ] .NET and Python products follow equivalent conceptual architecture
- [ ] Same domain/spec concepts named consistently across languages
- [ ] Python is not a disconnected prototype when .NET is a production library

## Phase 2: Governance Gap Analysis

For each checklist item:
```
→ Identify the existing validator, schema gate, or test that enforces it
→ If covered: note which validator/gate (e.g., V35 LOC cap, V41 analytics gate)
→ If NOT covered: classify as GOVERNANCE_GAP
```

## Phase 3: Governance Repair

For each GOVERNANCE_GAP:
```
→ Create a validator, schema rule, or test that would catch violations
→ Add it to the governance_validators.py suite (or equivalent)
→ Register it in the appropriate schema
→ Run it against the current codebase to confirm it detects violations
```

## Phase 4: Product Code Audit (only after Phase 3)

```
→ Run all governance validators against src/
→ Collect violations (files, rules violated, severity)
→ Prioritize: BLOCKING > HIGH > MEDIUM > LOW
→ Fix violations in order using the proven governance machinery
```

## Phase 5: Verification

```
→ All governance validators pass
→ LOC/function caps respected across src/
→ No monolithic files (> 800 LOC or > 60 functions) without baseline_loc_cap exceptions
→ All Python packages have spec_qname ClassVar fields
→ All .NET classes mapped to spec QNames
→ Product tests pass
```

## Evidence Requirements
- Checklist with each item: COVERED | NOT_COVERED | GOVERNANCE_GAP
- List of new validators/gates created
- Before/after LOC summary for files modified
- Test pass count before and after

## Completion Gate
- Phase 1 checklist complete
- All GOVERNANCE_GAPsaddressed (validator or gate created)
- All validators pass against current src/
- No new BLOCKING violations introduced
