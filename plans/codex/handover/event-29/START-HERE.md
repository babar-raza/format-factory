---
artifact_id: FF6-HANDOVER-EVENT-29-START
artifact_type: immutable_checkpoint_entrypoint
visibility: internal
publish_allowed: false
generated_by: codex
generated_at: 2026-07-30
---

# Event 29 checkpoint

This packet binds the provider shift to:

- XLIFF implementation commit
  `315efa5f5f4420202b5254c86ccd8863a91c385f`;
- Event/projection commit
  `c1f4be66b97acb9a23faa02764e3d41ec1e4a3b0`;
- native event `FF6-EVENT-000029`;
- event hash
  `de12acdefd04c37a918e3fd27dcb8dd076f53e576ee7049cf1efc732d02028bb`;
- controller state `CONTRACT`;
- canonical task `TC-FF6-XLIFF-PROFILE-SURFACE-001`;
- first unmet step `XLF-04`;
- exact next microstep
  `XLF-04-BATCH-005-PARTIAL-002_DISPOSITION_VERIFICATION_AND_OBLIGATION_COMPILATION`;
- zero certified products and no promotion.

The Batch 005 partial checkpoint proves source-authentic census generation,
not independent semantic verification: all 1,130 candidate dispositions remain
explicitly unverified.

Read [CHECKPOINT.yaml](CHECKPOINT.yaml), then [RUNBOOK.md](RUNBOOK.md). The
root [START-HERE](../START-HERE.md) links the complete durable program
documentation.
