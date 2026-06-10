# Acceleration R107 Sprint Prompt

## Sprint ID
FORMAT-FACTORY-ACCELERATION-R107-PIPELINE-ORCHESTRATOR-AND-STREAM-QUALITY-CAMPAIGN-001

## Mission
Advance the acceleration tooling from validated individual tools to a pipeline orchestrator that chains gap-selection → anti-skip → package-identity → prompt-quality → declaration-review in a single command.

## Lane A: Repair
- Fix any R106 anti-skip false positives identified during R106 closeout
- Address any evidence_quality_score violations that surfaced

## Lane B: Pipeline Orchestrator
- Create `tools/supervisor/pipeline_orchestrator.py`
- Chain: validate_declaration → inspect → grade → anti-skip → package-identity → prompt-quality
- Single entry point for full quality pipeline

## Lane C: Anti-Skip Advancement
- Add detector 15: `detect_stale_evidence_manifest` (manifest timestamp vs sprint date)
- Add detector 16: `detect_missing_changed_files` (declaration changed_files not on disk)

## Lane D: Package Identity Hardening
- Add global-state/ prefix validation to package identity validator
- Ensure R105 restructuring (global-state/ vs supervisor/) is enforced

## Evidence Closeout
Write evidence-declaration.yaml and run autonomous-cycle.
Build declaration review package ZIP.

## File Boundaries
- ALLOWED: tools/supervisor/*, tests/supervisor/acceleration/*, reports/acceleration-r107/*
- FORBIDDEN: src/net/*, src/python/*, tests/net/*, tests/python/*
