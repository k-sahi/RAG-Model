# Workflow Versioning

Every change to a workflow creates a new version. Helix retains the last **50 versions** of each workflow.

## How versions are created

A new version is created when you click **Save** in the workflow editor with at least one change. Minor edits like renaming or comment changes are batched into a single version if saved within 5 minutes.

## Viewing version history

In the workflow editor, click **Version History** in the top right. You will see a list of versions with timestamps and the user who made each change.

## Reverting to a prior version

Click any version and select **Restore**. This creates a new version that matches the selected one — it does not delete the versions in between. Active runs are not affected; they continue using the version they started on.

## Comparing versions

Click **Compare** to see a side-by-side diff of two versions. Added, modified, and removed steps are highlighted.

## Production vs draft

Helix has a single live version per workflow. There is no separate "production" and "staging" environment within a workflow. To stage changes, clone the workflow and test the clone before promoting changes to the original.

## Version retention

Versions older than the 50-version limit are deleted automatically. To preserve historical state beyond this, export the workflow as JSON via the API.
