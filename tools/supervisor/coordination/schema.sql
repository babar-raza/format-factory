-- Multi-agent coordination schema (Mission AGENT-COORD-2026-07-15)
-- Dedicated coordination.db -- deliberately separate from control-index.db
-- (per-edit hot path must not share a write lock with analytics ingest).
-- All timestamps are UTC ISO-8601 strings. Ordering guarantees come from
-- INTEGER PRIMARY KEY rowids, never from timestamps (clock-skew tolerance).

CREATE TABLE IF NOT EXISTS schema_meta (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS agents (
    agent_id         TEXT PRIMARY KEY,
    agent_token_hash TEXT NOT NULL,
    provider         TEXT NOT NULL,
    agent_type       TEXT NOT NULL DEFAULT 'interactive'
                     CHECK(agent_type IN ('interactive','headless','subagent')),
    execution_mode   TEXT NOT NULL DEFAULT 'interactive'
                     CHECK(execution_mode IN ('interactive','headless','ci')),
    claude_session_id TEXT,
    pid              INTEGER NOT NULL,
    pid_started_at   TEXT,
    hostname         TEXT NOT NULL,
    repo_identity    TEXT NOT NULL,
    worktree_id      TEXT NOT NULL,
    worktree_path    TEXT NOT NULL,
    task_id          TEXT,
    plan_authority   TEXT,
    declared_scope   TEXT NOT NULL DEFAULT '[]',
    protocol_version INTEGER NOT NULL DEFAULT 1,
    started_at       TEXT NOT NULL,
    last_heartbeat   TEXT NOT NULL,
    heartbeat_ttl_s  INTEGER NOT NULL DEFAULT 1800,
    status           TEXT NOT NULL DEFAULT 'ACTIVE'
                     CHECK(status IN ('ACTIVE','IDLE','STALE_SUSPECT',
                                      'COMPLETED','ABANDONED','TAKEN_OVER')),
    status_reason    TEXT
);
-- One live agent per Claude session (SessionStart resume is idempotent).
CREATE UNIQUE INDEX IF NOT EXISTS idx_agents_session_live
    ON agents(claude_session_id)
    WHERE claude_session_id IS NOT NULL
      AND status IN ('ACTIVE','IDLE','STALE_SUSPECT');
CREATE INDEX IF NOT EXISTS idx_agents_live
    ON agents(status) WHERE status IN ('ACTIVE','IDLE','STALE_SUSPECT');

CREATE TABLE IF NOT EXISTS leases (
    lease_id         TEXT PRIMARY KEY,
    agent_id         TEXT NOT NULL REFERENCES agents(agent_id),
    task_id          TEXT,
    resource_type    TEXT NOT NULL CHECK(resource_type IN ('file','dir','logical','command')),
    resource_key     TEXT NOT NULL,
    resource_display TEXT NOT NULL,
    worktree_id      TEXT NOT NULL DEFAULT 'global',
    mode             TEXT NOT NULL DEFAULT 'EXCLUSIVE_WRITE'
                     CHECK(mode IN ('EXCLUSIVE_WRITE','OBSERVE','APPEND','SRSW')),
    origin           TEXT NOT NULL DEFAULT 'explicit' CHECK(origin IN ('auto','explicit','takeover')),
    intended_ops     TEXT NOT NULL DEFAULT '[]',
    acquired_at      TEXT NOT NULL,
    last_renewed_at  TEXT NOT NULL,
    ttl_seconds      INTEGER NOT NULL DEFAULT 3600,
    expiry_policy    TEXT NOT NULL DEFAULT 'stale-recoverable',
    status           TEXT NOT NULL DEFAULT 'ACTIVE'
                     CHECK(status IN ('ACTIVE','STALE','RELEASED','TAKEN_OVER')),
    superseded_by    TEXT,
    takeover_of      TEXT,
    status_reason    TEXT
);
-- Race-proof backstop: two live exclusive leases can never share an exact key.
-- Parent/child (dir vs contained file) overlap is enforced by the
-- check-and-insert pass inside BEGIN IMMEDIATE; this index is the net under it.
CREATE UNIQUE INDEX IF NOT EXISTS idx_lease_exclusive
    ON leases(worktree_id, resource_key)
    WHERE status IN ('ACTIVE','STALE') AND mode IN ('EXCLUSIVE_WRITE','SRSW');
CREATE INDEX IF NOT EXISTS idx_leases_live
    ON leases(worktree_id, status) WHERE status IN ('ACTIVE','STALE');
CREATE INDEX IF NOT EXISTS idx_leases_agent ON leases(agent_id, status);
CREATE INDEX IF NOT EXISTS idx_leases_key ON leases(resource_key, status);

CREATE TABLE IF NOT EXISTS lease_baselines (
    lease_id         TEXT NOT NULL REFERENCES leases(lease_id),
    file_key         TEXT NOT NULL,
    file_display     TEXT NOT NULL,
    baseline_sha256  TEXT,
    baseline_size    INTEGER,
    captured_at      TEXT NOT NULL,
    head_sha256      TEXT,
    PRIMARY KEY (lease_id, file_key)
);

CREATE TABLE IF NOT EXISTS write_journal (
    entry_id     INTEGER PRIMARY KEY AUTOINCREMENT,
    agent_id     TEXT NOT NULL,
    lease_id     TEXT,
    file_key     TEXT NOT NULL,
    op           TEXT NOT NULL CHECK(op IN ('create','edit','append','regenerate','delete')),
    pre_sha256   TEXT,
    post_sha256  TEXT,
    source       TEXT NOT NULL DEFAULT 'cli' CHECK(source IN ('hook','cli','guard')),
    recorded_at  TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_wj_file ON write_journal(file_key, entry_id DESC);
CREATE INDEX IF NOT EXISTS idx_wj_agent ON write_journal(agent_id, entry_id DESC);

CREATE TABLE IF NOT EXISTS conflicts (
    conflict_id      TEXT PRIMARY KEY,
    resource_key     TEXT NOT NULL,
    resource_display TEXT NOT NULL,
    detected_by      TEXT NOT NULL,
    apparent_owner   TEXT,
    related_tasks    TEXT NOT NULL DEFAULT '[]',
    conflict_type    TEXT NOT NULL CHECK(conflict_type IN
                     ('lease-denied','baseline-drift','unknown-change','overlap',
                      'takeover-contested','generator-drift','doctor-detected')),
    baseline_sha256  TEXT,
    current_sha256   TEXT,
    attempted_op     TEXT,
    classification   TEXT,
    safe_action      TEXT NOT NULL,
    resolution_state TEXT NOT NULL DEFAULT 'OPEN'
                     CHECK(resolution_state IN ('OPEN','ACKNOWLEDGED','RESOLVED','WONT_FIX')),
    resolved_by      TEXT,
    resolution_note  TEXT,
    detected_at      TEXT NOT NULL,
    resolved_at      TEXT
);
CREATE INDEX IF NOT EXISTS idx_conflicts_open
    ON conflicts(resolution_state) WHERE resolution_state = 'OPEN';

CREATE TABLE IF NOT EXISTS coordination_events (
    event_id       INTEGER PRIMARY KEY AUTOINCREMENT,
    entity_type    TEXT NOT NULL CHECK(entity_type IN
                   ('agent','lease','conflict','takeover','doctor','generator','system')),
    entity_id      TEXT NOT NULL,
    from_status    TEXT,
    to_status      TEXT,
    actor_agent_id TEXT,
    verb           TEXT NOT NULL,
    detail         TEXT,
    occurred_at    TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_ce_entity ON coordination_events(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_ce_verb ON coordination_events(verb, event_id DESC);

CREATE TABLE IF NOT EXISTS quarantined_rows (
    qid            INTEGER PRIMARY KEY AUTOINCREMENT,
    source_table   TEXT NOT NULL,
    row_json       TEXT NOT NULL,
    reason         TEXT NOT NULL,
    quarantined_at TEXT NOT NULL
);
