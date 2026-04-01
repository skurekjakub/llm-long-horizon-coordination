---
id: ANTI-002
title: "Style invariant INV-formatting-016 (em dash vs en dash) is the most frequent ..."
type: anti-pattern
confidence: low
domains: ["how-to", "style-formatting", "invariant-system"]
discoveredDate: "2026-03-14T16:06:35+00:00"
lastReferencedDate: "2026-03-15T18:03:22Z"
usageCount: 3
sourceTasks: ["TASK-007", "TASK-010", "TASK-014", "DOC-2847-T-008"]
invariantsReferenced: ["INV-formatting-016"]
sourceSignals: ["SIG-003", "AGG-003"]
deprecated: false
---

## Insight

INV-formatting-016 triggered rejections in 3 tasks (TASK-007, TASK-010, TASK-014). Writers consistently produce em dashes (—) when the style guide requires en dashes (–).

## Evidence

### Run 2 (DOC-3137)

- Run 2 (DOC-3137): Em dash rejections in T-010, T-011, T-016 (3/16 tasks, 19%). T-009 proactively cited ANTI-002 and avoided the error, showing explicit awareness helps.
- Acceptance rate across 2 runs: confirmed
- Promoted: low → medium (2nd pipeline run confirmation)

### Run 1 (original)

- Source signal: AGG-003 (from task-signals)
- Within-run strength: single observation
- Tasks referenced: TASK-007, TASK-010, TASK-014
- Confidence: low (cold-start run — first observation)

## Recommendation

Add explicit em-dash/en-dash guidance to the content writer's pre-writing checklist. Consider a post-write automated check before human review.

### Run 3 (DOC-2847) — DEMOTION

- Run 3 (DOC-2847): T-008 had a style rejection for double-hyphen '--' instead of en dash '–' (INV-style-089). ANTI-002 was included in the knowledge brief warning about em dashes specifically, but the writer produced a dash-type variant error (double-hyphen→en-dash, not em dash→en dash). The brief's warning was variant-incomplete — it focused on em dashes while the actual violation was a different dash-type confusion.
- Demoted: medium → low (anti-pattern violated in run 3 despite being briefed; variant gap in the description)
- **Note**: The anti-pattern description should be broadened to cover ALL dash-type confusions (em dash, en dash, double hyphen, minus sign), not just em dash vs en dash.

## Applicability

Applicable to all pipeline runs involving prose documentation. **DEMOTED** due to variant gap. The original em dash focus was too narrow — writers can confuse multiple dash types (em dash ——, en dash –, double hyphen --, minus sign -). Future briefs should enumerate all dash-type variants and their correct usage contexts.
