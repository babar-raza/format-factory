# Skills-Acceleration Schema Compatibility
Sprint: FORMAT-FACTORY-SKILLS-PRODUCT-BREADTH-HANDOFF-FINALIZATION-001

---

## Purpose

Maps Skills packet fields to Acceleration packet schema so Acceleration can consume Skills
handoffs without confusion. Both schemas converge on the same product evidence, but use
different field names and authority semantics.

---

## Authority Difference

| Aspect | Skills Packet | Acceleration Packet |
|--------|--------------|---------------------|
| authority_state | omitted (governed by enforcement_tier) | always "ai_draft" |
| non_authoritative | omitted (packets are authoritative) | always true |
| requires_validation | implied by acceptance_criteria | always true |
| source of truth | hardening sprint + validate_skill_transcript.py | ai_draft advisory |

**Rule:** Skills packets supersede Acceleration ai_draft outputs. When both exist for the same
capability, use Skills packet allowed_files and acceptance_criteria.

---

## Field Compatibility

| Skills Field | Acceleration Field | Compatible? | Notes |
|-----------|--------------------|-------------|-------|
| allowed_files | allowed_files | YES | Same semantics |
| forbidden_files | forbidden_files | YES — more restrictive in Skills | Skills adds governance paths |
| gap_id | selected_gap | PARTIAL | Skills uses GAP-* prefix; Accel uses capability path |
| capability | capability_path | YES | Same capability path format |
| acceptance_criteria | downgrade_rules | DIFFERENT | Skills = pass/fail; Accel = downgrade conditions |
| enforcement_tier | governance_rules | COMPATIBLE | Skills tier maps to Accel governance_rules |
| proposed_capability_delta | capability_matrix_update_hint | COMPATIBLE | Both use "ai_draft until tested" semantics |
| mode (live/dry-run) | not present | Skills-only | Accel packets do not track mode |
| rollback_note | not present | Skills-only | Accel has no rollback |
| handoff_id | not present | Skills-only | Accel has no handoff ID |

---

## Consumption Guidance for Acceleration

When consuming a Skills full packet:
1. Use Skills `allowed_files` (more specific than Acceleration `allowed_files`)
2. Use Skills `acceptance_criteria` (replaces Acceleration `downgrade_rules`)
3. Skills `enforcement_tier: FAIL_CLOSED` maps to Acceleration `governance_rules[0]` (no capability matrix update without test evidence)
4. Skills `proposed_capability_delta` provides the hint for what Acceleration's `capability_matrix_update_hint.authority_state` should eventually become
5. Ignore Acceleration `authority_state: ai_draft` once Skills packet is available
