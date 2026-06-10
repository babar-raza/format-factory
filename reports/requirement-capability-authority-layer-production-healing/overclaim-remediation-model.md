# Overclaim Remediation Model

Sprint ID: FORMAT-FACTORY-REQUIREMENT-CAPABILITY-AUTHORITY-LAYER-PRODUCTION-BLOCKER-HEALING-001
Owner: Lane C

## 10 Overclaim Patterns and Remediation Actions

**Pattern 1:** Full support claimed, partial proof present
- Evidence: operation=full_support claimed; only parse + inspect TestArtifacts linked; no save or export TestArtifacts
- Remediation: **split_claim** — split into accepted PARSE claim (operation=parse, tests_present=true) + blocked SAVE claim (operation=save, blocked_missing_test)
- Result: valid parse evidence is preserved; full_support claim is rejected; two narrower claims replace it

**Pattern 2:** Save claimed, export proof only (different-format output)
- Evidence: operation=save claimed; DogfoodArtifact is in a different format (e.g., CSV produced from FODS)
- Remediation: **downgrade_status** — save claim rejected; new EXPORT claim created (operation=export, direction=export_only, fidelity=declared_limited)
- Result: export capability is accepted; save capability remains blocked_missing_implementation

**Pattern 3:** Roundtrip claimed, parse-only proof available (no same-format write)
- Evidence: operation=roundtrip claimed; only load and parse proof linked; write_fodt or write_fods not implemented
- Remediation: **reject_claim** (roundtrip) + **narrow_claim** — new LOAD_EXPORT claim created (operation=export, direction=export_only)
- Result: LOAD_EXPORT accepted; ROUNDTRIP rejected; no partial roundtrip passes as full roundtrip

**Pattern 4:** All variants claimed, one variant tested
- Evidence: variant=all_variants in claim scope; TestArtifacts cover only P3 ASCII; P6 binary untested
- Remediation: **split_claim** by variant — claim_P3: accepted (tests_present=true); claim_P6: blocked_missing_test
- Result: P3 claim is preserved; P6 claim is split out as a separate blocked claim

**Pattern 5:** Commercial ready claimed, helpers/CLI tools only (no format output produced)
- Evidence: accepted_for_poc claimed; only helper scripts or CLI wrappers exist; no format file output produced
- Remediation: **require_dogfood** — block readiness; add DogfoodArtifact requirement; claim demoted to blocked_missing_dogfood
- Result: no commercial readiness claim until actual format file output is produced and validated

**Pattern 6:** Dogfood complete claimed, no output artifact linked or checksum missing
- Evidence: dogfood_present=true claimed in delta; no DogfoodArtifact node linked in graph; or artifact path missing
- Remediation: **require_dogfood** — keep dogfood_present=false; block coverage_validated transition
- Result: dogfood claim cannot advance until EvidenceGraphImporter links a valid DogfoodArtifact with checksum

**Pattern 7:** Test coverage exists in repo, tests not linked to claim in graph
- Evidence: test files exist under tests/python/fods/; no tested_by edge links them to the CapabilityClaim
- Remediation: **require_tests** — coverage remains unvalidated; EvidenceGraphImporter must create tested_by edges
- Result: tests_present remains false in graph until edge exists; test existence alone is insufficient

**Pattern 8:** Spec-backed claimed, only empirical evidence available
- Evidence: derives_from=SpecRequirementRef claimed; actual source is EmpiricalEvidence (format sample)
- Remediation: **mark_empirical_only** — reclassify ProductRequirement as empirical_only with caveat; downstream claims become empirical_only-backed
- Result: empirical support is preserved but clearly labeled; spec-backed claims must not misrepresent source

**Pattern 9:** Accepted, requirement stale (stale requirement backing accepted claim)
- Evidence: CapabilityClaim status=accepted_for_poc; backing ProductRequirement changed to stale
- Remediation: **downgrade_status** — CapabilityClaim demoted from accepted_for_poc to stale; revalidation required
- Result: accepted claim cannot remain accepted_for_poc while its requirement is stale; propagation chain enforced

**Pattern 10:** Supports format claimed, blocking UnsupportedFeature present
- Evidence: operation=roundtrip or save claimed; UnsupportedFeature with severity=blocking exists (e.g., binary write not implemented)
- Remediation: **request_policy_decision** or **add_unsupported_feature** — if non_blocking: accepted_with_limitations; if blocking: claim must be blocked until feature is implemented
- Result: no accepted_for_poc while blocking UnsupportedFeature exists; non-blocking features allow accepted_with_limitations

## Remediation Actions Enum

- **narrow_claim** — Reduce the claim's scope dimensions (operation, variant, fidelity) to match what evidence supports
- **split_claim** — Divide one overbroad claim into multiple narrower claims, each matching a subset of evidence
- **add_unsupported_feature** — Create an UnsupportedFeature record for the missing or limited capability; link via limited_by edge
- **require_dogfood** — Block coverage_validated transition until DogfoodArtifact is linked with valid checksum
- **require_tests** — Block tests_present transition until TestArtifact is linked via tested_by edge
- **require_implementation** — Block implementation_present transition until ImplementationArtifact is linked
- **downgrade_status** — Demote claim status to the highest valid state given current evidence
- **mark_empirical_only** — Reclassify ProductRequirement source as empirical_only; add caveat to downstream claims
- **request_policy_decision** — Flag claim as requires_policy_decision; block until ProductPolicyDecision recorded
- **reject_claim** — Reject the claim entirely when no valid decomposition is possible; require new claim submission

## Product Examples (5)

**FODS:** Claim "FODS full object model support" with only read-side APIs implemented.
Overclaim pattern 1 applies. Remediation: split_claim. Result: inspect claims accepted (operation=inspect for all implemented APIs); edit/save claims split out as blocked_missing_implementation.

**FODT:** Claim "FODT roundtrip with formatting preserved" with only append_paragraph and get_paragraph_text implemented.
Overclaim pattern 3 applies. Remediation: reject_claim (roundtrip) + narrow_claim to paragraph_edit. Result: LOAD_EXPORT accepted (operation=export, fidelity=declared_limited); ROUNDTRIP rejected; formatting_preserved fidelity claim blocked.

**Netpbm:** Claim "Netpbm all formats supported" with only P3 ASCII PPM read/write proven.
Overclaim pattern 4 applies. Remediation: split_claim by variant. Result: claim_P3_ASCII accepted; claim_P6_binary, claim_PGM, claim_PBM split as separate blocked claims. variant=all_formats rejected.

**ZST:** Claim "ZST dictionary mode roundtrip" with only single-frame compress+decompress proven.
Overclaim pattern 3 applies. Remediation: reject_claim (dictionary roundtrip) + narrow_claim. Result: single_frame_compress accepted; dictionary_mode split as blocked_missing_implementation. Roundtrip claim requires byte-identical decompressed output before acceptance.

**SYLK:** Claim "SYLK full CSV export" with only single-sheet SYLK parsing + CSV output proven.
Overclaim pattern 1 applies (all-variants subtype). Remediation: split_claim by variant. Result: single_sheet_csv_export: accepted; multi_sheet_csv_export: blocked_missing_test. variant=full rejected in claim scope.
