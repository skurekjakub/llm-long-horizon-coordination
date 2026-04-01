## Docwriter

Docwriter is a fractal documentation pipeline that transforms code changes into publication-ready documentation. It is a concrete instantiation of the agent-as-function architecture described in the main README, running as a depth-2 hierarchy: one session orchestrator, seven coordinators, and twenty-four specialists — thirty-two agents total.

The system takes a git diff and a documentation workspace as input. It produces updated or new documentation pages, cross-reference fixes, a changelog entry, and — as a side effect — a curated knowledge base that improves subsequent runs.

This case study walks through the full pipeline: the agents that compose it, the artifacts they produce, how information flows across phases, how the system self-converges through feedback loops, and how the prompt architecture shifts from abstract routing at the top to concrete imperative work at the leaves.

The complete agent family is available in [case-studies/docwriter/](docwriter/).

### Architecture overview

![Docwriter pipeline overview](docwriter/_docwriter-overview.drawio.svg)

The docwriter family follows three tiers:

**Tier 1 — Session orchestrator** (`docwriter`). A pure router. It reads `progress.json`, looks up the first matching condition in a routing table, and dispatches the next coordinator. It never reads source code, documentation content, or guidelines. Its entire context footprint after a full pipeline run is roughly ten dispatch-and-return lines.

**Tier 2 — Coordinators** (7). Each coordinator owns one or more passes. It dispatches specialists in the correct order, validates their outputs, and writes a status file. Coordinators do not perform analysis, writing, or reviewing. They are routing agents scoped to a sub-workflow.

**Tier 3 — Specialists** (24). Leaf agents that do actual work. Each specialist reads a defined set of upstream artifacts, performs one focused task, and writes its output artifact. The content-writer reads a task definition and produces a documentation page. The accuracy-reviewer reads source code and a written page and produces a review verdict. Each specialist's context window contains only what it needs — nothing more.

The hierarchy:

```
docwriter (orchestrator)
├── Pass 0: knowledge-curator (specialist, direct dispatch)
├── Pass 0.5: codebase-orientation-coordinator
│   ├── codebase-surveyor
│   └── codebase-curator
├── Pass 1: discovery-coordinator
│   ├── diff-analyzer
│   └── corpus-scanner
├── Pass 2–3: analysis-coordinator (mode-detecting)
│   ├── invariant-scanner       (Pass 2)
│   ├── code-analyzer           (Pass 2, parallel)
│   ├── research-scout          (Pass 2, parallel, non-blocking)
│   ├── impact-mapper           (Pass 2)
│   ├── task-planner            (Pass 3)
│   └── risk-analyzer           (Pass 3)
├── Pass 4: execution-coordinator
│   ├── content-writer
│   ├── style-reviewer
│   ├── accuracy-reviewer
│   └── persona-reviewer
├── Pass 5–6: verification-coordinator
│   ├── cross-ref-updater
│   └── gap-hunter
├── Pass 6.5: synthesis-coordinator
│   ├── task-signal-analyzer
│   ├── context-signal-analyzer
│   ├── knowledge-integrator
│   └── skill-rebuilder
└── Pass 7: delivery-coordinator
    ├── frontmatter-validator
    └── changelog-writer
```

### The 10-pass pipeline

The orchestrator advances through ten passes. Each pass maps to a coordinator (or a directly dispatched specialist), which in turn runs its own sub-workflow. The routing table is the orchestrator's entire decision surface:

| Condition | Action |
|---|---|
| `pass0_knowledgeCuration` not done | Dispatch knowledge-curator |
| `pass05_codebaseOrientation` not done | Dispatch codebase-orientation-coordinator |
| `pass1_discovery` not done | Dispatch discovery-coordinator |
| `pass1_discovery` done, `pass2_analysis` not done | Dispatch analysis-coordinator (Pass 2 mode) |
| `pass2_analysis` done, `pass3_planning` not done | Dispatch analysis-coordinator (Pass 3 mode) |
| `pass3_planning` done, `pass4_execution` not done | Dispatch execution-coordinator |
| `pass4_execution` done, `pass5_verification` not done | Dispatch verification-coordinator |
| `pass6_gapHunting` done, `reEntryTarget` non-null, cycles < 3 | Cascade reset → re-enter from target pass |
| `pass6_gapHunting` done + converged, `pass65` not done | Dispatch synthesis-coordinator |
| `pass65_knowledgeSynthesis` done, `pass7_delivery` not done | Dispatch delivery-coordinator |
| `pass7_delivery` done | Pipeline complete |

After each coordinator returns, the orchestrator reads its status file, updates `progress.json`, appends to `manifest.json`, and re-evaluates. On crash recovery, the orchestrator reads `progress.json` and immediately resumes from the corresponding phase.

The following pass-by-pass breakdown uses artifacts from an actual pipeline run — task DOC-3167, documenting page-level ACL permissions for the Xperience platform. The run produced 8 documentation tasks across 8 files, completed in 2 gap-hunting cycles with zero blocked tasks. Full run data is available in [run-data/docwriter-page-permissions/](../run-data/docwriter-page-permissions/).

### Pass-by-pass breakdown

#### Pass 0 — Knowledge curation

Before anything else runs, the knowledge-curator scans the accumulated meta-knowledge base (patterns, anti-patterns, domain insights, style evolutions from previous pipeline runs) and produces a `knowledge-brief.json` — a focused subset of the most relevant entries for the current task.

The brief is scored by relevance (domain overlap 40%, confidence 25%, recency 20%, usage count 15%) and capped at twenty entries. On the first-ever run (`coldStart: true`), the brief is empty. On subsequent runs, it carries forward lessons learned: which task shapes succeed on the first attempt, which invariant counts correlate with acceptance, which documentation patterns tend to trigger reviewer rejections.

This pass is non-blocking. If knowledge curation fails, the pipeline proceeds without meta-knowledge — the core workflow does not depend on it.

**Artifacts produced:** `knowledge-brief.json`
**Read by:** task-planner, content-writer, style-reviewer, accuracy-reviewer, gap-hunter

From the page-permissions run — the knowledge-brief carries a `taskProfile` that anchors relevance scoring, followed by scored entries from the accumulated knowledge base:

```json
{
  "taskProfile": {
    "domains": ["admin-ui", "api-reference", "authentication", "content-security"],
    "docTypes": ["reference", "how-to", "conceptual"],
    "changeScope": "gap-fill",
    "historicalSimilarity": "DOM-004 (content-security domain overlap)"
  },
  "patterns": [
    {
      "id": "PAT-002",
      "title": "High invariant count correlates with first-attempt success for update tasks",
      "insight": "First-attempt tasks applied more invariants on average (13.1 vs 6.7 in DOC-3137). The 3 highest invariant counts (T-008: 24, T-007: 18, T-012: 29) all achieved first-attempt acceptance.",
      "applicability": "Directly applicable — this task updates existing pages (gap-fill).",
      "confidence": "high",
      "relevanceScore": 0.7143,
      "consumers": ["task-planner", "content-writer"]
    }
  ],
  "antiPatterns": [
    {
      "id": "ANTI-001",
      "title": "Create-action pages have higher rejection rates than updates",
      "insight": "Create tasks averaged 3.33 attempts vs update 1.33 in DOC-3137.",
      "consumers": ["style-reviewer", "gap-hunter"]
    }
  ]
}
```

The `taskProfile` is computed from `context.json` — it defines the domains and doc types for this run so the curator can score relevance. Each pattern and anti-pattern carries `consumers` — the downstream agents that should pay attention to it. The `relevanceScore` (0–1) is the weighted composite of domain overlap, confidence, recency, and usage count. This run curated 6 patterns, 4 anti-patterns, and 6 domain insights. On a cold-start run, these sections would be empty.

#### Pass 0.5 — Codebase orientation

