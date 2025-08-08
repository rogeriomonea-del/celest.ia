from sqlalchemy.orm import Session
from db.models_runs import Run

def record_run(db: Session, *, source: str, mode: str, route: str, ok: bool, latency_ms: int, fail_reason: str | None = None):
    r = Run(source=source, mode=mode, route=route, ok=ok, latency_ms=latency_ms, fail_reason=fail_reason)
    db.add(r)
    db.commit()

def get_http_health(db: Session) -> dict[str, dict]:
    # agrega sucesso http por fonte nas últimas ~500 execuções
    out: dict[str, dict] = {}
    q = db.query(Run).filter(Run.mode == "http").order_by(Run.id.desc()).limit(500).all()
    stats: dict[str, list[bool]] = {}
    for r in q:
        stats.setdefault(r.source, []).append(bool(r.ok))
    for source, arr in stats.items():
        if arr:
            sr = sum(1 for x in arr if x) / len(arr)
        else:
            sr = 0.0
        out[source] = {"success_rate_http": sr}
    return out
