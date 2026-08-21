"""Thin client for the QuanticData Collectors API."""
from __future__ import annotations

import os
import time
from typing import Any

import requests

BASE = "https://api.quanticdata.io/v1"
_session = requests.Session()


def _auth() -> dict[str, str]:
    key = os.environ.get("QUANTICDATA_API_KEY")
    if not key:
        raise SystemExit("set QUANTICDATA_API_KEY — https://app.quanticdata.io/register")
    return {"Authorization": f"Bearer {key}"}


def _unwrap(r: requests.Response, what: str) -> dict:
    data = r.json()
    if data.get("type") == "error" or not r.ok:
        raise RuntimeError(f"{what} failed ({r.status_code}): {data.get('message')}")
    return data.get("payload", {})


def catalog() -> dict:
    """GET the full catalogue: collectors[] + billing. Free."""
    r = _session.get(f"{BASE}/scraper/collectors", headers=_auth(), timeout=60)
    return _unwrap(r, "catalog")


def start(slug: str, payload: dict[str, Any], force_async: bool = False) -> dict:
    """POST a run. Returns the finished run (sync) or {run_id, status: queued}."""
    body = dict(payload)
    if force_async:
        body["async"] = True
    r = _session.post(f"{BASE}/scraper/collectors/{slug}/run", json=body,
                      headers=_auth(), timeout=180)
    return _unwrap(r, f"run {slug}")


def run_status(run_id: str) -> dict:
    r = _session.get(f"{BASE}/scraper/collectors/runs/{run_id}", headers=_auth(), timeout=60)
    return _unwrap(r, "run status")


def run_csv(run_id: str) -> str:
    """The same run streamed as CSV, columns following the output schema."""
    r = _session.get(f"{BASE}/scraper/collectors/runs/{run_id}", params={"format": "csv"},
                     headers=_auth(), timeout=120)
    if not r.ok:
        raise RuntimeError(f"csv export failed ({r.status_code})")
    return r.text


def run(slug: str, payload: dict[str, Any], poll_every: float = 3.0, timeout: float = 900) -> dict:
    """Run a collector and always come back with the finished run, sync or async."""
    started = start(slug, payload)
    if started.get("status") == "done" or started.get("results") is not None:
        return started

    run_id = started["run_id"]
    deadline = time.time() + timeout
    while time.time() < deadline:
        time.sleep(poll_every)
        current = run_status(run_id)
        if current.get("status") in ("done", "failed", "cancelled"):
            return current
    raise TimeoutError(f"run {run_id} still going after {timeout}s")
