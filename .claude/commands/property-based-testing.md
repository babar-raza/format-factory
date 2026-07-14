---
version: "1.0"
last-updated: "2026-07-14"
phase-available: "all"
gate-required: null
skill_type: ATOMIC_SKILL
idempotency: "Same target codec function/pair + same property-catalog mapping (this file) select the same property and priority tier every time; the Hypothesis-generated test data itself is randomized per run by design, but which property is under test is a deterministic function of the target's pattern"
loc_budget: "0 lines of executable code (prompt-driven checklist only; no bundled script)"
test_path: "tests/python/csv/test_tc_ext_018_csv_roundtrip_pbt.py (TC-EXT-018-03 pilot proof -- PASS)"
external_skill_origin: true
external_skill_source: trailofbits/skills
external_skill_commit: cfe5d7b1619e47fb5b38b7e2561dad7e5f1e89af
external_skill_license: CC-BY-SA-4.0
risk_level: MEDIUM
created-by: TC-EXT-018-01
product_track: testing
---

# /property-based-testing

Identify when a function or function-pair is a good property-based-testing
target, select the right property from the catalog below, and write a real
Hypothesis test directly into `tests/**` exercising it. Unlike the purely
read-only reviewer skills imported earlier in this plan (`sharp-edges`,
`comment-analyzer`, etc.), this skill writes real test files — that is why
its `risk_level` is `MEDIUM`, not `LOW` (same rationale as
`test-driven-development.md`, TC-EXT-014).

## Attribution

<!--
This skill's property catalog (Roundtrip, Idempotence, Invariant,
Commutativity, Associativity, Identity, Inverse, Oracle, Easy to Verify, No
Exception), its strength hierarchy (No Exception -> Type Preservation ->
Invariant -> Idempotence -> Roundtrip), and its pattern-to-property priority
table are adapted from the `property-based-testing` skill in
`trailofbits/skills`, commit `cfe5d7b1619e47fb5b38b7e2561dad7e5f1e89af`.
Author, per the upstream skill's own plugin.json: Henrik Brodin. Licensed
CC-BY-SA-4.0 (https://creativecommons.org/licenses/by-sa/4.0/).

CC-BY-SA-4.0 share-alike notice: this file is itself a derivative work of
the cited upstream skill's documented methodology (prose adaptation only —
no upstream code, script, or asset is vendored or executed). Per the
license's ShareAlike term, this derivative file
(`.claude/commands/property-based-testing.md`) is distributed under the same
CC-BY-SA-4.0 terms as the original. Any further redistribution of this
specific file must preserve this attribution notice and the CC-BY-SA-4.0
license grant. This share-alike obligation applies only to this file's
adapted methodology text — it does not relicense any other file in this
repository, all of which remain under this repository's own license terms.
-->

This skill adapts the property catalog, strength hierarchy, and
pattern-to-property priority table from Trail of Bits'
`property-based-testing` skill (`trailofbits/skills`, CC-BY-SA-4.0), commit
`cfe5d7b1619e47fb5b38b7e2561dad7e5f1e89af`. Author: Henrik Brodin, per the
upstream skill's own `plugin.json`. The catalog names, the strength
hierarchy, and the priority-table shape (pattern -> property -> priority)
are carried over near-verbatim from the upstream skill; the FF-specific
function-naming scope (TC-EXT-018-02, below), the Hypothesis-only recommendation,
and the `src/**` delegation boundary are original to this repository.
Cleared by `/skill-scanner` per TC-EXT-012's mandatory gating rule.

## Purpose

Most defects in codec/parser/validator code hide in inputs a human author
never thought to hand-write. Example-based tests only cover the examples
someone wrote. This skill's job is to recognize when a target's *shape*
(a serialization pair, a parser, a normalizer, a validator, a data
structure, a mathematical/algorithmic function) implies a provable property
that holds for *all* valid inputs, then drive that property through
Hypothesis-generated data instead of a fixed example list.

## When to Use / Activates On

- **Serialization pairs** — any two functions where one turns a structured
  value into a serialized form and the other turns it back (FF's real
  naming: `parse_<fmt>`/`write_<fmt>`, or `load`/`write_<fmt>` — see
  "FF Function-Naming Scope" below; upstream's generic examples are
  encode/decode, serialize/deserialize, toJSON/fromJSON, pack/unpack, none of
  which appear literally as FF function names).
