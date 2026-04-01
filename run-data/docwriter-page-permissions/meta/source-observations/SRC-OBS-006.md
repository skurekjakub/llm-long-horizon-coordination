---
id: SRC-OBS-006
title: "Recursive permission check parameters predict documentation need for scope-of-check callouts"
type: source-observation
confidence: low
domains: ["content-security", "xperience-platform", "reference"]
discoveredDate: "2026-03-18T22:24:04Z"
lastReferencedDate: "2026-03-18T22:24:04Z"
usageCount: 1
sourceTask: DOC-3167
invariantsReferenced: []
deprecated: false
---

## Code Characteristic

Operations with `evaluateChildPages=true` parameters, ancestor-chain iteration loops, or parent-context permission lookups in their permission evaluation code path. These parameters indicate that the permission check extends beyond the target page/resource to related entities in the content hierarchy.

## Predicted Documentation Need

Dedicated scope-of-check callouts explaining: (1) which entities are checked beyond the target, (2) what happens when any check in the chain fails, and (3) how this differs from the standard single-entity permission check. Without these callouts, users configure permissions on the target entity only and are surprised when the operation fails due to a permission gap on a related entity.

## Evidence

- DOC-3167 T-005 (delete): `evaluateChildPages=true` → checks DELETE on all child pages with broken ACL inheritance. Was in risk register and documented correctly on first attempt.
- DOC-3167 GAP-003 (synchronize): Ancestor-chain ACL check was undocumented because synchronize was excluded from scope. The code-analysis data showing the ancestor-chain pattern was available but not used for scoping.
- DOC-3167 T-004 (clone/create): Parent-page permission check pattern was documented as part of GAP-001 resolution.
- 3 operations exhibited this characteristic. The documented one (delete) passed first attempt; the undocumented ones required gap-hunting re-entry.

## Applicability

Any permission system where operations check permissions on entities beyond the direct target (parent, children, ancestors, related resources). When code analysis reveals recursive or chain-based permission evaluation, the task planner should flag these operations for dedicated scope-of-check documentation sections.
