# GOVERNANCE.md — Human Governance Rules

**Document type:** Governance — Phase 0 Foundation
**Last reviewed:** 2026-05-04 (run011: Sections 6.1 and 6.5 updated for format-first source layout)
**Authority:** This document governs the behavior of human contributors to format-factory. It defines decision-making authority, gate approval processes, visibility classification policy, and the rules that protect the open-source/commercial boundary.

---

## 1. Living Master Plan Authority

**1.1.** `plans/master-plan.md` is the single authoritative document for operational project state. It records the current phase, all gate histories, active work, decisions, gaps, and risks.

**1.2.** No other document supersedes `plans/master-plan.md` for operational status. `docs/architecture.md` is the design reference; `plans/master-plan.md` is the execution record. The `/memory` folder provides historical context and rationale from the ChatGPT conversation that shaped the project; it is not operational authority and does not supersede `plans/master-plan.md`. If `/memory` content conflicts with `plans/master-plan.md`, `AGENTS.md`, or `GOVERNANCE.md`, the conflict must be logged as a gap and resolved through normal governance — agents and humans must not silently defer to memory over the master plan.

**1.2a.** Memory content restrictions for human contributors: do not store secrets, API keys, raw LLM prompts, raw LLM responses, or copyrighted specification excerpts in `/memory`. `/memory` is internal documentation only and must not be published.

**1.3.** Human contributors must update `plans/master-plan.md` when they make decisions that affect project state: approving gates, resolving gaps, accepting risks, changing phase assignments.

**1.4.** Agents update `plans/master-plan.md` at every gate transition. Human contributors verify that the update is accurate before proceeding.

**1.5.** `plans/master-plan.md` must never be treated as a snapshot. It is always the current truth.

---

## 2. Gate Approval Process

**2.1.** All 11 gates require human approval. No agent, script, or automated process may approve a gate.

**2.2.** To approve a gate, the human reviewer must:
1. Verify that all required artifacts for the gate exist and are substantive (not placeholders).
2. Verify that the self-challenge answers from the agent are complete and credible.
3. Record approval in `registry/format-registry.yaml`: set `gate_N_status: passed`, `gate_N_approved_by: <your name>`, `gate_N_approved_date: <ISO-8601 date>`.
4. Update `plans/master-plan.md` with the gate history entry if the agent has not already done so.

**2.3.** A gate that has been marked passed must not be re-opened without a formal decision recorded in the decision register. If artifacts are later found to be deficient, create a gap entry and a resolution path rather than silently rolling back gate status.

**2.4.** The project lead may approve Gates 1-3 without an additional reviewer in Phase 1-2. Gates 7 (fuzz) and 8 (security) require the reviewer to be technically qualified to assess the security claims.

---

## 3. Release Control Policy

**3.1.** No artifact may be included in any release (open-source or commercial) without a confirmed `visibility` classification in its front matter.

**3.2.** No artifact with `visibility: blocked` may be released under any circumstances.

**3.3.** No artifact with `visibility: commercial` may appear in an open-source release.

**3.4.** No unreviewed `visibility: generated` artifact may appear in any public release.

**3.5.** Every release requires a human-reviewed release manifest before the release build is published. The manifest must be reviewed by the project lead.

---

## 4. Visibility Classification Policy

**4.1.** The default visibility for any new artifact is `internal`. Never default to `public`.

**4.2.** Changing visibility from `internal` to `public` requires: (1) human review, (2) license confirmation, (3) provenance confirmed (if required by the artifact type).

**4.3.** Changing visibility from `internal` to `commercial` requires: (1) commercial product lead approval, (2) Decision DD3 resolved.

**4.4.** An agent may never change visibility from `internal` or `generated` to `public` without an explicit human decision.

**4.5.** Six visibility classes are defined in `docs/release-control.md`: `public`, `internal`, `commercial`, `evidence-only`, `generated`, `blocked`. Every committed artifact must carry exactly one.

---

## 5. Open-Source Release Requirements

Before any Gate 10 (OSS release) is approved, the project lead must verify:

**5.1.** Release manifest reviewed: no `commercial`, `blocked`, or unreviewed `generated` artifacts are present.

**5.2.** Boundary check passed: the open-source solution has been built in isolation. Zero commercial namespace references found.

**5.3.** All samples used in tests have `provenance_status: confirmed` with a compatible open-source license (CC0, CC-BY, CC-BY-SA, Apache 2.0, MIT, or public domain).

**5.4.** All LLM-generated content in the release has been human-reviewed and visibility has been changed from `generated` to `public`.

**5.5.** All format legal notes confirm at minimum Category 1 or Category 2 with appropriate documentation.

---

## 6. Commercial Material Requirements

**6.1.** Commercial-tier source within `src/net/{format}/` must not be created until all of the following are true: (1) Gate 10 has been passed and recorded in `registry/format-registry.yaml`, (2) Decision DD3 (commercial isolation) is formally resolved by the project lead, (3) commercial implementation taskcards for the format exist, and (4) an explicit commercial implementation execution prompt has been issued. Gate 11 is commercial release readiness, not authorization to start writing commercial source. **Obsolete path:** `src/dotnet/commercial/` must not be created. The target layout is `src/net/{format}/`.

**6.2.** Commercial source code review by the commercial product lead is required before Gate 11 approval.

**6.3.** Legal review of commercial license terms is required before commercial release.

**6.4.** The one-way dependency rule must be verified: no open-source project references any commercial project.

**6.5.** `src/python/{format}/` and `src/net/{format}/` must not be created until: (1) Gates 1-9 are complete and Gate 9 human approval is recorded in `registry/format-registry.yaml`, (2) implementation taskcards for the format exist, and (3) an explicit Phase 4 implementation execution prompt has been issued. Gate 10 is OSS/product readiness, not the start of implementation. **Obsolete paths:** `src/python/open-source/` and `src/dotnet/open-source/` are not the target layout and must not be created.