The codebase-orientation-coordinator dispatches two specialists:

1. **codebase-surveyor** scans the source repository structure and produces a raw survey of modules, APIs, technology stack elements, and inter-module relationships.
2. **codebase-curator** merges the survey into a persistent `meta/codebase-map.json`, preserving stable entries across runs and integrating new observations.

The codebase map gives downstream agents (especially code-analyzer and task-planner) a structural overview of the repository without requiring them to independently discover the codebase layout.

Like Pass 0, this is non-blocking on failure.

**Artifacts produced:** `codebase-survey.json`, `meta/codebase-map.json`
**Read by:** code-analyzer, task-planner, knowledge-curator (future runs)

From the page-permissions run — the codebase-surveyor mapped 56 modules. Each module entry describes its purpose, key files, public interfaces, and dependencies on other modules. The `permissionRelevance` field was added because the surveyor is task-aware — it knows from `context.json` that this run is about permissions:

```json
{
  "path": "CMSSolution/Websites/",
  "name": "CMS.Websites",
  "purpose": "Website channel management — web page CRUD, ACL permissions, URL routing, page publishing, scheduled publishing, recycle bin, visual builder, page templates, web page scopes, and domain management.",
  "keyFiles": [
    "ACLs/WebPageAclPermissions.cs",
    "ACLs/WebPageAclPermissionConstants.cs",
    "ACLs/WebPageAclRolePermissionEvaluator.cs",
    "ACLs/IWebPageAclRolePermissionEvaluator.cs"
  ],
  "publicInterfaces": [
    "WebPageAclPermissions — static constants: DISPLAY, READ, CREATE, UPDATE, DELETE, SYNCHRONIZE",
    "IWebPageAclRolePermissionEvaluator — evaluates ACL permissions per role"
  ],
  "dependencies": ["CMSSolution/ContentEngine/", "CMSSolution/Core/", "CMSSolution/Membership/"],
  "surveyDepth": "full",
  "permissionRelevance": "primary — defines all web page ACL permission constants and core ACL evaluation infrastructure"
}
```

The `surveyDepth` field indicates how deeply the surveyor scanned each module — `full` for permission-relevant modules, `surface` for peripheral ones. The `dependencies` array creates an implicit module graph that the code-analyzer uses to trace call chains across module boundaries.

#### Pass 1 — Discovery

Discovery answers two questions: what changed in the code, and what already exists in the documentation.

**diff-analyzer** parses the git diff specified in `context.json`, categorizes changes by product area, and emits a structured `change-inventory.json` — each changed file annotated with change type, summary, affected symbols, and whether the change is user-facing.

**corpus-scanner** indexes the entire documentation workspace, producing `doc-index.json` — every page catalogued with its path, title, collection, classification, target personas, headings, outgoing/incoming links, and topic cluster membership. This is the system's map of the existing documentation landscape.

Both artifacts are foundational. Nearly every downstream specialist reads one or both.

**Artifacts produced:** `change-inventory.json`, `doc-index.json`
**Read by:** Most downstream specialists — code-analyzer, impact-mapper, task-planner, cross-ref-updater, gap-hunter, changelog-writer, persona-reviewer

From the page-permissions run — the diff-analyzer found 14 changed files across 4 areas. Each file entry carries the symbols that changed and a `userFacing` boolean that tells the impact-mapper whether documentation is needed:

```json
{
  "totalFilesChanged": 14,
  "areas": [
    {
      "id": "AREA-001",
      "name": "Page ACL Permission Evaluation and Constants",
      "description": "Core ACL permission evaluation engine, permission constant definitions, and the prerequisite-Read gating logic",
      "files": [
        {
          "path": "CMSSolution/Admin/.../WebPageAclPermissionEvaluator.cs",
          "changeType": "modified",
          "summary": "Central ACL permission evaluator. Checks if the current user is a channel admin (bypasses all ACL checks). For non-admin users, evaluates page-level permissions via ACL role mappings. Implements the prerequisite-Read rule.",
          "symbols": ["WebPageAclPermissionEvaluator", "Evaluate()", "EvaluatePermission()"],
          "userFacing": true
        }
      ]
    }
  ]
}
```

The area grouping (`AREA-001` through `AREA-004`) is the diff-analyzer's own categorization — it clusters files by functional area so the code-analyzer can process related files together. The `changeType` is one of `modified`, `added`, `deleted`, or `renamed`.

The corpus-scanner indexed 1,800 documentation pages. Each page entry provides the full cross-reference graph — `outgoingLinks` and `incomingLinks` — that the cross-ref-updater and impact-mapper need:

```json
{
  "totalPages": 1800,
  "pages": [
    {
      "path": "_documentation/administration-interface-basics.md",
      "title": "Administration interface basics",
      "collection": "documentation",
      "identifier": "IJXWCQ",
      "personas": ["all"],
      "headings": ["Xperience administration interface", "Applications", "Administration interface URL structure"],
      "outgoingLinks": [
        "_documentation/developers-and-admins/installation.md",
        "_documentation/developers-and-admins/installation/system-requirements.md"
      ],
      "incomingLinks": [
        "_documentation/changelog/documentation-updates.md",
        "_documentation/glossary.md"
      ],
      "topicCluster": "General"
    }
  ]
}
```

The `identifier` is a stable page ID from the Jekyll front matter — cross-references use this rather than file paths so that page renames do not break links. The `topicCluster` groups pages for the impact-mapper's stale-content detection.

#### Pass 2 — Analysis

The analysis-coordinator runs in Pass 2 mode, dispatching four specialists:

**invariant-scanner** reads all guidelines files (style guides, persona definitions, content type specs, Jekyll conventions) and extracts every discrete, enforceable rule into `invariant-inventory.json`. Each invariant gets a unique ID (`INV-style-001`, `INV-persona-003`, `INV-jekyll-015`), a domain classification, an enforcement type (machine-checkable vs. reviewer-checkable), and applicability scope. The scanner uses a hash-based incremental approach — unchanged guidelines sections are not re-processed.

This is the traceability backbone. Every downstream decision about documentation quality traces back to a specific invariant ID. When the style-reviewer rejects a page, it cites `INV-style-007`. When the gap-hunter flags a missing check, it references `INV-persona-003`. There is no ambiguity about which rule was violated.

**code-analyzer** performs deep code analysis — tracing call chains, extracting behavioral impact (user-facing changes, developer-facing changes, side effects, breaking changes), and producing structured `docFacts` (parameters, configuration changes, error conditions, prerequisites). This runs in parallel with the research-scout.

**research-scout** researches latest documentation best practices from curated internet sources, filters findings through the invariant inventory (recommendations that conflict with invariants are blocked), and produces `research-brief.json`. This specialist is non-blocking — if research fails or times out, the pipeline proceeds without it.

**impact-mapper** cross-references code changes with the documentation corpus to determine which existing pages need updates, which new pages are needed, and which content has become stale. The output is `impact-matrix.json` — each impact entry has an ID, type (update/new-page/stale/no-impact), priority, target page, and affected sections.

**Artifacts produced:** `invariant-inventory.json`, `code-analysis.json`, `research-brief.json`, `impact-matrix.json`
**Read by:** task-planner, content-writer, all reviewers, gap-hunter, risk-analyzer

From the page-permissions run — the invariant-scanner extracted 231 invariants. Each invariant has a domain, enforcement type, and applicability scope. Task-specific invariants (`TINV-*`) are ephemeral — they apply only to this run. Permanent invariants (`INV-*`) persist across runs:

```json
{
  "id": "TINV-001",
  "domain": "persona",
  "rule": "Task must cover both developer and business user scenarios.",
  "source": { "file": "context.json", "section": "task.instructions" },
  "enforcement": "reviewer-checkable",
  "appliesTo": ["all"],
  "ephemeral": true
}
```

