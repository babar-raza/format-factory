# Scoring Model

**Document type:** Process Reference — Phase 0 Foundation
**Last reviewed:** 2026-05-03 (run005: Hardened to seven-factor 100-point format-neutral model. FODS pre-scoring removed.)
**Authority:** This document defines the scoring model used at Gate 1 to evaluate format candidates. All Gate 1 evaluations must use this model. Scoring is evidence for human Gate 1 review — not approval. Human approval is required to pass Gate 1.

---

## Purpose

The scoring model provides a consistent, documented, format-neutral basis for evaluating format candidates. It ensures that acceptance decisions are traceable, reproducible, and free of prior bias. The score is evidence presented to the human reviewer — it does not approve Gate 1 by itself.

**Critical rule:** A score in the "accept" band does NOT pass Gate 1. The human reviewer reads the scoring evidence and records approval in `registry/format-registry.yaml`. Until the human sets `gate_1.status: passed`, `approved_by`, and `approved_date`, Gate 1 is not passed.

---

## Seven Scoring Factors

Seven factors are scored. The total is out of 100 points.

### Factor 1: Legal Safety (Weight: 30 points)

How legally safe is it to implement a parser or converter for this format?

| Score | Points | Criterion |
|---|---|---|
| 3 | 30 | Legal Category 1: Open standard, royalty-free (e.g., OASIS RF, W3C RF, ISO open standard) |
| 2 | 20 | Legal Category 2: Permissive OSS implementation (MIT/Apache reference parser, some spec-drift risk) |
| 1 | 10 | Legal Category 3: Published proprietary spec with documented parser permission from rights holder |
| 0 | 0 | Legal Category 4: Ambiguous documentation; no clear permission; implementation at legal risk |

**Automatic reject rules (apply regardless of total score):**
- Score 0 on legal safety (Category 4 score of 0): automatic reject. No further scoring required.
- Legal Category 5 (reverse-engineered binary, no public spec, no permission): automatic reject.
- Legal Category 6 (blocked — legally prohibited): automatic reject.
- Any evidence of DRM circumvention, access-control bypass, or legally prohibited parser work: automatic reject.
- Missing legal category: cannot pass Gate 1. Classify before scoring.

---

### Factor 2: Specification Availability (Weight: 20 points)

How complete, accessible, and reliable is the format specification?

| Score | Points | Criterion |
|---|---|---|
| 3 | 20 | Comprehensive official spec; covers all data structures, encoding, constraints; regularly maintained; publicly accessible |
| 2 | 13 | Official spec exists but has gaps, ambiguities, or is not regularly maintained; publicly accessible |
| 1 | 7 | Informal or community spec; significant gaps; must rely partly on reference implementation |
| 0 | 0 | No spec; format must be inferred entirely from files or reference implementations |

---

### Factor 3: Parseable Structure (Weight: 15 points)

How structurally straightforward is the format to parse correctly?

| Score | Points | Criterion |
|---|---|---|
| 3 | 15 | Simple, well-structured; single-file; parseable with standard library tools (e.g., flat XML, plain JSON, standard CSV) |
| 2 | 10 | Moderate complexity; container-based (ZIP/OPC) with clear internal structure; documented edge cases |
| 1 | 5 | High complexity; multiple interdependent parts; binary blocks; non-trivial parser required |
| 0 | 0 | Extreme complexity; multiple compression layers, encryption, undocumented binary structures, or schema-level variability |

---

### Factor 4: Community or Customer Demand (Weight: 15 points)

How strong is the demand for support for this format from users, customers, or the developer ecosystem?

| Score | Points | Criterion |
|---|---|---|
| 3 | 15 | High demand; multiple major software products generate or consume it; active community or enterprise users |
| 2 | 10 | Moderate demand; established niche or segment; used by significant subset of target customers |
| 1 | 5 | Declining or low demand; specialized contexts; limited customer need |
| 0 | 0 | Negligible demand; rarely encountered in practice; no identified customer need |

---

### Factor 5: Strategic Track Value (Weight: 10 points)

Does this format align with the project's product track and format family strategy?

| Score | Points | Criterion |
|---|---|---|
| 3 | 10 | Core format in a target family (Cells, Words, Slides, Imaging, Diagram, Archive); first or second acquisition; expands the product catalog meaningfully |
| 2 | 7 | Adjacent format; adds coverage to an established family; complements existing or planned formats |
| 1 | 3 | Peripheral format; covers an edge case; limited incremental value |
| 0 | 0 | No strategic fit; outside all target families; or redundant with an already-acquired format at the same tier |

---

### Factor 6: Implementation Complexity (Weight: 5 points)

How much implementation effort is required to build a correct, production-quality parser?

| Score | Points | Criterion |
|---|---|---|
| 3 | 5 | Low complexity; straightforward parser; can reuse existing libraries or patterns from prior formats |
| 2 | 3 | Moderate complexity; some novel work required; implementation is bounded and well-defined |
| 1 | 2 | High complexity; significant novel work; multiple edge cases; requires specialized parser skills |
| 0 | 0 | Extreme complexity; may require research-level effort; high risk of correctness issues |

---

