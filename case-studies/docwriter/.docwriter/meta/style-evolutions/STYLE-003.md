---
id: STYLE-003
title: "Empty redirect_from frontmatter triggered rejections in 2 tasks (TASK-001, TASK-"
type: style-evolution
confidence: medium
domains: ["page-creation", "style-formatting", "invariant-system"]
discoveredDate: "2026-03-14T16:06:35+00:00"
lastReferencedDate: "2026-03-15T06:23:39Z"
usageCount: 2
sourceTasks: ["TASK-001"]
invariantsReferenced: ["INV-frontmatter-004"]
sourceSignals: ["SIG-R2-metaknowledge", "STYLE-EVO-003"]
deprecated: false
---

## Insight

Create-action pages consistently get empty redirect_from arrays. Writers need explicit guidance to derive redirect_from from identifier pattern (x/<identifier>).

## Evidence

### Run 2 (DOC-3137)

- Run 2 (DOC-3137): No empty redirect_from issues on create-action pages T-001, T-002, T-003. Mitigation from brief was effective — writer correctly derived redirect_from values. Anti-pattern avoidance confirmed.
- Acceptance rate across 2 runs: confirmed
- Promoted: low → medium (2nd pipeline run confirmation)

### Run 1 (original)

- Source signal: STYLE-EVO-003 (from task-signals)
- Within-run strength: moderate (2 tasks)
- Tasks referenced: TASK-001
- Confidence: low (cold-start run — first observation)

## Recommendation

See insight above for actionable guidance.

## Applicability

Applicable to future pipeline runs involving page-creation, style-formatting, invariant-system documentation domains. Promoted to medium after confirmation in second pipeline run (DOC-3137).
