---
id: ANTI-006
title: "Collection-specific structural conventions not audited before creating new pages cause complete rewrites"
type: anti-pattern
confidence: low
domains: ["api-reference", "page-creation", "pipeline-process", "xperience-platform"]
discoveredDate: "2026-03-15T06:23:39Z"
lastReferencedDate: "2026-03-15T06:23:39Z"
usageCount: 1
sourceTasks: ["T-002", "T-003"]
invariantsReferenced: []
sourceSignals: ["SIG-004", "GAP-003", "SE-004"]
deprecated: false
---

## Insight

When creating new pages in an existing collection directory, the task planner and content writer MUST audit sibling pages for structural conventions before writing. The _api collection follows a code-examples-only convention with companion .cs source files — this was not captured in the invariant inventory and caused the costliest rework in the pipeline (2 complete page rewrites + 2 companion .cs file creations). The invariant scanner processes guidelines files but not sibling page conventions — a systematic blind spot.

## Evidence

- T-002 and T-003 were initially written as standard API reference pages (prose, tables, admonitions) but the _api collection requires strict code-examples-only format
- Required complete rewrites including creation of companion .cs source files
- Discovered by gap-hunter in cycle 2, not caught by initial task planning
- Signal strength: high (2 tasks, high-impact rework)
- Confidence: low (first observation in a single run)

## Recommendation

For new pages in existing directories, add an acceptance criterion: "Content writer must structurally audit 2+ sibling pages and match their convention before drafting." The task planner should provide a structural template derived from sibling analysis.

## Applicability

Applicable to any pipeline run creating new pages in existing collection directories, especially _api and other collections with non-standard conventions.
