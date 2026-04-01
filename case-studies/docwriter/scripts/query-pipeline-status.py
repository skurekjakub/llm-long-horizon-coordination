#!/usr/bin/env python3
"""Pipeline status dashboard — reads progress.json, manifest.json, and task-graph.json.

Usage:
  python3 query-pipeline-status.py          # full dashboard
  python3 query-pipeline-status.py --tasks  # include task-level breakdown
  python3 query-pipeline-status.py --files  # include files written list

Outputs a unified status JSON to stdout.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from db_utils import load_json, output_json, summary


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Pipeline status dashboard")
    parser.add_argument("--tasks", action="store_true", help="Include per-task status")
    parser.add_argument("--files", action="store_true", help="Include files written list")
    args = parser.parse_args()

    status = {"available": [], "missing": []}

    # Progress
    progress = load_json("progress.json")
    if progress:
        status["available"].append("progress.json")
        status["progress"] = {
            "currentPass": progress.get("currentPass"),
            "passStatus": progress.get("passStatus"),
            "completedPasses": progress.get("completedPasses", []),
            "reEntryCount": progress.get("reEntryCount", 0),
        }
    else:
        status["missing"].append("progress.json")

    # Manifest
    manifest = load_json("manifest.json")
    if manifest:
        status["available"].append("manifest.json")
        files = manifest.get("files", manifest.get("written", []))
        if isinstance(files, list):
            status["manifest"] = {"filesWritten": len(files)}
            if args.files:
                status["manifest"]["fileList"] = files
        elif isinstance(manifest, dict):
            status["manifest"] = {"keys": list(manifest.keys())}
    else:
        status["missing"].append("manifest.json")

    # Task graph
    task_data = load_json("task-graph.json")
    if task_data:
        status["available"].append("task-graph.json")
        tasks = task_data.get("tasks", [])
        status_dist = {}
        for t in tasks:
            s = t.get("status", "unknown")
            status_dist[s] = status_dist.get(s, 0) + 1
        status["taskGraph"] = {
            "totalTasks": len(tasks),
            "byStatus": status_dist,
        }
        if args.tasks:
            status["taskGraph"]["tasks"] = [
                {"id": t.get("id"), "status": t.get("status"), "title": t.get("title")}
                for t in tasks
            ]
    else:
        status["missing"].append("task-graph.json")

    # Agent status files
    agents_dir = None
    try:
        from db_utils import resolve_docwriter_root
        agents_dir = resolve_docwriter_root() / "agents"
    except Exception:
        pass

    if agents_dir and agents_dir.is_dir():
        agent_statuses = {}
        for f in sorted(agents_dir.glob("*-status.json")):
            agent_data = None
            try:
                import json
                with open(f) as fh:
                    agent_data = json.load(fh)
            except Exception:
                pass
            if agent_data:
                name = f.stem.replace("-status", "")
                agent_statuses[name] = agent_data.get("status", "unknown")
        if agent_statuses:
            status["agents"] = agent_statuses

    output_json(status)
    summary({
        "available": len(status["available"]),
        "missing": len(status["missing"]),
    })


if __name__ == "__main__":
    main()
