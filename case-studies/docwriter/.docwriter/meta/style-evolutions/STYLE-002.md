---
id: STYLE-002
title: "Callout bold title requirement (INV-callout-002/INV-style-139) triggered rejections across 4 runs"
type: style-evolution
confidence: medium
domains: ["style-formatting", "invariant-system", "content-security"]
discoveredDate: "2026-03-14T16:06:35+00:00"
lastReferencedDate: "2026-03-18T22:24:04Z"
usageCount: 3
sourceTasks: ["DOC-3167-T-001", "DOC-3167-T-002"]
invariantsReferenced: ["INV-callout-002", "INV-style-139"]
sourceSignals: ["SE-002", "SIG-009", "STYLE-EVO-002", "CAPAT-002"]
deprecated: false
---

## Insight

Multi-sentence callouts must have a bold title on the first line. Writers omit this consistently — suggests the invariant needs more prominent placement in writer briefings. This is one of the most persistent style violations across pipeline runs.

## Evidence

### Run 4 (DOC-3167)

- T-001: Warning callout for Read permission prerequisite omitted bold title. Fix: added `**Read permission prerequisite**` after opening Liquid warning tag.
- T-002: 3 of 4 permission note callouts (Publish, Revert, Unpublish) had 2+ sentences without bold titles. Move note (single sentence) was correctly exempted. Fix: added `**Required permissions**` bold title to multi-sentence callouts.
- Writer showed partial awareness (correctly exempted single-sentence callout) but failed to apply the rule consistently to multi-sentence callouts.
- INV-style-139 was the enforcing invariant in this run (same rule as INV-callout-002 in earlier runs).

### Run 2 (DOC-3137)

- Callout bold title omission in T-010 and T-011, co-occurring with em dash errors. Confirms both issues share a common root: insufficient post-composition style checking.
- Promoted: low → medium (2nd pipeline run confirmation)

### Run 1 (original)

- Source signal: STYLE-EVO-002 (from task-signals)
- Within-run strength: strong (3+ tasks)

## Recommendation

Writer briefings should include an explicit checklist item: "For every callout with 2+ sentences, verify a bold title exists on the first line after the opening Liquid tag." Consider automated pre-submission check for callout structure.

## Applicability

Applicable to all pipeline runs involving callout/note insertions. The violation is most common when writing permission-requirement or prerequisite callouts where the writer focuses on content accuracy and overlooks structural formatting. Not promotable to `high` yet — STYLE-002 was not in the knowledge brief for DOC-3167, so no acceptance-rate-when-applied data available.
