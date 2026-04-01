#!/usr/bin/env python3
"""Query invariant-inventory.json with targeted filters.

Usage:
  python3 query-invariants.py                           # all invariants
  python3 query-invariants.py --domain style            # style-domain only
  python3 query-invariants.py --domain persona          # persona-domain only
  python3 query-invariants.py --applies-to tutorial     # applicable to tutorials
  python3 query-invariants.py --enforcement machine-checkable
  python3 query-invariants.py --id INV-codesamples-001  # exact match by ID
  python3 query-invariants.py --domain style --enforcement machine-checkable  # AND filters

Outputs matching invariants as JSON array to stdout.
Prints match count to stderr.
"""

import argparse
import sys
from pathlib import Path

# Allow imports from the scripts directory
sys.path.insert(0, str(Path(__file__).resolve().parent))
from db_utils import load_json, output_json, summary


def matches(inv, args):
    if args.id and inv.get("id") != args.id:
        return False
    if args.domain and inv.get("domain") != args.domain:
        return False
    if args.enforcement and inv.get("enforcement") != args.enforcement:
        return False
    if args.applies_to:
        applies = inv.get("appliesTo", [])
        if "all" not in applies and args.applies_to not in applies:
            return False
    return True


def main():
    parser = argparse.ArgumentParser(description="Query invariant-inventory.json")
    parser.add_argument("--domain", help="Filter by domain (style, jekyll, general, ...)")
    parser.add_argument("--applies-to", help="Filter by appliesTo value (tutorial, guide, ...)")
    parser.add_argument("--enforcement", help="Filter by enforcement level")
    parser.add_argument("--id", help="Exact match by invariant ID")
    parser.add_argument("--list-domains", action="store_true", help="List all domains with counts")
    args = parser.parse_args()

    data = load_json("invariant-inventory.json")
    if data is None:
        sys.exit(1)

    invariants = data.get("invariants", [])

    if args.list_domains:
        domains = {}
        for inv in invariants:
            d = inv.get("domain", "unknown")
            domains[d] = domains.get(d, 0) + 1
        output_json(domains)
        summary({"total": len(invariants), "domains": len(domains)})
        return

    results = [inv for inv in invariants if matches(inv, args)]
    output_json(results)
    summary({"matched": len(results), "total": len(invariants)})


if __name__ == "__main__":
    main()
