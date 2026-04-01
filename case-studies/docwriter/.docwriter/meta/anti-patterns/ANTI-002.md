---
id: ANTI-002
title: "Style invariant INV-formatting-016 (em dash vs en dash) is the most frequent ..."
type: anti-pattern
confidence: medium
domains: ["how-to", "style-formatting", "invariant-system"]
discoveredDate: "2026-03-14T16:06:35+00:00"
lastReferencedDate: "2026-03-20T09:04:44Z"
usageCount: 6
sourceTasks: ["TASK-007", "TASK-010", "TASK-014", "DOC-2847-T-008", "DOC-3167-T-003", "DOC-3167-T-005", "DOC-3167-T-006"]
invariantsReferenced: ["INV-formatting-016", "INV-style-096"]
sourceSignals: ["SIG-003", "AGG-003", "CAPAT-001"]
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

### Run 4 (DOC-3167) — RE-PROMOTION

- Run 4 (DOC-3167): En-dash detection failure was the single most impactful anti-pattern in this run. 3 tasks affected:
  - T-005: Rejected for 3 pre-existing en-dashes at lines 17, 35, 260 not converted. New content was clean — failure was in full-page scanning.
  - T-003: Required 3 attempts — gap remediation (attempt 3) to convert 7 pre-existing en-dashes.
  - T-006: Required verification that T-018 had already converted en-dashes in the file.
- The en-dash variant (U+2013 → `--`) is now INV-style-096, distinct from the original INV-formatting-016 em-dash issue.
- Root cause broadened: the anti-pattern now covers ALL Unicode dash variants that writers fail to convert when modifying existing pages.
- **Re-promoted: low → medium** (confirmed in run 4 despite being briefed; 3+ tasks affected; anti-pattern description broadened to cover en-dash + em-dash variants)
- **Recommendation**: Upgrade from awareness-level anti-pattern to mandatory automated pre-submission check (grep -P '\x{2013}|\x{2014}' on all modified files).

## Applicability

Applicable to all pipeline runs involving prose documentation. The anti-pattern encompasses ALL dash-type confusions (em dash U+2014, en dash U+2013, double hyphen --, minus sign -). Writers consistently fail to perform full-page Unicode scanning when modifying existing pages. Pre-existing encoding debt amplifies the issue. **PROMOTED back to medium** after re-confirmation in run 4.
