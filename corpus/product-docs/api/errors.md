# API Errors

Helix uses standard HTTP status codes and returns structured error bodies.

## Error codes

| Code | Meaning |
|------|---------|
| 400 | Bad request — malformed JSON or missing required fields |
| 401 | Invalid or expired API key |
| 403 | Insufficient permissions for this resource |
| 404 | Resource not found |
| 422 | Validation error — check request body |
| 429 | Rate limit exceeded |
| 500 | Internal server error |
| 503 | Service temporarily unavailable |

## Error body format

```json
{
  "error": {
    "type": "validation_error",
    "message": "Workflow name must be between 1 and 64 characters",
    "field": "name",
    "request_id": "req_abc123"
  }
}
```

Always log `request_id` — our support team can use it to investigate issues.

## Retrying

- 5xx errors should be retried with exponential backoff.
- 429 errors should be retried after the `Retry-After` delay.
- 4xx errors (except 429) should NOT be retried — they indicate a permanent problem with your request.

## Idempotency

Mutating endpoints support an optional `Idempotency-Key` header. Pass any unique string. Helix will return the same response for repeated requests with the same key, allowing safe retries.
