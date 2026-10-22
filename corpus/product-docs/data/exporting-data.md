# Exporting Data

Export your workflow runs, audit logs, and workspace metadata.

## What can be exported

- Workflow definitions (JSON)
- Workflow runs (JSON or CSV)
- Audit log (CSV or JSON, Enterprise only)
- User list (CSV)

## Initiating an export

**Settings → Data → Export**. Choose the data type, date range, and format.

## How exports are delivered

Exports are generated asynchronously. When ready, you receive an email with a signed download URL. The URL is valid for **24 hours**.

For programmatic access, use the API:

```
POST /v2/exports
{
  "type": "runs",
  "format": "csv",
  "started_after": "2024-01-01"
}
```

The response returns an `export_id`. Poll `/v2/exports/{export_id}` until status is `complete`, then download via the included URL.

## Large exports

Exports over 1 GB are split into multiple files (one per 1 GB). The email contains a manifest listing all parts.

## Export limits

- Maximum 5 active exports per workspace at a time.
- Exports requesting more than 1 year of data may take several hours.

## GDPR / DSAR exports

For data subject access requests, see the GDPR documentation.
