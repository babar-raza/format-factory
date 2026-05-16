# Memory 34: ZST R17 Gate 4 Planning and Multi-Format Gate 1 Intake
Sprint: FORMAT-FACTORY-R17-R16-CLOSURE-VERIFY-ZST-GATE4-PLANNING-AND-MULTI-FORMAT-GATE1-SWARM-001
Date: 2026-05-16
Commit: (see this sprint's commit)

## R16 Closure Verification

- Commit 9feea07 EXISTS and is complete (41 files, 2378 insertions)
- BUNDLE_BUILT_BEFORE_COMMIT: correctly classified; live repo is authoritative
- Registry gate_3.status=passed confirmed; corpus 8+3=11 files confirmed
- Tests: 69 passed, 7 skipped (post-fix)

## ZST Gate 4: planning_complete

- Status: gate_4.status = planning_complete (NOT passed; prototype required for full pass)
- Artifact: acquisition-packs/zst/parser-notes.md
- Created: R17 (2026-05-16)
- DEC-034 IV: PASS (10/10 checks)
- Gate 4 full pass: requires prototype in prototypes/by-format/zst/ + human review → R18+
- implementation_authorized: false (UNCHANGED)
- generated_requirements_authorized: false (UNCHANGED)

## Key Technical Notes from parser-notes.md

1. ZST is a codec/compression format — no DOM, no structured fields
2. Magic number: 0x28 0xB5 0x2F 0xFD (LE) for Zstandard frames
3. Skippable frame magic: 0x184D2A50–0x184D2A5F range
4. Content_Size in frame header is OPTIONAL — must use stream_reader() not decompress()
   for frames without Content_Size (block-128k.zst, empty-block.zst, zeroSeq_2B.zst)
5. RFC 9659 = HTTP context only; does not change frame format
6. Recommended architecture: Phase 1 = zstandard library wrapper; Phase 2 = pure parser
7. Commercial value risk: Aspose already supports ZST; standalone value unclear

## Multi-Format Gate 1 Intake (R17)

| Format | Status | Notes |
|--------|--------|-------|
| FODP | Gate 1 packet ready | OASIS RF Cat 1; ~8.5-8.8; Aspose audit needed |
| FODG | Gate 1 packet ready | OASIS RF Cat 1; ~8.2-8.5; Aspose audit needed |
| ORA | Gate 1 packet ready | freedesktop Cat 2; ~6.5-7.0; Aspose audit needed |
| Gnumeric | Gate 1 packet ready | GNOME OSS Cat 2; ~8.0-8.5; DEC-034 IV needed |
| ABW | Gate 1 packet ready | AbiSource Cat 2; ~7.5-8.0; outdated spec risk |
| dnumber | AUTOMATIC_REJECT | = Apple Numbers (.numbers); Category 5; no public spec |

### dnumber Identity Resolution
- Search evidence: "dnumber" = Apple Numbers (.numbers)
- No ".dnumber" extension in any file format database
- Apple has never published a formal spec; reverse engineering only → Category 5

## Taskcards Created in R17

- ZST-R18-GATE5-REQUIREMENTS-READINESS.md — pending execution prompt
- FODP-FODG-GATE1-BATCH.md — pending Conway R9 + execution prompt
- ORA-GNUMERIC-ABW-GATE1-SCORING-IV.md — pending Aspose audits + execution prompt

## Taskcards Completed in R17

- ZST-R17-GATE4-PARSER-PROTOTYPE-PLANNING.md → completed
- R17-MULTI-FORMAT-GATE1-INTAKE.md → completed

## Next Sprints

- R18: ZST Gate 4 prototype + Gate 5 readiness (requires execution prompt)
- R19: FODP/FODG Gate 1 batch (requires Conway R9 stable + execution prompt)
- R19/R20: Gnumeric/ABW/ORA Gate 1 scoring IV (requires Aspose audits + execution prompt)

## Authority File Updates

- master-plan.md: v2.62 (updated last_completed_sprint to R17 ID)
- ROADMAP.md: ZST Gate 4 planning_complete; multi-format shortlist expanded
- README.md: ZST and multi-format status updated
- registry/format-registry.yaml: gate_4.status=planning_complete
- acquisition-packs/zst/pack.yaml: parser_notes.status=planning_complete
