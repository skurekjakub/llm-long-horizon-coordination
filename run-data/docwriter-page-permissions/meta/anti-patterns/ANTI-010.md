---
id: ANTI-010
title: Writers trust pre-existing code examples without verifying API surface, propagating phantom method calls
type: anti-pattern
confidence: low
domains: ["api-reference", "code-samples", "accuracy"]
discoveredDate: "2026-03-15T18:03:22Z"
lastReferencedDate: "2026-03-15T18:03:22Z"
usageCount: 2
sourceTask: DOC-2847
invariantsReferenced: ["INV-codesamples-004"]
deprecated: false
---

## Insight

When a writer's task is scoped to "add named parameters" or "update syntax" on existing code examples in .md documentation files, the writer faithfully preserves all pre-existing code — including non-existent API method calls. The writer's mental model is "transform syntax, don't change behavior," which is correct for the task scope but silently propagates accuracy errors.

Root cause: `.md` documentation code blocks are not compiled. `INV-codesamples-004` (build verification) catches these for `.cs` files, but documentation code blocks bypass that safety net. Accuracy review is the only catch mechanism, and it requires method-by-method verification against the actual type hierarchy.

Specific phantom methods found in DOC-2847:
- `TopN()` on `RetrieveCurrentPageQueryParameters` — inherits `RetrieveQueryParametersBase` which has no `TopN` (source: `RetrieveQueryParametersBase.cs`)
- `OrderByDescending()` at 3 locations — does not exist on any `ContentRetriever` query parameter type; correct API is `OrderBy(OrderByColumn.Desc(...))` (source: `RetrieveQueryParametersBase.cs`)

## Evidence

- DOC-2847 T-001: `TopN(3)` preserved in code example, rejected by accuracy reviewer cycle 1, fixed to `Columns("ArticleTitle")`
- DOC-2847 T-002: `OrderByDescending()` at 3 locations, took 2 accuracy review cycles to find all instances across 1000+ line document
- Combined: 6 phantom method calls in 2 tasks, 5 review cycles to fully resolve

## Mitigation

For documentation (.md) code examples, task acceptance criteria should include: "Verify all API method calls in modified code blocks exist on their respective types — not just the newly-added named parameters." The accuracy reviewer must trace each method call back to the actual type hierarchy in the source code.
