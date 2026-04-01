---
id: ANTI-009
title: "Structural rewrites of linked pages invalidate link text descriptions on referring pages"
type: anti-pattern
confidence: low
domains: ["cross-references", "pipeline-process"]
discoveredDate: "2026-03-15T06:23:39Z"
lastReferencedDate: "2026-03-15T06:23:39Z"
usageCount: 1
sourceTasks: ["T-001"]
invariantsReferenced: []
sourceSignals: ["GAP-004"]
deprecated: false
---

## Insight

When a gap fix causes a structural rewrite of a page, link text descriptions on referring pages may become semantically inaccurate even though the link targets remain valid. The cross-ref updater validates link target existence but not link text semantic accuracy. GAP-004: T-001 promised "complete list of IActivityInfo properties" but after GAP-003 restructure, T-002/T-003 no longer contained property tables.

## Evidence

- GAP-004: T-001 lines 126 and 186 contained misleading link text after T-002/T-003 restructure
- Cross-ref updater confirmed links resolved to valid pages but did not check link text accuracy
- Cascade effect of GAP-003 structural fix
- Force-converged at cycle 3 safety valve (suitable for manual correction)
- Signal strength: medium
- Confidence: low (first observation in a single run)

## Recommendation

After structural rewrites, verify all incoming link texts against the new page content. Add a link-text-accuracy check to the cross-ref updater for pages that undergo structural changes.

## Applicability

Applicable to any pipeline run where gap hunting triggers structural rewrites of pages that have incoming cross-references.
