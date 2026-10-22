import json
import unittest

from helix_rag.generation import NO_ANSWER, format_context, generate
from helix_rag.llm import LLMError, parse_json
from helix_rag.retrieval import Retriever

from .helpers import index, settings


class FakeLLM:
    provider, model = "fake", "fake-1"

    def __init__(self, reply=None, error=False):
        self.reply, self.error, self.prompts = reply, error, []

    def complete(self, system, user, temperature=0.0):
        self.prompts.append((system, user))
        if self.error:
            raise LLMError("boom")
        return self.reply


class GenerationTest(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r = Retriever(index(), settings())
        cls.ret = cls.r.retrieve("How much does the Pro plan cost?")

    def test_llm_answer_maps_citations_to_sources(self):
        llm = FakeLLM(json.dumps({"answer": "Pro costs $299 per month [1].", "citations": [1], "confidence": "high", "insufficient_context": False}))
        ans = generate(self.ret, llm)
        self.assertEqual(ans.answer, "Pro costs $299 per month [1].")
        self.assertEqual([s["n"] for s in ans.sources], [1])
        self.assertEqual(ans.sources[0]["source"], self.ret.chunks[0].chunk.source)
        self.assertFalse(ans.abstained)
        system, user = llm.prompts[0]
        self.assertIn("ONLY the numbered context", system)
        self.assertIn("[1] (", user)

    def test_inline_citations_count_and_bad_numbers_are_dropped(self):
        llm = FakeLLM('```json\n{"answer": "See [2] and [99].", "citations": [], "confidence": "medium"}\n```')
        ans = generate(self.ret, llm)
        self.assertEqual([s["n"] for s in ans.sources], [2] if len(self.ret.chunks) >= 2 else [])

    def test_model_reports_insufficient_context(self):
        llm = FakeLLM(json.dumps({"answer": "The docs don't say.", "citations": [], "confidence": "low", "insufficient_context": True}))
        ans = generate(self.ret, llm)
        self.assertTrue(ans.abstained)
        self.assertEqual(ans.confidence, "low")

    def test_non_json_reply_is_kept_as_text(self):
        ans = generate(self.ret, FakeLLM("Plain text answer [1]"))
        self.assertEqual(ans.answer, "Plain text answer [1]")

    def test_llm_failure_falls_back_to_extractive(self):
        ans = generate(self.ret, FakeLLM(error=True))
        self.assertEqual(ans.provider, "extractive")
        self.assertRegex(ans.answer, r"\[\d\]")
        self.assertTrue(ans.sources)

    def test_abstained_retrieval_never_calls_llm(self):
        llm = FakeLLM("should not be used")
        ans = generate(self.r.retrieve("Who won the 2022 football World Cup?"), llm)
        self.assertEqual(ans.answer, NO_ANSWER)
        self.assertTrue(ans.abstained)
        self.assertEqual(llm.prompts, [])

    def test_extractive_answer_has_citations(self):
        ans = generate(self.ret, None)
        self.assertRegex(ans.answer, r"\[\d\]")
        self.assertTrue(ans.sources)

    def test_context_labels_document_types(self):
        ctx = format_context(self.ret.chunks)
        self.assertIn("[1] (", ctx)
        self.assertRegex(ctx, r"\((product doc|runbook|support ticket)\)")


class ParseJsonTest(unittest.TestCase):
    def test_parses_fenced_json(self):
        self.assertEqual(parse_json('Sure:\n```json\n{"a": 1}\n```'), {"a": 1})

    def test_raises_without_json(self):
        with self.assertRaises(LLMError):
            parse_json("no json here")


if __name__ == "__main__":
    unittest.main()
