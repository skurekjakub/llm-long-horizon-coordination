---
id: SRC-OBS-007
title: "Hub pages absorbing >40% of total impacts predict critical-risk tasks needing 2+ review cycles"
type: source-observation
confidence: low
domains: ["impact-analysis", "risk-analysis", "pipeline-process"]
discoveredDate: "2026-03-18T22:24:04Z"
lastReferencedDate: "2026-03-18T22:24:04Z"
usageCount: 1
sourceTask: DOC-3167
invariantsReferenced: []
deprecated: false
---

## Code Characteristic

Impact concentration: a single documentation page absorbs >40% of total mapped impacts from the impact matrix. This typically occurs with hub/overview pages that aggregate information from multiple code areas, or reference pages that document a central API/feature with many touchpoints.

## Predicted Documentation Need

Critical-risk task classification requiring: (1) higher acceptance criteria count to cover all impacted areas, (2) budget for 2+ review cycles due to the volume of new/changed prose, and (3) potential decomposition into sub-tasks if the page modifications span multiple independent sections.

## Evidence

- DOC-3167 T-001 (page-permission-management.md): Absorbed 17 of 38 impacts (44.7%), had 19 acceptance criteria, was the only critical-risk task. Required 2 initial review cycles plus 1 re-entry cycle. All other tasks (1-6 impacts each) had 80% first-attempt success.
- Impact concentration >40% was a reliable predictor of multi-cycle outcome in this run.
- The high criteria count (19) correlates with more prose generation, which correlates with more opportunities for style violations (INV-style-132, INV-style-139).

## Applicability

Any pipeline run with an impact matrix. The risk analyzer should flag tasks where a single page absorbs >40% of total impacts as critical-risk, automatically budgeting 2+ review cycles. Consider decomposing such tasks into section-level sub-tasks when the impacted sections are independent. The 40% threshold is based on a single run and may need calibration.
