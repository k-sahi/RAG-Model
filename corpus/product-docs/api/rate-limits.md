# API Rate Limits

Helix enforces rate limits to ensure platform stability and fair use.

## Limits by plan

| Plan | Requests per minute |
|------|---------------------|
| Starter | API access not included |
| Pro | **1000** |
| Enterprise | **unlimited** |

Limits are per-workspace, not per-API-key. All keys in the same workspace share the budget.

## Rate limit headers

Every API response includes these headers:

```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 847
X-RateLimit-Reset: 1714515600
```

`X-RateLimit-Reset` is a Unix timestamp indicating when the budget refills.

## When you hit the limit

Helix returns **429 with Retry-After header**. The Retry-After header indicates how many seconds to wait before retrying.

```
HTTP/1.1 429 Too Many Requests
Retry-After: 23
```

## Best practices

- **Respect Retry-After**: Pause your client when you receive 429 and resume after the indicated delay.
- **Implement exponential backoff**: For repeated 429s, double the wait between retries.
- **Batch where possible**: Some endpoints support bulk operations to reduce request count.
- **Use webhooks instead of polling**: If you're polling for changes, switch to webhooks.

## Exemptions

Enterprise customers can request a custom rate limit by contacting their account team.
