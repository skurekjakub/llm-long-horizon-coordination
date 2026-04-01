#!/usr/bin/env python3
"""
docwriter-corpus-scanner: Full scan of the documentation workspace.
Produces /workspace/.docwriter/doc-index.json with complete page index.
"""

import json
import os
import re
import sys
import yaml
from collections import defaultdict
from pathlib import Path
from datetime import datetime, timezone

# ── Configuration ──────────────────────────────────────────────────────
WORKSPACE_ROOT = Path("/workspace/src/_documentation/_documentation")
OUTPUT_PATH = Path("/workspace/.docwriter/doc-index.json")
REL_PREFIX = "_documentation"  # prefix used in paths within the index

# ── Regex patterns ─────────────────────────────────────────────────────
# {% page_link IDENTIFIER linkText="..." %} or {% page_link IDENTIFIER collection="..." linkText="..." %}
PAGE_LINK_RE = re.compile(r'\{%\s*page_link\s+(\S+)')
# Heading extraction: ## and ### only
HEADING_RE = re.compile(r'^(#{2,3})\s+(.+?)(?:\s*\{.*\})?\s*$', re.MULTILINE)
# Include/render refs
INCLUDE_RE = re.compile(r'\{%\s*(?:include|render)\s+(\S+)')
# Front matter boundary
FM_BOUNDARY = re.compile(r'^---\s*$')


def parse_front_matter(content):
    """Extract YAML front matter from markdown content."""
    lines = content.split('\n')
    if not lines or not FM_BOUNDARY.match(lines[0]):
        return {}, content
    
    end_idx = None
    for i in range(1, len(lines)):
        if FM_BOUNDARY.match(lines[i]):
            end_idx = i
            break
    
    if end_idx is None:
        return {}, content
    
    fm_text = '\n'.join(lines[1:end_idx])
    body = '\n'.join(lines[end_idx + 1:])
    
    try:
        fm = yaml.safe_load(fm_text)
        if not isinstance(fm, dict):
            fm = {}
    except yaml.YAMLError:
        fm = {}
    
    return fm, body


def extract_headings(body):
    """Extract h2 and h3 headings from markdown body."""
    headings = []
    for match in HEADING_RE.finditer(body):
        text = match.group(2).strip()
        # Clean up any remaining markdown formatting
        text = re.sub(r'[`*_]', '', text)
        text = text.strip()
        if text:
            headings.append(text)
    return headings


def extract_page_links(body):
    """Extract page_link identifiers from body."""
    identifiers = set()
    for match in PAGE_LINK_RE.finditer(body):
        ident = match.group(1).strip()
        # Skip if it looks like a variable or Liquid expression
        if not ident.startswith('{') and not ident.startswith('%'):
            identifiers.add(ident)
    return list(identifiers)


def extract_include_refs(body):
    """Extract include/render references from body."""
    refs = set()
    for match in INCLUDE_RE.finditer(body):
        ref = match.group(1).strip().strip('"').strip("'")
        if ref:
            refs.add(ref)
    return list(refs)


def parse_personas(fm):
    """Extract persona list from front matter."""
    persona_val = fm.get('persona') or fm.get('personas')
    if not persona_val:
        return []
    if isinstance(persona_val, list):
        return [p.strip() for p in persona_val]
    if isinstance(persona_val, str):
        return [p.strip() for p in persona_val.split(',')]
    return []


def derive_topic_cluster(rel_path, fm):
    """Derive topic cluster from path and front matter."""
    parts = Path(rel_path).parts
    # Skip the leading _documentation prefix
    if len(parts) >= 2:
        section = parts[0]  # e.g. "developers-and-admins", "business-users", "changelog"
        
        if section == "changelog":
            return "Changelog"
        elif section == "security-advisories":
            return "Security advisories"
        
        # Get subsection — strip .md if it's a file, not a directory
        subsection = parts[1]
        if subsection.endswith('.md'):
            subsection = subsection[:-3]
        
        cluster_name = subsection.replace('-', ' ').replace('_', ' ').title()
        return cluster_name
    
    # Top-level files
    return "General"


def derive_classification(fm, rel_path, body):
    """Infer page classification from front matter and content clues."""
    cat = fm.get('category', '')
    layout = fm.get('layout', '')
    
    if layout in ('homepage', 'error'):
        return layout
    
    path_lower = rel_path.lower()
    if 'tutorial' in path_lower:
        return 'tutorial'
    if 'reference' in path_lower or 'ref-' in path_lower:
        return 'reference'
    if 'changelog' in path_lower or 'release-notes' in path_lower:
        return 'changelog'
    if 'security-advisor' in path_lower:
        return 'security-advisory'
    
    return ''


