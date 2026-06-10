# Archive and Split Strategy

**Sprint ID:** FORMAT-FACTORY-MASTER-PLAN-GOVERNANCE-REVIEW-HEALING-PLAN-001
**Date:** 2026-06-10

## Archive Files to Create (in execution)

1. **`docs/history/master-plan-full-before-healing-2026-06-10.md`** — Full backup of plans/master-plan.md before any edits (SHA-256 recorded)
2. **`docs/history/master-plan-archived-sections-2026-06-10.md`** — Just the archived sections with context headers

## Sections to Archive

| Old Section | Line Range | Destination | Content Summary | Replacement Pointer Text | Reason |
|-------------|------------|-------------|-----------------|--------------------------|--------|
| §7 Evidence Bundle Inspection Rule | 152-166 | archived-sections | Bundle upload rule | `> Archived: See docs/history/master-plan-archived-sections-2026-06-10.md §7. Replaced by declaration-driven pipeline (Section 12).` | Superseded by §41 declaration-driven model |
| §9 Phase 0 Required Files | 209-260 | archived-sections | 45-file list | `> Archived: See docs/history/master-plan-archived-sections-2026-06-10.md §9. Phase 0 accepted 2026-05-04.` | Phase 0 complete; list served its purpose |
| §25 Active Taskcards | 666-691 | archived-sections | TC-0001..0053 table | `> Archived: See docs/history/master-plan-archived-sections-2026-06-10.md §25. Current taskcard model uses declaration-driven taskcards.` | Stale; project uses new taskcard model |
| §27 Gap Register | ~780-840 | archived-sections | G-001+ gaps | `> Archived: See docs/history/master-plan-archived-sections-2026-06-10.md §27. Historical gaps preserved.` | All gaps historical |
| §28 Healing Gap Register | ~840-900 | archived-sections | G-HEAL-001..036+ | `> Archived: See docs/history/master-plan-archived-sections-2026-06-10.md §28. All healing gaps resolved.` | All resolved |
| §31 Phase 0 Review Checklist | ~990-1000 | archived-sections | 36-check list | `> Archived: See docs/history/master-plan-archived-sections-2026-06-10.md §31. Phase 0 accepted 2026-05-04.` | Phase 0 complete |
| §32 Run History Table | ~1000-1050 | archived-sections | run001-run042 | `> Archived: See docs/history/master-plan-archived-sections-2026-06-10.md §32. Modern sprints use declaration-driven model.` | Historical; modern sprints different |
| §33 Run Commit Ledger | 1052-1429 | archived-sections | ~380 lines commit records | `> Archived: See docs/history/master-plan-archived-sections-2026-06-10.md §33. Current-state authority: session-resume.md and bundle-metadata/.` | Largest historical section |
| §36 S-F2F Secondary Sprint | 1506-1577 | archived-sections | S-F2F-00..08 roadmap | `> Archived: See docs/history/master-plan-archived-sections-2026-06-10.md §36. S-F2F-00 through S-F2F-04 closed; remainder never authorized.` | Closed/unauthorized |
| §37 Format Understanding Layer | 1582-1656 | archived-sections | FUL/LLM/EMB/REP/NAC backlogs | `> Archived: See docs/history/master-plan-archived-sections-2026-06-10.md §37. Never authorized; backlog only.` | Never executed |
| §39 AI/LLM Platform Layer | 1747-1844 | archived-sections | AI platform plan | `> Archived: See docs/history/master-plan-archived-sections-2026-06-10.md §39. Conflicts with ai-authority-boundary.md. Never authorized.` | Conflicts with current AI model |

## Sections to Condense (keep short version, archive full)

| Old Section | Current Lines | Target Lines | What to Keep | What to Archive |
|-------------|--------------|-------------|--------------|-----------------|
| §6 Current Project State | 38 | 20 | Source pointers (poc-targets.yaml, session-resume.md) | Detailed gate status narrative |
| §26 Decision Register | ~86 | 60 | All DECs, condensed notes | Verbose notes |
| §29 Risk Register | ~50 | 10 | Top risks summary | Full register |
| §38 Format Expansion Roadmap | ~83 | 5 | Strategic direction (1 sentence) + pointer | Full roadmap, Non-Aspose backlog |
| §23 Pilot Recommendation | 20 | 5 | "First pilot: FODS, completed" | Full rationale and history |
| §44 Authority Layers | 90 | 15 | Core principle + pointers | Detailed subsystem requirements |

## Rules

1. The word "delete" is **forbidden** — use "archive and replace with pointer"
2. Every archived section must have a pointer in the healed master plan
3. No decision or historical record may be permanently lost
4. The full backup (`master-plan-full-before-healing-2026-06-10.md`) preserves the complete document
5. SHA-256 of the pre-edit document must be recorded in `preedit-sha.txt`
6. Archive-pointer-map.json must map every archived section to its destination

## Archive Pointer Map Structure

```json
{
  "archive_date": "2026-06-10",
  "full_backup": "docs/history/master-plan-full-before-healing-2026-06-10.md",
  "archived_sections": "docs/history/master-plan-archived-sections-2026-06-10.md",
  "mappings": [
    {"old_section": "7", "destination": "archived-sections", "pointer_in_healed": "Section 12"},
    {"old_section": "9", "destination": "archived-sections", "pointer_in_healed": "ARCHIVE-PTR"},
    {"old_section": "25", "destination": "archived-sections", "pointer_in_healed": "ARCHIVE-PTR"},
    {"old_section": "27", "destination": "archived-sections", "pointer_in_healed": "ARCHIVE-PTR"},
    {"old_section": "28", "destination": "archived-sections", "pointer_in_healed": "ARCHIVE-PTR"},
    {"old_section": "31", "destination": "archived-sections", "pointer_in_healed": "ARCHIVE-PTR"},
    {"old_section": "32", "destination": "archived-sections", "pointer_in_healed": "ARCHIVE-PTR"},
    {"old_section": "33", "destination": "archived-sections", "pointer_in_healed": "ARCHIVE-PTR"},
    {"old_section": "36", "destination": "archived-sections", "pointer_in_healed": "ARCHIVE-PTR"},
    {"old_section": "37", "destination": "archived-sections", "pointer_in_healed": "ARCHIVE-PTR"},
    {"old_section": "39", "destination": "archived-sections", "pointer_in_healed": "ARCHIVE-PTR"}
  ]
}
```
