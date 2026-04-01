"""Shared utilities for docwriter query scripts.

All scripts under .docwriter/scripts/ use this module for:
- Resolving the .docwriter/ root directory
- Loading JSON database files with error handling
- Outputting structured JSON to stdout
- Printing summary stats to stderr
"""

import json
import sys
from pathlib import Path


def resolve_docwriter_root():
    """Find the .docwriter/ directory by walking up from this script's location."""
    scripts_dir = Path(__file__).resolve().parent
    docwriter_dir = scripts_dir.parent
    if docwriter_dir.name == ".docwriter" and docwriter_dir.is_dir():
        return docwriter_dir
    # Fallback: walk up from cwd
    cwd = Path.cwd()
    for parent in [cwd] + list(cwd.parents):
        candidate = parent / ".docwriter"
        if candidate.is_dir():
            return candidate
    print("ERROR: Cannot find .docwriter/ directory", file=sys.stderr)
    sys.exit(1)


def load_json(filename, docwriter_root=None):
    """Load a JSON file from .docwriter/. Returns parsed data or exits on error."""
    if docwriter_root is None:
        docwriter_root = resolve_docwriter_root()
    filepath = docwriter_root / filename
    if not filepath.exists():
        print(f"ERROR: {filepath} not found", file=sys.stderr)
        return None
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {filepath}: {e}", file=sys.stderr)
        return None


def write_json(filename, data, docwriter_root=None):
    """Write data as formatted JSON to a file in .docwriter/."""
    if docwriter_root is None:
        docwriter_root = resolve_docwriter_root()
    filepath = docwriter_root / filename
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
        f.write("\n")


def output_json(data):
    """Write structured JSON to stdout for agent consumption."""
    json.dump(data, sys.stdout, indent=2, ensure_ascii=False)
    sys.stdout.write("\n")


def summary(stats):
    """Print a summary line to stderr. stats is a dict of label→value."""
    parts = [f"{k}: {v}" for k, v in stats.items()]
    print(" | ".join(parts), file=sys.stderr)
