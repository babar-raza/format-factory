# Skill gate ↔ validator seam (V249 / V250 / V251)

**Status:** skill-gate side SHIPPED (TC-PA-009, TC-PA-010, 2026-07-17).
Validator side (V249/V250/V251) SHIPPED same day by a parallel agent.
**Seam CLOSED 2026-07-17: V249/V250/V251 now delegate detection to
`tools/governance/skill_gates/` via `tools/supervisor/skill_gate_bridge.py`. The rule
has ONE implementation. See "Resolution".**
**Plan:** `plans/.claude/primary-purpose-the-python-starry-cupcake.md`
**Mission:** PORTFOLIO-AUDIT-2026-07-16

## Why this document exists

Three defect classes each need checking at **two** moments:

| Defect class | Creation time (skill gate) | Sprint time (validator) |
|---|---|---|
| `sys.path` mutation in product source | `/add-dogfood-export` Step 0, `/new-format-kickstart` validation | **V249** |
| stdlib / popular-package name collision | `/new-format-kickstart` Step 0 | **V250** |
| converter information-model compatibility | `/add-dogfood-export` Step 0 | **V251** |

If both sides implement the rules independently they will drift, and the two will
disagree about whether the same file is a violation. That is worse than one check:
an agent that passes the skill gate and then fails the validator (or vice versa)
learns that the rules are arbitrary. EP-3 (skill-driven architecture) requires one
implementation.

## The seam

The rules live **once**, in `tools/governance/skill_gates/`:

| Module | Public API | Validator that should call it |
|---|---|---|
| `import_hygiene.py` | `check_source(src, path) -> list[Finding]`, `check_file(path)`, `check_paths(paths)` | V249 |
| `namespace_collision.py` | `check_name(name) -> CollisionResult`, `stdlib_names() -> frozenset[str]` | V250 |
| `converter_compat.py` | `check_pair(src_fmt, tgt_fmt, matrix_path=None) -> CompatResult`, `load_matrix()` | V251 |

All are pure functions over inputs: no I/O beyond reading the file/registry named,
no `sys.exit`, no printing. They are safe to call from inside a validator.

### Expected validator usage

```python
from tools.governance.skill_gates import import_hygiene

def _v249(declaration, repo_root):
    findings = import_hygiene.check_paths([repo_root / "src" / "python"])
    return {
        "rule_id": "V249",
        "status": "FAIL" if findings else "PASS",
        "blocks_sprint": bool(findings),
        "detail": [f.format() for f in findings[:20]],
    }
```

`tools/` is importable from validator context (`tools.supervisor.*` modules already
import each other this way, and `pythonpath = ["."]` in `pyproject.toml` covers pytest).

## Resolution: the rule now has one implementation (2026-07-17)

V249/V250/V251 delegate to the shared checkers. The duplicate AST detector that lived in
`governance_validators_import_hygiene.py` is **deleted**, not merely reconciled.

| Validator | Delegates to | Keeps locally (correctly) |
|---|---|---|
| V249 | `import_hygiene.check_file()` | frozen ratchet baseline + LOAD_BEARING/REDUNDANT classification |
| V250 | `namespace_collision.check_name()` | runtime failure-mode probe (MODE_1 / MODE_2) + collision baseline |
| V251 | `converter_compat.load_matrix()`, category constants | on-disk converter enumeration ("is every pair that EXISTS classified?") |

The split is the one this document prescribed: **only detection is shared**; baselines,
classification, and the "what exists on disk" question stay in the validators. The skill
gate answers *"may I create this pair?"*; V251 answers *"is every pair that exists
classified?"*. Neither question subsumes the other.

**Rule-scope: no disagreement.** The shared `_MUTATING_METHODS` superset
(`insert, append, extend, remove, pop, clear`) plus AugAssign / slice-assign / rebind is
adopted wholesale. `sys.path.remove(...)`, `.pop()`, `.clear()` and `sys.path += [...]`
are all mutations of the interpreter-global import path from library code — the rule is
"product source must not mutate sys.path", not "must not insert". The narrower set was
an oversight, not a position.

### Why a bridge module and not `from tools.governance.skill_gates import ...`

The plain import **does not work from validator context** and would have reintroduced the
exact defect V249 exists to prevent. `tools/` has no `__init__.py`, so `tools.governance...`
resolves only with the REPO ROOT on `sys.path`. The repo root is *not* injected by the
editable-install `.pth` files (they inject `src/python` and `src`) — measured 2026-07-17
from a neutral cwd:

```
$ cd /some/other/dir && python -c "import sys; sys.path.insert(0, '<repo>/tools/supervisor');
                                   from tools.governance.skill_gates import import_hygiene"
ModuleNotFoundError: No module named 'tools'
```

