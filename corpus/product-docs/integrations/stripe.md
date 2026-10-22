# Stripe Integration

Process payments, manage subscriptions, and react to billing events from Stripe.

## Connecting

1. Go to **Integrations → Stripe → Connect**.
2. You will be redirected to Stripe's OAuth flow.
3. Choose the Stripe account to connect (live or test).
4. Approve and return.

## Triggers

- **Payment succeeded**: A payment was successfully captured.
- **Payment failed**: A payment attempt failed.
- **Subscription created**: A new subscription started.
- **Subscription cancelled**: A subscription was cancelled.
- **Invoice paid**: An invoice was paid.
- **Customer created**: A new customer record was created.

## Actions

- **Create customer**: Add a new customer to Stripe.
- **Create subscription**: Subscribe a customer to a price.
- **Charge a payment method**: One-time charge against a saved payment method.
- **Issue refund**: Refund a previous payment, fully or partially.
- **Look up customer**: Find a customer by email or ID.

## Test mode

If you connect a Stripe test account, all events use Stripe's test data. Helix labels test connections with a yellow badge so you don't confuse them with live.

## Webhook reliability

Stripe events are delivered to Helix via webhooks. If our webhook endpoint is down, Stripe retries with exponential backoff for up to 3 days. Missed events during longer outages can be backfilled via the **Sync events** action.
