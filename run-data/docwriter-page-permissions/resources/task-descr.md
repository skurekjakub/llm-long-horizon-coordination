Problem

The documentation does not clearly describe which permissions are required for common page operations (publish, unpublish, create, delete). The multi-layered permission model (application-level → ACL → workflow) is documented across four separate pages, but never tied together per operation. This leaves admins troubleshooting permission problems to reverse-engineer requirements from fragmented sources.

A precedent exists: the "Page permissions for moving pages" section on the Page permission management page already enumerates exact requirements for the move operation. The same treatment is missing for publish, unpublish, create, and delete.

Additionally, the Read ACL permission is an undocumented prerequisite for Update, Create, Delete, and Synchronize — granting Update without Read silently has no effect, which is a likely pit of failure for admins.

Proposed changes

1. Page permission management — Add operation-specific permission requirement sections

Page: https://docs.kentico.com/documentation/developers-and-admins/configuration/users/role-management/page-permission-management

Expand the page with sections analogous to the existing "Page permissions for moving pages", covering:

Page permissions for publishing pages:

Application permission: View (Access channel) on the website channel application

ACL: Read + Update on the page being published

For publishing a newly created page: Create on the parent page

Under workflow: user must have a role assigned to the current workflow step, or a Full Control role on the workflow

Users with the Administrator role or the Manage permissions application permission bypass all ACL checks

Page permissions for creating pages:

Application permission: View (Access channel)

ACL: Create on the parent page (+ Read as prerequisite)

Page permissions for deleting pages:

Application permission: View (Access channel)

ACL: Read + Delete on the page

Page permissions for unpublishing pages:

Application permission: View (Access channel)

ACL: Read + Update on the page

Source references for publish specifically:

ContentTab.cs — [PageCommand(Permission = SystemPermissions.VIEW)] + CheckAclPermission(..., WebPageAclPermissions.UPDATE)

PageBuilderTab.cs — same pattern

UrlsTab.cs — same pattern

CreateWebPage.cs — uses WebPageAclPermissions.CREATE on parent

WebPageCommandManagerBase.cs — workflow checks in PublishInternal() / ChangeWorkflowStepInternal()

2. Page permission management — Document Read as a prerequisite for other permissions

Page: https://docs.kentico.com/documentation/developers-and-admins/configuration/users/role-management/page-permission-management

Add a note after the permission descriptions table:

"The Read permission is a prerequisite for all permissions other than Display. Granting Update, Create, Delete, or Synchronize without also granting Read will have no effect."

Source references:

WebPageAclPermissionEvaluator.cs — enforces grantedPermissions.Contains(READ) && grantedPermissions.Contains(permission) for non-individually-checked permissions

WebsiteConstants.cs — IndividuallyCheckedPermissions = { Read, Display }

3. Edit and publish pages — Add permission cross-reference to "Publish pages" section

Page: https://docs.kentico.com/documentation/business-users/website-content/edit-and-publish-pages

The "Publish pages" section currently lists only workflow conditions. Add a brief note:

"In addition to the conditions above, users need the appropriate page permissions (Read and Update) for the page they are publishing. Users with the Administrator role or the Manage permissions permission are exempt from page permission checks. See [Page permission management] for details."

4. Workflows — Make the "other relevant permissions" callout specific

Page: https://docs.kentico.com/documentation/developers-and-admins/configuration/workflows

Replace the current vague callout:

"In addition to the role settings for workflows, the system also checks other relevant permissions (application-level and page permissions)..."

With:

"In addition to workflow step roles, users need the View (Access channel) application permission for the respective website channel, and Read + Update page permissions on the item they are working with. For details, see the operation-specific requirements in [Page permission management]."

Source files reference (resources/repositories/xperience)

File

Relevance

WebPageAclPermissionEvaluator.cs 

Read prerequisite logic (L118-121), channel admin bypass (L83-87) 

WebsiteConstants.cs 

IndividuallyCheckedPermissions = { Read, Display } (L20-24) 

