# GOVERNANCE.md — Human Governance Rules

**Document type:** Governance — Phase 0 Foundation
**Last reviewed:** 2026-05-05 (run027: Section 17 added — Hybrid Spec Retrieval Strategy governance)
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

## 15. Independent Verification Before Human Review

**15.1.** Any item that an agent produces as a candidate for human review must first pass an independent agent verification sprint in a separate execution session before the human is asked to review it.

**15.2.** This requirement applies to: gate scoring evidence, phase acceptance claims, commit acceptability, release readiness, and any other item requiring human approval.

**15.3.** The human must not be asked to approve, accept, or sign off on any agent-produced claim until an independent verification sprint has been completed and a verification audit document has been produced in the evidence bundle.

**15.4.** The human may explicitly waive this requirement for a specific item by stating so in the execution prompt for the current session. The waiver must be explicit, in writing, and named to the specific item being waived. The agent must record the waiver in the run record.

**15.5.** This rule is recorded as DEC-034 in `plans/master-plan.md` and governed in detail by AGENTS.md Section V.

---

## 16. Specification Normalization Layer Governance

**16.1.** Normalized spec artifacts (text extractions, section maps, citation maps) are local-only derived materials. They are never the authoritative source. The cached spec PDF is the authority.

**16.2.** Human reviewers must not treat normalized artifact content as the primary spec source. When in doubt, verify against the original cached PDF and its SHA-256 hash.

**16.3.** Evidence pack files (committed to git) must not contain full extracted spec text. Short cited excerpts (≤ 3 sentences with page/section citation) are acceptable. Full text remains local-only under `.local/spec-cache/{format-id}/{version}/normalized/`.

**16.4.** Before Gate 4 (Prototype) may begin, `parser-requirements.yaml` must exist under the normalized directory, OR a human-approved explicit waiver must be logged as a gap with gap ID G-NORM-004. This is a hard gate dependency.

**16.5.** Normalization tools (`normalize_pdf.py`, `build_citation_map.py`, `validate_normalized_spec.py`) must not call remote network endpoints or LLM endpoints. Normalization is a local, deterministic operation. Any normalization tool that calls a remote endpoint is a governance violation.

**16.6.** A human may approve redistribution of specific normalized content if the spec's redistribution terms permit it and legal review has confirmed this. This approval must be recorded explicitly (decision register or gate approval record). Without such approval, all normalized text content is local-only.

See `docs/specification-normalization.md` for full policy. See AGENTS.md Section W for agent rules.

---

## 17. Hybrid Spec Retrieval Strategy Governance

**17.1.** Agents must follow the three-tier retrieval hierarchy defined in `docs/spec-retrieval-strategy.md`: Tier 1 (deterministic) → Tier 2 (lexical) → Tier 3 (vector/semantic, future). Lower tiers must be exhausted before advancing to a higher tier.

**17.2.** Tier 3 (vector search) must not be implemented until TC-0015 (evaluation) is completed and the evaluation report is reviewed and approved by a human. Human approval of TC-0015 is required before TC-0016 (implementation) begins.

**17.3.** Every normalized spec query used in a Gate evidence artifact must include provenance: section ID, page, source SHA-256 hash, spec version, and retrieval method. Evidence without provenance is incomplete and cannot be submitted for Gate review.

**17.4.** Format isolation is mandatory. No index, embedding, or query result from one format may be used as evidence for another format. Cross-format retrieval bleed is a governance violation.

**17.5.** The vector index (when built) is local-only and must never be committed to git. It falls under the same local-only policy as normalized text artifacts.

See `docs/spec-retrieval-strategy.md` for full strategy. See AGENTS.md Section X for agent rules.

---

## 18. Evidence Bundle Policy

**18.1.** Evidence bundles must be built using `tools/evidence/build_evidence_bundle.py` and validated using `tools/evidence/validate_evidence_bundle.py`. Manual zip packaging is prohibited for production bundles.

**18.2.** The `EVIDENCE_BUNDLE:` path must not be printed unless the validator reports `BUNDLE_VALIDATION: PASS`.

**18.3.** Every sprint must use a contract file (in `tools/evidence/contracts/`). Missing required metadata, forbidden files, or incorrect top-level folder layout are hard failures.

**18.4.** Thin evidence bundles (below `min_metadata_count`) are not acceptable for Gate reviews or phase transitions.

