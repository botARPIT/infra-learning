# Async Job Service v1 — Reliability Contract

## 1. Service Purpose

This service accepts asynchronous jobs through an API, persists them durably in the database, signals them through Redis for worker execution, and guarantees eventual transition into a terminal state (`done` or `failed`) under bounded retry and recovery policies.

The database is the durable source of truth. Redis acts only as transport for work discovery.

---

## 2. Lifecycle States

The service currently supports the following job states:

- `enqueue_failed` → Job persisted in database but queue signal failed.
- `queued` → Job available for worker claim.
- `processing` → Worker owns valid execution authority.
- `done` → Job completed successfully and result is durable.
- `failed` → Retry budget exhausted and terminal failure reached.

### Legal Transitions

- `enqueue_failed → queued`
- `queued → processing`
- `processing → done`
- `processing → queued` (retry or reaper recovery)
- `processing → failed`

Terminal states:

- `done`
- `failed`

---

## 3. Authority Model

Worker authority is enforced using three fields:

- `lease_version`
- `owned_by`
- `status`

A worker may write state only if all three match current database truth.

### Authority Predicate

A write is valid only when:

- `lease_version` matches
- `owned_by` matches worker id
- `status = processing`

This prevents stale workers from writing results after timeout recovery or ownership reassignment.

---

## 4. Retry Policy

The service uses bounded retries.

### Retry Budget

- Maximum retries: `3`

### Retry Flow

On worker failure:

- `retry_count += 1`
- `error = latest failure`
- `result = null`

If retry budget remains:

- `status = queued`
- `lease_version += 1`
- `owned_by = null`
- `claimed_at = null`

If retry budget exhausted:

- `status = failed`
- `owned_by = null`
- `claimed_at = null`

Redis enqueue occurs only after DB commit.

---

## 5. Recovery Model

A reaper process periodically repairs unfinished work.

### Timeout Rules

- Processing timeout: `15 seconds`
- Reaper interval: `5 seconds`

### Recovery Logic

If a job remains in `processing` beyond timeout:

- lock row
- set `status = queued`
- increment `lease_version`
- clear ownership
- clear claim timestamp
- commit
- enqueue again

This restores claimability while preserving stale-write safety.

---

## 6. Latency SLO

### Internal Design Upper Bound

Worst modeled recovery path:

- worker compute: `5s`
- timeout detection: `15s`
- reaper interval: `5s`

Total upper bound:

- `25 seconds`

### Initial External SLO

95% of jobs must reach terminal state within **25 seconds**.

Terminal states include:

- `done`
- `failed`

---

## 7. Reliability Interpretation

Latency SLO and success rate are independent.

A failed job may satisfy latency SLO if terminal state is reached within budget.

Failure still impacts reliability metrics separately.

---

## 8. Known Current Limitations

- Redis duplicate delivery tolerated but not suppressed.
- Queue visibility is repaired by reaper, not transactionally guaranteed.
- Historical executor identity is not preserved separately from active ownership.
- Logs are required for full failure chronology.

---

## 9. Current System Truth

- PostgreSQL = authority
- Redis = discovery
- Worker = execution
- Reaper = authority repair
