---
artifact_id: TC-FF6-SAFETENSORS-REFERENCE-SLICE-001
artifact_type: taskcard
path: taskcards/TC-FF6-SAFETENSORS-REFERENCE-SLICE-001.md
format_id: safetensors
product_family: python-format-library
visibility: internal
publish_allowed: false
license: null
provenance_required: true
provenance_status: pending-execution
source_hash: null
generated_by: codex
generated_at: 2026-08-03
reusable: false
refresh_policy:
  trigger: safetensors-source-test-upstream-or-package-change
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
goal_id: FF6-PRODUCTION-LIBRARIES-001
parent_task_id: TC-FF6-SAFETENSORS-READINESS-001
status: CANDIDATE_ACCEPTED_AWAITING_COMMIT_AUTHORIZATION
lane: SAFETENSORS
skill_ids:
  - product-source-task
  - test-driven-development
  - run-oracle
  - package-install-proof
  - plan-control
release_blockers:
  - TC-FF6-EXECUTION-RECOVERY-001
notes: >
  Second product archetype proves or disproves reusable binary and
  lazy-access execution machinery. Amended 2026-08-04: was
  BLOCKED_BY_NRRD_ACCEPTANCE / release_blockers=[TC-FF6-NRRD-GOLDEN-SLICE-001];
  reclassified READY / release_blockers=[TC-FF6-EXECUTION-RECOVERY-001] under
  the concurrent-stage-2/3 hardening amendment in
  plans/strategic/ff6/execution-recovery-directive.yaml (source/test trees
  are fully disjoint from NRRD; this card never actually depended on NRRD's
  outcome, only on Stage 1 control-repair being accepted, which it now is).
---

## Execution record (2026-08-04)

All eight obligations were found already implemented in product source
(consistent with the independent review's finding that SafeTensors' 11
declared capabilities were already coded); this session's work was writing
the obligation-bound proof file
(`tests/python/safetensors/test_reference_header_layout_lazy_slice.py`,
25 tests) and resolving obligation 7's environment blocker. **Zero product
source files were changed** — verified independently.

The "official `safetensors` co-installs without namespace shadowing"
precondition, previously marked NOT YET SATISFIED, is now resolved via a
genuinely isolated environment
(`.local/run-records/ff6/TC-FF6-SAFETENSORS-REFERENCE-SLICE-001/installed-env`):
fresh core+safetensors wheels installed alongside the real official
`safetensors==0.8.0` package, no collision, all 4 previously-blocked interop
tests pass there (independently re-run by a separate validator agent with
an identical result). Full record:
`.local/run-records/ff6/TC-FF6-SAFETENSORS-REFERENCE-SLICE-001/candidate.json`.
Independent validator verdict: `ACCEPT_WITH_NOTES` (one cosmetic docstring
issue, fixed).

**Not yet done — awaiting explicit authorization:** same as
TC-FF6-NRRD-GOLDEN-SLICE-001 — not committed, so the FF6 controller event
has not been appended (would follow whichever of these two candidates is
committed first, continuing the sequence rather than reusing an event
number).

# TC-FF6-SAFETENSORS-REFERENCE-SLICE-001: Header, layout, writer, and lazy access

## Objective and exact obligation movement

Implement one coherent eight-obligation SafeTensors slice that exercises a
different production archetype from NRRD:

- `SAL-SAFETENSORS-OBL-12CE1029701DCBC7`: exact little-endian length prefix and
  declared UTF-8 JSON header.
- `SAL-SAFETENSORS-OBL-0DEA50E8E2B34729`: checked shape and element-bit
  multiplication.
- `SAL-SAFETENSORS-OBL-3D1240179879C5E9`: 100,000,000-byte official header
  limit plus configurable stricter resource limits.
- `SAL-SAFETENSORS-OBL-56F8EB4984CEBAE8`: contiguous, non-overlapping,
  hole-free complete payload indexing.
- `SAL-SAFETENSORS-OBL-2C467A52ABF9B0B1`: deterministic metadata/payload write
  with recomputed offsets and inconsistent-model rejection.
- `SAL-SAFETENSORS-OBL-83A3FF76296963EE`: stable diagnostic validation of
  metadata, dtype, shape, size, offsets, coverage, limits, and borrowed views.
