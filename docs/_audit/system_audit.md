# System Audit

## Product/System Purpose
format-factory is a File Format Acquisition System that produces legal parsers, converters, importers, exporters, validators, and compatibility tools for structured file formats. This is evidenced by the README.md and the acquisition pipeline implementation in tools/ (evidence, oracle, validation, etc.) and the gate-based progression recorded in registry/format-registry.yaml.

## Component Map
- **docs/**: Architecture, policy, and process documentation
- **plans/**: Living master plan (single operational authority)
- **taskcards/**: Atomic work units
- **registry/**: Format registry and scoring model (registry/format-registry.yaml, registry/scoring/_scoring-model.md)
- **acquisition-packs/**: Per-format evidence, legal notes, samples, parser notes
- **samples/**: Licensed sample corpus with provenance records
- **schemas/**: Neutral-model and format-understanding schemas
- **prototypes/**: Reference prototype parsers (internal only)
- **src/**: Production source code (src/python/{format}/ for Python FOSS, src/net/{format}/ for .NET product)
- **tests/**: Test fixtures, oracle outputs, fuzz seeds, product tests
- **tools/**: Acquisition, scoring, validation, evidence, and oracle tools (subdirectories: ai, evidence, format_understanding, fuzz, governance, llm, model, oracle, package, packaging, playbook, requirements, samples, skills, spec-cache, spec-normalize, state, testing)
- **reports/**: Security and legal reports
- **.claude/**: Claude Code project configuration and commands

## Key Workflows
The acquisition pipeline consists of 11 mandatory gates (see docs/gates.gov):
1. **Gate 1**: Candidate Accepted – scoring and legal classification
2. **Gate 2**: Evidence Complete – spec analysis and legal notes
3. **Gate 3**: Sample Corpus Ready – licensed samples with confirmed provenance
4. **Gate 4**: Prototype Complete – working parser and security baseline
5. **Gate 5**: Neutral Model Defined – format-family data schema
6. **Gate 6**: Oracle Comparison Complete – discrepancy analysis
7. **Gate 7**: Fuzz Testing Complete
8. **Gate 8**: Security Review Complete
9. **Gate 9**: Product Mapping Complete – tier assignment and delivery plan
10. **Gate 10**: OSS Readiness Complete – production source and release manifest
11. **Gate 11**: Commercial Readiness Complete – commercial tier and proprietary manifest
Agents may prepare evidence, but only a human can approve a gate (see docs/gates.md and AGENTS.md §D1). The pipeline is sequential: a format may not begin Stage N+1 work until Gate N has been passed and recorded (docs/gates.md §15.3).

## Config Reference
- **.claude/settings.json**: Claude Code permissions, model, phase, and notes (see .claude/settings.json)
- **.env.example**: Template for environment variables including LLM endpoints (ANTHROPIC_API_KEY, OPENAI_API_KEY, PROFESSIONALIZE_API_KEY, LOCAL_LLM_ENDPOINT, LOCAL_LM_STUDIO_ENDPOINT, LOCAL_CUSTOM_ENDPOINT, GPT_OSS_ENDPOINT, GPT_OSS_API_KEY, AGENT_METRICS_ENDPOINT, AGENT_METRICS_API_KEY)
- **tools/llm/endpoints.yaml**: LLM endpoint configuration (referenced in .env.example)
- **tools/llm/model-selection.yaml**: Model selection rules (referenced in docs/llm-endpoint-strategy.md)
- **pytest.ini**: Pytest configuration (--import-mode=importlib, timeout=120)
- **kilo.json**: Not present in this repository
- **setup.py/pyproject.toml**: Not present; project uses external tooling

## CLI/API Reference
- **Claude Code Slash Commands** (in .claude/commands/):
  - `/evidence-review-next-prompt`: Review evidence bundle and produce next execution prompt
  - `/execution-handoff`: Generate execution handoff prompt
  - `/export-plan-context`: Export plan context for agent
  - `/memory-sprint`: Run memory sprint
  - `/plan-hardening`: Harden a plan for execution
- **Python Tools** (in tools/):
  - `tools/evidence/build_evidence_bundle.py`: Build evidence bundles
  - `tools/evidence/validate_evidence_bundle.py`: Validate evidence bundles
  - `tools/evidence/check_current_state_consistency.py`: Check current state consistency
  - `tools/evidence/write_sidecar_proof.py`: Write sidecar proof
  - `tools/ai/run_ai_checks.py`: Run AI pipeline checks
  - `tools/skills/commands/format_context.py`: Format context resolver (internal)
  - `tools/skills/commands/commercial_sprint.py`: Commercial sprint orchestrator (internal)
  - `tools/oracle/run_fods_oracle.py`, `tools/oracle/run_fodt_oracle.py`: Oracle comparison runners
  - `tools/model/validate_neutral_model.py`: Neutral model validation
  - `tools/playbook/validate_playbook.py`: Playbook validation
  - `tools/spec-normalize/normalize_pdf.py`: PDF normalization
  - `tools/spec-normalize/query_normalized_spec.py`: Query normalized spec
  - `tools/samples/create_fods_samples.py`, `tools/samples/create_fodt_samples.py`: Sample generation
- **External Interfaces**: No REST API or gRPC service defined in codebase; interaction is via file-based evidence and command-line tools.

## Data Directories and File Contracts
- **samples/by-format/{format}/**: Licensed samples with confirmed provenance (see samples/_provenance.yaml)
- **acquisition-packs/{format}/**: Per-format evidence (spec-evidence.md, legal-notes.md, sample-sources.md, parser-notes.md, gate plans, pack.yaml)
- **schemas/neutral-model/{format}/**: Neutral model entities, mappings, and validation rules (model.yaml, field-map.yaml, validation-rules.yaml)
- **schemas/playbook/**: Playbook schemas for acquisition-pack and family playbooks
- **prototypes/by-format/{format}/**: Reference prototype parsers (internal only)
- **src/python/{format}/**: Production Python FOSS source (e.g., __init__.py, parser.py, neutral_model.py, constants.py, exceptions.py, list_traversal.py, writer.py)
- **src/net/{format}/**: Production .NET source (C# projects, e.g., FormatFactory.Fods.csproj)
- **tests/**: 
  - tests/fixtures/{format}/: Test fixtures (malformed, fuzz, etc.)
  - tests/oracle/{format}/: Oracle outputs for comparison
  - tests/fuzz/{format}/: Fuzz test seeds
  - tests/python/{format}/: Product tests for Python FOSS
  - tests/net/{format}/: Product tests for .NET
  - tests/evidence/, tests/governance/, tests/playbook/, tests/format_understanding/: Domain-specific tests
- **tools/evidence/**: Evidence bundle metadata (bundle-manifest.yaml, git-log.txt, git-status-final.txt, verdict.md, etc.)
- **tools/spec-cache/{format}/{version}/**: Cached specifications (spec-index.yaml, normalized/)

## Observability
- **Logging**: AI pipeline logging via tools/ai/telemetry/ (call_logger.py, drain.py, spool_manager.py, artifacts.py)
- **Telemetry**: Agent Metrics endpoint configurable via .env.example (AGENT_METRICS_ENDPOINT, AGENT_METRICS_API_KEY)
- **Metrics**: AI synthesis evaluation, citation verification, contradiction detection, and evaluator regression (see tools/ai/synthesis/)
- **Artifact Index**: LLM run records stored in .local/llm-logs/ (see AGENTS.md §H5)
- **State Consistency**: Current state consistency checked via tools/evidence/check_current_state_consistency.py
- **Git Safety**: Git safety checked via tools/governance/check_git_safety.py

## Testing Strategy
- **Unit Tests**: Located in tests/python/{format}/ and tests/net/{format}/ for product source
- **Fixture Tests**: tests/fixtures/{format}/ for malformed and fuzz inputs
- **Oracle Comparison**: Tests compare output against reference implementations (LibreOffice) via tools/oracle/
- **Fuzz Testing**: tests/fuzz/{format}/ for fuzz seeds
- **Evidence Validation**: Tests for evidence bundle validation in tools/evidence/
- **Playbook Validation**: Tests for playbook schema in tools/playbook/
- **Format Understanding**: Tests for format understanding layer in tools/format_understanding/
- **Pytest Configuration**: pytest.ini uses --import-mode=importlib to avoid basename collisions and sets timeout=120
- **Test Runner**: tools/testing/run_bounded_pytest.py provides bounded replay fallback
- **Full Suite**: Can be run with `python -m pytest tests/` (see README.md and TC-0052 test results)

## Known Gaps/Risks
- **Gap G-NORM-002**: Hash mismatch detected on re-verification of normalized artifacts (see docs/specification-normalization.md)
- **Gap G-NORM-004**: Normalization tooling unavailable (see docs/specification-normalization.md)
- **Gap M1**: Unknown, ambiguity, missing required artifact, or situation not covered by existing rules must be logged as a gap (see AGENTS.md §M1)
- **Gap T3-gap**: Missing spec from cache and download not authorized must be logged as a gap (see AGENTS.md §T3-gap)
- **Gap G-HEAL-015**: Product source layout in governance docs used obsolete paths (resolved in run011, see plans/master-plan.md)
- **Risk**: Network download commands (curl, wget, Invoke-WebRequest, iwr) are denied by default in .claude/settings.json; spec acquisition requires explicit T3 authorization (see AGENTS.md §T3)
- **Risk**: LLM-generated content defaults to visibility: generated; changing to public requires human approval (see AGENTS.md §F6)
- **Risk**: Full specification documents must not be sent to remote LLM endpoints by default (see AGENTS.md §T9)
- **Risk**: Commercial artifacts must never appear in open-source releases (see AGENTS.md §G3)