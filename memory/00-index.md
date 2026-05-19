---
memory_package: format-factory-chat-memory
version: 1.0
created_at: 2026-05-03
intended_location: /memory
source: ChatGPT conversation memory plus inspected Phase 0 evidence bundles through run015
visibility: internal
publish_allowed: false
notes: Place this folder at repo root as /memory. These files are for agent context and must not supersede plans/master-plan.md.
---

# 00 â€” Memory Index

## Purpose

This index helps an agent understand the complete picture without reading a single huge transcript.

The memory package captures:

- the origin of the project
- the userâ€™s standing governance rules
- the architecture decisions
- the reason for each Phase 0 hardening run
- the evidence-bundle review pattern
- the current state before Phase 1
- future memory synchronization rules

## Files

| File | Purpose |
|---|---|
| `01-project-origin-and-intent.md` | Why the project exists and what â€œfile format hackingâ€ means here. |
| `02-standing-operating-rules.md` | Non-negotiable rules the user established for ChatGPT and agents. |
| `03-architecture-and-product-tracks.md` | Acquisition layer, OSS Python, OSS .NET, commercial .NET, tiers. |
| `04-phase0-evolution-and-bundle-reviews.md` | Chronological account of plan versions and evidence bundle inspections. |
| `05-decision-register-expanded.md` | Expanded decision log with rationale and consequences. |
| `06-gap-risk-and-healing-history.md` | Gap, risk, and healing history through run014. |
| `07-agent-governance-model.md` | Claude/Codex, AGENTS.md, commands, skills, gates, bundles. |
| `08-specification-cache-amendment.md` | Requirement to cache specifications/materials locally on disk. |
| `09-current-state-before-phase1.md` | Current repo/project state after run015: Phase 0 accepted, Phase 1A FODS scoring complete. |
| `10-memory-maintenance-protocol.md` | How agents should maintain `/memory` over time. |
| `11-prompting-and-agent-style-rules.md` | Prompt mode labels, execution handoffs, bundle requirements. |
| `12-glossary.md` | Project terminology. |
| `11-format-understanding-and-llm-strategy.md` | Format Understanding Layer, LLM/embedding strategy, non-XML backlog, non-Aspose registry, discovered-gap capture rule (memory sprint 2026-05-08). Updated 2026-05-09 with AI direction refinement notes. |
| `12-planning-and-agent-handoff-methodology.md` | Planning methodology, execution handoff standard, user preferences for prompts and plans. Updated with methodology index and prompt README links (linkage sprint 2026-05-08). Updated 2026-05-09 with ChatGPT supervision and parallel sprint handling rules. |
| `13-chatgpt-initial-project-analysis-20260509.md` | ChatGPT first project-level analysis (2026-05-09). Project purpose, user requirement, standing, strengths, gaps, intended path, next-level AI interpretation, bottom-line assessment. Required reading for AI/LLM, Phase 4, or multi-stream sprint work. |
| `14-ai-supervision-and-three-pilot-direction-20260509.md` | AI supervision rules and three-pilot direction agreed in 2026-05-09 session. User confirmation, end goal, AI roles, ChatGPT supervisory workflow, parallel sprint rules, stream notes, LLM design refinement required. Required reading for Phase 4, AI strategy, and sprint driving. |
| `15-ai-modules-and-state-management-architecture-20260509.md` | Detailed AI module, embedding retrieval, agent role, source generation, Format Factory State Manager, community component, and no-drift architecture direction. Required reading for LLM/embedding work, state management work, no-drift work, agent workflow design, Phase 4 source generation, playbook replay, and review queue design. |
| `16-controlled-swarm-execution-and-acceleration-20260512.md` | Controlled swarm model, ACCEL-003 pattern, S-F2F-05 schema fix, METADATA_IDENTITY pattern, DEC-033 status record, Gate 10 approval record. POST-FODT-GATE10-CONTROLLED-SWARM-001 sprint record. |
| `17-dec033-option-b-gate11-and-github-pat-20260512.md` | DEC-033 Option B resolution (Babar Raza, 2026-05-12), Gate 11 commercial skeleton status, SDK blocker, GitHub PAT scope/propagation rules, ACCEL-003 hardening (final bundle metrics in proof). |
| `18-gate11-tier0-dotnet-and-accel003-repair-20260513.md` | GATE11-TIER0-COMMERCIAL-AND-ACCEL003-REPAIR-SWARM-001 (2026-05-13): ACCEL-003 3-pass repair (proof inside ZIP), .NET 10 SDK 10.0.204 installed, FODS Tier 0 12/12 tests PASS, FODT Tier 0 13/13 tests PASS, DEC-034 IV prep, GitHub PAT refresh. |
| `19-dec034-gate11-tier0-commercial-iv-20260513.md` | DEC034-GATE11-TIER0-COMMERCIAL-IV-SWARM-001 (2026-05-13): DEC-034 independent verification of Gate 11 Tier 0 work. All lanes PASS. FODS 12/12, FODT 13/13, ACCEL-003 38/38, DEC-033 Option B confirmed. READY_FOR_GATE11_HUMAN_APPROVAL. |
| `20-gate11-approval-release-readiness-20260513.md` | GATE11-APPROVAL-AND-RELEASE-READINESS-SWARM-001 (2026-05-13): Gate 11 approval DEFERRED (flags not YES). Commercial license NOT finalized. Package dry-run PASS. CLI help fixed. f1ae4c9 audited. FODP recommended next. |
| `21-commercial-product-direction-reset-20260513.md` | COMMERCIAL-REQUIREMENTS-DOC-SYNC-20260513: Human clarified full commercial requirements (load-edit-save-convert). Current .NET is C2 (Tier 0 baseline). Gate 11 deferred/rebaselined. Capability model C0-C10 created. 10 implementation taskcards created. Authority files synced. |
| `23-ai-usage-operating-model-20260513.md` | AI-USAGE-LOCAL-DOC-SYNC-20260513: Human authorized AI acceleration. AI is accelerator not authority. docs/ai-usage-operating-model.md, docs/ai-assisted-commercial-development.md, docs/spec-retrieval-and-rag-policy.md, docs/agent-swarm-ai-orchestration.md created. AGENTS.md AF12 + GOVERNANCE.md 26.10 added. 5 AI taskcards created. |
| `24-chatgpt-session-memory-sync-20260513.md` | CHATGPT-MEMORY-LOCAL-SYNC-20260513: ChatGPT session became too long; full project continuity synced to local repo. Commercial product target (C7+), FODS/FODT status (Gates 1-10 PASSED, Gate 11 in progress), DEC-033 Option B, AI usage policy, generated-requirements direction, skill-system direction, controlled swarm model, git safety, fresh-chat bootstrap instructions, next recommended sprint. |
| `25-assistant-supervision-methodology-20260513.md` | CHATGPT-MEMORY-LOCAL-SYNC-20260513-ADDENDUM: Captures the supervision and execution methodology expected by Babar Raza. Evidence-first review, challenge-agent-claims, ready-to-send prompts, controlled swarm execution, AI governance, generated-requirements-first, gate/evidence safety, new-chat behavior checklist, next-agent behavior checklist. Full methodology in docs/assistant-supervision-methodology.md. |
| `26-format-expansion-roadmap-and-non-aspose-backlog-20260514.md` | FORMAT-FACTORY-ROADMAP-MEMORY-SYNC-001 (2026-05-14): Strategic format expansion direction, immediate/short-term/long-term roadmap, and full non-Aspose candidate backlog (13 categories, ~200+ candidates, all marked needs_audit). Immediate: finish XML proof (FODS/FODT) + Conway R1-R9. Short-term: expand to public-spec XML/package formats. Long-term: any format family with sufficient public technical info. Key files: docs/format-expansion-roadmap.md/.yaml, taskcards/FORMAT-EXPANSION-ROADMAP.md, NON-ASPOSE-FORMAT-BACKLOG.md, PUBLIC-SPEC-FORMAT-EXPANSION.md. |
| `36-r19-high-throughput-acquisition-train-20260517.md` | FORMAT-FACTORY-R19-HIGH-THROUGHPUT-ACQUISITION-TRAIN-001 (2026-05-16, commit 2dcd7f8). BACKFILL — created 2026-05-17. ZST Gates 4-7 ALL PASSED (G5 waived G-NORM-004). FODP/FODG Gates 2-3 PASSED (fast-path ODF 1.3). Gnumeric/ABW Gates 2-3 PASSED. ORA DEFERRED_BORDERLINE (6.8/10 < 7.0). FODS/FODT Gate 11 plan only (not approved). P-EVID-001 to P-EVID-004 established. 14 registry gate transitions. Test baseline: 1181 passed, 8 skipped. Note: memory/37 (R20) is missing; memory/38 (R21) is current. |
| `38-r21-foss-release-readiness-and-gate11-preexecution-20260517.md` | FORMAT-FACTORY-R21-FOSS-RELEASE-READINESS-AND-GATE11-COMMERCIAL-PREEXECUTION-TRAIN-001 (2026-05-17). ZST/FODP/FODG/Gnumeric/ABW Gates 8-10 PASSED (local_release_candidate_ready). FODS/FODT G11-A/B/C/E planning complete. docs/python-foss/, examples/python/, packaging/python/, release-manifests/python-foss/ created. CURRENT AUTHORITATIVE for R21+ state. memory/37 (R20) not yet backfilled. |
| `42-ai-llm-embedding-platform-plan-hardening-20260518.md` | FORMAT-FACTORY-AI-LLM-EMBEDDING-PLAN-MEMORY-SYNC-001 (2026-05-18). AI platform plan hardened — no implementation. Three AI types (agentic/synthesis/embeddings) + mandatory control plane. Qwen2 low-risk only. GPT-OSS citation-verified synthesis. Format-segregated LanceDB vector stores. Agent Metrics canonical telemetry. 40-item risk register. 11 docs/ai/ files, 10 taskcards, master plan Section 39, GOVERNANCE 26.14, AGENTS AF16. Implementation not yet authorized until plan reviewed. Required reading for AI work. |
| `43-ai-platform-phase1-control-plane-foundation-20260518.md` | FORMAT-FACTORY-R24-AI-PHASE1-COMMITTED (2026-05-18, commit f0f742e). AI Phase 1 Control Plane Foundation implemented. tools/ai/ full structure: control_plane/gateway.py (GPT-OSS only), schemas/ (5 Pydantic), contracts/ (5 YAML), validators/ (runtime_guard, authority_lifecycle, schema_validator, secret_redaction), telemetry/ (spool_manager, call_logger), prompts/registry.py. 70 AI tests PASS. No embeddings/vector DB/LanceDB. GPT_OSS_ENDPOINT env required; fixture mode when absent. LLM-001/EMB-001 taskcards superseded. Required reading for AI Phase 2 work. |
| `44-r25-ai-phase1-gate4-forward-train-20260518.md` | FORMAT-FACTORY-R25-AI-PHASE1-GATE4-FORWARD-TRAIN-AND-R24-METADATA-SYNC-001 (2026-05-18). R25 COMPLETE. ODS/ODT/QOI Gate 3 IV PASS (gate_3_iv_status=verified, gate_4_readiness=ready_for_parser_planning). FODS G11-F: 120/120 tests (+8 malformed XML guard). FODT G11-F: 108/108 tests (+8 heading detection + guard). Python full: 2039 PASS (13 skip). AI tests: 70 PASS. Packaging: 68 PASS. AI Phase 1 pre-resolved. Publication BLOCKED (blocked_external_authority). |
| `45-r26-ai-phase2-gate4-g11g-prep-20260519.md` | FORMAT-FACTORY-R26-AI-PHASE2-ENDPOINT-TELEMETRY-GATE4-PROTOTYPE-AND-G11G-PREP-001 (2026-05-19). R26 COMPLETE. AI Phase 2: model registry hardening (guess_model_family, role_candidates, 5 new ModelCapability fields), Agent Metrics telemetry mapping + spool validation, direct endpoint bypass detection. ODS/ODT/QOI Gate 4 parser plans (parser_plan_complete, no source). G11-G readiness packet (NOT_STARTED). Python FOSS publication review (blocked). AI tests: 109/109 (+39 Phase 2). Python full: 2078 PASS. .NET FODS 120/120, FODT 108/108. Total: 2306 PASS. |
| `46-r27-ai-platform-full-cycle-20260519.md` | FORMAT-FACTORY-R27-AI-PLATFORM-FULL-GOVERNED-IMPLEMENTATION-CYCLE-001 (2026-05-19). R27 COMPLETE. Full AI platform: synthesis controls (runner.py), authority lifecycle integration (state records, transition evidence), spec normalization adapter, embedding/vector-store foundation (namespace isolation), telemetry drain (Agent Metrics mapping), test generation (proposal reviewer), Qwen2 agentic controls (scoped runner), risk controls (6 checks). Control-plane hardened (NO_FALLBACK_ROLES). AI tests: 202/202 (+93). Blockers: GPT-OSS live (env), LanceDB (dep), Agent Metrics posting (env), Qwen2 live (model). |
| `47-r27-gate4-prototypes-g11-c7-c8-publication-20260519.md` | FORMAT-FACTORY-R27-GATE4-PROTOTYPES-G11-C7-C8-HARDENING-PUBLICATION-PACKET-AND-METADATA-SYNC-001 (2026-05-19). R27 non-AI lanes. ODS/ODT/QOI Gate 4 prototypes (29 tests). FODS C7/C8 136/136 (+16), FODT C7/C8 124/124 (+16). 5 Python FOSS packages README+LICENSE. XCF Gates 1-3 PASS (7.8/10), ZPAQ Gates 1-2 PASS/G3 BLOCKED (6.2/10). Cross-format harness 15/15. Registry updated. |

