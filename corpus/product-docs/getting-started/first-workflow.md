# Your First Workflow

This tutorial walks you through creating your first workflow in Helix.

## What you will build

A workflow that posts a Slack message every time a new row is added to a Google Sheet.

## Prerequisites

- Connected Slack integration
- Connected Google Drive integration
- A Google Sheet with at least one column

## Steps

### 1. Create the workflow

From the dashboard, click **New Workflow**. Give it a name like "New row to Slack".

### 2. Add a trigger

Click **Add Trigger** and select Google Sheets. Choose "New row added" as the event. Select your spreadsheet and the worksheet within it.

### 3. Add an action

Click the **+** below the trigger to add an action. Select Slack and choose "Send channel message". Pick the channel and write your message. You can reference data from the trigger using `{{trigger.row.column_name}}` syntax.

### 4. Test the workflow

Click **Test** in the top right. Helix will run the workflow with sample data so you can verify the output before going live.

### 5. Activate

Toggle the workflow to **Active** in the top right. Your workflow is now live.

## What happens next

Every time a new row is added to your sheet, Helix will post to Slack within 60 seconds. You can view every run under the **Runs** tab.
