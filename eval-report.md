# Evaluation report

All numbers come from `python -m evals.run_eval`, `python -m evals.ablation` and `python -m evals.tune` on the 50-question test set (20 easy, 20 medium, 10 hard) with the default configuration: local LSA embeddings, local reranker, 900-character chunks. The full per-question output is in `evals/results/latest.md`.

## Summary

| Metric | Result | Target |
|---|---|---|
| Context precision | **0.718** | ≥ 0.60 ✅ |
| Context recall | 0.788 | |
| MRR (first expected document) | 0.880 | |
| Expected document ranked 1st | 0.80 | |
| Expected document in top 3 | 0.96 | |
| Chunks sent to the model per question | 4.4 | |
| Retrieval latency | ~5 ms | |
| Off-topic questions refused | 11 / 15 | |
| Real questions wrongly refused | 0 / 50 | |
| Faithfulness (LLM judge) | not measured here, see below | ≥ 0.70 |
| Answer correctness (LLM judge) | not measured here, see below | |

Faithfulness and correctness need an LLM, both for the answers and for the judge, so they are not in this offline run. They are produced by `python -m evals.run_eval --judge` with `ANTHROPIC_API_KEY` or `OPENAI_API_KEY` set. CI runs that step and fails below 0.70 faithfulness when an `ANTHROPIC_API_KEY` repository secret is configured.

## By difficulty

| Difficulty | n | Precision | Recall | Hit@1 | Hit@3 |
|---|---|---|---|---|---|
| Easy | 20 | 0.669 | 0.925 | 0.75 | 0.95 |
| Medium | 20 | 0.732 | 0.783 | 0.85 | 1.00 |
| Hard | 10 | 0.787 | 0.525 | 0.80 | 0.90 |

Easy questions have the highest recall but the lowest precision. They have exactly one expected document, so any second document the cutoff lets through counts fully against precision. Hard questions are the opposite: precision is high because what comes back is relevant, but recall is 0.53 because they need 3 or 4 documents (runbook + ticket + product doc) and the cutoff keeps at most 3, usually fewer.

## What each stage adds

| Retrieval | Precision | Recall | Chunks / question |
|---|---|---|---|
| Dense only (LSA), top-5 | 0.520 | 0.808 | 5.0 |
| BM25 only, top-5 | 0.456 | 0.833 | 5.0 |
| Hybrid RRF, top-5 | 0.500 | 0.828 | 5.0 |
| Hybrid RRF + rerank, top-5 | 0.604 | 0.828 | 5.0 |
| **Hybrid RRF + rerank + document-aware cutoff** | **0.718** | 0.788 | 4.4 |

- **Fusion alone does not beat the best single retriever here.** BM25 has the best recall at top-5, because this corpus is full of exact tokens (error codes, prices, setting names) that the tokenizer keeps intact. RRF lands between the two retrievers. Its value is the wider candidate pool it hands to the reranker.
- **Reranking** adds about 0.10 precision at the same recall. The biggest single feature is the similarity between the question and the *whole* source document. It stops a document that mentions a term once from outranking the document that is about it.
- **The document-aware cutoff** adds another 0.11 precision for 0.04 recall. A fixed top-5 always sends 5 chunks. On a single-document question that means 3 or 4 distractors from other documents, which is the main way an LLM ends up blending facts from the wrong page.

The trade is deliberate: precision protects faithfulness. A system that wants maximum recall for hard questions can raise `HELIX_MAX_DOCS` or lower `HELIX_RELATIVE_CUTOFF`. With `HELIX_RELATIVE_CUTOFF=0.7`, precision is 0.64 and recall 0.81.

## Tuning without fitting the test set

The reranker weights and cutoffs were chosen on this test set, so there is a real risk of tuning to these 50 questions. Two checks:

**2-fold cross-validation of the reranker weights** (`python -m evals.tune`, metrics are document-level hit@1 / recall@3):

| | Tuned on half A → held-out B | Tuned on half B → held-out A |
|---|---|---|
| Best weights for the training half | 0.80 / 0.79 | 0.80 / 0.87 |
| Shipped weights | 0.80 / 0.81 | 0.80 / 0.91 |

The best-on-train weights reach 0.84–0.88 hit@1 on their own half and drop to 0.80 on the other. That gap is what over-fitting looks like. The shipped weights are a rounder, more even mix. They score lower than the best grid point on the full set (0.80 vs 0.86 hit@1) but do at least as well on every held-out half, so they were kept.

**Fresh off-topic questions.** The abstain threshold (0.36) was set from the first 11 questions in `evals/out_of_scope.json`. The last 4 were written afterwards as a check, and **all 4 got through** (confidence 0.39–0.42, against a lowest real question at 0.41). The threshold catches obviously unrelated questions, but the margin is thin, and it should not be presented as more than that. The second line of defence is the generator: it is told to set `insufficient_context` when the passages don't answer the question. Off-topic questions that pass retrieval get chunks that have nothing to do with them, so the model has nothing to cite.

## Where it fails

| Question | What went wrong |
|---|---|
| Q002 "How long can a workflow run before it times out?" | Vocabulary gap. The doc says "Maximum runtime per run: 30 minutes" and never "time out"; the timeout *ticket* wins instead. That ticket does contain the right number, so the answer can still be right while precision and recall are 0. |
| Q026 "How do I cancel my subscription?" | Found (`plan-changes.md`, rank 2), but `stripe.md` ranks first on "subscription" (Stripe subscriptions), and webhook docs follow (webhook subscriptions), so precision is 0.2. Before a stemmer fix this question missed entirely: "cancel" and "cancellation" stemmed to different tokens. |
| Q043 "Our auditor is asking for 18 months of run history" | Needs 4 documents (retention, run logs, export, ticket). The question shares almost no words with any of them; "history" and "auditor" pull in billing and audit-log content. |
| Q038 "Most efficient way to process a large batch" | Expected `loops.md` and `parallel-execution.md`; got branching docs and the timeout ticket. LSA does not connect "batch" with "loop over items" or "parallel". |
| Hard questions in general | Recall 0.53. They need the ticket *and* the doc *and* the runbook, and the cutoff stops at the strongest one or two. |

The common cause is the same: the question and the answer use different words, and LSA trained on 305 chunks is too weak a semantic model to bridge that. That leads directly to the next steps.

## Next steps

1. **Better embeddings.** `HELIX_EMBEDDER=openai` (text-embedding-3-small) is implemented and cached; it should fix most vocabulary-gap misses (Q002, Q038, Q043). It wasn't measured here because it needs an API key.
2. **Query rewriting** (`HELIX_QUERY_REWRITE=1`) for the same gap, for example "times out" → "maximum runtime".
3. **LLM reranker** (`HELIX_RERANKER=llm`) for hard questions, together with a less strict document cutoff, since a stronger reranker makes extra documents less risky.
4. **Calibrate the abstain threshold on a larger off-topic set** and add a small classifier instead of a single lexical score.
5. **Run the judged eval** in CI with a key and report faithfulness and correctness alongside these numbers.
