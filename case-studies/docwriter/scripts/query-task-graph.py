#!/usr/bin/env python3
"""Query task-graph.json with targeted filters.

Usage:
  python3 query-task-graph.py --task-id T-003          # single task with full details
  python3 query-task-graph.py --status planned          # all planned tasks
  python3 query-task-graph.py --status written           # all written tasks
  python3 query-task-graph.py --phase 2                  # phase 2 tasks only
  python3 query-task-graph.py --type create              # only 'create' tasks
  python3 query-task-graph.py --summary                  # status distribution only

Outputs matching tasks as JSON array to stdout.
Prints task count and status distribution to stderr.
"""

import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from db_utils import load_json, output_json, summary


def matches(task, args):
    if args.task_id and task.get("id") != args.task_id:
        return False
    if args.status and task.get("status") != args.status:
        return False
    if args.phase is not None and task.get("phase") != args.phase:
        return False
    if args.type and task.get("type") != args.type:
        return False
    if args.target_page:
        target = task.get("targetPage", task.get("target", ""))
        if args.target_page.lower() not in target.lower():
            return False
    return True


def main():
    parser = argparse.ArgumentParser(description="Query task-graph.json")
    parser.add_argument("--task-id", help="Exact task ID match")
    parser.add_argument("--status", help="Filter by status (planned, in-progress, written, blocked)")
    parser.add_argument("--phase", type=int, help="Filter by phase number")
    parser.add_argument("--type", help="Filter by task type (create, modify, update)")
    parser.add_argument("--target-page", help="Substring match on target page path")
    parser.add_argument("--summary", action="store_true", help="Show status distribution only")
    args = parser.parse_args()

    data = load_json("task-graph.json")
    if data is None:
        sys.exit(1)

    tasks = data.get("tasks", [])

    if args.summary:
        status_dist = {}
        phase_dist = {}
        for t in tasks:
            s = t.get("status", "unknown")
            status_dist[s] = status_dist.get(s, 0) + 1
            p = t.get("phase", "?")
            phase_dist[str(p)] = phase_dist.get(str(p), 0) + 1
        output_json({
            "totalTasks": len(tasks),
            "byStatus": status_dist,
            "byPhase": phase_dist,
        })
        return

    results = [t for t in tasks if matches(t, args)]
    output_json(results)

    # Status distribution for stderr
    status_dist = {}
    for t in tasks:
        s = t.get("status", "unknown")
        status_dist[s] = status_dist.get(s, 0) + 1
    summary({"matched": len(results), "total": len(tasks), **status_dist})


if __name__ == "__main__":
    main()
