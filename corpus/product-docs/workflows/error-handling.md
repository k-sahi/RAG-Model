# Error Handling and Retries

When a workflow step fails, Helix automatically retries before marking the run as failed.

## Default retry behavior

Failed steps retry **3 times** with exponential backoff:

- 1st retry: after **1 minute**
- 2nd retry: after **5 minutes**
- 3rd retry: after **25 minutes**

If all retries fail, the run is marked as **Failed** and the workflow's failure handler runs (if configured).

## What counts as a failure

- Network errors (timeouts, connection refused)
- HTTP 5xx responses from integrated apps
- HTTP 429 (rate limit) responses
- Explicit step errors (e.g., a Code step throwing an exception)

HTTP 4xx responses (except 429) are **not** retried because they typically indicate a permanent problem (bad request, unauthorized).

## Custom retry configuration

You can override the default retry settings on individual steps:

- **Retry count**: 0 to 5
- **Backoff strategy**: Fixed, Linear, or Exponential
- **Initial delay**: 0s to 5min

## Failure handlers

Configure a failure handler at the workflow level under **Settings → Failure handler**. The handler can:

- Send a Slack or email notification
- Trigger another workflow
- Write to a Failures collection for later review

## Idempotency

Because steps may retry, your integrations should be idempotent. For HTTP calls, include an `Idempotency-Key` header to avoid duplicate side effects.
