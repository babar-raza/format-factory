# Next Skills Agent Prompt (R109)

## MODE: SKILLS STREAM — LIVE HANDOFF EXECUTION AND AUTONOMOUS CYCLE STREAM ISOLATION

## Sprint ID
FORMAT-FACTORY-SKILLS-R109-LIVE-HANDOFF-EXECUTION-AND-STREAM-ISOLATION-001

## Stream: skills

## Read First
1. `reports/skills-r108/final-adversarial-independent-verification.md`
2. `tools/supervisor/grade_declared_work.py` (transcript boost at line 148-155)
3. `tools/supervisor/validate_adoption_compliance.py` (new in R108)
4. `tools/supervisor/autonomous_cycle.py` (stream tagging needed)
5. `.supervisor/skill-registry.yaml`
6. `reports/skills-r108/adoption-packages/mainstream-adoption.yaml`

## R108 Carry-Forward
- Transcript-grade boost wired: transcript_validation.all_valid → ACCEPTED_VERIFIED
- Adoption compliance validator: validate_adoption_compliance.py (7 tests)
- Manifest path repair: decl_evidence_root fallback in build_declaration_review_package.py
- Anti-skip repair: raw-log type accepts hyphen and underscore
- 3 simulation transcripts validated (dry-run only — LIVE not yet executed)
- 3 adoption packages published (mainstream/supervisor/acceleration YAML)
- 5 sample outputs demonstrating stream-tagged format
- 172 total supervisor tests (28 new in R108)

## Tasks

### Task 1: Execute First LIVE Handoff Through Mainstream
- Pick one of: FODS RenameSheet, Netpbm ExtractChannel, FODT roundtrip, Python API roundtrip
- Execute the handoff skill (mode: "live") with actual src file changes
- Generate LIVE transcript JSON and validate
- This is the #1 priority — R108 simulations proved the pipeline, R109 must produce LIVE proof

### Task 2: Wire Stream Isolation into autonomous_cycle.py
- Step 6 (lines 274-334): Tag outputs with stream_id from declaration
- Option A: Write to `reports/supervisor/{stream_id}/` subdirectory
- Option B: Prefix output files with stream name
- Tests: stream detection, output path generation, no cross-stream contamination

### Task 3: Wire Adoption Compliance into autonomous_cycle Pipeline
- Add Step 4b: Call validate_adoption() on declaration after grading
- Include adoption compliance result in the final cycle output
- Tests: adoption check integrated into cycle

### Task 4: Registry Promotion Decision
- Re-evaluate deferred skills: record-lane-execution, check-mcp-status
- Lane execution ledger now exists (R108) — record-lane-execution has demand
- If demand proven, promote to active with command file

### Task 5: Evidence Quality Score Improvement
- With transcript boost active, R109 items with valid transcripts should get ACCEPTED_VERIFIED
- Target: evidence_quality_score >= 0.4 (at least 40% VERIFIED)
- Include transcripts in evidence_paths for all product work items

## Hard Quota
- 1 LIVE handoff transcript (validated, not simulation)
- Stream isolation in autonomous_cycle.py with tests
- Adoption compliance wired into cycle pipeline
- Registry promotion decision documented
- evidence_quality_score >= 0.4

## Forbidden Paths
- `registry/format-registry.yaml`
- `plans/master-plan.md`
- Direct `src/python/**` or `src/net/**` edits (delegate to Mainstream)
