# Glossary

Key terms used throughout Helix documentation.

**Workflow** — An automated sequence of steps that runs when a trigger fires.

**Trigger** — The event that starts a workflow. Can be a webhook, schedule, app event, or manual run.

**Step** — A single action within a workflow. Steps run in order and can pass data to subsequent steps.

**Run** — A single execution of a workflow. Each run is logged and can be inspected after the fact.

**Integration** — A connection to a third-party service like Slack or Salesforce.

**Workspace** — Your team's container for workflows, integrations, and settings. Each workspace is isolated.

**Connection** — A specific authenticated link to an integration. You can have multiple connections for the same integration (e.g., two Slack workspaces).

**Schedule** — A cron expression that runs a workflow at fixed intervals.

**Manual approval** — A step that pauses a workflow until a designated user approves or rejects it.

**Audit log** — A record of every administrative action in your workspace. Available on Enterprise plans.
