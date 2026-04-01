---
id: SRC-OBS-008
title: "Pure-FK binding classes predict custom-object-type-extension documentation need"
type: source-observation
confidence: low
domains: ["xperience-platform", "custom-object-types", "impact-analysis"]
discoveredDate: "2026-03-20T09:04:44Z"
lastReferencedDate: "2026-03-20T09:04:44Z"
usageCount: 1
sourceTask: DOC-3167
invariantsReferenced: []
deprecated: false
---

## Code Characteristic

Binding info classes with only foreign-key columns (no metadata fields like DateTime, Status, enum, or boolean columns). The class has exactly N columns where all are either an auto-increment ID or foreign keys to other info classes.

## Predicted Documentation Need

When business logic requires temporal or stateful semantics (expiration dates, subscription periods, status tracking), the documentation must cover a "custom object type extension" pattern — creating a parallel custom object type with the needed metadata columns alongside the native binding.

## Evidence

- DOC-3167: MemberRoleMemberInfo (FIND-002) has only 3 FK-style columns with no expiration/metadata fields. The entire T-001 scenario page was driven by this constraint.
- The custom object type extension pattern was the core deliverable of the documentation task.
- Related findings: FIND-002, FIND-034, FIND-042, FIND-049.

## Applicability

Any Xperience binding class lacking metadata columns will need extension documentation when business logic requires time-based or state-based relationships. The threshold is: if the binding class has ONLY ID + FK columns and the use case requires any additional attributes, predict a custom object type documentation need.
