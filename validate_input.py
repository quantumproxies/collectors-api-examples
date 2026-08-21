"""Check an input against the collector's published JSON Schema before you spend.

The API validates anyway — this is about catching a typo locally instead of
discovering it after a 400, and about generating a form or a config from the
same schema the dashboard uses.

    pip install jsonschema requests
    python3 validate_input.py google_maps_places '{"query":"bakeries","location":"Lyon, France"}'
"""
from __future__ import annotations

import json
import sys

from qdcollectors import catalog

try:
    from jsonschema import Draft202012Validator
except ImportError:
    raise SystemExit("pip install jsonschema")


def main() -> None:
    if len(sys.argv) != 3:
        raise SystemExit(__doc__)
    slug, raw = sys.argv[1], sys.argv[2]

    entry = next((c for c in catalog()["collectors"] if c["slug"] == slug), None)
    if not entry:
        raise SystemExit(f"unknown collector {slug!r}")

    schema = entry["input_schema"]
    payload = json.loads(raw)
    errors = sorted(Draft202012Validator(schema).iter_errors(payload), key=lambda e: e.path)

    if not errors:
        rows = payload.get("max_results", 10)
        print(f"valid. up to {rows} {entry['unit']}s "
              f"≈ ${rows * entry['price']['your_usd']:.4f}")
        return

    for err in errors:
        where = "/".join(str(p) for p in err.path) or "(root)"
        print(f"  {where}: {err.message}")
    sys.exit(1)


if __name__ == "__main__":
    main()
