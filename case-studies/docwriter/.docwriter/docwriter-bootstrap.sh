#!/bin/bash
# Bootstrap for docwriter fractal orchestrator (31-agent pipeline)
#
# Run once to initialise the .docwriter/ artifact directory before the first
# orchestrator invocation. Use --clean to reset a prior run while keeping
# accumulated knowledge and task context.
#
# Usage: bash docwriter-bootstrap.sh [--clean] [root-dir]
#   root-dir  optional path to repo root (default: current directory)
#   --clean   re-run mode; see preservation policy below
#
# Pipeline passes (in order):
#   0   knowledge curation      — load meta-knowledge + research sources
#   0.5 codebase orientation    — survey + map the source repository
#   1   discovery               — diff analysis + corpus scan
#   2   analysis                — code impact analysis per changed file
#   3   planning                — task graph + per-task invariant injection
#   4   execution               — write/update documentation pages
#   5   verification            — cross-ref updates + gap hunting loop
#   6   gap hunting             — adversarial completeness audit (may re-enter pass 4)
#   6.5 synthesis               — integrate knowledge signals into meta-knowledge base
#   7   delivery                — front matter validation + changelog
#
# Artifacts created (all under .docwriter/):
#   context.json              — task + source + docs configuration (fill before run)
#   progress.json             — orchestrator pass state and counters (always reset)
#   manifest.json             — list of all files written this run (always reset)
#   directives.md             — mid-run guidance injected between agent calls
#   agents/                   — per-agent status JSON files
#   tasks/                    — per-task work artifacts (outlines, drafts, reviews)
#   discoveries/              — raw diff inventory and corpus scan outputs
#   synthesis-signals/        — inter-pass knowledge signals fed to synthesizer
#   logs/                     — timestamped run logs (used by writer-start.sh)
#   invariant-hashmap.json    — file-hash cache for incremental invariant scanning
#   invariant-inventory.json  — extracted invariant rules with unique IDs
#   doc-index.json            — indexed corpus of all documentation pages
#   meta/                     — persistent knowledge base, codebase map, research sources
#
# --clean preservation policy:
#   Preserved (stable across re-runs):
#     meta/                   — knowledge base entries, codebase map, research sources
#     synthesis-signals/      — prior knowledge signals (additive)
#     directives.md           — user-authored mid-run guidance
#     context.json            — task + source config (set once per task)
#     doc-index.json          — corpus page index (expensive to rebuild)
#     invariant-hashmap.json  — scan cache (avoids re-hashing unchanged files)
#     invariant-inventory.json — extracted invariants (avoid full re-scan)
#     docwriter-bootstrap.sh  — this script
#     writer-start.sh         — the supervisor launcher script
#   Reset (derived, reproducible):
#     progress.json, manifest.json, agents/, tasks/, discoveries/, logs/

set -euo pipefail

CLEAN_MODE=false
if [[ "${1:-}" == "--clean" ]]; then
  CLEAN_MODE=true
  shift
fi

ROOT="${1:-.}"
ARTIFACT_DIR="$ROOT/.docwriter"

if [ "$CLEAN_MODE" = true ]; then
  if [ ! -d "$ARTIFACT_DIR" ]; then
    echo "Error: $ARTIFACT_DIR does not exist. Run without --clean first."
    exit 1
  fi
  echo "Clean mode: resetting pipeline artifacts at $ARTIFACT_DIR"
  echo "  Preserving: meta/, synthesis-signals/, directives.md, context.json,"
  echo "              doc-index.json, invariant-hashmap.json, invariant-inventory.json,"
  echo "              docwriter-bootstrap.sh, writer-start.sh"
  echo "  Deleting:   progress.json, manifest.json, agents/, tasks/, discoveries/, logs/"

  # Delete all top-level items except those listed above. Using -mindepth 1 -maxdepth 1
  # ensures we only touch immediate children of ARTIFACT_DIR, never the directory itself.
  # The negated -name clauses mirror the preservation policy in the header comment exactly —
  # keep both in sync when adding new preserved artifacts.
  find "$ARTIFACT_DIR" -mindepth 1 -maxdepth 1 \
    ! -name "meta" \
    ! -name "synthesis-signals" \
    ! -name "directives.md" \
    ! -name "context.json" \
    ! -name "doc-index.json" \
    ! -name "invariant-hashmap.json" \
    ! -name "invariant-inventory.json" \
    ! -name "docwriter-bootstrap.sh" \
    ! -name "writer-start.sh" \
    -exec rm -rf {} +

  # Recreate transient directories that were just deleted.
  # synthesis-signals/ is preserved by find above but mkdir -p is harmless if it already exists.
  mkdir -p "$ARTIFACT_DIR/agents"
  mkdir -p "$ARTIFACT_DIR/tasks"
  mkdir -p "$ARTIFACT_DIR/discoveries"
  mkdir -p "$ARTIFACT_DIR/synthesis-signals"
  # logs/ is used by writer-start.sh for timestamped run logs.
  mkdir -p "$ARTIFACT_DIR/logs"
