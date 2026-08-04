---
artifact_id: TC-FF6-NRRD-GOLDEN-SLICE-001
artifact_type: taskcard
path: taskcards/TC-FF6-NRRD-GOLDEN-SLICE-001.md
format_id: nrrd
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
  trigger: nrrd-source-test-authority-or-oracle-change
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
goal_id: FF6-PRODUCTION-LIBRARIES-001
parent_task_id: TC-FF6-NRRD-READINESS-001
status: CANDIDATE_ACCEPTED_AWAITING_COMMIT_AUTHORIZATION
lane: NRRD
skill_ids:
  - product-source-task
  - test-driven-development
  - run-oracle
  - package-install-proof
  - plan-control
release_blockers:
  - TC-FF6-EXECUTION-RECOVERY-001
notes: >
  First product-delivery slice; three exact raw scalar payload integrity
  obligations. Amended 2026-08-04: TC-FF6-EXECUTION-RECOVERY-001 is
  ACCEPTED (see its evidence and plans/strategic/ff6/execution-recovery-directive.yaml
  stage_1_evidence); reclassified READY from BLOCKED_BY_STAGE_1. The guard's
  taskcard-bound authorization was proven end-to-end against this card's own
  real "Exact writable product paths" declaration (not a synthetic fixture)
  before this status change was made.
---

## Execution record (2026-08-04)

All three obligations closed with RED-to-GREEN tests, independent pynrrd
**and Teem** oracle evidence (both bidirectional, both isolated from the
shared dev environment), a distinct independent-validator review (verdict
`ACCEPT_WITH_NOTES`), and a wheel build + isolated-environment install
proof. Full record:
`.local/run-records/ff6/TC-FF6-NRRD-GOLDEN-SLICE-001/candidate.json`.

**Teem evidence — obtained (updated 2026-08-04, superseding an earlier
NOT_OBTAINED waiver in the same session):** no Teem/`unu` binary exists via
winget/choco/pip on native Windows, but this machine already has WSL2
(Ubuntu-22.04) installed. `apt-get download teem-apps libteem2` (no root
needed to download) + `dpkg-deb -x` (no root needed to extract into a
user-writable directory) produced a working `unu` binary. Full bidirectional
evidence — `format_factory.nrrd` writes read correctly by `unu`
(cross-checked byte-identical via `unu cksum`/`unu diff` after
canonicalization: "nrrds are the same"); `unu make` writes read correctly
by `format_factory.nrrd` — 5/5 checks pass, recorded in
`.local/run-records/ff6/TC-FF6-NRRD-GOLDEN-SLICE-001/teem-evidence/teem_independent_evidence.json`.
Lesson for future waivers: check WSL/apt (or any other already-installed
secondary environment) before concluding a tool is unavailable, not just
the primary OS's native package managers.

**Not yet done — awaiting explicit authorization:** this candidate has not
been committed, and the FF6 native controller event (would-be Event 48) has
therefore not been appended — the controller's own event schema binds
`semantic_commit`/`source_checkpoint_commit` to a real git commit, and
fabricating that binding without an actual commit would be exactly the kind
of false progress claim this mission's governance forbids. Commit + append
Event 48 once authorized.

# TC-FF6-NRRD-GOLDEN-SLICE-001: Raw scalar payload integrity

## Objective and exact obligation movement

Implement and independently prove one coherent NRRD vertical slice covering
multi-byte raw endian requirements and cheap hostile-size rejection:

| Obligation | Required result |
|---|---|
| `SAL-NRRD-OBL-5FAF36D205C887AD` | Enforce endian declaration for exposed multi-byte elements; transparently byte-swap on read/write; never transform opaque blocks. |
| `SAL-NRRD-OBL-644276A28216DFC0` | Require `endian` for raw multi-byte scalar payloads and accept only little/big semantics. |
| `SAL-NRRD-OBL-9C262130232DCD09` | Validate shape and encoded/decompressed payload size with checked arithmetic before allocation and fail hostile headers cheaply. |

