# Managing Connections

Connections are the authenticated links between Helix and your external apps.

## Viewing connections

**Integrations → All connections** lists every active and inactive connection in your workspace.

## Renaming connections

Click a connection's name to edit it. Names appear in the workflow builder, so use descriptive labels for multi-account setups (e.g., "Salesforce — Sandbox" vs "Salesforce — Production").

## Reconnecting

If a connection expires, click **Reconnect** to re-run the OAuth flow. Existing workflows will resume using the renewed connection.

## Deleting connections

Deleting a connection is permanent. Workflows that reference the deleted connection will fail until updated to use a different connection. Helix shows you a list of impacted workflows before confirming deletion.

## Sharing connections

By default, connections are shared across the entire workspace. Anyone with permission to build workflows can use any connection. To restrict this, contact your account admin about Connection Permissions (Enterprise feature).

## Connection rotation

For security-sensitive integrations, rotate credentials periodically. The recommended frequency is every 90 days. To rotate:

1. Disconnect the existing connection.
2. Reconnect with refreshed credentials.
3. Workflows will pick up the new credentials automatically.