elif [ -d "$ARTIFACT_DIR" ]; then
  echo "Artifact directory already exists at $ARTIFACT_DIR"
  echo "Delete it first if you want a fresh start, or use --clean to preserve meta-knowledge."
  exit 1
else
  echo "Creating .docwriter/ artifact directory at $ARTIFACT_DIR..."

  # Transient pipeline directories — reset on every --clean run.
  mkdir -p "$ARTIFACT_DIR/agents"       # per-agent status JSON files written by each agent
  mkdir -p "$ARTIFACT_DIR/tasks"        # per-task work: outline, draft, review artifacts
  mkdir -p "$ARTIFACT_DIR/discoveries"  # raw diff inventory + corpus scan outputs from pass 1
  mkdir -p "$ARTIFACT_DIR/logs"         # timestamped stdout logs from writer-start.sh runs

  # Persistent meta-knowledge directories — never deleted, survive --clean.
  # Populated incrementally by the knowledge synthesizer (pass 6.5) across runs.
  mkdir -p "$ARTIFACT_DIR/meta/patterns"         # recurring patterns that worked well
  mkdir -p "$ARTIFACT_DIR/meta/anti-patterns"    # failure patterns to avoid
  mkdir -p "$ARTIFACT_DIR/meta/domain-insights"  # product/domain knowledge extracted from code
  mkdir -p "$ARTIFACT_DIR/meta/task-retros"      # per-task retrospectives for post-run analysis
  mkdir -p "$ARTIFACT_DIR/meta/style-evolutions" # observed changes in style guide over time

  # Persistent signals directory — accumulates inter-pass knowledge signals.
  # Feeds the knowledge-integrator during pass 6.5 synthesis.
  mkdir -p "$ARTIFACT_DIR/synthesis-signals"
fi

# ---------------------------------------------------------------------------
# Seed files — written on every run (both fresh and --clean)
# ---------------------------------------------------------------------------

# progress.json tracks the orchestrator's current pass and all aggregate counters.
# Always reset so the new run starts from pass 0 with clean counts, regardless
# of where a prior run left off.
cat > "$ARTIFACT_DIR/progress.json" << 'EOF'
{
  "version": 2,
  "lastUpdated": null,
  "currentPass": 0,
  "passStatus": {
    "pass0_knowledgeCuration": "not-started",
    "pass05_codebaseOrientation": "not-started",
    "pass1_discovery": "not-started",
    "pass2_analysis": "not-started",
    "pass3_planning": "not-started",
    "pass4_execution": "not-started",
    "pass5_verification": "not-started",
    "pass6_gapHunting": "not-started",
    "pass65_knowledgeSynthesis": "not-started",
    "pass7_delivery": "not-started"
  },
  "counts": {
    "changesDiscovered": 0,
    "docPagesIndexed": 0,
    "invariantsExtracted": 0,
    "impactsMapped": 0,
    "tasksPlanned": 0,
    "tasksWritten": 0,
    "tasksVerified": 0,
    "tasksBlocked": 0,
    "knowledgePatternsCurated": 0,
    "codebaseModulesMapped": 0,
    "researchRecommendationsApproved": 0,
    "knowledgeEntriesNew": 0,
    "skillFilesRegenerated": 0
  },
  "gapHunting": {
    "cyclesCompleted": 0,
    "newItemsPerCycle": [],
    "converged": false,
    "reEntryTarget": null
  },
  "directives": {
    "activeCount": 0,
    "lastReadAt": null
  }
}
EOF

