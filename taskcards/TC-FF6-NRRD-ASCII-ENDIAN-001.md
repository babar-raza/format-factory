---
artifact_id: TC-FF6-NRRD-ASCII-ENDIAN-001
artifact_type: taskcard
path: taskcards/TC-FF6-NRRD-ASCII-ENDIAN-001.md
format_id: nrrd
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
  trigger: nrrd-source-test-authority-or-oracle-change
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
goal_id: FF6-PRODUCTION-LIBRARIES-001
parent_task_id: TC-FF6-NRRD-GOLDEN-SLICE-001
status: READY
lane: NRRD
skill_ids:
  - product-source-task
  - test-driven-development
  - run-oracle
release_blockers: []
notes: >
  Interoperability regression found while proving the encoding dimension of
  TC-FF6-NRRD-GOLDEN-SLICE-001's obligation SAL-NRRD-OBL-644276A28216DFC0
  ("endian-required matrix by type AND encoding"). The golden slice proved the
  type dimension only; every one of its endian tests uses `encoding: raw`.
  Probing the encoding dimension showed the endian guard fires for textual
  encodings too, which both the governing SAL fact and the reference
  implementation say it must not.
---

## Defect

`endian` is required for **every** multi-byte scalar payload regardless of
encoding, including the textual encodings (`ascii`/`text`/`txt`). It must be
required only for encodings whose on-disk bytes actually expose byte order.

### Governing authority

`shared/sal-facts/nrrd.yaml` fact `SAL-NRRD-00014` (`nrrd:endian`, status
`verified`):

> The endian field is required whenever **the encoding exposes byte order**
> and the element size exceeds one byte declaring little or big byte order.

Textual encodings do not expose byte order — the payload is decimal text.

### Independent oracle (Teem 1.12.0 `unu`, the reference C implementation)

Obtained via WSL2 Ubuntu-22.04, `apt-get download` + `dpkg-deb -x`, no root.

| Input | Teem `unu save -f text` | `format_factory.nrrd` |
|---|---|---|
| `encoding: ascii`, `type: uint16`, no `endian` | **accepted**, values `1 2 3` | **rejected** (`NrrdParseError`) |
| `encoding: raw`, `type: uint16`, no `endian` | **rejected** (header problems) | rejected (correct) |

We reject a file the reference implementation reads. That is an
interoperability defect, not a stricter-but-safe choice.

### Root cause

Both directions normalize through the binary codec even when the on-disk form
is textual, and that normalization step demands a declared byte order:

