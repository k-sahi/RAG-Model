# Audit Log

Track every administrative action in your workspace. Available on the Enterprise plan.

## What is logged

- User invitations, role changes, removals
- Workflow create/update/delete
- Integration connections, disconnections
- API key creation and deletion
- Settings changes (SSO config, IP allowlist, etc.)
- Billing events

Workflow runs and integration data flow are not in the audit log; see Run logs for those.

## Accessing the log

**Settings → Audit Log**. Each entry includes:

- Timestamp (UTC)
- Actor (user or API key)
- Action (e.g., `workflow.update`)
- Target (the resource affected)
- IP address and user agent

## Searching and filtering

Filter by date range, actor, action type, or target. Free-text search matches across all fields.

## Retention

Audit log entries are retained for **365 days**.

## Export

Export the audit log to CSV or JSON for compliance or external SIEM ingestion. Exports are generated asynchronously and emailed when ready.

## SIEM streaming

For real-time SIEM integration, configure a webhook destination in **Settings → Audit Log → Stream**. Events are delivered within 60 seconds of occurrence.
