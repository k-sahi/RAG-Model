# Data Retention Policy

Helix retains data only as long as needed for product functionality and legal compliance.

## Retention periods

| Data type | Pro | Enterprise |
|-----------|-----|------------|
| Workflow definitions | Indefinite | Indefinite |
| Workflow runs (logs + step data) | **90 days** | **365 days** |
| Audit log | N/A | **365 days** |
| Failed login attempts | 90 days | 90 days |
| Deleted workflows | 30 days (then hard-deleted) | 30 days |
| Deleted workspaces | 90 days | 90 days |

## Custom retention (Enterprise)

Enterprise customers can configure custom retention windows for runs and audit logs. Common configurations:

- Reduced retention for compliance (e.g., delete runs after 30 days)
- Extended retention for audit purposes (e.g., 7 years for audit log)

Custom retention is configured in your contract; contact your account team.

## Hard deletion

When data passes its retention window:

- Workflow runs: hard-deleted within 7 days
- Audit log: hard-deleted within 30 days
- Workspaces: hard-deleted on day 91 after deletion request

Hard-deleted data is irrecoverable.

## Backups

Helix maintains encrypted backups for disaster recovery. Backup retention is 35 days. Backup data inherits the same retention policy as production data; once data is hard-deleted in production, it is also removed from backups within the next backup cycle.
