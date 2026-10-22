import unittest

from helix_rag.chunking import ChunkerConfig, chunk_document, split_recursive
from helix_rag.documents import Document

from .helpers import index

MD = """# Guide

Intro paragraph that is long enough to stand on its own as a section of the document, with
some more words so it passes the minimum section size used by the chunker for merging.

## Limits

| Limit | Value |
|---|---|
| Steps | 100 |
| Runtime | 30 minutes |

Text after the table that explains the limits in a little more detail for the reader here.

## Example

```python
# a comment that looks like a heading
client.run(workflow_id="wf_123")
```

And a closing sentence about the example that makes this section long enough to keep.
"""


class MarkdownChunkingTest(unittest.TestCase):
    def setUp(self):
        self.chunks = chunk_document(Document("docs/guide.md", "markdown", "Guide", MD))

    def test_breadcrumbs(self):
        sections = [c.section for c in self.chunks]
        self.assertIn("Guide > Limits", sections)
        self.assertIn("Guide > Example", sections)

    def test_code_comment_is_not_a_heading(self):
        self.assertNotIn("Guide > a comment that looks like a heading", [c.section for c in self.chunks])

    def test_tables_and_code_stay_whole(self):
        small = chunk_document(Document("docs/guide.md", "markdown", "Guide", MD), ChunkerConfig(60, 10))
        table = [c for c in small if "| Steps | 100 |" in c.text]
        self.assertEqual(len(table), 1)
        self.assertIn("| Runtime | 30 minutes |", table[0].text)
        code = [c for c in small if "client.run" in c.text]
        self.assertIn("```python", code[0].text)

    def test_index_text_carries_context(self):
        c = next(c for c in self.chunks if c.section == "Guide > Limits")
        self.assertTrue(c.index_text.startswith("Guide > Guide > Limits"))


class RecursiveSplitTest(unittest.TestCase):
    def test_respects_size_and_overlaps(self):
        text = " ".join(f"Sentence number {i} is here." for i in range(200))
        parts = split_recursive(text, 300, 60)
        self.assertTrue(all(len(p) <= 300 for p in parts))
        self.assertGreater(len(parts), 5)
        for a, b in zip(parts, parts[1:]):
            self.assertTrue(a.split(". ")[-1].rstrip(".") in b, "consecutive windows should overlap")

    def test_short_text_is_one_chunk(self):
        self.assertEqual(split_recursive("short", 100, 10), ["short"])


class CorpusChunkingTest(unittest.TestCase):
    def test_every_document_produces_chunks(self):
        chunks = index().chunks
        sources = {c.source for c in chunks}
        self.assertGreaterEqual(len(sources), 95)
        self.assertEqual(len({c.chunk_id for c in chunks}), len(chunks))

    def test_pdf_chunks_named_by_section(self):
        chunks = [c for c in index().chunks if c.source == "runbooks/customer-ops/refund-processing.pdf"]
        self.assertTrue(any("Approval Required For" in c.section for c in chunks))

    def test_long_ticket_has_summary_with_resolution(self):
        chunks = [c for c in index().chunks if c.source == "tickets/ticket-1301-unexpected-charge.html"]
        summary = chunks[0]
        self.assertEqual(summary.section, "Summary")
        self.assertIn("Resolution:", summary.text)
        self.assertIn("$612", summary.text)


if __name__ == "__main__":
    unittest.main()
