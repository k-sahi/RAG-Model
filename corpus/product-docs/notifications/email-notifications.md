# Email Notifications

Configure when Helix emails you about workflow events.

## Personal notification settings

**Settings → Notifications → Email** lets each user configure:

- Workflow run failures (mine, my team's, all)
- Run failures for specific workflows
- Daily/weekly summaries
- Billing events
- Security events (login from new device, password change, etc.)

## Workspace-wide notifications

Admins can configure workspace defaults that apply to all users unless individually overridden.

## Failure notifications

For workflow failures, the email includes:

- Workflow name and link to the run
- Trigger payload (truncated to 1 KB)
- Error message and step name
- Suggested next steps

## Frequency limits

To prevent inbox flooding, Helix throttles failure notifications. If a workflow fails 10+ times within an hour, subsequent failures are batched into a single email.

## Disabling all email

To disable all Helix email except mandatory account / billing emails, toggle **Pause all email** in notification settings. This is useful during long maintenance windows.