---

## 7. LLM-Generated Content Rules

**7.1.** All LLM-generated content is tagged with `generated_by: <model-id>` in the artifact's front matter.

**7.2.** LLM-generated content defaults to `visibility: generated`. Human review is required to change it to `public` or `internal`.

**7.3.** LLM-generated content that quotes substantial spec text defaults to `visibility: evidence-only` pending legal review.

**7.4.** LLM prompts and responses are stored locally only (`.local/llm-cache/`, gitignored). They must never be committed.

**7.5.** A reviewer can verify LLM-generated artifacts using the `prompt_id`, `response_hash`, and committed prompt templates — without needing the full prompt or response text.

---

## 8. Prompt and Response Handling

**8.1.** Prompts and LLM responses may contain spec text with copyright implications. They must never be committed.

**8.2.** The retention period for `.local/llm-cache/` files is the duration of the project phase in which they were produced. They may be deleted after the phase is complete and all artifacts have been validated.

**8.3.** Prompts and responses must never contain personal data (PII). If a sample being analyzed contains PII, it must be redacted before inclusion in any prompt.

**8.4.** Full policy details are in `docs/llm-endpoint-strategy.md`.

---

## 9. Gate Approval Authority

| Gate | Required Approver | Minimum Qualifications |
|---|---|---|
| Gate 1 (Scoring) | Project lead | Knowledge of scoring model |
| Gate 2 (Evidence) | Project lead (fast-path) or legal reviewer | Legal classification awareness |
| Gate 3 (Samples) | Project lead | License awareness |
| Gate 4 (Prototype) | Project lead + technically qualified reviewer | Parser correctness assessment |
| Gate 5 (Neutral Model) | Project lead | Data modeling review |
| Gate 6 (Oracle) | Project lead | Format knowledge |
| Gate 7 (Fuzz) | Technically qualified security reviewer | Security testing background |
| Gate 8 (Security Review) | Technically qualified security reviewer | Parser security background |
| Gate 9 (Product Mapping) | Project lead | Product planning |
| Gate 10 (OSS Release) | Project lead | Release and license review |
| Gate 11 (Commercial Release) | Project lead + commercial lead | Commercial product decision authority |

---

## 10. Gap and Risk Management

**10.1.** Any gap discovered by any contributor (human or agent) must be logged in the Gap Register in `plans/master-plan.md` before the contributor proceeds. An unlogged gap is a governance violation.

**10.2.** Each gap entry requires: ID, description, owner, severity, what it blocks, resolution trigger, and whether it is a phase blocker.

**10.3.** Risks are logged in the Risk Register in `plans/master-plan.md` with: ID, description, severity, phase affected, mitigation, owner, and re-evaluation trigger.

**10.4.** The project lead reviews the gap and risk registers at each phase transition and before each gate approval.

**10.5.** "I noticed a gap but proceeded anyway without logging it" is a governance violation for both humans and agents.

---

## 11. Credential and Secret Handling

**11.1.** No API key, token, credential, or secret value may ever appear in a committed file.

**11.2.** If a credential is found in a committed file, it is treated as compromised and must be rotated immediately. The commit must not be pushed until the credential is removed from history.

**11.3.** `.env` is gitignored and must never be committed. `.env.example` (committed) contains only placeholder variable names.

**11.4.** CI workflows (Phase 4+) use GitHub Secrets for authentication, not `.env` files.

---

## 12. Conflict Resolution

**12.1.** If an agent's output conflicts with a policy document, the policy document governs.

**12.2.** If two policy documents conflict, the project lead makes a formal decision recorded in the decision register.

**12.3.** If a human contributor and an agent disagree on a classification or approach, the human decision governs. The agent's reasoning should be logged for reference.

**12.4.** The decision register in `plans/master-plan.md` is the authoritative record of all project decisions. Verbal or undocumented decisions do not override documented decisions.

---

## 13. Evidence Bundle Inspection Requirement

**13.1.** Before issuing any next prompt (Phase 1 or otherwise), the human must upload the latest evidence bundle, extract it, and inspect its contents against the agent summary. No next prompt may rely on the agent summary alone.

**13.2.** If the bundle contents do not match the agent summary, the discrepancy must be logged as a gap and a targeted healing prompt must be issued — not a Phase 1 or advancement prompt.

**13.3.** This rule is non-negotiable. An agent that says "work is complete" has produced a hypothesis. The bundle is the evidence. The human is the judge.

**13.4.** See `plans/master-plan.md` Section 7 (Evidence Bundle Inspection Rule) for the step-by-step inspection process.

---

## 14. Commit Policy

**14.1.** No commit is made unless the human explicitly requests it in the current session. "Phase complete" does not authorize a commit.

**14.2.** An agent must never run `git commit` or `git push` on its own initiative, even if it believes the work is complete.

**14.3.** Before any authorized commit: verify no `.env`, no secrets, no `.local/` contents, no `visibility: blocked` artifacts are staged.

**14.4.** Authorization to commit in a previous session does not carry over. Each session requires explicit human instruction to commit.

---

## Relationship to Other Documents

- `AGENTS.md` — non-negotiable operating rules for agents
- `plans/master-plan.md` — single authoritative operational state
- `docs/gates.md` — gate pass criteria and artifact requirements
- `docs/release-control.md` — visibility classifications and release policy
- `docs/legal-and-licensing.md` — format legal classification and license policy
- `docs/llm-endpoint-strategy.md` — LLM endpoint and prompt handling policy
