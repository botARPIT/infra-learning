from sqlalchemy import func
from api.app.db import SessionLocal
from api.app.models import Job
from api.app.queues import get_queue_depth
from datetime import timedelta, datetime, timezone



def get_metrics():
    db = SessionLocal()

    try:
        window = datetime.now(timezone.utc) - timedelta(hours=1)
        queue_depth = get_queue_depth()

        state_counts = (
            db.query(Job.status, func.count())
            .group_by(Job.status)
            .all()
        )

        jobs_by_state = {status: count for status, count in state_counts}

        retry_counts = (
            db.query(Job.retry_count, func.count())
            .group_by(Job.retry_count)
            .all()
        )

        retry_distribution = {
            str(retry): count for retry, count in retry_counts
        }

        terminal_latencies = (
            db.query(
                func.extract('epoch', Job.updated_at - Job.created_at)
            )
            .filter(
                Job.status.in_(["done", "failed"]),
                Job.updated_at >= window
                    )
            .all()
        )

        values = [row[0] for row in terminal_latencies if row[0] is not None]

        avg_latency = round(sum(values) / len(values), 2) if values else 0

        p95_latency = 0
        if values:
            values.sort()
            idx = int(0.95 * len(values)) - 1
            idx = max(idx, 0)
            p95_latency = round(values[idx], 2)

        return {
            "queue_depth": queue_depth,
            "jobs_by_state": jobs_by_state,
            "retry_distribution": retry_distribution,
            "avg_terminal_latency_seconds": avg_latency,
            "p95_terminal_latency_seconds": p95_latency,
        }

    finally:
        db.close()