See AGENTS.md Section Y for agent-specific evidence bundle rules.

---

## 19. Run-State Authority and Current-State Consistency (run041)

**19.1.** The exact final Git HEAD hash must NOT be recorded in committed files (master-plan.md, memory/09, etc.). Doing so creates a self-referential loop requiring an infinite series of housekeeping commits.

**19.2.** Committed files record `last_completed_run` and gate states. The final Git HEAD is authoritative only in evidence bundle metadata (`bundle-metadata/git-log.txt`, `bundle-metadata/git-status-final.txt`).

**19.3.** Sprint-in-progress PENDING markers (`Latest commit: PENDING`, `changes pending commit`) must be absent from committed current-state files. The consistency checker (`tools/evidence/check_current_state_consistency.py`) enforces this.

**19.4.** The complete policy is documented in `docs/current-state-and-evidence-authority.md`. See AGENTS.md Section Z for agent-specific rules.

---

## Section 20 — Playbook Layer Governance (S-F2F-01 and S-F2F-02 Complete; Replay/Apply Unauthorized)

**STATUS: Playbook schema, policy, and read-only validation tool ACTIVE after S-F2F-02
(2026-05-08). schemas/playbook/, docs/playbook-layer.md, and tools/playbook/validate_playbook.py
exist. Replay engine, apply mode, acquisition-pack playbooks, and family playbooks remain
unauthorized until S-F2F-03 through S-F2F-06 are explicitly authorized.**

**20.0. Validation Tool Is Evidence-Eligible Input Only.** tools/playbook/validate_playbook.py
output (PLAYBOOK_VALIDATION: PASS) is an evidence-eligible input. It is NOT gate approval,
NOT a DEC-034 substitute, and NOT a human approval record. The tool writes no files.

**20.1.** Playbook YAML files are internal artifacts. They are NOT evidence, NOT operational
authority, and NOT gate approval substitutes. `plans/master-plan.md` and evidence bundle
metadata are the sole operational authority.

**20.2.** Replay reports produced by the dry-run replay engine are evidence-eligible inputs
to the evidence bundle. They are informational and subject to the same DEC-034 independent
verification requirement as all other evidence. They are NOT substitutes for gate approval.

**20.3.** Review queue items with `severity: high` require human resolution before apply mode
is unblocked for the affected format. An agent must NOT proceed with apply mode when any
unresolved `severity: high` item exists in `plans/review-queues/` for that format.

**20.4.** Family reuse claims require explicit `reuse_level` classification in the family
playbook file: `full` (exact reuse), `adapt` (minor changes), `guide` (major changes), or
`new` (family pattern only). No gate approval is inherited from a family playbook regardless
of reuse_level. Each gate for each format requires independent DEC-034 + human approval.

**20.5.** No gate can pass purely through automated playbook replay. Independent DEC-034
verification and explicit human approval are always required for any gate transition,
regardless of replay success or family reuse level.

---

---

## 21. Discovered Gap Backlog Capture Rule (memory sprint 2026-05-08)

**21.1.** Any gap discovered by any contributor (human or agent) that is not authorized for
immediate execution must be captured in at least one durable local artifact before the session
ends: the Gap Register in `plans/master-plan.md`, a `taskcards/` entry with status
`proposed_pending_human_approval`, a `memory/` file update, or the roadmap. Discovered gaps
must not remain only in chat or only in evidence bundles.

**21.2.** This rule extends Section 10.1 (Gap Logging Requirement) to explicitly cover gaps
that are out of scope for the current sprint. The gap must be recorded even if no resolution
is authorized or planned.

**21.3.** Each captured gap entry (wherever recorded) must include: description, owner,
what it blocks, reason it is not in scope now, and future trigger.

---

## 22. Format Understanding Layer, LLM Strategy, and Non-XML Adaptability (memory sprint 2026-05-08)

**22.1. Format Understanding Layer is a Required Planning Layer.** Before Phase 4 product
source begins for any format, a compiled Format Understanding Layer should be in place or
explicitly waived by the project lead. See `docs/format-understanding-layer.md` for the
plan. The six per-format target files are: format-profile.yaml, verified-facts.yaml,
implementation-requirements.yaml, parser-strategy.yaml, security-surface.yaml,
product-readiness.yaml. These are in backlog (FUL-001 through FUL-005).

