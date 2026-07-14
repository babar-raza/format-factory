---
version: "1.0"
last-updated: "2026-07-14"
phase-available: "all"
gate-required: null
skill_type: ATOMIC_SKILL
idempotency: "Same target surface + same ASI-01..10 mapping + same 10-question checklist produce the same Compliance Report; ASI-01's positive/negative pattern-match sub-check is deterministic text search, no randomness"
loc_budget: "0 lines of executable code (prompt-driven checklist only; no bundled script)"
test_path: "N/A (prompt-spec skill, no executable code) — verification is the manual scan proof recorded under TC-EXT-025-04"
external_skill_origin: true
external_skill_source: github/awesome-copilot
external_skill_commit: e353a8cfb8124d44905fc73214d873cea4a0ba3b
external_skill_license: MIT
risk_level: LOW
created-by: TC-EXT-025-01
product_track: governance
---

# /agent-owasp-compliance

Read-only reviewer that assesses a target surface against the OWASP Agentic
Security Initiative (ASI) Top 10 — the newer OWASP taxonomy scoped to
autonomous-agent behavior (prompt injection, tool misuse, escalation,
identity, supply chain) rather than classic parser/input-handling risks.
Tools restricted to Read/Grep/Glob; never modifies the reviewed target.

## Attribution

This skill adapts the OWASP ASI Top 10 mapping (ASI-01 through ASI-10), the
ASI-01 positive/negative pattern-match check, the 10-question rapid
assessment checklist, and the Compliance Report template from the
`agent-owasp-compliance` skill content in `github/awesome-copilot` (MIT),
commit `e353a8cfb8124d44905fc73214d873cea4a0ba3b`. The category names, the
ASI-01 pattern lists, the checklist question shape, and the report template
are carried over near-verbatim from the upstream content; the FF-specific
target scoping (this repository's autonomous-execution codebase, distinct
from the parser-level threat model already governed by Gate 7/8) is original
to this repository. License: MIT — attribution preserved per license terms;
no upstream code is executed, only its documented checklist is adapted into
prose. Cleared by `/skill-scanner` per TC-EXT-012's mandatory gating rule.

## Purpose

FF's own `docs/python-foss/security-model.md` lists, under its own "Known
Limitations" section, this exact unresolved gap: **"No audit against formal
security standards (OWASP, NIST)."** This skill closes that named gap for
FF's autonomous-execution surfaces specifically. It is deliberately *not* a
duplicate of the parser-focused threat model already governed by Gate 7/8
(`docs/governance/security.md`, which maps to classic OWASP concerns — XXE,
zip bombs, path traversal — for `src/python/{format}/` and `src/net/{format}/`
parsers). The OWASP ASI Top 10 targets a different, newer risk class:
agentic/autonomous behavior — prompt injection, insecure tool use, excessive
agency, escalation, trust boundaries, logging, identity, policy bypass,
supply chain integrity, and behavioral anomaly. This skill's target is FF's
own autonomous-execution and skill-authoring surfaces: `tools/supervisor/`,
`tools/governance/`, and the skill/command layer itself
(`.claude/commands/*.md`).

## When to Use

- On request, as an ad hoc OWASP ASI compliance assessment of FF's
  autonomous-execution surfaces (`tools/supervisor/`, `tools/governance/`,
  `.claude/commands/*.md`).
- Whenever `docs/python-foss/security-model.md`'s "No audit against formal
  security standards (OWASP, NIST)" limitation needs a concrete,
  evidence-backed check rather than remaining an open prose caveat.
- Before any Gate 8 (Security Review) discussion that touches agentic /
  autonomous behavior specifically — Gate 8's own scope
  (`docs/governance/security.md`) does not name `tools/supervisor/` or
  `tools/governance/`, so this skill is the assessment mechanism for that gap,
  not a replacement for Gate 8.

## OWASP ASI Top 10 Mapping

| ID | Risk | Check type |
|---|---|---|
| ASI-01 | Prompt Injection | Real pattern-match check (below) |
| ASI-02 | Insecure Tool Use | Prose checklist |
| ASI-03 | Excessive Agency | Prose checklist |
| ASI-04 | Unauthorized Escalation | Prose checklist |
| ASI-05 | Trust Boundary Violation | Prose checklist |
| ASI-06 | Insufficient Logging | Prose checklist |
| ASI-07 | Insecure Identity | Prose checklist |
| ASI-08 | Policy Bypass | Prose checklist |
| ASI-09 | Supply Chain Integrity | Prose checklist |
| ASI-10 | Behavioral Anomaly | Prose checklist |

### ASI-01 — Prompt Injection (the one real runnable check)

