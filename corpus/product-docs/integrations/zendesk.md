# Zendesk Integration

Sync tickets, automate responses, and react to support events from Zendesk.

## Connecting

OAuth via your Zendesk subdomain. You will need an admin or agent role in Zendesk to authorize.

## Triggers

- **New ticket**: A new ticket was created.
- **Ticket updated**: A ticket's status, priority, or assignee changed.
- **Ticket solved**: A ticket was marked as solved.
- **New comment**: A comment was added to a ticket (private or public).

## Actions

- **Create ticket**: Open a new ticket with subject, description, and assignee.
- **Update ticket**: Change status, priority, or assign to a user.
- **Add comment**: Post a comment to a ticket (public or internal).
- **Find user**: Look up a Zendesk user by email or external ID.
- **Search tickets**: Run a Zendesk search query and return matching tickets.

## SLA awareness

When triggered by an SLA breach, you will receive a payload that includes the SLA target, time remaining, and the ticket's current state. This is useful for escalation workflows.

## API rate limits

Zendesk's API allows 700 requests per minute for most plans. Helix queues requests above this rate to avoid 429 errors but will not retry indefinitely; persistent overload causes runs to fail.
