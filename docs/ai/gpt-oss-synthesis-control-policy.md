# GPT-OSS Synthesis Control Policy

**Version:** 1.0
**Date:** 2026-05-18
**Status:** PLAN — Implementation not yet authorized
**Authority:** docs/ai/ai-platform-operating-model.md

---

## 1. Purpose

Define the controls for using GPT-OSS (via llm.professionalize.com) for LLM transformation and synthesis tasks. GPT-OSS is the preferred model family for structured extraction, analysis, and synthesis. Its outputs require more than schema validation — they require citation verification, contradiction detection, evaluator regression, and full artifact authority lifecycle enforcement.

## 2. Allowed Use Cases

| Use Case | Input | Output Schema | Citation Required |
|----------|-------|---------------|-------------------|
| Spec understanding | Normalized spec chunks | Section map YAML | Yes — chunk IDs |
| Requirement extraction | Spec chunks + existing facts | Requirement YAML | Yes — spec section |
| Test idea generation | Requirements + samples | Test idea YAML | Yes — requirement ID |
| Security analysis | Parser code + spec | Security finding YAML | Yes — code location + spec section |
| Evidence review | Sprint artifacts | Gap analysis YAML | Yes — artifact paths |
| Summary generation | Sprint report inputs | Summary markdown | Yes — source sections |
| Parser strategy drafting | Spec chunks + format samples | Strategy YAML | Yes — spec sections + sample IDs |
| Release-readiness review | Gate evidence | Readiness assessment YAML | Yes — gate evidence items |

## 3. Required Controls

### 3.1 Input Controls

| Control | Description |
|---------|-------------|
| Prompt/task contract | Versioned prompt template + task schema defining inputs and constraints |
| Input normalization | All spec inputs must come from normalized artifacts (not raw PDFs) |
| Input hash | SHA-256 of all input artifacts recorded in provenance |
| Context window check | Verify total input tokens fit within model context window |
| Sensitive content filter | No secrets, credentials, or private data in prompts |

### 3.2 Output Controls

| Control | Description |
|---------|-------------|
| Pydantic/JSON schema validation | Output must conform to declared schema |
| Cited source chunk requirement | Every factual claim must cite a specific source chunk ID |
| Source-support verifier | Deterministic check that the cited chunk actually contains supporting text |
| Contradiction detector | Compare output against existing verified facts; flag conflicts |
| Artifact authority state | Output tagged as `ai_draft` in authority lifecycle |
| Deterministic acceptance gate | Schema + citation + contradiction checks must ALL pass |

### 3.3 Regression Controls

| Control | Description |
|---------|-------------|
| Evaluator/regression suite | Golden eval dataset for each synthesis task type |
| Baseline comparison | New outputs compared against known-good baselines |
| Quality metrics | Precision, recall, citation accuracy tracked per task type |
| Prompt version tracking | Every prompt change triggers regression eval |
| Model change detection | If model fingerprint changes, trigger regression eval |

### 3.4 Provenance Controls

Every synthesis run must record:
- `model_id` and `model_fingerprint`
- `prompt_version` — hash of the prompt template used
- `input_hashes` — SHA-256 of each input artifact
- `output_hash` — SHA-256 of the output
- `taskcard_id` — linked taskcard
- `sprint_id` — current sprint
- `gate` — relevant gate if applicable
- `format` — target format
- `timestamp` — ISO 8601
- `token_counts` — input, output, total
- `citation_count` — number of source citations in output
- `citation_verified_count` — number passing source-support verification
- `contradiction_count` — number of detected contradictions
- `evaluator_score` — regression eval score if applicable

## 4. Output Authority Lifecycle

GPT-OSS synthesis output follows the artifact authority lifecycle:

```
ai_draft → schema_validated → source_cited → source_verified →
contradiction_checked → evaluator_passed → accepted_for_planning →
accepted_for_tests → accepted_for_source_requirements →
authoritative_after_gate
```

No skip allowed. Each transition requires the corresponding validation to pass. See `docs/ai/ai-artifact-authority-lifecycle.md`.

## 5. Prohibited Uses

GPT-OSS MUST NOT be used for:
- Gate approval decisions
- Authority file modifications without human review
- Direct code generation committed to product source
- Replacing human/delegated verification (DEC-034)
- Generating evidence that bypasses validation
- Making commercial readiness claims
- Producing outputs that skip the authority lifecycle

## 6. Failure Modes

| Failure | Response |
|---------|----------|
| GPT-OSS unavailable | Fail closed. Do not substitute Qwen2 for synthesis tasks. |
| Output fails schema validation | Reject. Log. May retry once with same prompt. |
| Citations do not match source | Reject entire output. Flag as hallucination risk. |
| Contradiction detected | Flag contradicting claims. Human review required before resolution. |
| Evaluator score below threshold | Reject output. Investigate prompt or model drift. |
| Context window exceeded | Split input into chunks. Process sequentially. Merge with dedup. |

## 7. Cross-References

| Document | Relationship |
|----------|-------------|
| `docs/ai/ai-platform-operating-model.md` | Parent platform model, Type B controls |
| `docs/ai/model-routing-and-discovery-policy.md` | GPT-OSS routing policy |
| `docs/ai/ai-artifact-authority-lifecycle.md` | Output authority states |
| `docs/ai/ai-risk-register.md` | RISK-AI-006 (hallucination), RISK-AI-007 (citation mismatch) |
