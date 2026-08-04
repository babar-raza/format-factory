---
artifact_id: TC-FF6-SHARED-CHECKED-ARITHMETIC-001
artifact_type: taskcard
path: taskcards/TC-FF6-SHARED-CHECKED-ARITHMETIC-001.md
format_id: null
product_family: python-format-library
visibility: internal
publish_allowed: false
license: null
provenance_required: true
provenance_status: pending-execution
source_hash: null
generated_by: claude
generated_at: 2026-08-04
reusable: false
refresh_policy:
  trigger: archetype-source-change
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
goal_id: FF6-PRODUCTION-LIBRARIES-001
parent_task_id: TC-FF6-EXECUTION-RECOVERY-001
status: READY
lane: SHARED
skill_ids:
  - product-source-task
  - test-driven-development
release_blockers: []
notes: >
  STAGE_4_EXTRACT_ONLY_PROVEN_SHARED_MACHINERY. Resolves directive GAP-010
  using the two accepted archetypes (NRRD, SafeTensors) as the proof of
  repeated need, per the directive's own pre-registered trigger.
---

## Two-archetype comparison (the evidence for extracting anything at all)

GAP-010 claims NRRD and SafeTensors "hand-roll their own overflow-checked
shape/size arithmetic independently ... same logical check, already implemented
twice, already behaviorally different." Reading both confirms the duplication
but shows the claim is **too broad**: most of what looks duplicated is
legitimately format-specific, and only a small core is genuinely the same.

| | NRRD `checked_element_count` | SafeTensors `_checked_element_count` |
|---|---|---|
| Ceiling | `limits.max_decompressed_bytes` — a **configurable memory budget** | `_MAX_U64` — a **format-defined representational ceiling** |
| Zero dims | rejected (`size <= 0`), NRRD axes must be positive | **allowed**; zero-element tensors are valid SafeTensors |
| Empty input | rejected (`sizes` needs ≥1 axis) | allowed (empty shape ⇒ scalar, product 1) |
| Arity guard | `len(sizes) > limits.max_entries` | none at this layer |
| Overflow check | **after** each multiply | **before** each multiply |
| Raises | `NrrdParseError` / `ResourceLimitError` | `ValueError` from a dataclass `__post_init__` |

Three of these differences are **correct** and must not be unified: the ceiling
means different things, zero is valid in one format and invalid in the other,
and each format has a published exception contract callers depend on. A shared
function that took flags for all of that would be an abstraction over
coincidence, not over a shared idea — worse than the duplication.

What **is** genuinely the same is one thing: *multiply a sequence of
non-negative integers, refusing to exceed a ceiling, without computing an
unbounded intermediate*. That is the piece worth extracting, and it is exactly
where the two already diverge (check-before vs check-after multiply).

### Decision

Extract the narrow primitive `checked_product` into `format_factory.core`;
leave every policy decision in each format. Adopt check-**before**-multiply, the
stricter of the two existing techniques.

### Observation recorded, not silently fixed

NRRD compares an **element count** against `max_decompressed_bytes`, a **byte**
budget — a unit mismatch. It is conservative (count ≤ bytes whenever item size
≥ 1) so it is not a defect, and `expected_binary_size` enforces the byte budget
properly afterwards. Left as-is: changing the ceiling would change NRRD's
public rejection threshold, which is out of scope for an extraction task.

## Exact writable product paths

- `src/python/core/src/format_factory/core/arithmetic.py`
- `src/python/core/src/format_factory/core/__init__.py`
- `src/python/nrrd/src/format_factory/nrrd/codec/payload.py`
- `src/python/safetensors/src/format_factory/safetensors/model/document.py`
- `tests/python/core/test_checked_arithmetic.py`

## Acceptance criteria

- [x] `checked_product` exists in core with its own tests, including the
      check-before-multiply property that no unbounded intermediate is formed.
      24 tests in `tests/python/core/test_checked_arithmetic.py`.
- [x] Both archetypes call it; neither hand-rolls the multiply loop any more.
- [x] **Both archetypes' public exception contracts are unchanged** — NRRD still
      raises `ResourceLimitError`/`NrrdParseError`, SafeTensors still raises
      `ValueError`. Proven by both suites passing unmodified.
- [x] NRRD suite ≥ 347 passed and SafeTensors suite ≥ 385 passed, 0 regressions.
      NRRD 347 passed / 1 skipped; SafeTensors 385 passed / 1 skipped with the
      same 4 pre-existing GAP-002 shadow-package failures as the baseline — no
      new failures.
- [x] `ruff`, `mypy`, `pyright` clean on all changed files.
      ruff clean; mypy `no issues found in 45 source files`; pyright `0 errors`.

## Execution record (2026-08-04)

### Two defects the extraction surfaced in my own first attempt

Both were caught by existing guards, which is worth recording because it is
evidence those guards are load-bearing rather than ceremonial:

1. **`tests/python/core/test_package_contract.py` blocked the new module.**
   core pins its exact module set, so adding `arithmetic.py` failed until the
   contract was updated deliberately. That is the guard working as intended —
   extending core's responsibilities is exactly the kind of thing that should
   not happen silently. The assertion now carries the reason it grew.

2. **The first wiring silently changed SafeTensors' error messages.**
   `test_obligation_integer_overflow.py` asserts the exact strings
   `"shape dimension exceeds unsigned 64-bit size"` and
   `"shape element count overflows unsigned 64-bit size"`. Re-raising
   `ValueError(str(exc))` preserved the *type* but not the *message*, which is
   still a public-contract break. Fixed by giving `CheckedArithmeticError` a
   `context["reason"]` (`factor_exceeds_ceiling` / `product_exceeds_ceiling`)
   so each caller maps back to its own published wording. An extraction that
   changes observable behavior is a regression, not a refactor.

### A correctness fix in the primitive itself

The first draft short-circuited on a zero factor (`if value == 0: return 0`),
which meant `checked_product([0, -5])` returned `0` instead of rejecting the
negative factor — a zero would mask any malformed input after it. It now
validates every factor and returns `0` at the end. Covered by
`test_zero_does_not_mask_a_later_malformed_factor`.

### What was deliberately not unified

Zero-validity, ceiling semantics, arity limits, and exception types stay in
each format. See the comparison table above — three of those differences are
correct, and a shared function taking flags for all of them would abstract over
coincidence rather than over a shared idea.
