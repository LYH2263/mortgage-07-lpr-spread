def list_all(conn, enabled_only=False):
    sql = "SELECT * FROM rate_baselines"
    if enabled_only:
        sql += " WHERE enabled = 1"
    sql += " ORDER BY id"
    return [dict(r) for r in conn.execute(sql).fetchall()]

def get(conn, bid):
    row = conn.execute("SELECT * FROM rate_baselines WHERE id=?", (bid,)).fetchone()
    return dict(row) if row else None

def insert(conn, name, lpr, spread_bps, enabled):
    cur = conn.execute(
        "INSERT INTO rate_baselines(name,lpr,spread_bps,enabled,created_at) VALUES (?,?,?,?,datetime('now'))",
        (name, lpr, spread_bps, 1 if enabled else 0))
    conn.commit()
    return get(conn, cur.lastrowid)

def update(conn, bid, fields: dict):
    cols, vals = [], []
    for k in ("name", "lpr", "spread_bps", "enabled"):
        if fields.get(k) is not None:
            cols.append(f"{k}=?")
            v = fields[k]
            vals.append(1 if v is True else (0 if v is False else v))
    if not cols:
        return get(conn, bid)
    vals.append(bid)
    conn.execute(f"UPDATE rate_baselines SET {', '.join(cols)} WHERE id=?", vals)
    conn.commit()
    return get(conn, bid)
