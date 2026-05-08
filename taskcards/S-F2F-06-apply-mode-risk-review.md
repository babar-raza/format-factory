# Taskcard S-F2F-06: Apply-Mode Risk Review

## 1. Taskcard ID and Title
S-F2F-06: Apply-Mode Risk Review

## 2. Status
proposed_pending_human_approval

## 3. Purpose
Produce a structured risk assessment for implementing apply mode in the replay engine.
Apply mode would allow the replay engine to actually execute operations (write files,
update acquisition packs). This taskcard produces the risk document ONLY — it does NOT
implement apply mode. The human must read the risk review and provide a separate explicit
authorization before apply mode is built.

## 4. Phase
S6 — Apply-Mode Risk Review

## 5. Scope
- plans/secondary/apply-mode-risk-review.md (risk assessment document only)
No apply mode implementation. No changes to existing tools.

## 6. Out of Scope
- Implementing apply mode in replay_acquisition_playbook.py
- Any LLM fallback implementation
- Any changes to gate states
- Any acquisition pack modifications
- Any product source

## 7. Inputs
- tools/playbook/replay_acquisition_playbook.py (from S-F2F-03)
- tests/playbook/golden/ (from S-F2F-04)
- plans/secondary/full2foss-inspired-system-strengthening-plan-v2.md (risk register)

## 8. Outputs
- plans/secondary/apply-mode-risk-review.md (one document only)

## 9. Exact Files Allowed
- plans/secondary/apply-mode-risk-review.md
- tools/evidence/contracts/s-f2f-06-apply-risk-review.yaml (sprint contract)
- memory/ (if updated)

## 10. Exact Files Forbidden
- tools/playbook/replay_acquisition_playbook.py (must not be modified to add apply mode)
- Any new CLI flag or method for apply mode in existing tools
- acquisition-packs/**/*.yaml (no mutations)
- schemas/product/**
- src/python/**, src/net/**
- registry/format-registry.yaml

## 11. Validation Commands
```bash
# Risk review doc exists
ls plans/secondary/apply-mode-risk-review.md && echo "OK"
# Confirm apply mode NOT added to replay tool
grep -n "def apply" tools/playbook/replay_acquisition_playbook.py && echo "FAIL: apply mode found" || echo "OK"
grep -n "mode.*apply" tools/playbook/replay_acquisition_playbook.py && echo "FAIL: apply mode found" || echo "OK"
# Risk review contains required sections
grep -n "checksum" plans/secondary/apply-mode-risk-review.md
grep -n "rollback" plans/secondary/apply-mode-risk-review.md
grep -n "review queue" plans/secondary/apply-mode-risk-review.md
python tools/evidence/validate_evidence_bundle.py \
  --bundle .local/evidence-bundles/s-f2f-06-*.zip \
  --contract tools/evidence/contracts/s-f2f-06-apply-risk-review.yaml \
  --check-no-pending
```

## 12. Evidence Requirements
Sprint-specific contract: tools/evidence/contracts/s-f2f-06-apply-risk-review.yaml
BUNDLE_VALIDATION: PASS required

Required content in apply-mode-risk-review.md:
- What files apply mode would mutate
- Checksum anchor strategy (prevent mutation without anchor check)
- Review queue integration requirements before apply mode activates
- Rollback plan for failed apply operations
- Testing requirements (golden tests must pass)
- Recommended safeguards

## 13. Rollback
Delete plans/secondary/apply-mode-risk-review.md.
Revert commit.

## 14. MAIN SPRINT Non-Deviation Rule
This sprint creates one documentation file only. No executable changes. MAIN SPRINT unaffected.

## 15. Format-Agnostic Requirement
Risk review must cover apply mode behavior for ALL formats, not just FODS.
Risk register must use format-agnostic language.

## 16. Approval Required Before Execution
Human authorization prompt must explicitly name "S-F2F-06 Apply-Mode Risk Review."
Apply mode IMPLEMENTATION requires a SEPARATE human authorization after reading the risk doc.
Two explicit prompts required: one for S-F2F-06 (risk review), one for apply mode implementation.

## 17. Dependencies
- S-F2F-04: completed (golden dry-run tests working)
- S-F2F-03: completed (dry-run replay engine working)

## 18. Done Definition
DONE when:
- plans/secondary/apply-mode-risk-review.md: present with all required sections
- NO apply mode added to replay_acquisition_playbook.py
- BUNDLE_VALIDATION: PASS
- Git status: clean after commit
- Human has been clearly informed that apply mode implementation requires a separate
  authorization prompt AFTER reading this risk review
