# Reproducible builds — all five FF6 distributions plus core (2026-08-04)

Extends `ipynb-reproducible-build-20260804.md` from one format to every FF6
distribution that has one. OpenRaster is excluded because it has no source tree
at all (GAP-021).

## Result

| distribution | verdict | gate cost |
|---|---|---|
| `format-factory-core` | REPRODUCIBLE | 40.5s |
| `format-factory-ipynb` | REPRODUCIBLE | 41.0s |
| `format-factory-nrrd` | REPRODUCIBLE | 41.0s |
| `format-factory-safetensors` | REPRODUCIBLE | 42.5s |
| `format-factory-xliff` | REPRODUCIBLE | 40.9s |
| `format-factory-ubl` | REPRODUCIBLE | 41.3s |

**6/6 after repair. 4/6 before it.** Every result carries the sensitivity
control: a third build at a different `SOURCE_DATE_EPOCH` must move the digests,
or the gate fails `COMPARISON_BLIND` instead of reporting success.

## Two real failures, found and fixed

`core` and `safetensors` were **NOT_REPRODUCIBLE**: identical wheels, *differing*
sdists on consecutive builds. The correlation was exact — they were the only two
of six without the canonicalising PEP 517 adapter, using bare
`setuptools.build_meta`, whose sdist varies in member order, mode, uid/gid,
mtime, and the gzip header's own timestamp.

This mattered more than a two-of-six ratio suggests. **`format-factory-core` is
the shared dependency of all six libraries**, so its sdist being irreproducible
undermined the reproducibility claim for the entire program, including the four
distributions that passed on their own.

## The machinery defect underneath

The adapter existed in four packages as **three different files**: `ipynb`,
`nrrd`, and an identical `xliff`/`ubl` pair, differing only in formatting. No
generator, no template, no drift check — four hand-copies that had already
diverged, and two packages that never received one.

PEP 517 resolves `backend-path` relative to the package directory, and every
distribution here must stay independently publishable, so a shared import is not
available at build time: each really does need its own copy. Copies without a
source of truth drift. So the repair is one canonical template plus a checker:

- `tools/packaging/reproducible_build_backend.py.template` — the only editable copy
- `tools/packaging/sync_build_backends.py` — `--write` to apply, `--check` to fail on drift

`--check` reported all eight problems before the fix (2 absent, 4 drifted, 2
pyproject entries) and passes after. The drift check is the durable part: it
fails on a copy that has been edited in place, which is how the three variants
appeared.

## A second defect the gate exposed only after the first was fixed

With the backend installed, `core` and `safetensors` still failed — now with
`BUILD_FAILED`:

```
* Building wheel from sdist
ERROR Backend '_build_backend' is not available.
```

Selecting an in-tree backend without shipping it in the sdist makes the sdist
**unbuildable**. The four working packages included it via `MANIFEST.in`; `core`
and `safetensors` had no `MANIFEST.in` at all. `sync_build_backends.py --check`
now treats a missing backend entry in `MANIFEST.in` as a failure, and `--write`
adds it.

This one is worth noting on its own: the first fix made the packages *look*
correct — canonical backend, correct `pyproject.toml` — while leaving them
unable to build from their own sdist. Only running the gate again caught it.
Applying a fix is not evidence the fix worked.

## Digests (wheel / sdist, truncated)

| distribution | wheel | sdist |
|---|---|---|
| core | `c2881a648116fb19` | `8b9e8920dc375cdc` |
| ipynb | `505838db95c201ed` | `06afcfbd0fb5e7c9` |
| nrrd | `0ceea89194f2069d` | `b8d4d9ff7458d746` |
| safetensors | `9b0ed1b588c6d437` | `d82b755383aa9d79` |
| xliff | `a01b50f7d9aed36c` | `b208628a862b776c` |
| ubl | `2e072c41a31f1b65` | `3df92a845e8678b2` |

The ipynb **sdist** digest differs from the one recorded earlier today
(`0fe3588b…`) because normalising its backend to the template changed a file the
sdist ships. The wheel digest is unchanged, as expected — the backend is not part
of the installed package. Full digests in
`reports/certification/{format}/reproducible-build.json`.

## What this establishes, and what it does not

Determinism **on this machine, this interpreter, this backend**: same source and
same declared epoch produce the same bytes, and the check that says so can fail.

It does **not** establish cross-machine or cross-interpreter reproducibility —
all builds ran on one Windows host under one CPython. That belongs to the
3.11–3.14 gate, unrun. It says nothing about whether wheel *contents* are
correct, only that they are stable; installed-wheel execution is a separate
gate.

## Cost

**~41s per distribution, ~4 minutes for all six.** No network, no external
acquisition, no licensed corpora. The cheapest gate measured, and now the only
one covering the whole portfolio.

## Status

All six formats remain `UNASSESSED`. Certification remains **0/6**. This is one
gate of eight; passing it portfolio-wide is a floor, not a certification.
