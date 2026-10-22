# Parallel Execution

Run independent branches of your workflow concurrently to reduce total runtime.

## Split step

Insert a **Split** step. Each output line from the Split is a parallel branch. Branches execute simultaneously and the workflow waits for all of them to finish before continuing.

## When to use parallelism

- Calling multiple independent APIs (e.g., enrich a contact from Clearbit and FullContact in parallel).
- Sending notifications to multiple channels.
- Aggregating data from multiple sources.

## When not to use parallelism

- Sequential dependencies — if step B needs the output of step A, they must run sequentially.
- Rate-sensitive operations — running 10 calls in parallel can trigger rate limits faster than running them sequentially.

## Combining branches

After parallel branches, use a **Join** step to merge their outputs. The Join exposes each branch's output as `{{branch_name.last_step.output}}`.

## Limits

- Maximum parallel branches per Split: 10
- Maximum nested Split depth: 2
