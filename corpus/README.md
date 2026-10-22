# Helix corpus

The knowledge base this project indexes. **Helix** is a fictional B2B SaaS workflow automation platform; every plan, limit, integration, error code and policy is defined in these files, so each test question has one unambiguous answer.

```
corpus/
├── test_set.json      50 evaluation questions with reference answers
├── product-docs/      60 markdown pages
│   ├── getting-started/  workflows/  integrations/  api/  admin/
│   └── billing/  data/  notifications/  mobile/
├── runbooks/          25 internal PDFs (5 are scanned images with no text layer)
│   └── incident-response/  customer-ops/  engineering/  csm/
└── tickets/           15 resolved support tickets (HTML)
```

60 markdown + 25 PDF + 15 HTML = 100 documents.

## What makes it messy

- Three formats, each needing its own loader and chunker.
- Five runbooks are scans and need OCR.
- The same fact can appear in several places (for example the 30-minute workflow timeout).
- Tables, code blocks and nested lists that a naive splitter breaks.
- Tickets are multi-turn conversations, and the fix is often only in the last agent reply.
- Some facts exist only in a ticket, and internal procedures exist only in runbooks.

## Test set

| Difficulty | Questions | What they test |
|---|---|---|
| Easy | 20 | One document, direct fact |
| Medium | 20 | Several documents, scenarios, specific details |
| Hard | 10 | Runbook + ticket + product doc together, edge cases |

Each entry has `id`, `query`, `ground_truth_answer`, `expected_sources` (corpus paths), `difficulty`, `category` and grading `notes`.

The test set is only used for scoring. Nothing in it is read at query time.
