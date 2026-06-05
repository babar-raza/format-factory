# Documentation Inventory

## Overview
This inventory lists all documentation files under `docs/` with their intended audience, purpose, status, and proposed action. ROOT ORPHANS (files directly under `docs/` excluding `docs/README.md` and meta folders) are highlighted.

## Table: Documentation Files

| Path | Intended Audience | Purpose | Status | Action | Notes |
|------|-------------------|---------|--------|--------|-------|
| acquisition-workflow.md | Contributor | Describes the end-to-end acquisition workflow from spec to release. | Accurate | keep | Matches code structure in tools/ and registry/. |
| agent-execution-handoff-standard.md | Contributor | Standard for agent execution handoff prompts. | Accurate | keep | Referenced in .claude/commands/evidence-review-next-prompt.md. |
| agent-methodology-index.md | Contributor | Index of agent methodology documents. | Accurate | keep | Entry point for plan and prompt work per README.md. |
| agent-swarm-ai-orchestration.md | Contributor | Guidance on AI-assisted agent swarm orchestration. | Unknown | keep | No verification performed. |
| ai-assisted-commercial-development.md | Contributor | Patterns for AI-assisted commercial development in src/net/{format}/. | Accurate | keep | Authority level normative; matches .NET source structure. |
| ai-assisted-commercial-development.yaml | Contributor | Machine-readable metadata for ai-assisted-commercial-development.md. | Accurate | keep | Structured counterpart to .md file. |
| ai-generated-format-requirements-pipeline.md | Contributor | Pipeline for AI-generated format requirements. | Unknown | keep | No verification performed. |
| ai-generated-format-requirements-pipeline.yaml | Contributor | Machine-readable metadata for AI-generated format requirements pipeline. | Unknown | keep | No verification performed. |
| ai-usage-operating-model.md | Contributor | Operating model for AI usage in the project. | Unknown | keep | No verification performed. |
| ai-usage-operating-model.yaml | Contributor | Machine-readable metadata for AI usage operating model. | Unknown | keep | No verification performed. |
| architecture.md | Contributor | High-level architecture of the format-factory system. | Accurate | keep | Describes components and their responsibilities. |
| assistant-supervision-methodology.md | Contributor | Methodology for supervising agent execution. | Unknown | keep | No verification performed. |
| assistant-supervision-methodology.yaml | Contributor | Machine-readable metadata for assistant supervision methodology. | Unknown | keep | No verification performed. |
| commercial-dotnet-architecture.md | Contributor | Architecture details for .NET commercial product. | Unknown | keep | No verification performed. |
| commercial-dotnet-architecture.yaml | Contributor | Machine-readable metadata for commercial .NET architecture. | Unknown | keep | No verification performed. |
| commercial-product-capability-model.md | Contributor | Capability model for commercial product readiness. | Unknown | keep | No verification performed. |
| commercial-product-capability-model.yaml | Contributor | Machine-readable metadata for commercial product capability model. | Unknown | keep | No verification performed. |
| conway-r9-authority-continuity.md | Contributor | Authority continuity model for Conway R9 governance. | Unknown | keep | No verification performed. |
| conway-r9-governed-simulation.md | Contributor | Governed simulation for Conway R9. | Unknown | keep | No verification performed. |
| conway-r9-swarm-governance.md | Contributor | Swarm governance model for Conway R9. | Unknown | keep | No verification performed. |
| current-state-and-evidence-authority.md | Contributor | Defines current state authority model and evidence bundling rules. | Accurate | keep | Referenced in AGENTS.md §Z and elsewhere. |
| format-completion-matrix.md | Contributor | Matrix tracking format completion across gates and tracks. | Unknown | keep | No verification performed. |
| format-expansion-roadmap.md | Contributor | Roadmap for expanding to new formats. | Unknown | keep | No verification performed. |
| format-expansion-roadmap.yaml | Contributor | Machine-readable metadata for format expansion roadmap. | Unknown | keep | No verification performed. |
| format-feature-matrix-template.md | Contributor | Template for format feature matrix. | Unknown | keep | No verification performed. |
| format-representation-model.md | Contributor | Model for representing format characteristics (e.g., text_xml, zip_container). | Unknown | keep | No verification performed. |
| format-understanding-layer.md | Contributor | Description of the Format Understanding Layer and its six per-format files. | Accurate | keep | Describes format-profile.yaml, verified-facts.yaml, etc., matching acquisition-packs/ structure. |
| fresh-chat-continuity-brief.md | Contributor | Guidance for starting fresh chat sessions. | Accurate | keep | Referenced in README.md under "Agent Methodology and Fresh Chat Start". |
| fresh-chat-project-bootstrap.md | Contributor | Bootstrap for fresh chat project orientation. | Unknown | keep | No verification performed. |
| fresh-chat-project-bootstrap.yaml | Contributor | Machine-readable metadata for fresh chat project bootstrap. | Unknown | keep | No verification performed. |
| gate-quality-criteria.md | Contributor | Quality criteria for each gate. | Unknown | keep | No verification performed. |
| gates.md | Contributor | Detailed description of the 11 acquisition gates, pass criteria, and rules. | Accurate | keep | Defines gate model used in registry/format-registry.yaml. |
| legal-and-licensing.md | Contributor | Legal categories and licensing guidelines for format acquisition. | Unknown | keep | No verification performed. |
| llm-and-embedding-strategy.md | Contributor | Strategy for LLM and embedding usage in the project. | Unknown | keep | No verification performed. |
| llm-endpoint-strategy.md | Contributor | Strategy for LLM endpoint configuration and usage. | Unknown | keep | No verification performed. |
| non-aspose-format-candidate-registry-plan.md | Contributor | Plan for evaluating non-Aspose format candidates. | Unknown | keep | No verification performed. |
| odf-flat-family-reuse-strategy.md | Contributor | Strategy for reusing ODF flat-XML acquisition across formats (FODS, FODT, etc.). | Accurate | keep | Referenced in README.md; matches reuse of spec and pipeline for FODS/FODT. |
| oracle-provider-strategy.md | Contributor | Strategy for selecting and using oracle providers (e.g., LibreOffice). | Unknown | keep | No verification performed. |
| plan-hardening-checklist.md | Contributor | 22-item checklist for hardening plans before execution. | Accurate | keep | Referenced in README.md and .claude/commands/plan-hardening.md. |
| planning-methodology.md | Contributor | Core planning principles and prompt anatomy for agents. | Accurate | keep | Referenced in README.md and .claude/commands/evidence-review-next-prompt.md. |
| playbook-layer.md | Contributor | Description of the playbook layer for acquisition-pack and family playbooks. | Unknown | keep | No verification performed. |
| product-object-model-edit-save-export-strategy.md | Contributor | Strategy for edit-save-export in product object model. | Unknown | keep | No verification performed. |
| product-tracks.md | Contributor | Description of product tracks (e.g., Python open-source, .NET product). | Accurate | keep | Matches src/python/{format}/ and src/net/{format}/ structure. |
| project-execution-standards.md | Contributor | Standards for project execution (e.g., command structure, artifact naming). | Unknown | keep | No verification performed. |
| project-execution-standards.yaml | Contributor | Machine-readable metadata for project execution standards. | Unknown | keep | No verification performed. |
| prototype-quarantine-policy.md | Contributor | Policy for quarantining prototypes to prevent premature promotion. | Unknown | keep | No verification performed. |
| release-control.md | Contributor | Rules for artifact visibility and release (public, internal, generated, etc.). | Accurate | keep | Defines visibility classifications used in AGENTS.md §F. |
| security.md | Contributor | Security guidelines for parsing untrusted file input (mitigations for XXE, DTD, etc.). | Accurate | keep | Referenced in AGENTS.md §Q; matches parser.py security mitigations. |
| source-package-hygiene.md | Contributor | Hygiene rules for source packages (e.g., no secrets, no broad writes). | Unknown | keep | No verification performed. |
| source-track-maturity-policy.md | Contributor | Policy for source track maturity and promotion. | Unknown | keep | No verification performed. |
| spec-consumption-workbench.md | Contributor | Workbench for consuming specifications (normalization, querying). | Unknown | keep | No verification performed. |
| spec-retrieval-and-rag-policy.md | Contributor | Policy for spec retrieval and RAG (retrieval-augmented generation). | Unknown | keep | No verification performed. |
| spec-retrieval-and-rag-policy.yaml | Contributor | Machine-readable metadata for spec retrieval and RAG policy. | Unknown | keep | No verification performed. |
| spec-retrieval-strategy.md | Contributor | Strategy for retrieving information from normalized spec artifacts. | Unknown | keep | No verification performed. |
| specification-cache.md | Contributor | Policy for specification caching (download, validation, staleness). | Accurate | keep | Matches tools/spec-cache/ and AGENTS.md §T. |
| specification-normalization.md | Contributor | Policy for normalizing spec artifacts (local-only, hash verification, etc.). | Accurate | keep | Matches tools/spec-normalize/ and AGENTS.md §W. |
| sprint-depth-policy.md | Contributor | Policy for managing sprint depth and avoiding scope overflow. | Unknown | keep | No verification performed. || ai\agentic-qwen2-control-policy.md | Contributor | agentic qwen2 control policy | Unknown | keep | |
| ai\ai-artifact-authority-lifecycle.md | Contributor | ai artifact authority lifecycle | Unknown | keep | |
| ai\ai-assisted-acquisition-pipeline.md | Contributor | ai assisted acquisition pipeline | Unknown | keep | |
| ai\ai-platform-operating-model.md | Contributor | ai platform operating model | Unknown | keep | |
| ai\ai-risk-register.md | Contributor | ai risk register | Unknown | keep | |
| ai\ai-system-verification-matrix.md | Contributor | ai system verification matrix | Unknown | keep | |
| ai\ai-technology-decision-record.md | Contributor | ai technology decision record | Unknown | keep | |
| ai\ai-telemetry-and-agent-metrics-policy.md | Contributor | ai telemetry and agent metrics policy | Unknown | keep | |
| ai\deferred-ai-features-review.md | Contributor | deferred ai features review | Unknown | keep | |
| ai\embedding-and-vector-store-policy.md | Contributor | embedding and vector store policy | Unknown | keep | |
| ai\gpt-oss-synthesis-control-policy.md | Contributor | gpt oss synthesis control policy | Unknown | keep | |
| ai\model-routing-and-discovery-policy.md | Contributor | model routing and discovery policy | Unknown | keep | |
| ai\readme.md | Contributor | readme | Unknown | keep | |
| commercial-gate11\r23-g11e-status-20260517.md | Contributor | r23 g11e status 20260517 | Unknown | keep | |
| examples\acquisition-playbook-fods-documentation-example.yaml | Contributor | acquisition playbook fods documentation example | Unknown | keep | |
| prompts\closure-hygiene-prompt-template.md | Contributor | closure hygiene prompt template | Unknown | keep | |
| prompts\evidence-bundle-review-prompt-template.md | Contributor | evidence bundle review prompt template | Unknown | keep | |
| prompts\execution-handoff-prompt-template.md | Contributor | execution handoff prompt template | Unknown | keep | |
| prompts\fresh-chat-bootstrap-prompt.md | Contributor | fresh chat bootstrap prompt | Unknown | keep | |
| prompts\independent-verification-prompt-template.md | Contributor | independent verification prompt template | Unknown | keep | |
| prompts\memory-sprint-prompt-template.md | Contributor | memory sprint prompt template | Unknown | keep | |
| prompts\plan-hardening-prompt-template.md | Contributor | plan hardening prompt template | Unknown | keep | |
| prompts\README.md | Contributor | README | Unknown | keep | |
| prompts\unblocking-patch-prompt-template.md | Contributor | unblocking patch prompt template | Unknown | keep | |
| python-foss\api-guidelines.md | Contributor | api guidelines | Unknown | keep | |
| python-foss\examples-index.md | Contributor | examples index | Unknown | keep | |
| python-foss\format-support-matrix.md | Contributor | format support matrix | Unknown | keep | |
| python-foss\release-process.md | Contributor | release process | Unknown | keep | |
| python-foss\security-model.md | Contributor | security model | Unknown | keep | |
