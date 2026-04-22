from sqlalchemy import func
from datetime import timedelta, datetime, timezone
from prometheus_client import Gauge, generate_latest, Counter

from api.app.db import SessionLocal
from api.app.models import Job
from api.app.queues import get_queue_depth

# Guages
queue_depth_gauge = Gauge(
    "queue_depth",
    "Current Redis queue depth"
)

terminal_latency_avg_gauge = Gauge(
    "terminal_latency_avg_seconds",
    "Average terminal latency"
)

terminal_latency_p95_gauge = Gauge(
    "terminal_latency_p95_seconds",
    "P95 terminal latency"
)

jobs_completed_total = Gauge(
    "jobs_completed_total",
    "Total completed jobs"
)

jobs_failed_total = Gauge(
    "jobs_failed_total",
    "Total failed jobs"
)

jobs_retried_total = Gauge(
    "jobs_retried_total",
    "Total retried jobs"
)

queue_wait_avg_gauge = Gauge(
    "queue_wait_avg_seconds",
    "Average queue wait time"
)

execution_avg_gauge = Gauge(
    "execution_avg_seconds",
    "Average execution latency"
)
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

        completed = db.query(func.count()).filter(
            Job.status == "done"
            ).scalar()
        
        failed = db.query(func.count()).filter(
            Job.status == "failed"
            ).scalar()
        
        retried = db.query(func.count()).filter(
            Job.retry_count > 0
            ).scalar()
        
        retry_distribution = {
            str(retry): count for retry, count in retry_counts
        }

        terminal_latencies = (
            db.query(
                func.extract('epoch', Job.updated_at - Job.created_at)
            )
            .filter(
                Job.status.in_(["done", "failed"]),
                Job.claimed_at.isnot(None),
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
            
        queue_wait_latencies = (
            db.query(
                func.extract('epoch', Job.claimed_at - Job.created_at)
            )
            .filter(
                Job.claimed_at.isnot(None)
            )
            .all()
        )
        
        queue_wait_values = [
            row[0] for row in queue_wait_latencies if row[0] is not None
        ]
        
        queue_wait_avg = round(
            sum(queue_wait_values) / len(queue_wait_values), 2
        ) if queue_wait_values else 0
        
        
        execution_latencies = (
            db.query(
                func.extract('epoch', Job.updated_at - Job.claimed_at)
            )
            .filter(
                Job.status.in_(["done", "failed"]),
                Job.claimed_at.isnot(None)
            )
            .all()
        )     
        
        execution_values = [
            row[0] for row in execution_latencies if row[0] is not None
        ]
        
        execution_avg = round(
            sum(execution_values) / len(execution_values), 2
        ) if execution_values else 0  

        return {
            "queue_depth": queue_depth,
            "jobs_by_state": jobs_by_state,
            "retry_distribution": retry_distribution,
            "avg_terminal_latency_seconds": avg_latency,
            "p95_terminal_latency_seconds": p95_latency,
            "jobs_completed_total": completed,
            "jobs_failed_total": failed,
            "jobs_retried_total": retried,
            "queue_wait_avg_seconds": queue_wait_avg,
            "execution_avg_seconds": execution_avg,
        }

    finally:
        db.close()
        
def get_prometheus_metrics():
    metrics = get_metrics()

    queue_depth_gauge.set(metrics["queue_depth"])
    
    terminal_latency_avg_gauge.set(
        metrics["avg_terminal_latency_seconds"]
    )
    
    terminal_latency_p95_gauge.set(
        metrics["p95_terminal_latency_seconds"]
    )
    
    jobs_completed_total.set(metrics["jobs_completed_total"])
    
    jobs_failed_total.set(metrics["jobs_failed_total"])
    
    jobs_retried_total.set(metrics["jobs_retried_total"])
    
    queue_wait_avg_gauge.set(metrics["queue_wait_avg_seconds"])
    
    execution_avg_gauge.set(metrics["execution_avg_seconds"])

    return generate_latest()