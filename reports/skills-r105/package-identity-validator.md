# Package Identity Validator -- Skills R105
# Train B Supervisor Analysis
# Generated: 2026-06-03

## Purpose

This document defines validation rules that a Skills R105 evidence package must satisfy
to confirm stream-state isolation. These rules prevent wrong-stream contamination from
being accepted as Skills primary evidence.

---

## Validation Rules

### Rule V1: context-pack latest_sprint must match Skills stream

**Field:** `.supervisor/context-pack.yaml` -> `latest_sprint.sprint_id`

**Requirement:** The sprint_id must contain the substring `SKILLS` or be explicitly
classified as `GLOBAL_CONTEXT` (not `SKILLS_PRIMARY`).

**Current state:** FAIL
- Actual value: `FORMAT-FACTORY-ACCELERATION-R105-PACKAGE-IDENTITY-SELF-CONTAINMENT-AND-ACCELERATION-ADVANCEMENT-001`
- Stream: Acceleration (not Skills)
- Classification: `WRONG_STREAM_PRIMARY`

**Remediation:** If the global context pack cannot be regenerated for Skills, the
package must include a Skills-specific context pack at `reports/skills-r105/context-pack.yaml`
and classify the global one as non-authoritative.

---

### Rule V2: evidence-review sprint_id must match Skills stream

**Field:** `reports/supervisor/evidence-review.md` -> Sprint ID (line 2)

**Requirement:** The Sprint ID must reference a Skills sprint or the file must be
classified as `WRONG_STREAM_PRIMARY`.

**Current state:** FAIL
- Actual value: `FORMAT-FACTORY-MAINSTREAM-R107-PRODUCT-DEPTH-AND-EVIDENCE-GOVERNANCE-CAMPAIGN-001`
- Stream: Mainstream (not Skills)
- Classification: `WRONG_STREAM_PRIMARY`

**Remediation:** Skills must produce its own evidence review at
`reports/skills-r105/evidence-review.md`. The global file should be placed under
`global-state/` in any Skills package.

---

### Rule V3: contradictions sprint_id must match Skills stream

**Field:** `reports/supervisor/contradictions.md` -> Sprint ID (line 2)

**Requirement:** The Sprint ID must reference a Skills sprint or the file must be
classified as `WRONG_STREAM_PRIMARY`.

**Current state:** FAIL
- Actual value: `FORMAT-FACTORY-MAINSTREAM-R107-PRODUCT-DEPTH-AND-EVIDENCE-GOVERNANCE-CAMPAIGN-001`
- Stream: Mainstream (not Skills)
- Classification: `WRONG_STREAM_PRIMARY`

**Remediation:** Skills must produce its own contradictions report at
`reports/skills-r105/contradictions.md`. The global file should be placed under
`global-state/` in any Skills package.

---

### Rule V4: selected-product-gaps must not be stale

**Field:** `.local/supervisor/selected-product-gaps.json` -> `sprint`

**Requirement:** The `sprint` field must reference the current or immediately prior
sprint. If stale, it must be classified as `HISTORICAL_CONTEXT`, not `SKILLS_PRIMARY`.

**Current state:** FAIL
- Actual value: `R98` (7+ sprints behind current R105)
- Classification: `STALE_PRIMARY`

**Remediation:** Either refresh the product gaps for R105 or label the R98 file as
historical context. Skills workers must not treat stale gap selections as current
authoritative state.

---

### Rule V5: next-sprint prompt must be Skills-specific

**Field:** `reports/supervisor/next-sprint.md` -> Source sprint and Stream

**Requirement:** The source sprint must reference a Skills sprint and the stream
field must be `skills`. Otherwise, classify as `WRONG_STREAM_PRIMARY`.

**Current state:** FAIL
- Source sprint: `FORMAT-FACTORY-MAINSTREAM-R107-PRODUCT-DEPTH-AND-EVIDENCE-GOVERNANCE-CAMPAIGN-001`
- Stream: `mainstream`
- Classification: `WRONG_STREAM_PRIMARY`

**Remediation:** Skills next prompt must be generated at
`reports/skills-r105/generated-next-skills-prompt.md` by the Skills pipeline.

---

### Rule V6: session-resume must reference Skills stream

**Field:** `reports/supervisor/session-resume.md` -> Last sprint

**Requirement:** The last sprint must reference a Skills sprint or be classified as
`WRONG_STREAM_PRIMARY`.

**Current state:** FAIL
- Actual value: `FORMAT-FACTORY-MAINSTREAM-R107-PRODUCT-DEPTH-AND-EVIDENCE-GOVERNANCE-CAMPAIGN-001`
- Stream: Mainstream (not Skills)
- Classification: `WRONG_STREAM_PRIMARY`

**Remediation:** Skills must produce its own session resume at
`reports/skills-r105/session-resume.md`.

---

## Validation Summary

| Rule | Status | Classification |
|------|--------|----------------|
| V1: context-pack sprint_id | FAIL | WRONG_STREAM_PRIMARY |
| V2: evidence-review sprint_id | FAIL | WRONG_STREAM_PRIMARY |
| V3: contradictions sprint_id | FAIL | WRONG_STREAM_PRIMARY |
| V4: selected-product-gaps sprint | FAIL | STALE_PRIMARY |
| V5: next-sprint stream | FAIL | WRONG_STREAM_PRIMARY |
| V6: session-resume last sprint | FAIL | WRONG_STREAM_PRIMARY |

**Overall: 0/6 rules pass.** All global state files are contaminated from the Skills
R105 perspective. The Skills stream must generate its own isolated state files to
achieve package identity self-containment.
