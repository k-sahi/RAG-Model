import json
import unittest
from copy import copy

from helix_rag.documents import Chunk
from helix_rag.retrieval import Retriever, Scored, rrf_fuse

from .helpers import CORPUS, index, settings


def _scored(source, score, n=0):
    c = Chunk(f"{source}#{n}", source, "markdown", source, "", "text")
    return Scored(chunk=c, score=score)


class RRFTest(unittest.TestCase):
    def test_formula(self):
        fused = rrf_fuse([["a", "b"], ["b", "c"]], k=60)
        self.assertAlmostEqual(fused["a"], 1 / 61)
        self.assertAlmostEqual(fused["b"], 1 / 62 + 1 / 61)
        self.assertAlmostEqual(fused["c"], 1 / 62)
        self.assertEqual(max(fused, key=fused.get), "b")


class SelectionTest(unittest.TestCase):
    def setUp(self):
        self.r = Retriever(index(), copy(settings()))

    def test_drops_documents_far_below_the_best(self):
        self.r.s.relative_cutoff, self.r.s.max_docs, self.r.s.per_doc, self.r.s.chunk_cutoff = 0.75, 3, 3, 0.7
        ranked = [_scored("a.md", 1.0, 0), _scored("a.md", 0.8, 1), _scored("b.md", 0.9), _scored("c.md", 0.5), _scored("a.md", 0.3, 2)]
        chosen = [(s.chunk.source, s.score) for s in self.r.select(ranked)]
        self.assertEqual(chosen, [("a.md", 1.0), ("b.md", 0.9), ("a.md", 0.8)])

    def test_caps_documents_and_chunks(self):
        self.r.s.relative_cutoff, self.r.s.max_docs, self.r.s.per_doc, self.r.s.chunk_cutoff, self.r.s.top_k = 0.0, 2, 1, 0.0, 8
        ranked = [_scored("a.md", 1.0, 0), _scored("a.md", 0.99, 1), _scored("b.md", 0.9), _scored("c.md", 0.8)]
        self.assertEqual([s.chunk.chunk_id for s in self.r.select(ranked)], ["a.md#0", "b.md#0"])


class RetrievalQualityTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = Retriever(index(), settings())

    def top_source(self, q):
        return self.r.retrieve(q).chunks[0].chunk.source

    def test_exact_facts(self):
        self.assertEqual(self.top_source("What's the maximum number of steps allowed in a single workflow?"),
                         "product-docs/workflows/creating-workflows.md")
        self.assertEqual(self.top_source("What is the API rate limit on the Pro plan?"), "product-docs/api/rate-limits.md")

    def test_ticket_only_fact_is_found(self):
        res = self.r.retrieve("Salesforce connection keeps expiring every couple of weeks, refresh token policy")
        self.assertIn("tickets/ticket-1267-integration-disconnect.html", res.sources)

    def test_runbook_found_for_internal_procedure(self):
        res = self.r.retrieve("Who has to approve a refund over $1,000?")
        self.assertEqual(res.chunks[0].chunk.source, "runbooks/customer-ops/refund-processing.pdf")

    def test_abstains_off_topic(self):
        for q in ("What is the capital of France?", "How do I bake sourdough bread?", "Who painted the Mona Lisa?"):
            res = self.r.retrieve(q)
            self.assertTrue(res.abstained, q)
            self.assertEqual(res.chunks, [])

    def test_no_false_abstentions_on_test_set(self):
        queries = json.loads((CORPUS / "test_set.json").read_text())["queries"]
        refused = [q["id"] for q in queries if self.r.retrieve(q["query"]).abstained]
        self.assertEqual(refused, [])

    def test_deterministic(self):
        q = "How do I verify webhook signatures?"
        a = [s.chunk.chunk_id for s in self.r.retrieve(q).chunks]
        b = [s.chunk.chunk_id for s in self.r.retrieve(q).chunks]
        self.assertEqual(a, b)

    def test_scores_sorted_and_bounded(self):
        res = self.r.retrieve("How do I export my data as CSV?")
        scores = [s.score for s in res.chunks]
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertTrue(0.0 <= res.confidence <= 1.0)
        self.assertLessEqual(len(res.chunks), settings().top_k)


if __name__ == "__main__":
    unittest.main()