```json
{
  "id": "INV-style-001",
  "domain": "style",
  "rule": "Use 4 spaces for indentation. No tabs.",
  "source": { "file": "./.github/resources/styleguides/docs-style-guide-full.md" },
  "enforcement": "machine-checkable",
  "appliesTo": ["all"],
  "ephemeral": false
}
```

The `enforcement` field determines who checks the invariant: `machine-checkable` rules are validated by the frontmatter-validator, `reviewer-checkable` rules are evaluated by the three reviewers. The `appliesTo` field scopes which tasks the invariant is relevant to — `["all"]` means every task, but some invariants target specific content types or collections.

The code-analyzer produced deep behavioral analysis per file. The `docFacts` structure is what makes the content-writer's job tractable — it does not need to read source code, just the pre-extracted facts:

```json
{
  "filePath": "CMSSolution/Admin/.../WebPageAclPermissionEvaluator.cs",
  "behavioralImpact": {
    "userFacing": "Central ACL gatekeeper. Every page operation passes through Evaluate(). Implements two-tier: (1) Channel admin bypass, (2) ACL evaluation with Read prerequisite rule.",
    "developerFacing": "Scoped service (one per HTTP request). Caches granted permissions per web page item ID within a request."
  },
  "docFacts": {
    "keyBehaviors": [
      {
        "rule": "Read Prerequisite Rule",
        "description": "For permissions NOT in IndividuallyCheckedPermissions (Create, Update, Delete, Synchronize), requires BOTH Read AND the specific permission.",
        "implication": "Granting Update without Read has zero effect."
      },
      {
        "rule": "Channel Admin Bypass",
        "description": "Calls IsChannelAdmin(). If true, returns Success immediately without any ACL evaluation."
      }
    ]
  }
}
```

The research-scout produced 10 recommendations, of which 8 were approved and 2 were adapted. Each recommendation carries an `invariantCheck` — the invariant gate that prevents research findings from conflicting with established rules:

```json
{
  "id": "REC-001",
  "topic": "Prerequisite-Read rule warning callout",
  "recommendation": "Document the prerequisite-Read rule using a Warning callout, not a Note or Info. This is a 'pit of failure' pattern.",
  "source": "https://developers.google.com/style/notices",
  "status": "approved",
  "invariantCheck": {
    "compatible": ["INV-style-138", "INV-style-141", "INV-style-072", "INV-style-139"],
    "noConflict": true
  }
}
```

```json
{
  "id": "REC-002",
  "topic": "Permission requirement table for operation-to-permission mapping",
  "recommendation": "Present operation-to-permission mapping using a structured table.",
  "source": "https://developers.google.com/style/tables",
  "status": "adapted",
  "invariantCheck": {
    "noConflict": false,
    "adaptation": "INV-jekyll-001 requires Liquid table syntax. Google recommendation is format-agnostic."
  }
}
```

When `noConflict` is false, the recommendation is either blocked (filtered from downstream use) or adapted — the adaptation note explains how the recommendation was modified to satisfy the conflicting invariant. Four additional recommendations were blocked entirely by the invariant gate.

The impact-mapper produced 38 impacts — from critical (completely undocumented behavior) to low (minor cross-reference opportunity):

```json
{
  "id": "IMP-001",
  "areaId": "AREA-001",
  "type": "update",
  "priority": "critical",
  "targetPage": "page-permission-management.md",
  "targetSections": ["(after permission descriptions table — new section)"],
  "reason": "The Read prerequisite rule is completely undocumented: granting Update, Create, Delete, or Synchronize without also granting Read has zero effect."
}
```

The `type` is one of `update` (modify existing page), `new-page` (create new page), `stale` (content is outdated), or `no-doc-impact`. The `targetSections` tell the task-planner exactly where in the page the change should go. Out of 38 impacts: 1 critical, 13 high, 15 medium, 9 low.

#### Pass 3 — Planning

The same analysis-coordinator runs again, now in Pass 3 mode, dispatching two specialists:

**task-planner** converts the impact matrix into a dependency-ordered `task-graph.json`. Each task specifies the action (create/update/update-crossrefs), target file, target personas, sections to modify/add/remove, inlined invariants, inlined docFacts, acceptance criteria, and dependencies. The planner also inlines relevant patterns from the knowledge brief and approved research recommendations.

The invariant inlining is a key design choice. Instead of each downstream agent independently reading the 200+ line invariant inventory and deciding which rules apply, the task-planner performs this selection once and embeds only the relevant 15–20 invariants directly into each task definition. This focused context makes the content-writer's job more tractable and the reviewers' checks more precise.

**risk-analyzer** assesses each planned task across six dimensions: technical accuracy risk, scope creep, cross-reference fragility, staleness, persona complexity, and research alignment. The output is a `risk-register.json` that the execution-coordinator uses for ordering decisions (high-risk tasks first, when the pipeline has the most capacity for re-work).

**Artifacts produced:** `task-graph.json`, `risk-register.json`
**Read by:** execution-coordinator, content-writer, all reviewers, gap-hunter, frontmatter-validator, changelog-writer

From the page-permissions run — the task-planner produced 8 tasks. Each task is a self-contained work unit with inlined context from all upstream artifacts:

```json
{
  "id": "T-001",
  "name": "Update Page permission management page with operation-specific permission sections",
  "order": 1,
  "action": "update",
  "contentType": "reference",
  "targetFile": "page-permission-management.md",
  "targetPersonas": ["admin", "developer"],
  "sections": {
    "modify": ["Allow users to work with website channel content", "(Read row)", "(Delete row)"],
    "add": ["Read prerequisite warning", "Multi-layer permission model introduction",
            "Page permissions for publishing/creating/deleting/unpublishing pages"]
  },
  "docFacts": ["... 11 facts from code analysis ..."],
  "relatedImpacts": ["IMP-001", "IMP-002", "IMP-003", "IMP-004", "IMP-005", "IMP-006"],
  "dependsOn": [],
  "invariants": ["... 231 invariants embedded ..."]
}
```

The `sections.modify` and `sections.add` arrays tell the content-writer exactly which parts of the existing page to change and which new sections to insert. The `relatedImpacts` trace back to the impact-matrix, maintaining the full provenance chain: code change → area → impact → task. The `dependsOn` array enforces ordering — T-002 through T-008 depend on T-001 because it is the hub page that other pages cross-reference.

The risk-analyzer assessed each task across six dimensions:

```json
{
  "taskId": "T-001",
  "overallRisk": "critical",
  "dimensions": {
    "technicalAccuracy": "high",
    "scopeCreep": "high",
    "crossReference": "high",
    "staleness": "medium",
    "personaComplexity": "medium",
    "researchAlignment": "medium"
  },
  "incomingLinkCount": 27,
  "mitigations": [
    "Accuracy reviewer must cross-check every permission requirement against permissionSummary in code-analysis.json",
    "Writer must not expand beyond the 6 operation sections planned",
    "Cross-ref updater must verify all 27 incoming links remain valid"
  ]
}
```

The `incomingLinkCount` (27 pages linking to this page) directly drives the `crossReference` risk dimension. The `mitigations` are concrete instructions — the execution-coordinator routes high-risk tasks first and uses these mitigations to inform reviewer dispatch. Risk distribution for this run: 1 critical, 2 medium, 5 low.

#### Pass 4 — Execution

This is the most complex pass. The execution-coordinator iterates over every task in the task graph and runs a write-then-review loop for each.

For each task:

1. **content-writer** receives the task definition (with inlined invariants, docFacts, knowledge brief patterns, and research recommendations) and writes or updates the documentation page. One invocation per task — the writer's context contains only what it needs for that specific page.

