# Existing System Migration Model

Sprint ID: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-PRODUCTION-BLOCKER-HEALING-001
Owner: Lane D

## Input Sources (13)

1. **product-capability-matrix/poc-targets.yaml** — Current dashboard status per POC target; imported as candidate PocTargetField nodes (read-only; status is a starting candidate, not authority)
2. **registry/format-registry.yaml** — Format definitions, gate status, technical parameters; imported as context for ProductRequirement candidate generation
3. **reports/mainstream-poc-train/** — Mainstream sprint reports; extracted for candidate CapabilityClaim and ImplementationArtifact references
4. **reports/supervisor/** — Supervisor reports (evidence-review.json, latest-review.md, etc.); extracted for candidate CoverageRecord states and known gap references
5. **reports/r*/** (all sprint report directories) — Historical sprint evidence declarations; used to identify candidate TestArtifact and DogfoodArtifact references
6. **skills reports and transcripts** — Skills handoff transcripts; extracted for candidate StreamHandoff nodes
7. **acceleration reports** — Acceleration ai_draft outputs; imported as ai_draft=true advisory nodes (never proof nodes)
8. **.local/supervisor/reviews/** — Supervisor review ZIPs; extracted EvidencePackage candidates with materialized=true/false status
9. **tests/** (tests/net, tests/python) — Test files; imported as TestArtifact candidate nodes with file paths and test IDs
10. **examples/** — Example files; imported as ExampleArtifact candidate nodes
11. **dogfood outputs** (examples/, .local/dogfood/ if present) — Format output files; imported as DogfoodArtifact candidate nodes with file paths; checksum computed on import
12. **source-change ledgers** (reports/*/product-code-change-ledger.json) — Source file change logs; used to identify ImplementationArtifact nodes and detect staleness triggers
13. **evidence declarations** (.local/evidences/**) and **evidence manifests** — Existing declarations; imported to identify EvidencePackage candidates and materialized status

## Importer Output Types (9)

1. **candidate ProductRequirements** — From format-registry.yaml and poc-targets.yaml capability descriptions; status=candidate until RequirementProof is established
2. **candidate CapabilityClaims** — From sprint reports, poc-targets status fields, and mainstream reports; status=candidate until graph-linked
3. **EvidenceArtifact records** — EvidencePackage nodes from .local/supervisor/reviews/; materialized=true if zip_path resolves and checksum matches
4. **TestArtifact records** — TestArtifact nodes from tests/; last_passed_at=null until test run linkage is established
5. **DogfoodArtifact records** — DogfoodArtifact nodes from examples/ and dogfood outputs; checksum computed; produced_at from file mtime
6. **UnsupportedFeature candidates** — From sprint reports and known gap documentation; severity field populated from gap description
7. **Staleness candidates** — From source-change ledger comparison; StalenessEvent nodes created where implementation mtime > test last_passed_at
8. **Gap candidates** — From supervisor reports and poc-targets blocked entries; fed to MainstreamGapQueueGenerator after graph validation
9. **ImportConflicts** — Records of import conflicts: duplicate claim IDs, contradictory status values from different sources, unresolvable artifact paths

## 5 Import Rules

**Rule 1:** poc-targets.yaml status is not authority — Status fields in poc-targets.yaml are imported as candidate PocTargetField nodes only. A PASS status in poc-targets does not make a CapabilityClaim accepted_for_poc. The claim must pass through the full CapabilityDelta flow and CapabilityCoverageEvaluator.

**Rule 2:** Imported reports are candidates not truth — Sprint reports, supervisor reviews, and maintenance records are imported as candidate graph records. Their content is suggestions for node creation; the CapabilityCoverageEvaluator is the authority, not the reports.

**Rule 3:** Imported tests must link to a claim to count — A TestArtifact imported from tests/ does not satisfy TestProof until a tested_by edge is created linking it to a specific CapabilityClaim. Test file existence alone is insufficient.

**Rule 4:** Imported dogfood artifacts need path + checksum + validation record — A DogfoodArtifact imported from examples/ is only usable for DogfoodProof if: (a) the file path resolves in the repo, (b) a checksum is computed and stored, (c) a validator_used field is populated (even if the validator is "manual format inspection").

**Rule 5:** Evidence packages must materialize files or be marked declared_not_verified — An EvidencePackage from .local/supervisor/reviews/ is marked materialized=true only if the zip_path exists and the manifest entries can be verified by checksum. If the zip exists but manifest entries are unverifiable, the package is marked declared_not_verified and cannot satisfy EvidencePackageProof.

## Migration Phases (6)

**Phase 0 — Read-Only Inventory:**
Read all 13 input sources. Build an inventory of: existing files in tests/, examples/, src/, reports/; zip archives in .local/supervisor/reviews/; YAML/JSON in poc-targets and registry. Record file paths and mtimes. No graph nodes written. No authority mutations.

**Phase 1 — Candidate Graph Construction:**
For each file, report, and artifact identified in Phase 0: create candidate nodes (ProductRequirement, CapabilityClaim, TestArtifact, DogfoodArtifact, ExampleArtifact, EvidencePackage, UnsupportedFeature, CapabilityDelta). Write to capability-graph-nodes.jsonl as candidate entries. Create provisional edges where source-target relationships are clear (e.g., test file in tests/net/fods/ → candidate tested_by edge to candidate fods claim).

**Phase 2 — Validator Pass:**
Run schema validator on all candidate nodes. Reject nodes with missing required fields or invalid field values. Flag ImportConflicts (duplicate node IDs, contradictory status from different sources). Produce: candidate-graph-validation-report.json with PASS/FAIL per node.

**Phase 3 — Rejected/Blocked/Accepted Classification:**
For each candidate node: if all required fields present and no conflicts → mark import_status=imported_candidate. If conflict or missing field → mark import_status=import_conflict (must be resolved before coverage evaluation). ai_draft nodes → mark ai_draft=true; they exist in graph but are excluded from proof evaluation.

**Phase 4 — Gap Queue Generation (candidate):**
Feed validated candidate nodes to MainstreamGapQueueGenerator (Step 1–11 of gap queue algorithm). The generator identifies which candidate CapabilityClaims are missing required proof types. Produces: candidate-mainstream-gap-queue.json. This is advisory for the first MWP sprint; it becomes authoritative after Phase 5.

**Phase 5 — Supervisor Verdict Packet:**
Compile the first SupervisorVerdictPacket from the candidate graph state. Fields: claims_checked (count of candidate claims), coverage_records (all BLOCKED), stale_claims (all from Phase 0 staleness candidates), poc_readiness_verdict (computed from candidate graph — expected mostly COVERAGE_NEEDED for first run). Supervisor reviews packet and authorizes MWP execution sprint.
