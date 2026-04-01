#!/usr/bin/env python3
"""Query code-analysis.json with targeted filters.

Usage:
  python3 query-code-analysis.py --area 'Membership Core'  # by area name
  python3 query-code-analysis.py --area-id AREA-001         # by area ID
  python3 query-code-analysis.py --significance high         # high-significance only
  python3 query-code-analysis.py --has-breaking              # only entries with breaking changes
  python3 query-code-analysis.py --has-public-apis           # entries with public API changes
  python3 query-code-analysis.py --summary                   # area overview only

Outputs matching entries as JSON array to stdout.
Prints entry count to stderr.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from db_utils import load_json, output_json, summary


def matches(entry, args):
    if args.area:
        if args.area.lower() not in entry.get("areaName", "").lower():
            return False
    if args.area_id:
        if entry.get("areaId") != args.area_id:
            return False
    if args.significance:
        if entry.get("significance") != args.significance:
            return False
    if args.has_breaking:
        if not entry.get("breakingChanges"):
            return False
    if args.has_public_apis:
        if not entry.get("publicAPIs") and not entry.get("removedAPIs"):
            return False
    return True


def main():
    parser = argparse.ArgumentParser(description="Query code-analysis.json")
    parser.add_argument("--area", help="Substring match on area name")
    parser.add_argument("--area-id", help="Exact area ID match")
    parser.add_argument("--significance", help="Filter by significance (high, medium, low)")
    parser.add_argument("--has-breaking", action="store_true", help="Only entries with breaking changes")
    parser.add_argument("--has-public-apis", action="store_true", help="Only entries with public/removed API changes")
    parser.add_argument("--summary", action="store_true", help="Show area overview only")
    args = parser.parse_args()

    data = load_json("code-analysis.json")
    if data is None:
        sys.exit(1)

    entries = data.get("entries", [])

    if args.summary:
        areas = []
        for e in entries:
            areas.append({
                "areaId": e.get("areaId"),
                "areaName": e.get("areaName"),
                "significance": e.get("significance"),
                "publicAPIs": len(e.get("publicAPIs", [])),
                "removedAPIs": len(e.get("removedAPIs", [])),
                "breakingChanges": len(e.get("breakingChanges", [])),
            })
        output_json({
            "totalAreas": len(entries),
            "featureSummary": data.get("featureSummary", ""),
            "areas": areas,
        })
        return

    results = [e for e in entries if matches(e, args)]
    output_json(results)
    summary({"matched": len(results), "total": len(entries)})


if __name__ == "__main__":
    main()