2. Three reviewers evaluate the result independently:
   - **style-reviewer** checks style guide compliance, structural conventions, formatting, and cross-reference syntax
   - **accuracy-reviewer** verifies every technical claim against actual source code — it reads the relevant source files, not just the content-writer's output
   - **persona-reviewer** checks audience targeting, tone calibration, depth expectations, and taxonomy compliance

3. If any reviewer rejects, the coordinator merges all findings into a single `review-feedback.md` and re-dispatches the content-writer. All three reviewers re-run on the rewrite — this prevents fixing a style issue from introducing an accuracy regression.

4. Maximum three attempts per task. After three rejections, the task is marked `blocked` rather than looping indefinitely.

The triple-review design exists because a single reviewer trying to check style, accuracy, and persona simultaneously would need an enormous context (style guide + source code + persona definitions) and would produce ambiguous feedback. Three specialists give clear ownership, precise invariant-level verdicts, and focused context windows.

**Artifacts produced:** documentation files, `writer-output.json` per task, `style-review.json`, `accuracy-review.json`, `persona-review.json` per task
**Read by:** verification-coordinator, gap-hunter, task-signal-analyzer

From the page-permissions run — T-001 (the hub page) went through 3 attempts: 2 initial cycles plus 1 gap-hunting re-entry. The writer-output tracks what changed on each attempt:

```json
{
  "agent": "docwriter-content-writer",
  "taskId": "T-001",
  "attempt": 3,
  "action": "update",
  "targetFile": "page-permission-management.md",
  "sectionsModified": [
    "Permission requirements for page operations (added Synchronize to permission enumeration)",
    "Page permissions for creating pages (added clone permission requirements)"
  ],
  "sectionsAdded": ["Page permissions for synchronizing pages"],
  "docFactsUsed": [
    "permissionSummary.clonePage: READ on source page AND READ + CREATE on target parent",
    "permissionSummary.synchronize: READ + SYNCHRONIZE on page AND all ancestor pages"
  ],
  "invariantsApplied": ["INV-style-132", "INV-style-096", "INV-style-001", "INV-style-139"],
  "attemptNotes": "Attempt 3: Gap-hunting re-entry — targeted fixes for GAP-001 (clone perms), GAP-003 (Synchronize enumeration + new section)."
}
```

The `docFactsUsed` creates a verifiable link back to the code-analysis. The accuracy-reviewer's job is to confirm that every claim in the written page traces back to one of these facts.

The style-reviewer produces per-invariant verdicts — each reviewed rule is cited with evidence:

```json
{
  "agent": "docwriter-style-reviewer",
  "taskId": "T-001",
  "verdict": "approved",
  "invariantResults": [
    { "invariantId": "INV-style-096", "result": "pass", "evidence": "No Unicode en dashes found." },
    { "invariantId": "INV-style-132", "result": "pass", "evidence": "No 'must' directed at people." },
    { "invariantId": "INV-style-139", "result": "pass", "evidence": "All multi-content callouts have bold titles." }
  ]
}
```

The accuracy-reviewer checks every technical claim against source code:

```json
{
  "agent": "docwriter-accuracy-reviewer",
  "taskId": "T-001",
  "verdict": "approved",
  "claims": [
    { "claim": "Read is prerequisite for all page permissions except Display", "result": "verified",
      "evidence": "WebPageAclPermissionEvaluator.cs lines 118-123" },
    { "claim": "Channel admin bypass via Administrator role or ManagePermissions", "result": "verified" },
    { "claim": "Publish requires Read + Update", "result": "verified" },
    { "claim": "Create checks parent page, not page being created", "result": "verified" }
  ]
}
```

The persona-reviewer caught a real issue on attempt 1 — the front matter declared `persona: admin` but the task required both admin and developer coverage:

```json
{
  "agent": "docwriter-persona-reviewer",
  "taskId": "T-001",
  "attempt": 2,
  "verdict": "approved",
  "previousVerdict": "rejected",
  "previousRejectionReason": "Front matter declared persona: admin but required persona: admin, developer.",
  "fixVerification": { "fixed": true, "evidence": "Line 3 now reads persona: admin, developer" },
  "invariantResults": [
    { "invariantId": "TINV-001", "result": "pass" },
    { "invariantId": "INV-persona-001", "result": "pass" }
  ]
}
```

This demonstrates the feedback precision: the rejection cited a specific invariant (TINV-001 from `context.json` instructions), the writer fixed it, and the re-review confirmed the fix with evidence. Across the full run: 5 of 8 tasks passed on the first attempt, 3 required a second cycle. Zero tasks were blocked.

#### Pass 5–6 — Verification and gap hunting

The verification-coordinator runs two sub-passes:

**Pass 5: cross-ref-updater** scans all pages that link to or from modified documentation and fixes broken references, updates anchor targets, and identifies new cross-linking opportunities. Output: `verification-matrix.json`.

**Pass 6: gap-hunter** performs an adversarial completeness audit. It reads the change-inventory, task-graph, all written outputs, and the invariant inventory, then hunts for: undocumented code changes, stale content that was not caught, invariants that were never applied to any task, and any other coverage gaps.

The gap-hunter's output (`gap-analysis.json`) includes a convergence assessment. If `totalGaps > 0`, it sets a `reEntryTarget` indicating which pass must re-run to address the gaps. The orchestrator reads this and performs a cascade reset — resetting the target pass and all downstream passes to `not-started`, then continuing the routing loop from the reset point.

Every gap blocks. There is no severity-based filtering, no "known follow-up items". The philosophy is zero-tolerance: if the gap-hunter found it, the pipeline addresses it.

Smart re-entry avoids redundant work: the task-planner modifies only gap-affected tasks on re-entry (preserving completed work), and the execution-coordinator resets only `affectedTaskIds` from the gap analysis rather than re-running all tasks.

Maximum three gap-hunting cycles. After three, convergence is forced.

**Artifacts produced:** `verification-matrix.json`, `gap-analysis.json`
**Read by:** orchestrator (re-entry decision), analysis-coordinator (gap relay), execution-coordinator (smart task targeting)

From the page-permissions run — the cross-ref-updater validated 190 outgoing links across 48 pages with zero broken references:

```json
{
  "summary": {
    "pagesChecked": 48,
    "outgoingLinksValid": 190,
    "outgoingLinksBroken": 0,
    "allAnchorsValid": true,
    "verdict": "All cross-references are valid. No updates needed."
  }
}
```

The gap-hunter's cycle 1 found 3 gaps. The `convergenceAssessment` from cycle 1 triggered a re-entry to Pass 4. After the re-entry cycle addressed all gaps, cycle 2 confirmed convergence:

```json
{
  "cycle": 2,
  "previousCycleResolution": {
    "GAP-001": {
      "status": "resolved",
      "verification": "page-permission-management.md lines 222-226 now document clone-specific permissions."
    },
    "GAP-002": {
      "status": "resolved",
      "verification": "Hex-level grep confirmed zero Unicode en-dash (U+2013) characters remain in any of the 8 modified files."
    },
    "GAP-003": {
      "status": "resolved",
      "verification": "page-permission-management.md line 180 now lists Synchronize. New section 'Page permissions for synchronizing pages' added."
    }
  },
  "gaps": [],
  "convergenceAssessment": {
    "totalGaps": 0,
    "reEntryNeeded": false,
    "converged": true
  }
}
```

The three gaps illustrate the gap-hunter's different detection capabilities: GAP-001 and GAP-003 were coverage gaps (operations with distinct permission semantics that the task-planner missed), while GAP-002 was a pre-existing encoding violation (Unicode en-dashes in files the pipeline edited). The `previousCycleResolution` structure provides machine-verifiable proof that each gap was addressed — the gap-hunter does not just check that *something* changed, it verifies the specific content matches the expected fix.

The orchestrator's cascade reset for this run reset `pass4_execution`, `pass5_verification`, and `pass6_gapHunting` to `not-started`, as recorded in the manifest:

```json
{
  "agent": "docwriter",
  "action": "cascade reset — reEntryTarget=pass4, reset pass4_execution+pass5_verification+pass6_gapHunting to not-started (cycle 1, 3 gaps: GAP-001 clone perms, GAP-002 en-dashes, GAP-003 synchronize perms)"
}
```

On re-entry, the execution-coordinator only re-ran the 5 tasks affected by the gaps (out of 8 total), using style-only review mode since accuracy and persona reviews had already passed.

#### Pass 6.5 — Knowledge synthesis

This pass runs only after verification has fully converged (gap-hunter found zero new gaps, `reEntryTarget === null`). It is the learning system.

**task-signal-analyzer** examines per-task artifacts to extract knowledge signals: which task shapes succeeded on the first attempt, which required multiple revision cycles, which invariants were most frequently cited in rejections, which patterns from the knowledge brief were applied and with what effect.

**context-signal-analyzer** examines global pipeline artifacts to extract domain insights: research effectiveness, gap-hunting patterns, codebase complexity observations, documentation landscape evolution.

**knowledge-integrator** merges both signal sets into the persistent knowledge base (`meta/index.json`), calibrating confidence levels, promoting or demoting patterns based on new evidence, and applying quality gates (patterns need multiple confirmations before reaching high confidence).

**skill-rebuilder** reconstructs the skill reference files from the current state of the knowledge base, making the accumulated learning available to future pipeline runs.

Like Pass 0, this is non-blocking — synthesis failure does not prevent delivery.

**Artifacts produced:** `task-signals.json`, `context-signals.json`, updated `meta/` entries, rebuilt skill references
**Read by:** knowledge-curator (future runs), content-writer (future runs via skills), task-planner (future runs)

From the page-permissions run — the task-signal-analyzer produced execution statistics and per-task signals:

```json
{
  "runStats": {
    "totalTasks": 8,
    "firstAttemptAcceptance": 5,
    "multiCycleAcceptance": 3,
    "blocked": 0,
    "reEntryTasks": 5,
    "totalReviewCycles": 16,
    "gapsFound": 3,
    "gapsResolved": 3,
    "gapHuntingCycles": 2
  }
}
```

Per-task signals identify candidate patterns and anti-patterns from observation:

```json
{
  "taskId": "T-001",
  "result": "multi-cycle",
  "initialAttempts": 2,
  "reEntryAttempts": 1,
  "totalAttempts": 3,
  "acceptanceCriteria": 19,
  "gapsFixed": ["GAP-001", "GAP-003"],
  "rejectionAnalysis": {
    "rootCauses": [
      { "invariant": "INV-style-132", "description": "Used 'must' directed at people" },
      { "invariant": "INV-style-139", "description": "Multi-sentence callout lacked bold title" },
      { "invariant": "INV-persona-001", "description": "Front matter persona tag incomplete" }
    ]
  }
}
```

The context-signal-analyzer examines pipeline-level patterns. The gap signals are particularly valuable — they identify whether gaps were predictable from the available data:

```json
{
  "gapSignals": [
    {
      "gapId": "GAP-001",
      "gapType": "coverage-gap-operation-missing",
      "predictable": true,
      "predictableDetail": "Clone was explicitly listed in risk register as 'out of scope' but gap hunter found it needed documentation. The code-analysis permissionSummary included clonePage with full permission requirements.",
      "signal": {
        "type": "candidate-anti-pattern",
        "strength": "medium",
        "description": "Task planner excluded operations that code-analysis had fully documented. All operations with distinct permission requirements should be in scope."
      }
    }
  ]
}
```

The `predictable: true` flag means the gap could have been avoided if the task-planner had used the available data more thoroughly. This becomes an anti-pattern in the knowledge base: in future runs, the knowledge-brief will warn the task-planner not to exclude operations that the code-analysis has fully documented. This run produced 9 new knowledge entries and updated 3 existing ones.

#### Pass 7 — Delivery

**frontmatter-validator** validates Jekyll front matter, Liquid syntax, and build readiness for all created/modified documentation files. Machine-checkable invariants are enforced here.

**changelog-writer** produces a release notes entry summarizing all documentation changes — what was created, updated, and fixed, organized by product area.

The orchestrator emits `pipeline-summary.json` and signals completion.

**Artifacts produced:** `frontmatter-validation.json`, `changelog-entry.md`, `pipeline-summary.json`

From the page-permissions run — the frontmatter-validator checked all 8 modified files. Each result validates that the Jekyll front matter is build-ready:

```json
{
  "file": "page-permission-management.md",
  "taskId": "T-001",
  "frontMatter": {
    "valid": true,
    "fields": {
      "title": { "value": "Page permission management" },
      "identifier": { "value": "permissions_pagelevel_xp" },
      "persona": { "value": ["admin", "developer"] },
      "order": { "value": 100 }
    },
    "missingRequired": [],
    "invalidValues": []
  },
  "buildReady": true,
  "issues": []
}
```

The pipeline-summary captures the final state of the entire run:

```json
{
  "status": "complete",
  "tasksPlanned": 8,
  "tasksWritten": 8,
  "tasksBlocked": 0,
  "gapHuntingCycles": 2,
  "crossRefsVerified": {
    "outgoingLinksChecked": 190,
    "outgoingLinksValid": 190,
    "outgoingLinksBroken": 0
  },
  "metaKnowledge": {
    "patternsCurated": 6,
    "entriesNew": 9,
    "entriesUpdated": 3,
    "skillFilesRegenerated": 7
  },
  "research": {
    "recommendationsApproved": 8,
    "recommendationsBlocked": 4,
    "recommendationsAdapted": 2
  },
  "filesModified": [
    "page-permission-management.md", "edit-and-publish-pages.md", "workflows.md",
    "create-pages.md", "delete-pages.md", "security-guidelines.md",
    "content-versioning-configuration.md", "content-sync.md"
  ]
}
```

The `progress.json` state at completion shows the full pipeline state machine with all passes done and gap-hunting converged:

```json
{
  "currentPass": 7,
  "passStatus": {
    "pass0_knowledgeCuration": "done",
    "pass05_codebaseOrientation": "done",
    "pass1_discovery": "done",
    "pass2_analysis": "done",
    "pass3_planning": "done",
    "pass4_execution": "done",
    "pass5_verification": "done",
    "pass6_gapHunting": "done",
    "pass65_knowledgeSynthesis": "done",
    "pass7_delivery": "done"
  },
  "gapHunting": {
    "cyclesCompleted": 2,
    "newItemsPerCycle": [3, 0],
    "converged": true,
    "reEntryTarget": null
  },
  "counts": {
    "changesDiscovered": 4,
    "docPagesIndexed": 1800,
    "invariantsExtracted": 231,
    "impactsMapped": 38,
    "tasksPlanned": 8,
    "tasksWritten": 8,
    "tasksBlocked": 0
  }
}
```

The `newItemsPerCycle` array `[3, 0]` tells the story: cycle 1 found 3 gaps, cycle 2 found 0, convergence achieved. This entire state machine is how the orchestrator knows what to do — on any crash, it reads this file and resumes from the first non-done pass.

### Information flow: tracing a code change end-to-end

To make the artifact chain concrete, trace a single code change through the full pipeline:

1. A developer adds a new `roleExpiration` parameter to an API endpoint.

2. **diff-analyzer** (Pass 1) categorizes it in `change-inventory.json`:
   ```json
   { "file": "src/api/roles.ts", "changeType": "feature-addition",
     "symbols": ["roleExpiration"], "userFacing": true }
   ```

3. **code-analyzer** (Pass 2) traces the call chain and extracts docFacts:
   ```json
   { "behavioralImpact": { "userFacing": ["New optional parameter roleExpiration on POST /roles"] },
     "docFacts": { "parameters": [{ "name": "roleExpiration", "type": "ISO8601", "default": "null" }] } }
   ```