WebPageAclPermissions.cs 

ACL permission constants (Display, Read, Create, Update, Delete, Synchronize) 

SystemPermissions.cs 

Application-level permission constants (View, Create, Update, Delete) 

ContentTab.cs 

Publish command: [PageCommand(Permission=VIEW)] + CheckAclPermission(UPDATE) 

WebPageBase.cs 

CheckAclPermission() implementation (L194) 

WebPageCommandManagerBase.cs 

PublishInternal() — blocks if under workflow (L573-578); ChangeWorkflowStepInternal() — checks step role (L592-610) 

CoveringWorkflowRetriever.cs 

GetForEdit() — returns null when no workflow assigned (L43-47) 

WorkflowStepRoleArbiter.cs 

Step role checks: Draft=always allowed, Full Control bypass, step role assignment (L85-130) 

CreateWebPage.cs 

Publish-on-create uses CREATE ACL on parent page (L196) 

References

Layer 1: Application-level permission (View)

Entry point — the [PageCommand] attribute on the Publish method:

ContentTab.cs:

[PageCommand(CommandName = WebPageActionConstants.PUBLISH, Permission = SystemPermissions.VIEW)]
public async Task<ICommandResponse> Publish(PublishWebPageCommandArguments args, ...)

Enforcement — the framework's PageInvokerBase intercepts every [PageCommand] call and checks the Permission value:

PageInvokerBase.cs:

protected async Task CheckPermission(UITreeNode node, string permission)
{
    // ...
    var uiPermissionExists = await uiPermissionEvaluator.Evaluate(permission);
    if (!uiPermissionExists.Succeeded)
    {
        throw new ForbiddenAccessException();
    }
}

This checks: does the user's role have the "View" application permission for the Web Pages application?

Layer 2: Web Page ACL (Read + Update)

Entry point — the first line inside the Publish method body:

ContentTab.cs:

await CheckAclPermission(WebPageIdentifier.WebPageItemID, WebPageAclPermissions.UPDATE, CancellationToken.None);

Delegation — CheckAclPermission is defined in the base class:

WebPageBase.cs:

protected async Task CheckAclPermission(int webPageItemId, string permissionName, ...)
{
    var permissionResult = await webPageAclPermissionEvaluator.Evaluate(
        webPageItemId, ApplicationIdentifier.WebsiteChannelID, permissionName, ...);
    if (!permissionResult.Succeeded)
    {
        throw new ForbiddenAccessException();
    }
}

Channel admin bypass — the evaluator first checks if the user is a channel admin:

WebPageAclPermissionEvaluator.cs:

bool userIsChannelAdmin = await websiteChannelAdminProvider.IsChannelAdmin(user, websiteChannelId, ...);
if (userIsChannelAdmin)
{
    return WebPageAclPermissionEvaluationResult.Success;
}

WebsiteChannelAdminProvider.cs:

public async Task<bool> IsChannelAdmin(AdminApplicationUser user, int websiteChannelId, ...)
{
    if (user.IsAdministrator())        // global Administrator role
        return true;

    bool userIsChannelManager = (await GetManagingWebsiteChannels(user.UserID, ...))
        .Contains(websiteChannelId);    // has ManagePermissions on this channel
    return userIsChannelManager;
}

Read prerequisite — if not channel admin, the evaluator resolves the user's granted ACL permissions and checks:

WebPageAclPermissionEvaluator.cs:

if (WebsiteConstants.IndividuallyCheckedPermissions.Contains(permission))
{
    return grantedPermissions[webPageItemId].Contains(permission);
}
return grantedPermissions[webPageItemId].Contains(WebPageAclPermissions.READ) 
    && grantedPermissions[webPageItemId].Contains(permission);

Since Update is not in IndividuallyCheckedPermissions (which is { Read, Display } per WebsiteConstants.cs), both Read and Update must be granted.

Layer 3: Workflow check (only if page is under a workflow)

Is the page under a workflow? — checked inside PublishInternal():

