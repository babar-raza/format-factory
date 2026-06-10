# Tradeoffs, Risks, and Limits
Sprint ID: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-PRODUCTION-BLOCKER-PLAN-HEALING-001

---

## Tradeoffs

### T-01 — Strong 3-format pilot vs broad 5-format shallow coverage

**Chosen:** 3 formats (ZST, Netpbm, DIF) at full lifecycle depth.
**Rejected:** 5 formats at shallow depth.
**Rationale:** Full lifecycle pilot proves the system end-to-end. Shallow pilots produce
no verified requirements, no deterministic context packs, and no regression coverage.
A production-depth 3-format pilot is more valuable than 5 shallow ingestions.

---

### T-02 — Append-only usage ledger vs mutable database

**Chosen:** Append-only JSONL with correction_of pattern.
**Rejected:** Mutable database with UPDATE/DELETE.
**Rationale:** Append-only ensures complete audit trail; no record is ever silently corrected.
Tradeoff: disk growth over time (mitigated by daily rotation + archival compression).

---

### T-03 — Deterministic pack hash vs timestamp-inclusive hash

**Chosen:** Timestamps excluded from semantic hash; only source sha256 + request_type + index_version.
**Rejected:** Including created_at in hash.
**Rationale:** Including timestamps makes every build produce a different hash, defeating
the determinism guarantee. Timestamps are recorded for audit but not for identity.

---

### T-04 — SpecNormalizer as separate step vs inline in parser

**Chosen:** SpecNormalizer as distinct pipeline stage E.
**Rejected:** Normalization inline in SpecParser.
**Rationale:** Separation enables independent versioning and testing. Parser can evolve
without changing normalization schema. Normalization can be re-run without re-parsing.

---

### T-05 — SHA-256 content addressing for SpecVault vs URL-based lookup

**Chosen:** Content addressing (sha256 = key).
**Rejected:** URL-based lookup (same URL may return different content).
**Rationale:** URLs are unstable; content may change. SHA-256 pins the exact bytes used
for requirement extraction and verification, enabling reproducible provenance chains.

---

## Risks

### R-01 — Source URL Availability

**Risk:** Spec source URLs may become unavailable (404, site down).
**Likelihood:** LOW for RFC/OASIS; MEDIUM for project docs.
**Mitigation:** SpecVault immutability — once ingested, snapshot available indefinitely.
Re-registration with new URL if source moves. Archival sources (Wayback Machine) as fallback.
**Residual risk:** Initial ingest may fail if URL unavailable at time of MWP execution.

---

### R-02 — License Ambiguity for DIF/Gnumeric

**Risk:** License classification may need review for edge cases.
**Likelihood:** LOW (both assessed as clear)
**Mitigation:**
- DIF: Public domain (Software Arts dissolved; decades old)
- Gnumeric: GPL source code; format spec docs freely usable
**Residual risk:** If license re-assessed as PROPRIETARY_RESTRICTED → quarantine raw snapshot;
document fetch-blocker; do not use in production context packs until license confirmed.

---

### R-03 — Token Budget Constraints for Complex Specs

**Risk:** ODF spec is very large (hundreds of pages). Context pack may exceed token budget.
**Likelihood:** HIGH for ODF Part 3 (schema).
**Mitigation:** Multi-resolution context model — use Section Summaries (Level 6) for overview,
Indexed Chunks (Level 4) for targeted lookup, Task Context Pack (Level 8) for specific tasks.
**Residual risk:** Some ODF sections may not fit in any reasonable token budget.

---

### R-04 — Parser Coverage for Diverse Spec Formats

**Risk:** RFC parser may not handle all section structures; man page parser may miss some content.
**Likelihood:** MEDIUM (edge cases in any parser)
**Mitigation:** Parser version recorded; re-parse on version upgrade. Category C regression tests
catch parser regressions.
**Residual risk:** First version may miss some sections. Incomplete parse still produces partial artifact.

---

### R-05 — SpecGovernanceRuntime Performance

**Risk:** Runtime validation at every handoff may add latency.
**Likelihood:** LOW (simple checks, no network I/O)
**Mitigation:** Validation is local (file system checks + JSON validation); target < 100ms.
Cache context pack freshness checks.
**Residual risk:** Cache invalidation on source change may add latency for first pack use after refresh.

---

## Known Limits

### L-01 — This Sprint is Design Only

**Limit:** This healing sprint produces design documents, pilot specifications, and the MWP
execution prompt. It does NOT implement the 13 tools or run the 47 regression tests.
Implementation happens in the next sprint (MWP execution).

### L-02 — Pilot Source Snapshots are Specifications, Not Fetches

**Limit:** The pilot deliverables describe what will be ingested and what requirements will be
extracted. Actual HTTP fetches to spec sources happen during MWP execution, not here.

### L-03 — Cross-Format Requirements Limited to Defined Pilot Formats

**Limit:** RequirementGraph cross-format edges can only be built after both formats have
verified requirements. Gnumeric and FODS/FODT cross-format edges not available until
their full lifecycle pilots complete in MWP.

### L-04 — SpecVerifier Cannot Auto-Verify All Requirements

**Limit:** INFERRED verification method requires human review for complex multi-section
requirements. Some requirements will remain at candidate_requirement (H) until manual
verification is completed.