# ---------------------------------------------------------------------------
# Seed files — written only on fresh bootstrap, never on --clean.
# These files accumulate knowledge across runs; overwriting them would erase
# hard-won meta-knowledge from prior pipeline executions.
# ---------------------------------------------------------------------------
if [ "$CLEAN_MODE" = false ]; then
  # meta/index.json — master registry of all knowledge entries in the knowledge base.
  # Entries are appended by the knowledge-integrator (pass 6.5) over successive runs.
  cat > "$ARTIFACT_DIR/meta/index.json" << 'EOF'
{
  "version": 1,
  "lastSynthesized": null,
  "entries": []
}
EOF

  # meta/codebase-map.json — persistent map of the source repository structure.
  # Built by the codebase-surveyor (pass 0.5) and merged by the codebase-curator.
  # Survives --clean so the surveyor can skip stable, already-mapped modules.
  cat > "$ARTIFACT_DIR/meta/codebase-map.json" << 'EOF'
{
  "version": 1,
  "lastSurveyed": null,
  "runCount": 0,
  "repository": {},
  "modules": [],
  "entryPoints": [],
  "componentRelationships": [],
  "summary": {
    "totalModules": 0,
    "stableModules": 0,
    "verifiedModules": 0,
    "surveyedModules": 0,
    "deprecatedModules": 0
  }
}
EOF

  # invariant-hashmap.json — file-hash cache for the invariant scanner (pass 0).
  # Maps each guidelines file path to its last-seen content hash so the scanner
  # can skip files that haven't changed, avoiding a full re-scan every run.
  cat > "$ARTIFACT_DIR/invariant-hashmap.json" << 'EOF'
{
  "version": 1,
  "lastScanned": null,
  "files": {}
}
EOF

  # invariant-inventory.json — the extracted, deduplicated set of enforceable rules
  # with unique IDs (e.g. INV-001). Written by the invariant-scanner; read by planners
  # and writers as the authoritative constraint list. Preserved on --clean so the
  # scanner only re-processes changed guidelines files.
  cat > "$ARTIFACT_DIR/invariant-inventory.json" << 'EOF'
{
  "version": 1,
  "lastScanned": null,
  "invariants": []
}
EOF

  # doc-index.json — full index of every page in the documentation corpus.
  # Built by the corpus-scanner (pass 1); expensive to rebuild. Preserved on --clean
  # so re-runs can skip the full scan if the corpus hasn't changed materially.
  cat > "$ARTIFACT_DIR/doc-index.json" << 'EOF'
{
  "version": 1,
  "lastIndexed": null,
  "pages": []
}
EOF

  # meta/research-sources.json — curated list of external style/structure references
  # used by the research-scout (pass 0). New sources can be added here or by agents.
  cat > "$ARTIFACT_DIR/meta/research-sources.json" << 'EOF'
{
  "version": 1,
  "sources": [
    {
      "id": "SRC-001",
      "name": "Google Developer Documentation Style Guide",
      "url": "https://developers.google.com/style",
      "domains": ["style", "api-reference", "general"],
      "addedBy": "bootstrap",
      "addedDate": null,
      "usageCount": 0,
      "lastUsed": null,
      "effectiveness": null,
      "deprecated": false
    },
    {
      "id": "SRC-002",
      "name": "Diátaxis Documentation Framework",
      "url": "https://diataxis.fr/",
      "domains": ["structure", "conceptual", "tutorial", "howto", "reference"],
      "addedBy": "bootstrap",
      "addedDate": null,
      "usageCount": 0,
      "lastUsed": null,
      "effectiveness": null,
      "deprecated": false
    },
    {
      "id": "SRC-003",
      "name": "Microsoft Writing Style Guide",
      "url": "https://learn.microsoft.com/en-us/style-guide/welcome/",
      "domains": ["style", "accessibility", "general"],
      "addedBy": "bootstrap",
      "addedDate": null,
      "usageCount": 0,
      "lastUsed": null,
      "effectiveness": null,
      "deprecated": false
    },
    {
      "id": "SRC-004",
      "name": "Write the Docs — Documentation Guide",
      "url": "https://www.writethedocs.org/guide/",
      "domains": ["general", "structure", "style"],
      "addedBy": "bootstrap",
      "addedDate": null,
      "usageCount": 0,
      "lastUsed": null,
      "effectiveness": null,
      "deprecated": false
    }
  ]
}
EOF
fi

