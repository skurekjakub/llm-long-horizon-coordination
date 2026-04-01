
> Aside: Interestingly, imperative prompting also seems to override almost all pasisvity or reluctance imparted into agent systems via their agent and system prompts. Copilot agents, for example, can be very easily convinced to violate their agent-level directives with simple 


acceptance criteria example

 
 
 "acceptanceCriteria": [
    "Page explains why a custom object type is needed (MemberRoleMemberInfo has no expiration field -- FIND-002)",
    "Custom Info class code sample includes MemberID, RoleID, and ExpiresAt fields with correct TYPEINFO configuration (FIND-034, FIND-049)",
    "Scheduled task code sample implements IScheduledTask with constructor DI (FIND-010, FIND-016)",
    "Uses IDateTimeNowService for current time, not DateTime.Now (FIND-051)",
    "Shows RegisterScheduledTask attribute registration with matching identifier (FIND-011)",
    "Returns ScheduledTaskExecutionResult.Success or error result (FIND-014)",
    "Documents admin UI configuration steps for scheduled task (interval, enable)",
    "Explains 30-minute session persistence window after role removal (FIND-053)",
    "Mentions optional SecurityStamp regeneration for immediate revocation (FIND-053)",
    "Explicitly distinguishes membership roles from admin roles (FIND-050)",
    "Front matter has all required fields: title, identifier, order, redirect_from, persona, license (INV-jekyll-004)",
    "Identifier uses snake_case with _xp suffix, is unique (INV-jekyll-005, INV-jekyll-006)",
    "redirect_from includes x/<identifier> entry (INV-jekyll-008, INV-jekyll-032)",
    "Page title uses imperative verb phrase in sentence case, no -ing suffix (INV-style-099, INV-style-054)",
    "Introduction explains benefit and context (INV-structure-035)",
    "Key points callout with 3-5 bullet summary for this longer article (INV-structure-036)",
    "All code blocks use {% code lang=csharp %} Liquid syntax with title attribute (INV-jekyll-011, INV-codesamples-014)",
    "All cross-references use {% page_link %} with verified identifiers -- never fabricate (INV-crossref-002, INV-crossref-003)",
    "Multi-sentence callouts have bold title on first line (INV-style-139) -- known rejection cause",
    "All dashes use -- not en dash character (INV-style-096) -- known rejection cause",
    "Active voice throughout, present simple tense (INV-style-114, INV-style-115)",
    "Uses 'sign in' not 'log in', 'sign in to' not 'sign into' (INV-style-059, INV-style-148)",
    "Code comments use third person singular, no final period for single-line (INV-codesamples-005, INV-codesamples-026)"
  ],