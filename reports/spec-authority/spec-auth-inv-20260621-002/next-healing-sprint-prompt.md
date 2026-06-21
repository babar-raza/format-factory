# Next Healing Sprint Prompt — Spec Authority Layer
**Source investigation:** spec-auth-inv-20260621-002
**Date:** 2026-06-21
**Sprint identity:** sal-healing-sprint-20260621-001 (or next available)

This prompt is based on confirmed live findings. Do not execute from memory.
Read this prompt in full before taking any action.

---

## Context: What Was Found

The Specification Authority Layer (SAL) is a real, partially working subsystem — NOT purely advisory.
Key strengths discovered:
- FODS spec is cached with SHA-256 provenance (92cfe64…)
- 78 hand-curated FACT-FODS-001 to FACT-FODS-078 have exact spec line citations
- spec_verifier.py works correctly (14/14 adversarial tests PASS)
- V13, V47 governance validators are BLOCKING and wired
- 191 SAL tests collected; 13 adversarial + 13 traceability tests PASS

Key failures discovered:
- **CRITICAL**: `sal_master_runner.py --format zst` overwrites the all-format `sal-facts-latest.json`, degrading it from 22 formats to 1
- **HIGH**: V37 and V47 read from different paths (split-brain)
- **HIGH**: spec_verifier.py not called in production SAL runner (only in tests)
- **HIGH**: 8/10 registered formats have no spec text (sha256_snapshot=null)
- **HIGH**: No proof graph instantiated; fact-product traceability is advisory only
- **MEDIUM**: 4,913 auto-extracted EX facts mixed with 78 behavioral facts in same coverage bucket

---

## Sprint Scope

This sprint must repair the top 4 gaps (P0/P1) and run the ZST pilot.
Do NOT implement large new features. Keep repairs narrow, reversible, testable.

---

## Required Root Cause Repairs

### RC-1: Fix sal-facts-latest.json overwrite (GAP-SA-NEW-001) — MANDATORY

**File:** `tools/specification-authority-layer/sal_master_runner.py`

In `run_sal_pipeline()`, add a guard so that when `formats` is a subset of all formats
(i.e., single-format run), the function does NOT write `sal-facts-latest.json`.

Allowed paths:
- Single-format `--format zst` writes `sal-facts-zst.json` only
- All-format `--all` writes `sal-facts-latest.json` + per-format files

Forbidden:
- Do NOT change existing test behavior
- Do NOT change the output JSON schema

**Verification command:**
```bash
python tools/specification-authority-layer/sal_master_runner.py --all
python tools/specification-authority-layer/sal_master_runner.py --format zst
python -c "import json; d=json.loads(open('.local/sal-output/sal-facts-latest.json').read()); \
           assert len(d['results']) >= 20; print('PASS')"
```

---

### RC-2: Canonicalize V37 and V47 to same path (GAP-SA-NEW-002) — MANDATORY

**File:** `tools/supervisor/governance_validators.py`

Current state:
- V37 `validate_spec_fact_authority_chain` reads `.local/sal-output/sal-facts-latest.json`
- V47 `validate_spec_fact_refs_in_sal_output` reads `.local/spec-cache/sal-facts-latest.json`

Required: both use `.local/sal-output/sal-facts-latest.json` (the canonical output directory).
After RC-1 fixes the overwrite, this is the authoritative path.

Also update `autonomous_cycle.py` Step 0a to write to `sal-output` and ensure
`.local/spec-cache/sal-facts-latest.json` is either removed or symlinked.

**Verification command:**
```bash
grep -n "sal.facts.latest" tools/supervisor/governance_validators.py | \
  grep -E "V37|V47|validate_spec_fact_authority|validate_spec_fact_refs_in_sal" -A2
# Must show same path for both
```

---

### RC-3: Wire spec_verifier into SAL runner (GAP-SA-NEW-003) — REQUIRED

**File:** `tools/specification-authority-layer/sal_master_runner.py`

In `_load_workbench_verified_facts()`, after loading facts from YAML:
1. Import `verify_requirements` from `spec_verifier` (lazy import to avoid circular)
2. Filter loaded facts through `verify_requirements()`
3. Exclude ANTI_BYPASS_REJECTED facts
4. Log WARN for UNVERIFIABLE facts (but do not exclude them — they are still workbench-curated)
5. Keep VERIFIED facts as-is

This must NOT break existing behavior for facts that already have valid source_id and spec text.

**Verification:**
```bash
python -m pytest tests/specification-authority-layer/test_sal_verifier_adversarial.py -v
# Must still be 14/14 PASS
# Plus new test: inject no-source_id fact into test workbench → assert excluded
```

