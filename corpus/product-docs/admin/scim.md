# SCIM Provisioning

Automate user lifecycle with SCIM 2.0. Available on the Enterprise plan.

## What SCIM does

SCIM lets your identity provider automatically:

- Create Helix users when added to your IdP.
- Update user attributes (name, email, role) on changes.
- Deactivate users when removed from your IdP.

## Supported providers

- Okta
- Azure AD / Microsoft Entra
- OneLogin
- JumpCloud
- Any SCIM 2.0-compliant provider

## Setup

1. Enable SCIM in **Settings → Security → SCIM**.
2. Helix issues a SCIM token. Copy it.
3. In your IdP, create a SCIM provisioning app pointing to:
   - **SCIM URL**: `https://api.helix.io/v2/scim/v2`
   - **Token**: the token from step 2.
4. Map your IdP attributes to Helix attributes (email, displayName, role).
5. Enable provisioning and select which IdP groups sync to Helix.

## Role mapping

By default, all SCIM-provisioned users get the **Editor** role. To map roles, set the SCIM `userType` attribute to one of: `Owner`, `Admin`, `Editor`, `Viewer`. The Owner role cannot be assigned via SCIM — use the Helix UI for that.

## Deactivation

When SCIM marks a user as inactive, Helix:

1. Revokes all active sessions.
2. Disables API keys created by that user (within 1 hour).
3. Marks the user as deactivated but does not delete their data.

To fully delete a user, an Admin must do so from the Helix UI.
