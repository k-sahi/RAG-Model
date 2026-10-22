# Conditions and Branching

Conditional logic lets your workflow take different paths based on data.

## Condition steps

Insert a **Condition** step between any two steps. A condition evaluates an expression and routes the workflow to the True branch or False branch.

## Expression syntax

Conditions support comparison operators (`==`, `!=`, `>`, `<`, `>=`, `<=`), logical operators (`and`, `or`, `not`), and string functions (`contains`, `starts_with`, `ends_with`).

Examples:
- `{{trigger.amount}} > 1000`
- `{{trigger.email}} ends_with "@enterprise.com"`
- `{{step1.status}} == "approved" and {{trigger.priority}} != "low"`

## Branching strategies

### Two-way branching
Standard if-else. The Condition step has two outputs: True and False.

### Multi-way branching
Chain Condition steps for if-else-if logic. Each subsequent condition is reached only if the prior one was False.

### Parallel branches
Use a **Split** step to run multiple branches simultaneously. The workflow waits for all branches to complete before continuing.

## Common patterns

- **Approval routing**: Route to different approvers based on amount or category.
- **Customer segmentation**: Send different emails to free vs paid users.
- **Escalation**: Skip first-tier handling for high-priority items.
