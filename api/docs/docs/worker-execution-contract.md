# Worker Execution Contract v1

## Step 1

Receive job_id from Redis queue.

## Step 2

Open short database transaction.

## Step 3

Lock job row and verify status is queued.

## Step 4

Atomically transition:

- status → processing
- claimed_at → now
- owned_by → worker id
- lease_version += 1

## Step 5

Commit transaction.

## Step 6

Read current lease_version into worker memory.

## Step 7

Execute job logic outside database transaction.

## Step 8

Attempt final update only if lease_version still matches:

- status → done
- result persisted
- updated_at refreshed

## Step 9

If lease_version mismatch occurs, discard stale result.