# ---------------------------------------------------------------------------
# Seed files — written only if the file does not already exist.
# These are user-editable files that must never be clobbered.
# ---------------------------------------------------------------------------

# directives.md — user-authored mid-run guidance injected between agent calls.
# Never overwritten; the user edits this file directly during a run to steer behavior.
if [ ! -f "$ARTIFACT_DIR/directives.md" ]; then
  cat > "$ARTIFACT_DIR/directives.md" << 'EOF'
# Directives

<!-- Edit this file between agent invocations to inject mid-run guidance. -->
<!-- Directives are persistent until you remove them. -->
<!-- Invariants ALWAYS win — directives cannot override policy constraints. -->
<!-- See plans/docwriter-extensions/directive-format-spec.md for full reference. -->

## Global
<!-- Applies to all passes and agents. -->

## Context
<!-- Background information — enriches agent understanding without prescribing behavior. -->

## Routing
<!-- Orchestrator-only: skip/halt/re-run passes. -->
EOF
fi

# manifest.json — running list of all files written or modified during this pipeline run.
# Always reset to an empty array so the manifest reflects only the current run's output.
cat > "$ARTIFACT_DIR/manifest.json" << 'EOF'
[]
EOF

# context.json — the primary configuration file for this pipeline run.
# Contains task metadata, source repo references, docs workspace path, and output branch.
# Never overwritten; filled in by the user before the first agent invocation.
# On --clean runs, the existing context.json is deliberately preserved so the same
# task configuration drives the re-run.
if [ ! -f "$ARTIFACT_DIR/context.json" ]; then
  cat > "$ARTIFACT_DIR/context.json" << 'EOF'
{
  "version": 1,
  "task": {
    "id": "<FILL: task identifier, e.g. DOC-3187>",
    "description": "<FILL: brief description of the task goal and scope, e.g. Document the new environment-specific config overlay feature>",
    "instructions": [
      "<FILL or REMOVE: task-specific rules enforced as invariants for this run only>",
      "<e.g. All code samples must target .NET 8>",
      "<e.g. Do not modify pages under /legacy/ — they are frozen>"
    ]
  },
  "source": {
    "repoPath": "<FILL: path to cloned source repo, e.g. resources/repositories/xperience>",
    "diffRef": "<FILL: branch name or commit SHA to diff>",
    "baseBranch": "<FILL: base branch to diff against, e.g. main>"
  },
  "docs": {
    "workspacePath": "<FILL: path to Jekyll doc workspace root, e.g. src/>",
    "contentCollections": ["<FILL: e.g. documentation, guides, api>"]
  },
  "invariants": {
    "guidelinesPath": "<FILL: path to guidelines/invariants folder, e.g. resources/guidelines/>"
  },
  "output": {
    "branch": "<FILL: git branch name for doc changes, e.g. docs/feature-xyz>"
  }
}
EOF
fi

echo ""
if [ "$CLEAN_MODE" = true ]; then
  echo "Clean bootstrap complete at $ARTIFACT_DIR"
  echo "  Meta-knowledge, invariants, corpus index, and task context preserved."
  echo "  Pipeline state (progress.json, manifest.json, agents/, tasks/, discoveries/) reset."
else
  echo "Fresh bootstrap complete at $ARTIFACT_DIR"
  echo "  All artifact directories and seed files created."
fi
echo ""
echo "Next steps:"
if [ "$CLEAN_MODE" = false ]; then
  echo "  1. Edit $ARTIFACT_DIR/context.json — fill in all <FILL:...> values"
  echo "  2. Invoke the session orchestrator: @docwriter"
else
  echo "  1. Verify $ARTIFACT_DIR/context.json is correct for this re-run"
  echo "  2. Optionally update $ARTIFACT_DIR/directives.md with new guidance"
  echo "  3. Invoke the session orchestrator: @docwriter"
fi
echo ""
