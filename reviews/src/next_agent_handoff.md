# Next Agent Handoff


## Next-agent execution handoff

Start in planning/recon mode, not broad rewrite mode. The first implementation sprint should create the governance assets and validators, then perform one small pilot.

Recommended first pilot: **FODT .NET + FODT Python conceptual mirror**.

Taskcards:
- TC-001: Remove generated/build artifacts from source consideration and add ignore/audit rules.
- TC-002: Create canonical construct registry schema.
- TC-003: Seed FODT minimal QName registry from legal ODF/FODT spec facts: office body, text paragraph, text heading, text list, table/table-cell if currently parsed.
- TC-004: Add source-to-spec manifest for existing FODT classes and mark current names as facade/legacy.
- TC-005: Generate new spec-aligned class skeletons and adapters without deleting old behavior.
- TC-006: Add tests proving existing public API still works and new QName model exists.
- TC-007: Repeat for Python FODT using the same manifest identities.
- TC-008: Run validators, document evidence, and stop for audit before expanding to FODS.
