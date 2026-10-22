# Roles and Permissions

Helix uses role-based access control. Every user in a workspace has exactly one role.

## Available roles

- **Owner**
- **Admin**
- **Editor**
- **Viewer**

## What each role can do

| Capability | Owner | Admin | Editor | Viewer |
|------------|-------|-------|--------|--------|
| View workflows | ✓ | ✓ | ✓ | ✓ |
| Run workflows manually | ✓ | ✓ | ✓ |  |
| Create / edit workflows | ✓ | ✓ | ✓ |  |
| Manage integrations | ✓ | ✓ | ✓ |  |
| Invite users | ✓ | ✓ |  |  |
| Manage roles | ✓ | ✓ |  |  |
| Manage billing | ✓ |  |  |  |
| Delete workspace | ✓ |  |  |  |
| Transfer ownership | ✓ |  |  |  |

## The Owner role

Each workspace has exactly one Owner. The Owner has all permissions including billing and workspace deletion. To change Owner, the current Owner must transfer ownership in **Settings → Workspace → Transfer ownership**.

## Changing a user's role

Admins and Owners can change roles in **Settings → Team**. Click a user's row to see role options.

## Custom roles

Custom roles are available on Enterprise plans. Contact your account team to define roles with specific scopes.