- **Parsers** — any function that turns raw/untrusted input into a
  structured model (`parse_<fmt>`, `parse_<fmt>_strict`, `load`).
- **Normalization functions** — any function meant to produce a canonical
  form (`parse_and_rewrite`, or any future `normalize_*`).
- **Validators** — predicate functions (`probe_<fmt>`, `has_*`, `is_*`).
- **Data structures** — in-memory model mutators operating on a parsed
  dict/model (`add_*`, `remove_*`, `delete_*`, `rename_*`, `clear_*`,
  `swap_*`, `merge_*`).
- **Mathematical/algorithmic functions** — anything with a documented
  inverse, a commutative/associative combination rule, or a neutral element.

## Property Catalog (10 properties)

| Property | Definition |
|---|---|
| Roundtrip | `decode(encode(x))` is equivalent to `x` for all valid `x` |
| Idempotence | `f(f(x)) == f(x)` — applying the function twice is the same as once |
| Invariant | Some condition holds for every output (or every state) the function can produce |
| Commutativity | `f(a, b) == f(b, a)` — argument order does not change the result |
| Associativity | `f(f(a, b), c) == f(a, f(b, c))` — grouping does not change the result |
| Identity | There exists an `e` such that `f(x, e) == x` for all `x` |
| Inverse | `g(f(x)) == x` for a distinct pair of functions `f`/`g` (a generalization of Roundtrip for non-symmetric pairs, e.g. compress/decompress) |
| Oracle | The function's output matches an independent reference implementation (differential testing) |
| Easy to Verify | The property is checkable directly from the output alone, without needing a second computation (e.g. "output length equals input length") |
| No Exception | The function never raises an unhandled/undocumented exception for any input in its accepted domain |

## Strength Hierarchy

```
No Exception -> Type Preservation -> Invariant -> Idempotence -> Roundtrip
(weakest)                                                        (strongest)
```

A stronger property subsumes the guarantees of every weaker one to its left
— a passing Roundtrip test implies the function also didn't crash and did
preserve type. When a target could plausibly support more than one property
from this hierarchy, prefer testing the **strongest** one that can be
honestly justified from the target's real contract; do not settle for a
weaker property (e.g. No Exception only) when a stronger one (Roundtrip) is
actually true of the target and cheap to express.

## Priority Table (pattern -> property -> priority, FF-scoped)

| Pattern (FF real naming — see scope section below) | Property | Priority |
|---|---|---|
| Serialization pair: `parse_<fmt>`/`write_<fmt>` (csv, dif, sylk, tsv, fodt, fods, ods, odt, xcf, qoi, pbm/pgm/ppm) or `load`/`write_<fmt>` (abw, fodg, fodp, gnumeric) | Roundtrip | HIGH |
| Parser half of a pair alone, against malformed/arbitrary input (`parse_<fmt>`, `parse_<fmt>_strict`, `load`) | No Exception | HIGH |
| Normalization/rewrite function (`parse_and_rewrite`, future `normalize_*`) | Idempotence | HIGH |
| Validator/predicate (`probe_<fmt>`, `has_*`, `is_*`) | Invariant | MEDIUM |
| In-memory model mutator (`add_*`, `remove_*`, `delete_*`, `rename_*`, `clear_*`, `swap_*`) | Invariant (structural bookkeeping — counts, indices — stays consistent after every mutation) | MEDIUM |
| Function with a documented, distinct inverse (e.g. `_decompress` paired with its compressor) | Inverse | HIGH |
| Merge/union-style function (`merge_abw`) | Commutativity | MEDIUM |
| Concatenation/fold-style function (`join_paragraphs` + `split_paragraphs`) | Associativity | MEDIUM |
| Function with a neutral element (empty rows/paragraphs/sheets) | Identity | LOW-MEDIUM |
| Function with an independent reference implementation available to differential-test against (e.g. stdlib `csv` as an oracle for `write_csv`/`parse_csv`, per the existing helper in `tests/python/csv/test_csv_property_based.py`) | Oracle | MEDIUM |
| Any function, as a baseline before a stronger property is justified | No Exception | universal floor |
| Simple pure function with a small, fully enumerable input domain | Easy to Verify | LOW |

## Decision Tree

