# Eval run 2026-10-22T14:57:17Z

Config: `embedder=local-lsa`, `reranker=local`, `query_rewrite=False`, `generator=extractive`, `chunk_size=900`, `chunk_overlap=150`, `top_k=8`, `max_docs=3`, `per_doc=3`, `relative_cutoff=0.75`, `chunk_cutoff=0.7`, `abstain_threshold=0.36`, `chunks_indexed=305`

| metric | value |
|---|---|
| context_precision | 0.718 |
| context_recall | 0.788 |
| mrr | 0.88 |
| hit@1 | 0.8 |
| hit@3 | 0.96 |
| doc_recall@5 | 0.897 |
| key_fact_recall | 0.534 |
| chunks_returned | 4.42 |
| retrieve_ms | 7.16 |

## By difficulty

| difficulty | n | context_precision | context_recall | mrr | hit@1 | hit@3 | doc_recall@5 | key_fact_recall | chunks_returned | retrieve_ms |
|---|---|---|---|---|---|---|---|---|---|---|
| easy | 20 | 0.669 | 0.925 | 0.848 | 0.75 | 0.95 | 0.95 | 0.812 | 4.6 | 6.105 |
| hard | 10 | 0.787 | 0.525 | 0.856 | 0.8 | 0.9 | 0.7 | 0.291 | 3.9 | 9.36 |
| medium | 20 | 0.732 | 0.783 | 0.925 | 0.85 | 1.0 | 0.942 | 0.371 | 4.5 | 7.115 |

## By category

| category | n | context_precision | context_recall | hit@3 |
|---|---|---|---|---|
| admin | 7 | 0.779 | 0.857 | 1.0 |
| api | 14 | 0.784 | 0.786 | 1.0 |
| billing | 8 | 0.684 | 0.844 | 1.0 |
| csm | 1 | 0.667 | 0.667 | 1.0 |
| data | 5 | 0.613 | 0.8 | 0.8 |
| incident-response | 3 | 1.0 | 0.667 | 1.0 |
| integrations | 3 | 0.75 | 0.778 | 1.0 |
| mobile | 2 | 0.562 | 1.0 | 1.0 |
| workflows | 7 | 0.555 | 0.667 | 0.857 |

Abstention: 11/15 out-of-scope questions refused, 0 in-scope questions wrongly refused.

## Per question

