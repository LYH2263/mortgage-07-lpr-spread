import json
from datetime import datetime, timezone
def insert(conn, kind, payload, result, loan_id=None):
    now = datetime.now(timezone.utc).isoformat()
    cur = conn.execute("INSERT INTO calc_runs(kind,loan_id,input_json,result_json,created_at) VALUES (?,?,?,?,?)",
        (kind, loan_id, json.dumps(payload, ensure_ascii=False), json.dumps(result, ensure_ascii=False), now))
    conn.commit(); return int(cur.lastrowid)
def list_recent(conn, limit=50):
    return [dict(r) for r in conn.execute("SELECT * FROM calc_runs ORDER BY id DESC LIMIT ?", (limit,)).fetchall()]
def summarize(row):
    """从落库快照提取钉选字段；旧种子数据回退到 input_json 中的年利率。"""
    try:
        result = json.loads(row.get("result_json") or "{}")
    except (TypeError, ValueError):
        result = {}
    try:
        payload = json.loads(row.get("input_json") or "{}")
    except (TypeError, ValueError):
        payload = {}
    return {
        "annual_rate": result.get("annual_rate", payload.get("annual_rate")),
        "monthly_payment": result.get("monthly_payment"),
        "total_interest": result.get("total_interest"),
        "baseline_name": result.get("baseline_name"),
        "baseline_id": result.get("baseline_id", payload.get("baseline_id")),
    }
