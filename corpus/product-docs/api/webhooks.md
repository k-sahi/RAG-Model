# Webhooks

Subscribe to Helix events in your own services.

## Creating a webhook subscription

```
POST https://api.helix.io/v2/webhooks
{
  "url": "https://yourapp.com/helix-webhook",
  "events": ["run.succeeded", "run.failed"],
  "secret": "your_signing_secret"
}
```

## Available events

- `workflow.created`
- `workflow.updated`
- `workflow.deleted`
- `run.started`
- `run.succeeded`
- `run.failed`
- `run.cancelled`

## Verifying signatures

Every webhook delivery includes a **X-Helix-Signature** header containing an **HMAC-SHA256** signature of the body, computed with your subscription's secret.

To verify in Python:

```python
import hmac, hashlib
expected = hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()
if not hmac.compare_digest(expected, received_signature):
    raise Exception("Invalid signature")
```

## Delivery and retries

Helix POSTs the event to your URL with a **30 seconds** timeout. If your endpoint returns 2xx, the delivery is marked successful.

If your endpoint fails (timeout, 5xx, or non-2xx), Helix retries up to **3** times with exponential backoff.

After all retries fail, the delivery is marked permanently failed and a notification is sent to the workspace owner.

## Inspecting deliveries

The **Webhook Logs** page shows every delivery attempt with status code, response body, and timing.
