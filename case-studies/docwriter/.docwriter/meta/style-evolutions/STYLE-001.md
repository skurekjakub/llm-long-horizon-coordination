---
id: STYLE-001
title: "Em dash (—) vs en dash (–) enforcement triggered rejections in 3 tasks (TASK-007"
type: style-evolution
confidence: high
domains: ["style-formatting", "invariant-system"]
discoveredDate: "2026-03-14T16:06:35+00:00"
lastReferencedDate: "2026-03-20T09:04:44Z"
usageCount: 3
sourceTasks: ["TASK-007", "DOC-3167-T-003", "DOC-3167-T-005"]
invariantsReferenced: ["INV-formatting-016", "INV-style-096"]
sourceSignals: ["SE-001", "STYLE-EVO-001", "CAPAT-001"]
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

### Run 4 (DOC-3167)

- Run 4 (DOC-3167): INV-style-096 (en-dash normalization to `--`) was the most frequently enforced invariant across all 18 tasks. Caused rejections in T-005 (3 pre-existing en-dashes), drove gap remediation in T-003 (7 en-dashes) and T-006/T-018 (heading/anchor en-dashes).
- The invariant identifier evolved from INV-formatting-016 (em dash) to INV-style-096 (en-dash to `--`), confirming the broader dash-type confusion pattern.
- 100% of tasks (18/18) applied INV-style-096. The invariant is correctly specified but full-page scanning is systematically under-applied.
- **Promoted: medium → high** (3rd pipeline run confirmation, consistent observation across runs 1, 2, and 4)

## Applicability

**HIGH CONFIDENCE**: Applicable to all pipeline runs. Dash-type enforcement (em dash, en dash, double-hyphen) is the most persistent and impactful style issue across 3+ pipeline runs. The observation is stable: writers handle dash types correctly in new content but fail to scan existing content for pre-existing violations. Suggests automated pre-submission encoding check.
