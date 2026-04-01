---
id: SRC-OBS-012
title: "Cross-collection heading modifications predict multi-collection anchor audit need"
type: source-observation
confidence: low
domains: ["cross-references", "pipeline-process", "impact-analysis"]
discoveredDate: "2026-03-20T09:04:44Z"
lastReferencedDate: "2026-03-20T09:04:44Z"
usageCount: 1
sourceTask: DOC-3167
invariantsReferenced: ["INV-structure-030"]
deprecated: false
---

## Code Characteristic

Heading text modifications in a page belonging to one Jekyll collection (e.g., _documentation) that is referenced by anchor= attributes in pages belonging to a different collection (e.g., _guides).

## Predicted Documentation Need

Documentation requires: (1) multi-collection anchor search across all collections, (2) deferred task creation for off-limits collections (e.g., per INV-structure-030), and (3) an additional verification cycle to confirm cross-collection anchor integrity.

## Evidence

- DOC-3167 GAP-002: T-018 changed a heading in reference-tag-helpers.md (_documentation) that was referenced by anchor= attributes in store-files.md (_guides).
- INV-structure-030 prohibits modifying _guides files, requiring 2 deferred tasks.
- Cross-ref-updater cycle 2 fixed the _guides anchors.
- The cross-collection dependency was not detectable by single-collection scanning — it required multi-collection grep.

## Applicability

Any heading text change in a documentation page that could be referenced by anchor= attributes in other collections. The risk scales with heading uniqueness — common heading text (like "Overview") may have false positive matches, while specific headings (like "Attribute Tag Helpers -- Images") are more likely to be exact anchor targets.