4. **impact-mapper** (Pass 2) cross-references against the corpus and determines which pages need work:
   ```json
   { "id": "IMP-007", "type": "update", "priority": "high",
     "targetPage": "docs/admin/role-management.md", "targetSections": ["Configuration", "API reference"] }
   ```

5. **task-planner** (Pass 3) creates a task with inlined invariants and docFacts:
   ```json
   { "id": "T-003", "action": "update", "targetFile": "docs/admin/role-management.md",
     "targetPersonas": ["administrator"], "docFacts": ["...extracted above..."],
     "invariants": ["INV-style-001", "INV-persona-008", "INV-codesamples-003"],
     "acceptanceCriteria": ["roleExpiration parameter documented with type and default",
                            "Code sample shows usage", "Cross-ref to expiration guide added"] }
   ```

6. **content-writer** (Pass 4) receives T-003 and writes the updated page. Its context contains the task definition, the existing page content, relevant source code, and nothing else.

7. **Three reviewers** (Pass 4) independently verify: style-reviewer checks formatting and structure, accuracy-reviewer traces every claim back to source code, persona-reviewer confirms admin-appropriate tone and depth.

8. **cross-ref-updater** (Pass 5) finds pages linking to role-management.md and updates any affected anchors.

9. **gap-hunter** (Pass 6) verifies the change was fully documented — no missing parameters, no stale content left untouched.

10. **changelog-writer** (Pass 7) includes the change in the release notes entry.

At no point did any single agent hold the full picture. The information moved through the system via artifacts on disk, each agent consuming exactly the upstream slice it needed.

### Prompt architecture: declarative to imperative

The agent-as-function architecture creates a natural gradient in prompt style across the hierarchy.

**The orchestrator's prompt is almost entirely declarative.** It describes the desired system state (all passes done, gap-hunting converged) and the routing table that moves toward it. There are no instructions to "read the code" or "write documentation" — the orchestrator does not know how to do those things. Its prompt encodes what the pipeline should look like when finished and the rules for state transitions.

**Coordinator prompts are semi-declarative.** They describe which specialists to dispatch, in what order, and what validation to perform on outputs. The analysis-coordinator knows that code-analyzer and research-scout can run in parallel, that impact-mapper depends on both their outputs, and that all specialist status files must show success before the coordinator marks the pass complete. But the coordinator does not know how code analysis works or what makes a good impact matrix.

**Specialist prompts are imperative.** The content-writer's prompt says: read this task definition, read the existing page at this path, read the relevant source files from code-analysis.json, apply these specific invariants, and produce an updated page plus a structured writer-output.json. There is no ambiguity about what to do.

This gradient mirrors the declarative-to-imperative transformation described in the main essay. The system-level prompt (context.json + orchestrator routing table) is fully declarative — it describes the desired end state and constraints. By Pass 4, the content-writer's prompt is fully imperative — it specifies exactly which file to read, which rules to follow, and what output to produce. The transformation happens automatically through the artifact chain: each phase's output is more concrete than its input, and each downstream agent's prompt is more imperative than its parent's.

The practical consequence is that when context compaction hits (and it will, inside the longer coordinator and specialist sessions), the damage is bounded. A specialist that loses track of some earlier context is still anchored by its explicit task definition, its inlined invariants, and its upstream artifacts. The imperative structure provides guardrails that pure declarative prompting would not.

### Self-convergence

The docwriter pipeline has two self-convergence loops, operating at different granularities.

**The write→review cycle** (within Pass 4) is the inner loop. For each task, the content-writer produces output, three reviewers evaluate it, and if any reviewer rejects, the writer revises. Each reviewer cites specific invariant IDs with pass/fail verdicts and evidence — the writer knows exactly what to fix. Maximum three attempts, then the task is marked blocked. This loop converges because the feedback is precise: it is not "this needs improvement" but "INV-style-007 failed because passive voice was used in the introduction paragraph."

**The gap-hunting cycle** (Pass 5-6 → re-entry) is the outer loop. After all tasks are written and reviewed, the gap-hunter performs an adversarial audit of the entire pipeline's output. If it finds gaps, the orchestrator cascade-resets the appropriate passes and re-runs them. On re-entry, work is preserved: only gap-affected tasks are modified or re-executed.

The combination means the system can handle both local quality issues (a single page fails review) and global coverage issues (a code change was never documented at all) without human intervention. The pipeline keeps looping until the gap-hunter reports zero findings or the maximum cycle count is reached.

The manifest tracks every iteration. If three consecutive gap-hunting cycles produce the same gap types, that is a clear signal the pipeline cannot self-resolve — it escalates rather than looping forever.

### Meta-knowledge extraction and application

The synthesis pipeline (Pass 6.5) is the docwriter's learning system. It runs only after verification converges, ensuring it analyzes the final state of all artifacts rather than intermediate revision states.

The signal analyzers extract structured observations:

- **task-signal-analyzer** identifies which task shapes (action + contentType + persona + complexity) succeed on the first attempt, which invariant counts correlate with acceptance, and which patterns from the knowledge brief were used effectively
- **context-signal-analyzer** identifies pipeline-level insights: which code areas generate the most documentation work, which research recommendations proved useful, which gap-hunting patterns recur

The knowledge-integrator merges these into the persistent knowledge base with confidence calibration: new patterns start at low confidence, get promoted after multiple confirmations across runs, and are demoted or archived when contradicted by new evidence.

On subsequent runs, the knowledge-curator (Pass 0) reads this accumulated knowledge base and produces a focused brief for the current task. The task-planner inlines relevant patterns into task definitions. The content-writer sees them alongside invariants and docFacts.

The result is a pipeline that gets better over time. The first run is cold-start — no patterns, no prior knowledge. By the third or fourth run, the knowledge brief carries observations like:

```json
{
  "id": "PAT-001",
  "title": "Focused single-persona developer update pages achieve first-attempt acceptance",
  "insight": "3/3 first-attempt successes share: action=update, contentType=howto, targetPersonas=[developer], estimatedComplexity=medium. Average invariants applied: 5.7. Confirmed across 3 pipeline runs with 80% acceptance rate when applied.",
  "confidence": "medium",
  "relevanceScore": 0.70,
  "consumers": ["task-planner", "content-writer"]
}
```

```json
{
  "id": "PAT-002",
  "title": "High invariant count correlates with first-attempt success for update tasks",
  "insight": "First-attempt tasks averaged 13.1 invariants vs multi-cycle tasks 6.7. The 3 highest invariant counts (18-29 invariants) all achieved first-attempt acceptance. Promoted to HIGH confidence across 3 pipeline runs.",
  "confidence": "high",
  "relevanceScore": 0.72,
  "consumers": ["task-planner", "content-writer"]
}
```

These patterns directly influence the task-planner's behavior: it front-loads invariants more aggressively, structures tasks to match proven successful shapes, and avoids configurations that historically triggered multi-cycle revisions. The pipeline's convergence speed improves across runs without any change to the agent prompts themselves — the improvement flows entirely through the artifact layer.

### Cross-run knowledge persistence

![Cross-run persistence flow](docwriter/_docwriter-cross-run-persistence.drawio.svg)

The meta-knowledge system is not just a post-run summary. It is a persistent, structured knowledge base that accumulates across pipeline runs, providing downstream agents with increasingly precise guidance as runs accumulate.

After 4 pipeline runs against the same documentation workspace, the knowledge base contains 73 entries across 7 types: 12 patterns, 12 anti-patterns, 31 domain insights, 6 style evolutions, 12 source observations, and entries in two new operational collections — gap patterns and impact patterns. 10 of these entries have been confirmed across 3+ runs and promoted on the confidence ladder. 4 have reached `high` confidence — the maximum, requiring observation in 3+ runs with >80% acceptance rate when applied.

