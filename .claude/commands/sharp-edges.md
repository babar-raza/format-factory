---
version: "1.0"
last-updated: "2026-07-14"
phase-available: "all"
gate-required: null
skill_type: ATOMIC_SKILL
idempotency: "Same target surface + same 4-phase workflow produce the same category/severity findings; read-only end to end"
loc_budget: "0 lines of executable code (prompt-driven checklist only; no bundled script)"
test_path: "N/A (prompt-spec skill, no executable code) — verification is the manual scan proof recorded under TC-EXT-017-05"
external_skill_origin: true
external_skill_source: trailofbits/skills
external_skill_commit: cfe5d7b1619e47fb5b38b7e2561dad7e5f1e89af
external_skill_license: CC-BY-SA-4.0
risk_level: LOW
created-by: TC-EXT-017-05
product_track: governance
---

# /sharp-edges

Read-only reviewer that hunts for "sharp edges" — API surfaces where the
easy, obvious, or default way to use something is also the insecure or
incorrect way. Tools restricted to Read/Grep/Glob only; never modifies the
reviewed target.

## Attribution

<!--
This skill's methodology (6 Sharp Edge Categories, the 4-phase Analysis
Workflow, the 3 adversary personas, and the Critical/High/Medium/Low
severity table) is adapted from the `sharp-edges` skill in
`trailofbits/skills`, commit `cfe5d7b1619e47fb5b38b7e2561dad7e5f1e89af`.
Author, per the upstream skill's own plugin.json: "Trail of Bits"
(Scott Arciszewski). Licensed CC-BY-SA-4.0
(https://creativecommons.org/licenses/by-sa/4.0/).

CC-BY-SA-4.0 share-alike notice: this file is itself a derivative work of
the cited upstream skill's documented methodology (prose adaptation only —
no upstream code, script, or asset is vendored or executed). Per the
license's ShareAlike term, this derivative file (`.claude/commands/sharp-edges.md`)
is distributed under the same CC-BY-SA-4.0 terms as the original. Any further
redistribution of this specific file must preserve this attribution notice
and the CC-BY-SA-4.0 license grant. This share-alike obligation applies only
to this file's adapted methodology text — it does not relicense any other
file in this repository, all of which remain under this repository's own
license terms.
-->

This skill adapts the 6 Sharp Edge Categories, the 4-phase Analysis
Workflow, the 3 named adversary personas, and the severity table from
Trail of Bits' `sharp-edges` skill (`trailofbits/skills`, CC-BY-SA-4.0),
commit `cfe5d7b1619e47fb5b38b7e2561dad7e5f1e89af`. Author: Trail of Bits
(Scott Arciszewski), per the upstream skill's own `plugin.json`. The
category names, workflow phases, personas, and severity bands are carried
over near-verbatim from the upstream skill; the FF-specific finding-routing
rule (Critical severity hands off to `/found-issue-ownership`) is original
to this repository. Cleared by `/skill-scanner` per TC-EXT-012's mandatory
gating rule.

## Purpose

**"The pit of success: secure usage should be the path of least
resistance."** Many defects are not bugs in the traditional sense — the code
does exactly what it says, but what it says is a footgun: a permissive
default, a primitive API where a semantic one was needed, a silently
misconfigured mode. This skill's job is to find the places where doing the
easy thing is doing the wrong thing, before an attacker or a careless caller
finds them first.

## When to Use

- Reviewing any diff or file that touches cryptography, authentication,
  authorization, serialization/deserialization, input parsing, or any
  configuration surface with security-relevant defaults.
- Before closing a taskcard whose scope added a new public API, config
  option, or default value that a caller could get wrong without realizing
  it.
- On request, against any existing security-relevant surface, as an ad hoc
  audit.

## 6 Sharp Edge Categories

1. **Algorithm/Mode Selection Footguns** — an API that accepts an
   algorithm/mode parameter where the wrong (but plausible-looking) choice
   silently produces an insecure result (e.g. ECB mode, MD5/SHA1 for
   integrity, non-constant-time comparison for secrets).
2. **Dangerous Defaults** — a default value that is easy/convenient but
   insecure, where the secure choice requires the caller to know to opt in.
3. **Primitive vs Semantic APIs** — exposing a low-level primitive (raw
   bytes, raw comparison, raw string concatenation) where a higher-level,
   misuse-resistant API (constant-time compare, parameterized query,
   structured builder) should be the one offered or the one documented as
   preferred.
4. **Configuration Cliffs** — a configuration surface where a small,
   easy-to-make change (one flag, one missing option) drops security posture
   off a cliff rather than degrading gracefully or failing loudly.
5. **Silent Failures** — a security-relevant check (validation, signature
   verification, permission check) that fails open, returns a default
   "success," or is bypassable without any observable error.