def scan_all_pages():
    """Scan all markdown files and build the complete index."""
    print(f"Scanning workspace: {WORKSPACE_ROOT}", file=sys.stderr)
    
    # Step 1: Enumerate all markdown files
    all_files = sorted(WORKSPACE_ROOT.rglob("*.md"))
    total = len(all_files)
    print(f"Found {total} markdown files", file=sys.stderr)
    
    # Step 2: Parse each file
    pages = []
    identifier_map = {}  # identifier -> rel_path
    page_by_path = {}    # rel_path -> page entry
    
    for idx, filepath in enumerate(all_files):
        if (idx + 1) % 200 == 0:
            print(f"  Parsed {idx + 1}/{total}...", file=sys.stderr)
        
        rel_path = str(filepath.relative_to(WORKSPACE_ROOT))
        indexed_path = f"{REL_PREFIX}/{rel_path}"
        
        try:
            content = filepath.read_text(encoding='utf-8', errors='replace')
        except Exception as e:
            print(f"  WARN: Could not read {rel_path}: {e}", file=sys.stderr)
            continue
        
        fm, body = parse_front_matter(content)
        
        title = fm.get('title', '')
        if not title:
            title = filepath.stem.replace('-', ' ').replace('_', ' ').title()
        
        identifier = fm.get('identifier', '')
        if identifier:
            identifier_map[str(identifier)] = indexed_path
        
        personas = parse_personas(fm)
        headings = extract_headings(body)
        outgoing_ids = extract_page_links(body)
        include_refs = extract_include_refs(body)
        topic_cluster = derive_topic_cluster(rel_path, fm)
        classification = derive_classification(fm, rel_path, body)
        
        related = fm.get('related_pages', [])
        if isinstance(related, str):
            related = [related]
        elif not isinstance(related, list):
            related = []
        
        page_entry = {
            "path": indexed_path,
            "title": str(title),
            "collection": "documentation",
            "identifier": str(identifier) if identifier else None,
            "classification": classification if classification else None,
            "personas": personas,
            "category": fm.get('category', None),
            "layout": fm.get('layout', None),
            "headings": headings,
            "outgoingLinkIds": outgoing_ids,
            "outgoingLinks": [],
            "incomingLinks": [],
            "includeRefs": include_refs,
            "relatedPageIds": related,
            "topicCluster": topic_cluster,
            "order": fm.get('order', None),
        }
        
        pages.append(page_entry)
        page_by_path[indexed_path] = page_entry
    
    print(f"Parsed all {len(pages)} pages. Resolving cross-references...", file=sys.stderr)
    
    # Step 3: Resolve identifier-based links to paths
    total_internal_links = 0
    unresolved_ids = set()
    
    for page in pages:
        resolved_paths = set()
        for oid in page["outgoingLinkIds"]:
            target_path = identifier_map.get(oid)
            if target_path:
                resolved_paths.add(target_path)
            else:
                unresolved_ids.add(oid)
        
        for rid in page["relatedPageIds"]:
            target_path = identifier_map.get(str(rid))
            if target_path:
                resolved_paths.add(target_path)
        
        page["outgoingLinks"] = sorted(resolved_paths)
        total_internal_links += len(resolved_paths)
    
    if unresolved_ids:
        print(f"  Note: {len(unresolved_ids)} unresolved identifiers (may reference other collections)", file=sys.stderr)
    
    # Step 4: Build incoming link map (reverse index)
    for page in pages:
        for target_path in page["outgoingLinks"]:
            if target_path in page_by_path:
                page_by_path[target_path]["incomingLinks"].append(page["path"])
    
    for page in pages:
        page["incomingLinks"] = sorted(set(page["incomingLinks"]))
    
    # Step 5: Find orphaned pages
    orphaned_pages = [p["path"] for p in pages if not p["incomingLinks"] and not p["outgoingLinks"]]
    
    # Step 6: Build topic clusters
    cluster_map = defaultdict(list)
    for page in pages:
        cluster_map[page["topicCluster"]].append(page["path"])
    
    topic_clusters = []
    for name, paths in sorted(cluster_map.items()):
        topic_clusters.append({
            "name": name,
            "pageCount": len(paths),
            "pagePaths": sorted(paths)
        })
    
    # Step 7: Most linked pages
    most_linked = sorted(pages, key=lambda p: len(p["incomingLinks"]), reverse=True)[:20]
    most_linked_stats = [
        {"path": p["path"], "title": p["title"], "incomingCount": len(p["incomingLinks"])}
        for p in most_linked
    ]
    
    # Step 8: Clean up page entries for output
    for page in pages:
        del page["outgoingLinkIds"]
        del page["relatedPageIds"]
        page_clean = {k: v for k, v in page.items() if v is not None}
        page.clear()
        page.update(page_clean)
    
    # Step 9: Assemble final index
    now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    
    doc_index = {
        "version": 1,
        "generatedBy": "docwriter-corpus-scanner",
        "generatedAt": now,
        "workspace": "./src/_documentation/_documentation",
        "totalPages": len(pages),
        "collections": {
            "documentation": len(pages)
        },
        "pages": pages,
        "topicClusters": topic_clusters,
        "crossRefStats": {
            "totalInternalLinks": total_internal_links,
            "totalIdentifiersMapped": len(identifier_map),
            "orphanedPages": len(orphaned_pages),
            "orphanedPagePaths": orphaned_pages[:50],
            "mostLinkedPages": most_linked_stats
        }
    }
    
    return doc_index


def main():
    doc_index = scan_all_pages()
    
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_PATH, 'w', encoding='utf-8') as f:
        json.dump(doc_index, f, indent=2, ensure_ascii=False)
    
    print(f"\nWrote {doc_index['totalPages']} pages to {OUTPUT_PATH}", file=sys.stderr)
    print(f"Topic clusters: {len(doc_index['topicClusters'])}", file=sys.stderr)
    print(f"Total internal links: {doc_index['crossRefStats']['totalInternalLinks']}", file=sys.stderr)
    print(f"Orphaned pages: {doc_index['crossRefStats']['orphanedPages']}", file=sys.stderr)
    
    summary = {
        "totalPages": doc_index["totalPages"],
        "topicClusters": len(doc_index["topicClusters"]),
        "totalInternalLinks": doc_index["crossRefStats"]["totalInternalLinks"],
        "orphanedPages": doc_index["crossRefStats"]["orphanedPages"],
        "identifiersMapped": doc_index["crossRefStats"]["totalIdentifiersMapped"]
    }
    print(json.dumps(summary))


if __name__ == "__main__":
    main()
