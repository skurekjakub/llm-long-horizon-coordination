# Docwriter Query Scripts

CLI tools for querying `.docwriter/` JSON databases without loading full files into agent context.

**Convention**: All scripts output structured JSON to **stdout** and summary/error info to **stderr**. Pipe `2>/dev/null` in agent contexts to get clean JSON.

## Scripts

### query-invariants.py

Query `invariant-inventory.json` (229 invariants, ~109 KB).

```bash
# All invariants for the style reviewer (~92 entries instead of 229)
python3 .docwriter/scripts/query-invariants.py --domain style

# Just persona invariants (~9 entries)
python3 .docwriter/scripts/query-invariants.py --domain persona

# Invariants applicable to tutorials
python3 .docwriter/scripts/query-invariants.py --applies-to tutorial

# Combine filters (AND logic)
python3 .docwriter/scripts/query-invariants.py --domain style --enforcement machine-checkable

# Single invariant by ID
python3 .docwriter/scripts/query-invariants.py --id INV-codesamples-001

# List all domains and counts
python3 .docwriter/scripts/query-invariants.py --list-domains
```

### query-doc-index.py

Query `doc-index.json` (1,798 pages, ~1.07 MB).

```bash
# Pages in a topic cluster
python3 .docwriter/scripts/query-doc-index.py --cluster "Page Builder"

# Glob match on page path
python3 .docwriter/scripts/query-doc-index.py --path "*/forms/*"

# Case-insensitive title search
python3 .docwriter/scripts/query-doc-index.py --title membership

# Only pages that have cross-references
python3 .docwriter/scripts/query-doc-index.py --has-crossrefs

# Pages referencing a specific path
python3 .docwriter/scripts/query-doc-index.py --refs-to "developers-and-admins/configuration/some-page.md"

# Filter by front matter key or key=value
python3 .docwriter/scripts/query-doc-index.py --front-matter-key "layout=default"

# Combine filters with result limit
python3 .docwriter/scripts/query-doc-index.py --has-crossrefs --cluster Security --limit 10

# Index statistics
python3 .docwriter/scripts/query-doc-index.py --stats

# List all topic clusters
python3 .docwriter/scripts/query-doc-index.py --list-clusters
```

### query-task-graph.py

Query `task-graph.json` (10–40 tasks, 30–68 KB).

```bash
# Single task with full details (inlined invariants etc.)
python3 .docwriter/scripts/query-task-graph.py --task-id T-003

# All planned tasks
python3 .docwriter/scripts/query-task-graph.py --status planned

# Phase 2 tasks only
python3 .docwriter/scripts/query-task-graph.py --phase 2

# Status distribution overview
python3 .docwriter/scripts/query-task-graph.py --summary
```

### update-task-status.py

Surgical updates to `task-graph.json` — no full-file rewrite by the agent.

```bash
# Update task status
python3 .docwriter/scripts/update-task-status.py --task-id T-003 --status written

# Update arbitrary field
python3 .docwriter/scripts/update-task-status.py --task-id T-003 --field reviewCycles=2

# Multiple field updates
python3 .docwriter/scripts/update-task-status.py --task-id T-003 --status written --field reviewCycles=3
```

### query-code-analysis.py

Query `code-analysis.json` (10–30 entries, ~35 KB).

```bash
# By area name (substring match)
python3 .docwriter/scripts/query-code-analysis.py --area "Membership Core"

# By exact area ID
python3 .docwriter/scripts/query-code-analysis.py --area-id AREA-001

# High-significance entries only
python3 .docwriter/scripts/query-code-analysis.py --significance high

# Only entries with breaking changes
python3 .docwriter/scripts/query-code-analysis.py --has-breaking

# Area overview (compact summary of all areas)
python3 .docwriter/scripts/query-code-analysis.py --summary
```

### query-pipeline-status.py

Dashboard combining `progress.json`, `manifest.json`, and `task-graph.json`.

```bash
# Pipeline overview
python3 .docwriter/scripts/query-pipeline-status.py

# Include per-task status breakdown
python3 .docwriter/scripts/query-pipeline-status.py --tasks

# Include files written list
python3 .docwriter/scripts/query-pipeline-status.py --files
```

## Agent Integration

Instead of loading full JSON files, agents should call these scripts. Example agent prompt change:

**Before** (wastes ~250K tokens):
> Read `.docwriter/invariant-inventory.json` fully. Filter to style-domain invariants.

**After** (~60K tokens):
> Run: `python3 .docwriter/scripts/query-invariants.py --domain style 2>/dev/null`

## Context Savings

| Agent | Before | After | Savings |
|---|---|---|---|
| style-reviewer | 109 KB (all invariants) | ~44 KB (92 rules) | ~60% |
| content-writer | 1.07 MB (all pages) | ~15 KB (task pages) | ~98% |
| exec-coordinator (write) | 68 KB (full task-graph) | 0 KB (surgical update) | 100% |
| persona-reviewer | 109 KB (all invariants) | ~5 KB (9 rules) | ~95% |