- `SAL-SAFETENSORS-OBL-909DA5B5108BBCF6`: header-only validation, read-only
  path mapping, tensor-region views, limits, and access-strategy disclosure.
- `SAL-SAFETENSORS-OBL-991021FCD2FCB37C`: sparse-file proof of bounded Python
  allocation, mapped access, copied header lifetime, and borrowed-view lifetime.

No other obligation may move implicitly.

## Preconditions

- ~~The NRRD golden slice is independently accepted, or it is
  obligation-scoped blocked after three distinct repairs while the shared
  execution path remains proved safe.~~ **Superseded 2026-08-04:** under the
  concurrent-stage hardening amendment
  (`execution-recovery-directive.yaml` `state_machine.transitions`), this
  card does not depend on NRRD's outcome — only on Stage 1's own acceptance,
  which is satisfied. May run concurrently with
  `TC-FF6-NRRD-GOLDEN-SLICE-001`.
- SafeTensors authority and official implementation are pinned to exact commit,
  package, lock, and digest identities.
- A fresh baseline wheel is built; stale wheel and source-tree-only results are
  invalidated.
- **"Official `safetensors` co-installs without namespace shadowing" — NOT
  YET SATISFIED, evidenced 2026-08-04 (independent review GAP-002).**
  `pip install safetensors` (the real upstream PyPI package) was tried in
  the dev venv and immediately broke collection of 7 existing test files
  (`tests/python/safetensors/test_safetensors_{codec,analytics,compat,
  document_mutation,tensor_data,to_csv,validation}.py`), because those
  files import a deprecated local shadow package via
  `from safetensors.safetensors_codec import ...` — the exact same name as
  the official package. The install was reverted to avoid leaving the
  environment broken. This taskcard's obligation 7 ("official reads
  candidate / candidate reads official") and its "official `safetensors`
  co-installs" precondition cannot be satisfied until this collision is
  resolved: either retire/rename the legacy shadow package's import surface,
  or scope the official-package install to an isolated venv used only for
  the interop test run (matching how `run_package_install_proof.py` already
  isolates its own venv). Do not assume this precondition is met; verify it
  fresh before relying on it.
- **Environment pre-flight (added 2026-08-04, independent review GAP-002):**
  confirm `.venv/Scripts/python.exe -c "import format_factory.safetensors"`
  succeeds and resolves under `src/python/safetensors/src/` before starting.
  New tests MUST import `format_factory.safetensors`, never the deprecated
  `safetensors.safetensors_codec` shadow package.

## Exact writable product paths

- `src/python/safetensors/src/format_factory/safetensors/codec/reader/reader.py`
- `src/python/safetensors/src/format_factory/safetensors/codec/writer/writer.py`
- `src/python/safetensors/src/format_factory/safetensors/model/document.py`
- `src/python/safetensors/src/format_factory/safetensors/validation/validator.py`
- `src/python/safetensors/src/format_factory/safetensors/security/limits.py`,
  only for backward-compatible configurable limits
- `tests/python/safetensors/test_reference_header_layout_lazy_slice.py`
- slice-specific immutable official-oracle inputs/results, receipts, and local
  candidate proof

All adapters, sharded index, analytics, CLI, unrelated formats, shared core,
controller, registry, promotion, release, and package-matrix paths are forbidden
unless a separately reviewed amendment proves they are essential to one of the
eight obligations.

## RED tests required before implementation

1. Truncated prefix/header, declared header beyond file, malformed UTF-8/JSON,
   duplicate tensor keys, and configured/official header-limit violations.
2. Shape or bit-size overflow, negative dimensions, byte-span mismatch, invalid
   sub-byte alignment, overlap, hole, out-of-order region, truncation, and
   unindexed trailing payload.
3. Deterministic writer produces identical bytes over three clean runs, sorts or
   canonicalizes only as documented, recomputes offsets, and rejects inconsistent
   in-memory models before destination mutation.
4. Header-only validation does not read/map payload bytes unnecessarily.
5. Path-backed read uses read-only mapping, returns tensor-relative views,
   reports its access strategy, and keeps/invalidates borrowed views according
   to the documented ownership contract.
6. Sparse-file test demonstrates bounded Python allocation rather than copying
   the entire payload; close and lifetime edge cases fail safely.
7. Official implementation reads candidate output and candidate reads official
   output for every supported discriminating case.

