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
