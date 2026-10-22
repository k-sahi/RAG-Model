# Design notes

Decisions that aren't obvious from the code, and what they trade off.

## Chunking per format, not one splitter for everything

Each format's structure tells you where the meaning boundaries are, and a fixed-size splitter ignores all of it.

- **Markdown** splits on headings because each section of a product doc is about one thing ("Workflow limits", "Retrying"). The heading path is kept as a breadcrumb and prepended at index time, so a three-line section about the 30-minute limit is still findable by "workflow". Tables and code fences are treated as atomic blocks: a pricing table cut in half answers neither half of the question.
- **Runbooks** use ALL-CAPS section headings (`APPROVAL REQUIRED FOR`, `PROCEDURE`). Their sections are short, so consecutive sections are packed up to 900 characters, and the last section of one chunk is repeated at the start of the next when it is small. That overlap matters for questions that span "who approves" and "how to issue".
- **Tickets** stay whole when they fit (≤ 2,250 characters). The customer's problem is in the first turn and the fix in the last, and a chunk containing only one of them is far less useful. Longer tickets get a synthetic summary chunk (first customer message + resolution block) plus overlapping turn windows, so the problem/fix pair is always retrievable together.

Merging sections under 180 characters into the next section avoids a long tail of heading-only chunks that match on title words and carry no content.

## OCR

Five runbooks are scans. A page counts as scanned when `pypdf` extracts under 80 characters from it. Those pages go through `pdf2image` at 300 dpi and Tesseract. OCR takes ~5 seconds a page, so its output is cached by the file's SHA-256 and re-ingesting is instant. If Tesseract or Poppler is missing, the file is logged and skipped, never a crash. The tests cover both paths.

## Why local LSA embeddings by default

The default has to run in CI with no secrets and give the same result every time. TF-IDF + truncated SVD is deterministic (fixed seed, ARPACK solver), needs no network, and indexes the corpus in about 2 seconds. It is a weak semantic model, and the eval report shows exactly where that hurts (vocabulary mismatches). The OpenAI embedder is the production setting and sits behind one environment variable.

Because the LSA projection is refit from the saved chunks on load, nothing pickled is stored. The index is `chunks.json`, `vectors.npy` and a manifest.

## Tokenizer

Support content is full of tokens that generic tokenizers break: `X-Helix-Signature`, `HX-1267`, `pg_last_wal_receive_lsn`, `$299`, `429`. Compound tokens are emitted whole *and* split into parts, so an exact header name gets an exact-match boost and "signature" still matches. Stemming is a light suffix stripper plus double-letter collapsing. It is enough to make "cancel", "cancelled" and "cancellation" meet, and it leaves anything containing a digit alone.

## Fusion, reranking, cutoff

- **RRF** (`k = 60`) merges dense and BM25 rankings without having to put cosine similarity and BM25 scores on the same scale.
- **The reranker** is a linear model over five features: term coverage (IDF-weighted), chunk cosine, heading match, fused rank, and similarity between the query and the whole source document. That last feature does the most work. It favours chunks from documents that are *about* the question over chunks that merely mention a term. The weights came from a grid search checked with 2-fold cross-validation; the shipped weights are not the best grid point, but they hold up best on held-out halves.
- **The cutoff** works per document, not per chunk: documents within 75% of the best document's score (max 3), then up to 3 chunks from each that are within 70% of that document's best chunk. It returns one document for a one-document question and three for a three-document one, instead of always 5 chunks.

## Abstaining

Abstaining happens before generation, on lexical evidence only: the best IDF-weighted term coverage of any candidate and the best BM25 score, squashed to 0..1. Cosine is excluded because LSA puts even "write me a poem about autumn" near *some* chunk, while an off-topic question cannot fake matching rare corpus terms. The threshold is conservative (no real question is refused) and catches clearly unrelated questions. Questions that are about Helix but not covered ("what's Helix's stock price?") pass retrieval on purpose. The generator then has to say the context doesn't answer them, which its prompt and JSON schema (`insufficient_context`) require.

## Generation

- The prompt labels each chunk with its type and path, because "prefer product docs and runbooks over a single ticket" is only possible if the model knows which is which.
- Citations are taken from both the JSON `citations` field and inline `[n]` markers, and anything outside `1..n` is dropped, so the source list can't point at a chunk the model never saw.
- If the model returns prose instead of JSON, the prose is kept. If the API fails, the extractive answerer takes over, so a provider outage degrades the answer instead of breaking the request.
- `RAGPipeline.ask()` returns the retrieval it generated from, so the eval scores exactly the context the answer was produced from and never runs retrieval twice.

## What's deliberately not here

- No framework (LangChain, LlamaIndex). The whole pipeline is about 1,700 lines and every step can be inspected.
- No vector database by default: exact numpy search over 305 vectors is far faster than a network round trip. Pinecone is supported for when the corpus outgrows memory.
- No SDKs for the LLM APIs: two `urllib` calls with retry on 429/5xx, which keeps the dependency list to six packages.
