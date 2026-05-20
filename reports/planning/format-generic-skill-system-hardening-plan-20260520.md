# Format-Generic Skill System Hardening Plan

**Date:** 2026-05-20
**Companion Audit:** `reports/audit/format-generic-skill-system-audit-20260520.md`
**Goal:** Make the skill system registry-driven so that adding a new format requires zero code changes in `tools/skills/`

---

## 1. Design Principle

All format enumeration must flow from a single source of truth: `registry/format-registry.yaml`. No skill file should contain a hardcoded list of format IDs as a behavioral gate or iteration source.

**Exception:** Test fixtures may use FODS/FODT as concrete examples. Docstring examples (`e.g. 'fods'`) are informational and need not change.

---

## 2. Phase 1: Registry-Driven Format Discovery (Minimal Change)

### 2.1 New Utility: `tools/skills/_format_discovery.py`

Create a single utility module that all skill files import:

```python
def discover_active_formats() -> list[str]:
    """
    Read registry/format-registry.yaml and return all format_ids
    that have at least Gate 1 passed.
    Falls back to ["fods", "fodt"] if registry is unreadable.
    """

def discover_formats_at_gate(min_gate: int) -> list[str]:
    """Return format_ids where latest_gate_passed >= min_gate."""

def discover_commercial_candidates() -> list[str]:
    """Return format_ids where gate_10 == passed (commercial sprint eligible)."""
```

### 2.2 Replace All `["fods", "fodt"]` Expansion Lists

**14 files require changes** (see audit Section 2.1 and 2.2):

| File | Current Pattern | Replacement |
|------|----------------|-------------|
| `commands/format_context.py:32` | `["fods", "fodt"] if ... == "all"` | `discover_active_formats() if ... == "all"` |
| `commands/lane_select.py:32` | `["fods", "fodt"] if ... == "all"` | `discover_active_formats() if ... == "all"` |
| `commands/commercial_sprint.py:52` | `if fmt not in ("fods", "fodt")` | `if fmt not in discover_commercial_candidates()` |
| `format_context_resolver.py:344` | `["fods", "fodt"] if ... == "all"` | `discover_active_formats() if ... == "all"` |
| `lane_selector.py:342` | `["fods", "fodt"] if ... == "all"` | `discover_active_formats() if ... == "all"` |
| `stale_detection.py:339` | `["fods", "fodt"] if ... == "all"` | `discover_active_formats() if ... == "all"` |
| `replay_fingerprint.py:249` | `["fods", "fodt"] if ... == "all"` | `discover_active_formats() if ... == "all"` |
| `implementation_plan_expander.py:402` | `["fods", "fodt"] if ... == "all"` | `discover_active_formats() if ... == "all"` |
| `stale_propagation.py:335` | `["fods", "fodt"]` | `discover_active_formats()` |
| `execution_simulator.py:392` | `["fods", "fodt"]` | `discover_active_formats()` |
| `planning_bundle_runtime.py:91` | `["fods", "fodt"]` | `discover_active_formats()` |
| `multi_format_planning.py:37` | `SUPPORTED_FORMATS = ["fods", "fodt"]` | `SUPPORTED_FORMATS = discover_active_formats()` |
| `authority_continuity_registry.py:237` | `for fmt in ["fods", "fodt"]` | `for fmt in discover_active_formats()` |
| `commercial_sprint_dryrun.py:274` | `["fods", "fodt"] if ... == "all"` | `discover_commercial_candidates() if ... == "all"` |

### 2.3 Estimated Effort

- `_format_discovery.py`: ~40 lines
- 14 file edits: 1-2 lines each
- Total: ~70 lines changed, ~40 lines new

---

## 3. Phase 2: Data-Driven Constraint Injection

### 3.1 Problem

`swarm_prompt_generator.py` lines 223-231 hardcode FODT-REQ-040 constraint injection with an `if fmt == "fodt"` branch. New formats with critical constraints (e.g., a hypothetical PBM depth limit) would need code changes.

### 3.2 Solution

