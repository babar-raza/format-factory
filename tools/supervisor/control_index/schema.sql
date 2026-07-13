-- Operational Control Index schema v1
-- Non-destructive SQLite overlay for Format Factory
-- Every row carries provenance: source_file, ingested_at, source_hash

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;
PRAGMA busy_timeout = 5000;

-- Schema version tracking
CREATE TABLE IF NOT EXISTS schema_meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- Sync tracking (one row per source file or directory)
CREATE TABLE IF NOT EXISTS source_manifest (
    source_path   TEXT PRIMARY KEY,
    entity_type   TEXT NOT NULL,
    last_hash     TEXT,
    last_ingested TEXT NOT NULL,
    last_modified TEXT,
    row_count     INTEGER DEFAULT 0,
    file_size     INTEGER DEFAULT 0
);

-- T1: Formats (~25 rows from registry/format-registry.yaml)
CREATE TABLE IF NOT EXISTS formats (
    format_id     TEXT PRIMARY KEY,
    display_name  TEXT NOT NULL,
    family        TEXT,
    extensions    TEXT,        -- JSON array
    mime_type     TEXT,
    spec_body     TEXT,
    spec_version  TEXT,
    legal_category INTEGER,
    tier_target   INTEGER,
    visibility    TEXT,
    scoring_total INTEGER,
    raw_json      TEXT NOT NULL,
    source_file   TEXT NOT NULL,
    ingested_at   TEXT NOT NULL,
    source_hash   TEXT NOT NULL
);

