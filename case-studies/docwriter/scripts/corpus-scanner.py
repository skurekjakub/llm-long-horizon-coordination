#!/usr/bin/env python3
"""
Corpus Scanner — indexes documentation pages in the Jekyll workspace.

Reads .docwriter/context.json for workspace path and collection config.
Produces .docwriter/doc-index.json with front matter, headings, cross-references,
and topic clusters.

Usage:
  python3 .docwriter/scripts/corpus-scanner.py              # full scan
  python3 .docwriter/scripts/corpus-scanner.py --force       # ignore cache
  python3 .docwriter/scripts/corpus-scanner.py --dry-run     # count only, no write
  python3 .docwriter/scripts/corpus-scanner.py --stats       # print stats of existing index
"""

import argparse
import json
import os
import re
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path

# ---------------------------------------------------------------------------
# Path resolution
# ---------------------------------------------------------------------------

SCRIPT_DIR = Path(__file__).resolve().parent
DOCWRITER_ROOT = SCRIPT_DIR.parent  # .docwriter/
REPO_ROOT = DOCWRITER_ROOT.parent   # repository root

CONTEXT_FILE = DOCWRITER_ROOT / "context.json"
OUTPUT_FILE = DOCWRITER_ROOT / "doc-index.json"
STATUS_FILE = DOCWRITER_ROOT / "agents" / "corpus-scanner-status.json"
MANIFEST_FILE = DOCWRITER_ROOT / "manifest.json"

# Paths excluded from indexing (always, regardless of config)
EXCLUDED_PATH_PREFIXES = [
    "changelog/",
    "changelog.",
]
EXCLUDED_PATH_CONTAINS = [
    "_release-notes/",
    "release-notes/",
]


def is_excluded(rel_path):
    """Check if a page path should be excluded from the index."""
    for prefix in EXCLUDED_PATH_PREFIXES:
        if rel_path.startswith(prefix):
            return True
    for substr in EXCLUDED_PATH_CONTAINS:
        if substr in rel_path:
            return True
    return False


# ---------------------------------------------------------------------------
# Config loading
# ---------------------------------------------------------------------------

def load_config():
    """Load workspace config from context.json. Returns (workspace_path, collections)."""
    if not CONTEXT_FILE.exists():
        print(f"ERROR: {CONTEXT_FILE} not found", file=sys.stderr)
        sys.exit(1)

    with open(CONTEXT_FILE, encoding="utf-8") as f:
        ctx = json.load(f)

    docs = ctx.get("docs", {})
    workspace_path = docs.get("workspacePath", "./src/_documentation")

    # Resolve workspace path relative to repo root
    ws = (REPO_ROOT / workspace_path).resolve()
    if not ws.exists():
        print(f"ERROR: Workspace path not found: {ws}", file=sys.stderr)
        sys.exit(1)

    # Parse collections — handle freeform strings with parenthetical notes
    raw_collections = docs.get("contentCollections", [])
    collections = []
    for entry in raw_collections:
        # Extract the actual path/name before any parenthetical
        name = entry.split("(")[0].strip().strip("./").strip("/")
        if name.startswith("_"):
            name = name  # keep the underscore for Jekyll collections
        if name:
            collections.append(name)

    if not collections:
        # Default: scan everything under the workspace
        collections = ["_documentation"]

    return ws, collections


# ---------------------------------------------------------------------------
# Front-matter parser (stdlib only — no PyYAML dependency)
# ---------------------------------------------------------------------------

