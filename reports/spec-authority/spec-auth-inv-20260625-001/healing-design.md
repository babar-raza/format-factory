# SAL Healing Design
**Mission:** spec-auth-inv-20260625-001
**Date:** 2026-06-25

## Priority 1 Healing Actions

### H1: V13 ImportError Hardening (RC-003)
**File:** `tools/supervisor/governance_validators.py` — `validate_spec_fact_refs_wired()`
**Change:** Replace `except ImportError: return WARN` with `except ImportError: return FAIL` + clear error message
**Effort:** 5 LOC
**Risk:** LOW — makes existing gate stricter (was previously silently degrading)
**Test:** Add test proving V13 returns FAIL (not WARN) when spec toolchain unavailable

### H2: CSV SAL Expansion (RC-002)
**File:** `.local/spec-cache/sal-facts-csv.json`
**Change:** Expand from 2 facts to ~30+ facts from RFC 4180 ABNF grammar:
- Record structure (CRLF-delimited)
- Field structure (comma-delimited)
- Optional header row
- Quoting rules (double-quote escape)
- Null field semantics
**Effort:** 2 hours (manual extraction from RFC 4180 text)
**Risk:** MEDIUM — new facts must not break V47 validator

### H3: Gnumeric + ABW SAL Parsers (RC-001)
**File:** `tools/spec/workbench/gnumeric_spec_parser.py` (NEW)
**Spec source:** GNOME Gnumeric XML format documentation
**Expected facts:** ~50-100 (element/attribute level)
**Effort:** HIGH — requires reading and parsing spec docs
**Risk:** MEDIUM — new parser code

## Priority 2 Healing Actions

### H4: Evidence Schema Provenance Fields (RC-004)
**File:** `docs/automation/supervisor-worker-contract.md`
**Change:** Add optional fields: `chunk_id`, `section_ref`, `page_ref` to `evidence_artifacts` schema
**Effort:** LOW — documentation only + schema update

### H5: SAL Advisory Integration (RC-005)
**File:** `tools/supervisor/autonomous_cycle_extensions.py`
**Change:** Add SAL advisory step after Step 0a (spec-cache refresh)
**Effort:** LOW — ~20 LOC in extensions file (avoids LOC cap on autonomous_cycle.py)

## Priority 3 Healing Actions

### H6: Capability Compiler Spec-Grounding (RC-006)
**File:** `tools/capability_layer/capability_feature_compiler.py`
**Change:** Require `spec_fact_ref` on every gap-to-work-item translation
**Effort:** MEDIUM — requires SAL fact linkage for all 1,132 gaps

## Sequencing

```
H1 (V13 hardening) → H2 (CSV facts) → H5 (SAL advisory)
                                     ↘ H4 (schema provenance)
H3 (parsers) → H6 (compiler grounding)
```
