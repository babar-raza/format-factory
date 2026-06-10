# Capability Status Taxonomy
# Sprint: FORMAT-FACTORY-CAPABILITY-FEATURE-UNDERSTANDING-LAYER-INVESTIGATIVE-HEALING-001

## Overview

Every capability record in the capability map must have a `current_state` from this taxonomy.
States are ordered from least to most evidence. No state may skip levels to claim readiness.

## State Definitions (ordered by evidence level)

| State | Verified? | Required Evidence | Notes |
|-------|-----------|-------------------|-------|
| `missing` | NO | None | No implementation, no plan |
| `planned` | NO | Taskcard reference | Taskcard exists, not started |
| `ai_draft` | NO | None (AI is not authority) | AI/LLM produced it — never verified |
| `human_goal` | NO | plans/master-plan.md ref | Product goal stated by human |
| `inferred_unverified` | NO | Pattern observation | Inferred from code patterns, not confirmed |
| `spec_verified` | YES | Spec fact ref | Backed by confirmed spec fact |
| `requirement_verified` | YES | Requirement ref | Backed by extracted requirement |
| `capability_verified` | YES | Capability claim record | Capability claim independently validated |
| `implementation_partial` | NO | Source file ref (partial) | Implementation started but incomplete |
| `implementation_verified` | YES | Source file path + function | Complete implementation confirmed |
| `test_verified` | YES | Test file + passing log | Tests exist AND pass |
| `example_verified` | YES | Example file or sample output | Example/sample output exists |
| `package_verified` | YES | Package artifact + install log | Package built and installed successfully |
| `dogfood_verified` | YES | Dogfood output file | Output generated using another FF library |
| `blocked` | NO | Blocker description | Cannot progress due to constraint |
| `unsupported` | NO | Policy decision | Explicitly not in product scope |
| `out_of_scope` | NO | Product profile | Not part of this product profile |
| `future` | NO | Deferred intent | Deferred to future sprint |

## Enforcement Rules

1. `ai_draft` CANNOT count as verified even if combined with other states.
2. `human_goal` CANNOT count as verified.
3. `inferred_unverified` CANNOT count as verified.
4. `implementation_verified` REQUIRES at least one `source_refs` entry with an existing file path.
5. `test_verified` REQUIRES at least one `test_refs` entry AND a passing test log reference in `evidence_refs`.
6. `package_verified` REQUIRES a package artifact path in `package_refs`.
7. `dogfood_verified` REQUIRES a generated output file path in `dogfood_refs`.
8. Commercial capabilities and FOSS/reduced capabilities MUST appear in separate maps — never in a single record with ambiguous `product_type`.
9. A capability claiming `spec_verified` MUST have a `spec_refs` entry pointing to a specific spec fact ID or fact file.

## Promotion Path Examples

```
missing
  → planned (taskcard created)
  → implementation_partial (some code written)
  → implementation_verified (full code, confirmed by agent)
  → test_verified (tests pass with evidence)
  → example_verified (sample output exists)
  → package_verified (package built and installed)
  → dogfood_verified (output generated via FF library)
```

Or:

```
human_goal
  → spec_verified (spec fact found and confirmed)
  → requirement_verified (requirement extracted)
  → capability_verified (capability claim validated)
  → implementation_verified ...
```

## Anti-patterns (never allowed)

- Claiming `test_verified` without a test file reference
- Claiming `spec_verified` without a spec_refs entry
- Promoting `ai_draft` directly to any verified state
- Using `implementation_verified` + `product_type: commercial|foss_reduced` in same record
  (they must be separate records per product type)
