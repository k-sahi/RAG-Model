# Payment Methods

Helix accepts credit cards, ACH transfer, and (Enterprise only) wire transfer or invoice billing.

## Adding a payment method

**Settings → Billing → Payment methods → Add new**.

We accept:
- Visa, Mastercard, American Express, Discover
- ACH (US bank accounts)
- Wire transfer (Enterprise)

## Default payment method

If you have multiple payment methods, designate one as default. Subscription charges use the default; you can override per invoice.

## Updating cards

To update a card, add the new card and delete the old one. We do not support direct edits.

## Failed payments

If a charge fails, Helix retries automatically:

- 1st retry: 1 day later
- 2nd retry: 3 days later
- 3rd retry: 7 days later

After all retries fail, your account is downgraded to a read-only state. You can still view runs but cannot create or trigger new ones.

## Invoice billing (Enterprise)

Enterprise contracts can be billed via invoice with NET-30 or NET-60 terms. Invoices are sent monthly or annually depending on contract.