### Factor 7: Family Overlap or Redundancy (Weight: 5 points)

Does acquiring this format avoid duplication with formats already in the system?

| Score | Points | Criterion |
|---|---|---|
| 3 | 5 | No overlap; fills a gap in the format family; distinct format with unique characteristics |
| 2 | 3 | Minor overlap; variant of an existing format but with meaningful differences (e.g., flat vs. archive container) |
| 1 | 2 | Moderate overlap; largely similar to an existing format; differentiation requires justification |
| 0 | 0 | Redundant; another format in the system already covers the same use cases at the same tier |

---

## Weighted Scoring

```
Maximum score = 100 points

Factor weights:
  Legal Safety:             score 0-3 → 0 / 10 / 20 / 30 points
  Spec Availability:        score 0-3 → 0 / 7  / 13 / 20 points
  Parseable Structure:      score 0-3 → 0 / 5  / 10 / 15 points
  Community Demand:         score 0-3 → 0 / 5  / 10 / 15 points
  Strategic Track Value:    score 0-3 → 0 / 3  / 7  / 10 points
  Implementation Complexity:score 0-3 → 0 / 2  / 3  /  5 points
  Family Overlap:           score 0-3 → 0 / 2  / 3  /  5 points
                                                         ---
  Maximum total:                                         100 points
```

---

## Acceptance Bands

| Band | Score Range | Action |
|---|---|---|
| Accept | 70–100 | Submit for human Gate 1 approval. Set `gate_1.status: scored_pending_human_approval`. |
| Review or Defer | 50–69 | Project lead review required. May accept with documented rationale, or defer. Set `scored_pending_human_approval`. |
| Defer | 30–49 | Defer to later phase. Record rationale. Set `scored_pending_human_approval` with defer recommendation. |
| Reject | 0–29 | Reject. Set `gate_1.status: rejected`. Record reason in registry. |

**The accept band is not gate approval.** A score of 70–100 means the candidate is recommended for human review. The human reads the scoring sheet and decides. No score band approves Gate 1 automatically.

---

## Automatic Reject Rules

Check these FIRST, before computing the total score. Any of these conditions results in immediate rejection.

| Rule | Trigger | Action |
|---|---|---|
| AR-1 | Legal Category 5 (reverse-engineered binary with no permission) | Reject. Do not compute total. Set `gate_1.status: rejected`. |
| AR-2 | Legal Category 6 (blocked) | Reject. Do not compute total. Set `gate_1.status: rejected`. |
| AR-3 | Legal safety score = 0 (any legal category) | Reject. Automatic, regardless of total. |
| AR-4 | Evidence of DRM circumvention, access-control bypass, or legally prohibited parser work | Reject immediately. Log as blocked. |
| AR-5 | Legal category not classified | Cannot be scored. Do not submit for Gate 1. Classify first. |

---

## Scoring Sheet Format

When scoring a format, record the following:

```yaml
scoring:
  scorer: <name or agent-id>
  scored_date: <ISO-8601>
  model_version: "7-factor-100pt-v1"
  automatic_reject_check:
    legal_category_classified: true
    category_5_or_6: false
    drm_bypass_evidence: false
    legal_safety_score_zero: false
    result: no_automatic_reject
  dimensions:
    legal_safety:
      score: 0-3
      points: 0/10/20/30
      legal_category: 1-4
      rationale: "<brief text>"
    spec_availability:
      score: 0-3
      points: 0/7/13/20
      rationale: "<brief text>"
    parseable_structure:
      score: 0-3
      points: 0/5/10/15
      rationale: "<brief text>"
    community_demand:
      score: 0-3
      points: 0/5/10/15
      rationale: "<brief text>"
    strategic_track_value:
      score: 0-3
      points: 0/3/7/10
      rationale: "<brief text>"
    implementation_complexity:
      score: 0-3
      points: 0/2/3/5
      rationale: "<brief text>"
    family_overlap:
      score: 0-3
      points: 0/2/3/5
      rationale: "<brief text>"
  total_points: <0-100>
  band: accept | review-defer | defer | reject
  recommendation: "<text — recommendation to human reviewer>"
  gate_1_status_set_by_agent: scored_pending_human_approval
  approved_by: null
  approved_date: null
```

---

## Registry Status Lifecycle

```
not_started
  → scored_pending_human_approval  (agent produced scoring evidence; awaiting human review)
    → passed                       (human approved; approved_by and approved_date set by human)
    → rejected                     (human declined after review)
  → rejected                       (automatic reject triggered; agent records reason)
```

**Agent rule:** Agents may set `not_started → scored_pending_human_approval` or `not_started → rejected` (automatic reject only). Agents may NEVER set `→ passed`. Only humans set `passed`.

---

## Relationship to Other Documents

- `docs/gates.md` — Gate 1 pass criteria and authorization rules
- `docs/governance/legal-and-licensing.md` — legal category definitions and fast-path rules
- `registry/format-registry.yaml` — where scoring results are recorded
- `acquisition-packs/_template/pack.yaml` — where detailed scoring sheets are stored (Phase 2+)
- `docs/python-foss/acquisition-workflow.md` — Stage 1 scoring workflow steps
