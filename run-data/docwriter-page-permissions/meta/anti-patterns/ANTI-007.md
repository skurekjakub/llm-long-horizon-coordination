---
id: ANTI-007
title: "Async persistence mental models produce systematic accuracy errors in event-based documentation"
type: anti-pattern
confidence: low
domains: ["api-reference", "xperience-platform", "activity-logging"]
discoveredDate: "2026-03-15T06:23:39Z"
lastReferencedDate: "2026-03-15T06:23:39Z"
usageCount: 1
sourceTasks: ["T-005", "T-010", "T-011"]
invariantsReferenced: []
sourceSignals: ["SIG-006", "DI-007"]
deprecated: false
---

## Insight

Writers naturally assume synchronous database persistence when documenting logging/event services, but Xperience activity logging uses in-memory queuing with bulk inserts. This mental model mismatch produced ALL accuracy errors in the DOC-3137 run: T-010 wrote "saved to the database" (actually queued in memory), "ActivityID is available" (actually 0 at event fire time). T-011 used misleading "standard pipeline" label. T-005 attributed email clicks to wrong pipeline path.

## Evidence

- T-010: 4 accuracy errors all stemming from incorrect persistence mental model
- T-011: misleading "standard pipeline" label for email click logging
- T-005: 2 pipeline behavior errors (wrong logging path for email clicks, incomplete form submission path)
- All accuracy errors in this run were persistence/pipeline-semantics related
- Signal strength: medium (3 tasks, systematic pattern)
- Confidence: low (first observation in a single run)

## Recommendation

For any task documenting event timing, data flow, or pipeline stages, the writer should be briefed with a docFact covering the async persistence model. Prohibited language: "saved to database", "persisted", "stored" without qualification. Required framing: "queued in memory" or "logged" (not "saved").

## Applicability

Applicable to Xperience activity logging documentation and generalizable to any event/pipeline documentation where the persistence model is async or batched.
