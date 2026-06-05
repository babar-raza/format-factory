# Root Orphans Inventory

## Overview
This inventory lists all files directly under `docs/` (excluding `docs/README.md` and meta folders like `docs/_audit/` and `docs/_archive/`). Each orphan must be moved, merged, archived, or deleted. Since there is no `docs/README.md`, all files in the docs/ root are considered orphans.

## Table: Root Orphans

| Orphan Path | Brief Content Summary | Likely Target Area | Action | Canonical Merge Target (if merge) | Risks/Notes |
|-------------|-----------------------|--------------------|--------|-----------------------------------|-------------|
| acquisition-workflow.md | Describes the end-to-end acquisition workflow from spec to release, including gates, evidence, samples, prototype, neutral model, oracle comparison, security review, product mapping, and release. | reference | move to docs/reference/ |  |  |
| agent-execution-handoff-standard.md | Defines the standard format for agent execution handoff prompts, including dependency preflight, evidence review, claim challenging, and prompt generation. | guide | move to docs/guides/ |  |  |
| agent-methodology-index.md | Index of agent methodology documents, serving as the entry point for plan and prompt work. References planning-methodology.md, agent-execution-handoff-standard.md, plan-hardening-checklist.md, fresh-chat-continuity-brief.md, and prompts/README.md. | overview | move to docs/overview/ |  |  |
| agent-swarm-ai-orchestration.md | Guidance on AI-assisted agent swarm orchestration, including scoped runners, model discovery, and telemetry. | guide | move to docs/guides/ |  |  |
| ai-assisted-commercial-development.md | Patterns for AI-assisted commercial development in `src/net/{format}/`, covering AI usage types, control plane, model routing, and risk controls. | guide | move to docs/guides/ |  |  |
| ai-assisted-commercial-development.yaml | Machine-readable metadata for ai-assisted-commercial-development.md, including version, creation date, and applicable formats (fods_net, fodt_net, future_commercial_formats). | reference | move to docs/reference/ |  | Keep paired with .md file; consider placing both in same subdirectory. |
| ai-generated-format-requirements-pipeline.md | Pipeline for AI-generated format requirements, covering generation, schema validation, verifier review, and acceptance (ACCEPTED_FOR_VERTICAL_SLICE). | guide | move to docs/guides/ |  |  |
| ai-generated-format-requirements-pipeline.yaml | Machine-readable metadata for AI-generated format requirements pipeline. | reference | move to docs/reference/ |  | Keep paired with .md file. |
| ai-usage-operating-model.md | Operating model for AI usage in the project, defining three AI usage types (A: agentic, B: synthesis, C: embeddings), mandatory control plane, model selection, telemetry, and artifact author lifecycle. | reference | move to docs/reference/ |  |  |
| ai-usage-operating-model.yaml | Machine-readable metadata for AI usage operating model. | reference | move to docs/reference/ |  | Keep paired with .md file. |
| architecture.md | High-level architecture of the format-factory system, detailing components (docs, plans, taskcards, registry, acquisition-packs, samples, schemas, prototypes, src, tests, tools, reports, .claude). | reference | move to docs/reference/ |  |  |
| assistant-supervision-methodology.md | Methodology for supervising agent execution, covering supervision principles, prompt quality, and execution oversight. | guide | move to docs/guides/ |  |  |
| assistant-supervision-methodology.yaml | Machine-readable metadata for assistant supervision methodology. | reference | move to docs/guides/ |  | Keep paired with .md file. |
| commercial-dotnet-architecture.md | Architecture details for the .NET commercial product, including layout, tiers, and commercial isolation considerations. | reference | move to docs/reference/ |  |  |
| commercial-dotnet-architecture.yaml | Machine-readable metadata for commercial .NET architecture. | reference | move to docs/reference/ |  | Keep paired with .md file. |
| commercial-product-capability-model.md | Capability model for commercial product readiness, defining capability levels C0-C10 and linking to gate approvals. | reference | move to docs/reference/ |  |  |
| commercial-product-capability-model.yaml | Machine-readable metadata for commercial product capability model. | reference | move to docs/reference/ |  | Keep paired with .md file. |
| conway-r9-authority-continuity.md | Authority continuity model for Conway R9 governance, describing how authority flows and is maintained across governance layers. | reference | move to docs/reference/ |  |  |
| conway-r9-governed-simulation.md | Guide for running governed simulations under Conway R9 framework. | guide | move to docs/guides/ |  |  |
| conway-r9-swarm-governance.md | Guide for swarm governance under Conway R9, including review queues, apply mode, and family playbooks. | guide | move to docs/guides/ |  |  |
| current-state-and-evidence-authority.md | Defines the current state authority model, replacing self-referential commit hash with run-state authority, and details evidence bundle metadata as the authoritative source for Git HEAD. | reference | move to docs/reference/ |  |  |
| format-completion-matrix.md | Matrix tracking format completion across gates and tracks (Python FOSS, .NET product, commercial). | overview | move to docs/overview/ |  |  |
| format-expansion-roadmap.md | Roadmap for expanding to new formats, outlining phases, gates, and timelines for format acquisition. | guide | move to docs/guides/ |  |  |
| format-expansion-roadmap.yaml | Machine-readable metadata for format expansion roadmap. | reference | move to docs/reference/ |  | Keep paired with .md file. |
| format-feature-matrix-template.md | Template for format feature matrix, listing features and their completion status across formats. | reference | move to docs/reference/ |  | Can be used as a starting point for format-specific matrices. |
| format-representation-model.md | Model for representing format characteristics (e.g., text_xml, zip_container, binary_records, compound_document, delimited_text, json_like) and their acquisition implications. | reference | move to docs/reference/ |  |  |
| format-understanding-layer.md | Description of the Format Understanding Layer and its six per-format files: format-profile.yaml, verified-facts.yaml, implementation-requirements.yaml, parser-strategy.yaml, security-surface.yaml, product-readiness.yaml. | reference | move to docs/reference/ |  |  |
| fresh-chat-continuity-brief.md | Guidance for starting fresh chat sessions, emphasizing reading memory/00-index.md, memory/09-current-state-before-phase1.md, .claude/settings.json, and docs/fresh-chat-continuity-brief.md for session continuity. | guide | move to docs/guides/ |  |  |
| fresh-chat-project-bootstrap.md | Bootstrap for fresh chat project orientation, detailing the intended entry point for new sessions. | guide | move to docs/guides/ |  |  |
| fresh-chat-project-bootstrap.yaml | Machine-readable metadata for fresh chat project bootstrap. | reference | move to docs/guides/ |  | Keep paired with .md file. |
| gate-quality-criteria.md | Quality criteria for each gate, detailing the evidence and checks required for gate passage. | reference | move to docs/reference/ |  |  |
| gates.md | Detailed description of the 11 acquisition gates, their pass criteria, required artifacts, authorization rules, and fast-path options. | reference | move to docs/reference/ |  |  |
| legal-and-licensing.md | Legal categories (1-6) and licensing guidelines for format acquisition, including OASIS royalty-free, permissive OSS, proprietary+permission, and ambiguous categories. | reference | move to docs/reference/ |  |  |
| llm-and-embedding-strategy.md | Strategy for LLM and embedding usage in the project, covering permitted uses, restrictions, and future governance. | guide | move to docs/guides/ |  |  |
| llm-endpoint-strategy.md | Strategy for LLM endpoint configuration and usage, including endpoint selection, authentication, and model routing. | guide | move to docs/guides/ |  |  |
| non-aspose-format-candidate-registry-plan.md | Plan for evaluating non-Aspose format candidates for inclusion in the format registry. | guide | move to docs/guides/ |  |  |
| odf-flat-family-reuse-strategy.md | Strategy for reusing the ODF flat-XML acquisition strategy across formats (e.g., FODS, FODT), leveraging shared spec, pipeline, and tooling. | guide | move to docs/guides/ |  |  |
| oracle-provider-strategy.md | Strategy for selecting and using oracle providers (e.g., LibreOffice) for format acquisition and comparison. | guide | move to docs/guides/ |  |  |
| plan-hardening-checklist.md | 22-item checklist for hardening plans before execution, covering allowed/forbidden paths, validation commands, stop conditions, evidence bundle requirements, and more. | guide | move to docs/guides/ |  |  |
| planning-methodology.md | Core planning principles and prompt anatomy for agents, including plan challenging, inspecting referenced files, capturing gaps, not mixing sprint streams, avoiding broad destructive defaults, and requiring evidence-producing sprints to print bundle path. | guide | move to docs/guides/ |  |  |
| playbook-layer.md | Description of the playbook layer, stating that playbooks are execution aids (not authority), replay engines must be deterministic first, review queue is mandatory, family playbooks propose reuse only, and product tools are phase 4+ only. | reference | move to docs/reference/ |  |  |
| product-object-model-edit-save-export-strategy.md | Strategy for edit-save-export in the product object model, covering the flow from product creation to editing, saving, and exporting. | guide | move to docs/guides/ |  |  |
| product-tracks.md | Description of product tracks (e.g., Python open-source library, .NET product library) and their status, licensing, and development notes. | reference | move to docs/reference/ |  |  |
| project-execution-standards.md | Standards for project execution, including command structure, artifact naming, and workflow conventions. | guide | move to docs/guides/ |  |  |
| project-execution-standards.yaml | Machine-readable metadata for project execution standards. | reference | move to docs/guides/ |  | Keep paired with .md file. |
| prototype-quarantine-policy.md | Policy for quarantining prototypes to prevent premature promotion to product source, ensuring prototypes remain internal-only. | guide | move to docs/guides/ |  |  |
| release-control.md | Rules for artifact visibility and release, defining visibility classifications (public, internal, generated, evidence-only, blocked, commercial) and release manifest inclusion rules. | reference | move to docs/reference/ |  |  |
| security.md | Security guidelines for parsing untrusted file input, including mitigations for XXE, DTD, external entity resolution, and security considerations for various threat categories. | reference | move to docs/reference/ |  |  |
| source-package-hygiene.md | Guidelines for source package hygiene, prohibiting secrets, API keys, broad filesystem writes, and ensuring clean source packages. | guide | move to docs/guides/ |  |  |
| source-track-maturity-policy.md | Policy for source track maturity and promotion, defining criteria for moving source code from internal to product or commercial tracks. | guide | move to docs/guides/ |  |  |
| spec-consumption-workbench.md | Workbench for consuming specifications, including normalization, querying, and sample generation tools. | guide | move to docs/guides/ |  |  |
| spec-retrieval-and-rag-policy.md | Policy for spec retrieval and RAG (retrieval-augmented generation), covering retrieval strategies, embedding use, and truth attribution. | guide | move to docs/guides/ |  |  |
| spec-retrieval-and-rag-policy.yaml | Machine-readable metadata for spec retrieval and RAG policy. | reference | move to docs/guides/ |  | Keep paired with .md file. |
| spec-retrieval-strategy.md | Strategy for retrieving information from normalized spec artifacts, detailing the three-tier hierarchy (deterministic, lexical, vector/semantic). | guide | move to docs/guides/ |  |  |
| specification-cache.md | Policy for specification caching, including download authorization, validation, staleness detection, and cache structure (spec-index.yaml, normalized/). | reference | move to docs/reference/ |  |  |
| specification-normalization.md | Policy for normalizing spec artifacts, detailing the three-layer model (original cached spec, normalized derived artifacts, evidence pack claims), hash verification, local-only artifacts, and evidence pack citations. | reference | move to docs/reference/ |  |  |
| sprint-depth-policy.md | Policy for managing sprint depth and avoiding scope overflow, defining sprint boundaries, depth limits, and overflow handling mechanisms. | guide | move to docs/guides/ |  |  |