- Read: [reader.py:276-285](src/python/nrrd/src/format_factory/nrrd/codec/reader/reader.py#L276-L285)
  decodes ASCII correctly via `decode_ascii`, then calls `encode_binary(...,
  endian=header.get("endian"))` purely to populate the document's derived
  binary buffer. That call reaches `_endian_prefix`, which raises when
  `endian` is absent.
- Write: [writer.py:93-100](src/python/nrrd/src/format_factory/nrrd/codec/writer/writer.py#L93-L100)
  always calls `encode_binary` before `encode_encoding`, so authoring an ASCII
  document without `endian` fails too.

The requirement is a property of the **encoding**, but it is enforced in a
helper that only sees the **type**. The golden slice's fix was correct for the
encodings it tested and over-broad for the ones it did not.

### Secondary defect (same call path)

A failed write raises `NrrdParseError`, not `NrrdWriteError` — `_endian_prefix`
raises a parse error and `encode_binary` does not translate it on the write
path. `dumps()` on a raw document with no `endian` is a *write* failure and
must surface as one.

## Obligations

| Obligation | Requirement |
|---|---|
| `SAL-NRRD-OBL-644276A28216DFC0` | Require `endian` for raw multi-byte scalar payloads and accept only little/big semantics. Proof requirement: endian-required matrix **by type and encoding**. |
| `SAL-NRRD-OBL-5FAF36D205C887AD` | Enforce endian declaration for exposed multi-byte elements; transparently byte-swap on read/write; never transform opaque blocks. |

Neither obligation may be promoted past `partial` until the encoding dimension
is proven in both directions, because the currently-shipped behavior
contradicts the reference implementation.

## RED scenarios (must fail before the fix)

1. Read `encoding: ascii` + multi-byte type + no `endian` → succeeds with correct values.
2. Same for `text` and `txt` aliases.
3. Write an ASCII multi-byte document with no `endian` → succeeds, emits no `endian` field.
4. Round-trip an ASCII document with no `endian` through `dumps`/`loads`.
5. Every byte-order-exposing encoding (`raw`, `gzip`, `gz`, `bzip2`, `bz2`, `hex`)
   still rejects a missing `endian` for a multi-byte type — the golden slice's
   guarantee must not regress.
6. A declared `endian` on an ASCII document is still accepted and preserved.
7. An *invalid* endian token is still rejected even for ASCII (a declared value
   must be well-formed whether or not it is load-bearing).
8. `dumps()` of a raw multi-byte document with no `endian` raises
   `NrrdWriteError`, not `NrrdParseError`.

## Exact writable product paths

- `src/python/nrrd/src/format_factory/nrrd/codec/payload.py`
- `src/python/nrrd/src/format_factory/nrrd/codec/reader/reader.py`
- `src/python/nrrd/src/format_factory/nrrd/codec/writer/writer.py`
- `tests/python/nrrd/test_ascii_encoding_endian.py`

## Acceptance criteria

- [x] All 8 RED scenarios captured failing, then passing.
      Captured RED: **13 failed, 18 passed**. After fix: **31 passed**. The 18
      already-green tests are the byte-order-exposing regression guards, which
      were expected to pass throughout.
- [x] Full `tests/python/nrrd` suite green with no regression against the
      305-passed/1-skipped baseline at commit `028b6db4`.
      Result: **336 passed, 1 skipped, 0 regressions** (+31 new tests).
- [x] Teem bidirectional evidence: `unu` reads our ASCII output that declares
      no `endian`, and we read `unu`-authored ASCII input.
      Both directions pass — see
      `.local/run-records/ff6/TC-FF6-NRRD-ASCII-ENDIAN-001/teem_independent_evidence.json`.
      The reverse-direction artifact `teem_ascii_encoded.nrrd` is authored
      entirely by Teem (`encoding: ASCII`, no `endian` field) and would have
      been rejected by the pre-fix reader.
- [x] `ruff`, `mypy`, and `pyright` clean on every changed file.
      ruff clean; mypy `Success: no issues found in 17 source files`; pyright
      `0 errors` on product source. (Pyright reports an unresolved `pytest`
      import for the new test file; this reproduces identically on untouched
      test files such as `test_production_namespace.py` and is a pre-existing
      environment gap, not a defect in this change.)
- [x] Obligation evidence ledger
      (`shared/format-contracts/implementation-evidence/nrrd.yaml`) updated with
      the real new selectors, and the reconciliation report regenerated rather
      than hand-edited.

## Execution record (2026-08-04)

Fixed by scoping the requirement to the encoding rather than the element width:

- `payload.py` gains `TEXTUAL_ENCODINGS` / `BYTE_ORDER_EXPOSING_ENCODINGS`
  constants and a `require_endian` parameter threaded through `decode_binary`
  and `encode_binary`. When a textual payload is normalized into the document's
  derived binary buffer, a declared `endian` is still honored but never
  demanded, and the internal byte order is fixed (`_TEXTUAL_INTERNAL_BYTE_ORDER`)
  so that buffer stays deterministic across platforms.
- `reader.py` passes `require_endian=False` on the textual branch.
- `writer.py` passes `require_endian=False` for textual output and translates
  the header-derived `NrrdParseError` into `NrrdWriteError`, so a failed write
  surfaces as a write error.

The `{"ascii", "text", "txt"}` literal was replaced with the shared constant at
the three call sites inside this taskcard's declared writable paths. One further
copy remains at
[validator.py:55](src/python/nrrd/src/format_factory/nrrd/validation/validator.py#L55);
it is deliberately left untouched because `validator.py` is **not** in this
card's declared writable paths. Folding it in is a follow-up, not a silent
scope expansion.

### Truth boundary

This closes the encoding-scoping defect only. It does not certify NRRD and does
not by itself move `SAL-NRRD-OBL-644276A28216DFC0` or
`SAL-NRRD-OBL-5FAF36D205C887AD` to `implemented` — see the obligation ledger for
their post-fix status. NRRD remains `UNASSESSED`; certification remains 0/6.
