## Fractal Factory

The Fractal Factory is a meta-level agent family that produces other agent families. Give it a domain description, behavioral invariants, and optionally some exemplar agents to learn from — it outputs a complete, validated fractal agent system: orchestrator, coordinators, specialists, artifact schemas, bootstrap script, golden tests, and documentation.

The factory itself follows the same fractal pattern it produces: 1 guide agent, 1 session orchestrator, 8 coordinators, and 26 specialists — 36 agents total — running an 8-pass pipeline with gap-hunting re-entry and cross-run meta-knowledge synthesis.

The complete agent family is available in [fractal-factory/](fractal-factory/).

### Architecture overview

```
User invokes fractal-factory-guide (once)
       ↓
   fractal-factory-guide
       ↓ builds context.json, invokes:
   fractal-factory (session orchestrator)
       ↓ pipeline routing
   ┌─────────────────────────────────────────────────┐
   │ Pass 0: Knowledge Curation                      │
   │   knowledge-curator                             │
   ├─────────────────────────────────────────────────┤
   │ Pass 1: Discovery                               │
   │   discovery-coordinator                         │
   │     → domain-scanner → invariant-extractor      │
   │     → asset-auditor → exemplar-analyzer         │
   ├─────────────────────────────────────────────────┤
   │ Pass 2: Analysis                                │
   │   analysis-coordinator                          │
   │     → pipeline-architect → artifact-designer    │
   │     → depth-analyzer                            │
   ├─────────────────────────────────────────────────┤
   │ Pass 3: Planning                                │
   │   planning-coordinator                          │
   │     → roster-planner → routing-planner          │
   │     → test-planner → production-graph-planner   │
   ├─────────────────────────────────────────────────┤
   │ Pass 4: Execution                               │
   │   execution-coordinator                         │
   │     → prompt-writer ↔ prompt-reviewer (per task)│
   │     → infra-writer                              │
   ├─────────────────────────────────────────────────┤
   │ Pass 5: Verification                            │
   │   verification-coordinator                      │
   │     → checklist-validator → audit-oracle         │
   ├─────────────────────────────────────────────────┤
   │ Pass 6: Gap Hunting                             │
   │   gap-hunting-coordinator                       │
   │     → coverage-hunter (categories 1–3)          │
   │     → artifact-hunter (categories 4–6)          │
   │     → infrastructure-hunter (categories 7–9)    │
   ├─────────────────────────────────────────────────┤
   │ Synthesis: Meta-Knowledge Extraction            │
   │   synthesis-coordinator                         │
   │     → factory-signal-analyzer                   │
   │     → context-signal-analyzer                   │
   │     → knowledge-integrator                      │
   ├─────────────────────────────────────────────────┤
   │ Pass 7: Delivery                                │
   │   delivery-coordinator                          │
   │     → packager → documentation-writer           │
   │     → report-writer                             │
   └─────────────────────────────────────────────────┘
```

### Agent roster

