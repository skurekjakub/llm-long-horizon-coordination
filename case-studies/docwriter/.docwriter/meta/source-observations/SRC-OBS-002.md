---
id: SRC-OBS-002
title: Base-class property with high internal fanout predicts dedicated documentation section need
type: source-observation
confidence: low
domains: ["api-reference"]
discoveredDate: "2026-03-15T18:03:22Z"
lastReferencedDate: "2026-03-15T18:03:22Z"
usageCount: 1
sourceTask: DOC-2847
invariantsReferenced: []
deprecated: false
---

## Code Characteristic

A property defined on a base class and consumed at 7+ internal call sites across the implementation. High internal fanout indicates the property is a load-bearing configuration point that affects multiple behaviors.

## Predicted Documentation Need

Dedicated section with behavior description, not just a parameter table cell. When a single property is consumed at 7+ internal sites, its behavioral impact is too complex for a one-line table entry. It needs:
1. A conceptual explanation of what the property controls
2. Sub-sections for each behavioral dimension it affects
3. Cross-references to related pages where the property's effects surface

## Evidence

- DOC-2847: `IncludeUrlPath` defined on `RetrieveParametersBase.cs:56`, consumed at 8 `ForWebsite` call sites + 7 cache key generation sites in `ContentRetriever.cs`
- Required: dedicated section in content-retriever-api.md (T-001: "URL retrieval behavior" with sub-sections) + parameter table expansion (T-002) + cache key documentation (T-008)
- A single parameter table cell would have been insufficient — the 15-site internal fanout predicted multi-page documentation impact
- Total: 3 tasks (T-001, T-002, T-008) to fully document one property

## Applicability

Any API where a base-class property is consumed at 7+ internal implementation sites. The fanout count is the key predictor: properties consumed at 1-3 sites are adequately covered by parameter tables; 4-6 sites may need an expanded description; 7+ sites predict a dedicated section with cross-references. The threshold is approximate and should be calibrated per codebase.
