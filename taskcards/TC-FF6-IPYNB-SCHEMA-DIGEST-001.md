---
artifact_id: TC-FF6-IPYNB-SCHEMA-DIGEST-001
artifact_type: taskcard
path: taskcards/TC-FF6-IPYNB-SCHEMA-DIGEST-001.md
format_id: ipynb
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
  trigger: nbformat-schema-or-loader-change
  max_age_days: null
stale: false
open_source_allowed: false
commercial_allowed: false
goal_id: FF6-PRODUCTION-LIBRARIES-001
parent_task_id: IPYNB_IMPLEMENTATION_EVIDENCE_LEDGER
status: ACCEPTED
lane: IPYNB
skill_ids:
  - product-source-task
  - test-driven-development
release_blockers: []
notes: >
  Cross-platform defect: every IPYNB schema validation fails on Windows and
  passes on Linux. Found after installing the nbformat oracle made the 9
  previously-uncollectable obligation test files runnable.
---

## Defect

`validation/schema.py::_schema()` verifies each vendored official schema by
hashing its **raw bytes** against a pinned digest:

```python
payload = resources.files(__package__).joinpath("schemas", name).read_bytes()
actual = hashlib.sha256(payload).hexdigest()
if actual != SCHEMA_DIGESTS[minor]:
    raise SchemaArtifactError(...)
```

Raw bytes are platform-dependent. On a Windows checkout git rewrites LF to CRLF,
so every digest mismatches and **all six schemas fail to load**, making every
schema-validated operation raise `IPYNB_SCHEMA_ARTIFACT`. On Linux/macOS the
same source passes. The library is silently broken on one platform.

### Evidence that the content is correct and only the encoding differs

| file | raw == official | CRLF→LF == official | has CRLF |
|---|---|---|---|
| nbformat.v4.0.schema.json | False | **True** | True |
| nbformat.v4.1.schema.json | False | **True** | True |
| nbformat.v4.2.schema.json | False | **True** | True |
| nbformat.v4.3.schema.json | False | **True** | True |
| nbformat.v4.4.schema.json | False | **True** | True |
| nbformat.v4.5.schema.json | False | **True** | True |

`json.load(vendored) == json.load(official)` is `True` for all six. The pinned
`SCHEMA_DIGESTS` constants are **correct** — they match nbformat 5.10.4's real
schema files exactly. Nothing about the vendored content is wrong; only the
hashing is encoding-sensitive.

### Why it stayed hidden

The nine test files that exercise official-schema validation import `nbformat`,
which was never declared as a test dependency, so they died at collection with
`ModuleNotFoundError` and the whole IPYNB suite aborted. The digest guard was
firing correctly the entire time with nobody watching. Fixed in the preceding
commit; this taskcard fixes what that exposed.

## Fix

Hash the **canonical** form (CRLF→LF normalized) rather than raw bytes. This
matches the repository's own declared `digest_policy:
tracked_text_canonicalization: CRLF_TO_LF` in `plans/strategic/ff6/controller-state.yaml`,
keeps the guard's real purpose intact — it still detects any content change —
and makes it platform-independent.

Also add a `.gitattributes` rule pinning these schema files to LF so the working
tree and any wheel built from it stay byte-stable across platforms. The loader
fix is the primary defence; `.gitattributes` prevents the drift recurring.

## RED scenarios

1. A CRLF-encoded copy of an official schema loads successfully (currently raises
   `SchemaArtifactError`).
2. An LF-encoded copy still loads successfully (must not regress).
3. A schema whose **content** genuinely differs is still rejected — the guard
   must not be weakened into uselessness.
4. `validate(notebook, profile="4.0")` returns valid for a minimal notebook on
   this platform.
5. All six minors load and expose the expected `$schema` key.

## Exact writable product paths

- `src/python/ipynb/src/format_factory/ipynb/validation/schema.py`
- `tests/python/ipynb/test_obligation_schema_digest_encoding.py`
- `.gitattributes`

## Acceptance criteria

- [x] All 5 RED scenarios captured failing where applicable, then passing.
- [x] The 9 `test_obligation_official_schema_validation.py` failures resolve.
- [x] Full IPYNB suite improves against the 337-passed/50-failed baseline with
      no new failures.
- [x] `ruff`, `mypy` clean on changed files.
