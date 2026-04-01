#!/usr/bin/env python3
"""Surgical update to task-graph.json fields.

Usage:
  python3 update-task-status.py --task-id T-003 --status written
  python3 update-task-status.py --task-id T-003 --status in-progress
  python3 update-task-status.py --task-id T-003 --field reviewCycles=2

Reads task-graph.json, updates only the specified task's field, writes back.
Prints old→new value to stderr. Exits 1 if task not found.
"""

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from db_utils import load_json, write_json, summary

VALID_STATUSES = {"planned", "in-progress", "written", "blocked", "deferred", "not-started"}


def main():
    parser = argparse.ArgumentParser(description="Update task-graph.json fields surgically")
    parser.add_argument("--task-id", required=True, help="Task ID to update")
    parser.add_argument("--status", help="New status value")
    parser.add_argument("--field", action="append", help="key=value field to set (repeatable)")
    args = parser.parse_args()

    if not args.status and not args.field:
        parser.error("Provide --status and/or --field key=value")

    data = load_json("task-graph.json")
    if data is None:
        sys.exit(1)

    tasks = data.get("tasks", [])
    target = None
    for t in tasks:
        if t.get("id") == args.task_id:
            target = t
            break

    if target is None:
        print(f"ERROR: Task '{args.task_id}' not found in task-graph.json", file=sys.stderr)
        sys.exit(1)

    changes = {}

    if args.status:
        if args.status not in VALID_STATUSES:
            print(f"ERROR: Invalid status '{args.status}'. Valid: {VALID_STATUSES}", file=sys.stderr)
            sys.exit(1)
        old_status = target.get("status", "unknown")
        target["status"] = args.status
        changes["status"] = f"{old_status} → {args.status}"

    if args.field:
        for field_spec in args.field:
            if "=" not in field_spec:
                print(f"ERROR: --field must be key=value, got '{field_spec}'", file=sys.stderr)
                sys.exit(1)
            key, value = field_spec.split("=", 1)
            # Try to parse value as JSON for numbers/booleans
            try:
                value = json.loads(value)
            except (json.JSONDecodeError, ValueError):
                pass  # keep as string
            old_val = target.get(key, "<unset>")
            target[key] = value
            changes[key] = f"{old_val} → {value}"

    write_json("task-graph.json", data)

    # Verify the write
    verify = load_json("task-graph.json")
    if verify is None:
        print("ERROR: Written file is not valid JSON!", file=sys.stderr)
        sys.exit(1)

    for k, v in changes.items():
        print(f"  {args.task_id}.{k}: {v}", file=sys.stderr)
    print(f"OK: Updated {len(changes)} field(s) in task-graph.json", file=sys.stderr)


if __name__ == "__main__":
    main()
