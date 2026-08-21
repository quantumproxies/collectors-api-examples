"""Print the live catalogue: every collector, your price, its health.

    python3 catalog.py                  # the table
    python3 catalog.py web_search       # one collector's full schema + examples
"""
from __future__ import annotations

import json
import sys

from qdcollectors import catalog


def main() -> None:
    data = catalog()
    collectors = data.get("collectors") or []
    billing = data.get("billing") or {}

    if len(sys.argv) > 1:
        wanted = sys.argv[1]
        entry = next((c for c in collectors if c["slug"] == wanted), None)
        if not entry:
            raise SystemExit(f"unknown collector {wanted!r} — run without arguments to list them")
        print(json.dumps({
            "slug": entry["slug"], "version": entry["version"], "unit": entry["unit"],
            "price": entry["price"], "max_results": entry["max_results"],
            "input_schema": entry["input_schema"],
            "output_schema": entry["output_schema"],
            "examples": entry["examples"],
        }, indent=2))
        return

    mult = billing.get("discount_multiplier", 1)
    print(f"{len(collectors)} collectors — your tier multiplier {mult}\n")
    print(f"{'slug':<22} {'category':<14} {'unit':<9} {'$/row':>9} {'$/1k':>8}  health")
    print("-" * 78)
    for c in sorted(collectors, key=lambda c: (c["category"], c["slug"])):
        health = (c.get("health") or {}).get("status") or "?"
        print(f"{c['slug']:<22} {c['category']:<14} {c['unit']:<9} "
              f"{c['price']['your_usd']:>9.4f} {c['price']['per_1k_usd']:>8.2f}  {health}")


if __name__ == "__main__":
    main()
