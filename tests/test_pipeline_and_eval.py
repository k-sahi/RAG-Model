import unittest

from evals.metrics import context_precision, context_recall, hit, reciprocal_rank
from evals.run_eval import evaluate, key_fact_recall, key_facts
from helix_rag.pipeline import RAGPipeline

from .helpers import index, settings


class MetricsTest(unittest.TestCase):
    def test_precision_and_recall(self):
        got = ["a", "a", "b", "x"]
        self.assertEqual(context_precision(got, ["a", "b"]), 0.75)
        self.assertEqual(context_recall(got, ["a", "b", "c"]), 2 / 3)
        self.assertEqual(context_precision([], ["a"]), 0.0)

    def test_rank_metrics(self):
        self.assertEqual(reciprocal_rank(["x", "a"], ["a"]), 0.5)
        self.assertEqual(reciprocal_rank(["x"], ["a"]), 0.0)
        self.assertEqual(hit(["x", "a"], ["a"]), 1.0)

    def test_key_facts(self):
        facts = key_facts("The Pro plan costs $299 per month with 10,000 runs and `X-Helix-Signature`. (1) step")
        self.assertIn("$299", facts)
        self.assertIn("10000", facts)
        self.assertIn("x-helix-signature", facts)
        self.assertNotIn("1", facts)
        self.assertEqual(key_fact_recall("It is $299 a month.", "Costs $299, includes 10,000 runs"), 0.5)
        self.assertIsNone(key_fact_recall("anything", "no facts here"))


class PipelineTest(unittest.TestCase):
    def test_ask_returns_answer_with_retrieval_attached(self):
        rag = RAGPipeline(settings(), index=index(), llm=None)
        ans = rag.ask("How do I rotate an API key?")
        self.assertIsNotNone(ans.retrieval)
        self.assertTrue(ans.sources)
        self.assertIn("retrieve_ms", ans.timings)
        d = ans.to_dict(include_context=True)
        self.assertEqual(set(d) >= {"answer", "sources", "retrieved", "abstained"}, True)


class QualityGateTest(unittest.TestCase):
    """The offline eval must clear the project's floor on every commit."""

    def test_eval_thresholds(self):
        result = evaluate(settings())
        s = result["summary"]
        self.assertEqual(s["n"], 50)
        self.assertGreaterEqual(s["context_precision"], 0.60)
        self.assertGreaterEqual(s["context_recall"], 0.70)
        self.assertGreaterEqual(s["hit@3"], 0.90)
        self.assertEqual(result["abstention"]["in_scope_false_abstentions"], 0)
        self.assertGreaterEqual(result["abstention"]["out_of_scope_abstained"], 10)


if __name__ == "__main__":
    unittest.main()
