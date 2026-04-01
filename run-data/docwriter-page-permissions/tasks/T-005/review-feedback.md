# Review Feedback — T-005 (Attempt 1)

## Reviewers that PASSED
- **accuracy-reviewer**: approved (5/5 claims verified)
- **persona-reviewer**: approved-with-notes (minor note about "inherit" vocabulary)

## Reviewers that FAILED

### style-reviewer — REJECTED

**Failed invariant: INV-style-132**
- **Location**: Line 71
- **Issue**: `you must have the **Delete** permission set directly on that page` uses "must" directed at a person ("you"). INV-style-132 states: "Avoid must directed at people — they could perceive it as impolite."
- **Fix**: Change `you must have` to `you need to have` — consistent with the first sentence's phrasing ("You also need") and with line 19's "You need the **Read** and **Delete**..." pattern.

## Persona-reviewer notes (non-blocking, consider incorporating)
- The verb "inherit" in "does not inherit permissions from its parent" is a technical/system-administration concept that may not be immediately intuitive to business users.
- Suggested rephrasing: "If a child page uses its own permission settings instead of the parent page's, you need to have the **Delete** permission set directly on that page."
- This would address BOTH the style rejection (must → need) AND the persona note (inherit → simpler phrasing) in one edit.

## Required action
Fix line 71 to replace "you must have" with "you need to have" (or similar INV-style-132-compliant phrasing). Optionally also rephrase "does not inherit" to improve business-user accessibility.
