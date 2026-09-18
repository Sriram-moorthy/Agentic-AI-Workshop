"""Lab 3 — two runs booking the same slot; one wins cleanly.

TODO: write these tests yourself. Delete the skip line when you start.

1. test_two_workers_two_runs_one_slot
   Two students who are both eligible for TCS (22IT017 and 22CS045) each get a thread and a queued run.
   Each run applies to drive 2 and books slot 3 (build the model turns with PositionalMock).
   Use two RunStore and two PlacementDb connections on the same files (the db_files fixture), and one Worker
   per connection. Assert: both runs SUCCEED (losing a race is not a crash), exactly one book_interview_slot
   result is "booked", the other is the "slot_taken" error, and slot 3 holds exactly one student.

2. test_truly_concurrent_claims_have_one_winner
   Both students apply to drive 2. Read slot 3's version once. Start 8 threads, each with its OWN
   PlacementDb connection, held at a threading.Barrier, then all call claim_slot(3, student, version).
   Assert exactly one True, seven False, and the version went up by exactly one.
"""
import threading

from app.memory import RunStore
from app.placement_db import PlacementDb
from app.providers import ModelTurn, PositionalMock, ToolCall
from app.worker import Worker


class StudentPositionalMock(PositionalMock):
    def generate(self, system: str, contents: list[dict], tools: list) -> ModelTurn:
        sid = "22IT017" if "22IT017" in system else "22CS045"
        self.turns = [
            ModelTurn(text=None, tool_calls=[ToolCall("apply_to_drive", {"student_id": sid, "drive_id": 2})]),
            ModelTurn(text=None, tool_calls=[ToolCall("book_interview_slot", {"student_id": sid, "slot_id": 3})]),
            ModelTurn(text="All set!"),
        ]
        return super().generate(system, contents, tools)


def test_two_workers_two_runs_one_slot(db_files, clock):
    agent_path, placement_path = db_files
    store_a, store_b = RunStore(agent_path, clock), RunStore(agent_path, clock)
    place_a, place_b = PlacementDb(placement_path), PlacementDb(placement_path)

    thread_1 = store_a.create_thread("22IT017")
    run_1_id = store_a.enqueue(thread_1, "Apply to TCS and book slot 3", "mock")

    thread_2 = store_b.create_thread("22CS045")
    run_2_id = store_b.enqueue(thread_2, "Apply to TCS and book slot 3", "mock")

    worker_a = Worker(store_a, place_a, StudentPositionalMock([]), worker_id="worker-A")
    worker_b = Worker(store_b, place_b, StudentPositionalMock([]), worker_id="worker-B")

    t1 = threading.Thread(target=worker_a.run_until_idle)
    t2 = threading.Thread(target=worker_b.run_until_idle)
    t1.start()
    t2.start()
    t1.join()
    t2.join()

    run_1 = store_a.get_run(run_1_id)
    run_2 = store_b.get_run(run_2_id)

    assert run_1["status"] == "succeeded"
    assert run_2["status"] == "succeeded"

    res_1 = next(s["result"] for s in run_1["steps"] if s.get("tool_name") == "book_interview_slot")
    res_2 = next(s["result"] for s in run_2["steps"] if s.get("tool_name") == "book_interview_slot")

    results = [res_1, res_2]
    assert sum(1 for r in results if r.get("status") == "booked") == 1
    assert sum(1 for r in results if r.get("error") == "slot_taken") == 1

    slot = place_a.get_slot(3)
    assert slot.student_id is not None
    assert slot.student_id in (1, 2)


def test_truly_concurrent_claims_have_one_winner(db_files):
    _, placement_path = db_files
    place = PlacementDb(placement_path)

    place.create_application(1, 2)
    place.create_application(2, 2)

    version = place.slot_version(3)
    barrier = threading.Barrier(8)
    results = []
    lock = threading.Lock()

    def claim(student_id):
        conn = PlacementDb(placement_path)
        barrier.wait()
        res = conn.claim_slot(3, student_id, version)
        with lock:
            results.append(res)

    threads = [
        threading.Thread(target=claim, args=(1 if i % 2 == 0 else 2,))
        for i in range(8)
    ]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    assert results.count(True) == 1
    assert results.count(False) == 7
    assert place.slot_version(3) == version + 1
