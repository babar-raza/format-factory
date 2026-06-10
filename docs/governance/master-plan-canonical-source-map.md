# Master Plan Canonical Source Map

**Created:** 2026-06-10
**Authority:** This document defines which file owns each truth domain in format-factory.

## Truth Domain Mapping

| Truth Domain | Canonical Source | Master Plan Treatment |
|---|---|---|
| Product targets | `product-capability-matrix/poc-targets.yaml` | Pointer only |
| Format status | `registry/format-registry.yaml` | Pointer only |
| Current sprint state | `reports/supervisor/session-resume.md` | Pointer only |
| Gate approval status | `reports/supervisor/approval-gates.md` | Pointer only |
| Next sprint work | `reports/supervisor/next-sprint.md` | Pointer only |
| Governance rules | `docs/governance/*.md` | Brief canonical summary + pointer |
| Stream definitions | `docs/governance/four-stream-operating-model.md` | Brief summary + pointer |
| AI authority | `docs/governance/ai-authority-boundary.md` | Brief summary + pointer |
| Operating rules | `plans/master-plan.md` Section 1 | Canonical (master plan owns) |
| Phase model | `plans/master-plan.md` Section 14 | Canonical (master plan owns) |
| Gate model | `plans/master-plan.md` Section 13 | Canonical (master plan owns) |
| Decision register | `plans/master-plan.md` Section 16 | Canonical (master plan owns) |
| Tier model | `plans/master-plan.md` Section 4 | Canonical (master plan owns) |

## Rules

1. When the master plan says "Pointer only," the master plan must contain a one-line pointer to the canonical source, not a duplicate of the data.
2. When a claim in the master plan conflicts with its canonical source, the canonical source wins except for domains owned by the master plan itself.
3. New truth domains must be added to this map before creating new canonical sources.
4. This document is itself a governance doc under `docs/governance/` and is pointed to from the master plan.