## Local Methodology Entry Points (added linkage sprint 2026-05-08)

These files provide the local bridge for fresh-chat continuity. Future agents should start
from the methodology index before generating plans or prompts.

| File | Purpose |
|------|---------|
| [docs/agent-methodology-index.md](../docs/agent-methodology-index.md) | Start here for all plan and prompt work. Links all methodology docs, templates, commands, and enforcement rules. |
| [docs/prompts/README.md](../docs/prompts/README.md) | Index of all 8 prompt templates. Rules for using templates. |
| [.claude/commands/_readme.md](../.claude/commands/_readme.md) | Command registry. Lists all active methodology commands (/plan-hardening, /execution-handoff, /evidence-review-next-prompt, /memory-sprint). |

## Priority reading for a new agent

A new agent should read in this order:

```text
plans/master-plan.md
AGENTS.md
GOVERNANCE.md
docs/agent-methodology-index.md
memory/00-index.md
memory/12-planning-and-agent-handoff-methodology.md
memory/09-current-state-before-phase1.md
docs/fresh-chat-continuity-brief.md
```

Then it should read only the memory files relevant to the task.

### Additional priority files by task type

| Task type | Additional required reading |
|-----------|----------------------------|
| AI/LLM/embedding strategy | memory/43-ai-platform-phase1-control-plane-foundation-20260518.md (LATEST), memory/42-ai-llm-embedding-platform-plan-hardening-20260518.md, docs/ai/ai-platform-operating-model.md, plans/master-plan.md Section 39, docs/ai/ai-risk-register.md, memory/14-ai-supervision-and-three-pilot-direction-20260509.md |
| State management and no-drift work | memory/15-ai-modules-and-state-management-architecture-20260509.md, memory/12-planning-and-agent-handoff-methodology.md, docs/current-state-and-evidence-authority.md |
| Agent workflow design | memory/15-ai-modules-and-state-management-architecture-20260509.md, memory/12-planning-and-agent-handoff-methodology.md, docs/agent-execution-handoff-standard.md |
| Playbook replay and review queue design | memory/15-ai-modules-and-state-management-architecture-20260509.md, docs/playbook-layer.md, memory/14-ai-supervision-and-three-pilot-direction-20260509.md |
| Phase 4 product source planning | memory/13-chatgpt-initial-project-analysis-20260509.md, memory/14-ai-supervision-and-three-pilot-direction-20260509.md |
| Phase 4 source generation | memory/15-ai-modules-and-state-management-architecture-20260509.md, memory/11-format-understanding-and-llm-strategy.md, docs/format-understanding-layer.md |
| Three-pilot proof planning | memory/14-ai-supervision-and-three-pilot-direction-20260509.md |
| Sprint evidence review and next-prompt generation | memory/14-ai-supervision-and-three-pilot-direction-20260509.md, memory/12-planning-and-agent-handoff-methodology.md |
| Format expansion and non-Aspose backlog | memory/26-format-expansion-roadmap-and-non-aspose-backlog-20260514.md, docs/format-expansion-roadmap.md, taskcards/FORMAT-EXPANSION-ROADMAP.md, taskcards/NON-ASPOSE-FORMAT-BACKLOG.md |