1. **Writing a new test** — Identify the target's pattern from the table
   above (use FF's real function names, not the generic upstream examples).
   Select the property/priority. If no row honestly fits, do not force one —
   see Stop Conditions.
2. **Design** — Build the smallest Hypothesis strategy that generates the
   target's *real* accepted domain: bound collection sizes explicitly
   (`min_size`/`max_size`), use `.filter()`/`assume()` only to exclude inputs
   genuinely outside the target's documented contract (never to dodge an
   inconvenient in-contract failure), and prefer composable built-in
   strategies (`st.text`, `st.lists`, `st.one_of`) over hand-rolled string
   logic.
3. **Reviewing existing PBT** — Confirm the property actually claimed
   matches the row it's justified against, `max_examples` is not trivially
   low (bare defaults are acceptable; single-digit values are a red flag),
   and no `assume()`/`.filter()` discards so much of the input space that
   the test is effectively vacuous.
4. **Interpreting failures** — Always start from Hypothesis's **shrunk**
   minimal counterexample, never the raw first-found failure. Decide: is
   this a real product defect (route to `/found-issue-ownership`), or a
   test-scope error (the generator produced an out-of-contract input; fix
   the generator, not the property)? Never loosen the assertion or add an
   `assume()` filter merely to make a real in-contract failure disappear.

## Rationalizations to Reject

| Rationalization | Why it's rejected |
|---|---|
| "Property tests are slower than examples, examples are enough" | One generator run covers orders of magnitude more of the input space than any hand-picked example list; the speed cost is bounded by `max_examples`, the correctness cost of skipping PBT is unbounded |
| "It failed on a weird case, I'll `assume()` it away" | Valid only when the excluded case is genuinely out of the documented contract (see this skill's own pilot test for a real example); if it's in-contract, this hides a real defect |
| "I'll loosen the assertion so the test passes" | Weakening the property to fit a failing implementation defeats the purpose — fix the implementation or file a finding; never both weaken the check and stay silent |
| "Too many edge cases to model, I'll skip PBT here" | The targets with the most edge cases are exactly where PBT's search value is highest; complexity is a reason to use it, not skip it |
| "It passed once, that's good enough" | A single run explores a randomized subset; a different seed or a higher `max_examples` materially changes coverage — one green run is a data point, not proof |
| "The first failure is enough, I don't need the shrunk example" | The shrunk minimal counterexample is the one worth debugging; the raw first-found failure is often needlessly complex and obscures the actual defect |

## FF Function-Naming Scope (TC-EXT-018-02)

Confirmed against real source (`src/python/csv/`, `src/python/fods/`,
`src/python/abw/abw_codec.py`, `src/python/fodg/fodg_codec.py`,
`src/python/fodp/fodp_codec.py`, `src/python/gnumeric/gnumeric_codec.py`) —
upstream's generic activation examples (encode/decode, serialize/deserialize,
toJSON/fromJSON, pack/unpack) do **not** appear as literal function names in
this repository. FF's two real serialization-pair conventions are:

- **`parse_<fmt>` / `write_<fmt>`** — the dominant convention: `parse_csv`/
  `write_csv`, `parse_fods`/`write_fods`, and the same shape across dif,
  sylk, tsv, fodt, ods, odt, xcf, qoi, pbm/pgm/ppm. Most parsers also expose
  a `parse_<fmt>_strict` variant that raises instead of returning an
  error dict.
- **`load` / `write_<fmt>`** — the `*_codec.py` convention: `load(source)` /
  `write_abw(model, dest)` in abw, fodg (`write_fodg`), fodp (`write_fodp`),
  gnumeric (`write_gnumeric`). `load` is uniformly named across these four
  codecs; the write half is always `write_<fmt>`, never `save`.

When selecting a Roundtrip target, use these two real shapes — do not
pattern-match on `encode`/`decode`/`save` literal names, which do not exist
in this codebase.

## Recommended Library

**Hypothesis** (`hypothesis>=6.0`, already declared under `[project.
optional-dependencies].dev` in `pyproject.toml` and already installed in
`.venv` — confirmed via `.venv/Scripts/python -c "import hypothesis;
print(hypothesis.__version__)"`, version `6.155.7`, during TC-EXT-018-03).
If a future environment is missing it: add it to the same `dev` group in
`pyproject.toml` (do not create a new dependency group for it), then install
via the repository's normal dependency-install method — this skill's
Allowed Paths permit that one addition, nothing broader.

## Steps

1. Identify the target function or pair using the Priority Table and the FF
   Function-Naming Scope above.
2. Select the property and priority; if none honestly fits, stop (see Stop
   Conditions) rather than forcing a mismatched property onto the target.
