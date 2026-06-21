# Skill Inventory and Gaps — Format Factory Machinery Audit v2
# Sprint ID: ff-machinery-readiness-audit-v2-20260621-827f5a52

## Skill Command Inventory

29 slash commands in .claude/commands/:
_readme.md, add-analytics-function.md, add-dogfood-export.md, add-dotnet-api.md,
add-dotnet-object-model-feature.md, add-installed-package-example.md,
add-python-api.md, add-python-object-model-feature.md, add-roundtrip-test.md,
add-same-format-writer-feature.md, autonomous-loop.md, build-context-pack.md,
build-evidence-bundle.md, check-gate.md, check-release-boundary.md,
check-skill-coverage.md, create-acquisition-pack.md, create-taskcard.md,
evidence-review-next-prompt.md, execution-handoff.md, export-plan-context.md,
generate-execution-handoff.md, materialize-declaration-review.md, memory-sprint.md,
package-install-proof.md, plan-hardening.md, post-sprint-audit.md,
post-sprint-loop.md, promote-gap-to-taskcard.md, record-lane-execution.md,
reproduce-master-plan.md, **sal-pipeline-heal.md** (NEW — untracked),
score-format.md, select-poc-gap.md, spec-literal-qname-to-code-mapping.md,
spec-parity-source-regeneration-and-migration.md, spec-parity-verification.md,
spec-shaped-product-architecture-blueprint.md, sync-memory.md,
update-capability-matrix.md, validate-product-code-ledger.md,
validate-skill-transcript.md, verify-dogfood-path.md, python-reduced-spec-parity-model.md

## Product-Generating Skills

| Skill | File | Generates/Modifies | QName Enforced | SAL Used |
|-------|------|-------------------|---------------|---------|
| add-python-api | add-python-api.md | src/python/{format}/ | NO | NO |
| add-python-object-model-feature | add-python-object-model-feature.md | src/python/{format}/ | NO | NO |
| add-dotnet-api | add-dotnet-api.md | src/net/{format}/ | NO | NO |
| add-dotnet-object-model-feature | add-dotnet-object-model-feature.md | src/net/{format}/ | NO | NO |
| add-same-format-writer-feature | add-same-format-writer-feature.md | src/{lang}/{format}/ | UNKNOWN | UNKNOWN |
| add-roundtrip-test | add-roundtrip-test.md | tests/ | NO | NO |
| add-analytics-function | add-analytics-function.md | {format}_analytics.py | NO (SUSPENDED) | NO |
| add-dogfood-export | add-dogfood-export.md | dogfood examples | NO | NO |

### Key Skill Gaps

1. **No QName enforcement in product skills** — add-python-api, add-dotnet-api, and
   add-python-object-model-feature do not require spec_qname on created classes.
   A skill run can produce format-prefixed names without any validator blocking it.

2. **No SAL lookup in product skills** — skills do not query SAL facts to determine
   what classes/functions to create. Product deepening targets come from the gap ledger
   or the _EXPANSION_GOALS list (hardcoded).

3. **add-analytics-function suspended** — V42 validator blocks analytics.py additions
   without spec backing. Rotation suspended per keen-dancing-hopper plan.

4. **sal-pipeline-heal.md** — NEW untracked command. Purpose: trigger SAL pipeline repair.
   This is in the right direction but untracked.

5. **spec-parity-source-regeneration-and-migration** — skill exists but complex;
   requires governance authorization before execution.

6. **spec-literal-qname-to-code-mapping** — skill exists; maps spec qnames to code targets.
   Whether it is actually used in product deepening: UNKNOWN without runtime trace.

7. **validate-skill-transcript** — V46 governance validator added (commit 827f5a52);
   validates that skill execution transcripts exist for claimed skill runs.

## Skill Registry State (.supervisor/skill-registry.yaml)

Registered skills include product skills and infrastructure skills.
V41 (validate_analytics_skill_required) requires analytics.py changes to attribute a skill.
V46 (validate_skill_transcript) now validates skill transcript files.

## Skill Repeatability Assessment

| Property | Status |
|----------|--------|
| Skills are prompt-based | YES — text prompts, not deterministic programs |
| Skills enforce QName | NO |
| Skills use SAL | NO |
| Skills produce governed evidence | YES (via declaration + supervisor) |
| Skills are deterministic | NO — LLM-based, output varies |
| Skills are testable | PARTIALLY (transcript validation by V46) |
| Skills can generate malformed code | YES — no qname guard in skill prompts |

## Prior Audit Skill Finding vs. Current

Prior audit: "Core product skills (add-dotnet-api, add-python-api) are ready and governed.
QName skills cannot execute (generator tool missing)."

Current state:
- `qname_ontology_generator.py` EXISTS (in tools/supervisor/)
- `qname_structure_validator.py` EXISTS and functional
- Product skills remain without QName enforcement in their prompts
- No skill generates canonical classes from the spec/ hierarchy
- The gap between "skill exists" and "skill produces spec-aligned code" is NOT closed

## Key Skill Gap: No QName-Enforced Product Generation

The biggest skill gap is that no skill guarantees:
  "The code I generate will have spec_qname attributes and be organized under
   spec/{namespace}/{element}.py hierarchy"

Until this is wired into skill prompts and validated by the governance layer,
every product deepening sprint can introduce non-qname code.
