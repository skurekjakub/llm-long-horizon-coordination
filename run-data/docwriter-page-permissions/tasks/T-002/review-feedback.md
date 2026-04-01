# Review Feedback for T-002 (Attempt 1)

## Verdict: REWRITE NEEDED

### Style Review: REJECTED (2 failures)

**INV-style-132 (FAIL):** Line 128 (Revert note) uses "You must also be able to work with the page in its current workflow step." — Per INV-style-132, "must" should be avoided when directed at people. Change to "You also need to be able to work with the page in its current workflow step."

**INV-style-139 (FAIL):** Three of the four notes contain 2+ sentences but lack a bold title on a separate line. The Move note (single sentence) is correctly exempt. Add a bold title like `**Required permissions**` to the Publish, Revert, and Unpublish notes. Format:
```
{% note %}
**Required permissions**

Content here...
{% endnote %}
```

### Accuracy Review: APPROVED (12/12 claims verified)
No issues.

### Persona Review: APPROVED (8/8 checks passed, 13/13 invariants passed)
No issues.

## Required Changes
1. Change "You must" → "You also need to" in the Revert note (INV-style-132)
2. Add bold title line `**Required permissions**` to the Publish, Revert, and Unpublish notes (INV-style-139)
