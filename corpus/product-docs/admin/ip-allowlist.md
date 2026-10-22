# IP Allowlist

Restrict workspace access to specific IP ranges. Available on the Enterprise plan.

## How it works

When IP allowlisting is enabled, Helix rejects any request — UI login, API call, or webhook — that originates from outside the allowed CIDR ranges.

## Configuring

**Settings → Security → IP Allowlist**

- Add CIDR blocks (IPv4 or IPv6)
- Maximum **50 CIDR ranges** per workspace
- Toggle **Enforce** to activate

## What is restricted

- Web app login
- API requests
- Webhook delivery (inbound) — your webhook senders must be in the allowlist
- SAML SSO endpoints

## What is NOT restricted

- Outbound webhooks from Helix to your services (Helix's egress IPs are documented separately)
- Status page access
- Marketing site

## Best practices

**Allowlist your office VPN** rather than individual IPs. VPN ranges are more stable than individual user IPs.

**Allowlist webhook senders explicitly**. If you trigger workflows from third-party services, add their documented webhook IP ranges.

**Do not lock yourself out**. Always include an emergency CIDR (e.g., a backup VPN) in case the primary allowlist becomes unreachable.

## Recovery

If you accidentally lock yourself out, contact support@helix.io from the email of any Owner or Admin. We can disable enforcement after identity verification.