| Agent | Level | Parent | Pass |
|---|---|---|---|
| `fractal-factory` | orchestrator | guide | All |
| `fractal-factory-guide` | guide | user | — |
| `fractal-factory-knowledge-curator` | specialist | orchestrator | 0 |
| `fractal-factory-discovery-coordinator` | coordinator | orchestrator | 1 |
| `fractal-factory-analysis-coordinator` | coordinator | orchestrator | 2 |
| `fractal-factory-planning-coordinator` | coordinator | orchestrator | 3 |
| `fractal-factory-execution-coordinator` | coordinator | orchestrator | 4 |
| `fractal-factory-verification-coordinator` | coordinator | orchestrator | 5 |
| `fractal-factory-gap-hunting-coordinator` | coordinator | orchestrator | 6 |
| `fractal-factory-synthesis-coordinator` | coordinator | orchestrator | Synthesis |
| `fractal-factory-delivery-coordinator` | coordinator | orchestrator | 7 |
| `fractal-factory-domain-scanner` | specialist | discovery-coord | 1 |
| `fractal-factory-invariant-extractor` | specialist | discovery-coord | 1 |
| `fractal-factory-asset-auditor` | specialist | discovery-coord | 1 |
| `fractal-factory-exemplar-analyzer` | specialist | discovery-coord | 1 |
| `fractal-factory-pipeline-architect` | specialist | analysis-coord | 2 |
| `fractal-factory-artifact-designer` | specialist | analysis-coord | 2 |
| `fractal-factory-depth-analyzer` | specialist | analysis-coord | 2 |
| `fractal-factory-roster-planner` | specialist | planning-coord | 3 |
| `fractal-factory-routing-planner` | specialist | planning-coord | 3 |
| `fractal-factory-test-planner` | specialist | planning-coord | 3 |
| `fractal-factory-production-graph-planner` | specialist | planning-coord | 3 |
| `fractal-factory-prompt-writer` | specialist | execution-coord | 4 |
| `fractal-factory-prompt-reviewer` | specialist | execution-coord | 4 |
| `fractal-factory-infra-writer` | specialist | execution-coord | 4 |
| `fractal-factory-checklist-validator` | specialist | verification-coord | 5 |
| `fractal-factory-audit-oracle` | specialist | verification-coord | 5 |
| `fractal-factory-coverage-hunter` | specialist | gap-hunting-coord | 6 |
| `fractal-factory-artifact-hunter` | specialist | gap-hunting-coord | 6 |
| `fractal-factory-infrastructure-hunter` | specialist | gap-hunting-coord | 6 |
| `fractal-factory-factory-signal-analyzer` | specialist | synthesis-coord | Synthesis |
| `fractal-factory-context-signal-analyzer` | specialist | synthesis-coord | Synthesis |
| `fractal-factory-knowledge-integrator` | specialist | synthesis-coord | Synthesis |
| `fractal-factory-packager` | specialist | delivery-coord | 7 |
| `fractal-factory-documentation-writer` | specialist | delivery-coord | 7 |
| `fractal-factory-report-writer` | specialist | delivery-coord | 7 |

### Inputs

The factory accepts these inputs to define the target domain:

| Input | Required | Purpose |
|---|---|---|
| `domain-brief.md` | **Yes** | Narrative description of the domain — what the produced system should do, genre characteristics, input types, quality expectations |
| `domain-docs/` | No | Supporting documents — API specs, examples, reference material |
| `invariants.md` | No (recommended) | Behavioral rules the produced system must enforce |
| `exemplars/` | No | Existing agent families for the factory to learn from |
| `constraints.json` | No | Hard constraints — max agent count, required roles, depth limits |

The guide agent is the sole user-facing entry point. It interviews the user for domain details, validates inputs, builds `context.json`, and then invokes the session orchestrator which runs the full pipeline autonomously.

### The 8-pass pipeline

#### Pass 0 — Knowledge curation

The knowledge curator reads accumulated meta-knowledge from prior factory runs (`meta/index.json`) and produces a `knowledge-brief.json` — a curated summary of relevant insights for the current domain. On cold start (first-ever run), the brief is empty and the pipeline proceeds normally. This pass is non-blocking: if curation fails, later passes operate without prior knowledge.

#### Pass 1 — Discovery

Four specialists run sequentially, each contributing to the growing `domain-model.json` via a read-modify-write pattern:

1. **Domain scanner** — reads the domain brief and supporting documents, extracts subdomains, patterns, quality dimensions, and domain-specific vocabulary.
2. **Invariant extractor** — reads the invariants file and the domain model, classifies invariants by type (behavioral, structural, quality, workflow), and writes them to per-classification files under `invariants/`.
3. **Asset auditor** — inventories any existing assets the produced system needs to integrate with — existing documentation, schemas, file conventions.
4. **Exemplar analyzer** — if exemplar agent families were provided, analyzes their structure: how many agents, what depth, which patterns they use, what worked well. Insights feed into the analysis phase.

#### Pass 2 — Analysis

Three specialists design the produced system's architecture:

1. **Pipeline architect** — designs the produced system's pipeline: which phases, which coordinator boundaries, what artifact flows exist at each boundary. Produces `architecture.json`.
2. **Artifact designer** — specifies every artifact the produced system will use: schemas, ownership (which agent writes, which agents read), and lifecycle.
3. **Depth analyzer** — decides the produced system's depth: does it need 2 tiers or 3? Which phases justify sub-coordinators? The decision is based on task complexity, subdomain count, and the exemplar analysis.