#### The confidence ladder

Every knowledge entry follows a strict promotion/demotion lifecycle:

| Level | Criteria | TTL |
|---|---|---|
| `low` | Single observation in a single run | 180 days |
| `medium` | Confirmed in 2+ tasks or observed in 2+ separate runs | 365 days |
| `high` | Observed in 3+ runs AND >80% acceptance rate when applied | unlimited |

Promotion never skips levels. A brand-new signal starts at `low` regardless of how compelling it appears. Promotion to `medium` requires a second independent observation. Promotion to `high` requires a third run plus quantitative validation. This prevents the knowledge base from being corrupted by single-run flukes.

The TTL (time-to-live) mechanism prevents stale knowledge from accumulating. An entry that has not been re-referenced within its TTL window decays one step:

- `high` → `medium` after 365 days unreferenced
- `medium` → `low` after 180 days unreferenced
- `low` → deprecated after 180 days unreferenced

The knowledge-integrator runs this decay sweep at the start of every synthesis pass, before processing new signals. The knowledge-curator uses `effectiveConfidence` (the post-decay level) rather than the original `confidence` for relevance scoring. An entry that was once `medium` but has decayed to `low` scores lower in the curation brief, reducing its influence on downstream agents proportional to how long it has been since the pipeline actually confirmed it.

From the real knowledge base — PAT-001 ("Focused single-persona developer update pages achieve first-attempt acceptance") has been referenced in 10 tasks across 4 runs. It was discovered in the first run at `low`, promoted to `medium` after the second run confirmed it, and has maintained `medium` because its acceptance rate when applied is 70% — short of the 80% threshold for `high`. PAT-002 ("High invariant count correlates with first-attempt success") reached `high` after run 3, with an acceptance rate of 87% across 3 tasks where it was applied.

#### Contradiction detection

Promotion is only half the story. The knowledge base also needs to detect when previously trusted patterns become wrong.

The task-signal-analyzer (A4) watches for contradictions: cases where a content-writer cited a pattern from the knowledge brief (`metaPatternsUsed` in `writer-output.json`) but a reviewer then rejected the task specifically because of the approach that pattern prescribed. A general rejection that happens to occur in a task using a pattern is not a contradiction — the reviewer must explicitly cite the pattern's approach as the problem.

When a contradiction is detected:

- A `medium`-confidence entry is immediately demoted to `low`
- A `high`-confidence entry increments a `contradictionCount`. After 2 contradictions, it demotes to `medium`
- The entry's markdown file gains a `## Contradictions` section with the evidence trail

Contradictions are processed before confirmation signals in each synthesis cycle. This prevents a situation where a new run both contradicts and re-confirms a pattern — the demotion happens first, and re-confirmation must then re-earn the confidence through the normal promotion path.

Anti-pattern violations work in the reverse direction: when the brief warned about an anti-pattern but the writer violated it anyway (and the reviewer subsequently rejected the task), this confirms the anti-pattern and strengthens it.

#### Gap patterns and impact patterns: operational memory

The original knowledge types — patterns, anti-patterns, domain insights, style evolutions, source observations — capture what the pipeline learned about documentation quality. Two additional collections capture what the pipeline learned about its own operational behavior.

**Gap patterns** (`meta/gap-patterns/GAP-NNN.md`) record which change domains produce which types of gaps, with root-cause classifications. When the context-signal-analyzer processes `gap-analysis.json` at the end of a run, it extracts a reusable predictor for each gap: "When [change domain] changes, [gap type] tends to occur because [root cause]."

Root cause categories: `missing-cross-ref`, `stale-content`, `undocumented-behavior`, `incomplete-coverage`, `scope-miss`, `encoding-violation`. Each gap pattern carries the `changeDomain` (from `change-inventory.json`) and the `impactType` (from `impact-matrix.json`) that produced it.

The gap-hunter consumes these directly in its Step 6 history-informed hunting. Before running its standard audit, it reads all `GAP-NNN` entries and checks whether the current run's change-inventory contains areas matching any pattern's `changeDomain`. If yes, it proactively verifies the predicted gap didn't recur — checking the specific pages and cross-references the pattern identifies as commonly missed.

From the actual pipeline runs — across 4 runs, 6 gaps were found (5 in the membership-roles run alone). The most frequent root cause was `missing-cross-ref` (cross-references between authentication pages and business-user pages). The pattern extracted from this: "When membership/authentication APIs change, cross-references from `secure-pages.md` and `member-roles.md` are frequently missed." On subsequent runs touching authentication areas, the gap-hunter now checks these specific pages proactively rather than discovering the gaps reactively.

**Impact patterns** (`meta/impact-patterns/IMP-NNN.md`) record which code areas consistently affect which documentation clusters. When the context-signal-analyzer observes that changes in AREA-003 (authentication/membership) consistently produce impacts in both the "Registration & Authentication" and "Website Content" topic clusters, it emits an impact pattern with that mapping.

The impact-mapper consumes these as warm-start data. Instead of rediscovering the same area→cluster mappings from scratch on every run by cross-referencing change-inventory against doc-index, it reads existing `IMP-NNN` entries and uses matching patterns' `targetClusters` and `targetPages` as initial candidates. It still verifies each candidate against the actual change — patterns are starting points, not guaranteed matches.

From the pipeline runs — 10 documentation pages were impacted in 2+ runs. The authentication/membership area consistently produces impacts in both developer-facing API reference pages and business-user-facing pages about secure content. Without impact patterns, the impact-mapper would rediscover this mapping each time by string-matching area names against topic clusters. With the patterns, it starts with a pre-validated candidate set and focuses its analysis on confirming which candidates apply to this specific change.

Both gap patterns and impact patterns follow the same confidence ladder as other knowledge types. A single-run observation starts at `low`. Confirmation across runs promotes to `medium`. The deduplication key for gap patterns is `rootCause + changeDomain`; for impact patterns, it's `sourceAreaPattern + targetClusters`. Entries accumulate `occurrenceCount` — the more runs that confirm the pattern, the more weight it carries.

#### Three read channels

![Knowledge consumption channels](docwriter/_docwriter-knowledge-consumption.drawio.svg)

Knowledge flows from the persistent `meta/` directory to downstream agents through three distinct channels:

1. **Knowledge brief** (`knowledge-brief.json`) — the curator scores all entries, selects the top 20 by relevance to the current task, and groups them by consumer. Read by: task-planner, content-writer, style-reviewer, accuracy-reviewer, gap-hunter. This is the primary channel for patterns, anti-patterns, domain insights, style evolutions, and retrospective lessons.

2. **Skill reference files** (`.github/skills/docwriter-meta/references/*.md`) — the skill-rebuilder produces human-readable summaries of the full knowledge base, organized by type. Read by: code-analyzer, task-planner, content-writer, style-reviewer, gap-hunter. These provide broader context than the brief — the brief is filtered by task relevance, but the skill files contain everything.

3. **Direct meta reads** — some agents read raw `meta/` entries directly. The gap-hunter reads `meta/gap-patterns/` for proactive blind-spot checking. The impact-mapper reads `meta/impact-patterns/` for warm-start area→cluster mapping. The codebase agents read `meta/codebase-map.json` for structural orientation. The research-scout reads `meta/research-sources.json` for curated source URLs.

Gap patterns and impact patterns deliberately use channel 3 (direct reads) rather than channel 1 (the brief). This is because they serve operational purposes that require the full entry — the gap-hunter needs the exact `predictor` statement and `changeDomain` to verify against the current run, and the impact-mapper needs the specific `targetClusters` and `targetPages` to seed its candidate set. The brief's compressed one-liner summaries would lose the actionable detail.

Each channel has exactly one exclusive writer:
- `meta/*` → knowledge-integrator only
- `meta/codebase-map.json` → codebase-curator only
- `knowledge-brief.json` → knowledge-curator only
- Skill reference files → skill-rebuilder only