| id | diff | precision | recall | first expected doc rank | retrieved docs |
|---|---|---|---|---|---|
| Q001 | easy | 0.33 | 1.00 | 1 | creating-workflows.md<br>sso.md<br>glossary.md |
| Q002 | easy | 0.00 | 0.00 | 8 | ticket-1234-workflow-timeout.html<br>run-logs.md<br>email-notifications.md |
| Q003 | easy | 0.50 | 1.00 | 3 | plan-downgrade-workflow.pdf<br>custom-reports.md<br>plans.md |
| Q004 | easy | 1.00 | 1.00 | 1 | rate-limits.md |
| Q005 | easy | 1.00 | 1.00 | 1 | rate-limits.md |
| Q006 | easy | 1.00 | 1.00 | 1 | overview.md |
| Q007 | easy | 0.25 | 1.00 | 2 | custom-webhooks.md<br>webhooks.md<br>ticket-1212-webhook-not-firing.html |
| Q008 | easy | 0.57 | 1.00 | 1 | webhooks.md<br>custom-webhooks.md<br>ticket-1212-webhook-not-firing.html |
| Q009 | easy | 1.00 | 1.00 | 1 | roles-and-permissions.md |
| Q010 | easy | 0.60 | 1.00 | 1 | sso.md<br>overview.md<br>plans.md |
| Q011 | easy | 0.50 | 1.00 | 1 | audit-log.md<br>retention-policy.md |
| Q012 | easy | 0.80 | 1.00 | 1 | run-logs.md<br>ticket-1378-missing-data-in-export.html<br>retention-policy.md |
| Q013 | easy | 0.60 | 1.00 | 1 | exporting-data.md<br>data-export-requests.pdf |
| Q014 | easy | 1.00 | 1.00 | 1 | versioning.md |
| Q015 | easy | 0.75 | 1.00 | 1 | scheduling.md<br>ticket-1289-schedule-not-running.html |
| Q016 | easy | 1.00 | 1.00 | 1 | overview.md<br>authentication.md |
| Q017 | easy | 0.50 | 0.50 | 1 | errors.md<br>ticket-1189-401-with-valid-key.html |
| Q018 | easy | 1.00 | 1.00 | 1 | overview.md |
| Q019 | easy | 0.38 | 1.00 | 2 | mobile-push.md<br>mobile-app-overview.md<br>mobile-limitations.md |
| Q020 | easy | 0.60 | 1.00 | 2 | custom-sla-handling.pdf<br>plans.md |
| Q021 | medium | 1.00 | 1.00 | 1 | error-handling.md |
| Q022 | medium | 0.25 | 1.00 | 1 | webhooks.md<br>custom-webhooks.md<br>ticket-1212-webhook-not-firing.html |
| Q023 | medium | 0.60 | 1.00 | 2 | plan-changes.md<br>plans.md<br>overview.md |
| Q024 | medium | 0.75 | 0.50 | 1 | roles-and-permissions.md<br>mobile-limitations.md |
| Q025 | medium | 0.80 | 1.00 | 1 | ticket-1156-api-rate-limit-confusion.html<br>rate-limits.md<br>zendesk.md |
| Q026 | medium | 0.20 | 1.00 | 2 | stripe.md<br>plan-changes.md<br>webhooks.md |
| Q027 | medium | 1.00 | 0.50 | 1 | ticket-1322-downgrade-question.html |
| Q028 | medium | 0.67 | 1.00 | 1 | exporting-data.md<br>data-export-requests.pdf<br>ticket-1349-export-stuck.html |
| Q029 | medium | 1.00 | 1.00 | 1 | gdpr-exports.md<br>account-deletion.pdf |
| Q030 | medium | 0.60 | 1.00 | 1 | scim.md<br>user-provisioning.md |
| Q031 | medium | 0.57 | 1.00 | 1 | payment-methods.md<br>account-suspension.pdf<br>stripe.md |
| Q032 | medium | 0.75 | 1.00 | 1 | mobile-limitations.md<br>mobile-app-overview.md<br>mobile-push.md |
| Q033 | medium | 1.00 | 0.50 | 1 | authentication.md |
| Q034 | medium | 1.00 | 0.50 | 1 | errors.md |
| Q035 | medium | 1.00 | 1.00 | 1 | ip-allowlist.md |
| Q036 | medium | 0.25 | 0.33 | 1 | ticket-1267-integration-disconnect.html<br>connection-management.md |
| Q037 | medium | 1.00 | 1.00 | 1 | custom-webhooks.md |
| Q038 | medium | 0.60 | 0.33 | 2 | conditions-and-branching.md<br>ticket-1234-workflow-timeout.html<br>customer-feedback-intake.pdf |
| Q039 | medium | 1.00 | 0.50 | 1 | usage-and-overages.md |
| Q040 | medium | 0.60 | 0.50 | 1 | webhooks.md<br>webhook-delivery-failure.pdf |
| Q041 | hard | 1.00 | 0.50 | 1 | ticket-1042-sso-redirect-loop.html |
| Q042 | hard | 0.20 | 0.33 | 2 | ticket-1212-webhook-not-firing.html<br>ticket-1402-slow-execution.html<br>ticket-1234-workflow-timeout.html |
| Q043 | hard | 0.00 | 0.00 | 17 | ticket-1301-unexpected-charge.html<br>ticket-1349-export-stuck.html<br>usage-and-overages.md |
| Q044 | hard | 1.00 | 0.50 | 1 | ticket-1189-401-with-valid-key.html<br>authentication.md |
| Q045 | hard | 0.67 | 0.67 | 1 | renewal-at-risk.pdf<br>renewal-forecasting.pdf<br>churn-risk-indicators.pdf |
| Q046 | hard | 1.00 | 0.75 | 1 | usage-and-overages.md<br>ticket-1301-unexpected-charge.html<br>invoices.md |
| Q047 | hard | 1.00 | 1.00 | 1 | database-failover.pdf |
| Q048 | hard | 1.00 | 0.50 | 1 | deploy-rollback.pdf |
| Q049 | hard | 1.00 | 0.50 | 1 | ticket-1212-webhook-not-firing.html |
| Q050 | hard | 1.00 | 0.50 | 1 | p0-incident-response.pdf |