#### Pass 3 — Planning

Four specialists produce the full construction plan:

1. **Roster planner** — determines the exact agent list: names, roles, parent relationships, input/output contracts. Writes `roster.json`.
2. **Routing planner** — defines every routing table: which status codes map to which actions, mode detection logic for multi-mode coordinators, re-entry paths. Writes `routing.json`.
3. **Test planner** — creates golden test scenarios from the invariants and domain model: what inputs should produce what outputs, at what quality thresholds. Writes `test-plan.json`.
4. **Production-graph planner** — transforms the roster and routing plan into a dependency-ordered task graph (`production-graph.json`) where each task produces one or more agent prompts, schemas, or infrastructure files.

#### Pass 4 — Execution

The execution coordinator drives a dependency-gated single-task loop over `production-graph.json`:

1. Select the highest-priority task with status `planned` whose `dependsOn` tasks are all `verified`.
2. Dispatch the **prompt-writer** for that task. The writer produces the agent's `.agent.md` file (or schema, skill, etc.) following the structural requirements from `produced-agent.schema.md`.
3. Dispatch the **prompt-reviewer** for the same task. The reviewer validates against structural checklists, artifact contracts, routing table consistency, and invariant coverage.
4. On approval: mark the task `verified` in the production graph and move to the next eligible task.
5. On rejection: re-dispatch the writer with reviewer feedback. Maximum 3 retries per task; exhausted tasks are marked `blocked`.
6. After all tasks are terminal: dispatch the **infra-writer** to produce the bootstrap script and any remaining infrastructure.

Produced specialist agents follow a progressive disclosure pattern: the main `.agent.md` prompt stays compact and routes into a shared workflow skill with numbered phase reference files per specialist. This keeps context focused on the active phase without mounting the full workflow inline.

#### Pass 5 — Verification

Two specialists provide a post-execution safety net (primary verification happens per-task during execution via the prompt-reviewer):

1. **Checklist validator** — runs structural validation across all produced agents: frontmatter format, status contracts, write rules, input declarations, schema compliance.
2. **Audit oracle** — applies the perspectives from the `agent-as-function-audit` and `fractal-workflow-eval` evaluation frameworks. Checks routing purity, artifact contract consistency, instruction propagation between agents, and re-entry safety.

Pass 5 is strict — any issue from either verifier fails the pass. There is no pass-with-warnings outcome.

#### Pass 6 — Gap hunting

Three specialist hunters examine the produced system for different categories of gaps:

1. **Coverage hunter** (categories 1–3) — checks subdomain coverage, invariant enforcement, and routing completeness. Every subdomain must be addressable by at least one agent. Every invariant must be referenced in at least one agent prompt. Every routing path must terminate.
2. **Artifact hunter** (categories 4–6) — checks artifact coverage, schema completeness, and cross-reference integrity. Every artifact must have at least one writer and one reader. Every schema must exist.
3. **Infrastructure hunter** (categories 7–9) — checks bootstrap completeness, test coverage, and documentation sufficiency.

Gap hunters mutate `production-graph.json` directly: they add new task nodes for missing items (with `addedBy` and `addedInCycle` fields) and annotate existing tasks with `gapAnnotations` when issues are found in already-produced agents. If the graph was mutated, the execution coordinator naturally picks up new tasks on re-entry — no pass resets or roster mutations are needed.

Convergence is reached when a cycle produces zero new tasks or annotations. Maximum 3 cycles before forced delivery.

#### Synthesis — Meta-knowledge extraction

After gap-hunting converges, three specialists extract reusable learnings:

1. **Factory-signal analyzer** — examines which prompt structures worked on first pass, which triggered reviewer rejections, which domain patterns the prompt-writer handled well or poorly.
2. **Context-signal analyzer** — examines pipeline-level behavior: which passes were bottlenecks, how many gap-hunting cycles were needed, which invariant categories caused the most issues.
3. **Knowledge integrator** — merges both signal sets into `meta/index.json` with confidence calibration. New entries start at `low` confidence, get promoted to `medium` after independent confirmation in a second run, and to `high` after 3+ runs with >80% acceptance rate.

