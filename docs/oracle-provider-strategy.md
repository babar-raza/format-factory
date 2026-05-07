# Oracle Provider Strategy

**Document type:** Policy / Architecture
**Phase available:** Phase 3+
**Created:** run037 (2026-05-07)
**Visibility:** internal

---

## 1. Purpose

This document defines the oracle provider abstraction layer for the format-factory acquisition pipeline. An "oracle provider" is any external tool capable of performing authoritative format processing (parsing, conversion, or export) that serves as the reference implementation for comparing against our own parser output.

The abstraction exists because:

1. Different formats require different oracle tools (LibreOffice for ODF/OOXML, specialized tools for other formats).
2. The pipeline needs a consistent mechanism to discover, validate, and invoke oracle providers across formats.
3. Future formats must not require redesigning the oracle toolchain from scratch.
4. The registry gives operators a single place to see what oracle dependencies exist across all active formats.

---

## 2. Architecture

```
tools/oracle/
  provider_registry.yaml          ← Single source of truth for oracle providers
  validate_oracle_environment.py  ← Discovery and readiness check tool
  oracle_common.py                ← FODS-specific shared constants (see Note)
  preflight_oracle.py             ← FODS Gate 6 preflight (uses oracle_common)
  run_fods_oracle.py              ← FODS Gate 6 oracle execution
  compare_fods_oracle.py          ← FODS Gate 6 comparison
  summarize_oracle_results.py     ← FODS Gate 6 summary
  README.md                       ← Oracle toolset overview
```

**Note on oracle_common.py:** This module contains FODS-specific constants and path
models. Future formats will have their own `oracle_common_<format>.py` or an extended
provider-aware version of oracle_common. The `validate_oracle_environment.py` tool
operates at the registry level and is format-independent.

---

## 3. Provider Registry (`provider_registry.yaml`)

The registry is a YAML file with two top-level sections:

### 3.1 `providers`

Each provider entry defines:

| Field | Description |
|---|---|
| `provider_id` | Unique stable identifier (e.g. `libreoffice`) |
| `display_name` | Human-readable name |
| `provider_type` | `desktop-application`, `cli-tool`, `api-service`, `library` |
| `version_minimum` | Minimum acceptable version |
| `version_recommended` | Recommended version for reproducibility |
| `license` | SPDX identifier |
| `discovery.env_var` | Environment variable override (highest priority) |
| `discovery.binary_names` | Names to check in PATH |
| `discovery.standard_paths` | Absolute paths to check (per-platform) |
| `headless_flag` | Flag for non-interactive invocation |
| `convert_flag` | Flag for format conversion |
| `version_flag` | Flag to retrieve version string |
| `acquisition_pack` | Path to acquisition pack with installation guide |
| `status` | `approved`, `experimental`, `deprecated` |

### 3.2 `format_provider_assignments`

Each format key maps to:

| Field | Description |
|---|---|
| `gate` | Gate number where the oracle runs |
| `approved_providers` | List of `provider_id` values allowed for this format |
| `fallback_providers` | Optional fallback if primary is unavailable (may be empty) |
| `blocker_report` | Path to blocker report (if gate is currently blocked) |
| `installation_checklist` | Path to operator installation guide |
| `current_status` | Current gate status (updated each run) |

---

## 4. Provider Discovery Priority

For each provider, `validate_oracle_environment.py` checks in this order:

1. **Environment variable** (`FORMAT_FACTORY_SOFFICE` for LibreOffice, etc.) — highest priority, explicit override for non-standard installation locations.
2. **Binary names in PATH** — checks standard OS path resolution.
3. **Standard paths** — checks well-known installation locations for each platform.

The first match wins. If no match is found, the provider is reported as `NOT FOUND`.

---

## 5. Governance Rules for Oracle Providers

### 5.1 Adding a New Provider

To add a new oracle provider:

1. Add a provider entry to `tools/oracle/provider_registry.yaml`.
2. Add the provider ID to the `approved_providers` list for the target format.
3. Create or update the acquisition pack for the format (`acquisition-packs/<format>/oracle-installation-checklist.md`).
4. Update `docs/gates.md` to document the oracle provider requirement for the gate.
5. Update the master plan (Section 6 and the relevant run entry).
6. Log a decision record (DEC-XXX) for the new provider addition.

