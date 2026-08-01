---
artifact_id: FF6-ACTIVE-WORK-CHECKPOINT-EVENT-38
artifact_type: active_work_checkpoint
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-08-01
---

# Active work checkpoint: Event 38

## Immutable accepted boundary

- GitLab control checkpoint: `d1f8b3229bf3be32675e047b1469259ad7375500`
- XLIFF semantic commit: `3fc939ad70ec6caac9e0699041076e02de00c5d2`
- Native event: `FF6-EVENT-000038`
- Event hash: `13db4cceafcefb86d9c964d7c3e20e7d63092977faf50002ef0c88ea4f6b5603`
- Controller state: `CONTRACT`
- Active task: `TC-FF6-XLIFF-PROFILE-SURFACE-001`
- Task state: `WORK_IN_PROGRESS`
- First unmet task step: `XLF-04`
- Completed microstep: `XLF-04-BATCH-005-PARTIAL-002-F`
- Exact next microstep: `XLF-04-BATCH-005-PARTIAL-002-G`

## What the outgoing shift achieved

The accepted slice independently bound the XLIFF 2.1 source `xml:lang` versus
root `srcLang` compatibility report and corroborating prose. It accepted only
`SAL-XLIFF-CORE-DOCUMENT-SOURCE-LANGUAGE-001`, rejected downstream and
incidental mappings, rejected a cardinality overclaim, rejected omitted-value
inheritance as a separate unproved behavior, and explicitly excluded XLIFF 2.0.

It also repaired selected SAL seeding with exact-ID fail-closed selection,
transactional restore, scoped merge, QName collision protection, and
byte-idempotency. The repair and semantic slice passed 90 affected tests in the
shared worktree and immutable detached checkout, 69 production-program tests,
94 format-contract tests with one named baseline deselection, all 32 XLIFF SAL
facts, five authority locks, and static checks including Pyright.

Accepted counts are 7/1,130 dispositions and 30/105 source-bound obligations.
This is partial contract evidence only.

## Exact successor

Adjudicate `XLF-CAND-CORE-SCHEMATRON-5D563A565DC6DCFE` at XLIFF 2.1
`schematron/rule[14]/report[1]`, which compares target `xml:lang` with root
`trgLang`. Determine the direct compatibility owner or expand the denominator
only if primary authority proves a distinct obligation. Preserve all 30 rows
and all 1,130 candidate identities.

## Transfer status

The tracked semantic and control state is reconstructible from GitLab. No
uncommitted product overlay is part of this handover. Provider identities,
tokens, leases, execution manifests, and mutation authorizations do not
transfer. The outgoing identity remains live only while the handover packet is
being sealed and must be released after remote verification.

All six products remain `UNASSESSED`; certification remains `0/6`.
