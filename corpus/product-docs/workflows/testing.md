# Testing Workflows

Test before you ship. Helix provides several mechanisms for validating workflows without affecting production data.

## Test mode

In the workflow editor, click **Test**. Helix will:

1. Prompt you for sample trigger data (or use the most recent real trigger).
2. Run every step with that data.
3. Show you the inputs and outputs of each step.

Test runs do not count toward your monthly run quota.

## Step-level testing

Each step has a **Test this step** button. This is useful when debugging a specific step without re-running the whole workflow.

## Test data sources

You can provide test data via:

- **Manual entry**: Type a JSON payload.
- **Sample data**: Use a recent real run as the input.
- **Stored fixtures**: Save commonly-used test payloads under **Settings → Test data**.

## Production safety

By default, test runs **do** call external services. If your workflow sends emails or charges credit cards, test runs will perform those actions. To disable side effects, enable **Dry run mode** in the test panel — Helix will mock external calls and return synthesized responses.

## Continuous testing

For Enterprise customers, Helix supports scheduled workflow tests via the API. You can set up monitoring that runs your critical workflows nightly with known inputs and alerts you if outputs drift.
