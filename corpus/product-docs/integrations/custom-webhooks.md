# Custom Webhooks

Trigger Helix workflows from any service that can send an HTTP POST request.

## Creating a webhook trigger

1. In the workflow editor, add a Webhook trigger.
2. Helix generates a unique URL: `https://hooks.helix.io/wf/<workflow-id>/<token>`.
3. Configure your external service to POST to this URL when the event occurs.

## Request format

Helix accepts any JSON body. The body is parsed and made available as `{trigger.body}` in subsequent steps.

Headers and query parameters are also accessible:
- `{trigger.headers}`
- `{trigger.query}`

## Authentication

By default, webhook URLs are unauthenticated — anyone with the URL can trigger your workflow. For sensitive workflows, enable signature verification:

1. In the trigger settings, enable **Verify signature**.
2. Helix generates a webhook secret. Copy it.
3. Configure your external service to sign requests with **HMAC-SHA256** using the secret.
4. Send the signature in the **X-Helix-Signature** header.

Helix will reject requests with invalid or missing signatures.

## Timeouts and retries

- Helix webhook endpoints respond within **30 seconds** of receiving a request.
- If your service expects a synchronous response, your workflow's first step's output will be returned. Otherwise, Helix returns 200 immediately and processes the workflow asynchronously.
- If Helix's endpoint is temporarily unavailable, callers should retry with backoff. We recommend **3** retries.

## Outbound webhooks

To send a webhook from a workflow, use the **HTTP** action. You can sign outbound webhooks by computing an HMAC over the body and adding it as a header.
