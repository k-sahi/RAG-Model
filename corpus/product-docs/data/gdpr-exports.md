# GDPR Data Subject Requests

Helix supports the rights granted to data subjects under GDPR, CCPA, and similar regulations.

## Right to access

To export all personal data Helix holds about a specific user:

1. **Settings → Privacy → Data subject requests → New access request**
2. Enter the data subject's email
3. Confirm the request

Helix compiles a JSON archive within 7 days containing:

- The user's profile and authentication data
- Workspaces they belong to
- Workflows they created or last modified
- Runs they triggered manually
- Audit log entries where they were the actor

The archive is delivered via signed URL valid for **24 hours**.

## Right to deletion

To permanently delete a user and all associated data:

1. **Settings → Privacy → Data subject requests → New deletion request**
2. Enter the data subject's email and confirm
3. The deletion happens within **30 days**

The 30-day window allows you to cancel the request. After the window, deletion is irreversible.

## What is deleted vs anonymized

- **Deleted**: profile, authentication, personal preferences
- **Anonymized**: audit log entries (the actor field becomes `[deleted-user]`)
- **Retained**: workflows the user created (transferred to the workspace owner)

## Data Processing Agreements

Helix offers a standard DPA. Sign at **Settings → Compliance → DPA**. Custom DPAs are available for Enterprise.

## Sub-processors

A complete list of Helix sub-processors is at https://helix.io/legal/subprocessors.
