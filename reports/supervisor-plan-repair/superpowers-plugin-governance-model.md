# Superpowers Plugin Governance Model

Sprint: FORMAT-FACTORY-SUPERVISOR-PRODUCT-FIRST-TRAFFIC-CONTROLLER-REPLAN-AND-STREAM-LOCAL-CLOSURE-001

## Current Status

Superpowers: ABSENT — no `.claude-plugin/` directory detected.

## Install Requirements

Before any Superpowers installation:
1. Path impact analysis — identify all files the plugin can mutate
2. Rollback plan — document how to fully remove
3. SessionStart injection review — verify plugin does not inject uncontrolled prompts
4. Skill-registry conflict check — confirm no overlap with `skill-registry.yaml` entries

## Governance Rules

- Plugins may not silently override skill-registry.yaml
- SessionStart injection requires explicit review and approval
- Plugin output is advisory, not authoritative
- Installation requires human approval (not autonomous)

## Current Sprint Verdict: SUPERPOWERS_NOT_INSTALLED_EVALUATE_ONLY
