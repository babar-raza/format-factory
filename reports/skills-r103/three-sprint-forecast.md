# Skills Three-Sprint Forecast (R103)

## R104 (Next)
- **Theme:** Adoption enforcement + first LIVE executions
- **Targets:**
  - Execute 2 LIVE handoffs (FODS RenameSheet, Netpbm ExtractChannel)
  - Add transcript validation to supervisor grading pipeline
  - Add stream field to evidence declaration schema
  - Stream-specific supervisor outputs
- **Quota:** 2 LIVE transcripts, 1 supervisor integration, stream-aware outputs

## R105
- **Theme:** Enforce transcript gates in product source flows
- **Targets:**
  - All mainstream product lanes must produce valid transcripts
  - Supervisor rejects work items without transcripts (enforced, not advisory)
  - Cross-transcript consistency checks (no duplicate invocation_ids)
  - Validator v3: chronological ordering, stream tagging
- **Quota:** 3 mainstream transcripts validated, 1 consistency check

## R106
- **Theme:** Reduce manual handoff usage
- **Targets:**
  - Convert 2 manual handoffs into governed skills
  - Skill retirement: review draft skills, promote or remove
  - Skill-author-guide.md documentation
  - End-to-end proof: gap to taskcard to handoff to execution to transcript
- **Quota:** 2 skills promoted from handoff, 1 retirement, 1 full-loop proof
