---
artifact_id: TC-SKILL-004-decompose-monolithic-codec
artifact_type: taskcard
path: taskcards/skill-gaps/TC-SKILL-004-decompose-monolithic-codec.md
format_id: null
product_family: python-foss
visibility: internal
publish_allowed: false
license: null
provenance_required: false
provenance_status: not-applicable
source_hash: null
generated_by: tender-dreaming-lovelace
generated_at: 2026-06-21
reusable: false
refresh_policy:
  trigger: manual
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
release_blockers: []
notes: >
  Taskcard to create the decompose-monolithic-codec skill command file from the existing
  design in taskcards/skill-gaps/decompose-monolithic-codec-design.md. Created by
  tender-dreaming-lovelace plan.
---

# TC-SKILL-004: Create decompose-monolithic-codec Skill Command File and Register It

**Phase:** 3
**Status:** not_started
**Owner:** agent (claude-code)
**Created:** 2026-06-21
**Last updated:** 2026-06-21
**Blocking:** FODG/XCF/ZST monolith rework path execution
**Blocked by:** nothing (design already exists in decompose-monolithic-codec-design.md)
**Format:** none (multi-format infrastructure)
**Gate:** none

---

## Objective

Create the `decompose-monolithic-codec` skill command file from the existing design document
at `taskcards/skill-gaps/decompose-monolithic-codec-design.md`, register it in the skill
registry, and close the governance gap that currently prevents FODG/XCF/ZST monolith
decomposition from being executed through a governed skill path.

Deliverables:
1. `.claude/commands/decompose-monolithic-codec.md` — skill command file (from design doc)
2. Entry in `.supervisor/skill-registry.yaml` under HEALING_SKILLS category
3. Updated `docs/plans/skill-governance-bypass-audit.md` — mark TC-REWORK-001/002 as CLOSED
4. Closure of this taskcard with all acceptance criteria met

---

## Context

The design for the `decompose-monolithic-codec` skill was created by TC-REWORK-001 and TC-REWORK-002
as part of the skill-governance-bypass-audit. The design document exists at:
`taskcards/skill-gaps/decompose-monolithic-codec-design.md`

However, no command file or skill registry entry exists. This means:
- FODG, XCF, and ZST rework items (GOV_BLOCK:monolith_detection_validator) cannot reference a
  governed skill in their evidence declarations
- V46 would flag any FODG/XCF/ZST source changes as missing skill transcript
- The bypass audit marks this gap as "design closure — pending execution sprint"

Current monolith status (from design doc):
| Format | File | Current LOC | Cap | Over By |
|--------|------|-------------|-----|---------|
| FODG | fodg_codec.py | 5933 | 4334 | +37% — BLOCKING |
| XCF | xcf_parser.py | 5588 | 3997 | +40% — LATENT |
| ZST | zst_codec.py | 5750 | 4210 | +37% — LATENT |

Gap reference: GAP-SK-008 in `.local/recon/gap-register.yaml`
Correction plan lane: Lane F (SRC Healing), Lane D (Missing Skill Workflow)

---

## Scope

### In scope

- Creating `.claude/commands/decompose-monolithic-codec.md` from the design document
- Registering the skill in `.supervisor/skill-registry.yaml`
- Updating bypass audit to close TC-REWORK-001/002
- Adding command to `command-registry.yaml`

### Out of scope

- Actual execution of monolith decomposition (that is the work governed BY this skill)
- Changes to FODG/XCF/ZST source files
- Changes to analytics.py files

---

## Acceptance Criteria

Completion requires ALL of the following:

- [ ] `.claude/commands/decompose-monolithic-codec.md` created with:
      - Required inputs: `format_id` (one of fodg, xcf, zst), `source_file`, `analytics_target_file`
      - Allowed paths: ONLY `src/python/<format_id>/<format_id>_analytics.py` for new functions;
        `src/python/<format_id>/<format_id>_codec.py` or `xcf_parser.py` for deletions only
      - Forbidden paths: everything in `src/python/` NOT matching the pattern above
      - Stop conditions: `BLOCKED_CAP_REACHED` if analytics target at LOC cap;
        `BLOCKED_NO_BACKWARD_COMPAT` if backward compat verification fails
      - Transcript schema: `functions_moved`, `loc_reduction`, `backward_compat_verified` (must be true),
        `codec_tests_pass` (must be true)
      - Anti-overclaim: NEVER mark complete without backward_compat_verified=true and codec tests pass
- [ ] Skill registered in `.supervisor/skill-registry.yaml` under HEALING_SKILLS
      with `spec_qname_required: false`, `enforces_transcript: true`
- [ ] `decompose-monolithic-codec` added to `command-registry.yaml` (HEALING_SKILLS group)
- [ ] `docs/plans/skill-governance-bypass-audit.md` updated: TC-REWORK-001/002 marked CLOSED
- [ ] `python tools/supervisor/validate_skill_registry.py --registry .supervisor/skill-registry.yaml`
      passes for the new entry
- [ ] Self-challenge completed (see AGENTS.md Section I)

---

## Artifacts Produced

| Artifact | Path | Visibility | Notes |
|---|---|---|---|
| Skill command file | `.claude/commands/decompose-monolithic-codec.md` | internal | Core deliverable |
| Skill registry entry | `.supervisor/skill-registry.yaml` | internal | Under HEALING_SKILLS |
| Updated bypass audit | `docs/plans/skill-governance-bypass-audit.md` | internal | TC-REWORK-001/002 CLOSED |

---

## Artifacts Consumed (Inputs)

| Artifact | Path | Required? |
|---|---|---|
| Skill design document | `taskcards/skill-gaps/decompose-monolithic-codec-design.md` | Required |
| FODG rework path | `taskcards/skill-gaps/fodg-monolith-rework-path.md` | Required |
| XCF rework path | `taskcards/skill-gaps/xcf-monolith-rework-path.md` | Required |
| ZST rework path | `taskcards/skill-gaps/zst-monolith-rework-path.md` | Required |
| Bypass audit | `docs/plans/skill-governance-bypass-audit.md` | Required |
| Skill registry | `.supervisor/skill-registry.yaml` | Required |

---

## Steps

1. Read `taskcards/skill-gaps/decompose-monolithic-codec-design.md` in full.
2. Read the 3 format-specific rework path docs (fodg, xcf, zst).
3. Create `.claude/commands/decompose-monolithic-codec.md` per the design.
4. Add skill entry to `.supervisor/skill-registry.yaml` under HEALING_SKILLS.
5. Add `decompose-monolithic-codec` to `.claude/commands/command-registry.yaml`.
6. Update `docs/plans/skill-governance-bypass-audit.md`: change TC-REWORK-001/002 status to CLOSED.
7. Run `python tools/supervisor/validate_skill_registry.py --registry .supervisor/skill-registry.yaml`
   to confirm the new entry passes.
8. Complete self-challenge (AGENTS.md Section I).
9. Update this taskcard to `status: complete`.

---

## Completion Record

**Completed by:** [agent-id]
**Completion date:** [ISO-8601]
**Artifacts produced:** [list paths]
**Gaps discovered:** [list G-IDs or "none"]
**Notes:** [any notes for next phase]
