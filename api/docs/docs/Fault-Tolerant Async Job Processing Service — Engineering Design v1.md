# Fault-Tolerant Async Job Processing Service — Engineering Design v1

## 1. Goal

Design and deploy a fault-tolerant asynchronous job processing service that:

- accepts API requests immediately
- persists authoritative job state durably
- delegates execution to background workers
- survives worker crashes without corrupting state
- rejects stale worker writes
- exposes measurable latency and queue metrics

The design intentionally prioritizes:

> **state correctness over compute efficiency**
>
> because recomputation is cheaper than corrupted truth.

---

## 2. Service SLO

Current measured target on Amazon EC2 T3:

```
p95 terminal latency < 20 seconds
under 20-job burst load
with 2 workers
5-second simulated compute per job
```

Observed cloud result:

```
avg terminal latency = 11.87s
p95 terminal latency = 18.86s
```

This satisfies current SLO.

---

## 3. Cloud Topology

Infrastructure deployed inside:

**Amazon Virtual Private Cloud**

Topology:

```
VPC: 10.0.0.0/16

Public subnet: 10.0.1.0/24

Internet Gateway attached

Route:
0.0.0.0/0 → IGW
```

Instance:

**Amazon EC2**

```
Ubuntu
t3.micro
```

Security group — Allowed inbound:

```
22  → SSH (my IP only)
8002 → API public access
```

Security group — Blocked inbound:

```
5434 → Postgres
6381 → Redis
```

---

## 4. Runtime Components

Single-node runtime:

**API server** — FastAPI

Responsibilities:

- accept jobs
- persist DB state
- enqueue job id

**Queue transport** — Redis

Responsibilities:

- transport only
- not authoritative truth

Queue semantics:

> queue is transport, DB is truth

**Durable truth** — PostgreSQL

Responsibilities:

- store lifecycle state
- store lease ownership
- reject stale writes

**Workers** — 2 workers running independently.

Responsibilities:

- dequeue
- claim authority
- compute
- complete / fail

**Reaper**

Responsibilities:

- detect stale processing jobs
- reclaim authority
- re-enqueue stale jobs

---

## 5. Job Lifecycle State Machine

Defined states:

```
queued
processing
done
failed
enqueue_failed
```

Semantics:

**queued**
Persisted and waiting for worker claim.

**processing**
Worker owns lease and authority.

**done**
Terminal successful state.

**failed**
Terminal failed state after retry cap exhausted.

**enqueue_failed**
DB persisted but queue transport failed.

---

## 6. Authority Model

Authority is enforced using:

```
lease_version
owned_by
status
```

A worker may write only if all match:

```
job_id
lease_version
worker_id
status = processing
```

This guarantees:

> stale workers cannot overwrite newer truth

---

## 7. Failure Classes Handled

**Worker crash after claim**

DB remains:

```
processing
```

Reaper detects timeout and resets:

```
queued
owned_by = null
lease_version++
```

**Duplicate queue delivery**

Safe because DB authority rejects duplicate claims.

**Stale completion**

Rejected via lease mismatch.

**Enqueue failure**

Job remains durable in DB:

```
enqueue_failed
```

No truth loss.

**Retry loop control**

Retry cap prevents infinite recomputation.

---

## 8. Metrics Exposed

Current endpoint: `/metrics`

| Metric                         | Description               |
| ------------------------------ | ------------------------- |
| `queue_depth`                  | Current queue backlog     |
| `jobs_by_state`                | DB lifecycle distribution |
| `retry_distribution`           | Retry count histogram     |
| `avg_terminal_latency_seconds` | Average terminal latency  |
| `p95_terminal_latency_seconds` | Tail latency              |

---

## 9. Burst Test Evidence

20-job burst test on cloud:

```
20 POST requests
2 workers
5 sec simulated compute
```

Observed:

```
queue_depth: 0
done: 20
avg: 11.87s
p95: 18.86s
```

**Conclusion:** current architecture satisfies target SLO.

---

## 10. Known Limits

Current design intentionally accepts:

**single-node deployment**
One EC2 hosts all components.

**Redis non-durable**
Queue loss tolerated because DB truth survives.

**no process supervisor**
tmux used for process isolation.

**Postgres local container**
No managed DB yet.

**simulated compute only**
Real CPU-heavy compute may change scaling behavior.

---

## 11. Next Phase

Remaining work:

- Prometheus scrape integration
- Grafana dashboard
- process supervision (systemd / docker compose)
- private subnet split
- managed DB separation
