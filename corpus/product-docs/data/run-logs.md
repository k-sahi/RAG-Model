# Run Logs

Every workflow run is logged with full step-by-step detail.

## What is logged

For each run:

- Trigger payload
- Each step's input and output
- Errors and stack traces (if any)
- Timing for each step
- Total run duration
- Status transitions

## Accessing run logs

**Runs** in the sidebar shows a unified list. Filter by workflow, status, date.

Click any run to see step-by-step detail. Each step is expandable to show its inputs and outputs in JSON.

## Sensitive data

By default, all run data is logged including any secrets passed through the workflow. To redact specific fields:

1. Open a workflow
2. **Settings → Sensitive fields**
3. Add field names that should be redacted in logs (e.g., `password`, `ssn`, `credit_card`)

Redacted fields appear as `[redacted]` in run logs. Note: this only affects log display; the data itself is still passed through the workflow at runtime.

## Retention

- Pro: **90 days**
- Enterprise: **365 days**

After retention expires, runs are permanently deleted.

## Searching logs

Search by run ID, workflow name, status, or any text contained in step input/output. Search is full-text and case-insensitive.

## Exporting logs

See "Exporting Data" for full export options.
