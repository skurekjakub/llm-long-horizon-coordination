## Documentation Updates — 2026-03-18

Based on a documentation gap analysis of the `master` branch (gap-fill — no triggering diff).

### New Documentation

- [Page permission management](../src/_documentation/developers-and-admins/configuration/users/role-management/page-permission-management.md) — Comprehensive new reference covering the page-level permission model, including the six ACL permissions, the Read prerequisite rule, channel administrator bypass behavior, and how page permissions interact with workflow step roles and application-level access control.

### Updated Documentation

- [Edit and publish pages](../src/_documentation/business-users/website-content/edit-and-publish-pages.md) — Added permission requirement notes to the Publish, Unpublish, Revert changes, and Move sections with cross-references to the new permission management page.
- [Workflows](../src/_documentation/developers-and-admins/configuration/workflows.md) — Replaced vague permission callouts with specific guidance on how workflow step roles interact with page permissions and application-level permissions.
- [Create pages](../src/_documentation/business-users/website-content/create-pages.md) — Added a permission requirements note to the page creation section, cross-referencing Create permission details.
- [Delete pages](../src/_documentation/business-users/website-content/delete-pages.md) — Added permission requirements notes for page deletion and child page deletion, cross-referencing Delete permission details.
- [Security guidelines](../src/_documentation/developers-and-admins/security-guidelines.md) — Improved cross-references to the new permission management page with more descriptive link text and accurate context.
- [Content versioning configuration](../src/_documentation/developers-and-admins/configuration/content-versioning-configuration.md) — Updated the Permissions section with accurate cross-references and aligned Read/Update permission descriptions with the permission model.
- [Content sync](../src/_documentation/business-users/content-sync.md) — Added a note about Synchronize permission requirements for page content synchronization.
