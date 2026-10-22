# Triggers

A trigger is the event that starts a workflow. Every workflow has exactly one trigger.

## Trigger types

### Webhook trigger
Helix generates a unique URL for your workflow. Send a POST request to this URL to trigger a run. The request body is available as `{{trigger.body}}` in subsequent steps.

### Schedule trigger
Run a workflow on a fixed schedule using cron syntax. The format is the standard 5-field cron expression: `minute hour day-of-month month day-of-week`.

Examples:
- `0 9 * * 1-5` — Every weekday at 9am UTC
- `*/15 * * * *` — Every 15 minutes
- `0 0 1 * *` — First day of every month

All schedules run in UTC.

### App event trigger
Trigger when something happens in a connected app — for example, "new row in Google Sheets" or "new contact in HubSpot". Available events depend on the integration.

### Manual trigger
Run only when manually started from the dashboard or API. Useful for ad-hoc workflows.

## Trigger data

Trigger data is available throughout your workflow via the `trigger` object. The exact shape depends on the trigger type. You can inspect the trigger payload in the Runs view.
