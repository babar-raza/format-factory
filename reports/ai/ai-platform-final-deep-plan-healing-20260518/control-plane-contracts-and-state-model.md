# Control Plane Contracts and State Model

**Sprint:** FORMAT-FACTORY-AI-PLATFORM-FINAL-DEEP-PLAN-HEALING-001
**Date:** 2026-05-18
**Gate:** 5
**Lane:** L5

---

## 1. Purpose

Define the executable contract model that connects AI tasks to the control plane. Every AI operation must pass through a contract that specifies what the task is allowed to do, what model role it requires, what schemas govern its input/output, and what authority state its output starts in.

## 2. Task Contract Model

### 2.1 Required Fields (Pydantic v2)

```
TaskContract:
  task_id: str                    # Unique task identifier
  task_type: TaskType             # Enum: extraction, test_generation, security_analysis, evidence_review, classification, sorting
  model_role: ModelRole           # Enum: agentic_low_risk, structured_extraction, security_analysis, test_generation, evidence_review, embedding_retrieval
  taskcard_id: str                # Must reference existing AI-* taskcard
  sprint_id: str                  # Current sprint
  format: Optional[str]           # Target format (fods, fodt, etc.)
  input_schema_ref: str           # Python module path to Pydantic input model
  output_schema_ref: str          # Python module path to Pydantic output model
  prompt_template_id: str         # Reference to prompt registry
  allowed_paths: list[str]        # File paths task may read
  allowed_ops: list[str]          # Operations task may perform (read, classify, extract, generate)
  forbidden_paths: list[str]      # Explicit deny list (src/**, .env, etc.)
  max_tokens: int                 # Maximum output tokens
  timeout_seconds: int            # Task timeout
  temperature: float              # LLM temperature (0.0 for deterministic tasks)
  citation_required: bool         # Whether output must cite source chunks
  contradiction_check: bool       # Whether contradiction detector must run
  authority_initial_state: str    # Always "ai_draft"
  created_at: datetime
```

### 2.2 Contract Validation Rules

1. `taskcard_id` must reference a taskcard file that exists in `taskcards/`
2. `model_role` must be defined in `tools/ai/contracts/roles.yaml`
3. `input_schema_ref` and `output_schema_ref` must be importable Python paths
4. `allowed_paths` must not overlap with `forbidden_paths`
5. `forbidden_paths` must always include: `src/python/**`, `src/net/**`, `.env`, `*.key`, `*.pem`
6. `authority_initial_state` must be `ai_draft` (no exceptions)
7. `temperature` must be 0.0 for extraction and classification tasks
8. `citation_required` must be true for extraction and test_generation tasks

### 2.3 Contract Storage

- Committed contracts: `tools/ai/contracts/tasks/{task_type}.yaml`
- Runtime-resolved contracts: loaded by gateway at call time
- Contract changes require version bump and regression eval

## 3. Role Contract Model

### 3.1 Required Fields

```
RoleRequirement:
  role: ModelRole                 # Enum value
  min_context_window: int         # Minimum context tokens
  required_capabilities: list[str] # ["chat", "structured_output", "json_mode"]
  preferred_model_family: str     # "gpt-oss", "qwen2", "embedding"
  fallback_order: list[str]       # Ordered model families to try
  quality_threshold: float        # Minimum eval score (0.0-1.0)
  max_fallback_quality_drop: float # Maximum acceptable quality reduction from preferred
```

### 3.2 Concrete Role Definitions

| Role | Min Context | Required Capabilities | Preferred | Fallback | Quality Threshold |
|------|------------|----------------------|-----------|----------|-------------------|
| agentic_low_risk | 4096 | chat, structured_output | qwen2 | gpt-oss | 0.80 |
| structured_extraction | 8192 | chat, json_mode | gpt-oss | (none — fail closed) | 0.85 |
| security_analysis | 16384 | chat | gpt-oss | (none — fail closed) | 0.80 |
| test_generation | 8192 | chat, structured_output | gpt-oss | (none — fail closed) | 0.75 |
| evidence_review | 16384 | chat | gpt-oss | (none — fail closed) | 0.70 |
| embedding_retrieval | N/A | embedding | auto-detected | (none — fail closed) | N/A |