It works in practice only because `sys.path[0] == ''` when the interpreter's cwd happens to
be the repo root (and via pytest's `pythonpath = ["."]`). This document's earlier claim that
"`tools/` is importable from validator context" holds only under those conditions.

That matters because in `run_all_governance_validators()` a failed import lands in an
`except` branch that appends to `_skipped_validators` — so V249 would **silently not run**
whenever the sweep is invoked from another directory, while the sweep still reported green.
The two alternatives were worse: `sys.path.insert(0, repo_root)` inside V249 would build the
validator out of the anti-pattern it bans (V149's sin, PA-F3), and duplicating the checker is
the drift this seam exists to prevent.

So `tools/supervisor/skill_gate_bridge.py` loads each checker from an **absolute path
anchored on its own `__file__`** via `importlib` — no `sys.path` mutation, no cwd
dependency, no duplication. It raises `SkillGateUnavailable`, and every validator turns that
into `FAIL` / `blocks_sprint=True`, never a PASS: an enforcer that cannot load its rule has
certified nothing.

### Verified after consolidation (2026-07-17)

* `import_hygiene` over `src/python`: **406 findings / 219 files** — unchanged, and identical
  from a neutral cwd (the calibration below still reproduces).
* Three-way count: manifest sum **220** == `expected_count` **220** == live `ran_count` **220**.
* Full sweep with `changed_files=[]`: **0 FAIL**, `blocks_sprint=False`, `skipped: 0`.
* `tests/governance/test_skill_gates.py`: 50 passed.
  `tests/supervisor/test_import_hygiene_validators.py`: 25 passed.
  `tests/supervisor/test_governance_validators.py`: 199 passed, 1 skipped.

**On the tripwire:** `test_skill_gate_and_v249_agree_on_product_source` still passes, but it
no longer *proves* anything — with one implementation it compares the shared detector against
itself and is now trivially true. It is kept deliberately: it is cheap, and it documents the
intent (if someone re-introduces a second detector, the test regains its teeth). It should not
be cited as evidence that the detectors agree.

## Two things the validator author must NOT do

**1. Do not re-implement `sys.path` detection with a regex or a naive AST walk.**
It will report FALSE CLEAN. Measured 2026-07-17 on
`import sys as _sys; _sys.path.insert(0, "/x")` — the real form at
`src/python/dif/interchange_document.py:28`:

| Matcher | Result |
|---|---|
| `re.search(r"\bsys\.path", src)` | `None` — **misses** (`\b` doesn't match between `_` and `s`) |
| AST match on `Name.id == "sys"` | `[]` — **misses** (the name is `_sys`) |
| `import_hygiene.check_source` | 1 finding — catches |

Regression tests pinning this: `tests/governance/test_skill_gates.py::test_alias_defeats_naive_matchers_but_not_ours`.
A plain substring `grep "sys.path"` *does* catch `_sys.path` incidentally, which is
why the problem is easy to miss when spot-checking by hand.

Calibration for V249 — `import_hygiene.check_paths(["src/python"])` at HEAD returns
**406 findings across 219 files** of 755 scanned, 0 parse errors. That reproduces the
plan's independently-measured counts exactly. A V249 reporting materially fewer is
under-detecting.

**2. Do not make the converter matrix optional.**
`converter_compat.check_pair` returns `CONFIG_ERROR` (blocking) when
`registry/converter-compatibility-matrix.yaml` is absent. That is deliberate: every
*new* pair is by definition absent from the matrix, so an allow-on-missing gate would
never fire on the case it exists for.

## The matrix landed mid-task — and the seam immediately drifted

`registry/converter-compatibility-matrix.yaml` (TC-PA-008's deliverable) appeared at
14:54 on 2026-07-17, while TC-PA-009 was in progress. **Its schema did not match the one
this consumer had guessed**, which is a worked example of exactly the drift this document
exists to prevent:

| | consumer's guess (wrong) | registry as authored (authoritative) |
|---|---|---|
| entry key | pair id — `abw_to_csv` | **file path** — `src/python/abw/abw_to_csv.py` |
| class field | `classification:` | **`category:`** |
| projection loss | separate `loss_note:` | recorded in **`rationale:`** |
| extras | — | `pair`, `source_domain`, `target_domain`, `disposition`, `format_domains`, `totals` |

Symptom had it gone unnoticed: `check_pair` returns `BLOCK — no entry for '<pair>'` for
**all 222 registered pairs**. A gate that blocks everything for a bogus reason looks like
a working gate and gets bypassed as noise.

**Resolution: the consumer was reconciled to the registry, not the reverse.** TC-PA-008
owns the schema. `converter_compat._normalise_pair` now accepts the path key, the `pair`
field (`abw->csv`), and a bare pair id; `_classification_of` reads `category` with
`classification` as an alias; `_loss_documented` accepts `rationale` or `loss_note`.

Verified against the real registry after reconciliation:

| check | result |
|---|---|
| pairs indexed | **222** (= registry `totals.converters`) |
| ALLOW | **183** (= 54 COMPATIBLE + 129 PROJECTION) |
| BLOCK | **39** (= all INCOMPATIBLE) |
| `fods→pbm`, `abw→pbm`, `toml→ppm` | BLOCK ✓ (TC-PA-009 completion criteria) |
| CONFIG_ERROR on any registered pair | 0 |

**If you change the registry schema, run `tests/governance/test_skill_gates.py`.**
`test_gate_resolves_against_the_real_registry` asserts the live registry is readable, that
the indexed pair count equals `totals.converters`, and that no registered pair yields
CONFIG_ERROR. It is the tripwire that turns silent drift into a red test.
`test_renamed_class_field_does_not_read_as_allow` pins the related failure mode where a
renamed class field reads as blank and blank passes.

### Note on counts

The plan and the task brief cite **~45 meaningless projections**; the registry classifies
**39** pairs as INCOMPATIBLE (of 222). The two numbers are close but not the same measure
— 39 is the registry's declared-domain classification. The registry's own `scope_limit`
says V251 "gates the DECLARED relationship of a format pair, derived from format domains.
It does NOT read converter bodies: a faithful PROJECTION and a lazy one are
indistinguishable to it." So the 129 PROJECTIONs are unaudited for faithfulness, and the
gap between 39 and 45 most likely lives there. Neither number should be quoted as "the
number of meaningless converters" without saying which measure it is.

## Enforcement reality (read before claiming prevention)

The skill gates are **real checkers with deterministic verdicts**, but the `.md` contract
telling an agent to run them is **agent-cooperative** — nothing forces the call. Measured
facts about this repo's enforcement ladder (2026-07-17):

| Mechanism | Enforcing? | Evidence |
|---|---|---|
| `.md` prose / step lists | **No** — advisory | no executor reads them |
| `pre_execution_requirements` (registry field) | **No** — decorative | zero consumers repo-wide |
| `advisory_only` (registry field) | **No** — decorative | parsed at `registries.py:136`, `grep "\.advisory_only"` → 0 consumers |
| `mandatory_validations` (registry field) | **Shape only** | `validate_skill_registry.py` checks the list is non-empty; never executes the named checks |
| `pre_mutation_guard.py` | **No** — self-declared EP-002-GAP | "Agents can bypass this script by simply not calling it" |
| PreToolUse `gate.py` hook | **Yes, but coordination-only** | blocked a real write during this task; skill-blind (EP-010-GAP) |
| Governance validator, `blocks_sprint=True` | **Yes** | this is what V249/V250/V251 are for |
| `.git/hooks/pre-commit` → `.hooks/pre-commit-skill-guard` | **Yes** | symlink installed and live |

### What this means for TC-PA-009 / TC-PA-010 specifically

Sort the delivered changes by whether they need an agent to cooperate:

**Genuinely preventive (no cooperation required):**
- `generate_supervisor_packet.py` no longer manufactures a dogfood lane every sprint —
  it emits one only for a registered COMPATIBLE / documented-PROJECTION pair. This
  changes what work is *asked for*, so no agent has to refuse anything.
- `mega-train-template.md` no longer mandates "at least one dogfood export lane".
- V249 / V250 / V251 (parallel agent) block at sprint time with `blocks_sprint=True`.
  **These are the enforcement**, and the skill gates agree with them by construction
  (V251 reads the same registry; V249 is pinned to the gate by an agreement test).

**Advisory (agent must choose to run it):**
- The Step 0 gate invocations written into `add-dogfood-export.md` and
  `new-format-kickstart.md`. The *checkers* are real and deterministic; the *instruction
  to run them* is prose, and no executor reads it. An agent that skips Step 0 and writes
  a converter for an INCOMPATIBLE pair will not be stopped at that moment — it will be
  stopped later, by V251 at sprint close or by the pre-commit hook.

That later-stop is the actual safety net; the Step 0 gate's value is that it fails in
seconds with an actionable reason instead of after the code is written. **Do not describe
the skill-side gates as preventing the defect on their own — they don't.**

**Decorative (delivered because TC-PA-009 asked, but enforce nothing):**
- `advisory_only: false` on `add-dogfood-export`. TC-PA-009 step 5 says this flip lets
  "governance validators block non-compliant converters". That premise is false — the
  field has zero consumers. The flip makes the declaration honest; it changes no
  behaviour. It is annotated as such in the registry.
- The `pre_execution_gate_command` and the new `mandatory_validations` entries
  (`converter_compatibility_gate`, `import_hygiene_gate`, `format_name_collision_gate`,
  `no_syspath_mutation`) are **declarations**. `validate_skill_registry.py` checks the
  list is non-empty; nothing executes the named checks. They are useful as machine-
  readable intent and as the obvious place for a future executor to read from — but
  today they do not run.
