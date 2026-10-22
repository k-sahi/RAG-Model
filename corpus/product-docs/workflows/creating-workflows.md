# Creating Workflows

Workflows are the core of Helix. This guide covers everything you need to know about building them.

## Workflow structure

Every workflow has exactly one trigger and one or more steps. Steps run sequentially by default but can be branched, looped, or run in parallel.

## Creating a new workflow

From the **Workflows** page, click **New Workflow**. You will be taken to the workflow builder.

## Workflow limits

- Maximum steps per workflow: **100**
- Maximum runtime per run: **30 minutes**
- Workflow versions retained: **50** (older versions are deleted automatically)

If your workflow exceeds these limits, the run will be terminated and marked as failed.

## Naming conventions

While not required, we recommend descriptive workflow names with action verbs (e.g., "Post new leads to #sales" rather than "Slack workflow"). Names are searchable in the dashboard.

## Activating workflows

A workflow does not run until it is set to Active. Toggle the **Active** switch in the workflow editor. Inactive workflows can still be tested manually.

## Cloning workflows

Right-click any workflow and select **Clone** to create a copy. The clone is created in Inactive state to prevent accidental duplicate runs.