**22.2. Controlled LLM and Embedding Use Authorized for Future Work.** The project lead
authorizes controlled use of `llm.professionalize.com` model families (GPT OSS, Qwen Next,
embedding models) for future governed format understanding work. This authorization does not
authorize production LLM calls in any sprint unless an explicit execution prompt names the
taskcard, model family, and allowed outputs. See `docs/llm-and-embedding-strategy.md`.

**22.3. LLMs Are Not Gate Approvers or Spec Authority.** No LLM output becomes a verified
fact without citation and deterministic or human verification. LLMs may not approve gates,
classify legal status, or replace human review or DEC-034.

**22.4. Embeddings Are Controlled Retrieval.** Embedding indexes (when built) must use
verified-facts-first content strategy, include full provenance metadata, and must not be
treated as truth authority. See AGENTS.md Section AC.

**22.5. Non-XML Adaptability Is Explicit Backlog.** The current pipeline is validated for
XML-type formats (text_xml). Non-XML formats (zip_container, binary_records, compound_document)
are backlog. The pipeline architecture must avoid hardcoding XML-only assumptions, but no
non-XML implementation is authorized without explicit human prompt. See
`docs/format-representation-model.md`.

**22.6. Non-Aspose Candidate Registry Is Planned.** A registry of formats underserved by
Aspose products will be maintained at `registry/non-aspose-format-candidates.yaml` (future).
Candidates may not be claimed as not-supported by Aspose without verification evidence.
See `docs/non-aspose-format-candidate-registry-plan.md`.

---

## Relationship to Other Documents

- `AGENTS.md` — non-negotiable operating rules for agents
- `plans/master-plan.md` — single authoritative operational state
- `docs/gates.md` — gate pass criteria and artifact requirements
- `docs/release-control.md` — visibility classifications and release policy
- `docs/legal-and-licensing.md` — format legal classification and license policy
- `docs/llm-endpoint-strategy.md` — LLM endpoint and prompt handling policy
- `docs/specification-normalization.md` — specification normalization layer policy
- `tools/evidence/_readme.md` — evidence bundle contract system
- `docs/current-state-and-evidence-authority.md` — run-state authority model and current-state policy
- `docs/format-understanding-layer.md` — Format Understanding Layer backlog plan
- `docs/llm-and-embedding-strategy.md` — LLM and embedding strategy
- `docs/format-representation-model.md` — format representation categories and non-XML adaptability backlog
- `docs/non-aspose-format-candidate-registry-plan.md` — non-Aspose candidate registry plan

---

## 23. Planning and Agent Handoff Methodology (memory sprint 2026-05-08; updated memory-methodology-linkage-and-enforcement sprint 2026-05-08)

**23.0. Methodology Index Is the Governance Entry Point.** The file `docs/agent-methodology-index.md` is the local governance entry point for all plan and prompt work. It links all methodology docs, prompt templates, commands, and enforcement rules. Agents must read it before plan review or execution handoff work. The methodology index, prompt templates, and command files must remain linked from README, AGENTS.md, GOVERNANCE.md, memory/00-index.md, and the command registry. Any sprint that changes methodology docs must run the methodology link validation check.

**23.1. Local Planning Standards Are Authoritative.** The format-factory project maintains local planning and execution standards in docs/planning-methodology.md, docs/agent-execution-handoff-standard.md, and docs/plan-hardening-checklist.md. These documents are authoritative for how agents must write, harden, and execute plans. They supplement AGENTS.md.

**23.2. Plans Must Pass Hardening Before Execution.** No execution prompt may be run on an un-hardened plan. The plan hardening checklist (docs/plan-hardening-checklist.md) must be completed. A plan scoring below 18/22 must be returned to PLAN MODE for revision.

**23.3. Single-Go Handoffs Are the Standard for Complex Sprints.** When authorized, complex multi-section sprints are encoded as single-go execution prompts with internal gates and stop conditions. The agent self-manages the sprint. The human does not need to provide mid-execution guidance.

**23.4. Fresh-Chat Continuity Is Required.** The project must maintain sufficient local docs that a fresh chat session can orient itself without conversation history. docs/fresh-chat-continuity-brief.md and the prompt templates in docs/prompts/ are maintained for this purpose. Fresh chat sessions must read the continuity brief and memory index before planning work.

