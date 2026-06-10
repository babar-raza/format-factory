# Acceleration TC-EXT-007 Fix
# Taskcard: TC2 — Make Acceleration TC-EXT-007 Mandatory
# Sprint: FORMAT-FACTORY-CROSS-PLAN-HARMONIZATION-BEFORE-EXECUTION-001
# Date: 2026-06-04

## Problem

TC-EXT-007 ("Validate no external tool activation occurred") had `Status: PROPOSED` in the
Acceleration plan (`bubbly-wiggling-pizza.md`). A PROPOSED status means the task may be
deferred or skipped without blocking Gate 7 or sprint closeout.

This was a readiness blocker because:
1. No external tool activation proof could be required if the task is optional.
2. `external-tool-authority-validation.json` could remain in PENDING state at closeout.
3. The authority boundary model (Ruflo/Superpowers/GhidraMCP all non-authoritative) would be
   unverified.

## Changes Applied to Acceleration Plan

File: `C:\Users\prora\.claude\plans\bubbly-wiggling-pizza.md`

### Change 1: TC-EXT-007 body status
- **Old:** `Status: PROPOSED`
- **New:** `Status: READY`
- **Gate annotation updated:** `Gate: Gate 7 (verification step — MANDATORY; sprint cannot pass Gate 7 without this)`

### Change 2: Updated taskcard summary table
- **Old:** `| TC-EXT-007 | Validate no external tool activation | Lane 0 | Gate 7 | PROPOSED |`
- **New:** `| TC-EXT-007 | Validate no external tool activation (MANDATORY) | Lane 0 | Gate 7 | READY |`

### Change 3: Updated Gate 7 Additions section
Added explicit mandatory requirements:
```
Add to Gate 7 pass condition (ALL are mandatory — Gate 7 cannot pass without them):
- All 4 Mainstream packets have external_tool_context section
- All 4 have external_tool_activation_required_for_packet: false
- TC-EXT-007 (MANDATORY) verification commands run; external-tool-authority-validation.json updated
- external-tool-authority-validation.json final status must be PASS, SKIPPED_WITH_REASON,
  or BLOCKED_WITH_REASON — PENDING is NOT acceptable at Gate 7 closeout
- No Ruflo installation or activation occurred
- No Superpowers plugin installation occurred
- No GhidraMCP installation or activation occurred
- No binary analysis performed
- All external tool outputs carry ai_draft / non-authoritative label
```

### Change 4: Updated final response contract
Added field:
```
AUTHORITY VALIDATION FINAL STATUS: <PASS | SKIPPED_WITH_REASON | BLOCKED_WITH_REASON>
  (PENDING is NOT acceptable at final closeout — TC-EXT-007 is mandatory)
```

## Gate 7 Pass Criteria (post-fix)

For Acceleration sprint to pass Gate 7, ALL of the following must be true:

1. `reports/acceleration-product-first/external-tool-authority-validation.json` EXISTS
2. All 7 invariants in that file have `status: VERIFIED` (not PENDING)
3. `ruflo_mode_confirmed: absent`
4. `superpowers_mode_confirmed: audit_only`
5. `ghidra_mcp_status_confirmed: disabled`
6. Verification commands run and logged to `raw-logs/gate-7-ext-validation.txt`
7. No Ruflo install/activation
8. No Superpowers install
9. No GhidraMCP install/activation
10. No binary analysis performed
11. All external tool outputs labeled `ai_draft` / `non_authoritative: true`

## Final Closeout Rule

```
external-tool-authority-validation.json at final Acceleration closeout:
  MUST be one of: PASS | SKIPPED_WITH_REASON | BLOCKED_WITH_REASON
  MUST NOT be: PENDING
  If validation cannot be completed → use BLOCKED_WITH_REASON with explanation
  If external tool not present → use SKIPPED_WITH_REASON: "tool not present in environment"
```

## Acceptance Criteria — Met

- [x] TC-EXT-007 status is READY (not PROPOSED)
- [x] TC-EXT-007 is mandatory in Gate 7
- [x] external-tool-authority-validation.json existence is required
- [x] No Ruflo install/activation
- [x] No Superpowers install
- [x] No GhidraMCP install/activation
- [x] No binary analysis
- [x] All external tool outputs are ai_draft/non-authoritative
- [x] Final authority validation must not remain PENDING at closeout