-- T2: Gaps (~1277 rows from reports/capability-layer/gap-ledger.json)
CREATE TABLE IF NOT EXISTS gaps (
    gap_id        TEXT PRIMARY KEY,
    format        TEXT,
    product_type  TEXT,
    capability_name TEXT,
    current_state TEXT,
    gap_type      TEXT,
    status        TEXT NOT NULL,
    priority      TEXT,
    blocks_poc    INTEGER DEFAULT 0,
    blocks_readiness INTEGER DEFAULT 0,
    commercial_impact TEXT,
    foss_impact   TEXT,
    owning_lane   INTEGER,
    related_capability_id TEXT,
    notes         TEXT,
    raw_json      TEXT NOT NULL,
    source_file   TEXT NOT NULL,
    ingested_at   TEXT NOT NULL,
    source_hash   TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_gaps_format ON gaps(format);
CREATE INDEX IF NOT EXISTS idx_gaps_status ON gaps(status);
CREATE INDEX IF NOT EXISTS idx_gaps_priority ON gaps(priority);

-- T2b: Gap spec_facts junction
CREATE TABLE IF NOT EXISTS gap_spec_facts (
    gap_id        TEXT NOT NULL,
    spec_fact_ref TEXT NOT NULL,
    PRIMARY KEY (gap_id, spec_fact_ref)
);

-- T3: QNames (~66 rows from shared/qname-registry/*.yaml)
CREATE TABLE IF NOT EXISTS qnames (
    qname         TEXT PRIMARY KEY,
    format_id     TEXT,
    namespace_uri TEXT,
    local_name    TEXT,
    canonical_class TEXT,
    spec_fact_ref TEXT,
    status        TEXT,
    source_layer  TEXT,
    python_file   TEXT,
    dotnet_file   TEXT,
    facade_names  TEXT,          -- JSON array
    raw_yaml      TEXT NOT NULL,
    source_file   TEXT NOT NULL,
    ingested_at   TEXT NOT NULL,
    source_hash   TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_qnames_format ON qnames(format_id);

-- T4: Capabilities (~93 rows from .governance/capabilities/registry.yaml)
CREATE TABLE IF NOT EXISTS capabilities (
    capability_id TEXT PRIMARY KEY,
    command_file  TEXT,
    parity_status TEXT,
    product_track TEXT,
    purpose       TEXT,
    status        TEXT,
    claude_code   INTEGER DEFAULT 0,
    codex         INTEGER DEFAULT 0,
    ci            INTEGER DEFAULT 0,
    raw_yaml      TEXT NOT NULL,
    source_file   TEXT NOT NULL,
    ingested_at   TEXT NOT NULL,
    source_hash   TEXT NOT NULL
);

-- T5: Skills (~74 rows from .supervisor/skill-registry.yaml)
CREATE TABLE IF NOT EXISTS skills (
    skill_id      TEXT PRIMARY KEY,
    command       TEXT NOT NULL,
    command_file  TEXT,
    idempotency   TEXT,
    product_track TEXT,
    purpose       TEXT,
    status        TEXT,
    overflow_split_allowed INTEGER DEFAULT 0,
    raw_yaml      TEXT NOT NULL,
    source_file   TEXT NOT NULL,
    ingested_at   TEXT NOT NULL,
    source_hash   TEXT NOT NULL
);

-- T6: Sprints / Evidence Runs (~3199 rows from .local/evidences/*)
CREATE TABLE IF NOT EXISTS sprints (
    sprint_id     TEXT PRIMARY KEY,
    run_id        TEXT,
    evidence_root TEXT,
    declared_scope TEXT,
    start_time    TEXT,
    end_time      TEXT,
    git_head_start TEXT,
    git_head_end  TEXT,
    verdict       TEXT,
    test_count    INTEGER,
    fail_count    INTEGER,
    worker_self_grade TEXT,
    raw_yaml      TEXT,
    source_file   TEXT NOT NULL,
    ingested_at   TEXT NOT NULL,
    source_hash   TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_sprints_verdict ON sprints(verdict);

-- T6b: Sprint work items (many per sprint)
CREATE TABLE IF NOT EXISTS sprint_work_items (
    sprint_id     TEXT NOT NULL,
    item_id       TEXT NOT NULL,
    title         TEXT,
    item_type     TEXT,
    status        TEXT,
    gap_ledger_ref TEXT,
    PRIMARY KEY (sprint_id, item_id)
);
CREATE INDEX IF NOT EXISTS idx_swi_gap ON sprint_work_items(gap_ledger_ref);

-- T7: Failures (~31 rows from .local/supervisor/failure-memory.json)
CREATE TABLE IF NOT EXISTS failures (
    failure_id    TEXT PRIMARY KEY,
    category      TEXT NOT NULL,
    root_cause    TEXT,
    correction    TEXT,
    severity      TEXT,
    sprint_discovered TEXT,
    last_seen_sprint TEXT,
    discovered_at TEXT,
    last_seen_at  TEXT,
    occurrence_count INTEGER DEFAULT 0,
    escalated     INTEGER DEFAULT 0,
    resolved      INTEGER DEFAULT 0,
    resolution    TEXT,
    resolved_at   TEXT,
    raw_json      TEXT NOT NULL,
    source_file   TEXT NOT NULL,
    ingested_at   TEXT NOT NULL,
    source_hash   TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_failures_resolved ON failures(resolved);

-- T8: Layers (~11 rows from plans/layers/index.yaml)
CREATE TABLE IF NOT EXISTS layers (
    layer_id      TEXT PRIMARY KEY,
    canonical_name TEXT NOT NULL,
    permanent_plan_path TEXT,
    plane         TEXT,
    status        TEXT,
    health        TEXT,
    maturity_current INTEGER,
    maturity_target INTEGER,
    active_task_count INTEGER DEFAULT 0,
    next_task_id  TEXT,
    next_action   TEXT,
    raw_yaml      TEXT NOT NULL,
    source_file   TEXT NOT NULL,
    ingested_at   TEXT NOT NULL,
    source_hash   TEXT NOT NULL
);

-- T8b: Layer dependencies
CREATE TABLE IF NOT EXISTS layer_dependencies (
    upstream_layer_id   TEXT NOT NULL,
    downstream_layer_id TEXT NOT NULL,
    PRIMARY KEY (upstream_layer_id, downstream_layer_id)
);

-- T9: Plan locks (~104 rows from .local/supervisor/plan-locks/*.json)
CREATE TABLE IF NOT EXISTS plan_locks (
    lock_file     TEXT PRIMARY KEY,
    plan_path     TEXT,
    status        TEXT NOT NULL,
    session_id    TEXT,
    track_type    TEXT,
    last_taskcard TEXT,
    updated_at    TEXT,
    terminal_reason TEXT,
    raw_json      TEXT NOT NULL,
    source_file   TEXT NOT NULL,
    ingested_at   TEXT NOT NULL,
    source_hash   TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_plan_locks_status ON plan_locks(status);

-- T10: Source violations (from registry/source-structure-baseline.json)
CREATE TABLE IF NOT EXISTS source_violations (
    file_path     TEXT PRIMARY KEY,
    loc           INTEGER,
    baseline_loc_cap INTEGER,
    functions     INTEGER,
    baseline_functions_cap INTEGER,
    category      TEXT,
    healing_priority TEXT,
    healing_sprint TEXT,
    raw_json      TEXT NOT NULL,
    source_file   TEXT NOT NULL,
    ingested_at   TEXT NOT NULL,
    source_hash   TEXT NOT NULL
);

-- E1: Event log (append-only, from continuation-ledger.jsonl)
CREATE TABLE IF NOT EXISTS events (
    event_id      INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp     TEXT NOT NULL,
    event_type    TEXT NOT NULL,
    source        TEXT NOT NULL,
    session_id    TEXT,
    sprint_id     TEXT,
    artifact_path TEXT,
    detail        TEXT,
    ingested_at   TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
CREATE INDEX IF NOT EXISTS idx_events_session ON events(session_id);
CREATE INDEX IF NOT EXISTS idx_events_ts ON events(timestamp);

-- FTS5: Full-text search across all entity types
CREATE VIRTUAL TABLE IF NOT EXISTS fts_operational USING fts5(
    entity_type,
    entity_id,
    content,
    tokenize = 'porter unicode61'
);

-- ============================================================
-- CONCURRENCY CONTROL TABLES (schema v2)
-- ============================================================

-- T11: Mission-level controller lock
-- CRITICAL: partial unique index (not UNIQUE column constraint) to allow
-- unlimited RELEASED/EXPIRED rows while enforcing ONE ACTIVE per mission
CREATE TABLE IF NOT EXISTS mission_locks (
    lock_id         TEXT PRIMARY KEY,
    mission_id      TEXT NOT NULL,
    controller_type TEXT NOT NULL,
    pid             INTEGER NOT NULL,
    session_id      TEXT NOT NULL,
    host_identity   TEXT NOT NULL,
    branch          TEXT NOT NULL,
    worktree_path   TEXT NOT NULL,
    plan_version    TEXT,
    acquired_at     TEXT NOT NULL,
    heartbeat_at    TEXT NOT NULL,
    lease_expires   TEXT NOT NULL,
    recovery_token  TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'ACTIVE'
                    CHECK(status IN ('ACTIVE','RELEASED','EXPIRED','STOLEN'))
);
-- CRITICAL: partial unique index — only one ACTIVE row per mission
-- Multiple RELEASED/EXPIRED/STOLEN rows are allowed (history)
CREATE UNIQUE INDEX IF NOT EXISTS idx_mission_lock_active
    ON mission_locks(mission_id)
    WHERE status = 'ACTIVE';

-- T12: Worker path ownership claims
CREATE TABLE IF NOT EXISTS worker_claims (
    claim_id        TEXT PRIMARY KEY,
    mission_id      TEXT NOT NULL,
    lock_id         TEXT NOT NULL
                    REFERENCES mission_locks(lock_id) ON DELETE CASCADE,
    worker_id       TEXT NOT NULL,
    task_id         TEXT NOT NULL,
    resource_pattern TEXT NOT NULL,
    resource_type   TEXT NOT NULL DEFAULT 'file',
    mode            TEXT NOT NULL DEFAULT 'WRITE'
                    CHECK(mode IN ('READ','WRITE','INTEGRATE')),
    acquired_at     TEXT NOT NULL,
    lease_expires   TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'ACTIVE'
                    CHECK(status IN ('ACTIVE','RELEASED','EXPIRED'))
);
CREATE INDEX IF NOT EXISTS idx_worker_claims_active
    ON worker_claims(mission_id, status)
    WHERE status = 'ACTIVE';

-- T13: Immutable concurrency transition audit log
CREATE TABLE IF NOT EXISTS concurrency_transitions (
    transition_id   INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type     TEXT NOT NULL
                    CHECK(entity_type IN ('mission_lock','worker_claim','checkpoint')),
    entity_id       TEXT NOT NULL,
    from_status     TEXT,
    to_status       TEXT NOT NULL,
    actor           TEXT NOT NULL,
    reason          TEXT,
    occurred_at     TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_ct_entity ON concurrency_transitions(entity_type, entity_id);

-- T14: Task checkpoints (patch file references — no blobs in DB)
CREATE TABLE IF NOT EXISTS concurrency_checkpoints (
    checkpoint_id   TEXT PRIMARY KEY,
    task_id         TEXT NOT NULL,
    worker_id       TEXT NOT NULL,
    description     TEXT,
    base_sha        TEXT NOT NULL,
    patch_path      TEXT NOT NULL,
    changed_files   TEXT NOT NULL,
    created_at      TEXT NOT NULL,
    status          TEXT NOT NULL DEFAULT 'VALID'
                    CHECK(status IN ('VALID','APPLIED','SUPERSEDED'))
);
CREATE INDEX IF NOT EXISTS idx_checkpoints_task ON concurrency_checkpoints(task_id, created_at);

-- T15: Maintenance obligations (from reports/supervisor/maintenance-obligations.json)
CREATE TABLE IF NOT EXISTS maintenance_obligations (
    obligation_id   TEXT PRIMARY KEY,
    type            TEXT,
    status          TEXT NOT NULL DEFAULT 'open',
    scheduled_date  TEXT,
    owner           TEXT,
    source_plan     TEXT,
    source_taskcard TEXT,
    action          TEXT,
    reason          TEXT,
    created_at      TEXT,
    completed_at    TEXT,
    completion_evidence TEXT,
    raw_json        TEXT NOT NULL,
    source_file     TEXT NOT NULL,
    ingested_at     TEXT NOT NULL,
    source_hash     TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_mor_status ON maintenance_obligations(status);
CREATE INDEX IF NOT EXISTS idx_mor_scheduled ON maintenance_obligations(scheduled_date);
CREATE INDEX IF NOT EXISTS idx_mor_owner ON maintenance_obligations(owner);

-- v3: canary shadow observation tables
-- TC-SCHEMA-001 (clever-tickling-island): Extends control-index.db with two
-- shadow observation tables for staged promotion of governance validators and
-- LLM grader provider switches.

CREATE TABLE IF NOT EXISTS validator_shadow_observations (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id              TEXT    NOT NULL,
    sprint_id           TEXT    NOT NULL,
    validator_name      TEXT    NOT NULL,
    format_scope        TEXT,           -- NULL means portfolio-wide
    stable_result       TEXT    NOT NULL, -- PASS | WARN | FAIL
    stable_blocks_sprint INTEGER NOT NULL DEFAULT 0,
    candidate_result    TEXT,           -- NULL if candidate call failed
    candidate_blocks_sprint INTEGER,
    agreement           INTEGER,        -- 1=agree, 0=disagree, NULL=error
    error               TEXT,           -- error message if candidate call failed
    observed_at         TEXT    NOT NULL -- ISO-8601 timestamp
);

CREATE INDEX IF NOT EXISTS idx_vso_validator
    ON validator_shadow_observations (validator_name);

CREATE INDEX IF NOT EXISTS idx_vso_sprint
    ON validator_shadow_observations (sprint_id);

CREATE TABLE IF NOT EXISTS grader_shadow_observations (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    run_id              TEXT    NOT NULL,
    sprint_id           TEXT    NOT NULL,
    work_item_id        TEXT    NOT NULL,
    primary_provider    TEXT    NOT NULL,
    shadow_provider     TEXT    NOT NULL,
    primary_grade       TEXT    NOT NULL, -- ACCEPTED | REWORK | PARTIAL
    shadow_grade        TEXT,             -- NULL if shadow call failed
    agreement           INTEGER,          -- 1=agree, 0=disagree, NULL=error
    error               TEXT,             -- error message if shadow call failed
    observed_at         TEXT    NOT NULL  -- ISO-8601 timestamp
    -- Deferrable FK to sprint table if sprint tracking added in future
);

CREATE INDEX IF NOT EXISTS idx_gso_shadow_provider
    ON grader_shadow_observations (shadow_provider);

CREATE INDEX IF NOT EXISTS idx_gso_sprint
    ON grader_shadow_observations (sprint_id);

-- T-GA: gap_attempts — one row per sprint-gap attempt (TC-OCRD-A1)
CREATE TABLE IF NOT EXISTS gap_attempts (
    attempt_id     TEXT PRIMARY KEY,
    gap_id         TEXT NOT NULL,
    sprint_id      TEXT NOT NULL,
    item_id        TEXT,
    outcome        TEXT,
    rework_reason  TEXT,
    attempted_at   TEXT NOT NULL,
    source_file    TEXT,
    ingested_at    TEXT DEFAULT (datetime('now'))
);
CREATE INDEX IF NOT EXISTS idx_ga_gap ON gap_attempts(gap_id);
CREATE INDEX IF NOT EXISTS idx_ga_sprint ON gap_attempts(sprint_id);
CREATE INDEX IF NOT EXISTS idx_ga_outcome ON gap_attempts(outcome);

-- ============================================================
-- v4: Control Layer Discovery Tables (TC-OCRD-C3)
-- ============================================================

-- T-CL: Control layer registry (one row per identified control layer)
CREATE TABLE IF NOT EXISTS control_layers (
    layer_key                TEXT PRIMARY KEY,
    name                     TEXT NOT NULL,
    status                   TEXT NOT NULL,
    authority_scope          TEXT,
    primary_purpose          TEXT,
    implementation_paths     TEXT,  -- JSON array
    data_paths               TEXT,  -- JSON array
    consumers                TEXT,  -- JSON array
    observable_features_count INTEGER DEFAULT 0,
    last_assessed            TEXT,
    ingested_at              TEXT DEFAULT (datetime('now'))
);

-- T-CF: Control features (one row per observable feature per layer)
CREATE TABLE IF NOT EXISTS control_features (
    feature_id               TEXT PRIMARY KEY,
    control_layer_key        TEXT REFERENCES control_layers(layer_key),
    feature_name             TEXT NOT NULL,
    category                 TEXT,
    entry_points             TEXT,  -- JSON array
    current_status           TEXT NOT NULL,
    authority_effect         TEXT,
    observable_behavior      TEXT,  -- JSON object
    ingested_at              TEXT DEFAULT (datetime('now'))
);

-- T-CFC: Control feature consumers (many-to-many feature → consumer)
CREATE TABLE IF NOT EXISTS control_feature_consumers (
    id                       INTEGER PRIMARY KEY AUTOINCREMENT,
    feature_id               TEXT REFERENCES control_features(feature_id),
    consumer_id              TEXT NOT NULL,
    consumer_type            TEXT,
    consumer_path            TEXT,
    expected_contract        TEXT,
    dependency_strength      TEXT,
    migration_risk           TEXT
);

-- T-FPR: Feature parity results (one row per feature disposition)
CREATE TABLE IF NOT EXISTS feature_parity_results (
    feature_id               TEXT PRIMARY KEY REFERENCES control_features(feature_id),
    reuse_strategy           TEXT,
    parity_status            TEXT NOT NULL,
    intentional_changes      TEXT,
    verified_at              TEXT
);

-- T-QR: Quarantine registry (artifacts failing validation pre-ingest)
CREATE TABLE IF NOT EXISTS quarantines (
    quarantine_id            TEXT PRIMARY KEY,
    artifact_path            TEXT NOT NULL,
    detected_at              TEXT DEFAULT (datetime('now')),
    validation_failures      TEXT,  -- JSON array
    severity                 TEXT,
    status                   TEXT DEFAULT 'ACTIVE'
);

-- T-TR: Trust registry (authority level per artifact path)
CREATE TABLE IF NOT EXISTS trust_registry (
    artifact_path            TEXT PRIMARY KEY,
    authority_level          TEXT NOT NULL,
    trusted                  INTEGER NOT NULL DEFAULT 0,
    reason                   TEXT,
    assessed_at              TEXT DEFAULT (datetime('now'))
);

-- T-PL: Plans table (scanned from plans/ directory)
CREATE TABLE IF NOT EXISTS plans (
    plan_id                  TEXT PRIMARY KEY,
    plan_path                TEXT NOT NULL,
    plan_type                TEXT,
    title                    TEXT,
    status                   TEXT,
    open_taskcards           INTEGER DEFAULT 0,
    closed_taskcards         INTEGER DEFAULT 0,
    ingested_at              TEXT DEFAULT (datetime('now'))
);

-- Indexes for v4 tables
CREATE INDEX IF NOT EXISTS idx_cf_layer ON control_features(control_layer_key);
CREATE INDEX IF NOT EXISTS idx_cfc_feature ON control_feature_consumers(feature_id);
CREATE INDEX IF NOT EXISTS idx_q_status ON quarantines(status);
CREATE INDEX IF NOT EXISTS idx_tr_trusted ON trust_registry(trusted);
CREATE INDEX IF NOT EXISTS idx_plans_type ON plans(plan_type);
