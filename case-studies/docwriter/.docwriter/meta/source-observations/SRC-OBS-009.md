---
id: SRC-OBS-009
title: "Date-comparison scheduled tasks predict bulk-delete documentation pattern"
type: source-observation
confidence: low
domains: ["xperience-platform", "scheduled-tasks", "code-samples"]
discoveredDate: "2026-03-20T09:04:44Z"
lastReferencedDate: "2026-03-20T09:04:44Z"
usageCount: 1
sourceTask: DOC-3167
invariantsReferenced: []
deprecated: false
---

## Code Characteristic

Scheduled tasks that use date-comparison query patterns (WhereLessThan/WhereLessOrEquals on DateTime columns) to identify records for batch processing.

## Predicted Documentation Need

Documentation requires four elements: (1) date comparison query example, (2) BulkDelete usage example, (3) error handling pattern with ScheduledTaskExecutionResult, and (4) IDateTimeNowService/DateTime.UtcNow usage note for testability.

## Evidence

- DOC-3167: Three reference implementations follow this pattern — RecycleBinCleanerTask (FIND-017), ContentItemScheduledPublishAndUnpublishTask (FIND-018), DeleteExpiredShoppingCartsTask (FIND-019).
- T-001 validated this prediction by requiring all four documentation elements.
- FIND-054 synthesizes the cross-cutting pattern across reference implementations.

## Applicability

Any Xperience scheduled task that performs date-comparison batch processing. The pattern applies regardless of the specific entity being cleaned up — the documentation structure is consistent across recycle bin, shopping cart, content scheduling, and role expiration tasks.
