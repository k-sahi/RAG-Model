# User Provisioning

Add users to your workspace via invitation, SSO, or SCIM.

## Invitation flow

1. **Settings → Team → Invite users**
2. Enter email addresses (comma-separated for bulk)
3. Choose a role for the invitees
4. Send invitations

Invitees receive an email with a join link. Links expire after 7 days. To resend, click the user row in **Pending invitations** and select **Resend**.

## SSO auto-provisioning

If SSO is enabled, new users authenticated by your IdP are auto-provisioned. The default role is Editor; configure under **Settings → Security → SSO**.

## SCIM auto-provisioning

With SCIM, users in selected IdP groups are automatically provisioned and deprovisioned. See SCIM documentation for setup.

## Bulk invitation via API

```
POST /v2/users/invite
{
  "users": [
    {"email": "alice@company.com", "role": "Editor"},
    {"email": "bob@company.com", "role": "Viewer"}
  ]
}
```

## Domain capture

Enterprise customers can claim email domains so all users with matching emails are auto-provisioned to your workspace on first sign-in. Contact your account team.
