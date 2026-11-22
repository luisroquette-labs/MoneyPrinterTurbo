# Bounded task queue for anonymous requests

Status: accepted

## Context

The task endpoint may accept requests without a caller identity. When all worker slots are occupied, each additional request retains a task object and parameters in the queue. An unlimited queue can exhaust memory and increase third-party API costs.

## Decision

Keep a maximum queued-task count. Reject a new task with `TaskQueueFullError` when the queue has reached that limit.

## Consequences

Callers can receive a queue-full error during high load and retry later. The in-process limit prevents unlimited admission by one worker. With multiple Redis workers, counting and enqueuing are separate operations, so the limit can be exceeded in a race; strict cross-worker enforcement is tracked separately.
