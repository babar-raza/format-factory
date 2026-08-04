# IPYNB certification gate 1 — mutation testing (2026-08-04)

**The first certification gate ever executed in this program.** None of the
gates named in the goal record — licensed corpora, fuzzing, mutation testing,
cross-platform 3.11–3.14, reproducible builds, SBOM, provenance,
independent-repository extraction — had been run for any format before this.

## Why mutation testing first

IPYNB reached 633 passing tests today. The honest question is whether those
tests *assert* behavior or merely *execute* it. Mutation testing answers it
directly: change the source, see whether the suite notices. Given that this
session found three separate cases of checks that could not fail for the defects
they named, a large suite was exactly the place to expect the next one.

## Result

| target | mutations | killed | survived | kill rate | verdict |
|---|---|---|---|---|---|
| `validation/rules.py` | 25 | 25 | 0 | **100%** | STRONG |
| `model/metadata.py` | 20 | 20 | 0 | **100%** | STRONG |

Mutation operators exercised included `negate_comparison`, `off_by_one` and
`return_none`, applied across boundary checks, membership tests and identity
comparisons.

## The control run that makes the result trustworthy

A 100% kill rate is exactly the shape a broken tester would produce — one that
reports `killed` unconditionally would look identical. Reporting it without a
control would have been the fourth disguise of *"a check that cannot fail for
the defect it names"*.

So the tester was run against a deliberately powerless test directory containing
a single `assert True`:

```
target: validation/rules.py    tests: <a directory with one trivial test>
Result: 5 mutations, 0 killed, 5 SURVIVED, verdict NEEDS_HARDENING
```

It correctly identified every survivor with its exact line and mutation, e.g.
`L498: CELL_ID_PATTERN.fullmatch(cell_id) is None → is not None`.

**The tester detects survivors.** The 100% kill rates are therefore real
evidence, not an artefact.

## What this does and does not establish

It establishes that for the two modules tested, IPYNB's suite kills every
mutation attempted — meaningful evidence that those tests assert rather than
merely execute, and the strongest positive signal produced in this session.

It does **not** establish that IPYNB is certified, or that its whole suite is
strong. Two of roughly nineteen source modules were sampled, at 25 and 20
mutations each, bounded to keep the run inside a timeout. `model/diff.py` was
started and exceeded the two-minute command limit before finishing; it has no
result and is not counted. A full-package mutation campaign across every module
remains outstanding, and the gate is recorded as **sampled**, not complete.

## Cost, recorded because it was unknown

- `mutmut` is installed but unused here; `tools/certification/mutation_tester.py`
  (already in-repo) does the work and takes one source file at a time.
- Roughly 25 mutations against a 500-line module completes inside two minutes
  when the suite is fast (the IPYNB suite runs in ~5s).
- A whole-package campaign is therefore hours, not minutes, and needs to run
  detached rather than inside a command timeout. That is the first concrete
  cost datum for any certification gate in this program.

## Status

IPYNB remains `UNASSESSED`. Certification remains **0/6**. One gate of eight has
a sampled positive result.