3. Design the Hypothesis strategy per the Decision Tree's Design branch —
   bounded, filtered only for genuine out-of-contract exclusions.
4. Write the test directly into the target format's existing test directory
   (`tests/python/<fmt>/`), following this repository's existing Hypothesis
   conventions (`from hypothesis import given, settings, assume` /
   `from hypothesis import strategies as st`, as already used in
   `tests/python/csv/test_csv_property_based.py` and `test_pbt_csv.py`).
5. Run it: `.venv/Scripts/pytest <test_path> -v`. Confirm PASS.
6. On FAIL: apply the Decision Tree's Interpreting-Failures branch. If it is
   a real product defect, hand off to `/found-issue-ownership` — never fix
   `src/**` directly from this skill (see Forbidden Paths); route the fix
   through `/product-source-task`, `/add-python-api`, or `/add-dotnet-api`
   per EP-3, mirroring `test-driven-development.md`'s delegation boundary.
7. Record evidence: test path, the exact pytest command, and its PASS/FAIL
   output.

## Allowed Paths

- `tests/**` — write directly (new/modified property-based test files)
- `src/**` — read only, to discover the real function pair, its signature,
  and its documented contract (never mutated by this skill)
- `pyproject.toml` — write, but narrowly: only to add `hypothesis` to the
  existing `[project.optional-dependencies].dev` group if it is absent; no
  other dependency or section change
- `reports/`, `.local/evidences/**` — evidence output (write)

## Forbidden Paths

- `src/**` — **no direct write, ever.** A defect a property test uncovers is
  fixed by invoking `/product-source-task`, `/add-python-api`, or
  `/add-dotnet-api`; this skill creates no product-source mutation pathway
  of its own (EP-3, CLAUDE.md "Skill-Driven Architecture").
- `.supervisor/skill-registry.yaml`, `registry/found-issue-register.yaml` —
  never written by this skill directly
- `plans/master-plan.md`, `.local/supervisor/active-plan-lock.json` — never
  touched

## Mandatory Validations

- `property_priority_justified` — the property tested matches its Priority
  Table row for the target's real pattern (or a documented, honest
  deviation reason is recorded).
- `generator_bounded` — the Hypothesis strategy declares explicit
  `min_size`/`max_size` (or equivalent) bounds; no unbounded recursive or
  unbounded-size generation.
- `assume_filter_not_vacuous` — any `assume()`/`.filter()` documents *why*
  the excluded inputs are genuinely out of contract, not merely
  inconvenient.
- `shrunk_failure_examined` — on any FAIL, the recorded evidence is the
  shrunk minimal counterexample, not the raw first-found failure.
- `no_src_mutation` — this skill's own write surface never includes
  `src/**`.

## Stop Conditions

- Stop before writing a test if no Priority Table row can be honestly
  justified for the target — do not force a Roundtrip test onto a function
  pair that is not actually inverse to each other.
- Stop and route to `/found-issue-ownership` — never weaken the assertion —
  when a property fails on a genuinely in-contract input.
- Stop before writing any `src/**` fix directly; delegate per EP-3.

## Idempotency Contract

Given the same target function/pair and the same property-catalog mapping
(this file), the same property and priority tier are selected every time —
that selection is deterministic. The Hypothesis-generated test *data* is
randomized per run by design (that randomization is the point of PBT); the
property under test and its priority are not.

## Output Format

```
## Property-Based Test: <target function/pair>

### Selection
- Pattern matched: <row from Priority Table>
- Property: <one of the 10 catalog properties>
- Priority: HIGH | MEDIUM | LOW

### Test
- Path: <tests/python/<fmt>/test_....py>
- Strategy summary: <bounds, filters, and why>

### Run
- Command: .venv/Scripts/pytest <path> -v
- Result: PASS | FAIL
- If FAIL: shrunk counterexample: <value>; disposition: real defect
  (-> /found-issue-ownership) | test-scope error (generator fixed)
```

## Governance Note

Per TC-EXT-012 (external-skill-import plan) and TC-EXT-018 (this import),
this skill was cleared by `/skill-scanner` before registration. Its
TC-EXT-018-03 pilot is `tests/python/csv/test_tc_ext_018_csv_roundtrip_pbt.py`,
testing the Roundtrip property against `write_csv`/`parse_csv_strict` —
confirmed PASS (100 Hypothesis examples) before this skill's registration.
