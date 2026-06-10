# Skills Compatibility

**Sprint:** FORMAT-FACTORY-ACCELERATION-HARDENING-IV-AND-CONSUMPTION-CONTRACT-001
**Date:** 2026-06-04

## Skills Classification

**Result:** ACCELERATION_CONSUMABLE_WITH_LIMITATIONS

All 4 packets have `skills_handoff_compatibility.compatible: true` with the limitation
that Skills normalization is required before any registry entry.

## What Skills May Do With Packets

| Action | Allowed? |
|--------|----------|
| Read packet test_plan_path and review test plan | YES |
| Read source_patterns_path for skill pattern inspiration | YES |
| Use implementation_design_path as advisory context | YES |
| Add skills directly to skill-registry.yaml from packet | NO |
| Treat packet content as authoritative skill specification | NO |
| Close Skills taskcards based on packet | NO |

## Skills Normalization Path

```
Acceleration packet → Skills reads advisory content
        ↓
Skills extracts relevant patterns/proposals
        ↓
Skills creates local wrapper with:
  allowed_files: [...]
  forbidden_files: [...]
  validation_command: [...]
  evidence_rule: [...]
        ↓
Skills adds to skill-registry.yaml
        ↓
Skill available for authorized use
```

## Limitations

- agentic_low_risk management was skipped (no model) — sprint management advisory only
- Source patterns may be sparse for some formats (corpus_empty flag)
- Implementation designs are ai_draft — Skills worker must validate before implementation

## Current State (Post-Hardening)

All 4 packets: `skills_handoff_compatibility.compatible=true`.
Skills classification: **ACCELERATION_CONSUMABLE_WITH_LIMITATIONS**
(limitation: normalization required; agentic_low_risk management skipped)
