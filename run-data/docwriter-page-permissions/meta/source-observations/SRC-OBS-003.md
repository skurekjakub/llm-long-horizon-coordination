---
id: SRC-OBS-003
title: Shared lexical root on different type hierarchies predicts disambiguation section need
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

Two API concepts sharing a lexical root (e.g., "UrlPath" in both `IncludeUrlPath` and `UrlPathColumns`) but existing on different type hierarchies with different behaviors. The shared naming creates a false sense of equivalence for developers reading documentation.

## Predicted Documentation Need

Explicit disambiguation section mapping each concept to its class, layer, and behavior. Without disambiguation, developers assume the concepts are interchangeable or that one is a shorthand for the other. The section should:
1. Name both concepts explicitly
2. State which class/interface each belongs to
3. Explain the behavioral difference
4. Note any prerequisites (e.g., `UrlPathColumns()` only meaningful when `IncludeUrlPath=true`)

## Evidence

- DOC-2847: `IncludeUrlPath` (property on `RetrieveParametersBase`, parameter object layer) vs `UrlPathColumns()` (method on `RetrievePagesQueryParametersBase`, query configuration layer) — both contain "UrlPath" but control different behaviors
- T-001 needed a disambiguation section; T-002 needed separate parameter table cells with cross-references
- REC-002 (from SRC-WEB-005, boolean naming guidelines) provided the disambiguation pattern
- Both T-001 and T-002 required multi-cycle acceptance partly because the disambiguation was non-trivial

## Applicability

Any API with ≥2 members sharing a lexical root (3+ characters) but residing on different types or at different architectural layers. Detection heuristic: grep for common substrings across public member names, filter to members on different types. Higher priority when the shared root is a domain concept (e.g., "UrlPath", "Cache", "Security") rather than a generic term.
