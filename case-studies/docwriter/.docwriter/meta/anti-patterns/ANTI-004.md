---
id: ANTI-004
title: "Incomplete operation/method enumeration in acceptance criteria causes coverage gaps"
type: anti-pattern
confidence: medium
domains: ["api-reference", "xperience-platform", "risk-analysis", "content-security"]
discoveredDate: "2026-03-14T16:06:35+00:00"
lastReferencedDate: "2026-03-18T22:24:04Z"
usageCount: 3
sourceTasks: ["DOC-3167-T-001", "DOC-3167-T-004", "DOC-3167-T-008"]
invariantsReferenced: []
sourceSignals: ["SIG-R2-metaknowledge", "CTXGAP-003", "GAP-001-signal", "GAP-003-signal"]
deprecated: false
---

## Insight

When acceptance criteria say 'document methods of interface X' or 'document permission requirements for operations' without exhaustively enumerating them, writers miss less-prominent items. Code analysis provides complete inventories, but the task planner may not convert these into exhaustive checklists. High-accuracy-risk tasks should have item-level acceptance criteria cross-checked against code-analysis outputs.

## Evidence

### Run 4 (DOC-3167) — **VIOLATED DESPITE BRIEFING**

- ANTI-004 was included in the knowledge brief for this run. The brief explicitly warned: "code analysis should feed explicit checklists into task planning."
- Code-analysis permissionSummary contained 18 operations. Task planner scoped only 6.
- GAP-001: Clone operation (requires READ on source + CREATE on target parent) was excluded from scope despite being fully documented in code analysis. Risk register noted "out of scope" without flagging the exclusion as a gap risk.
- GAP-003: Synchronize operation (requires ancestor-chain ACL checks) was omitted entirely — not listed in scope or out-of-scope sets.
- Both gaps were caught by gap hunter in cycle 1 and resolved via re-entry, but cost an additional verification cycle.
- **Note**: The anti-pattern warning was available but the task planner did not cross-check scoped operations against the full permissionSummary. Mitigation needs stronger enforcement — passive briefing is insufficient.
- Confidence kept at `medium` — cannot promote to `high` because the mitigation was not effectively applied despite being briefed.

### Run 2 (DOC-3137)

- Task planner enumerated IActivityModifier.Modify() and IActivityLogValidator.IsValid() explicitly. No methods were missed. ANTI-004 mitigation (explicit method enumeration) confirmed effective.
- Promoted: low → medium (2nd pipeline run confirmation)

### Run 1 (original)

- Source signal: CTXGAP-003 (from context-signals)
- Within-run strength: single observation

## Recommendation

Task planner MUST cross-check scoped items against the full code-analysis inventory (permissionSummary, method lists, operation enumerations). Each exclusion must be explicitly justified with a gap-risk assessment. Operations with unique behavioral characteristics (different permission combinations, recursive checks, asymmetric workflow requirements) should never be excluded without documented rationale.

## Applicability

Applicable to any pipeline run where code-analysis provides an enumerated inventory of items (methods, operations, permissions, events) and the task planner scopes a subset. The anti-pattern is especially dangerous for permission documentation where operations with unique semantics can be silently omitted.
