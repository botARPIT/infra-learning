# Job Lifecycle Specification v1

## Purpose

Define authoritative lifecycle rules for async job execution so API, worker, and recovery logic share the same state model.

## Source of Truth

PostgreSQL is the authoritative source of job truth. Redis only transports work signals.

## Job States

### queued

Job exists durably in PostgreSQL and has been accepted for worker pickup.

### processing

A worker has atomically claimed ownership of the job and holds an active lease.

### done

Worker completed execution and persisted final result successfully.

### failed

Execution ended without meeting success condition, or retry budget exhausted.

### enqueue_failed

Job row exists but Redis enqueue did not succeed.

## Required Columns

- id
- status
- result
- error
- created_at
- updated_at
- claimed_at
- owned_by
- lease_version
- retry_count

## Ownership Rule

A worker may begin execution only after atomically changing status from queued to processing.

## Lease Rule

A processing job is considered abandoned if claimed_at exceeds lease duration.

## Retry Rule

Abandoned jobs return to queued with retry_count incremented.

## Retry Limit

If retry_count exceeds maximum allowed retries, state transitions to failed.

## Fencing Rule

Each ownership claim increments lease_version. A worker may persist final result only if lease_version matches current database value.

## Idempotency Rule

Before execution, worker must verify that status is not already done.
