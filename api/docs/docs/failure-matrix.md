# Failure Matrix v1

| Failure                          | Detected By      | State Transition        |
| -------------------------------- | ---------------- | ----------------------- |
| Redis enqueue fails              | API              | queued → enqueue_failed |
| Worker crashes during processing | lease recovery   | processing → queued     |
| Lease expires beyond retry limit | recovery process | processing → failed     |
| Fence mismatch on final write    | worker           | stale result discarded  |
| Final DB write fails             | lease recovery   | processing → queued     |
| Retry limit exceeded             | recovery process | queued → failed         |
