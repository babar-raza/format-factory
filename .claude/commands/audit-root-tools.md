# /audit-root-tools

Audit ad-hoc root-level scripts in `tools/supervisor/` to determine if each script should be:
- **REGISTERED**: migrated to a named skill entry in `.supervisor/skill-registry.yaml`
- **QUARANTINED**: moved to `.local/quarantine/` (one-time scripts, test artifacts)
- **KEPT**: utility scripts with clear ongoing purpose that don't need skill registration
- **REJECTED**: deleted (pure test artifacts with no ongoing value)

## Protocol

1. List all `.py` files in `tools/supervisor/` that are NOT referenced by any existing skill in `.supervisor/skill-registry.yaml`
2. For each unregistered script, determine purpose by reading first 30 lines
3. Apply mutation guard: if script matches pattern `close_*.py`, `scan_*.py`, or `adhoc_*.py` → classify as QUARANTINE candidate
4. Produce an audit register at `reports/skill-audit/root-tools-audit-{date}.yaml` with classification for each file
5. For REGISTERED candidates, create a draft skill entry block
6. For QUARANTINED candidates, confirm with evidence path before moving

## Output Fields (per script)

```yaml
- script: tools/supervisor/example.py
  classification: REGISTERED | QUARANTINED | KEPT | REJECTED
  reason: "one-line explanation"
  skill_draft: |   # only for REGISTERED
    skill_id: example
    status: active
    ...
```

## Acceptance Criteria

- All scripts in `tools/supervisor/` are either registered in skill-registry.yaml OR have a documented disposition in the audit register
- No script classified as QUARANTINE is left in tools/supervisor/ without evidence
- Audit register written to `reports/skill-audit/root-tools-audit-{date}.yaml`
- Zero ad-hoc mutations allowed without skill invocation proof

## Mutation Guard

This skill enforces the mutation guard: any modification to `tools/supervisor/*.py` must be traceable to a registered skill. Scripts that are ad-hoc mutations without skill attribution are flagged as `MUTATION_GUARD_VIOLATION`.

**Skill ID:** audit-root-tools
**Source Plan:** twinkly-gliding-thimble / TC-SFE2-003
**Sprint:** SKILL-FIRST-002
