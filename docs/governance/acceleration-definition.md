# Acceleration Definition

**Added:** 2026-06-03
**Authority:** plans/master-plan.md Section 43

## Problem Statement

Acceleration drifted from its original purpose (AI product acceleration) into governance-only machinery (anti-skip checking, prompt-quality metrics). This correction restores the original intent while preserving the governance value.

## Original Intent

Use AI/LLM/embeddings/retrieval to accelerate product development:
- Understand format specifications faster
- Mine source patterns for code generation
- Generate test cases from spec requirements
- Rank product gaps by impact
- Provide code-generation handoffs to Mainstream

## Drift Pattern

What happened:
- Anti-skip checker became a standalone feature
- Prompt-quality validation became self-referential
- Sample output generation served evidence quality, not product quality
- Stream-aware prompts optimized for machinery, not product throughput

## Corrected Model

### Acceleration-A: Governance Harness
Legitimate safety work that prevents product harm:
- Anti-skip enforcement (prevents skipping required work)
- Prompt-quality validation (ensures sprint prompts are actionable)
- Evidence-quality checks (ensures work claims are honest)

Success criteria: measurable reduction in false PASS or false STOP.

### Acceleration-B: AI Product Acceleration
Legitimate product acceleration:
- Spec understanding (LLM-assisted requirement extraction)
- Source-pattern mining (identify reusable code patterns)
- Code-generation handoffs (produce draft implementations for Mainstream)
- Test generation (produce test cases from spec requirements)
- Product gap ranking (prioritize most impactful capability gaps)

Success criteria: measurable increase in Mainstream product throughput.

## Validation

At sprint closeout, Acceleration must answer:
1. Which sub-lane did this sprint serve (A, B, or both)?
2. What product blocker was removed (A) or what product throughput improved (B)?
3. If neither: why was this sprint necessary?
