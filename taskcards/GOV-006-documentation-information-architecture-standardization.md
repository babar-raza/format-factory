---
taskcard_id: GOV-006
title: Documentation and Information Architecture Standardization
status: planning_ready
created: 2026-05-09
sprint: not_started -- requires separate explicit human authorization
visibility: internal
publish_allowed: false
authority: authority
relationship_to_main_sprint: governance -- documentation standards only
relationship_to_product_source: none
must_cross_check:
  - plans/master-plan.md
  - memory/00-index.md
  - docs/agent-methodology-index.md
---

# GOV-006 -- Documentation and Information Architecture Standardization

## Purpose

Create an industry-grade documentation and knowledge architecture for Format Factory.

The project currently uses a flat numbered memory file structure (memory/01 through memory/15)
and a flat docs/ directory without a taxonomy. Every sprint that adds a new file makes the next
sprint harder to orient. Agents cannot determine from directory structure alone whether a file is
an architecture decision, a context snapshot, a runbook, a standard, or a generated artifact.

GOV-006 defines the correct document structure, creates the taxonomy and standards, implements
enforcement tooling, and begins a gradual migration of existing memory and docs files.

## Problem Statement

The current knowledge structure has these specific deficiencies:

1. Architecture decisions stored as memory context snapshots. FFSM design, LLM module layout,
   community component positioning belong in docs/architecture/design-records/, not memory/15.
