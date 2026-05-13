# AGENTS.md — Agent Operating Contract

**Document type:** Governance — Phase 0 Foundation
**Last reviewed:** 2026-05-05 (run027: Section X added — Hybrid Spec Retrieval Strategy rules)
**Authority:** This document is the non-negotiable operating contract for all agents (Claude, Codex, and any other automated executor) working in this repository. Every rule below must be followed without exception unless a specific exception is logged in the gap register with human approval.

---

## A. Identity and Role

**A1.** Claude in VS Code is the primary agent executor for all project phases. Claude is driven by this document, project commands in `.claude/commands/`, taskcards in `taskcards/`, and gate definitions in `docs/gates.md`.

**A2.** Codex (OpenAI API or GitHub Copilot agent mode) is an optional secondary agent. Codex is activated only when explicitly instructed by a human. Codex output that enters the repository must be tagged `generated_by: codex` in the artifact's front matter.

**A3.** An agent must not assume a role beyond what is assigned. Claude is an executor, not an approver. Claude never approves its own output as production-ready.

---

## B. Phase and Plan Verification

**B1.** Before taking any action, read `AGENTS.md` and verify the current phase in `plans/master-plan.md`.

**B2.** Before any format-specific work, read `plans/master-plan.md` and verify the current active format and gate status.

**B3.** An agent must not proceed if the current phase or gate status is unclear. Log a gap and wait for human clarification.

---

## C. Plan Mode vs. Execution Mode

