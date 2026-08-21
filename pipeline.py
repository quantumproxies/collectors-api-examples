"""Chain collectors: find businesses, then enrich them with contact details.

    google_maps_places   query + location  ->  places (name, phone, website, rating)
    site_contacts        those domains     ->  emails, phones, socials, contact pages

Two calls, one CSV, and no HTML parsing anywhere in your codebase.

If you want both in a single call, `local_business_leads` does exactly this
server-side at $0.01 a lead — see https://quanticdata.io/collectors/lead-scraper-api/.
The two-step version below is cheaper when many places share a domain, and lets
you filter between the steps.

    python3 pipeline.py "dental clinics" "Austin, Texas" --max 40
"""
from __future__ import annotations

import argparse
import csv
from urllib.parse import urlparse

from qdcollectors import run


def domain_of(url: str | None) -> str | None:
    if not url:
        return None
    host = urlparse(url if "://" in url else f"https://{url}").netloc.lower()
    host = host[4:] if host.startswith("www.") else host
    return host or None


def flatten(value) -> str:
    """emails/phones are string[]; socials is an object of platform -> url."""
    if isinstance(value, dict):
        return "; ".join(f"{k}={v}" for k, v in value.items() if v)
    if isinstance(value, list):
        return "; ".join(str(v) for v in value)
    return str(value or "")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("query")
    ap.add_argument("location")
    ap.add_argument("--country", default="us")
    ap.add_argument("--max", type=int, default=40)
    ap.add_argument("--out", default="leads.csv")
    args = ap.parse_args()

    places = run("google_maps_places", {
        "query": args.query,
        "location": args.location,
        "country": args.country,
        "max_results": args.max,
    }).get("results") or []
    print(f"{len(places)} places")

    by_domain: dict[str, dict] = {}
    for place in places:
        d = domain_of(place.get("website"))
        if d:
            by_domain.setdefault(d, place)
    domains = list(by_domain)
    print(f"{len(domains)} distinct domains — enriching")

    contacts = run("site_contacts", {
        "domains": domains,
        "max_pages": 5,
        "max_results": len(domains),
    }).get("results") or []
    found = {c.get("domain"): c for c in contacts}

    with open(args.out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["name", "domain", "phone", "address", "rating", "reviews",
                    "emails", "site_phones", "socials", "contact_pages"])
        for d in domains:
            place, contact = by_domain[d], found.get(d, {})
            w.writerow([
                place.get("name"), d, place.get("phone"), place.get("address"),
                place.get("rating"), place.get("reviews"),
                flatten(contact.get("emails")),
                flatten(contact.get("phones")),
                flatten(contact.get("socials")),
                flatten(contact.get("contact_pages")),
            ])

    with_email = sum(1 for d in domains if found.get(d, {}).get("emails"))
    print(f"\n{with_email}/{len(domains)} rows carry at least one email → {args.out}")


if __name__ == "__main__":
    main()
