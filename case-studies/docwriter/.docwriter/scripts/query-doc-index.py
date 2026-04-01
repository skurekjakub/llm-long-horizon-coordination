#!/usr/bin/env python3
"""Query doc-index.json with targeted filters.

Usage:
  python3 query-doc-index.py --cluster Forms           # pages in Forms cluster
  python3 query-doc-index.py --path '*/forms/*'        # glob match on path
  python3 query-doc-index.py --title membership         # case-insensitive title search
  python3 query-doc-index.py --has-crossrefs            # pages with cross-refs
  python3 query-doc-index.py --refs-to some/page.md     # pages referencing that path
  python3 query-doc-index.py --limit 20                 # cap results
  python3 query-doc-index.py --list-clusters            # list all topic clusters

Outputs matching page entries as JSON array to stdout.
Prints match count to stderr.
"""

import argparse
import fnmatch
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from db_utils import load_json, output_json, summary


def matches(page, args):
    if args.cluster:
        clusters = page.get("topicClusters", [])
        if not any(args.cluster.lower() in c.lower() for c in clusters):
            return False
    if args.path:
        if not fnmatch.fnmatch(page.get("path", ""), args.path):
            return False
    if args.title:
        title = page.get("title", "")
        if args.title.lower() not in title.lower():
            return False
    if args.has_crossrefs:
        if len(page.get("crossRefs", [])) == 0:
            return False
    if args.refs_to:
        refs = page.get("crossRefs", [])
        target = args.refs_to.lower()
        if not any(target in str(r).lower() for r in refs):
            return False
    if args.front_matter_key:
        fm = page.get("frontMatter", {})
        key = args.front_matter_key
        if "=" in key:
            k, v = key.split("=", 1)
            fm_val = str(fm.get(k, ""))
            if v.lower() not in fm_val.lower():
                return False
        else:
            if key not in fm:
                return False
    return True


def main():
    parser = argparse.ArgumentParser(description="Query doc-index.json")
    parser.add_argument("--cluster", help="Filter by topic cluster name (substring match)")
    parser.add_argument("--path", help="Glob pattern to match page paths")
    parser.add_argument("--title", help="Case-insensitive substring match on title")
    parser.add_argument("--has-crossrefs", action="store_true", help="Only pages with cross-refs")
    parser.add_argument("--refs-to", help="Pages with cross-refs pointing to this path")
    parser.add_argument("--front-matter-key", help="Filter by front matter key or key=value")
    parser.add_argument("--limit", type=int, help="Max number of results")
    parser.add_argument("--list-clusters", action="store_true", help="List all topic clusters with counts")
    parser.add_argument("--stats", action="store_true", help="Show index statistics only")
    args = parser.parse_args()

    data = load_json("doc-index.json")
    if data is None:
        sys.exit(1)

    pages = data.get("pages", [])

    if args.stats:
        refs = [len(p.get("crossRefs", [])) for p in pages]
        clusters = set()
        for p in pages:
            clusters.update(p.get("topicClusters", []))
        output_json({
            "totalPages": len(pages),
            "pagesWithCrossRefs": sum(1 for r in refs if r > 0),
            "totalCrossRefs": sum(refs),
            "maxCrossRefs": max(refs) if refs else 0,
            "topicClusters": len(clusters),
            "generatedAt": data.get("generatedAt", "unknown"),
        })
        return

    if args.list_clusters:
        cluster_counts = {}
        for page in pages:
            for c in page.get("topicClusters", []):
                cluster_counts[c] = cluster_counts.get(c, 0) + 1
        output_json(dict(sorted(cluster_counts.items(), key=lambda x: -x[1])))
        summary({"clusters": len(cluster_counts), "totalPages": len(pages)})
        return

    results = [p for p in pages if matches(p, args)]
    if args.limit:
        results = results[:args.limit]

    output_json(results)
    summary({"matched": len(results), "total": len(pages)})


if __name__ == "__main__":
    main()
