# OAuth Connection Flow

Most Helix integrations use OAuth 2.0 for authentication. This page explains what happens during the connection flow and how to troubleshoot common issues.

## Connection steps

1. **You click Connect** in Helix. Helix records a connection attempt.
2. **Helix redirects to the provider** (e.g., Google, Salesforce). The redirect includes Helix's client ID and the requested scopes.
3. **You authorize** the connection on the provider's site.
4. **Provider redirects back** to Helix with an authorization code.
5. **Helix exchanges the code** for an access token and refresh token.
6. **Helix stores credentials** in encrypted storage and marks the connection as Active.

## Token refresh

Most providers issue access tokens that expire (usually after 1 hour). Helix uses the refresh token to obtain new access tokens automatically. You should not need to reconnect unless the refresh token itself expires (typically after 60–90 days of inactivity, depending on the provider).

## Troubleshooting

**"Invalid scope" error during authorization**
Check that the provider account has access to the resource type you are connecting (e.g., Google Drive vs Google Workspace).

**"Connection expired" status in Helix**
The refresh token has been revoked or expired. Click **Reconnect** to refresh.

**Provider asks "Helix is requesting access to your account"**
Expected. Helix is requesting the scopes needed for the specific integration. We do not request scopes we don't use.

**Connection works in Helix but actions fail with 401**
Likely a permissions issue at the provider. The connected user may have lost access to the resource. Check provider-side permissions.
