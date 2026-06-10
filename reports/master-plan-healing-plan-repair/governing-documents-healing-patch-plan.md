# Governing Documents Healing Patch Plan

**Sprint ID:** FORMAT-FACTORY-MASTER-PLAN-GOVERNANCE-REVIEW-HEALING-PLAN-001
**Date:** 2026-06-10

## Existing Governance Docs — Required Edits

No existing governance documents require editing for the master plan healing sprint. All 29 are CURRENT and consistent with the product-first model.

The master plan is the stale component, not the governance layer.

## New Governance Documents to Create (in execution)

### 1. docs/governance/master-plan-canonical-source-map.md

**Purpose:** Defines which document owns each truth domain, preventing future drift.

**Required content:**
| Truth Domain | Canonical Source | Master Plan Treatment |
|-------------|-----------------|----------------------|
| Product targets | product-capability-matrix/poc-targets.yaml | Pointer only |
| Format status | registry/format-registry.yaml | Pointer only |
| Current sprint state | reports/supervisor/session-resume.md | Pointer only |
| Gate approval | reports/supervisor/approval-gates.md | Pointer only |
| Next sprint work | reports/supervisor/next-sprint.md | Pointer only |
| Governance rules | docs/governance/*.md | Brief canonical summary + pointer |
| Stream definitions | docs/governance/four-stream-operating-model.md | Brief summary + pointer |
| AI authority | docs/governance/ai-authority-boundary.md | Brief summary + pointer |
| Operating rules | plans/master-plan.md Section 1 | Canonical (master plan owns) |
| Phase model | plans/master-plan.md Section 14 | Canonical (master plan owns) |
| Gate model | plans/master-plan.md Section 13 | Canonical (master plan owns) |
| Decision register | plans/master-plan.md Section 16 | Canonical (master plan owns) |
| Tier model | plans/master-plan.md Section 4 | Canonical (master plan owns) |

**Required before master plan execution:** YES — execution agent needs this map to correctly place pointers.
**Becomes canonical:** YES
**Validation command:** `grep -c "Canonical Source" docs/governance/master-plan-canonical-source-map.md` (should be >= 1)

### 2. docs/governance/master-plan-sync-policy.md

**Purpose:** Prevents append-only drift; defines when and how master plan updates happen.

**Required content:**
- **No-append-only rule:** Every update must review and condense existing content, not just append
- **Freshness triggers:** Phase change, gate transition, major decision, architecture amendment
- **Line budget:** 400-700 lines; exceeding 700 triggers mandatory condensation sprint
- **Stale-claim lint:** Run stale-claim lint (10 grep patterns) at every healing sprint
- **Source-of-truth rule:** Any claim that duplicates a canonical source must be a pointer, not a copy
- **Split-out authorization:** Governance docs in docs/governance/ are authorized split-outs with mandatory canonical summary in master plan
- **Archive rule:** Historical content must be archived to docs/history/, never simply deleted
- **Version rule:** Header and footer versions must always match

**Required before master plan execution:** YES — execution agent needs sync policy to apply during edit.
**Becomes canonical:** YES
**Validation command:** `grep -c "No-append-only" docs/governance/master-plan-sync-policy.md` (should be >= 1)

## Update to Master Plan §5 (in execution)

Current rule 6: "No section may be split out into a separate file in a way that removes it from this document."

Proposed replacement: "Governance documents in docs/governance/ are authorized split-outs. The master plan maintains a canonical summary with a pointer to the governance doc. See docs/governance/master-plan-canonical-source-map.md for the full authority map."

## Execution Order

1. Create docs/governance/master-plan-canonical-source-map.md (before master plan edit)
2. Create docs/governance/master-plan-sync-policy.md (before master plan edit)
3. Edit master plan Section 5 rule 6 (during master plan edit)
4. Verify pointers in healed master plan reference correct governance docs