def parse_front_matter(text):
    """Parse YAML front matter from markdown text. Returns (dict, body_text)."""
    fm = {}
    body = text
    stripped = text.lstrip()
    if not stripped.startswith("---"):
        return fm, body

    first_sep = stripped.index("---")
    rest = stripped[first_sep + 3:]
    second_sep = rest.find("\n---")
    if second_sep == -1:
        return fm, body

    fm_block = rest[:second_sep].strip()
    body = rest[second_sep + 4:]

    lines = fm_block.split("\n")
    current_key = None

    for line in lines:
        raw = line
        stripped_line = line.strip()
        if not stripped_line or stripped_line.startswith("#"):
            continue

        leading_spaces = len(raw) - len(raw.lstrip())

        # List item continuation
        if stripped_line.startswith("- ") and current_key is not None:
            if current_key not in fm:
                fm[current_key] = []
            if not isinstance(fm[current_key], list):
                fm[current_key] = []
            item_val = stripped_line[2:].strip().strip("'\"")
            fm[current_key].append(item_val)
            continue

        colon_idx = stripped_line.find(":")
        if colon_idx > 0:
            key = stripped_line[:colon_idx].strip()
            value = stripped_line[colon_idx + 1:].strip()

            # Skip deeply nested sub-keys
            if leading_spaces > 8 and current_key:
                continue

            current_key = key

            if value.startswith("[") and value.endswith("]"):
                inner = value[1:-1]
                items = [v.strip().strip("'\"") for v in inner.split(",") if v.strip()]
                fm[key] = items
            elif value in ("", "|", ">"):
                if key not in fm or not isinstance(fm.get(key), list):
                    fm[key] = ""
            else:
                fm[key] = value.strip("'\"")

    return fm, body


# ---------------------------------------------------------------------------
# Heading extractor
# ---------------------------------------------------------------------------

def extract_headings(body):
    """Extract h2 and h3 headings from markdown body."""
    headings = []
    for line in body.split("\n"):
        stripped = line.strip()
        if stripped.startswith("## ") and not stripped.startswith("### "):
            heading = stripped[3:].strip().rstrip("#").strip()
            heading = re.sub(r'[*_`]', '', heading)
            heading = re.sub(r'\{%.*?%\}', '', heading).strip()
            if heading:
                headings.append(heading)
        elif stripped.startswith("### "):
            heading = stripped[4:].strip().rstrip("#").strip()
            heading = re.sub(r'[*_`]', '', heading)
            heading = re.sub(r'\{%.*?%\}', '', heading).strip()
            if heading:
                headings.append(heading)
    return headings


# ---------------------------------------------------------------------------
# Cross-reference extractor
# ---------------------------------------------------------------------------

def extract_cross_refs(body):
    """Extract internal links, page_link refs, include refs."""
    outgoing = set()
    includes = set()

    # {% page_link IDENTIFIER ... %}
    for m in re.finditer(r'\{%\s*page_link\s+(\S+)', body):
        ident = m.group(1).strip('"\'')
        if ident:
            outgoing.add(ident)

    # {% link ... %}
    for m in re.finditer(r'\{%\s*link\s+([^\s%}]+)', body):
        ref = m.group(1).strip("'\"")
        if ref:
            outgoing.add(ref)

    # Standard markdown links to internal paths
    for m in re.finditer(r'\[([^\]]*)\]\((/[^)]+)\)', body):
        link_target = m.group(2)
        if not link_target.startswith("http"):
            outgoing.add(link_target)

    # {% include ... %} or {% render ... %}
    for m in re.finditer(r'\{%\s*(?:include|render)\s+([^\s%}]+)', body):
        ref = m.group(1).strip("'\"")
        if ref and not ref.startswith("{"):
            includes.add(ref)

    return sorted(outgoing), sorted(includes)


# ---------------------------------------------------------------------------
# Topic cluster inference
# ---------------------------------------------------------------------------

def humanize_dir_name(name):
    """Convert a kebab-case directory name to a readable cluster name.
    
    Examples:
      'ci-cd' → 'Ci Cd'
      'digital-marketing-setup' → 'Digital Marketing Setup'
    """
    return name.replace("-", " ").replace("_", " ").title()


