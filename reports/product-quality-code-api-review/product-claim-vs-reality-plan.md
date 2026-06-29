# Product Claim vs Reality Review Plan

Sprint: FORMAT-FACTORY-PRODUCT-CODE-API-QUALITY-REVIEW-PLAN-001
Date: 2026-06-25

---

## Purpose

Autonomous development systems can drift between what they claim and what is actually implemented. This plan identifies specific claim sources, cross-references them against source-verified reality, and flags contradictions.

---

## Claim Sources to Cross-Reference

| Source | Location | Claim Type |
|--------|----------|------------|
| `.csproj` PackageDescription | `src/net/fods/FormatFactory.Fods.csproj` | Gate status |
| Source header comments | `src/net/fods/FodsDocument.cs` (line 1-3) | Gate status |
| `capability_summary.json` | `reports/capability-layer/capability_summary.json` | Feature claims |
| `commercial-capability-map.json` | `reports/capability-layer/commercial-capability-map.json` | Commercial features |
| `foss-reduced-capability-map.json` | `reports/capability-layer/foss-reduced-capability-map.json` | FOSS features |
| `poc-targets.yaml` | `product-capability-matrix/poc-targets.yaml` | VERIFIED status per function |
| `parity-matrix.yaml` | `registry/parity-matrix.yaml` | Spec parity status |
| `gap-ledger.json` | `reports/capability-layer/gap-ledger.json` | Known gaps |
| `work-item-grades.json` | `reports/supervisor/work-item-grades.json` | Sprint completion claims |
| `latest-review.md` | `reports/supervisor/latest-review.md` | Review verdicts |
| `master-plan.md` | `plans/master-plan.md` | Strategic claims |

---

## Known Contradictions (Pre-Identified from Source Inspection)

### CONTRADICTION-001: Gate 11 Status (CRITICAL)

**Claim source:** `src/net/fods/FormatFactory.Fods.csproj`
```xml
<PackageDescription>Gate 11 approved 2026-06-05</PackageDescription>
```

**Source reality:** `src/net/fods/FodsDocument.cs` (line 1-3)
```csharp
// FormatFactory.Fods -- OpenDocument Flat Spreadsheet
// Gate 11 status: commercial_readiness_in_progress (NOT approved)
```

**Assessment:** CLAIM_CONTRADICTED — the source header explicitly says "NOT approved" while the NuGet package description claims approval.

**Also confirmed from plan:** `plans/strategic/spec-to-feature-radical-correction-plan.md` states:
> "Gate 11: NOT approved. Babar Raza is the only approver. Criteria: C1-C20 (.NET), P1-P11 (Python)."

**Severity:** HIGH — NuGet consumers reading the package description would be misled.
**PQ ID:** PQ-006

---

### CONTRADICTION-002: ZST .NET Capability

**Claim risk:** `reports/capability-layer/` files may claim ZST is a complete compression product
**Source reality:** `src/net/zst/ZstDocument.cs` is a pure read-only DTO. No `ZstWriter.cs` exists.
**Assessment:** NEEDS_VERIFICATION against capability-layer reports
**Severity:** HIGH
**PQ ID:** PQ-007

---

### CONTRADICTION-003: Python FOSS Formats at PROOF_LEVEL_4+

**Claim source:** `reports/supervisor/project-memory.md` (from MEMORY.md):
> "Product Deepening Mission COMPLETE (2026-06-25): 14 Python FOSS formats all at PROOF_LEVEL_4+."

**Source reality:**
- FODP Python: READ-ONLY, no write capability → NOT truly at PROOF_LEVEL_4+ if that level requires write
- QOI Python: No examples, minimal model
- XCF Python: No write/export, no examples

**Assessment:** CLAIM_OVERSTATED — the claim of PROOF_LEVEL_4+ needs definition verification. If PROOF_LEVEL_4 only requires roundtrip of what the format can do (e.g., FODP roundtrip = inspect + inspect again), then the claim may be technically valid but misleading.
**Severity:** MEDIUM

---

### CONTRADICTION-004: FODT .NET Table Operations

**Claim risk:** FODT may have claimed table operations as complete based on `Spec/Table/` stubs existing
**Source reality:** `Spec/Table/Table.cs`, `Spec/Table/TableCell.cs`, `Spec/Table/TableRow.cs` in FODT are architecture-only stubs (empty)
**Assessment:** NEEDS_VERIFICATION — whether table edit operations are actually wired to `FodtDocument`
**Severity:** MEDIUM
**PQ ID:** PQ-012

---

### CONTRADICTION-005: NetpbmExporter Scope

**Claim risk:** "Export" capability claimed for NetPBM may suggest external format export
**Source reality:** `src/net/netpbm/NetpbmExporter.cs` confirmed to be within-family only (PBM→PGM, PBM→PPM)
**Assessment:** NOT_CONTRADICTED but potentially OVERCLAIMED — "export" is misleading if external format export is implied
**Severity:** LOW
**PQ ID:** PQ-013

---

### CONTRADICTION-006: Python FODS 14 vs All 20

**Claim source:** "14 Python FOSS formats all at PROOF_LEVEL_4+"
**Source reality:** There are 20 Python packages total. The claim covers 14.
**Implication:** 6 formats (QOI, XCF, FODG, FODP, and 2 others?) are excluded. Why? Are they acknowledged as weaker?
**Assessment:** NEEDS_VERIFICATION — which 14 were included, which 6 were excluded?

---

## Claim Verification Method

For each claim:

1. **Locate claim source** — which file, which line?
2. **Identify claim subject** — what specifically is claimed?
3. **Find source truth** — what does the actual source code show?
4. **Compare** — does the source confirm, contradict, or partially match the claim?
5. **Classify:**
   - `CLAIM_VERIFIED` — source confirms the claim
   - `CLAIM_CONTRADICTED` — source directly contradicts
   - `CLAIM_OVERSTATED` — claim is partially true but inflated
   - `CLAIM_UNDERSTATED` — source is better than claimed (rare)
   - `CLAIM_UNVERIFIABLE` — insufficient source evidence to judge
   - `NEEDS_VERIFICATION` — requires deeper inspection to resolve

---

## Claim vs Reality Scoring

| Score | Meaning |
|-------|---------|
| 5 | All claims verified against source |
| 4 | Claims accurate with minor gaps |
| 3 | Claims mostly accurate; a few overstatements |
| 2 | Significant overclaiming; some verifiable false claims |
| 1 | Major contradictions; claims systematically inflated |
| 0 | Claims bear no relationship to actual implementation |

**Estimated overall project score:** 3 (mostly accurate, known contradictions)
- Known true: Gate 11 contradiction in csproj (PQ-006)
- Known true: PROOF_LEVEL_4 claim for 14 Python formats needs definition review
- Known false: FODT table operations claim if Spec/Table/* are architecture stubs

---

## Files Produced

- `product-claim-vs-reality-plan.md` (this file)
- `product-claim-vs-reality-matrix.json` — specific claim/reality pairs