### 5.2 Provider Status

- `approved`: Reviewed, tested, and cleared for use in oracle gates.
- `experimental`: Under evaluation. May be used for exploratory work but not for gate approval evidence.
- `deprecated`: No longer recommended. Must be replaced before the next gate execution.

Only `approved` providers may produce evidence counted toward gate passage.

### 5.3 Version Requirements

If a provider's version cannot be determined (e.g., binary found but `--version` fails), the provider is considered `FOUND (version unknown)` and may still be used. The oracle execution output should include the version string in its output artifacts.

If the discovered version is below `version_minimum`, the agent must log a gap before proceeding with oracle execution.

### 5.4 Fallback Providers

Fallback providers (in `fallback_providers`) may be used only if:
1. The primary provider is not found.
2. The fallback is independently approved for the format.
3. The gate documentation explicitly permits the fallback.

FODS Gate 6 currently has no approved fallback (only LibreOffice is approved).

---

## 6. Current Oracle Provider Status (as of run040)

| Format | Gate | Primary Provider | Status | Preflight Runs |
|---|---|---|---|---|
| FODS | 6 | LibreOffice | `oracle_blocked_missing_tool` — LibreOffice not installed | 6 FAIL (run035/036/037/038/039/040) |

LibreOffice has not been discovered on the dev machine across six consecutive runs (run035, run036, run037, run038, run039, run040). The operator must install LibreOffice per `acquisition-packs/fods/oracle-operator-handoff.md` (most complete operator instructions, run038) before TC-0026 can execute.

**Harness self-test added run038:** `tools/oracle/self_test_oracle_harness.py` validates the compare/summarize pipeline using synthetic CSV fixtures — no LibreOffice required. Result: `ORACLE_HARNESS_SELF_TEST: PASS 4/4`. Label: `HARNESS_SELF_TEST_ONLY` — this is **not** Gate 6 evidence and does not replace the oracle preflight.

**Current-state consistency tool added run039, strengthened run040:** `tools/evidence/check_current_state_consistency.py` validates that "Latest commit" references in master-plan match actual git HEAD, and adds 7 additional checks (memory/09 commit, registry gate_6 not approved, FODT candidate-only invariants, pack.yaml gate_6 not approved). Result: `CURRENT_STATE_CONSISTENCY: PASS`.

**Clean-git loophole closed run040:** `validate_evidence_bundle.py` and `build_evidence_bundle.py` now reject dirty git-status-final.txt even when `require_clean_git: false` in contract, unless `emergency_blocker_bundle: true` is set. New negative tests (6/6 PASS).

---

## 7. Adding Oracle Support for Future Formats

When a new format reaches its oracle gate:

1. Identify the reference oracle tool (the authoritative implementation).
2. Confirm the tool is open-source or its use is clearly authorized (see `docs/legal-and-licensing.md`).
3. Add it to `provider_registry.yaml` with `status: experimental`.
4. Create a format-specific preflight, run, compare, and summarize script (following the FODS oracle tools as templates).
5. Run the preflight in a dedicated verification sprint (DEC-034 requirement: independent verification before human gate review).
6. Promote to `status: approved` after the gate evidence passes independent verification.

---

## 8. Relationship to oracle_common.py

`oracle_common.py` is a FODS-specific implementation module. It imports the same discovery logic that `validate_oracle_environment.py` uses at the registry level, but packages it in a FODS-specific API with FODS-specific path constants. There is no circular dependency.

In future: if many formats share the same provider (e.g., LibreOffice for both FODS and ODS), a shared `oracle_common_libreoffice.py` may be extracted. This decision is deferred (not needed until a second LibreOffice-based format reaches its oracle gate).

---

## 9. References

- `tools/oracle/provider_registry.yaml` — registry (authoritative)
- `tools/oracle/validate_oracle_environment.py` — readiness check tool
- `tools/oracle/oracle_common.py` — FODS-specific constants and discovery
- `acquisition-packs/fods/oracle-installation-checklist.md` — LibreOffice install guide
- `acquisition-packs/fods/gate6-oracle-blocker-report.md` — current FODS blocker evidence
- `acquisition-packs/fods/oracle-provider-options.md` — alternative provider options (run037)
- `docs/gates.md` — gate definitions including oracle requirements