## Memory stream update history

| Run | Stream | Files updated |
|-----|--------|---------------|
| run019 | Main execution | 00-index.md, 04-phase0-evolution-and-bundle-reviews.md, 05-decision-register-expanded.md, 06-gap-risk-and-healing-history.md, 09-current-state-before-phase1.md, 10-memory-maintenance-protocol.md (run018 committed 0c97256; TC-0007 tooling implemented; TC-0009 Gate 2 evidence draft; master-plan v2.15) |
| run017 | Main execution | 00-index.md, 04-phase0-evolution-and-bundle-reviews.md, 05-decision-register-expanded.md, 06-gap-risk-and-healing-history.md, 09-current-state-before-phase1.md, 10-memory-maintenance-protocol.md (Gate 1 approval by Babar Raza; Phase 2 started; acquisition-packs/fods/ skeleton; TC-0009 created; master-plan.md v2.13) |
| run016 | Main execution | 02-standing-operating-rules.md, 07-agent-governance-model.md, 09-current-state-before-phase1.md, 10-memory-maintenance-protocol.md, 11-prompting-and-agent-style-rules.md (DEC-034 governance rule; AGENTS.md Section V; run016 verification sprint recorded) |
| run014 | Main execution | 00-index.md, 04-phase0-evolution-and-bundle-reviews.md, 09-current-state-before-phase1.md (run014 closure-readiness sprint recorded; master-plan.md v2.10; stale file-count and bundle references fixed) |
| run013 | Main execution | 00-index.md, 03-architecture-and-product-tracks.md, 04-phase0-evolution-and-bundle-reviews.md, 05-decision-register-expanded.md, 06-gap-risk-and-healing-history.md, 07-agent-governance-model.md, 09-current-state-before-phase1.md, 10-memory-maintenance-protocol.md (stale pending-propagation notes removed; run011/run013 status recorded) |
| run012 | Memory stream | 00-index.md, 03-architecture-and-product-tracks.md, 04-phase0-evolution-and-bundle-reviews.md, 05-decision-register-expanded.md, 06-gap-risk-and-healing-history.md, 07-agent-governance-model.md, 08-specification-cache-amendment.md, 09-current-state-before-phase1.md, 10-memory-maintenance-protocol.md |
| memory-sprint-2026-05-08 | Memory sprint | 00-index.md, 11-format-understanding-and-llm-strategy.md (NEW), AGENTS.md Sections AB+AC, GOVERNANCE.md Sections 21+22, docs/format-understanding-layer.md (NEW), docs/llm-and-embedding-strategy.md (NEW), docs/format-representation-model.md (NEW), docs/non-aspose-format-candidate-registry-plan.md (NEW), plans/master-plan.md Section 37 (NEW), ROADMAP.md Architecture Backlog (NEW), taskcards/FUL-001--FUL-004 (NEW), taskcards/LLM-001 (NEW), taskcards/EMB-001 (NEW), taskcards/REP-001 (NEW), taskcards/REP-003 (NEW), taskcards/NAC-001 (NEW), taskcards/GOV-001 (NEW) |
| memory-planning-methodology-2026-05-08 | Memory methodology sprint | 00-index.md (UPDATED), 12-planning-and-agent-handoff-methodology.md (NEW), docs/planning-methodology.md (NEW), docs/agent-execution-handoff-standard.md (NEW), docs/plan-hardening-checklist.md (NEW), docs/fresh-chat-continuity-brief.md (NEW), docs/prompts/ (8 templates NEW), AGENTS.md Section AD (NEW), GOVERNANCE.md Section 23 (NEW), taskcards/GOV-002 (NEW), .claude/commands/ (4 files NEW) |
| memory-methodology-linkage-2026-05-08 | Memory methodology linkage sprint | 00-index.md (UPDATED), 12-planning-and-agent-handoff-methodology.md (UPDATED), docs/agent-methodology-index.md (NEW), docs/prompts/README.md (NEW), README.md (UPDATED -- agent methodology section), .claude/commands/_readme.md (UPDATED -- methodology commands table), AGENTS.md AD0/AD8-AD10 (ADDED), GOVERNANCE.md Section 23.0/23.7-23.8/24 (ADDED), tools/governance/check_methodology_links.py (NEW), tests/governance/test_methodology_links.py (NEW), taskcards/GOV-003 (NEW) |
| memory-ai-direction-sync-2026-05-09 | ChatGPT AI supervision and sprint rules memory sync | 00-index.md (UPDATED -- new file rows, priority tables, stream history), 10-memory-maintenance-protocol.md (UPDATED -- 2026-05-09 entry), 11-format-understanding-and-llm-strategy.md (UPDATED -- AI direction refinement section), 12-planning-and-agent-handoff-methodology.md (UPDATED -- ChatGPT supervision rules, parallel sprint handling), 13-chatgpt-initial-project-analysis-20260509.md (NEW), 14-ai-supervision-and-three-pilot-direction-20260509.md (NEW), docs/fresh-chat-continuity-brief.md (UPDATED -- 2026-05-09 section), docs/agent-methodology-index.md (UPDATED -- new memory context refs), docs/prompts/README.md (UPDATED -- ChatGPT prompt note), ROADMAP.md (UPDATED -- 2026-05-09 AI direction note), taskcards/GOV-004 (NEW), tools/evidence/contracts/memory-ai-direction-sync-20260509.yaml (NEW) |
| memory-ai-state-management-sync-2026-05-09 | AI module and state-management architecture memory sync | 15-ai-modules-and-state-management-architecture-20260509.md (NEW), 00-index.md (UPDATED), 10-memory-maintenance-protocol.md (UPDATED), 11-format-understanding-and-llm-strategy.md (UPDATED), 12-planning-and-agent-handoff-methodology.md (UPDATED), 14-ai-supervision-and-three-pilot-direction-20260509.md (UPDATED), docs/fresh-chat-continuity-brief.md (UPDATED), docs/agent-methodology-index.md (UPDATED), docs/prompts/README.md (UPDATED), docs/llm-and-embedding-strategy.md (UPDATED), ROADMAP.md (UPDATED), taskcards/GOV-005 (NEW), tools/evidence/contracts/memory-ai-state-management-sync-20260509.yaml (NEW). No LLM modules, embeddings, vector DB, state manager code, orchestration components, product source, gate changes, playbook replay, or push. |
| DEC033-OPTION-B-GATE11-COMMERCIAL-SWARM-001 | DEC-033 Option B resolution, Gate 11 commercial skeletons, GitHub PAT probe, ACCEL-003 hardening | 16-controlled-swarm-execution-and-acceleration-20260512.md (NEW), 17-dec033-option-b-gate11-and-github-pat-20260512.md (NEW), 00-index.md (UPDATED). No Gate 11 approval, no .NET FOSS, no push. |
| CHATGPT-MEMORY-LOCAL-SYNC-20260513 | ChatGPT session too long; full project continuity synced to local repo | 24-chatgpt-session-memory-sync-20260513.md (NEW), 00-index.md (UPDATED), docs/fresh-chat-project-bootstrap.md (NEW), docs/fresh-chat-project-bootstrap.yaml (NEW), reports/governance/chatgpt-memory-local-sync-20260513.md (NEW), reports/planning/current-project-continuity-map-20260513.md (NEW), 3 taskcards (NEW), evidence contract + bundle. No Gate 11 approval, no .NET FOSS, no product source, no push. |
| CHATGPT-MEMORY-LOCAL-SYNC-20260513-ADDENDUM | Supervision methodology and execution standards transferred to local repo | 25-assistant-supervision-methodology-20260513.md (NEW), docs/assistant-supervision-methodology.md (NEW), docs/assistant-supervision-methodology.yaml (NEW), docs/project-execution-standards.md (NEW), docs/project-execution-standards.yaml (NEW), docs/fresh-chat-project-bootstrap.md (UPDATED — working style section), docs/fresh-chat-project-bootstrap.yaml (UPDATED — working style fields), 00-index.md (UPDATED), AGENTS.md (UPDATED — AF15), GOVERNANCE.md (UPDATED — 26.13), 2 taskcards (NEW), governance sync reports (NEW). |
| FORMAT-FACTORY-ROADMAP-MEMORY-SYNC-001 | Strategic format expansion roadmap and non-Aspose candidate backlog synced to local repo | 26-format-expansion-roadmap-and-non-aspose-backlog-20260514.md (NEW), docs/format-expansion-roadmap.md (NEW), docs/format-expansion-roadmap.yaml (NEW), docs/fresh-chat-project-bootstrap.md (UPDATED — format roadmap section), docs/fresh-chat-project-bootstrap.yaml (UPDATED — format roadmap fields), plans/master-plan.md (UPDATED — Section 38), taskcards/FORMAT-EXPANSION-ROADMAP.md (NEW), taskcards/NON-ASPOSE-FORMAT-BACKLOG.md (NEW), taskcards/PUBLIC-SPEC-FORMAT-EXPANSION.md (NEW), reports/planning/format-expansion-roadmap-memory-sync-20260514.md (NEW), tools/evidence/contracts/format-expansion-roadmap-memory-sync-20260514.yaml (NEW), 00-index.md (UPDATED). No Gate 11 approval, no format acquisition, no product source, no push. |
| FORMAT-FACTORY-R25-AI-PHASE1-GATE4-FORWARD-TRAIN-AND-R24-METADATA-SYNC-001 | R25 sprint memory integration | 43-ai-platform-phase1-control-plane-foundation-20260518.md (NEW — backfill from R24/f0f742e), 44-r25-ai-phase1-gate4-forward-train-20260518.md (NEW), 00-index.md (UPDATED). ODS/ODT/QOI Gate 3 IV. FODS/FODT G11-F hardening. AI Phase 1 pre-resolved. Python 2039 PASS. .NET FODS 120, FODT 108. |
| FORMAT-FACTORY-R26-AI-PHASE2-ENDPOINT-TELEMETRY-GATE4-PROTOTYPE-AND-G11G-PREP-001 | R26 sprint memory integration | 45-r26-ai-phase2-gate4-g11g-prep-20260519.md (NEW), 00-index.md (UPDATED). AI Phase 2 (model registry + telemetry + runtime guard). ODS/ODT/QOI Gate 4 parser plans. G11-G readiness. Python FOSS publication review. AI 109/109 (+39). Python 2078 PASS. .NET FODS 120, FODT 108. Total 2306. |
| FORMAT-FACTORY-R27-GATE4-PROTOTYPES-G11-C7-C8-HARDENING-PUBLICATION-PACKET-AND-METADATA-SYNC-001 | R27 non-AI sprint memory integration | 47-r27-gate4-prototypes-g11-c7-c8-publication-20260519.md (NEW), 00-index.md (UPDATED), registry/format-registry.yaml (UPDATED — ODS/ODT/QOI gate_3+gate_4, XCF gates 1-3, ZPAQ gates 1-2). ODS/ODT/QOI Gate 4 prototypes. FODS C7/C8 136/136. FODT C7/C8 124/124. Python FOSS README+LICENSE. XCF/ZPAQ new candidates. |
| run010 | Memory stream | Memory integration prompted by addition of /memory folder; AGENTS.md Section U added in run010 repo execution (not a /memory file edit — see run010 bundle) |

## Warning

Never act from this memory package alone. Always cross-check the actual repo state and the current master plan.

The source layout (`src/net/{format}`, `src/python/{format}`) was propagated to `plans/master-plan.md` v2.8 in run011 and verified in run013. Stale "pending propagation" notes have been removed. However, **no `src/` folders may be created in Phase 0** â€” source folder creation requires a Phase 4+ prompt with Gate 9 passed.