def infer_topic_cluster(rel_path, fm):
    """Infer topic cluster dynamically from directory structure.
    
    Strategy:
    - Top-level files → use filename as cluster name
    - Files nested 2+ levels → use the level-2 directory (the 'topic' dir) as cluster
    - e.g., developers-and-admins/configuration/... → 'Configuration'
    - e.g., business-users/content-hub/... → 'Content Hub'
    """
    parts = Path(rel_path).parts

    # Top-level files (no directory)
    if len(parts) == 1:
        stem = parts[0].replace(".md", "")
        return humanize_dir_name(stem)

    # Files directly under a top-level dir (e.g., security-advisories/page.md)
    # or deeper (e.g., developers-and-admins/configuration/page.md)
    if len(parts) >= 3:
        # Use level-2 directory as the topic cluster
        return humanize_dir_name(parts[1])
    
    if len(parts) == 2:
        # Could be a section index (developers-and-admins/installation.md)
        # or a direct child (security-advisories/advisory-1.md)
        # Use the parent directory as cluster
        return humanize_dir_name(parts[0])

    return "General"


# ---------------------------------------------------------------------------
# Main scanner
# ---------------------------------------------------------------------------

def scan_workspace(workspace_root, collections):
    """Scan all markdown files in configured collections. Returns doc_index dict."""
    # Collect (filepath, collection_dir) tuples so we can relativize correctly
    file_entries = []

    for collection in collections:
        collection_dir = workspace_root / collection
        if collection_dir.is_dir():
            for f in sorted(collection_dir.rglob("*.md")):
                file_entries.append((f, collection_dir))
        else:
            print(f"  WARN: Collection directory not found: {collection_dir}", file=sys.stderr)

    # Also grab top-level .md files in workspace root
    seen_paths = {f for f, _ in file_entries}
    for f in sorted(workspace_root.glob("*.md")):
        if f not in seen_paths:
            file_entries.append((f, workspace_root))

    total = len(file_entries)
    print(f"Found {total} markdown files across {len(collections)} collection(s).", file=sys.stderr)

    pages = []
    identifier_to_path = {}
    path_to_outgoing = {}
    excluded_count = 0

    for idx, (filepath, base_dir) in enumerate(file_entries):
        # Paths are relative to the collection dir (not workspace root)
        # This gives paths like 'developers-and-admins/configuration/...' 
        # instead of '_documentation/developers-and-admins/configuration/...'
        rel_path = str(filepath.relative_to(base_dir))

        if is_excluded(rel_path):
            excluded_count += 1
            continue

        if idx % 200 == 0 and idx > 0:
            print(f"  Processing {idx}/{total}...", file=sys.stderr)

        try:
            text = filepath.read_text(encoding="utf-8", errors="replace")
        except Exception as e:
            print(f"  WARN: Could not read {rel_path}: {e}", file=sys.stderr)
            continue

        fm, body = parse_front_matter(text)

        # Title
        title = fm.get("title", "")
        if isinstance(title, list):
            title = title[0] if title else ""
        if not title:
            title = filepath.stem.replace("-", " ").replace("_", " ").title()

        # Headings and cross-refs
        headings = extract_headings(body)
        outgoing_refs, include_refs = extract_cross_refs(body)

        # Topic cluster
        topic_clusters = [infer_topic_cluster(rel_path, fm)]

        # Identifier (Kentico-specific)
        identifier = fm.get("identifier", "")
        if isinstance(identifier, list):
            identifier = identifier[0] if identifier else ""
        if identifier:
            identifier_to_path[str(identifier)] = rel_path

        path_to_outgoing[rel_path] = outgoing_refs

        # Build page entry — consistent schema (v2 format)
        page_entry = {
            "path": rel_path,
            "title": str(title),
            "headings": headings,
            "frontMatter": {k: v for k, v in fm.items()
                           if k in ("title", "description", "persona", "personas",
                                    "layout", "permalink", "identifier",
                                    "classification", "product_version",
                                    "order", "searchable", "related_pages")},
            "topicClusters": topic_clusters,
            "crossRefs": outgoing_refs,
        }

        pages.append(page_entry)

    print(f"Indexed {len(pages)} pages ({excluded_count} changelog/release-notes excluded).",
          file=sys.stderr)

    # Resolve identifier-based crossRefs to file paths where possible
    resolved_count = 0
    for page in pages:
        resolved_refs = []
        for ref in page["crossRefs"]:
            target_path = identifier_to_path.get(ref)
            if target_path:
                resolved_refs.append(target_path)
                resolved_count += 1
            else:
                resolved_refs.append(ref)  # keep unresolved as-is
        page["crossRefs"] = sorted(set(resolved_refs))

    total_refs_raw = sum(len(v) for v in path_to_outgoing.values())
    print(f"Resolved {resolved_count}/{total_refs_raw} identifier-based cross-refs to paths.",
          file=sys.stderr)

    # Build incoming refs (reverse index)
    path_to_incoming = defaultdict(set)
    for src_path, out_refs in path_to_outgoing.items():
        for ref in out_refs:
            target = identifier_to_path.get(ref, ref)
            if target != src_path:
                path_to_incoming[target].add(src_path)

    # Build topic clusters summary
    cluster_pages = defaultdict(list)
    for page in pages:
        for c in page["topicClusters"]:
            cluster_pages[c].append(page["path"])

    topic_clusters = []
    for name in sorted(cluster_pages.keys()):
        paths = sorted(cluster_pages[name])
        topic_clusters.append({
            "name": name,
            "pageCount": len(paths),
            "pagePaths": paths,
        })

    # Stats
    total_refs = sum(len(p["crossRefs"]) for p in pages)
    total_incoming = sum(len(v) for v in path_to_incoming.values())
    by_cluster = {c["name"]: c["pageCount"] for c in topic_clusters}

    doc_index = {
        "version": 2,
        "generatedBy": "docwriter-corpus-scanner",
        "generatedAt": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "workspace": str(workspace_root),
        "totalPages": len(pages),
        "stats": {
            "totalPages": len(pages),
            "excludedPages": excluded_count,
            "byTopicCluster": by_cluster,
            "totalCrossRefs": total_refs,
            "totalIncomingRefs": total_incoming,
        },
        "pages": pages,
        "topicClusters": topic_clusters,
    }

    return doc_index


