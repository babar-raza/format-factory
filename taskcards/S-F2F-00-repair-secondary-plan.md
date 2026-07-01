# Taskcard S-F2F-00: Repair Secondary Plan (Full2Foss-Inspired Roadmap)

## 1. Taskcard ID and Title
S-F2F-00: Repair Secondary Plan — Full2Foss-Inspired Roadmap

## 2. Status
completed_by_plan_repair
closure_verified: CLOSED_VERIFIED (S-F2F-00B, 2026-05-08)
evidence_bundle: secondary-full2foss-plan-repair-closure-YYYYMMDD-HHMMSS.zip

## 3. Purpose
Repair the defective Full2Foss-inspired secondary roadmap plan produced in plan mode
(iridescent-coalescing-stearns.md). The original plan mixed planning and implementation,
pre-authorized governance changes without human approval, contained taskcard numbering
errors, a YAML typo, wrong sequencing for review queue vs apply mode, and missing rollback
and acceptance criteria. This taskcard covers the plan-repair execution sprint.

## 4. Phase
S0 — Plan Repair

## 5. Scope
- Create plans/secondary/ directory with corrected plan documents
- Create defect review (D-01 through D-15) and plan v2
- Create 9 proposed taskcards (S-F2F-00 through S-F2F-08)
- Append master-plan.md Section 34 (secondary roadmap)
- Append AGENTS.md Section AA (proposed-only governance note)
- Append GOVERNANCE.md Section 20 (proposed-only governance note)
- Append one-paragraph notes to docs/python-foss/acquisition-workflow.md and docs/governance/current-state-and-evidence-authority.md
- Create tools/evidence/contracts/secondary-full2foss-plan-repair.yaml
- Create 39 staging metadata files and evidence bundle

## 6. Out of Scope
- Any implementation of playbook tools, schemas, replay engines, or test infrastructure
- Any changes to gate statuses or registry
- Any product source, parser, neutral model, or sample creation
- Any settings.json allow-list changes
- Any implementation code whatsoever
- Push to remote

## 7. Inputs
- iridescent-coalescing-stearns.md (plan file, defective original)
- plans/master-plan.md (current master plan)
- registry/format-registry.yaml (current gate states)
- AGENTS.md, GOVERNANCE.md, docs/python-foss/acquisition-workflow.md,
  docs/governance/current-state-and-evidence-authority.md (governance files to append)
- tools/evidence/contracts/base-run.yaml (contract baseline)

## 8. Outputs
- plans/secondary/full2foss-inspired-plan-repair-review.md
- plans/secondary/full2foss-inspired-system-strengthening-plan-v2.md
- taskcards/S-F2F-00 through S-F2F-08 (9 files)
- plans/master-plan.md (Section 34 appended)
- AGENTS.md (Section AA appended)
- GOVERNANCE.md (Section 20 appended)
- docs/python-foss/acquisition-workflow.md (note appended)
- docs/governance/current-state-and-evidence-authority.md (note appended)
- tools/evidence/contracts/secondary-full2foss-plan-repair.yaml
- Evidence bundle zip

## 9. Exact Files Allowed
- plans/secondary/**
- taskcards/S-F2F-*.md
- plans/master-plan.md (append Section 34 only)
- AGENTS.md (append Section AA only)
- GOVERNANCE.md (append Section 20 only)
- docs/python-foss/acquisition-workflow.md (append note only)
- docs/governance/current-state-and-evidence-authority.md (append note only)
- tools/evidence/contracts/secondary-full2foss-plan-repair.yaml
- memory/ (if updated)
- .local/evidence-bundles/secondary-full2foss-plan-repair-staging/** (staging)

## 10. Exact Files Forbidden
- tools/playbook/**
- schemas/playbook/**
- schemas/product/**
- tools/product/**
- acquisition-packs/_families/**
- tests/playbook/**
- plans/review-queues/**
- docs/governance/playbook-layer.md
- docs/product-dependency-closure.md
- src/python/**
- src/net/**
- Any parser, neutral model, or sample file
- .claude/settings.json
- registry/format-registry.yaml (no gate changes)

## 11. Validation Commands
```bash
# Check no forbidden implementation paths exist
ls "plans/secondary/" && echo "OK: plans/secondary exists"
ls "taskcards/S-F2F-*.md" | wc -l  # should be 9
python tools/evidence/check_current_state_consistency.py
python tools/evidence/validate_evidence_bundle.py \
  --bundle .local/evidence-bundles/secondary-full2foss-plan-repair-*.zip \
  --contract tools/evidence/contracts/secondary-full2foss-plan-repair.yaml \
  --check-no-pending
```

## 12. Evidence Requirements
Contract: tools/evidence/contracts/secondary-full2foss-plan-repair.yaml
Min metadata: 39 files
BUNDLE_VALIDATION: PASS required

## 13. Rollback
Revert the single commit: `git revert <commit-hash>`
No irreversible changes are made.

## 14. MAIN SPRINT Non-Deviation Rule
This sprint makes NO changes to:
- registry/format-registry.yaml
- Any gate status
- Any MAIN SPRINT taskcard (TC-0001 through TC-0035)
- Any active acquisition pack gate field
MAIN SPRINT actions (FODS Gate 7, FODT Gate 4) are unaffected.

## 15. Format-Agnostic Requirement
No format-specific tooling is created. All planning documents use format-neutral language.
Future tools described in plan-v2 must accept format_id as a required parameter.

## 16. Approval Required Before Execution
This taskcard is completed by the plan-repair execution sprint authorized by the human
prompt. No additional approval needed — this IS the authorized sprint.

## 17. Dependencies
None — this is the root taskcard.

## 18. Done Definition
DONE when:
- plans/secondary/ contains exactly 2 .md files
- taskcards/ contains exactly 9 S-F2F-*.md files
- master-plan.md contains Section 34
- AGENTS.md contains Section AA
- GOVERNANCE.md contains Section 20
- Evidence bundle validates: BUNDLE_VALIDATION: PASS
- Metadata count: >= 39
- Git status: clean after commit
- No PENDING markers in committed files
- No push performed
