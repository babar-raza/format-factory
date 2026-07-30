---
artifact_id: FF6-EVENT-31-DELTA
artifact_type: current_checkpoint_delta
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-30
---

# Event 31 delta — read before any Event 30 execution detail

Event 31 is the current operational authority. Event 30 remains the last
production-accepted XLIFF evidence boundary. These are different facts:

```text
current control checkpoint:
  commit  240474babf868fa141850d4ed4792d3a8269ef28
  event   FF6-EVENT-000031
  hash    26f95f054774f35244a2edbfc08072156a1422acfb1e1d29c2c37a617dd90d55

preserved implementation attempt:
  commit  d99fc6bf3679cd39396afbf5621847e3009ddf31
  result  MECHANICALLY_GREEN_BUT_PRODUCTION_REJECTED

last production-accepted XLIFF boundary:
  event   FF6-EVENT-000030
  commit  e13e103de0bb789ff51a8e931af0fb649474be20
  rows    26 / 105 accepted; 79 missing
  proof   1 / 1,130 dispositions accepted; 1,129 open
```

The rejected attempt is retained on GitLab `main` because deleting or hiding a
green-but-wrong result would destroy diagnostic evidence. It mechanically
emits 27 rows and reports two verified dispositions, but those counts are not
production acceptance.

## Why the attempt was rejected

1. It accepted `SAL-XLIFF-CORE-INLINE-PC-001`; the direct owner of reciprocal
   sub-flow presence is `SAL-XLIFF-CORE-INLINE-PAIRING-001`.
2. It recorded only the start-to-end candidate. The reciprocal end-to-start
   candidate remains undecided.
3. It emitted a bidirectional obligation from one-sided proof.
4. It projected an exact XLIFF 2.1 Schematron rule into the XLIFF 2.0 profile
   without separate normative 2.0 authority.
5. `SAL-XLIFF-00005` does not bind both exact reciprocal Schematron
   occurrences.
6. The adjudicator constrains accepted IDs to the generator proposal set, so
   independent review cannot select a valid denominator ID omitted by the
   generator.
7. The implementation manifest did not bind the concurrently hardened plan
   digest, so the stronger acceptance contract did not invalidate the run
   before commit.

## Exact successor

Resume:

```text
TC-FF6-XLIFF-PROFILE-SURFACE-001
XLF-04
XLF-04-BATCH-005-PARTIAL-002-B-REPAIR-001
```

The repair must:

- add RED controls for generator-omitted denominator acceptance;
- bind both exact reciprocal candidates and SAL assertions;
- accept only `SAL-XLIFF-CORE-INLINE-PAIRING-001`;
- reject generic validator and incidental hierarchy proposals;
- compile at most one pairing row only after both decisions pass;
- narrow the row to `xliff_2.1` unless separate pinned 2.0 authority is found;
- preserve all 26 Event 30 accepted rows and all 1,130 candidate identities;
- bind the exact active plan digest into every execution manifest;
- rerun tamper, deterministic, static, authority, SAL, contract, and program
  regressions before a new acceptance event.

If another live agent owns those XLIFF paths, do not overlap it. Execute only
the serialized UBL fallback `UBL-03-PARTIAL-002`.

## Truth boundary

No product source, library certification, promotion, release, or gate changed.
All six products remain `UNASSESSED`; certified products remain `0/6`.
