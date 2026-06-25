# Product Quality Confirmation Process

Sprint: FORMAT-FACTORY-PRODUCT-CODE-API-QUALITY-REVIEW-PLAN-001
Date: 2026-06-25

---

## Purpose

This document defines the process for confirming problem findings from the product quality review.
Problems catalogued in `product-quality-problem-schema.json` have three confidence levels
(VERIFIED / LIKELY / NEEDS_CONFIRMATION). This process defines how LIKELY and NEEDS_CONFIRMATION
items are escalated to VERIFIED or resolved as false positives.

---

## Confidence Level Definitions

| Level | Meaning | Action Required |
|-------|---------|-----------------|
| **VERIFIED** | Source code directly confirms the finding. File path + line reference available. | No further confirmation needed. Proceed to fix planning. |
| **LIKELY** | Strong indirect evidence. Pattern observed but not line-by-line confirmed. | Requires targeted source inspection or test run. |
| **NEEDS_CONFIRMATION** | Observation from exploration. May be partially true or context-dependent. | Requires full review: read source, run tests, compare against claim source. |

---

## Confirmation Workflow

### Step 1 — Triage the Problem

For each LIKELY or NEEDS_CONFIRMATION problem:

1. Read the `evidence` field — what file(s) need inspection?
2. Determine the confirmation method:
   - **Source inspection**: read the source file and confirm or deny the claim
   - **Test run**: execute a specific test to verify behavior
   - **Behavioral test**: write a minimal smoke test to verify claimed behavior
   - **Claim cross-reference**: compare against claim source document

### Step 2 — Execute Confirmation

Execute ONE of these confirmation methods:

| Method | When to Use | Output |
|--------|-------------|--------|
| Source read | API surface, class presence, method signature | Line reference + verdict |
| grep/search | Wildcard imports, pattern presence | Match count + file list |
| Run existing test | Behavioral claims with test coverage | Test output (pass/fail) |
| Write smoke test | Behavioral claims with no test coverage | New test file + verdict |
| Registry compare | Capability claims vs source reality | Side-by-side diff |

### Step 3 — Record Verdict

After confirmation, update the problem entry:
- If CONFIRMED: set `confidence` to `VERIFIED`; update `evidence` with specific line reference
- If PARTIALLY TRUE: set `confidence` to `VERIFIED`; update `description` to be more precise; adjust `severity` if needed
- If FALSE POSITIVE: set `status` to `WONT_FIX`; add note to `description` explaining why

### Step 4 — Priority Assignment

After confirmation, assign `fix_priority`:
- **P0**: Blocks release; critical contradiction or missing capability that misleads users
- **P1**: Blocks release or significantly degrades product quality; HIGH severity
- **P2**: Important improvement; MEDIUM severity; does not block release
- **P3**: Nice-to-have; LOW severity; deferred if sprint capacity limited

---

## Problems Requiring Confirmation

### PQ-012 — FODT .NET Table Operations

**Current confidence:** NEEDS_CONFIRMATION

