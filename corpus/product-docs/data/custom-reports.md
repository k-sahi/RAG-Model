# Custom Reports

Build and schedule custom reports on top of your workspace data.

## Creating a report

**Analytics → Reports → New**. Define:

- Data source (runs, workflows, audit log, users)
- Filters (date range, status, workflow)
- Grouping (by day, week, workflow, user)
- Metrics (count, sum, average, p95)

## Saving and scheduling

Save the report and optionally schedule delivery:

- Frequency: daily, weekly, monthly
- Recipients: any email addresses
- Format: PDF, CSV, or inline HTML

## Report templates

Helix includes pre-built templates:

- Weekly run volume by workflow
- Monthly cost report (Pro+)
- Failed run summary
- User activity

## Programmatic access

Run reports via API:

```
POST /v2/reports/{report_id}/run
```

The response is a job ID; poll until complete.

## Plan availability

- Starter: default dashboards only
- Pro: custom dashboards and reports
- Enterprise: all of the above plus scheduled streaming to S3 / Snowflake / BigQuery
