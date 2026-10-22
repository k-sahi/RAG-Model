# API Overview

The Helix API lets you manage workflows, runs, and integrations programmatically.

## Base URL

All API requests go to:

```
https://api.helix.io/v2
```

## Authentication

All requests require an API key in the **Authorization** header:

```
Authorization: Bearer hlx_live_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

## API key formats

- **Live keys**: `hlx_live_<32 hex chars>` — affects production resources.
- **Test keys**: `hlx_test_<32 hex chars>` — sandboxed; safe for development.

Generate API keys from **Settings → API Keys**. Keep keys secret — never commit them to version control.

## Plan requirements

API access is included on Pro and Enterprise plans. Starter plans do not include API access.

## Versioning

The current version is **v2**. We maintain backwards compatibility within a major version. Breaking changes will be released as v3 with at least 12 months of overlap.

## Quick start

```bash
curl https://api.helix.io/v2/workflows \
  -H "Authorization: Bearer hlx_live_xxxxxxxx"
```