## Implementation rules

- Parse exactly eight prefix bytes and exactly the declared header bytes before
  touching payload.
- Use checked integer arithmetic for every dimension, bit, byte, and offset
  calculation.
- Validate complete ordered coverage before exposing tensor data.
- Memory mapping is read-only by default; no borrowed view may silently outlive
  its owner contract.
- Deterministic writer validates the complete model before writing and never
  leaves a partial destination on failure.
- Do not import optional NumPy/PyTorch adapters into the base path.
- Preserve the official top-level `safetensors` namespace for co-installation.

## Exact verification

```powershell
.venv\Scripts\python.exe -m pytest tests/python/safetensors/test_reference_header_layout_lazy_slice.py tests/python/safetensors/test_official_interop.py -q
.venv\Scripts\python.exe -m pytest tests/python/safetensors -q
.venv\Scripts\python.exe -m ruff check src/python/safetensors/src/format_factory/safetensors tests/python/safetensors/test_reference_header_layout_lazy_slice.py
.venv\Scripts\python.exe -m mypy src/python/safetensors/src/format_factory/safetensors
.venv\Scripts\python.exe -m pyright src/python/safetensors/src/format_factory/safetensors
.venv\Scripts\python.exe -m build src/python/core --outdir .local/run-records/ff6/TC-FF6-SAFETENSORS-REFERENCE-SLICE-001/wheelhouse
.venv\Scripts\python.exe -m build src/python/safetensors --outdir .local/run-records/ff6/TC-FF6-SAFETENSORS-REFERENCE-SLICE-001/wheelhouse
```

Install the fresh wheels plus the pinned official distribution into an isolated
environment under
`.local/run-records/ff6/TC-FF6-SAFETENSORS-REFERENCE-SLICE-001/installed-env`.
Run from outside the source tree; record import locations, wheel hashes, official
version/commit, peak allocation/RSS methodology, and exact oracle commands.

## Acceptance criteria

- [x] Initial RED and final GREEN evidence is selector- and digest-bound.
- [x] All eight named obligations have positive evidence and negative evidence
      for every rejection clause.
- [x] Prefix/header and all arithmetic/layout failures occur before unsafe
      payload exposure or allocation.
- [x] Three clean writer runs are byte-identical and official-readable.
- [x] Candidate reads official files and official implementation reads candidate
      files; contradictions are retained. (Resolved in an isolated env — see
      the Execution record above.)
- [x] Sparse-file/mmap tests prove bounded allocation and ownership behavior.
- [x] Fresh installed-wheel imports do not leak from source or shadow official
      `safetensors`. (Verified in the isolated env: both resolve from
      distinct site-packages roots, confirmed by an independent validator.)
- [x] Full affected suite, Ruff, Mypy, Pyright, architecture, namespace, and
      deterministic checks pass. (Mypy/Pyright fixed repo-wide 2026-08-04 —
      see TC-FF6-NRRD-GOLDEN-SLICE-001's candidate.json for the shared fix;
      both 0 errors on the full SafeTensors package.)
- [x] A distinct validator identity replays the candidate from the pinned
      baseline and produces a digest-bound verdict.
- [x] SafeTensors remains `UNASSESSED` and uncertified; the other 78 obligations
      do not move implicitly.
- [ ] **Controller event advancement (added 2026-08-04, independent review
      GAP-007):** on accepted integration, append a real FF6 native
      controller event (`plans/strategic/ff6/events.jsonl` +
      `controller-state.yaml`) recording this slice's acceptance — do not
      leave the controller silently frozen at Event 47. If
      `TC-FF6-NRRD-GOLDEN-SLICE-001` reaches accepted integration first and
      already advanced the controller, this card appends the next event in
      sequence rather than reusing its number.

## Rollback, successor, and Stage 4 gate

Revert only the isolated candidate on binary incompatibility, unbounded memory,
view-lifetime defect, namespace collision, oracle contradiction, or regression.
After three materially different failed repairs, block only the affected
obligation group and continue safe disjoint work.

After acceptance, compare the NRRD and SafeTensors execution receipts. Create a
Stage-4 shared-machinery task only for repeated code/control that both slices
actually used and that can be extracted with both regression suites. If there
is no material repeated machinery, record `STAGE_4_NOT_NEEDED` and proceed to
the first IPYNB vertical slice.
