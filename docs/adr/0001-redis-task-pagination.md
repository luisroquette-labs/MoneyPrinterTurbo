# Redis task pagination

Status: accepted

## Context

Redis `SCAN` returns batches whose sizes can vary. The task API returns a page of records together with the total number of matching keys.

## Decision

Calculate each page slice from the number of keys before the current batch. Continue scanning until Redis returns cursor zero, even after the page is full, to obtain the total.

## Consequences

A page request scans every key for an accurate total, while fetching task hashes only for the requested page. The regression case in `test/services/test_state.py` covers batches of ten and eight tasks.
