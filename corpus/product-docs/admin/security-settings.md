# Security Settings

Workspace-wide security controls available under **Settings → Security**.

## Password requirements

For non-SSO users, configure password policy:

- Minimum length: 8 to 32 characters
- Require uppercase, lowercase, numbers, special characters
- Disallow recent passwords (last 5)
- Maximum age: 30 to 365 days

## Session timeout

Configure how long a session lasts before re-authentication is required:

- Web sessions: 1 hour to 30 days
- API keys do not expire automatically; rotate manually

## Two-factor authentication

Enforce 2FA for all users via **Require 2FA**. Users without 2FA configured will be prompted to set it up on next login.

Supported 2FA methods:
- TOTP apps (Authy, Google Authenticator, 1Password)
- WebAuthn / hardware keys (YubiKey, Titan)
- SMS (not recommended; TOTP and WebAuthn are stronger)

## Login monitoring

The **Login activity** page shows successful and failed login attempts for every user. Filter by user, location, or status.

## Session revocation

Admins can revoke individual sessions or all sessions for a user under **Team → User → Sessions**. Useful when a user reports a lost device.