6. **Stringly-Typed Security** — security-relevant state (roles,
   permissions, trust levels, algorithm names) represented as unvalidated
   free-form strings instead of a closed type/enum, inviting typo-driven or
   injection-driven bypass.

## Steps (the real 4-phase workflow, adapted)

1. **Phase 1 — Surface Identification.** Enumerate the target's public
   entry points, configuration options, and default values. Identify which
   of the 6 categories above plausibly applies to each surface.
2. **Phase 2 — Edge Case Probing.** For each identified surface, probe: zero
   / empty / null input, negative values, type confusion (passing a string
   where an enum/typed value was expected, or vice versa), the behavior when
   nothing is configured (defaults), and every distinct error path.
3. **Phase 3 — Threat Modeling vs 3 Personas.** Evaluate each candidate
   sharp edge against 3 named adversary personas:
   - **The Scoundrel** — an actively malicious caller deliberately probing
     for the insecure path.
   - **The Lazy Developer** — a caller who copies the first example that
     compiles without reading the security implications.
   - **The Confused Developer** — a caller who misunderstands the API's
     contract and produces an insecure configuration by honest mistake.
   A sharp edge that only "The Scoundrel" could trigger is still a finding,
   but one that "The Confused Developer" could trigger by accident is
   generally the higher-severity finding — it does not require malice.
4. **Phase 4 — Validate Findings.** Before reporting: reproduce the misuse
   in principle from the code alone (does the code path actually behave as
   theorized), verify actual exploitability (not merely a theoretical
   concern with no reachable path), check existing documentation (is the
   danger already clearly warned against at the point of use), and consider
   whether any existing mitigation already narrows or closes the edge.

## Severity Table

| Severity | Criteria |
|---|---|
| Critical | Directly exploitable by "The Confused Developer" with no malicious intent required; leads to data exposure, auth bypass, or equivalent |
| High | Exploitable by "The Lazy Developer" following the obvious/first-found usage pattern; clear security impact |
| Medium | Requires "The Scoundrel"-level deliberate misuse, or a less-obvious usage pattern, to trigger |
| Low | Theoretical or best-practice concern with no demonstrated reachable misuse path |

## Output Format

```
## Sharp Edges Review: [Target]

### Findings
1. Category: <one of the 6 Sharp Edge Categories>
   Severity: Critical | High | Medium | Low
   Location: <file:line>
   Description: <what the sharp edge is>
   Minimal misuse example: <smallest input/config that triggers the wrong
     behavior>
   Recommendation: <concrete fix — e.g. safer default, semantic API,
     explicit fail-closed behavior>

(repeat per finding, most severe first)

### Assessment
- <one-paragraph overall verdict on this surface's "pit of success" posture>
```

## Finding Routing

- **Critical severity findings** — hand off to `/found-issue-ownership`
  (Step 1 — Capture). A Critical finding is directly exploitable by "The
  Confused Developer" with no malicious intent required, and must become a
  durable `FI-NNN` record.
- **High/Medium/Low severity findings** — logged inline in the review output
  only; no mandatory hand-off, though a recurring High-severity pattern
  across multiple surfaces may warrant one at the reviewing agent's
  discretion.

## Allowed Paths

- Read, Grep, Glob only — the file(s)/diff/surface under review, read only
- `.claude/commands/sharp-edges.md` (this file, its own reference
  categories/workflow)
- No report file is written by default — findings are recorded inline in the
  invoking taskcard's evidence

## Forbidden Paths

- **This skill has no write access at all.** Tools are restricted to
  Read/Grep/Glob only — there is no Edit, Write, or Bash-mutation path
  available to this skill under any circumstance.
- `src/**`, `tests/**` — read only, for the purpose of locating and probing
  security-relevant surfaces; never mutated by this skill
- `.supervisor/skill-registry.yaml`, `registry/found-issue-register.yaml` —
  never written directly; Critical-severity hand-off goes through
  `/found-issue-ownership`, not a direct write from this skill

## Constraints

- Read-only in all 4 phases, via Read/Grep/Glob only. No writes, no Edit, no
  Bash execution, no external network calls, no hooks executed.
- Phase 4 "Validate Findings" reproduction is textual/logical (tracing code
  paths), not a live exploit attempt against a running system — this skill
  has no execution capability to run one.

## Idempotency Contract

Given the same target surface's content and the same 4-phase workflow (this
file), the review produces the same category/severity findings. No
randomness; no time-dependent output.

## Governance Note

Per TC-EXT-012 (external-skill-import plan) and TC-EXT-017 (5 read-only
reviewer imports), this skill was cleared by `/skill-scanner` before
registration. It is a pure prompt/methodology spec: no bundled script, no
automated file operations, no hooks, and no external network calls of its
own. Its CC-BY-SA-4.0 share-alike attribution is recorded above in both
prose and an HTML comment, per TC-EXT-001-02's precedent for CC-BY-SA-4.0
imports.
