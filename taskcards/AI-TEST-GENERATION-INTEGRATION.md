# Taskcard: AI-TEST-GENERATION-INTEGRATION

## Objective
Implement mandatory AI-assisted test generation as part of the AI platform. Test ideas are generated, filtered by deterministic reviewer, and accepted tests become normal pytest/.NET tests.

## Status
`implemented_fixture_mode` — proposal.py with GeneratedTestProposal, ProposalReviewer, and EvidenceReviewHelper implemented in R27 (cb7e05c). 10 tests pass.

## Prerequisites
- AI-GPT-OSS-SYNTHESIS-CONTROLS operational (synthesis pipeline available)
- Requirements available for at least one format (FODS generated-requirements)

## Allowed Scope
- Define test idea schema in `tools/ai/schemas/`
- Implement test idea generator using synthesis pipeline
- Implement deterministic test reviewer/filter
- Create pipeline: requirements → test ideas → reviewed → accepted tests
- Create tests in `tests/ai/test_generation.py`

## Forbidden Scope
- No generated tests bypassing review gate
- No product source changes
- No test ideas treated as authoritative without review

## Gates
1. Test idea schema defined and validated
2. Generator produces test ideas citing requirements and spec chunks
3. Reviewer/filter rejects trivial/redundant/incorrect ideas
4. Accepted test ideas converted to pytest/xUnit tests
5. Generated tests pass when added to test suite
6. Test idea artifacts retained for replay

## Evidence Requirements
- Generated test idea samples
- Reviewer filter results (accepted/rejected counts)
- Accepted test execution results
- Quality metrics (acceptance rate, coverage contribution)

## Validation Requirements
- `tests/ai/test_generation.py` passes
- Acceptance rate > 50% (quality threshold)

## Closeout Criteria
- Test generation pipeline operational for one format
- At least 5 accepted tests added to suite and passing

## Next Transition
On closeout: Test generation available for all formats in acquisition pipeline.
