# Usage and Overages

Track your workflow run consumption and understand overage charges.

## Viewing usage

**Settings → Billing → Usage** shows:

- Current month's run count vs plan limit
- Daily run breakdown
- Top workflows by run count
- Projected end-of-month total

## Overage handling

If you exceed your plan's run limit:

- **Starter**: Overage runs are blocked. Upgrade to Pro or wait until next month.
- **Pro**: Overage runs are allowed at $0.01 per additional run, billed at the end of the month.
- **Enterprise**: Overages are negotiated per contract.

## Run limit alerts

By default, Helix sends email alerts at 80%, 100%, and 125% of your monthly limit. Configure recipients under **Settings → Billing → Alerts**.

## What counts as a run

A "run" is a single execution of a workflow trigger-to-completion. Failed runs count. Test runs do **not** count. Manual triggers count. Cancelled runs are pro-rated based on steps executed.

## Reducing run consumption

If you're consistently near your limit:

- Consolidate workflows that always run together.
- Use conditions to early-exit workflows that don't need the full pipeline.
- Switch high-frequency triggers to lower-frequency schedules.
- Upgrade to a higher plan with more headroom.
