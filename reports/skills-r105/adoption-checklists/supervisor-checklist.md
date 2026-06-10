# Supervisor Adoption Checklist (Skills R105)

## During Work Item Grading
- [ ] Check if work item declares a `skill_id`
- [ ] If skill_id present, locate transcript at declared evidence_path
- [ ] Validate transcript with `validate_skill_transcript.py`
- [ ] Apply grade mapping:
  - Missing transcript => OVERCLAIMED
  - Invalid transcript => OVERCLAIMED
  - Valid + PASS => ACCEPTED_VERIFIED eligible
  - Valid + FAIL => REWORK_REQUIRED
  - anti-bypass-demo + FAIL => ACCEPTED (expected)

## Pre-Sprint Checks
- [ ] Run `validate_claude_commands.py` to check command file integrity
- [ ] Verify no new orphan commands introduced
- [ ] Check registry consistency (active skills have command files)