**23.5. No Broad Cleanup Commands as Default.** Agents must not use broad destructive git commands (stash -u, reset --hard, clean -fd) as defaults or shortcuts. If a dirty worktree blocks clean git, the agent must document the dirty_git_reason and use emergency_blocker_bundle: true rather than discarding uncommitted work. Broad cleanup guidance requires explicit scoped justification.

**23.6. Evidence Bundle Path Is Required.** Every evidence-producing sprint response must end with the line: EVIDENCE_BUNDLE: <absolute Windows path to zip>. This is a non-negotiable governance requirement. See AGENTS.md Section AD6.

**23.7. Evidence Review Before Next Sprint.** When a prior sprint has produced an evidence bundle, that bundle must be reviewed (using /evidence-review-next-prompt or its template) before the next sprint prompt is generated.

**23.8. Discovered Gaps Must Not Remain Only in Chat.** Any architecture gap, capability gap, or structural weakness identified during a sprint must be captured in at least one durable local artifact (roadmap, backlog, taskcard, or memory file). See AGENTS.md Section AB.

---

## 24. Methodology Linkage and Enforcement (memory-methodology-linkage-and-enforcement sprint 2026-05-08)

**24.1. Methodology Must Be Locally Discoverable.** All methodology docs, prompt templates, and commands must be reachable from README.md, AGENTS.md, GOVERNANCE.md, memory/00-index.md, and .claude/commands/_readme.md. A fresh agent session must be able to find all planning tools without manual search.

**24.2. Methodology Link Check Is Required.** The command `python tools/governance/check_methodology_links.py` must pass before any sprint that modifies methodology docs is considered complete. METHODOLOGY_LINK_CHECK: FAIL blocks bundle acceptance.

**24.3. Command Registry Must Stay Current.** .claude/commands/_readme.md must list all active methodology commands. When a new command is added, the registry must be updated in the same sprint.

**24.4. Prompt Templates Must Have an Index.** docs/prompts/README.md must exist and list all templates. Template selection guidance must be included.

**24.5. No Methodology Regression.** Removing or unlinking methodology docs, prompt templates, or commands without an authorized replacement is a governance violation. If a methodology doc is renamed or moved, all cross-links must be updated atomically in the same commit.

---

## 25. Git Safety and Concurrent Sprint Governance (GOV-REVERT-001)

**25.1. No Stash-Based Cleanup.** Agent sprints must not use `git stash` to hide unrelated work. Dirty files from another sprint are evidence of concurrent work, not clutter to hide.

**25.2. No Reset, Restore, Checkout, or Clean for Appearance.** `git reset`, `git restore`, `git checkout --`, and `git clean` must not be used to make the repository appear clean. If cleanup is needed, it requires explicit prompt authorization, exact paths, and a preservation record.

**25.3. Exact-Path Staging.** Agents must stage exact authorized files only. Broad staging with `git add .` or `git add -A` is forbidden.

**25.4. One Active Execution Sprint Per Worktree.** A single worktree should have one active mutation sprint at a time. Concurrent streams require explicit authorization and dirty-state classification before any edits. Verification sprints may inspect but must not clean, stash, restore, or stage another sprint's files.

**25.5. Active Sprint Lock Convention.** `.local/active-sprint-lock.json` is the local-only lock convention. Agents must respect active locks for other mutation sprints. Stale locks require human review or explicit prompt authorization.

**25.6. Metadata Isolation.** New evidence bundles must use sprint-specific metadata directories under `.local/`. Root `bundle-metadata/` must not be used for new bundles. Bundle validators must reject mixed sprint identity in identity-critical metadata files.

**25.7. Required Closeout Proof.** Execution sprint metadata must include `git-safety-policy-check.md`, and final responses must include `NO_STASH_RESET_RESTORE_CLEAN_USED: YES`.

---

## 26. Always-Updated Enforcement and FFSM Policy (memory sprint 2026-05-09)

**26.1. Mandatory Closeout Phase.** Every execution sprint must include a mandatory closeout
phase before the evidence bundle is built. This phase updates Level 6 session hint files,
ensures gate status is consistent across all authority sources, and runs
CURRENT_STATE_CONSISTENCY: PASS before bundle build. Skipping this phase means the sprint
is INCOMPLETE.

