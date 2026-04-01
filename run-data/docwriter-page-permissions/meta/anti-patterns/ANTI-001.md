---
id: ANTI-001
title: "Create-action pages have higher rejection rates than updates"
type: anti-pattern
confidence: medium
domains: ["page-creation", "cross-references", "invariant-system"]
discoveredDate: "2026-03-14T16:06:35+00:00"
lastReferencedDate: "2026-03-15T06:23:39Z"
usageCount: 2
sourceTasks: ["TASK-001", "TASK-002"]
invariantsReferenced: ["INV-crossref-001", "INV-structure-001", "INV-frontmatter-004"]
sourceSignals: ["SIG-002", "AGG-002"]
deprecated: false
---

## Insight

Create tasks (TASK-001, TASK-002) averaged 2.5 attempts vs update tasks averaged 1.9 attempts. Create tasks triggered frontmatter (INV-frontmatter-004), cross-ref (INV-crossref-001), and structural (INV-structure-001) rejections that don't apply to updates.

## Evidence

### Run 2 (DOC-3137)

- Run 2 (DOC-3137): All 3 create tasks required multi-cycle rework. Average create attempts: 3.33 vs update 1.33. Create tasks consumed 40% of total writer attempts despite being 19% of tasks. Anti-pattern strongly confirmed.
- Acceptance rate across 2 runs: confirmed
- Promoted: low → medium (2nd pipeline run confirmation)

### Run 1 (original)

- Source signal: AGG-002 (from task-signals)
- Within-run strength: single observation
- Tasks referenced: TASK-001, TASK-002
- Confidence: low (cold-start run — first observation)

## Recommendation

Create-action tasks need explicit writer briefing on: redirect_from derivation from identifier, required page sections (Title/Intro/Body/Result/Next Steps), and page_link identifier verification.

## Applicability

Applicable to future pipeline runs involving page-creation, cross-references, invariant-system documentation domains. Promoted to medium after confirmation in second pipeline run (DOC-3137).
