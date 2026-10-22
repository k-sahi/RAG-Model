# Workflows Endpoint

Manage workflows programmatically.

## List workflows

```
GET https://api.helix.io/v2/workflows
```

Returns a paginated list of workflows in the workspace.

Query parameters:
- `limit` (default 25, max 100)
- `cursor` (for pagination)
- `status` (filter by `active` or `inactive`)

## Get a workflow

```
GET https://api.helix.io/v2/workflows/{workflow_id}
```

Returns the full workflow definition including all steps.

## Create a workflow

```
POST https://api.helix.io/v2/workflows
Content-Type: application/json

{
  "name": "My new workflow",
  "trigger": { "type": "webhook" },
  "steps": [...]
}
```

Returns the created workflow with a generated `workflow_id`.

## Update a workflow

```
PATCH https://api.helix.io/v2/workflows/{workflow_id}
Content-Type: application/json

{
  "name": "Updated name"
}
```

Updates only the fields included. Supplying a full `steps` array creates a new version.

## Delete a workflow

```
DELETE https://api.helix.io/v2/workflows/{workflow_id}
```

Soft-deletes the workflow. Existing runs continue to completion. Hard deletion happens 30 days later.

## Activate / deactivate

```
POST https://api.helix.io/v2/workflows/{workflow_id}/activate
POST https://api.helix.io/v2/workflows/{workflow_id}/deactivate
```
