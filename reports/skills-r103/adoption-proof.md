# Adoption Proof (Skills R103 Wave 6)

## 1. Mainstream Adoption

### How Mainstream Product Lanes Use Skill IDs

When a mainstream sprint prompt specifies a product feature (e.g., "Add RenameSheet to FODS"), the governed workflow is:

1. **Sprint prompt names the skill:** `/add-dotnet-object-model-feature`
2. **Agent looks up skill in registry:** `.supervisor/skill-registry.yaml` entry confirms active status
3. **Agent reads command file:** `.claude/commands/add-dotnet-object-model-feature.md` provides exact steps
4. **Agent consumes handoff:** `reports/skills-r103/generated-handoffs/handoff-001-fods-renamesheet.md` provides exact paths
5. **Agent produces transcript:** Written to `reports/skills-r<N>/skill-transcripts/`
6. **Supervisor validates transcript:** `tools/supervisor/validate_skill_transcript.py` confirms schema

### Mainstream Skill-Routing Handoff

```yaml
# Mainstream can route to skills by referencing skill_id in sprint tasks
task:
  description: "Add RenameSheet to FODS .NET product"
  skill_id: add-dotnet-object-model-feature
  handoff_ref: reports/skills-r103/generated-handoffs/handoff-001-fods-renamesheet.md
  validation: transcript must pass validate_skill_transcript.py
```

## 2. Supervisor Adoption

### How Supervisor Grading Rejects Missing Transcripts

The supervisor's `grade_declared_work.py` checks evidence_paths for each work item. If a skill-related work item declares completion but has no transcript file at the declared path, the grader can:

1. Check `evidence_paths` in the work item — if path doesn't exist, grade as INSUFFICIENT_EVIDENCE
2. If transcript exists, validate it with `validate_skill_transcript.py`
3. If validation fails (e.g., missing invocation_id, wrong mode, files outside allowed), grade as OVERCLAIMED

### Supervisor Enforcement Fixture

```yaml
# Supervisor grading rule: skill-related items require transcript
enforcement_rule:
  trigger: work_item.skill_id is not null
  check: transcript file exists at declared evidence_path
  validation: validate_skill_transcript.py returns valid=true
  failure_action: grade as OVERCLAIMED with reason "missing or invalid transcript"
```

## 3. Acceleration Adoption

### How Acceleration Routes Gaps to Skills/Handoffs

The acceleration stream identifies product gaps via `selected-product-gaps.json` and POC target matrix. To route a gap to the skills stream:

1. **Gap identified:** e.g., "FODS needs RenameSheet"
2. **Promote to taskcard:** `/promote-gap-to-taskcard` creates `taskcards/TC-FODS-RENAMESHEET-001.md`
3. **Generate handoff:** `/generate-execution-handoff` creates the handoff with exact paths
4. **Queue for execution:** Handoff placed in `reports/skills-r<N>/generated-handoffs/`
5. **Mainstream consumes:** Next mainstream sprint picks up the handoff via skill_id routing

### Acceleration Integration Snippet

```python
# Acceleration router pseudo-code
def route_gap_to_skill(gap):
    skill_id = SKILL_MAP.get(gap['product_track'])  # e.g., commercial_dotnet -> add-dotnet-object-model-feature
    if skill_id and skill_id in registry['active']:
        return generate_handoff(skill_id, gap)
    else:
        return flag_as_unroutable(gap)
```

## Evidence Files

- Mainstream routing: `reports/skills-r103/adoption-handoffs/mainstream-skill-routing.yaml`
- Supervisor enforcement: `reports/skills-r103/adoption-handoffs/supervisor-transcript-enforcement.yaml`
- Acceleration integration: `reports/skills-r103/adoption-handoffs/acceleration-gap-routing.yaml`
