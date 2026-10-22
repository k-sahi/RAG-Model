# Scheduling Workflows

Helix supports scheduled workflows using standard 5-field cron expressions.

## Cron format

A cron expression has 5 fields:

```
minute (0-59)  hour (0-23)  day-of-month (1-31)  month (1-12)  day-of-week (0-6, 0=Sunday)
```

## Common patterns

| Schedule | Cron expression |
|----------|----------------|
| Every hour | `0 * * * *` |
| Every day at 9am | `0 9 * * *` |
| Weekdays at 9am | `0 9 * * 1-5` |
| Every 15 minutes | `*/15 * * * *` |
| First of the month | `0 0 1 * *` |
| Every Sunday at midnight | `0 0 * * 0` |

## Timezone handling

All schedules run in **UTC**. Helix does not currently support per-workflow timezones. To run at 9am in your local time, calculate the UTC offset and adjust accordingly.

## Schedule precision

Scheduled workflows are dispatched within 60 seconds of their scheduled time. Do not rely on cron for sub-minute precision — use webhook triggers if precise timing is critical.

## Daylight saving time

Because Helix uses UTC, DST does not affect your schedules. If your local time observes DST, your workflow's local trigger time will shift by one hour twice a year.
