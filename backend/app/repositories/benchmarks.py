import sqlite3
from datetime import datetime, timezone

def _row(r):
    d = dict(r)
    d["enabled"] = bool(d["enabled"])
    return d

def list_all(conn):
    return [_row(r) for r in conn.execute("SELECT * FROM rate_benchmarks ORDER BY id").fetchall()]

def get(conn, bid):
    row = conn.execute("SELECT * FROM rate_benchmarks WHERE id=?", (bid,)).fetchone()
    return _row(row) if row else None

def insert(conn, name, lpr, spread_bp):
    now = datetime.now(timezone.utc).isoformat()
    cur = conn.execute(
        "INSERT INTO rate_benchmarks(name,lpr,spread_bp,enabled,created_at,updated_at) VALUES (?,?,?,1,?,?)",
        (name, lpr, spread_bp, now, now))
    conn.commit()
    return int(cur.lastrowid)

def update(conn, bid, name, lpr, spread_bp):
    now = datetime.now(timezone.utc).isoformat()
    cur = conn.execute(
        "UPDATE rate_benchmarks SET name=?, lpr=?, spread_bp=?, updated_at=? WHERE id=?",
        (name, lpr, spread_bp, now, bid))
    conn.commit()
    return cur.rowcount

def set_enabled(conn, bid, enabled):
    now = datetime.now(timezone.utc).isoformat()
    cur = conn.execute(
        "UPDATE rate_benchmarks SET enabled=?, updated_at=? WHERE id=?",
        (1 if enabled else 0, now, bid))
    conn.commit()
    return cur.rowcount
