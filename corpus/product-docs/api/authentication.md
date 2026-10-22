# API Authentication

The Helix API uses bearer token authentication.

## Generating API keys

1. Go to **Settings → API Keys**.
2. Click **Create new key**.
3. Choose **Live** or **Test**.
4. Name the key (for your reference).
5. Copy the key immediately — Helix shows it once and never again.

## Using the key

Include the key in the `Authorization` header of every request:

```
Authorization: Bearer hlx_live_a1b2c3d4...
```

## Key permissions

By default, API keys have full access to your workspace. To restrict a key, configure **Scoped keys** under **Settings → API Keys → Advanced**:

- `workflows:read`
- `workflows:write`
- `runs:read`
- `runs:trigger`
- `integrations:read`

## Rotating keys

To rotate:

1. Generate a new key.
2. Update your applications to use the new key.
3. Once you've verified the new key works, delete the old key.

Deleted keys cannot be recovered.

## Common authentication errors

- **Invalid or expired API key** — Returned as 401. The key is missing, malformed, or has been deleted.
- **Insufficient permissions for this resource** — Returned as 403. The key is valid but doesn't have the scope to perform this action.
