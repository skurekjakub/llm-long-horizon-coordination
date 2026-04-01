---
id: SRC-OBS-005
title: "Permission operations with unique permission combinations predict mandatory documentation coverage"
type: source-observation
confidence: low
domains: ["content-security", "task-planning", "risk-analysis"]
discoveredDate: "2026-03-18T22:24:04Z"
lastReferencedDate: "2026-03-18T22:24:04Z"
usageCount: 1
sourceTask: DOC-3167
invariantsReferenced: []
deprecated: false
---

## Code Characteristic

When code-analysis `permissionSummary` enumerates N operations with distinct permission combinations, each operation with a UNIQUE permission combination (different from the baseline READ + X pattern) predicts mandatory documentation coverage that cannot be safely excluded from scope.

## Predicted Documentation Need

Exhaustive operation coverage in the task plan. Operations with standard/shared permission patterns (e.g., save, discard, rename — all READ + UPDATE with no additional checks) can be safely grouped or summarized. Operations with unique combinations (clone: READ on source + CREATE on target parent; synchronize: ancestor-chain check) require individual documentation.

## Evidence

- DOC-3167: permissionSummary contained 18 operations. Task planner scoped 6. Two excluded operations (clone, synchronize) had unique permission semantics and required re-entry gap fixes (GAP-001, GAP-003).
- Operations with standard patterns (save, discard, rename — all READ + UPDATE) were safely excluded.
- The predictor threshold: operations whose permission combination appears only once in the permissionSummary (unique combination) predict mandatory coverage.

## Applicability

Any pipeline run where code-analysis produces an operation inventory with permission/authorization requirements. The task planner should cross-check: for each operation in the inventory, is its permission combination unique? If yes, it must be in scope or the exclusion must have an explicit gap-risk assessment. The threshold may need calibration — some unique combinations may still be low-documentation-value (e.g., internal-only operations).
