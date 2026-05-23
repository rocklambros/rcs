"""Canonicalize Python objects to deterministic bytes for hashing or writing.

This is the single source of truth for the canonical form used by the pipeline.
Every pipeline that produces a shared artifact MUST go through these functions
(or an equivalent that documents the same invariants). The CI drift check
re-canonicalizes the output and compares hashes; any deviation is a bug.

Invariants (per SKILL.md Steps 3–5):

1. JSON keys sorted (sort_keys=True)
2. Nested lists sorted IF order is not load-bearing — caller decides; if unsure,
   wrap the list with `sort_unless_ordered(x, ordered=False)` before calling
3. Floats rounded to a fixed precision (default 6 decimals)
4. NaN -> null; Inf -> null (project convention; document in README)
5. LF line endings; no BOM; UTF-8

Adapt freely. The functions are intentionally small so the canonical form is
easy to audit and difficult to silently change.
"""
from __future__ import annotations

import hashlib
import json
import math
from typing import Any


DEFAULT_FLOAT_PRECISION = 6


def round_floats(obj: Any, precision: int = DEFAULT_FLOAT_PRECISION) -> Any:
    """Recursively round floats. NaN / Inf become None (project convention)."""
    if isinstance(obj, float):
        if math.isnan(obj) or math.isinf(obj):
            return None
        return round(obj, precision)
    if isinstance(obj, dict):
        return {k: round_floats(v, precision) for k, v in obj.items()}
    if isinstance(obj, list):
        return [round_floats(v, precision) for v in obj]
    if isinstance(obj, tuple):
        return tuple(round_floats(v, precision) for v in obj)
    return obj


def sort_unless_ordered(seq: list, *, ordered: bool) -> list:
    """Sort a list unless the caller declares its order is load-bearing.

    Use this anywhere a list's element order is incidental — e.g., tags, labels,
    set-derived lists. Do NOT use for lists whose order encodes information
    (time series, ranked results, multi-index keys).
    """
    if ordered:
        return seq
    try:
        return sorted(seq)
    except TypeError:
        # Mixed-type list — sort by repr as a stable fallback
        return sorted(seq, key=repr)


def canonicalize_json(
    obj: Any,
    *,
    indent: int = 2,
    precision: int = DEFAULT_FLOAT_PRECISION,
) -> bytes:
    """Produce canonical UTF-8 bytes for a Python object.

    For JSONL, call this on each record with indent=None and join with b"\\n".
    """
    rounded = round_floats(obj, precision)
    text = json.dumps(
        rounded,
        sort_keys=True,
        ensure_ascii=False,
        indent=indent,
        separators=(",", ": ") if indent else (",", ":"),
        allow_nan=False,
    )
    return text.encode("utf-8")


def canonicalize_jsonl(records: list[Any], *, precision: int = DEFAULT_FLOAT_PRECISION) -> bytes:
    """Each record canonicalized as a one-line JSON object. Lines joined with LF.

    Caller is responsible for sorting the records on a stable key before calling.
    The function does NOT sort records — that decision is upstream because the
    stable key depends on the schema.
    """
    lines = [canonicalize_json(r, indent=None, precision=precision) for r in records]
    return b"\n".join(lines) + b"\n"


def content_hash(data: bytes) -> str:
    """SHA-256 of the canonicalized bytes, formatted as 'sha256:<hex>'."""
    h = hashlib.sha256(data).hexdigest()
    return f"sha256:{h}"


def write_artifact(path: str, data: bytes) -> str:
    """Write canonical bytes to path with LF line endings (no OS translation).

    Returns the content_hash of the written bytes.
    """
    with open(path, "wb") as f:
        f.write(data)
    return content_hash(data)


if __name__ == "__main__":
    # Smoke test — confirm canonical form is stable across runs.
    sample = {"b": 2, "a": [3, 1, 2], "c": {"y": 0.1234567, "x": float("nan")}}
    out = canonicalize_json(sample)
    print(out.decode("utf-8"))
    print(content_hash(out))
