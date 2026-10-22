# Salesforce Integration

Read and write Salesforce records from your workflows.

## Connecting

Salesforce uses OAuth. Click **Connect** on the Salesforce integration page and log in with your Salesforce credentials. You may need to grant your Helix workspace access to the Salesforce org.

For sandbox orgs, toggle **Sandbox** before clicking Connect.

## Supported objects

All standard objects (Account, Contact, Lead, Opportunity, Case, Task, Event) plus any custom objects in your org.

## Actions

- **Create record**: Insert a new record into any object.
- **Update record**: Update an existing record by ID.
- **Find record**: Look up a record by any field.
- **Run SOQL query**: Execute an arbitrary SOQL query and return results.
- **Bulk operation**: Insert/update up to 10,000 records via the Bulk API.

## Triggers

- **New record**: Fires when a new record is created in a specified object.
- **Field changed**: Fires when a specific field on a record changes value.

## Permissions

The connection runs with the permissions of the Salesforce user who authorized it. If you need to access fields, configure FLS (Field-Level Security) for that user in Salesforce.

## Bulk API quotas

Salesforce limits Bulk API to 10,000 requests per 24 hours. Helix surfaces 429 errors when you hit this limit; consider batching large updates.
