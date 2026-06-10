# AI Management Model

**Sprint:** FORMAT-FACTORY-ACCELERATION-PRODUCT-FIRST-AI-LLM-EMBEDDING-EXECUTION-001
**Date:** 2026-06-04

---

## 5 AI Layers

| Layer | Tool | Role | Gateway Role | Fixture OK? |
|-------|------|------|--------------|-------------|
| 1. Observation | ai_product_brain | Reads all POC targets; builds capability graph | summarization | YES |
| 2. Management | ai_sprint_manager | Pre/mid/final sprint passes; stuck lane detection | agentic_low_risk | NO — skipped |
| 3. Design | ai_implementation_designer | Per-gap implementation + test + dogfood design | structured_extraction | YES |
| 4. Critique | ai_evidence_critic | Semantic sprint review; MACHINERY_CREEP detection | evidence_review | YES |
| 5. Learning | ai_learning_loop | Categorized JSONL learnings for next sprint | summarization | YES |

## 5 Components

| Component | Tool | Output |
|-----------|------|--------|
| Source Intelligence | source_pattern_miner | Format-namespaced TF-IDF + AI summary |
| Test Design | test_plan_generator | 6-type proposals + AI enhancement |
| Packet Assembly | mainstream_acceleration_packet | 7-section packet per format gap |
| Evidence Layer | ai_evidence_critic | sprint_grade + machinery_creep verdict |
| Memory Layer | ai_learning_loop | sprint-learnings.jsonl machine-readable |

## Interaction Graph

```
poc-targets.yaml (read-only)
        ↓
ai_product_brain (observes)
        ↓
ai_sprint_manager pre-pass (plans lanes)
        ↓
source_pattern_miner × 4 formats (mines src/)
ai_implementation_designer × 4 formats (designs)
test_plan_generator × 4 gaps (test plans)
        ↓
mainstream_acceleration_packet × 4 formats (assembles)
        ↓
ai_sprint_manager mid-pass (checks for stuck lanes)
        ↓
ai_evidence_critic (critiques semantic quality)
        ↓
ai_learning_loop (records learnings as JSONL)
        ↓
ai_sprint_manager final-pass (grades sprint; recommends next)
        ↓
next sprint reads sprint-learnings.jsonl at pre-pass
```

## Authority at Each Layer

All layers output `authority_state: ai_draft`. No layer may modify:
- poc-targets.yaml
- src/net/ or src/python/
- skill-registry.yaml
- plans/master-plan.md

Evidence pipeline (tests + validator + human gate) is the only path to advancing artifacts
past ai_draft.
