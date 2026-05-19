# R30 Lane D: AI Test-Generation Proposal Repair
# Date: 2026-05-19

## Defect
`tools/ai/test_generation/proposal.py` lines 79 and 92: `ProposalReviewer.review()` and `reject()` type-hinted `TestProposal` which does not exist. The class is `GeneratedTestProposal`. This would cause `NameError` at runtime if Python evaluated those annotations.

## Fix
Replaced `TestProposal` with `GeneratedTestProposal` in both method signatures (lines 79, 92).

## Tests Added (Lane D in test_r30_ai_defect_closure.py)
- `test_review_valid_proposal` — instantiate ProposalReviewer, review valid GeneratedTestProposal
- `test_review_invalid_proposal` — review proposal with missing required fields
- `test_reject_sets_authority_state` — reject sets authority_state to rejected
- `test_accepted_metadata` — get_accepted_metadata returns correct data
- `test_missing_directory` — EvidenceReviewHelper on nonexistent path
- `test_empty_directory` — EvidenceReviewHelper on empty dir
- `test_pending_detection` — EvidenceReviewHelper detects PENDING

## Status: CLOSED_VERIFIED
