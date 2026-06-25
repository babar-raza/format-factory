# Initial Risk Register
# Format Factory — Expert Manual System Review
# Phase 10 output — Generated: 2026-06-25

## Purpose

Track risks associated with each proposed product fix and system change.
Every fix has a risk level, failure mode, and rollback strategy.

---

## Risk Categories

| Category | Meaning |
|---------|---------|
| REGRESSION | Fix may break existing tests or behavior |
| SCOPE_CREEP | Fix may grow beyond original intent |
| DEPENDENCY | Fix requires adding external packages |
| CROSS_PRODUCT | Fix affects multiple products |
| SYSTEM_INTEGRITY | Fix may corrupt authority registries or state |
| ESTIMATION | Fix complexity was underestimated |

---

## Risk Register

### R-001: Gap Ledger Taxonomy Repair (PROB-009)

| Field | Value |
|-------|-------|
| Risk Level | MEDIUM |
| Category | SYSTEM_INTEGRITY |
| Failure Mode | Category inference assigns wrong categories to gaps; routing sends gaps to wrong lanes |
| Probability | MEDIUM |
| Impact | HIGH — wrong categories mislead all future sprints |
| Mitigation | Run category inference on 10 known gaps first; verify categories are correct before bulk update |
| Rollback | Restore gap-ledger.json from git; no source changes involved |

---

### R-002: ZST .NET Decompression (PROB-001)

| Field | Value |
|-------|-------|
| Risk Level | HIGH |
| Category | DEPENDENCY, REGRESSION |
| Failure Mode | Adding ZST decompression requires a .NET NuGet package (ZstdNet or ZstdSharp); package adds size to NuGet artifact |
| Probability | LOW-MEDIUM |
| Impact | MEDIUM — extra dependency may conflict with consumer package graphs |
| Mitigation | Use System.IO.Compression if native .NET ZST support exists; else evaluate ZstdNet as light dependency |
| Rollback | Remove ZstDecompressor.cs; revert ZstDocument; no other products affected |

---

### R-003: FODS PDF Unicode Fix (PROB-002)

| Field | Value |
|-------|-------|
| Risk Level | HIGH |
| Category | SCOPE_CREEP, DEPENDENCY |
| Failure Mode | Proper Unicode PDF requires font embedding; font embedding is a large scope change to FodsPdfExporter |
| Probability | HIGH |
| Impact | MEDIUM — existing PDF output still works; new Unicode path is additive |
| Mitigation | Option A: Add TrueType font embedding to existing pure-.NET PDF writer (large scope). Option B: Add optional iText/PdfSharp dependency. Option C: Document as known limitation and scope commercial release to Latin-1 content only |
| Rollback | Option C rollback: update format-registry.yaml to document scope limitation |

---

### R-004: FODT Table Traversal (PROB-003)

| Field | Value |
|-------|-------|
| Risk Level | MEDIUM |
| Category | REGRESSION, SCOPE_CREEP |
| Failure Mode | Adding FodtTable to public API changes the shape of FodtBody; existing callers of FodtBody.Paragraphs are unchanged but new API may surprise users |
| Probability | LOW |
| Impact | LOW — FodtBody.Paragraphs still works; FodtBody.Tables is additive |
| Mitigation | Add Tables property as additive; do not change Paragraphs behavior |
| Rollback | Remove FodtBody.Tables property and FodtTable class |

---

### R-005: SAL Chain Extension (PROB-010)

| Field | Value |
|-------|-------|
| Risk Level | HIGH |
| Category | SCOPE_CREEP, ESTIMATION |
| Failure Mode | Building SAL extractor for CSV, TOML, SYLK requires parsing spec documents; spec documents may not be accessible in a structured form |
| Probability | MEDIUM-HIGH |
| Impact | MEDIUM — SAL chain broken state is pre-existing; extending it is improvement, not regression |
| Mitigation | Start with CSV (RFC 4180 is well-structured); then TOML spec; then SYLK |
| Rollback | No rollback needed; SAL extension is additive |

---

### R-006: FodsOdsExporter PASS Claim (PROB-013)

| Field | Value |
|-------|-------|
| Risk Level | LOW |
| Category | SYSTEM_INTEGRITY |
| Failure Mode | Downgrading poc-targets.yaml from PASS to PARTIAL may affect Gate 11 assessment |
| Probability | MEDIUM |
| Impact | MEDIUM — FODS Gate 11 approval was conditional; changing PASS to PARTIAL is honest but may delay commercial publication |
| Mitigation | Fix the ODS exporter first; then update poc-targets to PASS with evidence |
| Rollback | Revert poc-targets.yaml change |

---

### R-007: HTML/Markdown/TXT Reclassification (PROB-004)

| Field | Value |
|-------|-------|
| Risk Level | LOW |
| Category | SYSTEM_INTEGRITY |
| Failure Mode | Changing classification in format-registry.yaml may affect format count claims in documentation |
| Probability | LOW |
| Impact | LOW — reclassification is metadata only; products still exist and function |
| Mitigation | Update format-registry.yaml; update documentation to reflect "10 format products + 3 target writer utilities" |
| Rollback | Revert format-registry.yaml classification entries |

---

## Risk Summary

| Problem | Risk Level | Key Concern |
|---------|-----------|------------|
| PROB-001 (ZST decomp) | HIGH | NuGet dependency |
| PROB-002 (PDF Unicode) | HIGH | Scope creep; large change |
| PROB-003 (FODT tables) | MEDIUM | API surface change |
| PROB-004 (count inflation) | LOW | Metadata only |
| PROB-005 (CSV edit API) | LOW | Additive methods |
| PROB-006 (FODP no write) | MEDIUM | New feature |
| PROB-009 (gap taxonomy) | MEDIUM | Wrong categories may mislead |
| PROB-010 (SAL chain) | HIGH | Spec parsing complexity |
| PROB-013 (ODS PASS claim) | LOW | Gate assessment impact |

## Pre-Fix Checklist

Before executing any fix:
1. Gap ledger entry exists with correct category
2. Governance validator in place to prevent recurrence
3. Test strategy defined
4. Rollback strategy documented here
5. Sprint ID and evidence template prepared
