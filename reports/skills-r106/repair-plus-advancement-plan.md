# Repair + Advancement Plan — Skills R106

## Repair Items (from R105 limitations)
1. **Transcript grading integration** — R105 tested 13 scenarios but didn't modify grade_declared_work.py. R106 must add transcript-aware grading.
2. **Draft skill resolution** — record-lane-execution and check-mcp-status still draft. Decide: promote, defer-with-reason, or retire.
3. **Orphan command cleanup** — 4 command files not in registry as active skills. Register or document deferral.

## Advancement Items (new R106 work)
1. **Transcript-to-grade integration tests** — Add tests that verify grade_declared_work.py applies transcript rules
2. **Handoff advancement** — Add at least 1 new governed handoff beyond R105's 2
3. **Adoption enforcement hardening** — Move from checklists to validator-enforceable rules
4. **Command validator improvements** — Test missing required sections, incomplete refusal rules
5. **Next Skills prompt** — Generate R107 prompt incorporating all R106 improvements
