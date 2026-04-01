---
id: ANTI-008
title: "Risk register models directive compliance as binary, missing framing-quality dimension"
type: anti-pattern
confidence: low
domains: ["risk-analysis", "pipeline-process"]
discoveredDate: "2026-03-15T06:23:39Z"
lastReferencedDate: "2026-03-15T06:23:39Z"
usageCount: 1
sourceTasks: ["T-001"]
invariantsReferenced: []
sourceSignals: ["GAP-001"]
deprecated: false
---

## Insight

The risk analyzer models directive compliance as binary (include/exclude prohibited content) but misses framing quality. For tasks involving pubternal APIs (Internal namespace) where the API must be mentioned but properly framed with warning callouts, the risk register's 6 dimensions did not capture the "directive-framing-quality" risk. GAP-001 was about CMS.Activities.Internal being showcased without a warning callout — the content was included correctly but framed incorrectly.

## Evidence

- GAP-001: T-001 rated critical risk with technicalAccuracy=high, but "pubternal" dimension was not explicitly modeled
- Risk driver analysis mentioned "TINV-001 exposure" but framed it as IActivityLogFilter leakage, not Internal namespace framing
- Discovered cycle 1, resolved cycle 2
- Signal strength: medium
- Confidence: low (first observation in a single run)

## Recommendation

Add a "directive-framing-quality" risk dimension to the risk analyzer when tasks involve APIs in Internal namespaces that must be documented as exceptions rather than excluded entirely.

## Applicability

Applicable to any pipeline run where pubternal APIs must be mentioned with proper warning framing rather than simply excluded.
