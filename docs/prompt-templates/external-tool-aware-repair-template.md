# External Tool Aware Repair Template

**Added:** 2026-06-04
**Authority:** local-memory-sync sprint 2026-06-04

## Purpose

Use this template when running a plan repair pass to make a stream plan externally coherent. This template ensures the repaired plan correctly handles Ruflo, Superpowers, and GhidraMCP.

---

## Sprint Identity
- Sprint ID: FORMAT-FACTORY-{{STREAM}}-EXTERNAL-TOOL-AWARE-REPAIR-{{DATE}}
- Stream: {{STREAM}}
- Type: Plan repair (not product implementation)
- Date: {{DATE}}
- Reference: docs/prompt-templates/repair-order-reference.md

## Mission
Repair the {{STREAM}} plan to be externally coherent with:
- Four-stream operating model
- Product-first operating model
- External tool architecture
- AI authority boundary
- Mainstream mega-train continuation loop

## Allowed Paths
- docs/prompt-templates/{{stream}}-*.md
- docs/governance/*.md (read-only unless creating new doc)
- reports/supervisor/plan-repair-{{stream}}-{{DATE}}.md (NEW — repair summary)
- .local/evidences/plan-repair-{{stream}}-{{DATE}}/evidence-declaration.yaml

## Forbidden Paths
- src/net/*
- src/python/*
- tests/*
- .vscode/mcp.json
- .supervisor/policies.yaml
- registry/format-registry.yaml

## Required Sections to Add/Update

### Section: External Tool Architecture
Add a section to the repaired prompt that includes:

```markdown
## External Tool Architecture

### Ruflo
- Current mode: {{RUFLO_MODE}}
- Fallback if absent: local sequential coordinator
- Full loop requires: Supervisor + human authorization
- Reference: docs/governance/ruflo-runtime-governance.md

### Superpowers
- Usage: normalized skills only
- Plugin install: requires Supervisor + human authorization
- Reference: docs/governance/superpowers-skill-intake.md

### GhidraMCP
- Default: DISABLED_BY_DEFAULT
- Reference: docs/governance/ghidra-mcp-compliance-gate.md
```

### Section: AI Authority Boundary
Add:
```markdown
## AI Authority Boundary
- AI output is never authority — labeled ai_draft
- AI may not: mark capability complete, approve gates, override tests
- Reference: docs/governance/ai-authority-boundary.md
```

### Section: Four-Stream Interaction
Add:
```markdown
## Four-Stream Interaction
- This stream: {{STREAM}}
- Receives from: {{UPSTREAM_STREAMS}}
- Delivers to: {{DOWNSTREAM_STREAMS}}
- Cross-stream dependencies: {{DEPENDENCIES}}
- Reference: docs/governance/four-stream-operating-model.md
```

### Section: Product-First Justification
Add:
```markdown
## Product-First Justification
This sprint addresses: {{PRODUCT_BLOCKER_OR_THROUGHPUT_IMPROVEMENT}}
- What product blocker is removed: {{BLOCKER}}
- What product throughput is improved: {{THROUGHPUT_IMPROVEMENT}}
- What false verdict is prevented: {{FALSE_VERDICT_PREVENTED}}
- Reference: docs/governance/product-first-operating-model.md
```

## Repair Closeout

The repair produces:
1. Updated prompt template file
2. `reports/supervisor/plan-repair-{{stream}}-{{DATE}}.md` with:
   - What was added
   - What was changed
   - What references were added
   - Whether the plan is now repair-complete (PLAN_REPAIR_COMPLETE or PLAN_REPAIR_PARTIAL)

## Evidence
- No evidence declaration required for repair-only pass
- Changed files list in repair report is sufficient
- No product output required

## Repair Verdict
- PLAN_REPAIR_COMPLETE — all required sections added, plan ready for execution
- PLAN_REPAIR_PARTIAL — some sections added, further repair needed
- PLAN_REPAIR_BLOCKED — repair blocked by missing governance doc (create the doc first)

## Hard Prohibitions (repair pass)
- No product source changes
- No gate approval
- No git push or commit
- No external tool installation
