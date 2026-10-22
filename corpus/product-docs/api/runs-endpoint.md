# Runs Endpoint

Trigger and inspect workflow runs.

## Trigger a run

```
POST https://api.helix.io/v2/workflows/{workflow_id}/runs
Content-Type: application/json

{
  "input": { "any": "json data" }
}
```

Returns immediately with a `run_id`. The run executes asynchronously.

## Get a run

```
GET https://api.helix.io/v2/runs/{run_id}
```

Returns the run's current state including:
- `status`: `pending`, `running`, `succeeded`, `failed`, `cancelled`
- `started_at`, `finished_at`
- `steps`: array of step executions with their inputs and outputs
- `error`: details if the run failed

## List runs

```
GET https://api.helix.io/v2/runs
```

Query parameters:
- `workflow_id` (filter by workflow)
- `status` (filter by status)
- `started_after`, `started_before` (ISO 8601 timestamps)
- `limit` (default 25, max 100)
- `cursor` (pagination)

## Cancel a run

```
POST https://api.helix.io/v2/runs/{run_id}/cancel
```

Cancels a running execution. Already-completed steps are not rolled back.

## Retention

Run records are retained for **90 days** on Pro plans and **365 days** on Enterprise plans. Older runs are deleted automatically.