**C1. In plan mode:**
- Do NOT create, edit, or delete any repository file (plan files in `C:\Users\prora\.claude\plans\` are excluded).
- Do NOT create evidence bundles, ZIP files, or any file outside the plan directory.
- Do NOT score formats, create acquisition packs, or commit anything.
- State the intended bundle path and manifest as text only.
- All plan-mode outputs are analysis only.

**C2. In execution mode:**
- Create files only in directories appropriate to the current phase (see phase rules below).
- After completing a phase or gate, create an evidence bundle in `.local/evidence-bundles/` and print `EVIDENCE_BUNDLE: <absolute Windows path to the zip>` as the final output line.
- Update `plans/master-plan.md` after every gate transition.
- Update `.local/artifact-index.yaml` after creating or modifying any artifact.

---

## D. Gate Rules

**D1.** No agent may self-approve a gate. All 11 gates require human review and explicit sign-off recorded in `registry/format-registry.yaml`.

**D2.** Before requesting gate approval, complete the self-challenge (Section I). Log the results.

**D3.** A format must not begin Stage N+1 work until Gate N has been passed and recorded.

**D4.** After human approval of a gate, update `plans/master-plan.md` with the gate history entry and the approver's name and date.

---

## E. Reuse-Before-Regenerate Rule

**E1.** Before creating any artifact, check `.local/artifact-index.yaml` for an existing entry with the same `artifact_id` or the same (`format_id`, `artifact_type`) combination.

**E2.** If the artifact exists and is current (all validity conditions met per `docs/acquisition-workflow.md` Section "Rule 2: Validity Conditions"), reuse it. Log `ARTIFACT_REUSED: <artifact_id>` in the run record.

**E3.** If the artifact is stale (any validity condition fails), refresh only the stale artifact. Do not regenerate all artifacts from scratch.

**E4.** If the artifact is missing, generate it.

**E5.** Never re-create everything from scratch when partial valid work exists.

---

## F. Visibility Classification Requirement

**F1.** Every artifact produced must have a visibility classification conforming to the schema in `docs/release-control.md`. Classification may be provided either (a) as YAML front matter in the file itself, or (b) as an entry in `.local/artifact-index.yaml`. See the Hybrid Classification Policy in `docs/release-control.md` for which files require which approach.

**F2.** Phase 0 governance files (docs, AGENTS.md, GOVERNANCE.md, ROADMAP.md, README.md, registry skeleton, `_readme.md` files, config files) are classified via `.local/artifact-index.yaml`. This is explicitly permitted; these files are not required to carry inline front matter.

**F3.** Phase 1+ acquisition artifacts (`acquisition-packs/<format-id>/`, `samples/by-format/`, `schemas/neutral-model/`, `src/`, `reports/`) must carry front matter directly in the file. Taskcards carry front matter by convention (the template provides it).

**F4.** Default to `visibility: internal` when uncertain. Never default to `visibility: public`.

**F5.** Do not change visibility from `internal` to `public` without human review and explicit approval.

**F6.** LLM-generated content defaults to `visibility: generated`. Changing to `public` requires human approval.

**F7.** LLM content that quotes spec text defaults to `visibility: evidence-only` pending legal review.

---

## G. Open-Source Release Boundary Rules

**G1.** Never assign `visibility: public` or `open_source_allowed: true` to commercial artifacts.

**G2.** Never include `evidence-only`, `generated`, or `blocked` artifacts in release manifests without human review.

**G3.** Commercial artifacts must never appear in open-source releases. This is an absolute rule.

**G4.** Commercial-tier source within `src/net/{format}/` must not be created until all of the following are true: (1) Gate 10 has been passed and recorded in `registry/format-registry.yaml`, (2) Decision DD3 (commercial isolation) is formally resolved, (3) commercial implementation taskcards for the format exist, and (4) an explicit commercial implementation execution prompt has been issued by a human. Gate 11 is commercial release readiness, not authorization to start writing commercial source. **Obsolete path:** `src/dotnet/commercial/` must not be created.

**G5.** `src/python/{format}/` and `src/net/{format}/` must not be created until all of the following are true: (1) Gates 1-9 are complete and Gate 9 human approval is recorded in `registry/format-registry.yaml`, (2) implementation taskcards for the format exist, and (3) an explicit Phase 4 implementation execution prompt has been issued by a human. Gate 10 is OSS readiness, not authorization to start writing product source. **Obsolete paths:** `src/python/open-source/` and `src/dotnet/open-source/` must not be created — they are not the target layout.

---

## H. LLM Endpoint Rules

**H1.** Consult `tools/llm/endpoints.yaml` and `tools/llm/model-selection.yaml` (when it exists) before any LLM API call.

**H2.** Never embed API keys, tokens, or credentials in any committed file. Keys go in `.env` (gitignored).

**H3.** Use environment variable names from `.env.example` when referencing authentication configuration.

**H4.** If the preferred model is unavailable, try the next model in the fallback order. If no approved model is available, stop the task and log `ENDPOINT_UNAVAILABLE: <task_id>` in `.local/llm-logs/`. Do not proceed with an unapproved model.

**H5.** Persist a run record in `.local/llm-logs/` for every LLM-assisted execution. See Section L for the run record format.

---

## I. Self-Challenge Requirement

Before marking any gate complete, any taskcard complete, or any significant work done, the agent must explicitly answer all fifteen questions:

1. Did I perform all required steps for this gate or task?
2. Is any required evidence missing?
3. Is any evidence I produced too thin to meet the criteria?
4. Did I rely on a secondary source where a primary source was required?
5. Did I create any file in a phase-forbidden directory?
6. Did I attempt to self-approve a gate?
7. Did I accidentally perform Phase N+1 work during Phase N?
8. Did I commit or push without explicit human instruction?
9. Did I preserve the rule that bundle inspection is required before the next prompt?
10. Did I leave any gap unlogged?
11. Did I read the relevant `/memory` files before this task?
12. Did I treat `/memory` as context only, not as operational authority?
13. Did I log any contradictions I found between `/memory` and the master plan?
14. Did I update `/memory` or create a memory-update taskcard when a trigger event occurred?
15. Am I asking for human review or approval, and if yes, did an independent agent verification sprint already occur in a separate session for this item? (See Section V.)

The agent must answer "no" to questions 4, 5, 6, 7, 8, and 10, and "yes" to questions 1, 2 (all evidence present), 3 (evidence is sufficient), and 9. For questions 11-14: if a memory read was required for the task type, answer "yes" to 11 and 12. If no contradiction existed, "yes" to 13 means "I confirmed there was no contradiction to log." For question 14, if no memory-update trigger event occurred during the task, the acceptable answer is "Not applicable — no trigger event occurred." For question 15: if asking for human review, the answer must be "yes — independent verification sprint completed." If not asking for human review, the acceptable answer is "Not applicable — no human review requested." If any required answer is wrong, the agent must log the gap and wait for human resolution before marking work complete.

---

## J. Commands and Skills

**J1.** When a project command exists in `.claude/commands/` for a task, use that command rather than re-implementing the task ad hoc.

**J2.** If no command exists for a required task and one should, log a gap (`Gx: missing command for <task>`) and continue with a manual approach this one time only.

**J3.** Log all commands used in the run record under `commands_used`.

---

## K. Persistence Requirements

**K1.** Every artifact produced must be registered in `.local/artifact-index.yaml` with full schema fields from `docs/release-control.md`.

**K2.** LLM run records must be written to `.local/llm-logs/` in JSONL format. See Section L for the format.

**K3.** Local-only artifacts (`.local/`) must never be committed to git.

**K4.** Committed artifacts must never contain full LLM prompt or response text. Use `prompt_id` and `response_hash` for traceability.

---

## L. Run Record Format

Every LLM-assisted execution must produce a JSONL run record entry in `.local/llm-logs/<session-date>-<run-id>.jsonl`:

```jsonl
{
  "run_id": "<uuid>",
  "agent": "claude|codex|other",
  "model": "<model-id>",
  "session_date": "<ISO-8601>",
  "phase": "0|1|2|3|4",
  "taskcard": "TC-NNNN|null",
  "gate": "1-11|null",
  "commands_used": ["/<command-name>"],
  "artifacts_produced": ["<relative/path/to/file>"],
  "artifacts_reused": ["<relative/path/to/file>"],
  "gaps_logged": ["<G-ID>"],
  "self_challenge_passed": true,
  "gate_approved": false,
  "bundle_path": "<.local/evidence-bundles/bundle-name.zip>|null"
}
```

---

## M. Gap Logging Requirement

**M1.** If an agent encounters an unknown, an ambiguity, a missing required artifact, or a situation not covered by existing rules, it must log a gap before proceeding.

**M2.** Gaps are logged by adding an entry to the Gap Register in `plans/master-plan.md` with: ID, description, owner, severity, what it blocks, resolution trigger, and whether it is a phase blocker.

**M3.** An unlogged gap that is discovered and not recorded is a governance violation.

---

## N. Phase-Forbidden Files

An agent must never create the following in Phase 0:

- Any file in `registry/format-registry.yaml` that contains a format entry (empty skeleton only).
- Any file in `acquisition-packs/` except the `_template/` directory.
- Any file in `samples/by-format/` (empty provenance skeleton only).
- `.github/workflows/` or any CI workflow files.
- Any file in `tests/fixtures/`, `tests/oracle/`, or `tests/fuzz/`.
- Any file in `reports/security/` or `reports/legal/` with format-specific content.
- Any product source code in `src/python/{format}/` or `src/net/{format}/` (Phase 4+ only).
- Any product source code in obsolete paths: `src/python/open-source/`, `src/dotnet/open-source/`, `src/dotnet/commercial/` — these paths must NEVER be created.
- Any LLM client script in `tools/llm/` (Phase 0: config template only).
- Any command file in `.claude/commands/` other than `_readme.md` (Phase 0: directory + readme only).

---

## O. Evidence Bundle Rules

**O1.** In plan mode: provide intended bundle path and manifest text only. Never create a bundle.

**O2.** In execution mode at phase or gate completion: create a ZIP evidence bundle in `.local/evidence-bundles/<phase>-<date>-<run-id>.zip`.

**O3.** The final output line must be exactly: `EVIDENCE_BUNDLE: <absolute Windows path to the zip>`

**O4.** Bundle must include: all files created during the phase, `git-status.txt`, `master-plan-snapshot.md`, and a phase-completion report.

**O5.** Bundle must NEVER include: `.env`, `.local/` contents, `visibility: blocked` artifacts, LLM prompts or responses, or API keys.

**O6.** Evidence bundle inspection before next prompt: before any next prompt (Phase 1 or otherwise) is issued, the latest bundle must be uploaded by the human, extracted, and inspected. Its contents must be challenged against the agent summary. No next prompt may rely on the agent summary alone. Bundles are evidence; summaries are hypotheses. See `plans/master-plan.md` Section 7.

---

## P. Commit and Push Rules

**P1.** An agent must never run `git commit` or `git push` unless the human explicitly says to commit or push in the current session.

**P2.** "Phase complete" does not mean "commit." Completing a phase produces an evidence bundle and awaits human review. Commits happen only when the human explicitly requests them.

**P3.** If the human approved a commit in a previous session, that approval does not carry over to the current session. Each commit requires explicit human instruction in the current session.

**P4.** Before any commit (when authorized): verify no `.env`, no secrets, no `.local/` contents, no `visibility: blocked` artifacts are staged.

---

## Q. Security Rules

**Q1.** Never introduce security vulnerabilities: no command injection, no XSS, no SQL injection, no path traversal, no hard-coded credentials.

**Q2.** Any code that parses untrusted file input must implement the mitigations in `docs/security.md` for all applicable threat categories.

**Q3.** For XML parsing: use `defusedxml` (Python) or `XmlReaderSettings` with `DtdProcessing.Prohibit` and `XmlResolver = null` (.NET). Never use default XML parser settings on untrusted input.

**Q4.** If security-relevant code is written, note which threat categories it addresses in the artifact front matter or inline comment.

---

## R. Acquisition Workflow Rules

**R1.** The spec is the authority. The reference tool (oracle) is a comparison aid. When spec and oracle disagree, document the discrepancy — do not silently prefer one.

**R2.** Prototype code is internal-only (`visibility: internal`). It is never promoted directly to `src/`. Product code is written from scratch using the prototype as a design reference.

**R3.** No format-specific acquisition pack may be created until Gate 1 has been passed for that format.

**R4.** No sample may be committed without a confirmed provenance entry in `samples/_provenance.yaml`.

---

## S. What This Document Does Not Cover

This document governs agent behavior. For human contributor rules, see `GOVERNANCE.md`. For gate pass criteria, see `docs/gates.md`. For legal classification, see `docs/legal-and-licensing.md`. For artifact visibility and release rules, see `docs/release-control.md`. For LLM endpoint configuration, see `docs/llm-endpoint-strategy.md`. For specification cache policy, see `docs/specification-cache.md`. For specification normalization policy, see `docs/specification-normalization.md`. For historical project context, decision rationale, and phase evolution, see `memory/README.md` and `memory/00-index.md`.

---

## T. Specification Cache Rules

**T1.** Before performing any spec-dependent acquisition work (Stage 2 evidence drafting, Stage 4 prototype development, Stage 5 neutral model design, Stage 6 oracle comparison), check whether a cached copy of the relevant specification exists at `.local/spec-cache/<format-id>/<version>/`. If the cache is missing, stale, or incomplete, stop and log the missing-spec condition (see T3-gap rule below). Do not proceed with spec-dependent work without a cached spec unless the task explicitly authorizes and explains the exception.

**T2.** Check before downloading. If `.local/spec-cache/<format-id>/<version>/spec-index.yaml` exists and `stale: false`, reuse the cached file. Do not re-download.

**T3 (Authorization Required for Download).** A spec download requires ALL of the following to be satisfied before any download may occur:
  - The current phase permits spec acquisition (Phase 1+; Phase 0 prohibits all downloads).
  - An explicit taskcard exists authorizing acquisition for this format.
  - The format's legal category has been reviewed and confirmed (Legal Categories 1-3 only; see `docs/legal-and-licensing.md`).
  - A canonical source URL has been identified and approved (standards body official page or stable archival URL; no mirrors).
  - The current execution prompt explicitly authorizes the download (the prompt must name the format, version, canonical URL, and state that acquisition is permitted).
  - Storage will be local-only under `.local/spec-cache/` (gitignored, never committed).
  - A `spec-index.yaml` entry recording source, version, license, SHA-256, and redistribution status will be written.

**T3-gap rule.** If a required spec is missing from the cache and download is not authorized by the current prompt and taskcard, the agent MUST stop, log the missing-spec condition as a gap in the gap register, and either create or update a taskcard for spec acquisition. The agent must NOT proceed with spec-dependent work until the gap is resolved by a subsequent authorized execution prompt.

**T4.** Only acquire specifications from their canonical source URL (standards body official download page or stable archival URL). Never download from third-party mirrors, CDNs, or unofficial sources. If the canonical URL is unavailable, log a gap — do not substitute an unofficial source.

**T5.** Before any download, confirm the format's legal category. Only specifications in Legal Categories 1-3 may be cached. Do not attempt to acquire Category 5 or 6 materials. Log the legal category in the `spec-index.yaml` entry.

**T6.** Specification files are `visibility: evidence-only`. They are local-only and must never be committed to git. The `spec-index.yaml` metadata (without file content) may appear in evidence bundles. Cached specs are evidence inputs, not release artifacts.

**T7.** After acquiring a specification, compute SHA-256 of the file and record it in `spec-index.yaml`. On every subsequent use, re-verify the SHA-256 matches. A hash mismatch means the file is stale — log a gap; do not silently re-download.

**T8.** Specification cache contents must never be quoted at length in committed artifacts. Quote only the minimum necessary excerpts (a specific clause or key term definition) when citing the spec in `spec-evidence.md`. Full spec text in LLM prompts defaults to `visibility: evidence-only` per Section F7.

**T9 (Remote LLM Restriction).** Full specification documents must not be sent to remote LLM endpoints by default. If spec content is needed in a remote LLM prompt, the request requires: (1) legal review of the spec's redistribution/transmission terms, (2) privacy/confidentiality review, and (3) explicit human authorization in the execution prompt. Local LLM endpoints may be preferred for spec analysis to avoid potential copyright or privacy concerns.

**T10 (No Automatic Re-download).** A stale or missing cache entry does not automatically authorize re-download. Refresh checks (via `refresh_check.py`) may mark entries stale. Re-download requires the same authorization conditions as T3. Refresh automation is limited to metadata updates (updating `last_verified`, setting `stale: true`); it never automatically re-fetches spec content.

---

## U. Memory Usage and Maintenance

### U1. Purpose of /memory

The `/memory` folder contains historical context, decision rationale, project evolution records, bundle-review lessons, and ChatGPT conversation memory preserved as Markdown files.

`/memory` is **context and rationale only**. It does not supersede `plans/master-plan.md`, `AGENTS.md`, or `GOVERNANCE.md`. When `/memory` conflicts with any of those documents or with the current repo state, the agent must log a gap and treat `plans/master-plan.md` as the operational authority until the contradiction is resolved by a human.

### U2. When Agents Must Read Memory

An agent must read the relevant memory files before:

- any complex planning session
- any phase transition
- any change to governance files (`AGENTS.md`, `GOVERNANCE.md`)
- any change to `plans/master-plan.md`
- any contradiction-resolution task
- any long-running task resumed after a gap in sessions
- any bundle-review healing run
- any major architecture or release-control amendment

### U3. Minimal Required Memory Files for General Work

Before any general task, read at minimum:

- `memory/README.md`
- `memory/00-index.md`
- `memory/02-standing-operating-rules.md`
- `memory/09-current-state-before-phase1.md`

### U4. Additional Memory Files by Task Type

Read these additional files when the task type matches:

| Task type | Additional memory file |
|-----------|------------------------|
| Architecture work | `memory/03-architecture-and-product-tracks.md` |
| Governance work | `memory/07-agent-governance-model.md` |
| Specification cache work | `memory/08-specification-cache-amendment.md` |
| Phase 0 review or healing | `memory/04-phase0-evolution-and-bundle-reviews.md` |
| Prompt writing | `memory/11-prompting-and-agent-style-rules.md` |
| Gap or risk review | `memory/06-gap-risk-and-healing-history.md` |
| Current-state verification | `memory/09-current-state-before-phase1.md` |

### U5. Memory Contradiction Rule

If `/memory` conflicts with `plans/master-plan.md`, `AGENTS.md`, `GOVERNANCE.md`, or the current repo state:

1. Log a gap in the Gap Register (`plans/master-plan.md`) with description, severity, and what it blocks.
2. Do not silently update any file based only on memory content.
3. Do not silently choose the memory version over the repo version.
4. Treat `plans/master-plan.md` as operational authority until the human resolves the contradiction.
5. If the contradiction requires file changes, produce a plan-mode proposal before touching any file.

### U6. Memory Maintenance Rule

After any of the following events, either update the relevant `/memory` file(s) in the same execution run (if explicitly in scope) or create a taskcard to update memory in the next run:

- phase acceptance
- gate transition
- major decision recorded in the decision register
- major gap discovery
- significant healing run
- architecture amendment
- specification cache policy change
- release control change
- governance change

### U7. Memory Content Restrictions

Do not store in `/memory`:

- secrets, API keys, or credentials
- private tokens or endpoint secrets
- raw LLM prompts or raw LLM responses
- copyrighted specification excerpts or downloaded standards text

### U8. Evidence Bundle Rule for Memory Changes

If any `/memory` file is changed during an execution run:

1. Include all changed `/memory` files in the evidence bundle under `repo/memory/`.
2. Include a `memory-sync-report.md` in the bundle's `bundle-metadata/` directory. It must list: files changed, reason for change, and which master-plan section or decision prompted the update.

### U9. Future /sync-memory Command

A future `/sync-memory` command or taskcard (`TC-0008`) should be created (Phase 1 or later) to automate memory consistency checks: compare `/memory` files against `plans/master-plan.md`, flag contradictions, and produce a `memory-sync-report.md`. This command does not exist yet. Do not implement it in Phase 0. Log it as a planned capability via TC-0008.

---

## V. Independent Verification Before Human Review

**V1. The Rule.** Any item that an agent produces as a candidate for human review — including gate scoring evidence, phase acceptance claims, commit acceptability, release readiness, or any other artifact requiring human approval — must first be verified by an independent agent in a separate verification sprint before the human is asked to review it.

**V2. What Counts as Human Review.** Human review is required (and therefore this rule applies) for:
- Any gate approval request (Gates 1–11)
- Any phase acceptance request (Phase 0, 1, 2, 3, 4)
- Any commit authorization request
- Any release authorization request
- Any scoring evidence presented for Gate 1 human approval
- Any governance amendment proposed for human sign-off

**V3. What Is a Verification Sprint.** A verification sprint is a separate execution session in which:
- A different run ID is used (e.g., run015 produces evidence; run016 verifies it)
- The verifying agent independently re-reads all source files referenced in the claim
- The verifying agent independently re-computes or re-checks all quantitative claims (scores, counts, file lists)
- The verifying agent produces a verification audit document in the evidence bundle
- If contradictions or errors are found: they are logged as gaps and corrected before the human is asked to review

**V4. Exception.** If the human explicitly waives this requirement in the execution prompt for the current session (e.g., "I am waiving the verification sprint requirement for this approval"), the agent may proceed without a prior verification sprint. The waiver must be explicit and in writing in the prompt. The agent must note the waiver in the run record.

**V5. Decision Register Reference.** This rule is recorded as DEC-034 in `plans/master-plan.md`.

---

## W. Specification Normalization Layer Rules

**W1. Three-Layer Model.** Specifications exist in three layers: (1) the original cached spec file (immutable, local-only, never modified), (2) normalized derived artifacts (local-only, machine-readable, reproducible from source), and (3) evidence pack claims (committed, cited, short excerpts only). Each layer has different rules. Do not conflate them.

**W2. Immutable Source Rule.** The cached spec file (e.g., `.local/spec-cache/fods/1.3/OpenDocument-v1.3-os-part3-schema.pdf`) must never be modified, deleted by automation, or committed. It is the single authoritative source for all spec-derived claims.

**W3. Hash Verification Before Normalization.** Before running any normalization tool, verify the cached spec file's SHA-256 against the value in `spec-index.yaml`. A hash mismatch means the file may be corrupted. Log gap G-NORM-002 and stop. Do not normalize a potentially corrupted file.

**W4. Normalized Artifacts Are Local-Only.** All normalized artifacts are stored under `.local/spec-cache/{format-id}/{version}/normalized/` (gitignored). They must never be committed unless an explicit exception is granted (metadata-only artifacts that contain no spec text and have redistribution rights confirmed). Full extracted text (`text.txt`, `pages.jsonl`) is always local-only.

**W5. Normalization Tools Must Not Call Remote Endpoints.** `normalize_pdf.py`, `build_citation_map.py`, `validate_normalized_spec.py`, and any other normalization tool must not call network endpoints or LLM endpoints. Normalization is a local-only operation.

**W6. Stale Normalized Artifacts.** If the source spec file changes (hash mismatch detected on re-verification), all normalized artifacts derived from it are stale. Do not use stale normalized artifacts. Regenerate from the re-acquired source before using.

**W7. Evidence Pack Citations.** When making a claim in a committed evidence file (e.g., `spec-evidence.md`), cite the source spec (source_url, sha256, page, section), not just the normalized artifact. Short excerpts (≤ 3 sentences) are acceptable under fair use. Full text is not.

**W8. Gate 4 Normalization Dependency.** `parser-requirements.yaml` (or an explicit human-approved waiver) is required before Gate 4 (Prototype) may begin. If normalization tooling is unavailable, log gap G-NORM-004 and document the waiver condition. See `docs/specification-normalization.md` for the full gate relationship model.

**W9. Evidence Classification.** Normalized artifacts support the following evidence classifications:
- `[SUPPORTED_BY_NORMALIZED_ARTIFACT]` — claim extracted from spec with citation (normalized artifact exists)
- `[SUPPORTED_BY_CACHED_SOURCE]` — claim verified directly from cached spec (no normalization needed)
- `[PLAUSIBLE_PENDING_VERIFICATION]` — technically plausible but not yet verified from source
- `[SPECULATION]` — not grounded in spec text; must not appear in production evidence

**W10. No LLM Calls With Spec Text to Remote Endpoints.** Full specification documents must not be sent to remote LLM endpoints. This extends T9 of this document. Spec text may be used with local-only LLM endpoints if redistribution is not implicated and explicit authorization is in the execution prompt.

See `docs/specification-normalization.md` for the complete policy. See `tools/spec-normalize/` for normalization tooling.

---

## X. Hybrid Spec Retrieval Strategy Rules

**X1. Three-Tier Retrieval Hierarchy.** Agents must use the following hierarchy when retrieving information from normalized spec artifacts. Lower tiers must be exhausted before falling through to higher tiers:
- **Tier 1 (Deterministic):** `query_normalized_spec.py --section` or `--element` or `--page`. Use when exact section ID, element name, or page is known.
- **Tier 2 (Lexical):** `query_normalized_spec.py --keyword` or `--sample-req`. Use when a relevant keyword or structured requirement category is known.
- **Tier 3 (Vector/Semantic):** `query_normalized_spec.py --semantic` (future, when implemented after TC-0016). Use only for complex natural-language questions that Tier 1 and Tier 2 cannot answer.

**X2. Format Isolation.** Every retrieval query must specify `--format-id <id>`. Agents must never use a FODS index to answer questions about another format, and vice versa. Format bleed is a governance violation.

**X3. Local-First.** All retrieval operates on locally cached artifacts in `.local/spec-cache/`. No remote calls are made during retrieval queries. If local artifacts are missing, log a gap and stop.

**X4. Provenance Requirement.** Every spec excerpt cited in an evidence artifact must include: section ID, page number, source SHA-256 hash, spec version, and retrieval method (tier1_section, tier1_element, tier2_keyword, tier2_sample_req, or tier3_vector). Evidence without provenance is incomplete.

**X5. Gate Evidence Restriction for Tier 3.** Tier 3 vector search may not be used in any Gate evidence artifact until TC-0016 (FODS Vector Index Pilot) is completed and independently verified. Until then, all Gate evidence must cite Tier 1 or Tier 2 results only.

**X6. Do Not Scan text.txt Directly.** Agents must not scan or grep `text.txt` directly for spec content. Use the query tools. Direct scanning bypasses citation tracking and source hash provenance.

**X7. Evaluation Before Implementation.** Tier 3 vector search must be evaluated (TC-0015) before it is implemented (TC-0016). TC-0016 must not proceed without TC-0015 evaluation report reviewed and approved by a human.

See `docs/spec-retrieval-strategy.md` for the complete strategy. See `taskcards/TC-0015-spec-retrieval-strategy-evaluation.md` and `taskcards/TC-0016-fods-vector-index-pilot.md` for evaluation and implementation taskcards.

---

## Y. Evidence Bundle Contract Rules

**Y1. Deterministic Builder Required.** All evidence bundles must be built using `tools/evidence/build_evidence_bundle.py`. Manual zip packaging (Python zipfile, shell zip, etc.) is prohibited for production evidence bundles.

**Y2. Contract Validation Required.** All evidence bundles must be validated using `tools/evidence/validate_evidence_bundle.py` before the `EVIDENCE_BUNDLE:` path is printed. An agent must not print `EVIDENCE_BUNDLE:` unless the validator outputs `BUNDLE_VALIDATION: PASS`.

**Y3. Contract File Required.** Every sprint must have a contract file in `tools/evidence/contracts/` or use the `base-run.yaml` contract. The contract specifies required repo files, required metadata files, forbidden patterns, and top-level folder constraints.

**Y4. Two Top-Level Folders Only.** Evidence bundles must contain exactly two top-level folders: `repo/` and `bundle-metadata/`. Any other top-level folder (including wrapper folders) is a hard failure.

**Y5. Forbidden Files Are Hard Failures.** Any file matching a forbidden pattern (`.local/`, `.env`, `text.txt`, `pages.jsonl`, `chunks.jsonl`, embeddings, vector DB, `__pycache__/`, etc.) found in the bundle causes `BUNDLE_VALIDATION: FAIL`.

**Y6. Missing Required Metadata Is a Hard Failure.** If any required metadata file listed in the contract is absent from `bundle-metadata/`, validation fails.

**Y7. Thin Bundles Not Acceptable.** A bundle with fewer metadata files than `min_metadata_count` in the contract fails validation.

**Y8. Emergency Exception.** Manual zipping is permitted only for emergency diagnostics explicitly labeled as "INVALID/UNVERIFIED — not a production evidence bundle" in the filename and contents.

See `tools/evidence/_readme.md` for tooling documentation. See `tools/evidence/contracts/` for contract definitions.

---

## Z. Run-State Authority Model (run041)

**Z1. No Self-Referential Commit Hash in Committed Files.** Committed files (master-plan.md, memory/09, etc.) must NOT contain `Latest commit: <hash>` or `Latest commit: PENDING` in their current-state sections. Recording the exact final Git HEAD in a committed file creates an infinite loop of housekeeping commits.

**Z2. Run-State Authority Model.** Committed files record `last_completed_run` (e.g., `run041`) and gate states. The exact final Git HEAD hash is authoritative **only** in evidence bundle metadata: `bundle-metadata/git-log.txt` and `bundle-metadata/git-status-final.txt`.

**Z3. PENDING Markers Must Be Absent After Final Commit.** Sprint-in-progress PENDING markers (`Latest commit: PENDING`, `changes pending commit`, `run\d+ changes pending`) must be removed before the final commit of each sprint. The consistency checker (`tools/evidence/check_current_state_consistency.py`) and evidence bundle validator (`--check-no-pending` flag) enforce this rule.

**Z4. Current-State Authority.** See `docs/current-state-and-evidence-authority.md` for the complete policy. See Section Y for evidence bundle contract rules.

---

## AA. Playbook Layer Rules (S-F2F-01 and S-F2F-02 Complete; Replay/Apply Not Yet Authorized)

**STATUS: Schema, policy, and read-only validation tool ACTIVE after S-F2F-02 (2026-05-08).
schemas/playbook/, docs/playbook-layer.md, and tools/playbook/validate_playbook.py exist.
validate_playbook.py is READ-ONLY — it writes nothing, has no replay behavior, no apply mode,
and no review queue output. Replay tools, apply mode, acquisition-pack playbooks, and family
playbooks remain unauthorized — see S-F2F-03 through S-F2F-06 for those phases.**

**AA0. Validation Tool Is Read-Only.** tools/playbook/validate_playbook.py validates YAML
files against schema and reports PASS/FAIL. It writes NO files, creates NO review queues,
does NOT replay operations, does NOT approve gates, does NOT replace DEC-034, and does NOT
replace human approval. Validation PASS is an evidence aid only. See docs/playbook-layer.md
Section 21 for full tool policy.

**AA1. Playbooks Are Execution Aids, Not Authority.** Playbook YAML files record what
operations were performed, what files were expected/produced, what validation commands
confirm correctness, and what evidence artifacts are required. They are execution aids.
`plans/master-plan.md` and evidence bundle metadata remain the sole operational authority
for gate state and project state. Playbooks never supersede master-plan.md or bundle metadata.

**AA2. Replay Engines: Deterministic First; No LLM Authority.** Replay engines must operate
in deterministic mode first. LLM fallback is not implemented in any S-phase sprint and is
never authoritative for specification interpretation or legal classification. No replay result
can substitute for DEC-034 independent verification or human gate approval.

**AA3. Review Queue Is Mandatory.** Any unresolved replay conflict must produce a review
queue item (severity: low | medium | high). Items with `severity: high` block apply mode.
The review queue is managed in `plans/review-queues/` and must be resolved by a human or
by explicit downgrade with documented rationale before apply mode is unblocked.

**AA4. Family Playbooks: Propose Reuse Only.** Family-level playbook files in
`acquisition-packs/_families/` propose reuse patterns with explicit `reuse_level`
classification (full | adapt | guide | new). Family playbooks never grant inherited gate
approval. Each gate for each format requires independent DEC-034 verification and human
approval regardless of family reuse level.

**AA5. Product Tools: Phase 4+ Only.** No product dependency tools (tools/product/),
product schemas (schemas/product/), or product source (src/python/, src/net/) are created
until product-track gates (Gate 10+) explicitly unlock source work and a human authorization
prompt names the specific sprint (S-F2F-07 or S-F2F-08). Secondary sprint documentation
(S-F2F-07: design docs only) requires Gate 8 PASSED as a hard prerequisite.

---

## AB. Discovered Gap Backlog Capture Rule (memory sprint 2026-05-08)

**AB1. Discovered Gaps Must Be Captured.** When any agent identifies a missing architectural
layer, missing capability, or structural weakness that is NOT authorized for immediate execution
in the current sprint, the agent MUST still create or update at least one durable local artifact:
(1) roadmap (`ROADMAP.md`), (2) backlog (master-plan.md Gap Register or Backlog section),
(3) taskcard (`taskcards/` — status: proposed_pending_human_approval), (4) memory file (`memory/`),
(5) risk/gap register in master-plan.md, or (6) future sprint recommendation. The gap must NOT
remain only in chat or only in an evidence bundle.

**AB2. Gap Entry Requirements.** Every captured gap entry must include: what the gap is,
why it matters, owner (human approval required to act), scope (what is missing, what is
blocked without it), and future trigger (what condition authorizes addressing it).

**AB3. Scope Boundary.** Capturing a gap does not authorize implementing it. Backlog taskcards
must be marked `proposed_pending_human_approval`. Implementation requires an explicit
human-authorized execution prompt naming the taskcard, sprint, and allowed files.

**AB4. Gap Register vs. Chat.** Gaps discovered in chat that are not in the Gap Register or
backlog taskcards are considered undocumented gaps — a governance violation equivalent to
"I noticed a gap but proceeded anyway without logging it" (see GOVERNANCE.md Section 10.5).

---

## AC. Format Understanding Layer and LLM/Embedding Strategy (memory sprint 2026-05-08)

**AC1. Format Understanding Layer is a Required Backlog Layer.** Before Phase 4 product source
begins for any format, a compiled Format Understanding Layer should exist (or be explicitly
waived). See `docs/format-understanding-layer.md`. The six per-format files are:
format-profile.yaml, verified-facts.yaml, implementation-requirements.yaml,
parser-strategy.yaml, security-surface.yaml, product-readiness.yaml.

**AC2. Product Source Must Not Precede Compiled Understanding (unless waived).** Creating
src/python/{format}/ or src/net/{format}/ before the relevant FUL files are available
requires explicit human waiver recorded in the decision register.

**AC3. LLM Use is Authorized for Future Governed Work (backlog).** Controlled use of LLMs
and embeddings via `llm.professionalize.com` is authorized for future sprints under governance.
Model families: GPT OSS, Qwen Next, embedding models. See `docs/llm-and-embedding-strategy.md`.
No production LLM calls in this memory sprint.

**AC4. LLMs Are Not Authority.** LLMs may propose facts, summaries, draft code, and suggest
edge cases. They are not gate approval authority, not spec authority, not legal authority, and
not replacement for citations, DEC-034, or human approval.

**AC5. Embeddings Are Retrieval, Not Truth.** Embedding indexes are controlled retrieval tools.
They are not truth authority. Every embedding entry must include provenance (source hash, source
path, spec version, chunk ID, model name, created_at, refresh policy). Preferred source content:
verified-facts.yaml and implementation-requirements.yaml, not raw uncited spec chunks.

**AC6. No Secrets in Repo.** API keys, tokens, and model credentials must not be committed.
Environment variables only. Redact all credentials from logs and evidence bundles.

**AC7. Non-XML Formats Are Backlog.** The immediate focus is XML-type formats (text_xml).
Non-XML adaptability (zip_container, binary_records, compound_document, delimited_text, json_like)
is backlog only. See `docs/format-representation-model.md`. The architecture must avoid
hardcoding XML-only assumptions, but non-XML implementation is not authorized without explicit
human prompt.

---

## AD. Planning and Agent Handoff Methodology (memory sprint 2026-05-08; updated memory-methodology-linkage-and-enforcement sprint 2026-05-08)

**AD0. Methodology Index Is the Entry Point.** Before plan review, plan creation, or execution handoff work, read `docs/agent-methodology-index.md`. This file links all local methodology docs, prompt templates, commands, and enforcement rules. It is the authoritative local entry point for planning sessions and fresh chat orientation. If methodology docs are missing or unlinked, stop with METHODOLOGY_NOT_ACCESSIBLE.

**AD1. Plans Must Be Challenged Before Execution.** When asked to create or review a plan, agents must challenge every claim against repo truth. Plans are not ready for execution until all 22 items on docs/plan-hardening-checklist.md pass. Plans that lack exact allowed paths, forbidden paths, validation commands, stop conditions, or evidence bundle requirements are not execution-ready.

**AD2. Agents Must Inspect Referenced Files.** Before acting on any plan, summary, or prompt, agents must read all referenced files. Agent summaries are not trusted until the referenced evidence bundles and repo files have been inspected in the current session.

**AD3. Captured Gaps Are Required.** Any missing architecture, capability, or structural weakness discovered during a sprint must be captured in at least one durable local artifact (roadmap, backlog, taskcard, or memory). Gaps must not remain only in chat or evidence bundles. See AGENTS.md Section AB.

**AD4. Agents Must Not Mix Sprint Streams.** MEMORY SPRINT work must not include gate changes. MAIN SPRINT commits must not include memory-only files. Each stream has its own evidence contract, commit, and bundle. Classify every dirty file by stream ownership before staging.

**AD5. No Broad Destructive Defaults.** Agents must not use git stash -u, git reset --hard, or git clean -fd as default or catch-all commands. If cleanup is needed, scope it exactly and document the reason.

**AD6. Evidence-Producing Sprints Must Print Bundle Path.** Every sprint that produces an evidence bundle must print, as its final line: EVIDENCE_BUNDLE: <absolute Windows path to zip>. No other line may follow it.

**AD7. No Push Without Explicit Authorization.** Push is prohibited unless the human explicitly authorizes it in the current session. Default is no push.

**AD8. Before Converting Prose Plan, Use Methodology Docs.** Before converting a prose plan to an execution handoff, use `docs/planning-methodology.md` and `docs/plan-hardening-checklist.md`. Before writing a handoff prompt, use `docs/agent-execution-handoff-standard.md`. Before reviewing an evidence bundle and producing the next prompt, use `.claude/commands/evidence-review-next-prompt.md` or its template.

**AD9. Agents Must Not Rely on Sprint Summaries Alone.** When evidence bundles and repo files are available, they are the truth source. Sprint summaries are hypotheses. Read the actual files.

**AD10. No Methodology Skip.** Skipping plan hardening, independent verification, or evidence bundle validation is a governance violation. These steps are required infrastructure, not optional ceremony.

---

## AE. Git Safety, Dirty-State, and Metadata Isolation Rules (GOV-REVERT-001)

**AE1. No Stash to Hide Work.** Agents must not use `git stash` to hide unrelated work or to make the working tree appear clean. If unrelated dirty work exists, classify it by sprint ownership and stop or produce a blocker bundle. Clean-tree pressure from evidence tooling is not a valid reason to hide changes.

**AE2. No Cleanup Reverts for Cleanliness.** Agents must not use `git reset`, `git restore`, `git checkout --`, or `git clean` to make the tree clean. Any rollback must be explicitly authorized, exact-path scoped, and documented.

**AE3. Exact-Path Staging Only.** Every sprint must stage exact authorized paths only. `git add .` and `git add -A` are forbidden for agent work.

**AE4. One Active Execution Sprint Per Worktree.** Concurrent sprint streams must not share a single worktree unless the prompt explicitly allows it and dirty-state classification is complete. Verification sprints may inspect read-only, but must not clean up another sprint's files.

**AE5. Active Sprint Lock Convention.** Execution sprints use `.local/active-sprint-lock.json` as the local-only lock convention. Fields: `sprint_id`, `sprint_type`, `owner_agent`, `started_at`, `allowed_paths`, `forbidden_paths`, and `status`. Agents must stop if a lock exists for another active mutation sprint unless the prompt explicitly authorizes read-only verification. Stale lock handling requires human review or explicit prompt authorization.

**AE6. Sprint Metadata Isolation.** New evidence bundles must use sprint-specific metadata directories under `.local/<sprint-id>-metadata/`. Root `bundle-metadata/` is a stale staging risk and must not be used for new bundles. Bundle metadata identity files must agree on the primary sprint ID.

**AE7. Required Safety Artifacts.** Every future execution sprint must include `git-safety-policy-check.md` in metadata and must report `NO_STASH_RESET_RESTORE_CLEAN_USED: YES` in the final response.

---

## AF. Always-Updated Enforcement Model (memory sprint 2026-05-09)

**AF1. Mandatory Closeout Phase.** Every execution sprint must include a mandatory closeout
phase before the evidence bundle is built. The closeout phase is not optional. Failure to
complete it means the sprint is INCOMPLETE.

**AF2. Level 6 Session Hint Files Must Be Updated.** After every execution sprint, update all
Level 6 session hint files (memory/09-current-state-before-phase1.md, .claude/settings.json,
docs/fresh-chat-continuity-brief.md) to reflect the sprint's actual final state.

**AF3. Gate Changes Require Multi-File Updates.** If gate status changes in a sprint, update
all three sources consistently: registry/format-registry.yaml, plans/master-plan.md header,
and all pack.yaml files for the affected format. All three must agree before bundle build.

**AF4. CURRENT_STATE_CONSISTENCY Must Pass.** Run python tools/evidence/check_current_state_consistency.py
before building the evidence bundle. Confirm CURRENT_STATE_CONSISTENCY: PASS before proceeding.

**AF5. Pending Propagation Reports for Blocked Files.** When a sprint cannot safely update a
file because another stream owns it, create reports/propagation/{sprint-id}-propagation-pending.md
recording: sprint_id, blocked_file, blocking_stream, propagation_content, follow_up_sprint.

**AF6. Authority Level Hierarchy.** When sources conflict, higher authority wins:
Level 1 (registry) > Level 2 (master-plan) > Level 3 (taskcards) > Level 4 (evidence bundles)
> Level 5 (ROADMAP/README) > Level 6 (session hints) > Level 7 (derived mirrors).
See docs/current-state-and-evidence-authority.md Section 8 for the full hierarchy.

**AF7. No Memory/16+ Without GOV-006.** No new memory/NN files may be created beyond memory/15
without GOV-006 authorization. See taskcards/GOV-006-documentation-information-architecture-standardization.md.

**AF8. FFSM Is Design Only.** No tools/state/, tools/llm/, or tools/retrieval/ code may be
created without explicit human-authorized taskcards. See memory/15 for design direction.


## Section AF -- Always-Updated Enforcement Model (Added memory-ai-direction-sync-2026-05-09)

Every execution sprint must include a mandatory closeout phase before the evidence bundle is built.
This section records the enforcement rules that apply to ALL execution agents.

**AF1. Mandatory Closeout Phase.** Every execution sprint must update all Level 6 session hint files
(memory/09-current-state-before-phase1.md, .claude/settings.json, docs/fresh-chat-continuity-brief.md)
before building the evidence bundle. Skipping this step is a governance violation.

**AF2. Level 6 Session Hint Files.** After any sprint that changes gate status, sprint state, or
strategic direction, the Level 6 files must reflect the actual new state. Stale hints that contradict
authority state (registry, master-plan) are governance violations.

**AF3. Gate Changes Require Multi-File Consistency.** If a gate status changes, the agent must update
registry/format-registry.yaml, plans/master-plan.md header, and all pack.yaml files for the affected
format. All three must agree before the evidence bundle is built.

**AF4. CURRENT_STATE_CONSISTENCY Must Pass.** The agent must run
python tools/evidence/check_current_state_consistency.py and confirm CURRENT_STATE_CONSISTENCY: PASS
before building the evidence bundle. If it fails, fix the inconsistency first.

**AF5. Pending Propagation Reports.** When a sprint cannot safely update a file because another
active stream owns it, the agent must create
reports/propagation/{sprint-id}-propagation-pending.md with: sprint_id, blocked_file,
blocking_stream, propagation_content, follow_up_sprint. Do not silently skip the update.

**AF6. Authority Hierarchy.** The seven-level authority hierarchy applies to all file updates:
Level 1 (registry) > Level 2 (master-plan) > Level 3 (taskcards) > Level 4 (evidence bundles) >
Level 5 (ROADMAP/README) > Level 6 (session hints) > Level 7 (derived mirrors).
Level 6 and 7 must match Level 1-4 after every sprint closeout.

**AF7. No memory/16+ Without GOV-006 Authorization.** No new numbered memory files may be created
beyond memory/15 without explicit authorization from the documentation standard (GOV-006) or an
explicit human sprint prompt. This prevents memory sprawl.

**AF8. FFSM Is Design Only.** The Format Factory State Manager (FFSM) described in memory/15 and
docs/current-state-and-evidence-authority.md Section 8 is design direction only. No tools/state/ code
exists. Do not create FFSM code without an explicit authorized taskcard and sprint prompt.

**AF9. Commercial Product Readiness Requires Capability Model.** Agents must not claim commercial
product readiness from Tier 0 parser success alone. Current `src/net/fods/` and `src/net/fodt/` are
Tier 0 streaming parsers (capability level C2). Commercial readiness requires C7+ (load-edit-save-convert)
per `docs/commercial-product-capability-model.md`. Gate 11 approval or release readiness must be tied
to the capability model, not parser test pass counts.

**AF10. Gate Approval Tied to Capability Model.** Gate 11 human review packets must reference
`docs/commercial-product-capability-model.md` and state the achieved capability level (C0-C10).
If user requirements conflict with current plan/gate status, agents must pause approval/publish work
and run a direction rebaseline sprint before proceeding.

**AF11. Commercial Direction Override.** If a human clarifies or changes commercial product
requirements, agents must update authority files (registry, master-plan, capability model) before
continuing gate or implementation work. Product direction and gate integrity override speed.
Controlled swarm execution is preferred for larger work, but must preserve product direction.

**AF12. AI Is Permitted and Encouraged — Within Governance.** AI (LLMs, agents, embeddings) may be
used to accelerate implementation when it improves speed and quality. AI output is not authority
until validated per `docs/ai-usage-operating-model.md`. Embeddings and RAG are retrieval aids,
not truth — see `docs/spec-retrieval-and-rag-policy.md`. LLM calls must be logged in
`.local/llm-logs/` (AGENTS.md §H5) when used for repo-changing work. AI-generated code, tests,
and documentation must pass the same validation gates as human/agent work. No secrets may be sent
to AI. No gate approval may be delegated to AI. Full AI operating model: `docs/ai-usage-operating-model.md`.
