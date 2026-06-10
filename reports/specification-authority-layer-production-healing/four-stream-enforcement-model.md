# Four-Stream Enforcement Model
Sprint ID: FORMAT-FACTORY-SPECIFICATION-AUTHORITY-LAYER-PRODUCTION-BLOCKER-PLAN-HEALING-001

## Overview

The Format Factory operates four streams. Each stream has different spec-authority requirements
enforced by SpecGovernanceRuntime at every handoff point.

---

## Stream Definitions and Requirements

### Stream 1 — Mainstream Product

**Description:** Product implementation and test work (src/net, src/python, tests/).
**Spec authority level:** MAXIMUM
**Required at handoff:**
- context_pack_id (verified, not stale)
- manifest_sha256 (64-char hex)
- requirement_ids (at least 1 verified requirement per implemented behavior)
- source_snapshot_ids (list of sha256s)
- No ai_draft claims (AI summaries must be labeled; cannot be the spec authority)

**Evidence declaration enforcement:**
```yaml
# Required in evidence declaration for mainstream work:
spec_authority:
  context_pack_id: "<uuid>"
  manifest_sha256: "<64-char-hex>"
  requirement_ids: ["req-zst-001", "req-zst-002"]
  source_snapshot_ids: ["<sha256>"]
```

**Rejection conditions:**
- Missing context_pack_id → FAIL: MISSING_CONTEXT_PACK_ID
- Stale context pack → FAIL: STALE_CONTEXT_PACK
- requirements from unverified source → FAIL: UNVERIFIED_REQUIREMENTS
- ai_draft without label → FAIL: UNLABELED_AI_DRAFT

---

### Stream 2 — Acceleration Layer

**Description:** Governed acceleration work (prototype tools, rapid iteration).
**Spec authority level:** HIGH
**Required at handoff:**
- context_pack_id (verified, not stale)
- requirement_ids
- source_snapshot_ids
- ai_draft label on any AI-generated content (MANDATORY)

**Enforcement note:**
- Acceleration outputs MUST carry ai_draft label
- ai_draft outputs cannot be promoted to mainstream without SpecVerifier review
- ai_draft requirement claims not accepted as production spec authority

**Evidence declaration enforcement:**
```yaml
spec_authority:
  context_pack_id: "<uuid>"
  requirement_ids: ["req-zst-001"]
  source_snapshot_ids: ["<sha256>"]
  ai_draft: true  # Mandatory for acceleration outputs
```

---

### Stream 3 — Skills (Governed Execution)

**Description:** Skill templates and transcripts.
**Spec authority level:** HIGH
**Required at handoff:**
- context_pack_id
- requirement_ids
- usage_id (from usage ledger — confirms pack was consumed and recorded)
- No ad-hoc URL citations (all sources must be registered)

**Enforcement note:**
- Skill transcripts must reference registered sources only
- Memory-only spec claims rejected (must have source_ref)
- usage_id ensures ledger traceability

**Evidence declaration enforcement:**
```yaml
spec_authority:
  context_pack_id: "<uuid>"
  requirement_ids: ["req-zst-001"]
  usage_id: "usage-<uuid>"  # From usage ledger
```

---

### Stream 4 — Supervisor

**Description:** Sprint supervision, grading, contradiction detection.
**Spec authority level:** VALIDATION
**Supervisor checks:**
- context_pack_id present in evidence declarations for spec-dependent work
- Stale context packs flagged as contradictions
- ai_draft misuse detected (ai_draft in spec authority position without label)
- Unsupported claims (spec authority without source_ref) flagged
- False PASS (worker_self_verdict: PASS with no spec authority for spec-dependent work) flagged

**Supervisor enforcement:**
```python
def validate_spec_authority(declaration):
    if declaration.get("spec_dependent") and not declaration.get("spec_authority"):
        return CONTRADICTION("MISSING_SPEC_AUTHORITY_IN_SPEC_DEPENDENT_WORK")
    pack_id = declaration.get("spec_authority", {}).get("context_pack_id")
    if pack_id and context_pack_store.get(pack_id, {}).get("stale"):
        return CONTRADICTION("STALE_CONTEXT_PACK_IN_DECLARATION")
    return PASS
```

---

## Handoff Gate Summary

| Stream | context_pack_id | manifest_sha256 | requirement_ids | source_sha256s | usage_id | ai_draft label |
|--------|----------------|----------------|-----------------|---------------|----------|---------------|
| Mainstream | REQUIRED | REQUIRED | REQUIRED | REQUIRED | optional | PROHIBITED (spec authority) |
| Acceleration | REQUIRED | optional | REQUIRED | REQUIRED | optional | REQUIRED on output |
| Skills | REQUIRED | optional | REQUIRED | optional | REQUIRED | not allowed in spec authority |
| Supervisor | validates | validates | validates | validates | validates | detects misuse |

---

## Anti-Bypass Enforcement Rules

| Bypass Pattern | Detection | Response |
|----------------|-----------|----------|
| Ad-hoc URL citation without registered source | SpecSourceRegistry.is_approved(url) = false | FAIL: UNREGISTERED_SOURCE |
| Memory-only spec claim ("the spec says X" with no source_ref) | source_ref absent in claim | FAIL: UNSOURCED_CLAIM |
| Raw AI summary without ai_draft label | No ai_draft label but AI-generated | FAIL: UNLABELED_AI_DRAFT |
| Unverified requirement in production pack | Req status = candidate_requirement | FAIL: UNVERIFIED_REQUIREMENT_IN_PACK |
| Context pack without manifest.sha256 | manifest_sha256 absent | FAIL: MISSING_MANIFEST_SHA256 |
| Stale context pack used | stale=true in pack record | FAIL: STALE_CONTEXT_PACK |