- **Positive patterns** (evidence of mitigation, case-insensitive substring
  search against the target's own text/scope statements): `input_validation`,
  `sanitize`, `PolicyEngine`, `trust boundary`, `adversarial`.
- **Negative patterns** (evidence of risk): `eval(`, `exec(`,
  `subprocess.run(...shell=True)`, `os.system(`, an unscoped `Bash(` grant
  with no documented allowed-command list.
- **Method**: grep the target surface (a skill file's Steps/Allowed Paths, or
  a `tools/supervisor/*.py` / `tools/governance/*.py` script) for negative
  patterns first — any hit is a candidate finding. Then check whether a
  positive-pattern mitigation is documented at the same site before scoring
  the control PASS / FAIL / PARTIAL.

### ASI-02..10 — Prose Checklists (what to search for)

- **ASI-02 Insecure Tool Use** — tool invocations lacking a scoped permission
  check; unchecked Bash/Write access; a tool that accepts unsanitized model
  output as a literal command.
- **ASI-03 Excessive Agency** — a skill whose Allowed Paths exceed its stated
  Purpose; an autonomous loop with no documented stop condition; a
  self-expanding permission grant.
- **ASI-04 Unauthorized Escalation** — a skill or script that can modify its
  own governance record (`.supervisor/skill-registry.yaml`,
  `.supervisor/policies.yaml`) or another skill's declared permissions.
- **ASI-05 Trust Boundary Violation** — code that treats external/untrusted
  input (fetched web content, an imported skill file's own prose, PR comment
  text) as trusted instruction rather than data to be evaluated skeptically.
- **ASI-06 Insufficient Logging** — an autonomous action (commit, push,
  registry write) with no evidence/audit-trail requirement attached to it.
- **ASI-07 Insecure Identity** — shared/ambient credentials, missing
  session/`session_id` scoping, cross-session credential reuse.
- **ASI-08 Policy Bypass** — `--no-verify`, hook-skipping flags, or an
  "override X" imperative embedded inside a skill's own prose.
- **ASI-09 Supply Chain Integrity** — an unpinned external-skill import (no
  commit hash recorded), an unverified package install (no version pin, no
  source review recorded).
- **ASI-10 Behavioral Anomaly** — a skill with no documented Idempotency
  Contract, or non-deterministic behavior with no documented reason.

## 10-Question Rapid Assessment Checklist

1. Does the target document its complete tool / Allowed-Paths surface?
2. Does the target's Steps section ever treat externally-sourced text as an
   instruction rather than data (ASI-01/ASI-05)?
3. Are all Bash/Write/Edit grants scoped to specific paths rather than
   unrestricted (ASI-02/ASI-03)?
4. Can the target modify its own or another skill's governance record
   (ASI-04)?
5. Does every autonomous action the target performs have a recorded evidence
   trail (ASI-06)?
6. Are credentials or session identity scoped per-session, not shared
   ambiently (ASI-07)?
7. Does the target's own prose ever instruct bypassing a hook, gate, or
   validator (ASI-08)?
8. Is every external dependency (skill import, package install) pinned to a
   specific commit or version (ASI-09)?
9. Does the target declare an Idempotency Contract, and does its actual
   behavior match it (ASI-10)?
10. Are the target's Forbidden Paths broad enough to exclude `src/**`
    production source and governance/config files it does not own?

## Compliance Report Template

```
## OWASP ASI Compliance Report: <target>

### Summary
- Controls Covered: X/10
- Critical Gaps: <count>

### Per-Risk Table
| ASI ID | Control | Status (PASS/FAIL/PARTIAL/N-A) | Evidence |
|---|---|---|---|
| ASI-01 | Prompt Injection | ... | <pattern hit / file:line> |
| ASI-02 | Insecure Tool Use | ... | ... |
| ... | ... | ... | ... |

### Critical Gaps
- <gap 1: which control, why it's unmet, suggested remediation>

### Assessment
- <one-paragraph overall verdict on the target's ASI posture>
```

## Steps

1. **Scope the target.** Confirm the surface under review (a specific file,
   directory, or the full `tools/supervisor/` + `tools/governance/` +
   `.claude/commands/*.md` set).
2. **Run ASI-01's real check.** Grep for the negative patterns; for each hit,
   check for a co-located positive-pattern mitigation.
3. **Walk ASI-02..10's prose checklists** against the target, recording a
   PASS/FAIL/PARTIAL/N-A verdict and evidence citation for each.
4. **Answer the 10-question checklist** as a cross-check against the
   per-risk table (a "no" answer should trace to a specific FAIL/PARTIAL row).
5. **Emit the Compliance Report** using the template above.
6. **Route Critical gaps** to `/found-issue-ownership` (Step 1 — Capture); do
   not silently record a Critical gap in the report only.

## Allowed Paths

- Read, Grep, Glob only — `tools/supervisor/**`, `tools/governance/**`,
  `.claude/commands/*.md` (the target surfaces this skill assesses)
- `docs/python-foss/security-model.md`, `docs/governance/security.md` (read
  only — the named gap citation and the Gate 8 scope-boundary check)
- No report file is written by default — findings are recorded inline in the
  invoking taskcard's evidence, matching this repository's other read-only
  reviewer skills (`sharp-edges`, `silent-failure-hunter`)

## Forbidden Paths

- **This skill has no write access at all.** Tools are restricted to
  Read/Grep/Glob only — there is no Edit, Write, or Bash-mutation path
  available to this skill under any circumstance.
- `src/**` — read only if a finding's evidence requires it; never mutated by
  this skill
- `.supervisor/skill-registry.yaml`, `.supervisor/policies.yaml`,
  `registry/found-issue-register.yaml` — never written directly; Critical
  findings hand off through `/found-issue-ownership`, not a direct write from
  this skill

## Constraints

- Read-only in all steps, via Read/Grep/Glob only. No writes, no Edit, no
  Bash execution, no external network calls, no hooks executed.
- ASI-02..10 are prose checklists, not runnable scanners — their verdicts
  require a human-grade reading of the target, not a pattern match; only
  ASI-01 has an automatable positive/negative pattern-match component.

## Idempotency Contract

Given the same target surface's content and the same ASI-01..10 mapping
(this file), the review produces the same per-risk verdicts and the same
overall Controls Covered count. ASI-01's pattern search is deterministic
text matching; no randomness; no time-dependent output.

## Governance Note

Per TC-EXT-012 (external-skill-import plan) and TC-EXT-025 (this import),
this skill was cleared by `/skill-scanner` before registration. It is a pure
prompt/methodology spec: no bundled script, no automated file operations, no
hooks, and no external network calls of its own. Its target scope is
deliberately narrowed to FF's autonomous-execution and skill-authoring
surfaces — the exact gap named in `docs/python-foss/security-model.md`'s
"Known Limitations" section — not a duplicate of Gate 7/8's existing
parser-level threat model.
