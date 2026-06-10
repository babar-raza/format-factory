# Preserve / Redesign Decision Matrix

Sprint ID: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-PRODUCTION-BLOCKER-HEALING-001
Owner: Lane A

## Decision Table

| Item | Decision | Reason | Production Consequence | Required Action |
|------|----------|--------|----------------------|----------------|
| poc-targets.yaml as dashboard | Preserve | Single view of POC target status visible to all agents | Incorrect if used as authority | Read-only for queries; write only via proposed sync delta |
| registry/format-registry.yaml | Preserve | Canonical format context; gates and metadata | If mutated directly, authority is contaminated | Read-only; never mutated by authority layer |
| Existing tests (tests/net, tests/python) | Preserve | Product coverage is real; must be linked to claims | Tests pass but do not prove capability until graph-linked | Import as TestArtifact candidates; link to claims |
| Existing examples (examples/) | Preserve | Examples prove usage patterns | Examples alone insufficient for coverage_validated | Import as ExampleArtifact candidates; link to claims |
| Dogfood outputs (.local/dogfood, examples/) | Preserve | Real end-to-end format output proofs | Dogfood present does not mean claim linked | Import as DogfoodArtifact candidates; validate checksums |
| Supervisor review packages (.local/supervisor/reviews/) | Preserve | Structured artifact bundles with checksums | Evidence proves files, not capability truth | Use as EvidencePackage inputs; do not treat as claim proof |
| Mainstream dashboard and sprint model | Preserve | Gap selection consumer exists and is functional | Picks wrong gaps without computed queue | Replace ad-hoc selection with MainstreamGapQueueGenerator output |
| Skills handoff and transcript model | Preserve | Governance layer for governed execution | Handoffs miss claim IDs | Add required_claim_ids field to handoff template |
| Acceleration ai_draft packet format | Preserve | Useful for surfacing candidates and recommendations | ai_draft is not proof | Retain format; explicitly label all outputs as advisory, never proof |
| Specification Authority outputs | Preserve | Accepted spec requirements and empirical evidence | Context pack informs; does not prove capability alone | Import as SpecRequirementRef and EmpiricalEvidence candidates |
| build_declaration_review_package.py | Preserve | ZIP builder for evidence bundles | Package build ≠ capability proof | Retain as artifact integrity tool; evidence graph import is separate |
| Supervisor toolchain (tools/supervisor/) | Preserve | Pipeline infrastructure for grading and review | Grading is on declaration, not graph state | Extend to consume supervisor-verdict-packet.json |
| build_context_pack.py | Preserve | Context pack builder for cross-sprint reference | Context pack is informational | Retain; add graph_hash field to context pack outputs |
| Canonical proof graph (new) | Redesign/build | No current implementation | Without it, no deterministic readiness | Build: JSONL nodes + JSONL edges, recomputable |
| ProductRequirementRegistry (new) | Redesign/build | No registry with enforced lifecycle | Claims float without requirement anchors | Build: candidate → accepted/stale/rejected state machine |
| CapabilityClaimRegistry (new) | Redesign/build | Claims scattered, no lifecycle | PASS without uniform proof chain | Build: claim-scope dimensions + proof sufficiency enforcer |
| UnsupportedFeatureLedger (new) | Redesign/build | No ledger of declared limitations | Limitations invisible downstream | Build: per-claim UnsupportedFeature records |
| CapabilityDeltaSystem (new) | Redesign/build | Mainstream writes directly to poc-targets | Direct mutation bypasses authority | Build: delta proposal → schema validation → evidence import → accepted/rejected |
| CapabilityCoverageEvaluator (new) | Redesign/build | No binary evaluator | Any ad-hoc report can claim PASS | Build: binary PASS/FAIL per invariant from graph |
| OverclaimDetector (new) | Redesign/build | No detection + decomposition | Valid partial evidence wasted on rejection | Build: detects + decomposes; split/narrow rather than reject |
| StalenessInvalidationEngine (new) | Redesign/build | Staleness not propagated | Stale requirements silently support live claims | Build: propagation chain from source requirement through graph |
| PocReadinessComputer (new) | Redesign/build | No per-target readiness computation | Supervisor infers from prose | Build: computes verdict per POC target from graph state |
| MainstreamGapQueueGenerator (new) | Redesign/build | No deterministic gap queue | Same state yields different gaps | Build: 11-step algorithm, ranked output, deterministic |
| SupervisorVerdictPacketGenerator (new) | Redesign/build | No normalized machine-readable Supervisor input | Supervisor infers from heterogeneous reports | Build: 16-field JSON packet |
| PocTargetsSyncProposalGenerator (new) | Redesign/build | poc-targets.yaml mutated directly | Authority contamination | Build: proposes delta; never directly mutates |
| EvidenceGraphImporter (new) | Redesign/build | Evidence packages not graph-linked | Evidence proves files not capability | Build: imports package artifacts as graph nodes with claim links |
| GoldenReplaySuite (new) | Redesign/build | No determinism test | System cannot prove same result on same input | Build: 25 categories, 6 fixture packs, hash comparison |
| Direct PASS from prose | Remove/avoid | Prose contains unverifiable natural language claims | False PASS risk on every rerun | Reject all prose-sourced PASS verdicts in evaluator |
| Direct PASS from file existence | Remove/avoid | File existence does not prove capability truth | False PASS silently accepted | Require graph-linked artifacts for PASS |
| ai_draft as proof | Remove/avoid | AI-generated content is not authoritative | ai_draft can influence readiness verdict | Explicitly reject ai_draft node type as satisfying any proof class |
| Hidden unsupported features | Remove/avoid | Limitations invisible downstream cause overclaims | Consumers build on false capability | Require UnsupportedFeature records for accepted_with_limitations |
| Stale proof supporting readiness | Remove/avoid | Old evidence supports live claims silently | False PASS across sprint boundaries | StalenessInvalidationEngine demotes stale-backed claims |
| Hardcoded output file counts | Remove/avoid | Counts drift as files are added/removed | Script failures across sprint boundaries | Derive all counts dynamically from actual file lists |
| Evidence metadata polishing as sprint goal | Remove/avoid | Cosmetic repair is not product progress | Sprint burndown inflated with non-progress | Evidence repair is only a sprint goal when it affects proof validity |
| Direct poc-targets mutation from Mainstream | Remove/avoid | Bypasses authority layer | poc-targets status becomes untraceable | All updates go through PocTargetsSyncProposalGenerator |
| Empirical evidence as spec-backed without caveat | Defer | Acceptable short-term with explicit caveat | Misleads spec compliance claims | Mark empirical_only with caveat in ProductRequirementRegistry |
| Gnumeric without required capability validation | Defer | Stretch target; counts only if proven faster | Premature inclusion inflates POC scope | Include only if coverage-validated first |
