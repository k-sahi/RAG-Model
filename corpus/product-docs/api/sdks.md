# Official SDKs

Helix maintains official SDKs for major languages.

## Available SDKs

- **Python** — `pip install helix-sdk`
- **Node.js** — `npm install @helix/sdk`
- **Go** — `go get github.com/helix/helix-go`
- **Ruby** — `gem install helix-sdk`

## Authentication

All SDKs accept an API key via constructor or environment variable.

### Python

```python
from helix import Helix
client = Helix(api_key="hlx_live_xxxxxxxx")
workflows = client.workflows.list()
```

### Node.js

```javascript
const { Helix } = require('@helix/sdk');
const client = new Helix({ apiKey: 'hlx_live_xxxxxxxx' });
const workflows = await client.workflows.list();
```

## Environment variable

If `HELIX_API_KEY` is set, you can omit the constructor argument:

```python
client = Helix()  # reads HELIX_API_KEY
```

## Versioning

SDK versions follow semver. The major version matches the API version (e.g., SDK 2.x matches API v2).

## Issues and feedback

Report bugs at github.com/helix/helix-{language}. PRs are welcome.
