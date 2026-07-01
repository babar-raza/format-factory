# Reports

**Document type:** Directory Orientation — Phase 0 Foundation
**Last reviewed:** 2026-05-03

---

## Purpose

This directory contains security reports and legal reports produced during the acquisition pipeline. Reports are internal documents that record the results of Gate 7 (fuzz testing), Gate 8 (security review), and any legal findings from Gate 2. Reports may be partially reclassified to `public` after redaction, but they default to `internal` and are never released without explicit human approval.

---

## Directory Structure

```
reports/
+-- _readme.md               This file
+-- security/                Security reports (created Phase 3, Gate 7/8)
|   +-- <format-id>.md       One report per format
+-- legal/                   Legal reports (created Phase 2, Gate 2)
    +-- <format-id>.md       One report per format (if needed beyond legal-notes.md)
```

All subdirectories under `reports/` are created in Phase 2+ as formats progress through the pipeline. They do not exist in Phase 0.

---

## Security Report Requirements (Gate 7/8)

Security reports (`reports/security/<format-id>.md`) must contain:

1. **Fuzz results section** (Gate 7): fuzz seed list, iteration count, all crashes with input characterization, stack traces, root cause analysis, and mitigations applied.
2. **Threat category review section** (Gate 8): for each threat category in `docs/governance/security.md`, a statement of: applicable/not applicable, mitigation implemented, or explicitly deferred with rationale.
3. **Sign-off section** (Gate 8): reviewer name, review date, and list of any residual accepted risks.

No format passes Gate 8 without a human sign-off in the security report.

---

## Legal Report Usage

Legal reports in `reports/legal/` are used when the legal analysis for a format is too extensive to fit in `acquisition-packs/<format-id>/legal-notes.md`. For most Category 1 formats using the fast-path, the legal-notes.md in the acquisition pack is sufficient. A separate legal report is created when:
- The format is Category 3 or 4 and requires detailed patent risk analysis.
- External legal counsel review results need to be documented.
- A format is being reconsidered after a previous rejection.

---

## Visibility

All reports default to `visibility: internal`. Reports may be partially reclassified to `visibility: public` after redaction (removing sensitive security details that could aid attackers, or confidential legal analysis). Reclassification requires project lead approval.

Release manifests (`release-manifest-<version>.yaml`) are also stored in `reports/` but have `visibility: public` by design — they are the public record of what is in a release.

---

## Relationship to Other Documents

- `docs/governance/security.md` — threat categories that security reports must address
- `docs/legal-and-licensing.md` — legal categories and review requirements
- `docs/gates.md` — Gate 7 (fuzz) and Gate 8 (security review) pass criteria
- `docs/release-control.md` — visibility classification and redaction policy
- `acquisition-packs/_template/legal-notes.md` — Gate 2 legal notes (usually sufficient for Category 1)
