"""Fire several long runs at once and collect them as they finish.

Anything that pages heavily — 300 job listings, 500 Zillow rows, a domain sweep
with site_contacts — is better started with `async: true` and polled, than held
open on one HTTP request.
"""
from __future__ import annotations

import time

from qdcollectors import run_status, start

JOBS = [
    ("indeed_jobs", {"query": "data engineer", "location": "New York", "max_results": 200}),
    ("linkedin_jobs", {"query": "data engineer", "location": "United States", "max_results": 200}),
    ("google_jobs", {"query": "data engineer", "location": "New York", "max_results": 100}),
]

pending = {}
for slug, payload in JOBS:
    started = start(slug, payload, force_async=True)
    pending[started["run_id"]] = slug
    print(f"queued {slug:<15} {started['run_id']}")

print()
while pending:
    time.sleep(5)
    for run_id, slug in list(pending.items()):
        current = run_status(run_id)
        status = current.get("status")
        if status in ("done", "failed", "cancelled"):
            rows = current.get("results") or []
            cost = (current.get("usage") or {}).get("cost_usd")
            print(f"{slug:<15} {status:<9} {len(rows):>4} rows  ${cost}")
            del pending[run_id]
        else:
            print(f"{slug:<15} {status} …")
