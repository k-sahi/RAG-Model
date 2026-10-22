# Slack Notifications

Send Helix events to Slack channels for team-wide visibility.

## Setup

1. Connect your Slack workspace in **Integrations → Slack**.
2. Go to **Settings → Notifications → Slack**.
3. Add a channel destination — choose the channel and event types.

## Event types

- All workflow failures (workspace-wide)
- Specific workflow failures
- Daily summary digest
- High-priority alerts (downtime, security events)
- Custom events via webhook

## Message format

Helix Slack messages use Block Kit. Each message includes:

- Workflow name and link
- Status (succeeded / failed)
- Trigger summary
- Action buttons (Re-run, View logs, Acknowledge)

## Channel vs DM

Notifications can go to channels (visible to all members) or DMs (private to a user). DM destinations require the recipient to have authorized the Helix Slack app.

## Threading

To reduce channel noise, enable **Thread updates**. Subsequent updates to the same workflow run are posted as replies to the original message instead of new messages.
