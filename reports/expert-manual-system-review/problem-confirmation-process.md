# Problem Confirmation Process
# Format Factory — Expert Manual System Review
# Phase 7 output — Generated: 2026-06-25

## Purpose

Define the process for confirming, classifying, and prioritizing problems found during expert review.
Every problem must go through this process before entering the problem matrix as VERIFIED.

---

## Step 1: Find Direct Evidence

**Rule:** Never enter a problem as VERIFIED without reading the actual source.

For each suspected problem:
1. Identify the specific file and line number where the problem manifests
2. Read the file directly (using the Read tool)
3. Copy the relevant code snippet into `direct_evidence` field
4. Identify secondary evidence (test files, poc-targets claims, SAL facts)

**Evidence quality tiers:**
- TIER-1: Source code read directly in this review session
- TIER-2: Test file read and test names inspected
- TIER-3: Authority registry claim (poc-targets, parity-matrix)
- TIER-4: Prior sprint evidence bundle

Only TIER-1 evidence supports VERIFIED confidence.

---

## Step 2: Classify System Gap vs. Product Gap

For each confirmed problem, answer:

**Q1: Is there a gap in the gap ledger for this problem?**
- Yes → Check if gap has been worked or is still open
- No → This is a gap in the gap detection system (meta-gap)

**Q2: Is there a governance validator that would catch this recurrence?**
- Yes → Which one? Is it wired?
- No → Add "add validator" to the product fix plan

**Q3: Is there a spec fact in the SAL cache for the affected format?**
- Yes → Can we trace the defect to a spec requirement?
- No → CHAIN_BROKEN_AT_SAL is a contributing system gap

**Q4: Is there a skill that should govern this type of fix?**
- Yes → Skill must be invoked in the fix sprint
- No → Add skill to skill registry before executing fix

---

## Step 3: Determine System Healing Sequence

Before any product fix can be executed through the governed system, the relevant system components must work:

```
System healing order:
1. Gap ledger taxonomy repair (enables gap routing)
2. SAL chain extension (enables spec-parity grading for broken formats)
3. LLM grader resolution (enables evidence quality verification)
4. Then: product fixes through healed system paths
```

For each product problem, identify:
- Which system component's failure allowed this product gap to exist?
- Does the gap ledger track this problem with meaningful category?
- Can the healed system re-run and detect/fix this product gap?

---

## Step 4: Priority Scoring

Calculate priority score = `Severity × Confidence × Impact`:

| Factor | Weight |
|--------|--------|
| CRITICAL severity | 4 |
| HIGH severity | 3 |
| MEDIUM severity | 2 |
| LOW severity | 1 |
| VERIFIED confidence | 1.0 |
| LIKELY confidence | 0.7 |
| NEEDS_CONFIRMATION | 0.4 |
| Blocks commercial publication | +2 |
| Blocks FOSS release | +1 |
| Has system root cause (multiply) | 1.5x |

---

## Step 5: Problem Resolution

A problem is closed when ALL of:
1. Source fix implemented (in src/ through governed sprint)
2. Test verifies the fix (new test or updated test)
3. Gap ledger entry marked `closed` or `test_verified`
4. Governance validator added to prevent recurrence (if applicable)
5. Spec fact referenced (if SAL chain is intact for the format)

---

## Known Problems from Pre-Identification (Status as of 2026-06-25)

| PROB ID | Category | Severity | Confidence | Status | Correction |
|---------|---------|---------|-----------|--------|-----------|
| PROB-001 | DOTNET_COMMERCIAL | CRITICAL | VERIFIED | OPEN | ZST .NET probe-only; NO decompression |
| PROB-002 | DOTNET_COMMERCIAL | HIGH | VERIFIED | OPEN | FODS PDF Latin-1 only |
| PROB-003 | DOTNET_COMMERCIAL | HIGH | VERIFIED | OPEN | FODT no table traversal in public model |
| PROB-004 | DOTNET_COMMERCIAL | HIGH | LIKELY | OPEN | HTML/Markdown/TXT counted as format products |
| PROB-005 | DOTNET_COMMERCIAL | MEDIUM | VERIFIED | OPEN | CSV .NET no edit API |
| PROB-006 | PYTHON_FOSS | MEDIUM | VERIFIED | OPEN | FODP no write_fodp (NARROWED from HIGH: has exports) |
| PROB-007 | PYTHON_FOSS | LOW | CORRECTED | CLOSED_CORRECTED | ODS Python has write_ods() — was misassessed |
| PROB-008 | PYTHON_FOSS | LOW | CORRECTED | CLOSED_CORRECTED | PBM/PGM/PPM have write_* — was misassessed |
| PROB-009 | SYSTEM_GAP | CRITICAL | VERIFIED | OPEN | Gap ledger: 1131/1132 unknown category |
| PROB-010 | SYSTEM_GAP | HIGH | VERIFIED | OPEN | SAL chain broken for 10 formats |
| PROB-011 | SYSTEM_GAP | HIGH | VERIFIED | OPEN | LLM grader dependency; silent degradation |
| PROB-012 | SYSTEM_GAP | MEDIUM | VERIFIED | OPEN | autonomous_cycle and governance_validators violate LOC caps they enforce |
| PROB-013 | EVIDENCE | HIGH | LIKELY | OPEN | FodsOdsExporter: "PROTOTYPE" in source vs PASS in poc-targets |
| PROB-014 | PYTHON_FOSS | MEDIUM | VERIFIED | OPEN | Analytics masquerade (GAP-PROD-INV-MASQ-001) — deferred rename |
| PROB-015 | SKILLS | MEDIUM | VERIFIED | OPEN | Several skills have empty implementation_paths |
| PROB-016 | DOTNET_COMMERCIAL | MEDIUM | NEEDS_CONFIRMATION | OPEN | FODS ODS exporter — PROTOTYPE comment vs PASS (same as PROB-013) |
| PROB-017 | SYSTEM_GAP | MEDIUM | VERIFIED | OPEN | Skill transcript: ci_transcript_verification backlog |
| PROB-018 | PYTHON_FOSS | LOW | VERIFIED | OPEN | ZST Python: 1549 LOC mostly analytics; core thin |

*Note: PROB-007 and PROB-008 were CORRECTED after reading actual source files in this sprint.*
*PROB-013 and PROB-016 describe the same FODS ODS exporter issue from different angles.*