# ---------------------------------------------------------------------------
# Freshness check
# ---------------------------------------------------------------------------

def is_cache_fresh(workspace_root, collections, force=False):
    """Check if existing doc-index.json is fresh enough to skip re-scan."""
    if force:
        return False
    if not OUTPUT_FILE.exists():
        return False

    try:
        with open(OUTPUT_FILE, encoding="utf-8") as f:
            existing = json.load(f)
    except (json.JSONDecodeError, OSError):
        return False

    generated_at = existing.get("generatedAt", "")
    cached_count = existing.get("totalPages", 0)

    # Quick file count in workspace
    current_count = 0
    for collection in collections:
        cdir = workspace_root / collection
        if cdir.is_dir():
            current_count += sum(1 for f in cdir.rglob("*.md") if not is_excluded(
                str(f.relative_to(cdir))))
    for f in workspace_root.glob("*.md"):
        if not is_excluded(f.name):
            current_count += 1

    if current_count != cached_count:
        print(f"Cache stale: page count changed ({cached_count} → {current_count})", file=sys.stderr)
        return False

    # Check age (24 hour threshold)
    try:
        gen_time = datetime.fromisoformat(generated_at.replace("Z", "+00:00"))
        age = datetime.now(timezone.utc) - gen_time
        if age.total_seconds() > 86400:
            print(f"Cache stale: older than 24 hours ({age})", file=sys.stderr)
            return False
    except (ValueError, TypeError):
        return False

    print(f"Cache fresh: {cached_count} pages, generated {generated_at}", file=sys.stderr)
    return True


# ---------------------------------------------------------------------------
# Output writing
# ---------------------------------------------------------------------------

