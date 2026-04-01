---
id: ANTI-012
title: "Permission-requirement prose systematically triggers 'must' directed at people (INV-style-132)"
type: anti-pattern
confidence: low
domains: ["content-security", "style-formatting", "invariant-system"]
discoveredDate: "2026-03-18T22:24:04Z"
lastReferencedDate: "2026-03-18T22:24:04Z"
usageCount: 1
sourceTask: DOC-3167
invariantsReferenced: ["INV-style-132"]
deprecated: false
---

## Insight

Permission-requirement documentation contexts systematically trigger INV-style-132 violations ('must' directed at people). The writer consistently produces phrases like 'you must have', 'the user must have', 'they must advance' when documenting what permissions are required for an operation — a context where imperative phrasing feels natural but violates the style guide. This is not a general 'must' problem; it is specifically triggered by the permission-requirement content domain where requirements are inherently directed at people.

## Evidence

- DOC-3167 T-001: Used 'must have' and 'must advance' in permission requirement sentences. Rejected by style reviewer. Fix: 'must have' → 'needs to have', 'must advance' → 'need to advance'.
- DOC-3167 T-002: Used 'You must also be able to' in Revert permission note. Rejected by style reviewer. Fix: → 'You also need to be able to'.
- DOC-3167 T-005: Used 'you must have the Delete permission'. Rejected by style reviewer. Fix: → 'you need to have'. Third instance despite INV-style-132 being listed in applied invariants.
- All 3 multi-cycle outcomes in the run were caused (solely or primarily) by INV-style-132. All 3 fixes were mechanical: 'must' → 'need to' / 'needs to'.
- 3 of 8 tasks (37.5%) failed for this reason. 100% of multi-cycle outcomes had this as a root cause.

## Recommendation

For permission-documentation tasks, the content writer should:
1. Pre-emptively search the draft for 'must' after composition and replace with 'need to' / 'needs to' when the subject is a person.
2. Alternative: rephrase so the requirement is the subject ('a role assignment is required' instead of 'you must have a role assignment').
3. Consider adding a task-scoped invariant (TINV) specifically for permission tasks: "Replace all instances of 'must' + person-subject with 'need to' before submission."

## Applicability

Applicable to any pipeline run involving permission, authorization, or access-control documentation where requirements are expressed as things users/administrators need to have or do. The trigger is the semantic domain (requirements directed at people), not a specific product or technology.
