# IPYNB certification gate — mutation testing, corrected (2026-08-04)

Replaces the retracted sampled result in `ipynb-mutation-testing-20260804.md`,
which was an artifact of a red baseline. **This is the first valid mutation
result for any format in this program.**

## Result

Whole-package campaign, run in the isolated lab, with the baseline proven green
before any mutation was applied.

| | |
|---|---|
| modules discovered | 29 |
| modules scored | 18 |
| mutations tested | **387** |
| killed | **197** |
| survived | **190** |
| **kill rate** | **50.9%** |
| modules STRONG (≥70%) | **1** |
| modules NEEDS_HARDENING | **17** |
| wall time | 1,448s (~24 min) |

| module | killed | kill rate | verdict |
|---|---|---|---|
| `validation/schema.py` | 21/25 | **84.0%** | STRONG |
| `model/diff.py` | 17/25 | 68.0% | NEEDS_HARDENING |
| `model/lifecycle.py` | 17/25 | 68.0% | NEEDS_HARDENING |
| `model/cleanup.py` | 14/21 | 66.7% | NEEDS_HARDENING |
| `model/editor.py` | 16/25 | 64.0% | NEEDS_HARDENING |
| `validation/rules.py` | 16/25 | 64.0% | NEEDS_HARDENING |
| `codec/reader/reader.py` | 15/25 | 60.0% | NEEDS_HARDENING |
| `validation/validator.py` | 4/7 | 57.1% | NEEDS_HARDENING |
| `model/metadata.py` | 14/25 | 56.0% | NEEDS_HARDENING |
| `security/trust.py` | 13/25 | 52.0% | NEEDS_HARDENING |
| `model/attachments.py` | 13/25 | 52.0% | NEEDS_HARDENING |
| `codec/writer/writer.py` | 12/25 | 48.0% | NEEDS_HARDENING |
| `security/sanitizer.py` | 12/25 | 48.0% | NEEDS_HARDENING |
| `model/document.py` | 10/25 | 40.0% | NEEDS_HARDENING |
| `security/limits.py` | 3/25 | **12.0%** | NEEDS_HARDENING |
| `analytics/notebook.py` | 0/13 | **0.0%** | NEEDS_HARDENING |
| `cli/main.py` | 0/18 | **0.0%** | NEEDS_HARDENING |
| `model/output.py` | 0/3 | **0.0%** | NEEDS_HARDENING |

## How far off the retracted number was

The retracted gate reported both of its sampled modules at 100% STRONG. Measured
properly:

| module | retracted | actual |
|---|---|---|
| `validation/rules.py` | 25/25 = **100%** STRONG | 16/25 = **64%** NEEDS_HARDENING |
| `model/metadata.py` | 20/20 = **100%** STRONG | 14/25 = **56%** NEEDS_HARDENING |

Nine survivors in one module, eleven in the other, reported as zero.

## What the survivors say

**`security/limits.py` at 12% is the most serious.** Its resource-limit
constants can be changed by ±1 and 22 of 25 mutations go unnoticed — the tests
exercise the limit machinery without pinning the boundaries it enforces. For a
module whose entire job is bounding untrusted input, that is close to no
coverage of the property that matters.

```
L32: off_by_one  0 -> 1      survived
L32: off_by_one  0 -> -1     survived
L33: off_by_one  0 -> 1      survived
```

**Three modules at 0%** — `analytics/notebook.py`, `cli/main.py`,
`model/output.py`. Every function in `analytics/notebook.py` can be replaced
with `return None` and the suite stays green. `cli/main.py` can have its command
dispatch inverted (`args.command == "probe"` → `!=`) unnoticed: the CLI is
essentially untested.

**`security/sanitizer.py` at 48% and `security/trust.py` at 52%** are the other
two security-relevant modules, both around coin-flip. Together with `limits.py`,
IPYNB's security surface is its weakest tested area — the opposite of what the
633-test count suggested.

The one bright spot is `validation/schema.py` at 84%, the only STRONG module.

## Method

- Baseline proven green before mutating (`BaselineNotGreen` otherwise, GAP-023)
- Three tests deselected as environmental: they assert the package is resident
  in `site-packages`, which is false under an editable install. They assert
  *where the package lives*, not what it does, so no source mutation can change
  their outcome. Nothing behavioural was deselected.
- Run in the isolated lab (GAP-024), which proved before starting that it
  imports its own copy — it breaks the lab's `loads()`, requires the lab suite
  to notice, and confirms the live tree is byte-identical afterwards.
- 25 mutations per module cap, sampled evenly across lines.

**This result needs no vacuity control, because it is not a perfect score.** 190
survivors, each named with file, line and exact mutation, is itself proof the
tester detects survivors. The retracted run needed a control precisely because
100% is indistinguishable from a broken measurement.

## What this establishes, and what it does not

It establishes that IPYNB's 633 passing tests catch about half of the injected
faults, with security-relevant modules among the weakest. That is a real, useful,
and unflattering measurement of the format previously described as the program's
strongest.

It does **not** establish that the surviving 190 are all genuine test gaps —
some mutations are semantically equivalent and unkillable by any test. Triage is
outstanding. Nor does it cover the 11 modules too small to yield mutations under
this operator set, so the campaign is whole-package but not exhaustive.

## Cost, measured

**1,448s (~24 min)** for 18 modules / 387 mutations, with the ipynb suite at
~4s. The earlier estimate of "hours" was too pessimistic by roughly 5×. Running
the same campaign for all six formats is a few hours total, not days — it is
affordable, and should be run for the remaining five now that the lab exists.

Tools: `tools/certification/mutation_lab.py`, `tools/certification/mutation_tester.py`
Machine-readable: `reports/certification/ipynb/mutation-campaign/campaign-summary.json`

## Status

IPYNB remains `UNASSESSED`. Certification remains **0/6**. Two gates of eight
now have valid results: reproducible builds (portfolio-wide, passing) and
mutation testing (one format, largely negative).
