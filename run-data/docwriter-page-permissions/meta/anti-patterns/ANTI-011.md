---
id: ANTI-011
title: Incomplete mechanical bulk conversion misses code blocks within a page
type: anti-pattern
confidence: low
domains: ["code-samples", "task-planning"]
discoveredDate: "2026-03-15T18:03:22Z"
lastReferencedDate: "2026-03-15T18:03:22Z"
usageCount: 1
sourceTask: DOC-2847
invariantsReferenced: []
deprecated: false
---

## Insight

When a documentation page has many code blocks requiring the same transformation (e.g., positional→named parameter conversion), the task planner may scope one task to the page without auditing every code block. The writer then converts most blocks but misses a subset, leaving the page in an inconsistent state where some code blocks use the new syntax and others use the old.

GAP-001 in DOC-2847 found 2 of 9 code blocks in `retrieve-content-items.md` were missed by T-007 (which correctly converted the other 7). The risk register flagged T-007 as medium technicalAccuracy but did not anticipate incomplete coverage.

Distinct from ANTI-004 (interface method enumeration completeness): ANTI-004 targets *listing all methods of an interface*, while this anti-pattern targets *transforming all code blocks on a page*. Both are enumeration completeness failures but in different dimensions.

## Evidence

- DOC-2847 GAP-001: 2/9 code blocks missed in retrieve-content-items.md by T-007, caught by gap hunter cycle 1, resolved by T-010
- Risk register predicted medium technicalAccuracy but not incomplete coverage
- Acceptance rate: N/A (gap was caught outside normal task flow)

## Mitigation

For bulk mechanical conversions, task acceptance criteria should include an explicit completeness check: "Enumerate all code blocks on the target page, confirm each is addressed or explicitly excluded with rationale." The task planner should provide the exact count of code blocks requiring transformation.
