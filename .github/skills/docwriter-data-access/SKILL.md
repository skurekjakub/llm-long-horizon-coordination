---
name: docwriter-data-access
description: "Query scripts for accessing .docwriter/ JSON databases without loading full files into context. Mount this skill on any docwriter agent that reads invariant-inventory.json, doc-index.json, task-graph.json, or code-analysis.json. Provides targeted CLI commands that return only matching entries, dramatically reducing context consumption."
---

# Data Access — Docwriter Query Scripts

The `.docwriter/` directory contains large JSON databases that waste context when loaded fully. Use the query scripts below instead of reading entire files.

**Convention:** All scripts output structured JSON to **stdout** and summary info to **stderr**. Use `2>/dev/null` for clean JSON piping.

## invariant-inventory.json (~109 KB, 229 invariants)

```bash
# Domain-filtered (style: ~92, persona: ~9, jekyll: ~33, etc.)
python3 .docwriter/scripts/query-invariants.py --domain style

# Applicable to a content type
python3 .docwriter/scripts/query-invariants.py --applies-to tutorial

# Combine filters (AND logic)
python3 .docwriter/scripts/query-invariants.py --domain style --enforcement machine-checkable

# Single invariant by ID
python3 .docwriter/scripts/query-invariants.py --id INV-codesamples-001

# List all domains with counts
python3 .docwriter/scripts/query-invariants.py --list-domains
```

## doc-index.json (~1.07 MB, 1,798 pages)

**NEVER read this file in full.** Always use targeted queries.

```bash
# Pages in a topic cluster
python3 .docwriter/scripts/query-doc-index.py --cluster "Development"

# Glob match on page path
python3 .docwriter/scripts/query-doc-index.py --path "*/forms/*"

# Case-insensitive title search
python3 .docwriter/scripts/query-doc-index.py --title membership

# Pages with cross-references
python3 .docwriter/scripts/query-doc-index.py --has-crossrefs

# Pages referencing a specific path (inverse cross-ref lookup)
python3 .docwriter/scripts/query-doc-index.py --refs-to "developers-and-admins/configuration/some-page.md"

# Combine with result limit
python3 .docwriter/scripts/query-doc-index.py --has-crossrefs --cluster Security --limit 10

# Index statistics only (no page data)
python3 .docwriter/scripts/query-doc-index.py --stats

# List all topic clusters with counts
python3 .docwriter/scripts/query-doc-index.py --list-clusters
```

## task-graph.json (30–68 KB, 10–40 tasks)

```bash
# Single task with full details + inlined invariants
python3 .docwriter/scripts/query-task-graph.py --task-id T-003

# All tasks with a specific status
python3 .docwriter/scripts/query-task-graph.py --status planned

# Phase-filtered
python3 .docwriter/scripts/query-task-graph.py --phase 2

# Status distribution overview (no task details)
python3 .docwriter/scripts/query-task-graph.py --summary
```

### Surgical task updates (no full-file rewrite)

```bash
# Update task status
python3 .docwriter/scripts/update-task-status.py --task-id T-003 --status written

# Update arbitrary field
python3 .docwriter/scripts/update-task-status.py --task-id T-003 --field reviewCycles=2
```

## code-analysis.json (~35 KB, 10–30 entries)

```bash
# By area name
python3 .docwriter/scripts/query-code-analysis.py --area "Membership Core"

# High-significance only
python3 .docwriter/scripts/query-code-analysis.py --significance high

# Entries with breaking changes
python3 .docwriter/scripts/query-code-analysis.py --has-breaking

# Area summary (compact)
python3 .docwriter/scripts/query-code-analysis.py --summary
```

## Pipeline status dashboard

```bash
# Full pipeline overview (progress + tasks + manifest)
python3 .docwriter/scripts/query-pipeline-status.py

# Include per-task breakdown
python3 .docwriter/scripts/query-pipeline-status.py --tasks
```

## When to use full reads vs. queries

| Scenario | Approach |
|---|---|
| Need all invariants for a domain | `--domain X` query |
| Need a single task's details | `--task-id X` query |
| Need cross-ref inverse lookup | `--refs-to X` query |
| Corpus statistics only | `--stats` query |
| Writing full file (scanner/planner) | Normal full write — scripts are for reads |
| Comprehensive audit (gap-hunter) | Full read is acceptable for exhaustive coverage |
| Status update after task completion | `update-task-status.py` — never rewrite full JSON |