### 3.3 Fail-Closed Semantics

When no model meets a role's minimum requirements:
1. Gateway returns `ROLE_UNAVAILABLE` error (not a fallback)
2. Telemetry records the failure with `status: role_unavailable`
3. Task contract execution stops — no partial output
4. Evidence bundle notes the gap
5. Caller receives structured error, not exception

## 4. Artifact Authority State Machine

### 4.1 States (12)

```
ai_draft → schema_validated → source_cited → source_verified →
contradiction_checked → evaluator_passed → accepted_for_planning →
accepted_for_tests → accepted_for_source_requirements →
authoritative_after_gate
Any state → rejected
Any state → superseded
```

### 4.2 Transition Prerequisites

| From | To | Prerequisite | Validator |
|------|----|-------------|-----------|
| ai_draft | schema_validated | Pydantic model validates output | schema_validator |
| schema_validated | source_cited | All claims have chunk_id citations | citation_checker |
| source_cited | source_verified | Cited chunks contain supporting text | source_support_verifier |
| source_verified | contradiction_checked | No contradiction with verified-facts.yaml | contradiction_detector |
| contradiction_checked | evaluator_passed | Golden eval score >= threshold | evaluator_runner |
| evaluator_passed | accepted_for_planning | Human or delegated review approval | human_review |
| accepted_for_planning | accepted_for_tests | Human or delegated review approval | human_review |
| accepted_for_tests | accepted_for_source_requirements | DEC-034 independent verification | iv_review |
| accepted_for_source_requirements | authoritative_after_gate | Human gate approval | gate_review |

### 4.3 Skip Prevention Enforcement

The state machine validator:
1. Reads current state from artifact metadata
2. Checks requested transition against adjacency map
3. Rejects any transition that skips an intermediate state
4. Logs rejection with reason and attempted transition
5. Evidence: transition log as JSONL

### 4.4 Integration with Format Registry Gates

| Artifact Authority State | Minimum Gate Prerequisite |
|-------------------------|--------------------------|
| accepted_for_planning | Gate 1 (candidate identified) |
| accepted_for_tests | Gate 4 (parser strategy) |
| accepted_for_source_requirements | Gate 6 (tests passing) |
| authoritative_after_gate | Gate 10+ (release candidate) |

### 4.5 Artifact Metadata Schema

```
ArtifactMetadata:
  artifact_id: str               # UUID
  artifact_type: ArtifactType    # requirement, test_idea, security_finding, summary, strategy, assessment
  authority_state: AuthorityState # Current state enum
  state_history: list[StateTransition]  # Immutable log
  source_model: str              # model_id from discovery
  model_fingerprint: Optional[str]
  prompt_version: str            # Hash of prompt template
  input_hashes: list[str]        # SHA-256 of all inputs
  output_hash: str               # SHA-256 of output
  taskcard_id: str
  sprint_id: str
  format: Optional[str]
  created_at: datetime
  updated_at: datetime

StateTransition:
  from_state: AuthorityState
  to_state: AuthorityState
  timestamp: datetime
  validator: str                 # Name of validator/reviewer
  evidence_ref: str              # Path to validation result
  notes: Optional[str]
```

## 5. Gateway Contract

The AI Gateway (`tools/ai/control_plane/gateway.py`) is the **only** entry point for AI calls:

1. Receives: TaskContract + caller context
2. Validates: contract fields, role requirements, path restrictions
3. Resolves: model via router
4. Executes: LLM call via LiteLLM
5. Validates: output against output_schema_ref
6. Records: telemetry
7. Returns: TaskResult with authority_state=ai_draft

**Gateway MUST reject:**
- Tasks without valid contract
- Tasks with unknown model_role
- Tasks referencing forbidden paths
- Tasks without linked taskcard
- Tasks where model role is ROLE_UNAVAILABLE

## 6. Contract Versioning

- Task contracts: versioned YAML, changes require regression eval
- Role contracts: versioned YAML in `tools/ai/contracts/roles.yaml`
- Prompt templates: versioned with content hash in `tools/ai/prompts/{task_type}/v{N}.yaml`
- Schema versions: Python module version + structural hash
- Breaking changes: require explicit migration and re-validation of existing artifacts