Only these three obligations may move state. Supporting behavior may be changed
only where necessary to close them and must not be credited as a fourth
obligation without a new taskcard amendment and independent evidence.

## Preconditions

- `TC-FF6-EXECUTION-RECOVERY-001` is independently accepted and its continuation
  selects this card. **Satisfied 2026-08-04** — see
  `plans/strategic/ff6/execution-recovery-directive.yaml` `stage_1_scope.stage_1_evidence`.
- Exact path guard, transactional attempt, author/validator separation, and
  serialized integration candidate path pass.
- Slice-required Teem and pynrrd executables/corpora are pinned by digest,
  license/provenance, command, version, environment, and expected discriminator.
- Baseline wheel and focused behavior are captured before mutation.
- **Environment pre-flight (added 2026-08-04, independent review GAP-002):**
  before writing any RED test, confirm `.venv/Scripts/python.exe -c "import
  format_factory.nrrd"` succeeds and resolves under `src/python/nrrd/src/`.
  A same-day review found the dev `.venv` held stale pre-namespace-migration
  editable installs (`import format_factory` failed entirely); this was
  fixed by reinstalling `format-factory-core` and all six FF6 packages
  editable at current versions. If this regresses, re-run:
  `.venv/Scripts/python.exe -m pip install --no-deps -e src/python/core -e src/python/nrrd`.
  New tests in this taskcard MUST import `format_factory.nrrd` — never the
  deprecated legacy shadow package `nrrd.nrrd_codec` (6 of the 11 existing
  `tests/python/nrrd/*.py` files import that legacy package and do not count
  as coverage for this taskcard's obligations).

## Exact writable product paths

- `src/python/nrrd/src/format_factory/nrrd/codec/payload.py`
- `src/python/nrrd/src/format_factory/nrrd/codec/reader/reader.py`
- `src/python/nrrd/src/format_factory/nrrd/codec/writer/writer.py`, only if a RED
  writer endian case proves it is required
- `src/python/nrrd/src/format_factory/nrrd/validation/validator.py`
- `src/python/nrrd/src/format_factory/nrrd/security/limits.py`, only if current
  configurable limits cannot express the obligation without hard-coding
- `tests/python/nrrd/test_golden_raw_scalar_slice.py`
- slice-specific immutable corpus manifests, oracle results, receipts, and local
  candidate proof

All other product/shared/controller/registry/release files are forbidden. Do not
restructure the whole package, rename public APIs, or implement other encodings,
detached forms, spatial metadata, analytics, or CLI behavior in this slice.

## RED tests required before implementation

1. Multi-byte raw read without `endian` fails with a stable diagnostic before
   payload allocation/read.
2. One-byte raw and opaque block payloads do not require or receive byte swap.
3. Little- and big-endian 16/32/64-bit scalar fixtures decode to identical
   logical values on the host and write back with the declared byte order.
4. Invalid endian token and conflicting header semantics fail deterministically.
5. Shape multiplication overflow, negative/invalid dimension, declared byte
   count mismatch, truncated payload, decompressed-size limit, and compression
   ratio limit fail before large allocation.
6. A hostile declared shape is measured with a subprocess memory/time sentinel;
   rejection stays within configured bounded memory and time.
7. Writer roundtrip is byte-order correct and deterministic when writer changes
   are required.

## Implementation rules

- Centralize checked element-count/byte-count arithmetic; do not duplicate it
  across reader and validator.
- Separate scalar endian conversion from opaque block transfer.
- Stream or preflight sizes so validation precedes allocation/decompression.
- Use existing `ResourceLimits` and stable diagnostics; extend them only through
  the allowed limits file with backward-compatible defaults.
- Preserve working header/payload behavior and exact unknown metadata semantics.
- No recovery mode and no silent default endian for invalid multi-byte raw input.

## Independent evidence

- Read at least one Teem-produced and one pynrrd-produced little/big-endian raw
  fixture through the built wheel.
- Write discriminating fixtures with the candidate wheel and read them with both
  Teem and pynrrd where those tools support the case.
- Preserve any oracle disagreement and add a discriminating test; never choose
  the convenient result.
- Synthetic hostile headers supplement, but do not replace, independent
  interoperability inputs.

## Exact verification

```powershell
.venv\Scripts\python.exe -m pytest tests/python/nrrd/test_golden_raw_scalar_slice.py -q
.venv\Scripts\python.exe -m pytest tests/python/nrrd -q
.venv\Scripts\python.exe -m ruff check src/python/nrrd/src/format_factory/nrrd tests/python/nrrd/test_golden_raw_scalar_slice.py
.venv\Scripts\python.exe -m mypy src/python/nrrd/src/format_factory/nrrd
.venv\Scripts\python.exe -m pyright src/python/nrrd/src/format_factory/nrrd
.venv\Scripts\python.exe -m build src/python/core --outdir .local/run-records/ff6/TC-FF6-NRRD-GOLDEN-SLICE-001/wheelhouse
.venv\Scripts\python.exe -m build src/python/nrrd --outdir .local/run-records/ff6/TC-FF6-NRRD-GOLDEN-SLICE-001/wheelhouse
```

Create an isolated environment under
`.local/run-records/ff6/TC-FF6-NRRD-GOLDEN-SLICE-001/installed-env`, install the
fresh core and NRRD wheels with locked dependencies, run the focused and oracle
selectors from outside the source tree, and record that imports resolve inside
that environment's `site-packages`. The package-install-proof skill owns the
exact install receipt and wheel hashes.

## Acceptance criteria

- [x] Initial RED failures and final GREEN results are both retained.
- [x] All three obligations have positive evidence; their rejection clauses
      have negative evidence with stable diagnostics.
- [x] Checked size validation occurs before allocation/decompression.
- [x] Opaque block and one-byte behavior are not weakened.
- [x] Teem and pynrrd evidence is immutable, independent, and wheel-based.
      (Teem obtained 2026-08-04 via WSL/apt after an initial waiver —
      see the Execution record above.)
- [x] Full NRRD affected suite plus Ruff, Mypy, Pyright, architecture, API, and
      deterministic-write checks pass. (Mypy/Pyright fixed repo-wide
      2026-08-04 via pyproject.toml `[tool.mypy]` + `pyrightconfig.json`
      `extraPaths`; both 0 errors on the full NRRD package.)
- [x] Fresh wheel imports only from the installed environment.
- [x] A different validator identity replays the candidate from its pinned
      baseline and signs a digest-bound verdict.
- [x] One bounded semantic candidate lists exact changed paths, commands,
      obligation transitions, rollback, and proof digests.
- [x] NRRD remains `UNASSESSED` and uncertified; 62 other obligations do not
      move implicitly.
- [ ] **Controller event advancement (added 2026-08-04, independent review
      GAP-007):** on accepted integration, append a real FF6 native
      controller event (`plans/strategic/ff6/events.jsonl` +
      `controller-state.yaml`, advancing past Event 47) recording this
      slice's acceptance. The 2026-08-04 Stage 1 acceptance deliberately did
      NOT touch the controller (review boundary forbade it); the controller
      currently still shows Event 47 / `next_task: TC-FF6-NRRD-READINESS-001`
      and has no knowledge Stage 1 happened. This taskcard's acceptance is
      the first point where something must actually advance it — do not
      leave it silently stale a second time.

## Rollback and successor

Revert only this isolated candidate on regression, oracle contradiction, memory
limit breach, or public behavior break. Keep the RED fixture and blocker record.
After three materially different failed repairs of the same root cause, block
only these obligations and proceed to the SafeTensors reference slice if safe.

On accepted integration, select
`TC-FF6-SAFETENSORS-REFERENCE-SLICE-001` immediately. Do not insert broad NRRD
readiness, handover, dashboard, or supervisor-generalization work.
