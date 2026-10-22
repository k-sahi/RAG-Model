# Pagination

Helix uses cursor-based pagination for all list endpoints.

## How it works

List responses include a `next_cursor` field. To fetch the next page, pass this value as the `cursor` query parameter.

```json
{
  "data": [...],
  "next_cursor": "eyJpZCI6Imxhc3RfaXRlbV9pZCJ9",
  "has_more": true
}
```

When `has_more` is `false`, you have reached the end. The `next_cursor` field will be omitted.

## Page size

Use the `limit` query parameter to control page size. The default is 25 and the maximum is 100.

```
GET https://api.helix.io/v2/runs?limit=100
```

## Stable ordering

Pagination is stable: items added or removed during paging will not cause duplicates or skips. Items are ordered by creation time descending unless otherwise documented.

## Common mistake

Do not infer the cursor from the data. The `next_cursor` is opaque — its format may change. Always use the value returned by the previous response.
