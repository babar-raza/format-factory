# Skills Three-Sprint Forecast (R102)

## R103 (Next)
- **Theme:** Governed feature execution + handoff consumption
- **Targets:**
  - Execute handoff-001 (FODS RenameSheet) via /add-dotnet-object-model-feature — LIVE mode
  - Execute handoff-002 (Netpbm ExtractChannel) via /add-dotnet-object-model-feature — LIVE mode
  - Execute handoff-004 (PPM brightness_adjust) via /add-python-object-model-feature — LIVE mode
  - Capture LIVE transcript for each, validate with transcript validator
  - Ledger entries for all 3 src-editing skills
  - Context-pack skill mapping validator (first version)
- **Quota:** 3 LIVE transcripts, 3 ledger entries, 0 anti-bypass (proven in R102)

## R104
- **Theme:** Cross-format governance + packaging integration
- **Targets:**
  - Execute handoff-003 (FODT GetPlainTextRange) via /add-dotnet-object-model-feature — LIVE mode
  - Promote 2 POC gaps to taskcards via /promote-gap-to-taskcard
  - Generate 2 execution handoffs via /generate-execution-handoff
  - Validate context-pack isolation (skills stream must not reference mainstream sprint IDs)
  - Begin skills-aware package inclusion (command files + transcripts in review ZIP)
- **Quota:** 1 LIVE transcript, 2 taskcards, 2 handoffs

## R105
- **Theme:** Full loop proof + skill retirement
- **Targets:**
  - End-to-end proof: gap → taskcard → handoff → execution → transcript → validation → package
  - Retire 1 draft skill (prove it should stay draft or promote to active)
  - Validator v3: cross-transcript consistency checks (no duplicate invocation_ids, chronological ordering)
  - Skills stream documentation: skill-author-guide.md
- **Quota:** 1 full-loop proof, 1 skill retirement, 1 validator upgrade
