def init_sqlite(conn):
    cur = conn.cursor()

    # --- Week 5 tables already here ---

    # Week 6.1: persistent self-state
    cur.execute("""
    CREATE TABLE IF NOT EXISTS self_state (
        agent_id TEXT PRIMARY KEY,
        version INTEGER NOT NULL,
        created_at TEXT NOT NULL,
        last_tick_at TEXT NOT NULL,
        boot_count INTEGER NOT NULL,
        last_summary TEXT
    )
    """)

    # Week 6.1: persistent goals
    cur.execute("""
    CREATE TABLE IF NOT EXISTS goals (
        goal_id TEXT PRIMARY KEY,
        agent_id TEXT NOT NULL,
        text TEXT NOT NULL,
        priority INTEGER NOT NULL,
        status TEXT NOT NULL,  -- pending/active/done
        created_at TEXT NOT NULL,
        last_touched_at TEXT NOT NULL
    )
    """)

    # Week 6.2: health metrics per tick
    cur.execute("""
    CREATE TABLE IF NOT EXISTS health_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tick_id TEXT NOT NULL,
        metric_name TEXT NOT NULL,
        metric_value REAL NOT NULL,
        status TEXT NOT NULL,   -- OK/WARN/FAIL
        created_at TEXT NOT NULL
    )
    """)

    conn.commit()