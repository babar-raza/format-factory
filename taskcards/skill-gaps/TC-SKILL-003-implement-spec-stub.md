---
artifact_id: TC-SKILL-003-implement-spec-stub
artifact_type: taskcard
path: taskcards/skill-gaps/TC-SKILL-003-implement-spec-stub.md
format_id: fodt
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
notes: Skill-gap taskcard for the implement-spec-stub skill. Created by tender-dreaming-lovelace plan.
---

# TC-SKILL-003: Design and Register implement-spec-stub Skill for Architecture-Only Spec/ Bootstrap

**Phase:** 3
**Status:** not_started
**Owner:** agent (claude-code)
**Created:** 2026-06-21
**Last updated:** 2026-06-21
**Blocking:** FODT spec/ bootstrap completion, FODT compat.py activation
**Blocked by:** spec-literal-qname-to-code-mapping must have run for FODT format
**Format:** fodt
**Gate:** none

---

## Objective

Design and register the `implement-spec-stub` skill, which governs filling in `architecture_only`
Python spec/ stub files with real implementation. The skill must include behavioral equivalence
verification to ensure no regression against the existing `models.py` implementation.

Deliverables:
1. `.claude/commands/implement-spec-stub.md` — skill command file with full governance rules
2. Entry in `.supervisor/skill-registry.yaml` under SPEC_LITERAL_SKILLS category
3. `tests/python/fodt/test_compat_bootstrap.py` — behavioral equivalence test skeleton
4. Closure of this taskcard with all acceptance criteria met

---

## Context

`src/python/fodt/spec/` has 11 Python stub files (text/ and table/ entity classes) at status
`architecture_only`. The file `src/python/fodt/compat.py` contains a BOOTSTRAP RULE that
FORBIDS importing from spec/ until:

1. spec/ stubs reach `status: implemented` in shared/qname-registry/fodt.yaml
2. `tests/python/fodt/test_compat_bootstrap.py` proves behavioral equivalence

Without the `implement-spec-stub` skill, filling these stubs would be an ungoverned direct edit
to `src/python/fodt/spec/`, violating the skill-first policy enforced by V46.

Gap reference: GAP-SK-004 in `.local/recon/gap-register.yaml`
Correction plan lane: Lane F (SRC Healing), Lane D (Missing Skill Workflow)

---

## Scope

### In scope

- Design of the `implement-spec-stub` skill command file
- Registration of the skill in `.supervisor/skill-registry.yaml`
- Creation of `tests/python/fodt/test_compat_bootstrap.py` with behavioral equivalence skeleton
- Documentation of allowed and forbidden paths for the skill

### Out of scope

- Actual implementation of FODT spec/ stubs (that is the work governed BY this skill)
- Changes to FODT `models.py`, `parser.py`, or `writer.py`
- Changes to FODS or other format source files

---

## Acceptance Criteria

Completion requires ALL of the following:

- [ ] `.claude/commands/implement-spec-stub.md` created with all required governance fields:
      - Required inputs: `format_id`, `stub_path`, `spec_qname`, `behavioral_equivalence_test`
      - Allowed paths: `src/python/<format_id>/spec/**/*.py`, `src/python/<format_id>/compat.py`,
        `tests/python/<format_id>/test_compat_bootstrap.py`
      - Forbidden paths: `src/python/<format_id>/models.py`, `src/python/<format_id>/parser.py`
      - Stop conditions: `BLOCKED_EQUIVALENCE_FAILURE` if equivalence test fails;
        `BLOCKED_NO_QNAME_RECORD` if spec_qname not in qname-registry
      - Transcript schema: `architecture_only_stubs_filled`, `equivalence_proof_path`,
        `behavioral_regression_count` (must be 0)
      - Anti-overclaim rule: NEVER mark stub as implemented without equivalence test proof
- [ ] Skill registered in `.supervisor/skill-registry.yaml` under SPEC_LITERAL_SKILLS
      with `spec_qname_required: true`, `enforces_transcript: true`, `bootstrap_mode: true`
- [ ] `tests/python/fodt/test_compat_bootstrap.py` skeleton created with at minimum:
      - One test verifying `FodtParagraph` from `models.py` has `.kind`, `.text`, `.spans` attrs
      - One placeholder test for equivalence check (marked `xfail` until spec/ stubs implemented)
- [ ] skill command file added to `command-registry.yaml` in the SPEC_LITERAL_SKILLS group
- [ ] Self-challenge completed (see AGENTS.md Section I)

---

## Artifacts Produced

| Artifact | Path | Visibility | Notes |
|---|---|---|---|
| Skill command file | `.claude/commands/implement-spec-stub.md` | internal | Core deliverable |
| Skill registry entry | `.supervisor/skill-registry.yaml` | internal | Under SPEC_LITERAL_SKILLS |
| Bootstrap test skeleton | `tests/python/fodt/test_compat_bootstrap.py` | internal | Behavioral equivalence baseline |

---

## Artifacts Consumed (Inputs)

| Artifact | Path | Required? |
|---|---|---|
| FODT compat.py bootstrap rule | `src/python/fodt/compat.py` | Required — understand constraints |
| FODT spec/ stubs | `src/python/fodt/spec/` | Required — list of stubs to govern |
| QName registry | `shared/qname-registry/fodt.yaml` (if exists) | Required — spec_qname verification |
| Skill registry template | `.supervisor/skill-registry.yaml` | Required — registration pattern |
| Taskcard template | `taskcards/_template.md` | Reference |

---

## Steps

1. Read `src/python/fodt/compat.py` bootstrap rules in full.
2. Read all 11 spec/ stub files in `src/python/fodt/spec/` to understand their current state.
3. Design skill command file per the allowed/forbidden paths and transcript schema above.
4. Create `.claude/commands/implement-spec-stub.md`.
5. Add skill entry to `.supervisor/skill-registry.yaml` under SPEC_LITERAL_SKILLS.
6. Create `tests/python/fodt/test_compat_bootstrap.py` with behavioral equivalence skeleton.
7. Add `implement-spec-stub` to `.claude/commands/command-registry.yaml` (SPEC_LITERAL_SKILLS group).
8. Run `python tools/supervisor/validate_skill_registry.py --registry .supervisor/skill-registry.yaml`
   to confirm new entry passes schema validation.
9. Complete self-challenge (AGENTS.md Section I).
10. Update this taskcard to `status: complete`.

---

## Completion Record

**Completed by:** [agent-id]
**Completion date:** [ISO-8601]
**Artifacts produced:** [list paths]
**Gaps discovered:** [list G-IDs or "none"]
**Notes:** [any notes for next phase]
