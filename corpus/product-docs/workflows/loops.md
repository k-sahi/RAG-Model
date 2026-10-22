# Loops

Loops let you process collections of data — for example, sending an email to every user in a list.

## Loop step

Insert a **Loop** step. Connect it to a list — typically the output of a previous step that returned an array.

## Loop variables

Inside a loop, the following variables are available:

- `{{loop.item}}` — The current item being processed.
- `{{loop.index}}` — The current 0-based index.
- `{{loop.total}}` — The total number of items.

## Performance considerations

Loops execute sequentially by default. For 100 items at 1 second each, that's 100 seconds. If your loop iterations are independent, use a **Parallel Loop** step to process up to 10 items concurrently.

## Limits

- Maximum iterations per loop: 1,000
- Maximum nested loop depth: 3
- Total workflow runtime still capped at 30 minutes regardless of loop count

## Common pitfalls

**Hitting rate limits**: If your loop calls an external API, you may hit rate limits. Add a delay step inside the loop or use parallelism cautiously.

**Memory issues**: Very large loops accumulate state. If you don't need data from prior iterations, clear it explicitly.
