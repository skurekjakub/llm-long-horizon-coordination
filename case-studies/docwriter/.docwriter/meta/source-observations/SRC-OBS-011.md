---
id: SRC-OBS-011
title: "Conditional security-stamp regeneration predicts negative-behavior documentation callouts"
type: source-observation
confidence: low
domains: ["xperience-platform", "authentication", "security"]
discoveredDate: "2026-03-20T09:04:44Z"
lastReferencedDate: "2026-03-20T09:04:44Z"
usageCount: 1
sourceTask: DOC-3167
invariantsReferenced: []
deprecated: false
---

## Code Characteristic

Info classes where SecurityStamp regeneration is triggered by a narrow condition (e.g., only on MemberEnabled change, not on role assignment/removal).

## Predicted Documentation Need

Documentation must include explicit "what does NOT trigger revocation" callouts. When a security operation has a narrow trigger scope, documentation must state the negative behavior — what operations are excluded from triggering the security response.

## Evidence

- DOC-3167: FIND-005 documents MemberInfoProvider.Set() regenerating stamp only on MemberEnabled change.
- This narrow trigger scope meant role removal does NOT trigger revocation — a critical negative behavior.
- T-001 and T-002 both needed to document this negative behavior.
- Risk register for T-001 explicitly listed SecurityStamp claim verification as the "most subtle accuracy trap."
- T-001 accuracy reviewer caught this as a verification target.

## Applicability

Whenever a security operation has a narrow trigger scope, documentation must explicitly state what does NOT trigger it. Generalizes to any authentication system where revocation conditions are narrower than expected. The pattern applies across Xperience and other platforms with conditional security invalidation.