No agent both reads and writes the same knowledge artifact. This prevents feedback loops where an agent's own output influences its future input within the same run.

#### Cross-run improvement trajectory

The pipeline's actual performance across runs demonstrates the knowledge system's effect:

| Run | Tasks | First-attempt rate | Patterns discovered | Entries updated | Knowledge base size |
|---|---|---|---|---|---|
| DOC-2847 (run 1) | 10 | 70% | 2 | 5 | ~15 |
| DOC-3167 (run 2) | 8 | 62.5% | 1 | 3 | ~30 |
| DOC-3167 (run 3) | 18 | 72% | 0 | 11 | ~55 |
| DOC-3187 (run 4) | 17 | 18% | 7 | 0 | 73 |

Run 4's anomalously low first-attempt rate (18%) is instructive — it was a fundamentally different task scope (first run against a new content area with no domain coverage in the knowledge base). The 7 new patterns discovered in that run confirm the system's response: when existing knowledge doesn't apply, the pipeline reverts to cold-start behavior and extracts new domain-specific knowledge aggressively.

The knowledge base grew from 0 to 73 entries across 4 runs. Of those 73: 4 reached `high` confidence, 26 have been referenced in 2+ runs, and the rest remain at `low` — single-run observations awaiting confirmation. With TTL-based decay now active, the `low`-confidence entries that are never re-confirmed will automatically deprecate after 180 days, keeping the knowledge base focused on validated insights.

### Discoveries: the bottom-up information channel

The artifact flow described so far is top-down: the orchestrator dispatches coordinators, coordinators dispatch specialists, specialists read upstream artifacts and produce downstream ones. Information moves through planned channels — change-inventory feeds code-analysis, which feeds impact-matrix, which feeds task-graph.

Discoveries are the reverse channel. They are a mechanism for leaf-level specialists to surface observations that fall outside their immediate task scope but are relevant to the pipeline's completeness.

Any specialist can write a discovery file to `.docwriter/discoveries/`. Five agents are instrumented to produce them: code-analyzer, content-writer, impact-mapper, research-scout, and cross-ref-updater. A discovery is something the specialist noticed while doing its primary work that does not belong in its primary output artifact — an undocumented behavior in an adjacent code area, a missing coverage gap in a page the specialist was not assigned to update, a cross-cutting concern that spans multiple tasks.

The discovery schema:

```json
{
  "id": "DISC-CA-001",
  "type": "undocumented-behavior",
  "summary": "UnpublishInternal does NOT check workflow step roles — unlike Save, Discard, ChangeWorkflowStep, and CancelScheduledPublish which all call CanWorkWithContentItemInCurrentStep. A user with Update ACL can unpublish a page even if they have no role assigned to the current workflow step.",
  "evidence": "WebPageCommandManagerBase.cs:734-756 — UnpublishInternal checks only VersionStatus conditions with no call to CanWorkWithContentItemInCurrentStep.",
  "suggestedAction": "Document this exception in the operation-specific permission requirements.",
  "affectedArea": "workflow-permissions",
  "severity": "high"
}
```

Each field serves a distinct role:

- **`id`** — prefixed by producing agent (`DISC-CA-*` for code-analyzer, `DISC-IM-*` for impact-mapper, `DISC-CW-*` for content-writer, `DISC-RS-*` for research-scout, `DISC-XR-*` for cross-ref-updater). This makes the provenance immediately traceable.
- **`type`** — one of `undocumented-behavior`, `missing-coverage`, `stale-content`, `cross-cutting-concern`, or `scope-expansion`. The gap-hunter maps these to its own gap types when triaging.
- **`evidence`** — concrete file paths and line numbers, not vague observations. This is what distinguishes a discovery from a guess — the specialist has already looked at the code or content and can cite exactly what it found.
- **`suggestedAction`** — what the specialist thinks should be done. The gap-hunter can override this, but it provides a starting signal for triage.
- **`severity`** — the specialist's assessment. High-severity discoveries are more likely to be converted to gaps; low-severity ones are more likely to be marked out-of-scope.

Discovery files are named by producer, context, and cycle: `code-analyzer--AREA-003--c1.json`, `impact-mapper--global--c1.json`. No other agent reads them — they sit untouched in the `discoveries/` directory until the gap-hunter consumes them in Pass 6, Step 7.

From the page-permissions run — the code-analyzer produced 5 discoveries while analyzing AREA-003 (workflow commands). These were behaviors it noticed that were adjacent to but outside its assigned analysis scope:

```json
{
  "id": "DISC-CA-005",
  "type": "cross-cutting-concern",
  "summary": "Delete operations use evaluateChildPages=true when checking DELETE ACL — meaning the user needs Delete permission not just on the page but also on all child pages with broken ACL inheritance. This subtree permission check is unique to delete and move operations.",
  "evidence": "WebPagesApplication.cs:528 — CheckAclPermission(args.WebPageItemId, WebPageAclPermissions.DELETE, true, ...)",
  "suggestedAction": "Document that delete-with-children requires Delete permission on the target page AND all child pages that have broken ACL inheritance.",
  "affectedArea": "page-permissions",
  "severity": "high"
}
```

The impact-mapper produced 5 discoveries about missing permission coverage in adjacent documentation pages:

```json
{
  "id": "DISC-IM-005",
  "type": "cross-cutting-concern",
  "summary": "Clone page operation mentions that 'page permissions are not cloned' but does not mention what permissions are needed TO clone — code analysis shows Read on source + Read + Create on target parent.",
  "evidence": "create-pages.md line 31 mentions 'page permissions are not cloned' but the Clone procedure steps have no permission prerequisite.",
  "suggestedAction": "Add a brief permission note to the Clone section.",
  "affectedArea": "page-operations",
  "severity": "medium"
}
```

This particular discovery (DISC-IM-005) is the one that eventually became GAP-001 — the clone permission gap that triggered the re-entry cycle. The impact-mapper spotted the issue during its Pass 2 work, wrote it as a discovery because it was outside its impact-mapping scope, and the gap-hunter picked it up in Pass 6 and converted it to a formal gap.

#### Why discoveries exist as a separate mechanism

The alternative would be to expand each specialist's primary output to include adjacent findings. The code-analyzer could put workflow observations into `code-analysis.json`. The impact-mapper could add speculative impacts to `impact-matrix.json`. But this would contaminate the primary artifacts:

- **`code-analysis.json`** is consumed by the task-planner, content-writer, and accuracy-reviewer. Adding speculative adjacent findings would expand those agents' context with information that may not be relevant to their tasks.
- **`impact-matrix.json`** feeds directly into task planning. Speculative impacts would create tasks for unverified observations.

Discoveries keep the primary artifacts clean while providing a structured channel for bottom-up information flow. The gap-hunter is the single consumer — it has the full pipeline context needed to triage discoveries against the completed work and decide which ones represent real gaps.

#### The triage process

The gap-hunter's Step 7 processes all discovery files:

1. Parse every discovery in `discoveries/*.json`
2. Cross-reference against gaps already found in Steps 1–6 to deduplicate — if a discovery describes the same issue as an existing gap, skip it or add its evidence to the gap
3. Convert novel discoveries to formal gap entries with appropriate `reEntryTarget` values
4. Mark out-of-scope discoveries (like DISC-IM-003 about headless content) as dispositioned without creating gaps

In the page-permissions run, 10 discoveries were filed (5 from code-analyzer, 5 from impact-mapper). The gap-hunter processed all 10: some were deduplicated against gaps it had already found independently, some added evidence to existing gaps, and some were dispositioned as out-of-scope. The discovery that became GAP-001 (clone permissions) and the one that contributed to GAP-003 (synchronize permissions) both originated from this bottom-up channel.

