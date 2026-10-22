# Single Sign-On (SSO)

SSO via SAML 2.0 is available on the Enterprise plan.

## Supported identity providers

- Okta
- Azure AD / Microsoft Entra
- Google Workspace
- OneLogin
- Auth0
- Any SAML 2.0-compliant IdP

## Setup steps

1. Contact your account team to enable SSO for your workspace.
2. In **Settings → Security → SSO**, you'll find the Helix-side SAML metadata.
3. Configure your IdP with this metadata:
   - **Entity ID**: provided in settings
   - **ACS URL**: provided in settings
   - **NameID format**: emailAddress
4. Upload your IdP's metadata XML to Helix.
5. Test with a single user before rolling out to the team.

## Just-in-time provisioning

When a new user signs in via SSO and doesn't yet have a Helix account, Helix automatically provisions one with the **Editor** role. To change the default role, configure **JIT default role** in security settings.

## Forcing SSO

To require all users to sign in via SSO (no password fallback), enable **Enforce SSO** in security settings. Existing password-based sessions are invalidated; users must re-authenticate via SSO.

## Service accounts and SSO

Service accounts (used for API keys) bypass SSO. They authenticate via API key only.

## Common issues

**"User not found" after SSO redirect**: The IdP is not sending the user's email in the NameID field. Adjust your IdP's NameID format.

**Loop redirect to IdP**: Browser cookies are blocked. Check third-party cookie settings.
