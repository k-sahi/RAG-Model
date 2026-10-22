# Slack Integration

Connect Helix to Slack to post messages, read channels, and trigger workflows from Slack events.

## Connecting

1. Go to **Integrations → Slack → Connect**.
2. You will be redirected to Slack's authorization page.
3. Grant Helix the requested scopes (channels:read, chat:write, im:write).
4. Confirm. The connection is now ready.

## Triggers

- **New message in channel**: Fires when a message is posted in a specified channel.
- **Reaction added**: Fires when a user adds an emoji reaction.
- **Slash command**: Fires when a user runs a custom slash command.

## Actions

- **Send channel message**: Post a message to a channel. Supports markdown and Slack Block Kit JSON.
- **Send DM**: Direct message a user. Requires the user's Slack ID or email.
- **Update message**: Edit a previously-sent message by timestamp.
- **Add reaction**: Add an emoji reaction to a message.

## Block Kit support

For rich messages, paste Slack Block Kit JSON into the message body. Helix will substitute `{{variables}}` before sending.

## Bot vs user posting

Messages are posted by the Helix bot user. To make messages appear from a specific user, use the user's Slack token directly via the HTTP integration.
