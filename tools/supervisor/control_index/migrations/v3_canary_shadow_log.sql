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
