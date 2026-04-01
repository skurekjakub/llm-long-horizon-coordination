---
id: STYLE-001
title: "Em dash (—) vs en dash (–) enforcement triggered rejections in 3 tasks (TASK-007"
type: style-evolution
confidence: medium
domains: ["style-formatting", "invariant-system"]
discoveredDate: "2026-03-14T16:06:35+00:00"
lastReferencedDate: "2026-03-15T06:23:39Z"
usageCount: 2
sourceTasks: ["TASK-007"]
invariantsReferenced: ["INV-formatting-016"]
sourceSignals: ["SE-001", "STYLE-EVO-001"]
deprecated: false
---

## Insight

Writers consistently produce em dashes when en dashes are required. INV-formatting-016 is well-defined but writers need stronger pre-writing guidance on dash types.

## Evidence

### Run 2 (DOC-3137)

- Run 2 (DOC-3137): Em dash rejections in 3/16 tasks (T-010, T-011, T-016). Persistent writer confusion confirmed across both pipeline runs.
- Acceptance rate across 2 runs: confirmed
- Promoted: low → medium (2nd pipeline run confirmation)

### Run 1 (original)

- Source signal: STYLE-EVO-001 (from task-signals)
- Within-run strength: strong (3+ tasks)
- Tasks referenced: TASK-007
- Confidence: low (cold-start run — first observation)

## Recommendation

See insight above for actionable guidance.

## Applicability

Applicable to future pipeline runs involving style-formatting, invariant-system documentation domains. Promoted to medium after confirmation in second pipeline run (DOC-3137).
