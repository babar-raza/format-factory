# /sync-build-backends

Write the canonical reproducible-build PEP 517 backend into every managed
distribution, and fail if any copy has drifted.

## Why this skill exists

Setuptools' default sdist is not byte-reproducible: member order, mode, uid/gid
and mtime vary between runs, and gzip records its own timestamp. Format Factory
distributions therefore ship a small PEP 517 adapter that rebuilds the archive
deterministically.

Each distribution needs **its own copy** of that adapter, because `backend-path`
is resolved relative to the package directory and every distribution must stay
independently publishable — a shared import is not available at build time.
Copies without a source of truth drift, and these had. Measured 2026-08-04
across the six FF6 packages:

- four carried the adapter as **three different files** (ipynb, nrrd, and an
  identical xliff/ubl pair), differing only in formatting
- `core` and `safetensors` carried none, and failed the reproducible-build gate
  with identical wheels but **differing sdists** on consecutive builds

`format-factory-core` is the shared dependency of all six libraries, so its
sdist being irreproducible undermined the reproducibility claim for the whole
program, including the four distributions that passed on their own.

## Usage

```bash
python tools/packaging/sync_build_backends.py --check    # report drift, change nothing
python tools/packaging/sync_build_backends.py --write    # apply the canonical backend
```

`--check` exits 1 and names every problem. `--write` re-checks after writing and
exits 1 if anything is still wrong.

## What it enforces

For each managed package (`core`, `ipynb`, `nrrd`, `safetensors`, `ubl`,
`xliff` — OpenRaster has no source tree yet, GAP-021):

1. `_build_backend.py` is byte-identical to
   `tools/packaging/reproducible_build_backend.py.template`
2. `pyproject.toml` selects `build-backend = "_build_backend"` with
   `backend-path = ["."]`
3. `MANIFEST.in` ships `_build_backend.py` in the sdist

Rule 3 is not cosmetic. A distribution that selects an in-tree backend without
shipping it produces an sdist that **cannot be built from**:

```
* Building wheel from sdist
ERROR Backend '_build_backend' is not available.
```

Both `core` and `safetensors` were in exactly that state after the backend was
added and before `MANIFEST.in` was — the first fix made them look correct while
leaving them unbuildable. Only re-running the gate caught it.

## Verifying the result

Applying the fix is not evidence the fix worked. Always follow with the gate:

```bash
python tools/certification/reproducible_build_gate.py \
  --package-dir src/python/<name> \
  --output reports/certification/<name>/reproducible-build.json
```

It builds twice and compares, and then builds a third time at a different
`SOURCE_DATE_EPOCH` and **requires the digests to move**. If all three match, the
comparison is insensitive to a change it must detect, and the gate fails
`COMPARISON_BLIND` rather than reporting success.

## Editing the backend

Edit `tools/packaging/reproducible_build_backend.py.template`, then run
`--write`, then re-run the gate for every managed package. Never edit a
distribution's `_build_backend.py` in place — that is how the three variants
appeared, and `--check` will fail on it.

## Tests

`tests/certification/test_reproducible_build_backends.py` — asserts no drift in
the real tree, and separately proves the drift check can fail (absent backend,
edited backend, sdist omitting the backend), so a passing run means something.