The meta-knowledge boundary is strict: only reusable patterns, strategies, and recurring failure modes enter the knowledge base. Raw per-run invariant catalogs, domain-local rule inventories, and single-run observations are excluded by a three-criterion quality gate (reusability, actionability, non-redundancy).

#### Pass 7 — Delivery

Three specialists prepare the final output:

1. **Packager** — validates that all expected files exist, checks completeness percentages, and copies the produced system to the output directory.
2. **Documentation writer** — produces architecture overview, user guide, and roster reference documentation for the produced system.
3. **Report writer** — generates the delivery report with aggregate statistics, outstanding items, and verification coverage.

### Key design patterns

**Production-graph-driven execution.** The `production-graph.json` artifact is the sole runtime-state artifact for execution. Tasks have explicit dependency edges (`dependsOn`), priority ordering, per-task acceptance criteria, and verification hooks. The execution coordinator selects tasks by dependency readiness rather than batch ordering or roster position. This means gap-hunting re-entry is cheap — new tasks appear in the graph and execution picks them up naturally.

**Read-modify-write for shared artifacts.** Multiple discovery specialists write to `domain-model.json`. Each reads the current state, adds its entries (identified by a `discoveredBy` field), preserves all entries from other agents, and writes back. The same pattern applies to `invariants/*.json` and `production-graph.json`.

**Oracle verification.** The audit-oracle does not just check structural checklists — it applies multi-perspective analysis derived from the `agent-as-function-audit` and `fractal-workflow-eval` evaluation frameworks. This catches issues that structural validation alone misses: routing purity violations (a coordinator that does substantive work instead of dispatching), artifact contract drift (an agent that writes fields no downstream consumer reads), and instruction propagation gaps (a directive that the orchestrator specifies but no coordinator relays).

**Meta-knowledge boundary.** The knowledge integrator enforces a strict separation between run-local domain data and persistent cross-run learning. Per-run invariant catalogs stay in discovery and planning artifacts. Only insights abstracted into reusable heuristics, verification strategies, or recurring failure modes pass the quality gate and enter `meta/index.json`. This prevents the knowledge base from growing into an unbounded cache of raw domain facts.

### Routing and failure paths

The factory's routing architecture handles 14 distinct execution paths:

| Path | Entry condition | Terminal state |
|---|---|---|
| Happy path | All passes succeed, gap hunting converges | `delivered` |
| Graph re-entry | Gap hunting reports `gaps-found` within cycle limit | Re-enters at execution |
| Forced convergence | Gap hunting at max cycles | `delivered-with-gaps` |
| Discovery blocked | Discovery coordinator returns `blocked` | `failed` |
| Any coordinator failure | Coordinator returns `failed` | `failed` |
| Execution partial | Some tasks exhausted retries | Continues to verification |
| Crash recovery | Active pass found on startup | Resets to pending, re-dispatches |
| Knowledge curator cold start | No meta store available | Pass 0 completes without prior knowledge |
| Synthesis degraded | Synthesis returns `degraded` | Continues to delivery |

Crash recovery is built on the same `progress.json` mechanism as every other pipeline in the architecture. If the orchestrator starts and finds any pass with status `"active"`, it resets that pass to `"pending"`, deletes the coordinator's status file, and resumes routing. Children with completed status files are reused — the coordinator skips specialists that already have valid status on disk.

### Artifact directory

```
.fractal-factory/
├── context.json              — User input (domain, paths, options)
├── progress.json             — Pipeline state (owned by orchestrator)
├── manifest.json             — Prepend-only audit log
├── domain-model.json         — Discovery output (subdomains, patterns, assets)
├── invariants/               — Per-classification invariant files
├── architecture.json         — Pipeline design, artifact schemas, depth decisions
├── roster.json               — Full agent roster with routing tables
├── routing.json              — All routing tables for all routing agents
├── test-plan.json            — Golden test scenarios
├── production-graph.json     — Dependency-ordered task graph (runtime state)
├── verification-report.json  — Checklist validation results
├── audit-report.json         — Oracle audit findings
├── gap-report.json           — Gap hunting convergence and findings
├── agents/                   — Per-agent status.json and output.md
├── produced-output/          — The actual product
│   ├── agents/               — .agent.md files for the produced system
│   ├── schemas/              — Artifact JSON schemas
│   ├── skills/               — Shared workflow router + domain skills
│   ├── tests/                — Golden test scenario files
│   ├── docs/                 — Architecture, user guide, roster reference
│   └── bootstrap.sh          — Bootstrap script for the produced system
├── meta/                     — Meta-knowledge store
│   ├── index.json            — Registry of all knowledge entries
│   └── entries/              — Individual knowledge entries
├── knowledge-brief.json      — Pass 0 output (curated per-task)
└── synthesis-signals/        — Signal analyzer outputs
```

