# Acceleration Adoption Checklist (Skills R106) -- Enforcement Gates

This checklist replaces the R105 advisory version. Every gate is enforced.
The Acceleration stream MUST NOT edit product source directly -- all source changes
flow through Mainstream via governed skill handoffs.

---

## GATE A-01: Gap Selection from Matrix (REQUIRED)

- **What:** Select gaps exclusively from `product-capability-matrix/poc-targets.yaml`.
- **Check:** Generated handoff YAML contains a `gap_id` field that matches an entry in the matrix.
- **Validator:** Handoff YAML parsed; `gap_id` cross-referenced against `poc-targets.yaml` entries.
- **Command:** Manual check or future `validate_handoff.py` (not yet implemented -- manual enforcement via supervisor review).
- **Failure:** OVERCLAIMED -- "Handoff generated without valid matrix gap_id reference."
- **Responsible:** Acceleration worker.

| Condition | Pass/Fail |
|-----------|-----------|
| `gap_id` present and found in `poc-targets.yaml` | PASS |
| `gap_id` present but not in matrix | FAIL (OVERCLAIMED) |
| `gap_id` absent | FAIL (OVERCLAIMED) |

---

## GATE A-02: Skill Routing (REQUIRED)

- **What:** Identify the correct `skill_id` for the gap's `product_track` using the registry.
- **Check:** Handoff YAML contains `skill_id` matching an active entry in `.supervisor/skill-registry.yaml`.
- **Validator:** Cross-reference `skill_id` against registry. Unregistered skill_id fails.
- **Routing map (from registry):**

| Product Track | API Skill | Feature Skill |
|--------------|-----------|---------------|
| `commercial_dotnet` | `add-dotnet-api` | `add-dotnet-object-model-feature` |
| `foss_python` | `add-python-api` | `add-python-object-model-feature` |
| `cross_product` | `add-dogfood-export` | `add-same-format-writer-feature` |
| `testing` | `add-roundtrip-test` | -- |
| `packaging` | `package-install-proof` | `add-installed-package-example` |

- **Failure:** OVERCLAIMED -- "Gap executed without skill routing."
- **Responsible:** Acceleration worker.

---

## GATE A-03: Handoff Generation with Required Fields (REQUIRED)

- **What:** Use `/generate-execution-handoff` to create a structured handoff YAML.
- **Check:** Handoff YAML contains all `required_handoff_fields` defined in the target skill's registry entry.
- **Validator:** YAML lint + field presence check against `skill-registry.yaml` `required_handoff_fields`.
- **Required output fields (minimum):**
  - `skill_id`
  - `format_id`
  - `exact_source_paths`
  - `exact_test_paths`
  - `ledger_entry_path` (for src-editing skills)
  - `focused_test_command`
- **Failure:** Missing required fields => REWORK_REQUIRED -- "Handoff generated but missing required fields."
- **Responsible:** Acceleration worker.

---

## GATE A-04: No Direct Source Edits (REQUIRED -- HARD BOUNDARY)

- **What:** Acceleration stream MUST NOT modify files under `src/net/` or `src/python/`.
- **Check:** `inspect_declared_evidence.py` scans all evidence paths and transcript `actual_files_changed` for acceleration-tagged work items. Any `src/net/` or `src/python/` path triggers immediate rejection.
- **Validator:** Built into inspection pipeline. Supervisor gate S-07 enforces this from the grading side.
- **Failure:** REJECTED -- "Acceleration stream edited product source directly. Route through Mainstream via handoff."
- **Responsible:** Acceleration worker (must not edit); Supervisor grader (enforces).

| Condition | Pass/Fail |
|-----------|-----------|
| No `src/` paths in evidence | PASS |
| `src/` path found in evidence_paths | FAIL (REJECTED) |
| `src/` path found in transcript actual_files_changed | FAIL (REJECTED) |

---

## GATE A-05: Handoff Placement (REQUIRED)

- **What:** Place generated handoffs in `reports/skills-r{N}/generated-handoffs/` for Mainstream consumption.
- **Check:** Handoff file exists at the standard path; referenced in evidence declaration `evidence_paths`.
- **Validator:** `inspect_declared_evidence.py` confirms file existence.
- **Failure:** REWORK_REQUIRED -- "Handoff not placed in standard directory."
- **Responsible:** Acceleration worker.

---

## GATE A-06: Delegation Tracking (REQUIRED)

- **What:** Track which handoffs have been consumed by Mainstream in subsequent sprints.
- **Check:** Evidence declaration references the handoff and notes consumption status.
- **Validator:** Manual review in supervisor grading (future: consumption tracker tool).
- **Failure:** Not gate-blocking, but unclaimed handoffs are flagged as forward work items.
- **Responsible:** Acceleration worker (generates); Mainstream worker (consumes); Supervisor (tracks).

---

## Allowed vs Forbidden Actions

### Allowed (Acceleration stream)
- Generate execution handoffs (`/generate-execution-handoff`)
- Promote gaps to taskcards (`/promote-gap-to-taskcard`)
- Select POC gaps (`/select-poc-gap`)
- Update capability matrix (`/update-capability-matrix`)
- Write reports and planning documents

### Forbidden (route through Mainstream)
- Edit `src/net/**` -- REJECTED
- Edit `src/python/**` -- REJECTED
- Create new test files under `tests/` -- delegate to Mainstream via handoff
- Modify `.csproj` or `pyproject.toml` build files -- delegate to Mainstream

---

## Quick Reference: Validator Commands

```
# Validate handoff YAML (manual -- check required fields)
python -c "import yaml; h=yaml.safe_load(open('<handoff.yaml>')); assert 'skill_id' in h; assert 'gap_id' in h; print('PASS')"

# Check gap_id against matrix
python -c "import yaml; m=yaml.safe_load(open('product-capability-matrix/poc-targets.yaml')); print([e for e in m if e.get('gap_id')=='<GAP_ID>'])"

# Validate commands (pre-sprint)
.local/venv/Scripts/python tools/supervisor/validate_claude_commands.py

# Full grading (supervisor runs this -- enforces A-04)
.local/venv/Scripts/python tools/supervisor/grade_declared_work.py --inspection <i> --declaration <d> --output-dir <o>
```
