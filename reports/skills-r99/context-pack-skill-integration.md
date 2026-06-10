# Train J: Context Pack and Next-Sprint Skill Integration Report
Sprint: FORMAT-FACTORY-SKILLS-R99-SKILL-REGISTRY-GOVERNED-EXECUTION-PARALLEL-MEGA-TRAIN-001
Date: 2026-06-03

## Context Pack Integration

The context pack (`tools/supervisor/build_context_pack.py`) already includes:

| Feature | Status | Location |
|---------|--------|----------|
| Skill IDs listed | YES | `read_skill_registry()` at line 148 |
| Active skill count | YES | `active_skills` field |
| Source-edit handoff requirement | YES | `source_edits_require_handoff` |
| Ledger requirement | YES | `ledger_required` |
| Command paths | IMPLICIT | Via skill_id → command mapping in registry |

### Output in context-pack.md

```
## Skill Registry
Skills: add-dotnet-api, add-python-api, add-dogfood-export, ...

## Governance
- Source edits require governed skill or handoff: True
- Product-code ledger required: True
```

## Next-Sprint Prompt Integration

The next-sprint generator (`tools/supervisor/generate_next_worker_prompt.py`) includes:

| Feature | Status | Location |
|---------|--------|----------|
| Skill registry reference | YES | Line 549, 611, 631 |
| Ledger reference | YES | Line 550, 612, 632 |
| No ad-hoc src edit rule | YES | Line 549 |
| Per-product gap → skill mapping | YES | Lines 600-634 (product items reference SKILL_REGISTRY_PATH) |

### Generated Prompt Contains

```
- No ad-hoc src/ edits: use .supervisor/skill-registry.yaml or a generated execution handoff.
- Any src/ edit requires an entry in reports/r90/product-code-change-ledger.json.
```

Each product work item says:
```
Select work from .local/supervisor/selected-product-gaps.json;
use .supervisor/skill-registry.yaml;
record any src edit in reports/r90/product-code-change-ledger.json.
```

## Gap-to-Skill Mapping

The `tools/supervisor/choose_skill_or_handoff.py` classifier maps gaps to skills:

| Gap Type | Skill/Decision |
|----------|---------------|
| dogfood/export | governed-dogfood-export |
| dependency/offline resolution | governed-dependency-resolution-review |
| writer not implemented / write_ppm | governed-product-capability-implementation |
| installed_workflow / self-contained install | governed-installed-workflow-verification |
| approval / gate 8 / gate 11 / push | EXTERNAL_GATE_ESCALATION |
| anything else | GOVERNED_HANDOFF_REQUIRED |

## Conclusion

The context pack and next-sprint generators are already skill-aware. Every generated sprint prompt:
1. Lists active skills by ID
2. References the skill registry path
3. Requires ledger entries for src edits
4. Directs workers to select work from product gaps and use governed skills
5. Classifies gaps deterministically via choose_skill_or_handoff.py
