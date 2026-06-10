# Contradiction and Stale-Claim Audit

**Sprint ID:** FORMAT-FACTORY-MASTER-PLAN-GOVERNANCE-REVIEW-HEALING-PLAN-001
**Date:** 2026-06-10
**Source:** plans/master-plan.md (2229 lines), poc-targets.yaml, state/current-state.md, session-resume.md, docs/governance/*

## Audit by Category

### Product Targets
| Claim ID | Issue | Status |
|----------|-------|--------|
| CLAIM-005 | WIP limit "1 format" for product stages contradicts 11 active targets | contradictory |
| CLAIM-009 | "Active formats: fods, fodt" ignores 9 other targets | stale |
| CLAIM-024 | commercial_product_ready: false | accurate |

### Gate 11 Status
| Claim ID | Issue | Status |
|----------|-------|--------|
| CLAIM-010 | "Gate 11 NOT approved" in header/Section 6 contradicts poc-targets.yaml | contradictory |
| CLAIM-019 | state/current-state.md "Gate 11 approved: False" contradicts poc-targets.yaml | contradictory |

### Commercial vs FOSS
| Claim ID | Issue | Status |
|----------|-------|--------|
| CLAIM-003 | last_completed_sprint frozen at 2026-05-13 era | stale |
| CLAIM-025 | Header Current phase frozen at R78 description | stale |

### AI Role / Authority
| Claim ID | Issue | Status |
|----------|-------|--------|
| CLAIM-017 | Section 39 AI/LLM Platform Layer conflicts with ai-authority-boundary.md | historical-only |
| CLAIM-007 | Codex as secondary executor — unsupported | unsupported |

### Evidence Model
| Claim ID | Issue | Status |
|----------|-------|--------|
| CLAIM-004 | "bundle must be uploaded by human" superseded by declaration-driven pipeline | stale |
| CLAIM-018 | Section 7 rules as primary evidence model | stale |

### Commands / Skills
| Claim ID | Issue | Status |
|----------|-------|--------|
| CLAIM-008 | "No functional commands exist" — 25 commands exist | stale (FALSE) |

### Autonomous Continuation
| Claim ID | Issue | Status |
|----------|-------|--------|
| CLAIM-023 | "Netpbm must be retained; SVG must NOT replace it" | accurate |

### Old Sprints / Closed Gates
| Claim ID | Issue | Status |
|----------|-------|--------|
| CLAIM-011 | TC-0001 through TC-0053 status table | stale |
| CLAIM-012 | Run Commit Ledger run001-run048 | historical-only |
| CLAIM-013 | G-HEAL-001..036+ healing gap register | historical-only |
| CLAIM-014 | Phase 0 Review Checklist | historical-only |
| CLAIM-021 | Run history table run001-run042 | stale |
| CLAIM-022 | Phase 0 Required Files (45-file list) | historical-only |

### Unauthorized Backlog
| Claim ID | Issue | Status |
|----------|-------|--------|
| CLAIM-015 | S-F2F Secondary Sprint Roadmap | historical-only |
| CLAIM-016 | Format Understanding Layer backlog | historical-only |
| CLAIM-017 | AI/LLM Platform Layer backlog | historical-only |
| CLAIM-020 | Conway R1-R9 references | stale |

### Version / Metadata
| Claim ID | Issue | Status |
|----------|-------|--------|
| CLAIM-001 | Header 2.64 vs footer 2.70 | contradictory |
| CLAIM-002 | last_updated 2026-05-31 but content to 2026-06-04 | stale |
| CLAIM-006 | "No section may be split out" contradicts 29 governance files | contradictory |

## Summary

| Status | Count |
|--------|-------|
| contradictory | 5 |
| stale | 9 |
| historical-only | 7 |
| unsupported | 1 |
| accurate | 2 |
| **Total claims audited** | **25** |

All contradictory and stale claims must be resolved in the healing execution sprint.
Historical-only claims must be archived with pointers.
Accurate claims are confirmed and will be preserved.