def write_output(doc_index):
    """Write doc-index.json, status file, and manifest entry."""
    DOCWRITER_ROOT.mkdir(parents=True, exist_ok=True)
    (DOCWRITER_ROOT / "agents").mkdir(parents=True, exist_ok=True)

    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(doc_index, f, indent=2, ensure_ascii=False)
        f.write("\n")
    size = os.path.getsize(OUTPUT_FILE)
    print(f"Wrote {OUTPUT_FILE} ({size:,} bytes)", file=sys.stderr)

    # Status
    status = {
        "agent": "docwriter-corpus-scanner",
        "status": "done",
        "result": "doc-index-ready",
        "totalPages": doc_index["totalPages"],
        "topicClusters": len(doc_index["topicClusters"]),
        "reusedCache": False,
        "timestamp": doc_index["generatedAt"],
    }
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2)

    # Manifest
    entry = {
        "agent": "docwriter-corpus-scanner",
        "action": f"wrote doc-index.json ({doc_index['totalPages']} pages)",
        "timestamp": doc_index["generatedAt"],
    }
    manifest = []
    if MANIFEST_FILE.exists():
        try:
            with open(MANIFEST_FILE, encoding="utf-8") as f:
                manifest = json.load(f)
        except (json.JSONDecodeError, OSError):
            manifest = []
    if isinstance(manifest, dict):
        manifest = [manifest]
    manifest.insert(0, entry)
    with open(MANIFEST_FILE, "w", encoding="utf-8") as f:
        json.dump(manifest, f, indent=2)


def write_cache_status(generated_at, total_pages, clusters):
    """Write status file for cache-hit case."""
    (DOCWRITER_ROOT / "agents").mkdir(parents=True, exist_ok=True)
    status = {
        "agent": "docwriter-corpus-scanner",
        "status": "done",
        "result": "doc-index-ready",
        "totalPages": total_pages,
        "topicClusters": clusters,
        "reusedCache": True,
        "timestamp": generated_at,
    }
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2)


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(description="Corpus scanner for docwriter pipeline")
    parser.add_argument("--force", action="store_true", help="Force full re-scan (ignore cache)")
    parser.add_argument("--dry-run", action="store_true", help="Count files only, don't write")
    parser.add_argument("--stats", action="store_true", help="Print existing index stats")
    args = parser.parse_args()

    if args.stats:
        if not OUTPUT_FILE.exists():
            print("No doc-index.json found.", file=sys.stderr)
            sys.exit(1)
        with open(OUTPUT_FILE, encoding="utf-8") as f:
            idx = json.load(f)
        stats = idx.get("stats", {})
        stats["generatedAt"] = idx.get("generatedAt", "?")
        stats["version"] = idx.get("version", "?")
        json.dump(stats, sys.stdout, indent=2)
        print()
        return

    workspace_root, collections = load_config()
    print(f"Workspace: {workspace_root}", file=sys.stderr)
    print(f"Collections: {collections}", file=sys.stderr)

    # Cache check
    if not args.force and not args.dry_run and is_cache_fresh(workspace_root, collections):
        with open(OUTPUT_FILE, encoding="utf-8") as f:
            existing = json.load(f)
        write_cache_status(
            existing.get("generatedAt", ""),
            existing.get("totalPages", 0),
            len(existing.get("topicClusters", [])),
        )
        print("Using cached index.", file=sys.stderr)
        return

    # Full scan
    doc_index = scan_workspace(workspace_root, collections)

    if args.dry_run:
        print(f"\nDry run — would write {doc_index['totalPages']} pages.", file=sys.stderr)
        json.dump(doc_index["stats"], sys.stdout, indent=2)
        print()
        return

    write_output(doc_index)

    # Summary
    clusters = sorted(doc_index["topicClusters"], key=lambda c: c["pageCount"], reverse=True)
    print(f"\n{'='*60}", file=sys.stderr)
    print(f"CORPUS SCAN COMPLETE", file=sys.stderr)
    print(f"{'='*60}", file=sys.stderr)
    print(f"Total pages indexed: {doc_index['totalPages']}", file=sys.stderr)
    print(f"Excluded (changelog): {doc_index['stats']['excludedPages']}", file=sys.stderr)
    print(f"Topic clusters: {len(clusters)}", file=sys.stderr)
    print(f"Cross-refs: {doc_index['stats']['totalCrossRefs']}", file=sys.stderr)
    print(f"\nTop clusters:", file=sys.stderr)
    for c in clusters[:15]:
        print(f"  {c['name']:40s} {c['pageCount']:>5d} pages", file=sys.stderr)


if __name__ == "__main__":
    main()
