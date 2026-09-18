"""Stable fingerprints for side effects. Hashing, used for exactly-once."""
import hashlib  # noqa: F401
import json  # noqa: F401
import uuid
from datetime import date


def _normalize(val):
    if isinstance(val, bool):
        return val
    if isinstance(val, float):
        if val.is_integer():
            return int(val)
        return val
    if isinstance(val, dict):
        return {k: _normalize(v) for k, v in val.items()}
    if isinstance(val, (list, tuple)):
        return [_normalize(item) for item in val]
    return val


def canonical_json(value) -> str:
    return json.dumps(_normalize(value), sort_keys=True, separators=(",", ":"))


def idempotency_key(run_id: str, step_seq: int, tool_name: str, args: dict) -> str:
    raw = canonical_json([run_id, step_seq, tool_name, args])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def notification_dedupe_key(roll_no: str, message: str, day: date) -> str:
    collapsed = " ".join(message.split())
    raw = canonical_json([roll_no, collapsed, day.isoformat()])
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
