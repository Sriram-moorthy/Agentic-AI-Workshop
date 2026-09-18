# Lab 4 — crash drill

## Before idempotency
If you ran the drill before finishing Part 2 (or with `call_tool` reverted to call tools directly), paste the last lines here.

## After
Paste the output of three runs of `python -m scripts.crash_drill`.

### Run 1
```
1. queued run eaa29554
2. worker-A started
3. killed worker-A after it sent the notification but before it recorded doing so: run is 'running', leased to worker-A, 6 steps recorded
4. waiting 4 s for worker-A's lease to expire...
5. worker-B finished the run: 'succeeded' after 2 attempts

applications 1   booked slots 1   notifications 1
PASS: exactly one of each
```

### Run 2
```
1. queued run c810aa29
2. worker-A started
3. killed worker-A after it sent the notification but before it recorded doing so: run is 'running', leased to worker-A, 6 steps recorded
4. waiting 4 s for worker-A's lease to expire...
5. worker-B finished the run: 'succeeded' after 2 attempts

applications 1   booked slots 1   notifications 1
PASS: exactly one of each
```

### Run 3
```
1. queued run 2518dc9d
2. worker-A started
3. killed worker-A after it sent the notification but before it recorded doing so: run is 'running', leased to worker-A, 6 steps recorded
4. waiting 4 s for worker-A's lease to expire...
5. worker-B finished the run: 'succeeded' after 2 attempts

applications 1   booked slots 1   notifications 1
PASS: exactly one of each
```

## Explain
1. At which moment was worker-A killed, and what had and hadn't been written?
Worker-A was killed immediately after executing `notify_student` (and committing its side effect and idempotency record in `placement.db`), during the artificial delay before `store.record_tool_call` could record the tool step in `agent.db`.
- **What had been written:** In `placement.db`, the application row, the interview slot reservation, the notification row, and the idempotency table entries for `apply_to_drive`, `book_interview_slot`, and `notify_student` were all committed. In `agent.db`, the thread, user message, model turn, and tool calls for steps up to `book_interview_slot` were committed.
- **What hadn't been written:** In `agent.db`, the tool call step for `notify_student` was never recorded, and the run's final completion/success state was never updated.

2. How did worker-B know where to resume?
After worker-A's lease expired, `reap_expired()` reset the run status back to `queued`. Worker-B claimed the run and called `execute_run()`, which invoked `rebuild(store, thread_id, run_id)`. `rebuild()` reconstructed the history of recorded steps and detected that the model turn called two tools: `book_interview_slot` (which was recorded) and `notify_student` (which had no matching tool_call recorded in `agent.db`). `rebuild()` placed `notify_student` into `pending` with its step sequence number. Worker-B therefore knew to resume from that exact pending tool call.

3. Which line of code stopped the second notification?
In `app/placement_db.py`, inside `PlacementDb.once()`:
```python
row = conn.execute("SELECT result FROM idempotency WHERE key = ?", (key,)).fetchone()
if row is not None:
    return json.loads(row["result"]), False
```
Because the idempotency key was deterministically recomputed as SHA-256 of `canonical_json([run_id, step_seq, tool_name, args])`, Worker-B generated the identical key that Worker-A had committed to `placement.db`. When `once()` found that key already present, it returned the stored result directly and skipped executing the side effect.