WebPageCommandManagerBase.cs:

if (await IsUnderWorkflow(webPage))
{
    return ... .AddErrorMessage("contentitemunderworkflow"); // direct publish blocked
}

WebPageCommandManagerBase.cs:

private async Task<bool> IsUnderWorkflow(IContentItemAdminModel contentItemAdminModel)
{
    var coveringWorkflow = await coveringWorkflowRetriever.GetForEdit(
        contentItemAdminModel.ContentItemID, contentItemAdminModel.ContentLanguageID);
    return coveringWorkflow is not null;
}

CoveringWorkflowRetriever.cs — returns null when no workflow step exists (i.e. no workflow assigned → direct publish allowed).

If under workflow — the user must use ChangeWorkflowStep instead, which checks step role permissions:

WebPageCommandManagerBase.cs:

if (!await CanWorkWithContentItemInCurrentStep(webPage, languageName))
{
    return ... .AddErrorMessage("changeworkflowstep.changestep.pagevalidation.role");
}

WebPageCommandManagerBase.cs:

private async Task<bool> CanWorkWithContentItemInCurrentStep(IContentItemAdminModel page, string languageName)
{
    var user = await userAccessor.Get();
    return await workflowStepRoleArbiter.CanWorkWithContentItemInCurrentStep(user.UserID, page.ContentItemID, languageName);
}

The arbiter's decision tree — WorkflowStepRoleArbiter.cs:

private async Task<bool> CanWorkWithContentItemInStepInternal(ContentWorkflowStepInfo step, int userId, ...)
{
    // 1. Draft step → always allowed
    if (IsDraft(step)) return true;

    // 2. Full control role on workflow → allowed
    var hasFullControl = await HasFullControlInternal(step.ContentWorkflowStepWorkflowID, user, ...);
    if (hasFullControl) return true;

    // 3. Final step → delegates to last custom step's role check
    if (IsFinal(step))
    {
        var lastCustomStep = await contentWorkflowStepRetriever.GetLastCustomStep(...);
        if (lastCustomStep is null) return true;
        return await CanWorkWithContentItemInStepInternal(lastCustomStep, userId, ...);
    }

    // 4. Custom step → user must be in a role assigned to this step
    var assignedStepRoles = await contentWorkflowRolesRetriever.GetWorkflowStepRoles(step.ContentWorkflowStepID, ...);
    return assignedStepRoles.Any(stepRole => user.IsInRole(stepRole?.RoleName));
}

Full control check — WorkflowStepRoleArbiter.cs:

private async Task<bool> HasFullControlInternal(int workflowId, UserInfo user, ...)
{
    var fullControlRoles = await contentWorkflowRolesRetriever.GetFullControlRoles(workflowId, ...);
    return fullControlRoles.Any(role => user.IsInRole(role.RoleName));
}

Execution order summary

User clicks Publish
  │
  ├─ 1. PageInvokerBase.CheckPermission("View")          ← Application permission
  │     └─ uiPermissionEvaluator.Evaluate("View")
  │
  ├─ 2. ContentTab.Publish() body                        ← ACL permission
  │     └─ CheckAclPermission(pageId, "Update")
  │           └─ WebPageAclPermissionEvaluator.Evaluate()
  │                 ├─ IsChannelAdmin? → bypass
  │                 └─ Has Read AND Update in ACL? → pass/fail
  │
  └─ 3. WebPageCommandManager.Publish()                  ← Workflow check
        └─ PublishInternal()
              ├─ IsUnderWorkflow? = false → proceed to publish
              └─ IsUnderWorkflow? = true  → ERROR (must use ChangeWorkflowStep)
                    └─ ChangeWorkflowStepInternal()
                          └─ CanWorkWithContentItemInCurrentStep()
                                └─ WorkflowStepRoleArbiter
                                      ├─ Draft? → allowed
                                      ├─ Full control? → allowed
                                      ├─ Final? → check last custom step roles
                                      └─ Custom? → user in step's assigned roles?

