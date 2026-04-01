---
id: SRC-OBS-004
title: code_link consumer graph predicts cross-directory code sample audit need
type: source-observation
confidence: low
domains: ["code-samples", "impact-analysis"]
discoveredDate: "2026-03-15T18:03:22Z"
lastReferencedDate: "2026-03-15T18:03:22Z"
usageCount: 1
sourceTask: DOC-2847
invariantsReferenced: []
deprecated: false
---

## Code Characteristic

Documentation pages referencing code sample files via `code_link` (or equivalent include/embed) tags. The code_link targets form a dependency graph that may span multiple directory trees beyond the obvious co-located examples directory.

## Predicted Documentation Need

Cross-directory code sample audit during impact analysis. When an API's parameter-passing convention or calling pattern changes, the impact mapper must trace all `code_link` consumers to find every code sample file that exercises the changed API — not just files in the same directory as the API reference documentation.

## Evidence

- DOC-2847: Impact mapper found `Pages.cs` and `ContentItems.cs` in `APIExamples/` but missed `ProductService.cs` (6 call sites) and `ProductDataRetriever.cs` (1 call site) in `DigitalCommerce/`
- The missed files are referenced by `example-product-catalog.md` and `implementation.md` via `code_link` tags
- GAP-002 caught the scope miss in verification cycle 1; T-009 resolved it
- Verification matrix confirmed 6 `code_link` references across 2 doc pages → digital commerce files

## Applicability

Any project using `code_link`, `code_include`, or similar tag-based code embedding. The predictor is: when the changed API is consumed by code sample files in ≥2 directory trees, a `code_link` dependency scan during impact analysis catches scope misses proactively. Priority scales with the number of separate code sample directories and the API's consumer count.
