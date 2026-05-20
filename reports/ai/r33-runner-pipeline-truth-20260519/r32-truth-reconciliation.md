# R32 Truth Reconciliation

## R32 Narrative Conflicts Identified
1. **"AI_SYSTEM_CLEANLY_VERIFIED" vs "control_plane_only"**: R32 final verdict says "AI_SYSTEM_CLEANLY_VERIFIED" but the AI system was really only verified at the control-plane + fixture level. Live pipeline was a stub returning `not_yet_implemented`.
2. **Commit SHA confusion**: R32 implementation commit was f299a5b, metadata commit was b158afe. The final verdict listed f299a5b but the bundle was built at b158afe HEAD.
3. **Retrieval "ranked, filtered, and explainable"**: R32 implemented TF-IDF lexical retriever, but the default fixture chunks were all identical ("Normalized content for fods section X"), so retrieval returned all 3 with equal scores (0.05). The ranking mechanism worked but had nothing to rank.

## R33 Resolutions
1. **Synthesis mode labels**: R33 introduces explicit `synthesis_mode` field: `fixture_synthesis` vs `live_gateway_synthesis` vs `blocked_live_synthesis`. Every pipeline output now self-labels its mode.
2. **Commit metadata model**: R33 introduces `SprintCommitMetadata` with separate `implementation_commit`, `metadata_commit`, `bundle_head_commit` fields. No more ambiguity.
3. **Diverse fixture corpus**: R33 replaces generic identical chunks with 5 FODS-specific chunks containing distinct technical content (XML structure, cell formatting, data types, formulas, metadata). Retrieval now produces differentiated scores: Data Types (0.049, 5/5 terms), XML Structure (0.036, 5/5 terms), Metadata (0.015, 2/5 terms). Two chunks excluded below threshold.
4. **Live pipeline implemented**: R33 replaces `not_yet_implemented` stub with real `run_live_pipeline_checks()` that calls `_build_live_output()` via gateway. Blocked gracefully when env not configured.
5. **Contradiction policy**: R33 adds explicit modes (required, optional, skipped_fixture_only) instead of implicit boolean.
6. **Evidence validator integration**: R33 adds `--validate-evidence` flag to runner that checks contract artifact existence.
