
- terminology: public, authenticated, role-restricted x public, secured, secured with member roles
	- using the second ones does not "break" things in the docs, secured items are still called secured
	- https://docs.kentico.com/documentation/business-users/content-hub/content-items#secure-content-items
	- listingy - různá terminologie
### Authorize using roles

- Intro - "restrict access" -> "restrict access to pages and content items" to mention this functionality?
- The system supports creating, assigning, and querying roles through standard ASP.NET Identity APIs. -> link to the role manager CRUD section 
- Class and interface names with type qualification (throughout the docs)
	- `ApplicationRole` extends `IdentityRole<int>` etc.
	- Is it necessary? The existing authentication docs omit the types
- Code examples wrapped in methods - imho it would be better not to wrap examples in methods that are not real meaningful methods, adds unnecessary lines to read
- **Extend application role**
	- move the original remark info among remarks on this page - too much info from the start
	- add the full process for user and AI convenience? (two out of three steps are there anyway). Or at least make the steps more explicit (1. Add new fields following the same process as... 2. Modify 3. register). It's also currently mixed with the general info.
- **Integrate custom authorization logic** 
	- link to content retrieval docs (instead of the content items business page) -> could serve as a source of the 3 tier access scheme, but also provides information on the API which would fit here
		- https://docs.kentico.com/documentation/developers-and-admins/development/content-retrieval/retrieve-page-content#page-security-configuration
		- https://docs.kentico.com/documentation/developers-and-admins/development/content-retrieval/retrieve-content-items#content-item-security
- Page preview mode
	- different wording? e.g. member role instead of role
	- what about the usage of [Authorize] attribute? https://docs.kentico.com/documentation/developers-and-admins/development/registration-and-authentication#page-preview-mode -> MVC authorization flows and preview mode

### Registration and authentication

- Configure registration and authentication - move the `ApplicationUserStore` bullet point before the role bullet points for a better flow?
- Why not mention Display name and Description property of Application role in the diagram?
- Use store not in the diagram - just an observation

### Administration - forms authentication

- link to relevant docs in this section: (e.g., the account is disabled, a password is changed, or role assignments are modified)
- https://docs.kentico.com/documentation/developers-and-admins/configuration/users/user-management


### Content sync 

- duplicite content in content sync internals - already in the Ensure compatibility section, not that much internal 

- Content access settings are synchronized for content items and pages. If a content item is {% page_link 8oouCw linkText="secured" %} with {% page_link member_roles_xp linkText="member role" %} restrictions on the source instance, the same security configuration and role assignments are restored on the target instance.

### Retrieve content items

-  Project security properties - minor, duplicate content in a way?
	- Additionally, the `ContentItemRequiredMemberRoleNames` property contains the code names of [member roles](https://docs.kentico.com/documentation/developers-and-admins/development/registration-and-authentication/member-roles) required for access. For role-restricted items, `ContentItemRequiredMemberRoleNames` contains the code names of the required roles (e.g., `["Subscriber", "Premium_Member"]`). For public and authenticated-only items, the collection is empty or null.

### Retrieve page content

- the example **Reflect page security in views** has only the HasAccess Condition
- **Authentication and authorization** responses section - the config might make sense somewhere else (not quite a content retrieval scenario)

### Customize customer eligibility

- old screenshot

### API examples

Create content items - basic scenario, is it a good idea to complicate it with the security settings?

### Guides - Require authentication for certain content
- This might be a guide problem, but currently the system also return 403, doesn't it?

### UI docs