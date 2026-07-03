---
espanso_provenance:
  source_trigger: ":ff-humanfree"
  source_block: 118
  source_line_range: [125600, 126293]
  gap_id: GAP-ESP-008
  extraction_date: "2026-07-03"
  capability_id: human-free-rectification
  supersedes_block: 53
prompt_id: ESP-PROMPT-6
title: "Human-Free Autonomy Governance Rectification"
version: "1.0"
status: ACTIVE
mutating: true
context_profile: full
---

# Human-Free Autonomy Governance Rectification Sprint

## Doctrine

The system goal is complete practical autonomy. Any governance text that says or implies
a human is required at a point where the agent CAN act honestly, safely, and within
repository policy is a governance defect.

This protocol scans governance surfaces, identifies such defects, and repairs them.

## Short-Context View

Scan AGENTS.md, CLAUDE.md, docs/governance/, .supervisor/prompts/, and related governance
files for text that incorrectly requires human intervention. For each finding: classify whether
it is a true external impossibility or a fixable governance defect. Fix the defects.
Do NOT remove genuine external blockers (missing credentials, unavailable permissions, etc.).

---

## Genuine External Impossibilities (NOT defects — preserve these)

A human requirement is legitimate ONLY when:
- Missing credentials that no agent has
- Denied permissions from an external service
- Unavailable network or remote service
- Legally restricted decision with no repository policy to resolve it
- Destructive action explicitly forbidden by repository policy
- Branch protection requiring unavailable external identity
- Absent policy authority for an irreversible action
- Inaccessible external account, registry, or provider

Everything else is a governance defect.

## Scan Targets

Primary targets (always scan):
- `AGENTS.md`
- `CLAUDE.md`
- `.github/copilot-instructions.md` (if exists)

Secondary targets (scan if present):
- `docs/governance/**`
- `.supervisor/prompts/**`
- `.supervisor/policies.yaml`
- `docs/automation/**`

## Defect Patterns to Find

Scan for these phrases and classify each occurrence:

| Pattern | Likely Classification |
|---|---|
| "human must review" | DEFECT unless review requires credentials |
| "human must approve" | DEFECT unless Gate 11 or external commercial sign-off |
| "human must commit" | DEFECT — SCM Agent can commit |
| "human must push" | DEFECT if credentials exist; TRUE_EXTERNAL_GATE if not |
| "human must decide" | DEFECT if a policy can resolve it |
| "ask the user" | DEFECT if the answer is derivable from repository policy |
| "wait for user" | DEFECT in autonomous context |
| "operator approval" | DEFECT unless Gate 11 |
| "manual gate" | DEFECT unless truly external |

Legitimate patterns (preserve these):
- Gate 11 execution approval by Babar Raza
- PyPI/NuGet publication credentials
- Git push when branch protection requires unavailable identity
- Destructive operations without policy authority

## Repair Protocol

### Phase 1: Discovery
```
For each scan target file:
  → Read the complete file
  → Search for defect patterns (see table above)
  → For each match: record file, line, exact text, classification
```

### Phase 2: Classification
For each finding:
```
→ Ask: "Can an agent do this honestly, safely, and within repository policy?"
  → YES: GOVERNANCE_DEFECT — repair it
  → NO: TRUE_EXTERNAL_GATE — preserve it and add a comment explaining why
```

### Phase 3: Repair
For each GOVERNANCE_DEFECT:
```
→ Replace human-required language with agent-executable alternative
→ Follow AGENTS.md AG1-AG2 decision loop format:
  "Apply AGENTS.md §AG1-AG2: agent executes when <condition>.
   Only <specific external gate> requires human authority."
→ Preserve the intent of the original rule
→ Do not weaken security or governance rules — only remove unjustified human gates
```

### Phase 4: Verify
```
→ Re-read each modified file
→ Confirm no legitimate external gate was removed
→ Confirm no governance intent was lost
→ Run any available governance validators
```

### Output
```
reports/human-free-audit/
  scan-results-<date>.yaml   — All findings with classification
  repair-log-<date>.md       — What was changed and why
```

### Evidence Requirements
- List of all files scanned
- Count of defects found and repaired
- Count of genuine external gates preserved
- Diff of each modified file

### Completion Gate
- All primary targets scanned
- All GOVERNANCE_DEFECTs repaired
- All TRUE_EXTERNAL_GATEs preserved and annotated
- Repair log written to `reports/human-free-audit/`
- No legitimate governance rule weakened
