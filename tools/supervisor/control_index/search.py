"""FTS5 full-text search for the control index."""

import sqlite3


def populate_fts(conn: sqlite3.Connection):
    """Populate the FTS5 virtual table from all entity tables."""
    conn.execute("DELETE FROM fts_operational")

    # Gaps
    conn.execute("""
        INSERT INTO fts_operational (entity_type, entity_id, content)
        SELECT 'gap', gap_id,
               COALESCE(gap_id,'') || ' ' || COALESCE(format,'') || ' ' ||
               COALESCE(capability_name,'') || ' ' || COALESCE(status,'') || ' ' ||
               COALESCE(notes,'') || ' ' || COALESCE(priority,'')
        FROM gaps
    """)

    # Failures
    conn.execute("""
        INSERT INTO fts_operational (entity_type, entity_id, content)
        SELECT 'failure', failure_id,
               COALESCE(failure_id,'') || ' ' || COALESCE(category,'') || ' ' ||
               COALESCE(root_cause,'') || ' ' || COALESCE(correction,'')
        FROM failures
    """)

    # Skills
    conn.execute("""
        INSERT INTO fts_operational (entity_type, entity_id, content)
        SELECT 'skill', skill_id,
               COALESCE(skill_id,'') || ' ' || COALESCE(command,'') || ' ' ||
               COALESCE(purpose,'') || ' ' || COALESCE(product_track,'')
        FROM skills
    """)

    # Capabilities
    conn.execute("""
        INSERT INTO fts_operational (entity_type, entity_id, content)
        SELECT 'capability', capability_id,
               COALESCE(capability_id,'') || ' ' || COALESCE(purpose,'') || ' ' ||
               COALESCE(product_track,'')
        FROM capabilities
    """)

    # Layers
    conn.execute("""
        INSERT INTO fts_operational (entity_type, entity_id, content)
        SELECT 'layer', layer_id,
               COALESCE(layer_id,'') || ' ' || COALESCE(canonical_name,'') || ' ' ||
               COALESCE(next_action,'')
        FROM layers
    """)

    # QNames
    conn.execute("""
        INSERT INTO fts_operational (entity_type, entity_id, content)
        SELECT 'qname', qname,
               COALESCE(qname,'') || ' ' || COALESCE(canonical_class,'') || ' ' ||
               COALESCE(spec_fact_ref,'') || ' ' || COALESCE(format_id,'')
        FROM qnames
    """)

    # Sprints
    conn.execute("""
        INSERT INTO fts_operational (entity_type, entity_id, content)
        SELECT 'sprint', sprint_id,
               COALESCE(sprint_id,'') || ' ' || COALESCE(declared_scope,'') || ' ' ||
               COALESCE(verdict,'')
        FROM sprints
    """)

    # Formats
    conn.execute("""
        INSERT INTO fts_operational (entity_type, entity_id, content)
        SELECT 'format', format_id,
               COALESCE(format_id,'') || ' ' || COALESCE(display_name,'') || ' ' ||
               COALESCE(family,'') || ' ' || COALESCE(mime_type,'')
        FROM formats
    """)


def search(conn: sqlite3.Connection, query: str, *,
           entity_types: list[str] | None = None,
           limit: int = 20) -> list[dict]:
    """Search the FTS5 index.

    Returns list of {entity_type, entity_id, rank, snippet}.
    """
    if entity_types:
        placeholders = ",".join("?" for _ in entity_types)
        rows = conn.execute(
            f"""SELECT entity_type, entity_id, rank,
                       snippet(fts_operational, 2, '>>>', '<<<', '...', 40) as snippet
                FROM fts_operational
                WHERE fts_operational MATCH ?
                  AND entity_type IN ({placeholders})
                ORDER BY rank
                LIMIT ?""",
            [query] + entity_types + [limit],
        ).fetchall()
    else:
        rows = conn.execute(
            """SELECT entity_type, entity_id, rank,
                      snippet(fts_operational, 2, '>>>', '<<<', '...', 40) as snippet
               FROM fts_operational
               WHERE fts_operational MATCH ?
               ORDER BY rank
               LIMIT ?""",
            (query, limit),
        ).fetchall()

    return [dict(r) for r in rows]
