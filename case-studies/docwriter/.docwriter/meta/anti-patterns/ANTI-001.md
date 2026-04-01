---
id: ANTI-001
title: "Create-action pages have higher rejection rates than updates"
type: anti-pattern
confidence: medium
domains: ["page-creation", "cross-references", "invariant-system"]
discoveredDate: "2026-03-14T16:06:35+00:00"
lastReferencedDate: "2026-03-20T09:04:44Z"
usageCount: 3
sourceTasks: ["TASK-001", "TASK-002", "DOC-3167R4-T-001"]
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

### Run 4 (DOC-3167 — 18-task execution)

- Run 4: The sole create task (T-001, 23 acceptance criteria, code samples) required 2 attempts. Style rejections (contraction inconsistency INV-style-125/126, wrong UI verb INV-style-130) AND accuracy rejections (wrong namespace for RegisterScheduledTaskAttribute, .Internal namespace conflict for IDateTimeNowService).
- Create task consumed 2 of 24 total review cycles (8.3%) despite being 1 of 18 tasks (5.6%).
- Update tasks with ≤6 criteria achieved 80% first-attempt success. Create task: 0% first-attempt.
- Anti-pattern confirmed across 3 runs: Run 1 (0/2 first-attempt creates), Run 2 (0/3), Run 4 (0/1) = **0% aggregate create first-attempt rate**.
- Confidence held at **medium**: Consistently confirmed but mitigation approaches haven't improved the rate.

## Applicability

Applicable to future pipeline runs involving page-creation, cross-references, invariant-system documentation domains. Confirmed across 3 pipeline runs. **Create tasks have 0% aggregate first-attempt rate** across all observations. Code-sample create tasks are the highest-risk category. Create-action tasks need pre-writing reviewer briefing on: namespace resolution, frontmatter derivation, required page sections, and code compilation verification.
