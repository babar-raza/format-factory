# Tradeoffs, Risks, and Limits

Sprint ID: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-PRODUCTION-BLOCKER-HEALING-001
Owner: Lane E

## Tradeoffs and Risks

- Strict proof requirements may slow final readiness declarations, but this must not block implementation attempts. The authority layer should gate accepted_for_poc, not initial development. Mainstream continues building while proof graph is populated incrementally.

- The Specification Authority may initially be incomplete. Not every ODF or Netpbm spec section will have a SpecRequirementRef node in the first MWP sprint. Empirical evidence (actual file samples) is a legitimate and necessary substitute, provided it is marked empirical_only with a visible caveat.

- Empirical evidence is necessary for legacy and real-world formats. Many formats (SYLK, DIF, historical PPM) have ambiguous or sparse formal specs. Requiring formal-spec-only requirements would block valid commercial capabilities. The system must allow empirical_only with caveats.

- Evidence packages may initially be declared-only (materialized=false) when the build toolchain is not fully set up. These must be clearly flagged as declared_not_verified and must not count as EvidencePackageProof until materialized.

- Tests may not prove capability if not linked in the graph. A large existing test suite (e.g., 536 .NET tests) does not automatically provide TestProof for specific claims. Linking tests to claims via tested_by edges is a required migration step, not optional cleanup.

- Dogfood validation needs format-specific validators. The system requires validator_used on every DogfoodArtifact. For some formats, the only available validator is "manual format inspection" or "re-parsed and compared". This is acceptable with explicit documentation.

- Overclaim detection may produce false positives early in the migration. The candidate graph built from existing reports will have broad, underspecified claims. The decomposition model must handle gracefully: narrow and split rather than reject wholesale.

- Graph migration from existing reports may be imperfect. Sprint reports use inconsistent terminology and field names. The EvidenceGraphImporter must be tolerant of import conflicts and flag them as ImportConflict records for human review, not fail silently.

- poc-targets.yaml remains a dashboard, not a proof system. Even after the authority layer is operational, poc-targets.yaml is updated only via proposed sync deltas. It is a human-facing view, not the source of truth for capability state.

- accepted_with_limitations must be visible downstream. All consumers (Mainstream gap queue, Supervisor verdict packet, Skills handoffs) must receive UnsupportedFeature records for any accepted_with_limitations claim. Downstream tools must not treat accepted_with_limitations as equivalent to accepted_for_poc.

- Graph maintenance has overhead. The proof graph must be maintained as source files, tests, and dogfood outputs change. Staleness propagation is automated, but the EvidenceGraphImporter must be run after every sprint that modifies implementation files. This is a runtime cost that must be accepted.

- Initial MWP covers POC targets only, not all historical claims. The first graph migration should focus on the 8 POC targets (FODS, FODT, Netpbm .NET, ZST, Python Netpbm, SYLK, DIF, Gnumeric). Historical format claims from prior sprints can be imported as candidates but are not on the critical path.

## Balanced Rules

- **Block final readiness claims, not implementation attempts.** Mainstream must be able to implement new capabilities, write tests, and produce dogfood outputs without requiring pre-approval. The authority layer gates accepted_for_poc only. Intermediate states (implementation_present, tests_present) are self-service.

- **Empirical evidence is allowed but must be visible.** A ProductRequirement backed only by empirical samples is valid for POC purposes. It must be marked empirical_only and the caveat must appear in all downstream consumers. Empirical evidence is not treated as equivalent to formal spec backing for commercial readiness claims.

- **Proposed deltas are allowed; direct truth mutation is forbidden.** Mainstream may submit any CapabilityDelta proposal. The proposal may be accepted or rejected. What Mainstream may not do is write accepted_for_poc status directly into poc-targets.yaml or into the CapabilityClaim node without going through the delta+evaluator flow.

- **Evidence repair is not product progress unless it affects proof validity.** If evidence metadata (timestamps, field names, advisory fields) is repaired without changing which claims it proves or which artifacts it links, this is a cosmetic change and must not count as product progress. Evidence repair counts as progress only when it moves a claim from blocked to unblocked (e.g., resolving declared_not_verified to materialized=true).

- **Partial claims should be narrowed not discarded.** When OverclaimDetector finds an overbroad claim, the default remediation is decomposition (narrow_claim or split_claim). Wholesale rejection (reject_claim) is reserved for cases where no valid decomposition exists. Valid partial evidence must be preserved.