2. No file taxonomy. Agents do not know whether new knowledge should go in memory/NN, docs/*.md,
   or a specific subdirectory.
3. Naming is inconsistent. memory/11 covers multiple topics; memory/12 overlaps docs/; memory/13,
   14, 15 are date-stamped context snapshots with no standard naming scheme.
4. No lifecycle model. Documents have no status field (draft, accepted, superseded, deprecated).
5. No document registry. There is no single file listing all durable docs with type, authority,
   owner, and update trigger.
6. No enforcement linter. Nothing prevents future agents from creating memory/16+, arbitrary docs,
   or duplicate content.
7. No migration strategy. memory/13, 14, 15 contain architecture content that should eventually
   live under docs/architecture/. No plan exists for migration without breaking active agents.

## Scope (when authorized)

### Files to create

```
docs/governance/standards/documentation-standard.md
docs/governance/standards/naming-standard.md
docs/governance/standards/sprint-closeout-standard.md
docs/governance/README.md
docs/architecture/README.md
docs/architecture/decisions/README.md
docs/architecture/design-records/README.md
docs/context/README.md
docs/context/chat-sync/2026-05-09-chatgpt-initial-analysis.md
docs/context/chat-sync/2026-05-09-ai-supervision-three-pilot.md
docs/architecture/design-records/DR-20260509-governed-ai-and-state-management.md
docs/document-registry.yaml
memory/legacy/README.md
tools/docs/lint_documentation_structure.py
tools/docs/validate_frontmatter.py
```

### Files to update

```
memory/00-index.md -- add docs/context/ references; update legacy notes
docs/agent-methodology-index.md -- add docs/architecture/ and docs/context/ references
docs/fresh-chat-continuity-brief.md -- add new canonical locations
AGENTS.md -- add documentation governance section (citing documentation-standard.md)
GOVERNANCE.md -- add documentation policy section
```

## Hard prohibitions (when this sprint executes)

- No product source
- No gate status changes
- No LLM calls
- No embeddings
- No state manager code (FFSM is design only)
- No push

## Acceptance criteria

1. `docs/governance/standards/documentation-standard.md` defines the document type taxonomy
   (minimum 12 types), naming conventions, lifecycle states, ownership model, update triggers,
   archival model, and registry requirements.
2. `docs/document-registry.yaml` lists all durable docs with doc_id, doc_type, authority,
   owner, status, and update_trigger.
3. `tools/docs/lint_documentation_structure.py` implemented and exits 0 on the current repo.
4. `tools/docs/validate_frontmatter.py` implemented and exits 0 on all durable docs.
5. `docs/context/chat-sync/` contains equivalents for memory/13 and memory/14 content or
   migration pointers to their new canonical locations.
6. `docs/architecture/design-records/DR-20260509-governed-ai-and-state-management.md` captures
   the content currently in memory/15 in the correct document format (architecture_decision or
   design_record doc_type, ADR/DR template, required frontmatter).
7. `memory/legacy/README.md` (or `memory/README.md`) explains the transitional model and points
   future agents to docs/context/ as the new canonical location for context snapshots.
8. METHODOLOGY_LINK_CHECK: PASS
9. CURRENT_STATE_CONSISTENCY: PASS
10. BUNDLE_VALIDATION: PASS

## Document type taxonomy (defined in this taskcard for planning purposes)

| Type | doc_type | Location | Authority |
|------|----------|----------|-----------|
| Authority document | authority | registry/, plans/, taskcards/, tools/evidence/contracts/ | Level 1-3 |
| Architecture document | architecture_doc | docs/architecture/*.md | standard |
| Architecture Decision Record | architecture_decision | docs/architecture/decisions/ | architecture_decision |
| Design Record | design_record | docs/architecture/design-records/ | design_record |
| Standard | standard | docs/governance/standards/ | standard |
| Policy | policy | docs/governance/policies/ | policy |
| Runbook | runbook | docs/operations/runbooks/ | standard |
| Checklist | checklist | docs/operations/checklists/ | standard |
| Context snapshot | context_only | docs/context/chat-sync/ or memory/NN (legacy) | context_only |
| Methodology doc | standard | docs/ root (existing) | standard |
| Status / operational state | generated | docs/status/ or memory/09 (legacy) | derived_mirror |
| Evidence | historical | .local/evidence-bundles/ | historical |
| Taskcard | authority | taskcards/ | authority |
| Prompt template | standard | docs/prompts/ | standard |

## Naming conventions (defined here for planning purposes)

- ADRs: `ADR-YYYYMMDD-short-kebab-title.md` in `docs/architecture/decisions/`
- Design Records: `DR-YYYYMMDD-short-kebab-title.md` in `docs/architecture/design-records/`
- Standards: `lowercase-kebab-title-standard.md` in `docs/governance/standards/`
- Runbooks: `lowercase-kebab-title-runbook.md` in `docs/operations/runbooks/`
- Context snapshots: `YYYY-MM-DD-short-kebab-topic.md` in `docs/context/chat-sync/`

## Migration plan for existing memory files

Stage 1 (GOV-006 sprint -- immediate):
- Keep all existing memory/NN files in place.
- Mark memory/13, 14, 15 as transitional context snapshots.
- Create docs/context/ and docs/architecture/ with READMEs.
- Create docs/context/chat-sync/ equivalents for memory/13 and memory/14.
- Create DR-20260509 as the design-record equivalent for memory/15.
- Update memory/00-index.md to point to new canonical locations.

Stage 2 (gradual migration -- future sprints):
- Move durable architecture content from memory/11, 13, 14, 15 into docs/architecture/.
- Keep memory files as compatibility indexes or pointers.
- Update fresh-chat bootstrap to point to docs/context/ as primary.

Stage 3 (enforcement -- after GOV-006):
- Add documentation structure linter (tools/docs/lint_documentation_structure.py).
- Add frontmatter validator (tools/docs/validate_frontmatter.py).
- Add local pre-close check to sprint closeout runbook.
- Reject new unclassified or out-of-taxonomy docs in any sprint.

## Blocking constraint

GOV-006 must NOT be executed before the documentation standard is drafted.
The standard must define the taxonomy before the first ADR or DR is filed.
Do not create docs/architecture/ content in any sprint other than GOV-006.
Do not create docs/context/ content in any sprint other than GOV-006.
Do not create docs/document-registry.yaml in any sprint other than GOV-006.

Memory/13, 14, 15 are explicitly marked as transitional. They may be used until GOV-006
migrates their content to the correct canonical locations.

No new memory/NN files (memory/16 or later) may be created without GOV-006 authorization.
All new durable architecture decisions must wait for GOV-006 to define the correct location.

## Relationship to other governance taskcards

| Taskcard | Relationship |
|----------|-------------|
| GOV-004 | Created the current ChatGPT analysis memory sprint; GOV-006 will migrate memory/13 content |
| GOV-005 | Created the AI module architecture memory sprint; GOV-006 will migrate memory/15 content |
| GOV-001 | Discovered-gap rule; GOV-006 provides the doc framework for gap capture |
| GOV-002 | Local planning methodology; GOV-006 will integrate with methodology index |
| GOV-003 | Methodology linkage and enforcement; GOV-006 extends this to full doc taxonomy |

## Validation commands (when executed)

```bash
python tools/governance/check_methodology_links.py
python -m pytest tests/governance/test_methodology_links.py -q
python tools/docs/lint_documentation_structure.py
python tools/docs/validate_frontmatter.py
python tools/evidence/check_current_state_consistency.py
```