---

### RC-4: Fix test_gap_int_002 PBM failure (GAP-SA-NEW-001 consequence) — REQUIRED

After RC-1 and RC-2, re-run `test_gap_int_002_product_source_fact_refs.py`.
The PBM failure should resolve because `sal-facts-latest.json` will again have all 22 formats.

If PBM facts (FACT-PBM-001, FACT-PBM-002) are still not in the all-format output:
- Check `sal_master_runner.py` for PBM format registration
- Ensure PBM/PGM/PPM formats are included in `--all` run

**Verification:**
```bash
python -m pytest tests/specification-authority-layer/test_gap_int_002_product_source_fact_refs.py -v
# Must be 13/13 PASS
```

---

## Pilot Rerun: ZST

Run the ZST pilot as defined in `pilot-rerun-plan.md`:

1. `python tools/spec-cache/refresh_check.py --verbose` — verify ZST not stale
2. `python tools/specification-authority-layer/run_fact_verification.py --format zst` — verify facts against spec
3. `python tools/specification-authority-layer/sal_master_runner.py --format zst --from-cache-only` — emit ZST facts
4. Assert all 15 FACT-ZST-* facts have non-null `source_id`
5. Run deterministic rerun: run twice and compare fact QNames
6. Run anti-bypass test: inject AI-only fact → assert ANTI_BYPASS_REJECTED

---

## Allowed Paths

- Modifying `sal_master_runner.py` (minimal, surgical)
- Modifying governance validator paths in `governance_validators.py`
- Adding spec_verifier call to `_load_workbench_verified_facts`
- Running existing tests and pilot
- Creating test fixtures for new tests

---

## Forbidden Paths

- Do NOT implement the proof graph (FPR-1) — that is Phase 2
- Do NOT add V48 governance validator (that is P1 — next sprint)
- Do NOT add fact_category schema changes (that is P2)
- Do NOT delete or modify any workbench YAML files
- Do NOT change the SAL output JSON schema in ways that break consumers
- Do NOT introduce embeddings, vector stores, or AI calls
- Do NOT overwrite old investigation reports

---

## Required Tests

After repairs:

1. `python -m pytest tests/specification-authority-layer/ --timeout=300 -q`
   → Target: ≥190/191 PASS

2. `python -m pytest tests/supervisor/test_governance_validators.py -v --timeout=60`
   → All V13, V37, V47 tests must PASS

3. ZST pilot steps 1-6 (per pilot-rerun-plan.md)

4. Single-format overwrite protection test (new test for RC-1)

---

## Evidence Required

Submit these files in the sprint evidence declaration:

| Evidence | Path |
|----------|------|
| sal-facts-latest.json snapshot (22 formats) | `.local/sal-output/sal-facts-latest.json` |
| ZST facts with source_id | `.local/sal-output/sal-facts-zst.json` |
| test_gap_int_002 results (13/13) | Test output |
| SAL test suite results | Test output |
| Governance validator results | Test output |
| ZST pilot step outputs | `reports/spec-authority/sal-healing-sprint-20260621-001/evidence/` |

---

## Stop Gates

**STOP if any of these occur:**
1. Modifying workbench YAML files would alter verified fact content (not allowed)
2. A repair requires schema changes incompatible with existing consumers
3. spec_verifier call causes >5% of workbench facts to be rejected (indicates broader data quality issue needing investigation, not a quick fix)
4. Any governance validator that was previously PASS now FAILs due to a repair

**CONTINUE (do not stop) if:**
- Tests time out at 300s — increase timeout for SAL tests; they are slow due to large workbench file
- ZST pilot step 2 shows ≥10% not_found facts — log as finding but continue
- autonomous_cycle step 0a produces exit 3 — log and continue

---

## Final Verdict Format

```
HEALING_SPRINT_VERDICT:
  RC_1_sal_overwrite_fixed: RESOLVED | PARTIAL | UNRESOLVED
  RC_2_validator_paths_aligned: RESOLVED | PARTIAL | UNRESOLVED
  RC_3_spec_verifier_wired: RESOLVED | PARTIAL | UNRESOLVED
  RC_4_gap_int_002_13_13: PASS | FAIL
  PILOT_ZST_COMPLETE: PASS | PARTIAL | FAIL
  SAL_TESTS: N/191 PASS
  GOVERNANCE_TESTS: N/M PASS
  OVERALL: HEALING_COMPLETE | PARTIAL_HEALING | HEALING_BLOCKED
```

Report result inline before closing the sprint.
Do NOT claim HEALING_COMPLETE unless RC_1, RC_2, RC_3 are all RESOLVED.