### Example run: Romantic Fantasy Writer

The factory's first production run generated a complete romantic fantasy fiction agent family — a system that takes a story idea and autonomously produces publication-quality romantic fantasy chapters through worldbuilding, character development, plotting, prose drafting, adversarial review gates, and multi-pass revision.

**Input:** A 3-page domain brief describing the romantic fantasy genre, its characteristics (fantasy-primary plot, romance as emotional spine, slow-burn dynamics, detailed worldbuilding), the input types a user would provide (story idea, optional style samples, character sketches, world fragments), and the quality expectations (adversarial consistency gates, multi-lens beta reading, craft-level prose calibration). Plus 81 behavioral invariants and the existing docwriter agent family as an exemplar.

**Configuration:**
```json
{
  "domain": "fantasy-writer",
  "namingPrefix": "romantic-fantasy-writer",
  "maxAgents": 80,
  "maxGapCycles": 10,
  "maxWriterReviewerRetries": 10,
  "metaKnowledge": { "enabled": true, "domainSignalName": "craft" }
}
```

**Run statistics:**
- 67 agents produced (1 guide + 1 orchestrator + 9 coordinators + 10 sub-coordinators + 46 specialists)
- 81 behavioral invariants extracted and distributed across agent prompts
- 14 subdomains identified and covered
- 42 artifacts designed with full schema coverage (18 schema files)
- 163 routing table entries across 20 routing agents
- 26 golden test scenarios
- 4 gap-hunting cycles (convergence trajectory: 22 → 6 → 2 → 0)
- 0 blocked tasks — all tasks verified on pass or within retry limit
- 29 meta-knowledge entries extracted (15 factory-domain, 14 process-level)
- 176 files packaged in the final output
- 3 documentation files totaling ~10,000 words (architecture, user guide, roster reference)

**Gap-hunting convergence.** The initial execution pass produced 45 agent prompts covering the core pipeline. The first gap-hunting cycle found 22 gaps — primarily missing specialist agents for sub-workflows that the depth-analyzer had recommended (beta-reader sub-coordinators, craft-profile selectors, series knowledge management). The second cycle found 6 remaining gaps (schema files, infrastructure). The third found 2 (test fixture detail). The fourth found zero — convergence.

The 9 gap-hunting categories all converged to clean:

| Category | Items checked | Result |
|---|---|---|
| Subdomain coverage | 14 subdomains | All covered by 2–32 agent files each |
| Invariant enforcement | 81 invariants | All referenced; 8 single-reference invariants confirmed correctly scoped |
| Routing completeness | 163 routes | All paths terminate, all dispatched agents exist |
| Artifact coverage | 42 artifacts | All have writers, readers, and schema coverage |
| Schema completeness | 18 schemas | All present and cross-referenced |
| Cross-reference integrity | — | All agent references resolve |
| Bootstrap completeness | — | Bootstrap script initializes all required directories and seed files |
| Test coverage | 26 scenarios | All subdomains exercised |
| Documentation sufficiency | 3 docs | Architecture, user guide, and roster reference complete |

**Meta-knowledge synthesis.** Since this was a cold-start run (no prior factory executions), all 29 extracted signals entered the knowledge base at `low` confidence. Factory-domain signals included observations like "depth-3 hierarchies with sub-coordinators work well for domains with >10 specialists in a single phase" and "progressive disclosure via shared workflow skills reduces specialist prompt size by 40-60%." Context signals included "gap-hunting convergence follows a power-law decline — most gaps are found in cycle 1" and "the prompt-reviewer's structural checklist catches ~80% of issues before oracle verification."

The produced fantasy writer family is available in [fantasy-writer/romantic-fantasy-writer/](fantasy-writer/romantic-fantasy-writer/).
