# API Versioning

Helix's API is versioned in the URL path: `https://api.helix.io/v2`.

## Current version

**v2** is the current stable version.

## Backwards compatibility

Within a major version, the following changes will not be made:

- Removing endpoints
- Removing fields from responses
- Adding required fields to requests
- Changing the type of an existing field

The following changes are considered backwards compatible:

- Adding new endpoints
- Adding new optional fields to requests
- Adding new fields to responses (your client should ignore unknown fields)
- Adding new error codes (handle unknown codes generically)

## Deprecation policy

When we deprecate an endpoint or field:

1. Documentation is updated to mark it deprecated.
2. Responses include a `Deprecation` header.
3. The deprecated feature continues to work for at least 12 months.
4. We send email notices to API key owners 30 days before removal.

## Version history

- **v2** (current): Released 2023. Adds webhooks, scoped API keys, GraphQL endpoint.
- **v1** (deprecated): Released 2020. Sunset date 2024-12-31.
