# Skill Inventory and Gaps

**Sprint:** forensics-archaeology-20260621

---

## Registered Skills (`.claude/commands/`)

40+ skills registered. Categorized by purpose:

### Product Generation Skills
| Skill | File | Purpose |
|-------|------|---------|
| add-python-api | add-python-api.md | Add new Python API function to a format package |
| add-python-object-model-feature | add-python-object-model-feature.md | Add object model class |
| add-dotnet-api | add-dotnet-api.md | Add new .NET API method |
| add-dotnet-object-model-feature | add-dotnet-object-model-feature.md | Add .NET object model feature |
| add-same-format-writer-feature | add-same-format-writer-feature.md | Add write-back capability |
| add-roundtrip-test | add-roundtrip-test.md | Add load-edit-save-reload test |
| add-analytics-function | add-analytics-function.md | Add analytics function (SUSPENDED) |
| add-installed-package-example | add-installed-package-example.md | Add dogfood example |
| add-dogfood-export | add-dogfood-export.md | Add dogfood export scenario |

### Spec-Parity Skills
| Skill | File | Purpose |
|-------|------|---------|
| spec-parity-verification | spec-parity-verification.md | Verify spec parity |
| spec-parity-source-regeneration-and-migration | spec-parity-source-regeneration-and-migration.md | Regenerate from spec |
| spec-literal-qname-to-code-mapping | spec-literal-qname-to-code-mapping.md | Map QNames to code |
| spec-shaped-product-architecture-blueprint | spec-shaped-product-architecture-blueprint.md | Generate architecture |
| python-reduced-spec-parity-model | python-reduced-spec-parity-model.md | Python spec parity |
| sal-pipeline-heal | sal-pipeline-heal.md | Heal SAL pipeline (NEW — untracked) |

### Validation and Auditing Skills
| Skill | File | Purpose |
|-------|------|---------|
| validate-product-code-ledger | validate-product-code-ledger.md | Validate code ledger |
| validate-skill-transcript | validate-skill-transcript.md | Validate skill execution |
| check-skill-coverage | check-skill-coverage.md | Check skill coverage |
| spec-parity-verification | spec-parity-verification.md | Spec parity check |
| post-sprint-audit | post-sprint-audit.md | Sprint audit |
| plan-hardening | plan-hardening.md | Plan hardening after audit |

### Gate / Release Skills
| Skill | File | Purpose |
|-------|------|---------|
| check-gate | check-gate.md | Check gate readiness |
| check-release-boundary | check-release-boundary.md | Check release boundary |
| score-format | score-format.md | Score format for acquisition |
| create-acquisition-pack | create-acquisition-pack.md | Create acquisition pack |
| package-install-proof | package-install-proof.md | Prove package install |

### Lifecycle / Orchestration Skills
| Skill | File | Purpose |
|-------|------|---------|
| autonomous-loop | autonomous-loop.md | Run autonomous sprint loop |
| post-sprint-loop | post-sprint-loop.md | Post-sprint continuation |
| execution-handoff | execution-handoff.md | Hand off to next agent |
| generate-execution-handoff | generate-execution-handoff.md | Generate handoff doc |
| memory-sprint | memory-sprint.md | Memory maintenance sprint |
| sync-memory | sync-memory.md | Sync memory files |
| build-context-pack | build-context-pack.md | Build context pack |
| build-evidence-bundle | build-evidence-bundle.md | Build evidence bundle |
| record-lane-execution | record-lane-execution.md | Record lane execution |
| select-poc-gap | select-poc-gap.md | Select next POC gap |
| export-plan-context | export-plan-context.md | Export plan context |

### Planning Skills
| Skill | File | Purpose |
|-------|------|---------|
| create-taskcard | create-taskcard.md | Create governed taskcard |
| reproduce-master-plan | reproduce-master-plan.md | Reproduce master plan |
| promote-gap-to-taskcard | promote-gap-to-taskcard.md | Gap → taskcard |
| materialize-declaration-review | materialize-declaration-review.md | Review materialization |
| evidence-review-next-prompt | evidence-review-next-prompt.md | Next prompt from review |
| update-capability-matrix | update-capability-matrix.md | Update capability matrix |

---

## Skill Gap Analysis

### Critical Missing Skills

| Gap | Impact |
|----|--------|
| No skill enforces `spec_qname` on product code | Generated product classes may lack spec_qname |
| No skill links `FACT-FORMAT-NNN` to generated code | Spec fact → code traceability absent |
| No skill creates qname-registry YAML files | Registry stays unwritten |
| No skill creates non-XML format canonical names | DIF, SYLK, CSV have no canonical naming |
| No skill audits existing code for spec_qname gaps | Backfill has no automated driver |
| No skill validates Compat/ completeness | Missing facades go undetected |
| No skill creates .NET spec stub files | .NET Spec/ not systematically populated |

### Skills With Enforcement Problems

| Skill | Problem |
|-------|---------|
| `add-python-object-model-feature` | Does not mandate `spec_qname` in generated class |
| `add-dotnet-object-model-feature` | Does not mandate .NET spec reference |
| `add-analytics-function` | SUSPENDED — deepening_suspension_validator blocks it (V42) |
| `add-python-api` | No spec_qname requirement in prompt |

### Skills That Are Well-Designed

| Skill | Strength |
|-------|---------|
| `spec-literal-qname-to-code-mapping` | Directly maps spec QNames to code patterns |
| `spec-parity-verification` | Checks spec parity explicitly |
| `check-gate` | Verified working (FODS gate 11 check returned 6/7) |
| `sal-pipeline-heal` | New — targets SAL pipeline directly |
| `validate-skill-transcript` | V46 validator was recently added (commit 827f5a52) |

---

## Verdict

Skills exist but do not uniformly enforce spec_qname requirements on generated code. The most
critical gap is in `add-python-object-model-feature` and `add-dotnet-object-model-feature` —
these are the primary product deepening skills, yet they do not require spec_qname in generated
output.

**Required:** Add spec_qname requirement to all product-generating skill prompts. Create
a qname-registry skill. Create a non-XML canonical naming skill for binary/text formats.
