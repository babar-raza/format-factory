# Skills Repeatability Audit
## Run ID: spec-authority-machinery-explosion-20260625-c6b2470

---

## 1. What Repeatability Means Here

A spec authority operation is "repeatable" when:
1. It is registered as a governed skill in `.supervisor/skill-registry.yaml`
2. It has a command file in `.claude/commands/`
3. It produces a transcript (evidence artifact) per execution
4. It can be triggered by the autonomous loop without manual intervention
5. It has idempotency guarantees (running twice produces same result)

---

## 2. Spec Authority Pipeline — Repeatability Status

| Operation | Tool | Registered Skill? | Has Transcript? | Auto-triggerable? | Idempotent? | Status |
|-----------|------|-------------------|-----------------|-------------------|-------------|--------|
| Spec download + hash | `acquire_spec.py` | **NO** | NO | NO | YES | **UNGOVERNED** |
| T3 authorization check | T3 auth workflow | **NO** | NO | NO | YES | **UNGOVERNED** |
| Spec normalization | `spec_normalizer.py` | **NO** | NO | NO | YES | **UNGOVERNED** |
| Fact extraction | `run_extraction_pipeline.py` | **NO** | NO | NO | YES | **UNGOVERNED** |
| Fact verification | `spec_verifier.py` | **NO** | NO | NO | YES | **UNGOVERNED** |
| Requirement pack generation | `requirement_extractor.py` | **NO** | NO | NO | YES | **UNGOVERNED** |
| Authority gate validation | `authority_gate_validation.py` | **NO** | NO | YES (manual) | YES | **UNGOVERNED** |
| Proof graph build | `build_proof_graph_iter003.py` | **NO** | NO | NO | NO | **UNGOVERNED** |
| Pilot rerun (full chain) | manual | **NO** | NO | NO | NO | **UNGOVERNED** |
| Staleness check | `refresh_check.py` | NO (but wired advisory) | NO | YES (Step 0a) | YES | PARTIAL |

---

## 3. Registered Skills (Spec Authority Domain)

Searching `.supervisor/skill-registry.yaml` for spec-authority-related skills:

| Skill Name | Status in Registry | Relevant? |
|------------|-------------------|-----------|
| `rollback-and-recovery` | active | Partially — for authority machinery repair |
| `sal-pipeline-heal` | active | YES — spec authority layer healing |
| `spec-parity-verification` | active | YES — but for code parity, not spec acquisition |
| `scan-residual-bypasses` | active | YES — bypass detection |
| `python-qname-code-reviewer` | active | Partially — reviews QName citations |

**Missing critical skills:**

| Required Skill | Command | Gap |
|----------------|---------|-----|
| `acquire-spec-t3` | `.claude/commands/acquire-spec-t3.md` | T3 authorization + download workflow |
| `normalize-spec` | `.claude/commands/normalize-spec.md` | Run spec_normalizer.py + chunk extraction |
| `extract-spec-facts` | `.claude/commands/extract-spec-facts.md` | Run run_extraction_pipeline.py + verify |
| `verify-spec-facts` | `.claude/commands/verify-spec-facts.md` | Human-in-the-loop fact verification |
| `generate-requirement-pack` | `.claude/commands/generate-requirement-pack.md` | requirement_extractor.py execution |
| `authority-gate-validation` | `.claude/commands/authority-gate-validation.md` | Run authority_gate_validation.py and record result |
| `pilot-rerun-authority` | `.claude/commands/pilot-rerun-authority.md` | Full chain rerun from spec to evidence |
| `test-from-verified-facts` | `.claude/commands/test-from-verified-facts.md` | Generate tests citing FACT-* IDs |
| `product-impl-from-req-pack` | `.claude/commands/product-impl-from-req-pack.md` | Implement code from requirement pack |
| `contradiction-audit-spec` | `.claude/commands/contradiction-audit-spec.md` | Compare implementation to spec facts |

---

## 4. Root Cause of Ungoverned State

**RCA-SKILLS-REPEATABILITY-001**: The spec authority pipeline was built as a one-time manual process for FODS during T3 authorization. No mechanism was established to:
1. Register pipeline steps as skills
2. Generate transcripts per execution
3. Track which formats have completed which pipeline steps
4. Trigger pipeline steps from the autonomous loop

As a result:
- FODS has a complete workbench because someone ran the pipeline manually
- No other format can achieve the same state without repeating the manual process
- If the FODS workbench is lost, there is no automated way to reproduce it

---

## 5. Proposed Skill Registrations

### Priority 1 (Phase A — critical for bypass closure)

**`authority-gate-validation`**
```yaml
name: authority-gate-validation
description: Run authority_gate_validation.py for a target format and record P-level result
command: tools/supervisor/authority_gate_validation.py --format-id {format} --json
output: .local/authority-gate-records/{format}/{date}/gate-result.json
transcript_required: true
idempotent: true
```

### Priority 2 (Phase B — for pilot rerun)

**`pilot-rerun-authority`**
```yaml
name: pilot-rerun-authority
description: Full chain authority rerun for a target format from spec cache to evidence
steps:
  - run_extraction_pipeline.py --format {format}
  - spec_verifier.py --format {format}
  - authority_conveyor.py --format-id {format} --target-level {level}
  - build_proof_graph_iter003.py --format {format}
output: .local/pilot-reruns/{format}/{date}/
transcript_required: true
idempotent: false
```

### Priority 3 (Phase C — governed acquisition)

**`acquire-spec-t3`**
```yaml
name: acquire-spec-t3
description: Complete T3 authorization workflow for a format spec and download source file
steps:
  - Check T3 authorization conditions (6 conditions)
  - Record operator sign-off
  - Run acquire_spec.py --format {format} --execute
output: .local/spec-cache/{format}/{version}/raw/
transcript_required: true
requires_human_signoff: true  # T3 condition 5: operator sign-off
idempotent: true
```

---

## 6. Verdict

**REPEATABILITY STATUS: WEAK**

All spec authority pipeline steps are one-time manual operations with no governed repeatability. 5 minimum skills must be registered before the pipeline can be driven from the autonomous loop. The FODS workbench is the only format with a complete manual pipeline run — and it cannot be automatically reproduced.
