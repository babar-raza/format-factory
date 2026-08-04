# IPYNB certification gate 1 — mutation testing (2026-08-04)

> **RETRACTED, same day, by the agent that produced it.** The result below —
> 45/45 mutations killed, 100%, verdict STRONG — was an **artifact of a broken
> measurement**. It is preserved rather than deleted because how it passed
> review matters more than the number did.
>
> **Status: no valid mutation-testing result exists for any format.** A corrected
> whole-package campaign is running; its result will be recorded separately.

## What was originally reported

| target | mutations | killed | survived | kill rate | verdict |
|---|---|---|---|---|---|
| `validation/rules.py` | 25 | 25 | 0 | **100%** | STRONG |
| `model/metadata.py` | 20 | 20 | 0 | **100%** | STRONG |

## Why it was wrong

`mutation_tester.py` scores a mutation `killed` when the test suite exits
non-zero. The IPYNB suite **already exited non-zero before any mutation was
applied**:

```
$ .venv/Scripts/pytest tests/python/ipynb/ -x -q --tb=no --no-header --timeout=30
EXACT_TESTER_INVOCATION_ON_PRISTINE_SOURCE_EXIT=1
```

Three tests fail under an editable install because they assert the package is
resident in `site-packages`:

- `test_obligation_attachments.py::test_attachment_proof_uses_installed_production_namespace`
- `test_obligation_nbformat_core.py::test_core_proof_uses_installed_production_namespace`
- `test_production_namespace.py::test_implicit_namespace_has_no_parent_init`

With the baseline red, `tests_pass` was `False` for every mutation. Every
mutation was scored `killed`. **A 100% kill rate was the only result the run
could have produced** — the same number would have come back had the mutations
never been applied at all.

## The control ran, and still missed it

A vacuity control *was* run, precisely because a 100% kill rate is the shape a
broken tester produces. It pointed the tester at a scratch directory holding one
`assert True` and got 5 mutations, 0 killed, 5 SURVIVED — proving the tester
*can* report survivors.

That control tested the wrong half. It proved the tester reports survivors when
the baseline is green; it never checked whether **this target's** baseline was
green. The failure mode it needed to exclude — a suite that can never exit zero —
was invisible to it, because the control used a different, passing suite.

The lesson is sharper than "run a control": **a control must be run against the
same configuration as the result it vouches for.** A control on a neighbouring
setup can look rigorous and certify nothing.

This is the fifth disguise of *"a check that cannot fail for the defect it
names"* found in this program, after a skipped pytest branch in a selector list,
`==` against `-0.0`, an audit hook never proven to fire, and a bare 100% kill
rate. It is the first of the five that was produced by the agent's own gate work
rather than found in inherited material.

## How it was caught

Not by review of the number. By building an isolated mutation lab
(`tools/certification/mutation_lab.py`) so an hours-long campaign could not
rewrite the live working tree — the lab's own baseline check refused to start,
naming the same three residency failures. The safety measure found the
measurement error.

## What was changed so it cannot recur

`mutation_tester.py` now runs the suite on unmutated source **before** mutating
and raises `BaselineNotGreen` if it does not pass, refusing to report a kill
rate at all (exit 2). Verified against the exact run that produced the retracted
result:

```
$ python tools/certification/mutation_tester.py --target .../validation/rules.py \
    --tests tests/python/ipynb/ --max-mutations 3
BASELINE NOT GREEN -- refusing to report a kill rate:
  tests/python/ipynb/ does not pass on unmutated source. Every mutation would be
  scored 'killed' regardless of detection.
EXIT=2
```

Environmental failures that cannot kill a mutation may be excluded with an
explicit, repeatable `--deselect`, recorded in the gate document. The three
residency assertions above qualify: they assert *where the package lives*, not
what it does, so no source mutation could change their outcome. Nothing
behavioural may be deselected.

## Cost, corrected

The original cost datum (~25 mutations per 500-line module inside two minutes)
still holds mechanically — but it was the cost of a run that measured nothing.
Real cost is recorded with the corrected campaign.

## Status

IPYNB remains `UNASSESSED`. Certification remains **0/6**. Gates with a valid
result: **0**.
