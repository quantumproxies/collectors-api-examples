"""Run any collector from the command line.

    python3 run_collector.py web_search --input '{"query":"proxy api","country":"us"}'
    python3 run_collector.py indeed_jobs --input @jobs.json --csv jobs.csv
    python3 run_collector.py site_contacts --input '{"domains":["stripe.com"]}' --async
"""
from __future__ import annotations

import argparse
import json
import pathlib
import sys

from qdcollectors import run, run_csv, start


def load_input(raw: str) -> dict:
    if raw.startswith("@"):
        return json.loads(pathlib.Path(raw[1:]).read_text(encoding="utf-8"))
    return json.loads(raw)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("slug")
    ap.add_argument("--input", required=True, help="JSON, or @file.json")
    ap.add_argument("--async", dest="force_async", action="store_true")
    ap.add_argument("--csv", default=None, metavar="FILE")
    ap.add_argument("--json", default=None, metavar="FILE")
    args = ap.parse_args()

    payload = load_input(args.input)

    if args.force_async:
        queued = start(args.slug, payload, force_async=True)
        print(json.dumps(queued, indent=2))
        return

    result = run(args.slug, payload)
    rows = result.get("results") or []
    cost = (result.get("usage") or {}).get("cost_usd")

    print(f"{result.get('status')}: {len(rows)} rows"
          f"{' (partial)' if result.get('partial') else ''}"
          f"  cost ${cost}", file=sys.stderr)
    for note in result.get("notes") or []:
        print(f"  note: {note}", file=sys.stderr)

    if args.csv:
        pathlib.Path(args.csv).write_text(run_csv(result["run_id"]), encoding="utf-8")
        print(f"wrote {args.csv}", file=sys.stderr)
    elif args.json:
        pathlib.Path(args.json).write_text(json.dumps(rows, indent=1, ensure_ascii=False),
                                           encoding="utf-8")
        print(f"wrote {args.json}", file=sys.stderr)
    else:
        print(json.dumps(rows[:20], indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