The constraint system already reads from `generated-requirements/{fmt}/verifier-review.yaml` via `_collect_known_constraints(fmt)` in `format_context_resolver.py`. The fix is to:

1. Remove the `if fmt == "fodt"` special case in `swarm_prompt_generator.py`
2. Replace it with a generic loop over `constraints` returned by the resolver
3. Format all constraints uniformly into the prompt template

```python
# Before (hardcoded):
if fmt == "fodt" and constraints:
    fodt_constraint_section = "FODT CRITICAL CONSTRAINT..."

# After (generic):
if constraints:
    constraint_section = format_constraint_block(fmt, constraints)
```

### 3.3 Estimated Effort

- ~15 lines changed in `swarm_prompt_generator.py`
- Update corresponding test assertions in `test_swarm_prompt_generator.py`

---

## 4. Phase 3: Test Genericity Layer

### 4.1 Problem

All 21 test files use FODS/FODT as concrete test data. This is acceptable (TEST_FIXTURE_ALLOWED) but means there is no coverage proving the system works for ODS, QOI, PGM, etc.

### 4.2 Solution

Add a parametrized test module `tests/skills/test_format_generic_skill_system.py`:

```python
@pytest.mark.parametrize("fmt", ["fods", "fodt", "ods", "odt", "qoi", "pgm"])
def test_resolver_accepts_any_registered_format(fmt):
    """format_context_resolver should not crash for any registered format."""

@pytest.mark.parametrize("fmt", ["fods", "fodt", "ods"])
def test_lane_selector_accepts_any_registered_format(fmt):
    """lane_selector should return valid structure for any format."""

def test_discover_active_formats_returns_superset_of_fods_fodt():
    """Registry discovery must include at least fods and fodt."""
```

### 4.3 Estimated Effort

- ~60 lines new test file
- No changes to existing tests (they remain as FODS/FODT regression tests)

---

## 5. Phase 4: Data Table Migration (Lower Priority)

### 5.1 Problem

`acquisition_lifecycle_simulator.py` (lines 387-397) and `implementation_simulation_v2.py` (lines 565-566) contain hardcoded FODS/FODT data entries used in simulation. These are classified GOLDEN_REFERENCE_ALLOWED because they represent historical state, but the simulation cannot model new formats without code changes.

### 5.2 Solution

Move the per-format simulation data to `registry/format-registry.yaml` or a companion `registry/format-simulation-state.yaml`. Have the simulators read from this data file.

### 5.3 Estimated Effort

- ~50 lines new YAML schema
- ~30 lines changed per simulator (2 files)
- Lower priority: these simulators are planning tools, not production code

---

## 6. Implementation Sequencing

| Phase | Priority | Prerequisite | Estimated Lines | Risk |
|-------|----------|-------------|-----------------|------|
| Phase 1: Registry discovery | HIGH | None | ~110 | LOW -- fallback to `["fods", "fodt"]` on registry read failure |
| Phase 2: Constraint injection | MEDIUM | Phase 1 | ~30 | LOW -- constraint data already in resolver |
| Phase 3: Generic tests | MEDIUM | Phase 1 | ~60 | NONE -- additive only |
| Phase 4: Data table migration | LOW | Phase 1 | ~130 | LOW -- simulation-only code |

**Total estimated: ~330 lines across all 4 phases.**

---

## 7. Governance Notes

- All phases are code changes in `tools/skills/` (planning/support tooling), not in `src/` (product code)
- No gate approval implications
- No commercial readiness changes
- Phase 1 can be included in any future sprint as a Lane H sub-item
- Tests in Phase 3 should be added to the standard test suite (`tests/skills/`)

---

## 8. Success Criteria

After all phases are complete:

1. `python tools/skills/commands/format_context.py all` lists all registered formats (not just FODS/FODT)
2. `python tools/skills/commands/commercial_sprint.py ods --dry-run` works if ODS reaches Gate 10
3. No Python file in `tools/skills/` contains `["fods", "fodt"]` as a behavioral gate (docstring examples excluded)
4. `pytest tests/skills/test_format_generic_skill_system.py` passes for all registered formats
5. Adding a new format to the registry requires zero code changes in the skill system
