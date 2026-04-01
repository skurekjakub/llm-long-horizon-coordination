---
id: SRC-OBS-001
title: API methods with 3+ similar-type parameters predict named parameter documentation need
type: source-observation
confidence: low
domains: ["api-reference", "code-samples"]
discoveredDate: "2026-03-15T18:03:22Z"
lastReferencedDate: "2026-03-15T18:03:22Z"
usageCount: 7
sourceTask: DOC-2847
invariantsReferenced: ["INV-codesamples-011"]
deprecated: false
---

## Code Characteristic

Public API methods with 3+ parameters of similar types (delegates, optional objects, cancellation tokens). The IContentRetriever Retrieve methods follow the pattern `(parameters, additionalQueryConfiguration, cacheSettings, configureModel, cancellationToken)` — 3 of these are optional delegates/objects.

## Predicted Documentation Need

Named parameter syntax in all code examples to disambiguate call semantics. Without named parameters, readers must count positional arguments and cross-reference the method signature. INV-codesamples-011 codifies the 4+ parameter rule, but the documentation need emerges at 3+ when parameter types are similar (all delegates or all optional objects).

## Evidence

- DOC-2847 T-003, T-004, T-007, T-009, T-010: All converted positional→named and all passed first-attempt review
- DOC-2847 T-001, T-002: Documentation .md files also adopted named params for IContentRetriever calls
- Reviewers consistently validated that named params improved clarity — zero pushback on the convention
- All 8 IContentRetriever Retrieve methods have 3-5 parameters with similar delegate/object types

## Applicability

Any public API with 3+ parameters where ≥2 share a type category (all delegates, all optional objects, all configuration callbacks). The threshold may need calibration per project — INV-codesamples-011 uses 4+ but the documentation clarity benefit begins at 3+ for similar-type parameters. Strongest predictor when the API is fluent/builder-pattern with optional chaining.
