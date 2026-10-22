# GitHub Integration

Automate development workflows with GitHub triggers and actions.

## Connecting

GitHub uses OAuth. You can connect either a personal account or a GitHub App installation. For org-level access, GitHub App is recommended.

## Triggers

- **New issue**: Fires when an issue is opened.
- **Issue closed**: Fires when an issue is closed.
- **New pull request**: Fires when a PR is opened.
- **PR merged**: Fires when a PR is merged.
- **New comment on issue/PR**: Fires when someone comments.
- **Push to branch**: Fires on every push to a specified branch.

## Actions

- **Create issue**: Open a new issue with title, body, labels, and assignees.
- **Comment on issue**: Add a comment to an existing issue or PR.
- **Add label**: Apply a label to an issue or PR.
- **Close issue**: Close an issue with optional comment.
- **Create branch**: Create a branch from a specified base.
- **Get file contents**: Read a file from a repository.

## Repository scope

Each connection covers all repositories the authorizing user can access. To limit scope, use a service account or a GitHub App with restricted permissions.

## Webhook setup

Helix automatically configures webhooks on connected repositories for the triggers you use. You can see the active webhooks in your repo settings.
