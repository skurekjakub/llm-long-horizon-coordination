# T-001 Review Feedback — Attempt 1

## Style Review: REJECTED (2 invariant failures)

### Failure 1: INV-style-132 — "must" directed at people
- **Line 177:** "the user must have a role assigned to the current workflow step" — `must` directed at a person ("the user")
- **Line 203:** "they must advance the page through the workflow steps" — `must` directed at people ("they")
- **Fix:** Replace with `needs to have` / `need to advance`, or rephrase so the subject of "must" is not a person (e.g., "a role assigned to the current workflow step is required").

### Failure 2: INV-style-139 — Multi-sentence callout without bold title
- **Lines 106–108:** The new warning callout contains 3 sentences but has no bold title on a separate line. The single-sentence exception does not apply.
- **Fix:** Add a bold title after `{% warning %}`:
  ```
  {% warning %}
  **Read permission prerequisite**

  The *Read* permission is a prerequisite...
  ```

### Style Note (non-blocking):
- **Lines 118–120:** The modified tip (cache TTL note added) also has 2 sentences without a bold title. Adding a title like **"Channel admin bypass"** would improve INV-style-139 compliance.

## Accuracy Review: APPROVED
All 21 technical claims verified. No issues.

## Persona Review: REJECTED (1 issue)

### Failure: Front matter persona tag incomplete
- **Current:** `persona: admin` (line 3)
- **Required:** `persona: admin, developer`
- **Violated invariants:** INV-persona-001 (incomplete persona list) and INV-persona-002 ("config/user roles → admin, developer")
- **Fix:** Change line 3 of front matter from `persona: admin` to `persona: admin, developer`.

All tone, depth, and classification checks passed.
