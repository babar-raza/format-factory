# Lane H: AI Test Generation and Evidence Review

## Implementation
Created `tools/ai/test_generation/proposal.py` with:
1. `GeneratedTestProposal` dataclass — proposal_id, source_requirement_ids, source_chunk_ids, proposed_test_name, target_file, risk_covered, expected_oracle, authority_state, test_code, rationale
2. `ProposalReviewer` — review/accept/reject pipeline with metadata tracking
3. `EvidenceReviewHelper` — scans directories for evidence gaps, produces ai_draft findings

## Key Design Decisions
- All proposals start as `ai_draft` — enforced by validate()
- ProposalReviewer does NOT write tests to product suites — only metadata
- EvidenceReviewHelper findings are always `authority_state: ai_draft`

## Tests (10)
- test_valid_proposal, test_missing_proposal_id, test_missing_source_ids, test_wrong_initial_authority
- test_accept_valid, test_reject_invalid, test_explicit_rejection, test_accepted_metadata
- test_missing_directory, test_empty_directory

## Lane H Status: CLOSED_VERIFIED