**Claim:** Spec/Table/* files exist (Table.cs, TableCell.cs, TableRow.cs) but table operations may NOT be wired to FodtDocument public API.

**Confirmation method:** Source inspection
- Read `src/net/fodt/FodtDocument.cs` (or FodtDocumentAccessor.cs if split)
- Search for `AddTable`, `InsertTable`, `GetTables`, `RemoveTable`
- Read `src/net/fodt/Spec/Table/Table.cs` — confirm it is architecture_only skeleton

**Expected confirmation outcome:** CONFIRMED — Spec/Table/*.cs files contain `# GENERATED — architecture_only` markers. FodtDocument has no table-wiring methods.

**Remediation path after confirmation:**
- Option A: Implement real table operations in FodtDocument (EFFORT: L, P1)
- Option B: Delete Spec/Table/* architecture stubs to prevent false capability signal (EFFORT: XS, P2)
- Option C: Add XML doc comment marking stubs as architecture-only, not user-accessible (EFFORT: XS, P3)

---

### PQ-017 — Sprint-Named Tests

**Current confidence:** VERIFIED (LOW confidence revision needed)

**Claim:** Test files named by sprint (FodsR87ProductDeepening.cs) not by feature. ~60-80% sprint-named.

**Confirmation method:** grep/search
```bash
# Count sprint-named vs feature-named test files
ls tests/net/fods/ | grep -E "R[0-9]+" | wc -l
ls tests/net/fods/ | wc -l
```

**Expected confirmation outcome:** CONFIRMED — majority of test files follow sprint naming convention (RNN prefix).

---

### Contradiction-002 — ZST .NET Compress Capability in Capability Map

**Current confidence:** NEEDS_VERIFICATION

**Claim:** Capability map may claim ZST .NET has compress/decompress.

**Confirmation method:** Registry compare
- Read `reports/capability-layer/commercial-capability-map.json`
- Search for ZST entries; check claimed capabilities
- Compare against `src/net/zst/ZstDocument.cs` (confirmed: pure DTO, no compress)

**Expected confirmation outcome:** CLAIM_CONTRADICTED if capability map claims compress; CLAIM_UNVERIFIABLE if map is silent on ZST.

---

### Contradiction-003 — 14 Python FOSS Formats at PROOF_LEVEL_4+

**Current confidence:** NEEDS_VERIFICATION

**Claim:** MEMORY.md claims "14 Python FOSS formats all at PROOF_LEVEL_4+"

**Confirmation method:** Source inspection + cross-reference
- Identify which 14 formats are claimed (likely excludes FODP, QOI, XCF, FODG, DIF, GNUMERIC)
- For each: verify `consumer_roundtrip.py` example exists AND produces CONSUMER_PROOF: PASS output
- Check if PROOF_LEVEL_4 is defined anywhere

**Expected confirmation outcome:** LIKELY TRUE — consumer_roundtrip.py examples confirmed for most formats in MEMORY.md. FODP is confirmed read-only (no write proof). PROOF_LEVEL_4 definition is implicit.

---

### Contradiction-004 — FODT .NET Table Operations

**See PQ-012 above — same confirmation process applies.**

---

## False Positive Candidates (to be resolved quickly)

| Problem | Why Possibly False Positive | Quick Check |
|---------|----------------------------|-------------|
| PQ-016 (_shared dead abstraction) | _shared might be used by FODS or FODT | grep `_base_codec` across src/python |
| PQ-013 (NetpbmExporter scope) | Already VERIFIED LOW — just needs doc fix | No confirmation needed |
| PQ-020 (no .pyi stubs) | Could have been added post-exploration | ls src/python/fods/*.pyi |

---

## Confirmation Priority Queue (ordered)

Execute confirmations in this order:

1. **PQ-012** (FODT .NET table operations) — NEEDS_CONFIRMATION, HIGH severity, P1
2. **Contradiction-002** (ZST capability map) — NEEDS_VERIFICATION, HIGH severity
3. **Contradiction-003** (14 Python formats claim) — NEEDS_VERIFICATION, MEDIUM severity
4. **PQ-016** (_shared dead abstraction) — VERIFIED, LOW — but quick to recheck
5. **PQ-020** (no .pyi stubs) — VERIFIED, LOW — quick to recheck

---

## Confirmed Problems (no further confirmation needed)

These problems are already VERIFIED from source inspection during Phase A:

| PQ-ID | Verification Source |
|-------|---------------------|
| PQ-001 | src/python/fods/__init__.py — wildcard imports confirmed |
| PQ-002 | src/python/fods/__init__.py — dual API confirmed |
| PQ-003 | examples/python/fods/edit_save_fods.py — sys.path.insert confirmed |
| PQ-004 | src/python/fods/pyproject.toml — missing metadata confirmed |
| PQ-005 | src/net/fods/FormatFactory.Fods.csproj — README.md referenced but missing |
| PQ-006 | csproj vs FodsDocument.cs header — Gate 11 contradiction confirmed |
| PQ-007 | src/net/zst/ZstDocument.cs — pure DTO, no compress confirmed |
| PQ-008 | FodsDocument.Load() — no Stream overload confirmed |
| PQ-009 | src/python/fodp/fodp_codec.py — no write_fodp confirmed |
| PQ-010 | src/net/ndjson/NdjsonDocument.cs — List<JsonElement> confirmed |
| PQ-011 | NdjsonDocument.Load(string content) naming confirmed |
| PQ-013 | NetpbmExporter.cs — PbmToPgm/PbmToPpm only, confirmed |
| PQ-014 | No README.md at src/net/fods/ or src/python/fods/ — confirmed |
| PQ-015 | src/net/html/HtmlWriter.cs — single file, no parser/model — confirmed |
| PQ-018 | FodsDocument.GetColumnHeaders() static overload — confirmed |
| PQ-019 | pyproject.toml — no [project.scripts] — confirmed |

---

## Output Artifacts

When confirmation is complete for all NEEDS_CONFIRMATION items, update:
- `product-quality-problem-schema.json` — set confidence to VERIFIED for confirmed items
- `product-claim-vs-reality-matrix.json` — update classification for contradiction items
- `product-quality-master-plan.md` — reflect final confirmed problem count

---

## Confirmation Decision Log (to be filled during execution)

| Problem | Date | Confirmed By | Verdict | Notes |
|---------|------|--------------|---------|-------|
| PQ-012 | 2026-06-25 | Source inspection | PENDING | Read FodtDocument.cs |
| Contradiction-002 | 2026-06-25 | Registry compare | PENDING | Check capability map |
| Contradiction-003 | 2026-06-25 | Cross-reference | PENDING | Verify 14 formats list |
