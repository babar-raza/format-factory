# IPYNB certification gate — reproducible builds (2026-08-04)

**The first certification gate in this program with a valid result.** Gate 1
(mutation testing) was retracted the same day as a measurement artifact; see
`ipynb-mutation-testing-20260804.md`.

## Claim under test

Rebuilding `format-factory-ipynb` from source produces byte-identical
artifacts — so a published wheel can be independently reproduced from the
tagged source rather than trusted because it was uploaded.

## Result

Three builds via `python -m build`, each into a fresh output directory:

| build | `SOURCE_DATE_EPOCH` | wheel | sdist |
|---|---|---|---|
| 1 | `315532800` (backend default) | `505838db…` | `0fe3588b…` |
| 2 | `315532800` | **identical to build 1** | **identical to build 1** |
| control | `1600000000` | **differs** | **differs** |

- `format_factory_ipynb-0.2.0.dev0-py3-none-any.whl`
  → `505838db95c201edc8fe109511c36949cf15ec455c0a04d4153a5a0bd8b33e53`
- `format_factory_ipynb-0.2.0.dev0.tar.gz`
  → `0fe3588bfdafd7ae00ff7d480f54e0be80f8fabf1aaf67bd10f1621a46cd1a2f`

**Verdict: REPRODUCIBLE.**

## The control, and why this gate has one

Two builds agreeing is necessary but not sufficient. A comparison that could not
have detected a difference proves nothing, and there are several cheap ways to
write one by accident: comparing a file to itself, digesting two paths that both
failed to exist, or letting a build cache serve the second run. Any of those
yields "identical" and looks like success.

So the gate builds a third time with a different `SOURCE_DATE_EPOCH` and
**requires the digests to change**. Both artifacts moved, so the comparison is
demonstrably sensitive to the input it must be sensitive to. Had all three
matched, the gate would have failed with `COMPARISON_BLIND` rather than
reporting success — the sensitivity check is a gate condition, not a note.

This is deliberate: the immediately preceding gate reported a perfect score that
its own control could not distinguish from a broken measurement.

## What this establishes, and what it does not

It establishes determinism of the build **on this machine, this interpreter,
this backend**: same source and same declared epoch produce the same bytes, and
the check that says so can fail.

It does **not** establish cross-machine or cross-interpreter reproducibility.
All three builds ran on one Windows host under one CPython. Reproducibility
across platforms and versions belongs to the cross-platform gate (3.11–3.14),
which has not been run. It also does not verify that the wheel's *contents* are
correct — only that they are stable. Installed-wheel execution is a separate
gate.

Reproducibility here is not accidental: `src/python/ipynb/_build_backend.py`
canonicalises sdist archives (sorted members, fixed mode/uid/gid, `mtime` pinned
to `SOURCE_DATE_EPOCH`). This gate is the first evidence that the backend
actually does what it was written to do — until now it was untested machinery,
which the GAP-022 rule says is not evidence of anything.

## Cost

- build 1: 17.2s · build 2: 14.9s · control: 15.5s
- **whole gate: ~47s** plus negligible digesting

The cheapest gate measured so far by a wide margin, and it needs no external
acquisition, no network, and no licensed corpora. It should be run for every
format as soon as that format has a buildable distribution.

Tool: `tools/certification/reproducible_build_gate.py`
Machine-readable result: `reports/certification/ipynb/reproducible-build.json`

## Status

IPYNB remains `UNASSESSED`. Certification remains **0/6**. This is one gate of
eight, and the first with a result that survives its own control.