**26.2. Authority Level Hierarchy.** Format Factory uses a seven-level authority hierarchy:
- Level 1: registry/format-registry.yaml (gate authority -- highest)
- Level 2: plans/master-plan.md (operational authority)
- Level 3: taskcards/ (task authority)
- Level 4: Evidence bundles (sprint output authority)
- Level 5: ROADMAP.md, README.md (navigation authority)
- Level 6: Session hints: memory/09, .claude/settings.json, docs/fresh-chat-continuity-brief.md
- Level 7: Derived mirrors: pack.yaml, format-profile.yaml, product-readiness.yaml

When sources conflict, higher authority always wins. Full rules in
docs/current-state-and-evidence-authority.md Section 8.

**26.3. Gate Changes Require Multi-File Consistency.** When a gate status changes, all three
sources must be updated atomically in the same commit: registry/format-registry.yaml,
plans/master-plan.md header, and pack.yaml for the format. CURRENT_STATE_CONSISTENCY: PASS
must be confirmed before the bundle is built.

**26.4. No Memory/16+ Without GOV-006.** No new memory/NN files may be created beyond
memory/15 without GOV-006 taskcard authorization. See
taskcards/GOV-006-documentation-information-architecture-standardization.md.

**26.5. FFSM Is Design Only.** The Format Factory State Manager is defined in design direction
documents only. No tools/state/, tools/llm/, or tools/retrieval/ code exists. No LangGraph,
Prefect, Temporal, or Dagster is installed or imported. Creating any of these requires explicit
human-authorized taskcards approved before code is written. See
memory/15-ai-modules-and-state-management-architecture-20260509.md.

**26.6. Pending Propagation Reports.** When a sprint cannot safely update a file because
another active stream owns it, a pending-propagation report must be created at
reports/propagation/{sprint-id}-propagation-pending.md. See
docs/agent-execution-handoff-standard.md Section 19.


## Section 25 -- Always-Updated Enforcement and FFSM Policy (Added memory-ai-direction-sync-2026-05-09)

**26.1. Mandatory Sprint Closeout.** Every execution sprint must run a mandatory closeout phase
after all sprint work and before the evidence bundle is built. The closeout phase must:
(a) update all Level 6 session hint files (memory/09, settings.json, docs/fresh-chat-continuity-brief.md),
(b) if gate status changed: update registry, master-plan header, and all pack.yaml files,
(c) if a taskcard was created or completed: update plans/master-plan.md taskcards table,
(d) run python tools/evidence/check_current_state_consistency.py and confirm PASS,
(e) create propagation reports for files that cannot be updated due to stream ownership.

**26.2. Seven-Level Authority Hierarchy.** The project authority hierarchy is:
Level 1 (registry/format-registry.yaml) > Level 2 (plans/master-plan.md) > Level 3 (taskcards/) >
Level 4 (evidence bundles) > Level 5 (ROADMAP.md, README.md) > Level 6 (session hints) >
Level 7 (derived mirrors). After every sprint, Level 6 and 7 must match Level 1-4.

**26.3. Gate Changes Require Consistent Multi-File Update.** A gate status change is not complete
until registry, master-plan header, and pack.yaml all agree. If any of these is inconsistent,
the sprint is incomplete. An evidence bundle must not be built until they agree.

**26.4. No memory/16+ Without GOV-006.** No new numbered memory files (memory/16 or higher) may be
created without explicit authorization from the GOV-006 documentation standard sprint or an explicit
human-authorized sprint prompt naming the new file. This is enforced per AGENTS.md Section AE7.

**26.5. FFSM Is Design Direction Only.** The Format Factory State Manager (FFSM) architecture
documented in memory/15 and docs/current-state-and-evidence-authority.md Section 8 is DESIGN ONLY.
No tools/state/, tools/llm/, or tools/retrieval/ code may be created without an explicit authorized
taskcard and sprint prompt. LangGraph, Prefect, Temporal, and Dagster must not be imported without
an explicit integration sprint.

**26.6. Documentation Taxonomy Requires GOV-006.** Until GOV-006 is executed, no new architecture
decisions may be filed as docs/architecture/decisions/ADR-*.md, no standards as
docs/governance/standards/*.md, and no context snapshots as docs/context/chat-sync/*.md. Use
transitional memory/NN files (if authorized) or create a propagation report.

**26.7. Pending Propagation Reports Are Required.** When a sprint cannot update a file because
another stream owns it, a pending propagation report is REQUIRED at
reports/propagation/{sprint-id}-propagation-pending.md. Silently skipping the update is a
governance violation.
